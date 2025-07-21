





# def generate_interview_report(interview_data):
#     try:
#         # Calculate interview duration
#         duration = "N/A"
#         if interview_data['start_time'] and interview_data['end_time']:
#             duration_seconds = (interview_data['end_time'] - interview_data['start_time']).total_seconds()
#             minutes = int(duration_seconds // 60)
#             seconds = int(duration_seconds % 60)
#             duration = f"{minutes}m {seconds}s"
        
#         # Calculate average rating
#         ratings = interview_data.get('ratings', [])
#         avg_rating = sum(ratings) / len(ratings) if ratings else 0
#         logger.debug(f"Average rating: {avg_rating:.1f}, based on {len(ratings)} ratings")
        
#         # Determine status based on average rating
#         if avg_rating >= 7:
#             status = "Selected"
#             status_class = "selected"
#         elif avg_rating >= 4 and avg_rating < 7:
#             status = "On Hold"
#             status_class = "onhold"
#         else:
#             status = "Rejected"
#             status_class = "rejected"
        
#         # Calculate skill distribution
#         questions = interview_data.get('questions', [])
#         question_topics = interview_data.get('question_topics', [])
#         ratings = interview_data.get('ratings', [])
        
#         technical_scores = []
#         communication_scores = []
#         behavioral_scores = []

#         # Categorize ratings based on question types
#         for i, (question, topic, rating) in enumerate(zip(questions, question_topics, ratings)):
#             topic_lower = topic.lower() if topic else ""
#             if "technical" in topic_lower or i < 10:
#                 technical_scores.append(rating)
#             elif "experience" in topic_lower or "role" in topic_lower or i < 15:
#                 behavioral_scores.append(rating)
#             communication_scores.append(rating * 0.4)

#         technical_avg = sum(technical_scores) / len(technical_scores) if technical_scores else 5
#         behavioral_avg = sum(behavioral_scores) / len(behavioral_scores) if behavioral_scores else 5
#         communication_avg = sum(communication_scores) / len(communication_scores) if communication_scores else 5
#         logger.debug(f"Skill averages - Technical: {technical_avg:.1f}, Communication: {communication_avg:.1f}, Behavioral: {behavioral_avg:.1f}")

#         total = max(technical_avg + communication_avg + behavioral_avg, 0.01)
#         technical_pct = (technical_avg / total) * 100
#         communication_pct = (communication_avg / total) * 100
#         behavioral_pct = 100 - technical_pct - communication_pct
#         logger.debug(f"Skill percentages - Technical: {technical_pct:.1f}%, Communication: {communication_pct:.1f}%, Behavioral: {behavioral_pct:.1f}%")

#         bar_chart_html = f"""
#         <div style="font-family: Arial, sans-serif; max-width: 400px; margin: 20px auto;">
#             <h4 style="text-align: center;">Skill Distribution</h4>
#             <div style="margin-bottom: 15px;">
#                 <span style="display: inline-block; width: 120px; font-weight: bold;">Technical 🛠</span>
#                 <div style="display: inline-block; width: 200px; background-color: #e0e0e0; border-radius: 5px; overflow: hidden;">
#                     <div style="width: {min(technical_pct, 100)}%; background-color: #4CAF50; height: 20px;"></div>
#                 </div>
#                 <span style="margin-left: 10px;">{technical_pct:.1f}%</span>
#             </div>
#             <div style="margin-bottom: 15px;">
#                 <span style="display: inline-block; width: 120px; font-weight: bold;">Communication 🗣</span>
#                 <div style="display: inline-block; width: 200px; background-color: #e0e0e0; border-radius: 5px; overflow: hidden;">
#                     <div style="width: {min(communication_pct, 100)}%; background-color: #2196F3; height: 20px;"></div>
#                 </div>
#                 <span style="margin-left: 10px;">{communication_pct:.1f}%</span>
#             </div>
#             <div style="margin-bottom: 15px;">
#                 <span style="display: inline-block; width: 120px; font-weight: bold;">Behavioral 🤝</span>
#                 <div style="display: inline-block; width: 200px; background-color: #e0e0e0; border-radius: 5px; overflow: hidden;">
#                     <div style="width: {min(behavioral_pct, 100)}%; background-color: #FFC107; height: 20px;"></div>
#                 </div>
#                 <span style="margin-left: 10px;">{behavioral_pct:.1f}%</span>
#             </div>
#         </div>
#         """

#         conversation_history_text = "\n".join([f"{item['speaker']}: {item['text']}" for item in interview_data['conversation_history'] if 'speaker' in item])
        
#         report_prompt = f"""
# You are an expert AI HR assistant responsible for generating professional interview evaluation reports.

# The following interview was conducted for the role of {interview_data['role']}.

# ### Candidate Overview:
# - 🎓 Experience Level: {interview_data['experience_level']}
# - 🕒 Years of Experience: {interview_data['years_experience']}
# - ⏱ Interview Duration: {duration}
# - ⭐ Average Interviewer Rating: {avg_rating:.1f}/10

# ### 📜 Interview Transcript:
# {conversation_history_text}

# ---

# ## 🎯 Your Task:
# Generate a detailed interview evaluation report using the transcript and rating context.

# Format the output in clean HTML with semantic structure, using <h2>, <table>, and <div>.

# ✅ Include the following 5 sections:

# ---

# ### 1. <h2>Interview Summary</h2>
# - Provide a concise overview of how the interview went.
# - Mention how well the candidate communicated, handled technical questions, and overall impression.

# ---

# ### 2. <h2>Key Strengths</h2>
# - Show a table with exactly 2 columns: 'Aspect' and 'Evidence from Responses'.
# - Include 2-4 rows, each identifying a strength (e.g., Problem Solving, Communication, Domain Expertise) and quoting or summarizing a relevant answer from the transcript.
# - Use the following HTML table structure:
#   <table style="width: 100%; border-collapse: collapse;">
#     <tr style="border: 1px solid #000;">
#       <th style="border: 1px solid #000; padding: 8px;">Aspect</th>
#       <th style="border: 1px solid #000; padding: 8px;">Evidence from Responses</th>
#     </tr>
#     <tr style="border: 1px solid #000;">
#       <td style="border: 1px solid #000; padding: 8px;">[Strength Aspect]</td>
#       <td style="border: 1px solid #000; padding: 8px;">[Quote or Summary]</td>
#     </tr>
#     <!-- Additional rows as needed -->
#   </table>

# ---

# ### 3. <h2>Areas for Improvement</h2>
# - Show a table with exactly 2 columns: 'Aspect to Improve' and 'Suggestion or Evidence'.
# - Include 2-4 rows, each identifying an area for improvement (e.g., Confidence, Project Depth) and providing actionable feedback or evidence from the transcript.
# - Use the following HTML table structure:
#   <table style="width: 100%; border-collapse: collapse;">
#     <tr style="border: 1px solid #000;">
#       <th style="border: 1px solid #000; padding: 8px;">Aspect to Improve</th>
#       <th style="border: 1px solid #000; padding: 8px;">Suggestion or Evidence</th>
#     </tr>
#     <tr style="border: 1px solid #000;">
#       <td style="border: 1px solid #000; padding: 8px;">[Improvement Aspect]</td>
#       <td style="border: 1px solid #000; padding: 8px;">[Feedback or Evidence]</td>
#     </tr>
#     <!-- Additional rows as needed -->
#   </table>

# ---

# ### 4. <h2>Visual Analysis</h2>
# Include the following:
# - Interview Round Ratings (list each question's rating, e.g., Question 1: 8/10)
# - Skill Balance Bar Chart:
#   - Technical Skills  — {technical_pct:.1f}%
#   - Communication  — {communication_pct:.1f}%
#   - Behavioral Fit  — {behavioral_pct:.1f}

# Use the provided HTML for the bar chart:
# {bar_chart_html}

# ---

# ### 5. <h2>Overall Recommendation</h2>
# - Clearly state whether the candidate is:
#   - ✅ Selected
#   - ⏳ On Hold
#   - ❌ Rejected
# - Explain why using 2-3 crisp bullet points in a <ul> list.

# ---

# ## Requirements:
# - Return the entire content as pure HTML.
# - Do not add external CSS or scripts.
# - Ensure tables for 'Key Strengths' and 'Areas for Improvement' strictly follow the provided HTML structure with inline CSS.
# - Use <p> tags for text content outside tables.
# - Do not use markdown or other formats; output must be valid HTML.
# """
#         logger.debug("Sending prompt to OpenAI for HTML report generation")
#         report_response = client.chat.completions.create(
#             model="gpt-4-turbo",
#             messages=[
#                 {"role": "system", "content": "You are a professional HTML interview report writer."},
#                 {"role": "user", "content": report_prompt}
#             ],
#             max_tokens=2000,
#             temperature=0.5
#         )

#         report_content = report_response.choices[0].message.content.strip()
#         logger.debug("Received report content from OpenAI")

#         voice_feedback_prompt = f"""
# Extract or create a concise 5-6 line voice feedback summary from this interview report:
# {report_content}

# The feedback should:
# - Be spoken in a natural, conversational tone
# - Highlight the key conclusions
# - Be encouraging but honest
# - Be exactly 5-6 lines long
# """

#         logger.debug("Sending prompt to OpenAI for voice feedback")
#         voice_response = client.chat.completions.create(
#             model="gpt-4-turbo",
#             messages=[
#                 {"role": "system", "content": "You are a professional HR summarizer creating spoken feedback."},
#                 {"role": "user", "content": voice_feedback_prompt}
#             ],
#             max_tokens=300,
#             temperature=0.5
#         )

#         voice_feedback = voice_response.choices[0].message.content.strip()
#         logger.debug(f"Generated voice feedback: {voice_feedback}")

#         logger.debug("Converting voice feedback to audio")
#         voice_audio = text_to_speech(voice_feedback)

#         return {
#             "status": "success",
#             "report": report_content,
#             "voice_feedback": voice_feedback,
#             "voice_audio": voice_audio,
#             "status_class": status_class,
#             "avg_rating": avg_rating,
#             "duration": duration
#         }

#     except Exception as e:
#         logger.error(f"Error generating report: {str(e)}", exc_info=True)
#         return {
#             "status": "error",
#             "message": str(e),
#             "report": "<p>Error generating report. Please try again.</p>",
#             "voice_feedback": "We encountered an error generating your feedback.",
#             "voice_audio": None
#         }





# services/report/generator.py
import logging
import os
from datetime import datetime
from openai import OpenAI
from config import Config
from services.tts_service import text_to_speech
from utils.file_utils import html_to_pdf

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=Config.OPENAI_API_KEY)

def generate_interview_report(interview_data):
    try:
        # Calculate interview duration
        duration = "N/A"
        if interview_data['start_time'] and interview_data['end_time']:
            duration_seconds = (interview_data['end_time'] - interview_data['start_time']).total_seconds()
            minutes = int(duration_seconds // 60)
            seconds = int(duration_seconds % 60)
            duration = f"{minutes}m {seconds}s"

        # ✅ Build actual Q-A-Rating pairs from conversation history
        conversation_history = interview_data.get('conversation_history', [])
        ratings = interview_data.get('ratings', [])

        paired_questions = []
        rating_index = 0  # For sequentially mapping ratings

        for idx, item in enumerate(conversation_history):
            if item.get('speaker', '').lower() == 'bot':
                question_text = item.get('text', '').strip()

                # Find next user's answer
                answer_text = "Not Answered"
                for next_item in conversation_history[idx+1:]:
                    if next_item.get('speaker', '').lower() == 'user':
                        answer_text = next_item.get('text', '').strip() or "Not Answered"
                        break

                # Get matching rating
                rating_score = ratings[rating_index] if rating_index < len(ratings) else 0
                rating_index += 1

                paired_questions.append((question_text, answer_text, rating_score))

        # ✅ Average rating calculation based on actual questions
        valid_ratings = [score for _, _, score in paired_questions]
        avg_rating = sum(valid_ratings) / len(valid_ratings) if valid_ratings else 0

        logger.debug(f"Average rating: {avg_rating:.1f}, based on {len(paired_questions)} questions actually asked")

        # Determine status based on average rating
        if avg_rating >= 7:
            status_class = "selected"
            overall_recommendation = "✅ Selected"
        elif 4 <= avg_rating < 7:
            status_class = "onhold"
            overall_recommendation = "⏳ On Hold"
        else:
            status_class = "rejected"
            overall_recommendation = "❌ Rejected"

        # Skill distribution
        questions = interview_data.get('questions', [])
        question_topics = interview_data.get('question_topics', [])
        technical_scores, communication_scores, behavioral_scores = [], [], []

        for i, (question, topic, rating) in enumerate(zip(questions, question_topics, ratings)):
            topic_lower = topic.lower() if topic else ""
            if "technical" in topic_lower or i < 10:
                technical_scores.append(rating)
            elif "experience" in topic_lower or "role" in topic_lower or i < 15:
                behavioral_scores.append(rating)
            communication_scores.append(rating * 0.4)

        technical_avg = sum(technical_scores) / len(technical_scores) if technical_scores else 5
        behavioral_avg = sum(behavioral_scores) / len(behavioral_scores) if behavioral_scores else 5
        communication_avg = sum(communication_scores) / len(communication_scores) if communication_scores else 5

        total = max(technical_avg + communication_avg + behavioral_avg, 0.01)
        technical_pct = (technical_avg / total) * 100
        communication_pct = (communication_avg / total) * 100
        behavioral_pct = 100 - technical_pct - communication_pct

        # Bar chart HTML
        bar_chart_html = f"""
        <div style=\"font-family: Arial, sans-serif; max-width: 400px; margin: 20px auto;\">
            <h4 style=\"text-align: center;\">Skill Distribution</h4>
            <div style=\"margin-bottom: 15px;\">
                <span style=\"display: inline-block; width: 120px; font-weight: bold;\">Technical </span>
                <div style=\"display: inline-block; width: 200px; background-color: #e0e0e0; border-radius: 5px; overflow: hidden;\">
                    <div style=\"width: {min(technical_pct, 100)}%; background-color: #4CAF50; height: 20px;\"></div>
                </div>
                <span style=\"margin-left: 10px;\">{technical_pct:.1f}%</span>
            </div>
            <div style=\"margin-bottom: 15px;\">
                <span style=\"display: inline-block; width: 120px; font-weight: bold;\">Communication </span>
                <div style=\"display: inline-block; width: 200px; background-color: #e0e0e0; border-radius: 5px; overflow: hidden;\">
                    <div style=\"width: {min(communication_pct, 100)}%; background-color: #2196F3; height: 20px;\"></div>
                </div>
                <span style=\"margin-left: 10px;\">{communication_pct:.1f}%</span>
            </div>
            <div style=\"margin-bottom: 15px;\">
                <span style=\"display: inline-block; width: 120px; font-weight: bold;\">Behavioral </span>
                <div style=\"display: inline-block; width: 200px; background-color: #e0e0e0; border-radius: 5px; overflow: hidden;\">
                    <div style=\"width: {min(behavioral_pct, 100)}%; background-color: #FFC107; height: 20px;\"></div>
                </div>
                <span style=\"margin-left: 10px;\">{behavioral_pct:.1f}%</span>
            </div>
        </div>
        """
        # visual_analysis_html = "<h2>Visual Analysis</h2>\n<ul>\n"
        # for idx, (question, answer, score) in enumerate(paired_questions, 1):
        #     displayed_answer = answer if answer.strip() else "Not Answered"
        #     visual_analysis_html += (
        #         f"<li><strong>Q{idx}.</strong> {question}<br>"
        #         f"<em>Answer:</em> {displayed_answer}<br>"
        #         f"<em>Score:</em> {score}/10</li>\n"
        #     )
        # visual_analysis_html += "</ul>\n"


        conversation_history_text = "\n".join([
            f"{item['speaker']}: {item['text']}"
            for item in interview_data['conversation_history']
            if 'speaker' in item
        ])

        report_prompt = f"""
You are an expert AI HR assistant responsible for generating professional interview evaluation reports.
The following interview was conducted for the role of {interview_data['role']}.

### Candidate Overview:
- 🎓 Experience Level: {interview_data['experience_level']}
- 🕒 Years of Experience: {interview_data['years_experience']}
- ⏱ Interview Duration: {duration}
- ⭐ Average Interviewer Rating: {avg_rating:.1f}/10

### 📜 Interview Transcript:
{conversation_history_text}

## 🎯 Your Task:
Generate a detailed interview evaluation report using the transcript and rating context.

Format the output in clean HTML with semantic structure, using <h2>, <table>, and <div>.

IMPORTANT:
- Use this exact recommendation in the <h2>Overall Recommendation</h2> section: {overall_recommendation}
- Do not contradict this recommendation.

✅ Include the following 6 sections:


Sections:
<h2>Interview Summary</h2>
- Provide a concise overview of how the interview went.
- Mention how well the candidate communicated, handled technical questions, and overall impression.

<h2>Key Strengths</h2>:
- Show a table with exactly 2 columns: 'Aspect' and 'Evidence from Responses'.
- Include 2-4 rows, each identifying a strength (e.g., Problem Solving, Communication, Domain Expertise) and quoting or summarizing a relevant answer from the transcript.
- Use the following HTML table structure:
  <table style="width: 100%; border-collapse: collapse;">
    <tr style="border: 1px solid #000;">
      <th style="border: 1px solid #000; padding: 8px;">Aspect</th>
      <th style="border: 1px solid #000; padding: 8px;">Evidence from Responses</th>
    </tr>
    <tr style="border: 1px solid #000;">
      <td style="border: 1px solid #000; padding: 8px;">[Strength Aspect]</td>
      <td style="border: 1px solid #000; padding: 8px;">[Quote or Summary]</td>
    </tr>
    <!-- Additional rows as needed -->
  </table>

<h2>Areas for Improvement</h2>: 
- Show a table with exactly 2 columns: 'Aspect to Improve' and 'Suggestion or Evidence'.
- Include 2-4 rows, each identifying an area for improvement (e.g., Confidence, Project Depth) and providing actionable feedback or evidence from the transcript.
- Use the following HTML table structure:
  <table style="width: 100%; border-collapse: collapse;">
    <tr style="border: 1px solid #000;">
      <th style="border: 1px solid #000; padding: 8px;">Aspect to Improve</th>
      <th style="border: 1px solid #000; padding: 8px;">Suggestion or Evidence</th>
    </tr>
    <tr style="border: 1px solid #000;">
      <td style="border: 1px solid #000; padding: 8px;">[Improvement Aspect]</td>
      <td style="border: 1px solid #000; padding: 8px;">[Feedback or Evidence]</td>
    </tr>
    <!-- Additional rows as needed -->
  </table>

<h2>Visual Analysis</h2>: Use this question-wise analysis:

<h2>Skill Distribution</h2>: Use this chart:
{bar_chart_html}

<h2>Overall Recommendation</h2>:

- Clearly state whether the candidate is:
  - ✅ Selected
  - ⏳ On Hold
  - ❌ Rejected
- Mention the candidate’s status.
- Write **2-3 professional and varied bullet points** inside a <ul> HTML list to explain the decision.

Important instructions:
- Use professional, human-like language.
- Avoid repetitive wording across different candidates.
- Vary your tone, phrasing, and bullet point structure naturally.
- Mention candidate strengths, weaknesses, or observations as justification.
- Ensure each output feels unique and expert-written.

Input data to consider:
- Candidate's total rating out of 10
- Key strengths
- Key improvement areas
- Interview observations

Ensure the final output is creative, professional, and recruiter-ready for inclusion in an official interview report.

## Requirements:
- Return the entire content as pure HTML.
- Do not add external CSS or scripts.
- Ensure tables for 'Key Strengths' and 'Areas for Improvement' strictly follow the provided HTML structure with inline CSS.
- Use <p> tags for text content outside tables.
- Do not use markdown or other formats; output must be valid HTML.
"""
        logger.debug("Sending prompt to OpenAI for HTML report generation")
        report_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional HTML interview report writer."},
                {"role": "user", "content": report_prompt}
            ],
            max_tokens=2000,
            temperature=0.5
        )

        report_content = report_response.choices[0].message.content.strip()

        # ✅ Remove markdown code block markers from response
        if report_content.startswith("```html"):
            report_content = report_content.replace("```html", "").strip()
        if report_content.endswith("```"):
            report_content = report_content[:-3].strip()
        
        logger.debug("Generated HTML Report:\n" + report_content)

        # Save to PDF
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"interview_report_{timestamp}.pdf"
        pdf_path = os.path.join("./reports", pdf_filename)
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
        html_to_pdf(report_content)

        # Generate voice summary
        voice_prompt = f"Summarize this interview report in 5–6 spoken lines:\n{report_content}"
        voice_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You summarize interviews as voice feedback."},
                {"role": "user", "content": voice_prompt}
            ],
            max_tokens=300,
            temperature=0.5
        )

        voice_feedback = voice_response.choices[0].message.content.strip()
        logger.debug(f"Generated voice feedback: {voice_feedback}")

        logger.debug("Converting voice feedback to audio")
        voice_audio = text_to_speech(voice_feedback)

        return {
            "status": "success",
            "report": report_content,
            "report_pdf_path": pdf_path,
            "voice_feedback": voice_feedback,
            "voice_audio": voice_audio,
            "status_class": status_class,
            "avg_rating": avg_rating,
            "duration": duration
        }

    except Exception as e:
        logger.error(f"Error generating report: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "report": "<p>Error generating report. Please try again.</p>",
            "voice_feedback": "We encountered an error generating your feedback.",
            "voice_audio": None
        }