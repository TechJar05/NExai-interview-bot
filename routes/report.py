# # routes/report.py

# import os
# import base64
# import logging
# import requests
# import pdfkit
# from flask import Blueprint, session, jsonify, send_from_directory
# from datetime import datetime, timezone

# # ✅ correct (use new structure)
# from services.report.generator import generate_interview_report
# # from services.report.file_manager import save_admin_report_txt
# from utils.file_utils import html_to_pdf
# from utils.helpers import init_interview_data

# logger = logging.getLogger(__name__)

# report_bp = Blueprint('report_bp', __name__, url_prefix='/interview/report')


# CONVERSATION_FILE = "interview_conversation.txt"
# PDF_OUTPUT_DIR = os.path.join(os.getcwd(), "reports")
# os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)


# @report_bp.route('/generate_report', methods=['GET'])
# def generate_report():
#     logger.info("Generate report request received")
#     interview_data = session.get('interview_data', init_interview_data())

#     if not interview_data['interview_started']:
#         logger.warning("Attempt to generate report before interview started")
#         return jsonify({"status": "error", "message": "Interview not started"}), 400

#     if not interview_data['end_time']:
#         interview_data['end_time'] = datetime.now(timezone.utc)
#         session['interview_data'] = interview_data

#     interview_data["candidate_name"] = session.get("candidate_name", "Anonymous")
#     interview_data["organization_name"] = session.get("organization_name", "N/A")
#     interview_data["email"] = session.get("email", "Not Provided")
#     interview_data["job_title"] = session.get("job_title", "Unknown")
#     interview_data["resume_text"] = session.get("resume_text", "")
#     interview_data["jd_text"] = session.get("jd_text", "")
#     session['interview_data'] = interview_data

#     # ✅ Generate HTML report
#     report = generate_interview_report(interview_data)
#     if report["status"] == "error":
#         return jsonify(report), 500

#     html_report = report.get("report", "")
#     try:
#         pdf_binary = html_to_pdf(html_report)
#         if not pdf_binary:
#             raise Exception("Empty PDF data")
#     except Exception as e:
#         logger.error(f"PDF generation failed: {e}")
#         return jsonify({"status": "error", "message": "PDF generation failed"}), 500

#     # ✅ Prepare Django payload
#     django_payload = {
#         "candidate_name": interview_data["candidate_name"],
#         "role": interview_data["job_title"],
#         "organization_name": interview_data["organization_name"],
#         "years_experience": interview_data["years_experience"],
#         "start_time": interview_data["start_time"].isoformat(),
#         "end_time": interview_data["end_time"].isoformat(),
#         "average_rating": report["avg_rating"],
#         "status": report["status_class"].capitalize(),
#         "report_text": html_report,
#         "pdf_file": base64.b64encode(pdf_binary).decode("utf-8")
#     }

#     try:
#         django_url = "https://nexai.qwiktrace.com/api/jobs/store-interview-report/"
#         django_response = requests.post(django_url, json=django_payload, headers={"Content-Type": "application/json"})

#         if django_response.status_code == 201:
#             logger.info("Report successfully sent to Django backend")
#         else:
#             logger.warning(f"Failed to save report in Django: {django_response.text}")
#     except Exception as e:
#         logger.error(f"Failed to send data to Django: {e}")

#     return jsonify(report)








import os
import base64
import logging
import requests
from flask import Blueprint, session, jsonify
from datetime import datetime, timezone

from services.report.generator import generate_interview_report
from utils.file_utils import html_to_pdf
from utils.helpers import init_interview_data

logger = logging.getLogger(__name__)


report_bp = Blueprint('report_bp', __name__, url_prefix='/ibot/interview')


@report_bp.route('/generate_report/', methods=['GET'])
def generate_report():
    logger.info("Generate report request received")
    interview_data = session.get('interview_data', init_interview_data())

    if not interview_data['interview_started']:
        return jsonify({"status": "error", "message": "Interview not started"}), 400

    if not interview_data['end_time']:
        interview_data['end_time'] = datetime.now(timezone.utc)
        session['interview_data'] = interview_data

    interview_data["candidate_name"] = session.get("candidate_name", "Anonymous")
    interview_data["organization_name"] = session.get("organization_name", "N/A")
    interview_data["email"] = session.get("email", "Not Provided")
    interview_data["job_title"] = session.get("job_title", "Unknown")
    interview_data["resume_text"] = session.get("resume_text", "")
    interview_data["jd_text"] = session.get("jd_text", "")

    session['interview_data'] = interview_data

    report = generate_interview_report(interview_data)
    if report["status"] == "error":
        return jsonify(report), 500

    try:
        pdf_binary = html_to_pdf(report["report"])
        if not pdf_binary:
            raise Exception("Empty PDF content")

        logger.info("PDF generated successfully")

        django_payload = {
            "candidate_name": interview_data["candidate_name"],
            "role": interview_data["job_title"],
            "organization_name": interview_data["organization_name"],
            "years_experience": interview_data["years_experience"],
            "start_time": interview_data["start_time"].isoformat(),
            "end_time": interview_data["end_time"].isoformat(),
            "average_rating": report["avg_rating"],
            "status": report["status_class"].capitalize(),
            "report_text": report["report"],
            "pdf_file": base64.b64encode(pdf_binary).decode("utf-8")
        }

        django_url = "https://nexai.qwiktrace.com/api/jobs/store-interview-report/"
        response = requests.post(django_url, json=django_payload)

        if response.status_code == 201:
            logger.info("Report sent to Django successfully")
        else:
            logger.warning(f"Django response: {response.text}")

        
        # ✅ New: Call Django to mark interview as completed
        interview_token = session.get("interview_token")  # Must be stored in session earlier
        logger.info(f"Using interview token--------------------------: {interview_token}")

        if interview_token:
            mark_complete_url = f"https://nexai.qwiktrace.com/api/jobs/interview/submit/{interview_token}/"
            complete_resp = requests.post(mark_complete_url)

            if complete_resp.status_code == 200:
              logger.info("Interview marked as completed.")
            elif complete_resp.status_code == 400 and "already submitted" in complete_resp.text.lower():
              logger.info("Interview was already marked as completed.")
            else:
             logger.warning(f"Failed to mark interview complete: {complete_resp.text}")

        else:
            logger.warning("No interview token found in session to mark as complete.")

    except Exception as e:
            logger.error(f"Report sync or PDF error: {str(e)}")
            return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify(report)
