from flask import Blueprint, request, jsonify, session
from datetime import datetime, timezone
import numpy as np
import base64
import cv2
import logging

from utils.helpers import init_interview_data
from routes.session import save_conversation_to_file
from services.tts_service import text_to_speech
from services.visual_service import analyze_visual_response
from services.cohere.followup_generator import generate_dynamic_follow_up
from services.report.generator import generate_interview_report
# from services.report.file_manager import save_admin_report_txt
from services.scoring_service import evaluate_response
from services.stt_service import process_audio_from_base64  # Import WebRTC VAD service

answer_bp = Blueprint('answer_bp', __name__)
logger = logging.getLogger(__name__)

FRAME_CAPTURE_INTERVAL = 5
MAX_FOLLOW_UPS = 3

@answer_bp.route('/process_answer', methods=['POST'])
def process_answer():
    logger.info("Process answer request received")
    interview_data = session.get('interview_data', init_interview_data())

    if not interview_data.get('interview_started', False):
        return jsonify({"status": "error", "message": "Interview not started"}), 400

    data = request.get_json()
    answer = data.get('answer', '').strip()
    frame_data = data.get('frame', None)
    audio_data_base64 = data.get('audio_data', None)  # Get audio data for VAD processing

    if not answer:
        return jsonify({"status": "error", "message": "Empty answer"}), 400

    current_question = interview_data['conversation_history'][-1].get('text', '')

    # Store answer
    interview_data['answers'].append(answer)
    interview_data['conversation_history'].append({"speaker": "user", "text": answer})
    save_conversation_to_file([{"speaker": "user", "text": answer}])
    interview_data['last_activity_time'] = datetime.now(timezone.utc)

    # Feedback
    feedback_label = "Good answer" if len(answer) > 50 else "Needs improvement"
    feedback_audio = text_to_speech(feedback_label)

    interview_data['conversation_history'].append({
        "speaker": "user",
        "text": answer,
        "feedback_label": feedback_label,
        "feedback_audio": feedback_audio
    })
    save_conversation_to_file([interview_data['conversation_history'][-1]])
    interview_data['last_activity_time'] = datetime.now(timezone.utc)

    # Visual feedback
    visual_feedback = None
    current_time = datetime.now().timestamp()
    last_frame_time = interview_data.get("last_frame_time", 0)

    if frame_data and (current_time - last_frame_time) > FRAME_CAPTURE_INTERVAL:
        try:
            # Decode base64 frame safely
            base64_str = frame_data.split(',')[1] if ',' in frame_data else frame_data

            if not base64_str.strip():
                logger.warning("⚠ Empty frame received, skipping visual analysis.")
            else:
                frame_bytes = base64.b64decode(base64_str)
                frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)

                if frame_array.size == 0:
                    logger.warning("⚠ Decoded frame array is empty, skipping visual feedback.")
                else:
                    frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)

                    if frame is not None:
                        frame_base64 = process_frame_for_gpt4v(frame)
                        visual_feedback = analyze_visual_response(
                            frame_base64,
                            interview_data['conversation_history'][-3:]
                        )
                        if visual_feedback:
                            interview_data['visual_feedback'].append(visual_feedback)
                            interview_data['last_frame_time'] = current_time
                    else:
                        logger.warning("⚠ OpenCV failed to decode frame, skipping.")
        except Exception as e:
            logger.error(f"❌ Error processing frame: {str(e)}", exc_info=True)

    # Process audio with WebRTC VAD
    if audio_data_base64:
        has_speech, speech_ratio = process_audio_from_base64(audio_data_base64)
        if has_speech:
            logger.info("Speech detected in the audio answer")
        else:
            logger.warning("No speech detected in the audio answer")

    # Rating (no length check — evaluates based on meaning & depth)
    rating = evaluate_response(
        answer,
        current_question,
        interview_data['role'],
        interview_data['experience_level'],
        visual_feedback
    )
    interview_data['ratings'].append(rating)

    # Follow-up logic
    current_main_index = interview_data['current_question'] - 1
    if interview_data['follow_up_count'] < MAX_FOLLOW_UPS:
        if (
            current_main_index < len(interview_data['conversation_history']) and
            'prepared_follow_ups' in interview_data['conversation_history'][current_main_index]
        ):
            for fup in interview_data['conversation_history'][current_main_index]['prepared_follow_ups']:
                if fup not in interview_data['used_follow_ups'] and fup not in interview_data['follow_up_questions']:
                    interview_data['follow_up_questions'].append(fup)

        # Dynamic follow-up
        if len(interview_data['follow_up_questions']) < MAX_FOLLOW_UPS:
            dynamic_fup = generate_dynamic_follow_up(
                interview_data['conversation_history'],
                interview_data.get('current_topic', '')
            )
            if dynamic_fup and dynamic_fup not in interview_data['used_follow_ups'] and dynamic_fup not in interview_data['follow_up_questions']:
                interview_data['follow_up_questions'].append(dynamic_fup)

    # Interview complete?
    is_done = (
        interview_data['current_question'] >= len(interview_data['questions']) and
        not interview_data['follow_up_questions']
    )

    if is_done:
        user_report = generate_interview_report(interview_data)
        admin_path, admin_name = save_admin_report_txt(interview_data)

        return jsonify({
            "status": "interview_complete",
            "message": "Interview complete, report generated.",
            "report_html": user_report.get('reports', ''),
            "admin_report_filename": admin_name
        })

    session['interview_data'] = interview_data
    return jsonify({
        "status": "answer_processed",
        "current_question": interview_data['current_question'],
        "total_questions": len(interview_data['questions']),
        "interview_complete": False,
        "has_follow_up": len(interview_data['follow_up_questions']) > 0,
        "feedback_audio": feedback_audio
    })


def process_frame_for_gpt4v(frame):
    """Convert OpenCV frame to base64 string for visual analysis."""
    _, buffer = cv2.imencode('.jpg', frame)
    return base64.b64encode(buffer).decode('utf-8')
