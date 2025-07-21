from flask import Blueprint, session, render_template
import requests
import logging
from config import Config

logger = logging.getLogger(__name__)
view_bp = Blueprint('view_bp', __name__)

DJANGO_API_URL = Config.DJANGO_API_URL

# @view_bp.route('/jobs/interview/<token>/')
# def interview(token):
#     try:
#         # Step 1: Get interview metadata from Django
#         interview_url = f"{DJANGO_API_URL}{token}/"
#         print(f"🔍 Requesting interview metadata from: {interview_url}")
#         logger.debug(f"🔍 Requesting interview data from: {interview_url}")
#         response = requests.get(interview_url, timeout=30)

#         if response.status_code == 200:
#             data = response.json()
#             match_id = data.get('id')
#             session['id'] = match_id

#             # Step 2: Get Resume & JD using match ID
#             resume_jd_url = f"https://nexai.qwiktrace.com/api/jobs/resume-jd-by-id/{match_id}/"
#             resume_jd_response = requests.get(resume_jd_url, timeout=30)

#             if resume_jd_response.status_code == 200:
#                 resume_jd_data = resume_jd_response.json()

#                 # Save relevant fields to session
#                 session['resume_text'] = resume_jd_data.get('resume_text')
#                 session['jd_text'] = resume_jd_data.get('jd_text')
#                 session['organization_name'] = resume_jd_data.get('organization_name')
#                 session['job_title'] = resume_jd_data.get('job_title')
#                 session['email'] = resume_jd_data.get('email')
#                 session['candidate_name'] = resume_jd_data.get('candidate_name')

#                 logger.debug("✅ Resume & JD data stored in session.")
#                 full_data = {**data, **resume_jd_data}
#                 return render_template("index.html", data=full_data)

#             else:
#                 logger.warning(f"❌ Resume/JD fetch failed: {resume_jd_response.status_code}")
#                 return render_template("error.html", message="❌ Unable to fetch resume and JD."), 500

#         elif response.status_code == 403:
#             return render_template("error.html", message="✅ Interview already completed."), 403
#         elif response.status_code == 404:
#             return render_template("error.html", message="❌ Invalid or expired interview link."), 404
#         elif response.status_code == 410:
#             return render_template("error.html", message="❌ Interview link has expired."), 410
#         else:
#             logger.error(f"Unexpected error: {response.status_code} - {response.text}")
#             return render_template("error.html", message="⚠ Something went wrong. Try again later."), 500

#     except requests.Timeout:
#         logger.error("❌ Request timed out while fetching interview data.")
#         return render_template("error.html", message="⚠ Server timeout. Please try again."), 504
#     except Exception as e:
#         logger.error(f"❌ Exception during interview page load: {str(e)}")
#         return render_template("error.html", message="⚠ Unexpected server error."), 500









@view_bp.route('/jobs/interview/<token>/')
def interview(token):
    try:

        session['interview_token'] = token
        # Step 1: Get interview metadata from Django
        interview_url = f"{DJANGO_API_URL}{token}/"
        logger.debug(f"🔍 Requesting interview metadata from: {interview_url}")
        response = requests.get(interview_url, timeout=30)

        if response.status_code == 200 and response.text.strip():
            try:
                data = response.json()
            except Exception as e:
                logger.error(f"❌ Failed to parse JSON from interview metadata: {e}")
                return render_template("error.html", message="❌ Invalid interview data received."), 500

            match_id = data.get('id')
            session['id'] = match_id
             
            # Step 2: Get Resume & JD using match ID
            resume_jd_url = f"https://nexai.qwiktrace.com/api/jobs/resume-jd-by-id/{match_id}/"
            resume_jd_response = requests.get(resume_jd_url, timeout=30)

            if resume_jd_response.status_code == 200 and resume_jd_response.text.strip():
                try:
                    resume_jd_data = resume_jd_response.json()
                except Exception as e:
                    logger.error(f"❌ Failed to parse JSON from resume_jd: {e}")
                    return render_template("error.html", message="❌ Invalid resume or JD data."), 500

                # Save relevant fields to session
                session['resume_text'] = resume_jd_data.get('resume_text')
                session['jd_text'] = resume_jd_data.get('jd_text')
                session['organization_name'] = resume_jd_data.get('organization_name')
                session['job_title'] = resume_jd_data.get('job_title')
                session['email'] = resume_jd_data.get('email')
                session['candidate_name'] = resume_jd_data.get('candidate_name')

                logger.debug("✅ Resume & JD data stored in session.")
                full_data = {**data, **resume_jd_data}
                return render_template("index.html", data=full_data)
            else:
                logger.warning(f"❌ Resume/JD fetch failed: {resume_jd_response.status_code}")
                return render_template("error.html", message="❌ Unable to fetch resume and JD."), 500

        elif response.status_code == 403:
            return render_template("error.html", message="✅ Interview already completed."), 403
        elif response.status_code == 404:
            return render_template("error.html", message="❌ Invalid or expired interview link."), 404
        elif response.status_code == 410:
            return render_template("error.html", message="❌ Interview link has expired."), 410
        else:
            logger.error(f"Unexpected error: {response.status_code} - {response.text}")
            return render_template("error.html", message="⚠ Something went wrong. Try again later."), 500

    except requests.Timeout:
        logger.error("❌ Request timed out while fetching interview data.")
        return render_template("error.html", message="⚠ Server timeout. Please try again."), 504
    except Exception as e:
        logger.error(f"❌ Exception during interview page load: {str(e)}")
        return render_template("error.html", message="⚠ Unexpected server error."), 500






