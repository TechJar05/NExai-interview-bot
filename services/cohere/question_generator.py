



# import logging
# import re
# from openai import OpenAI
# from config import Config
# from services.cohere.client import client 
# from services.cohere.prompt_builder import extract_topic

# # Initialize OpenAI client
# client = OpenAI(api_key=Config.OPENAI_API_KEY)

# logger = logging.getLogger(__name__)


# def generate_initial_questions(role, experience_level, years_experience, jd_text, resume_text, load_conversation_fn=None):
#     logger.debug("Starting OpenAI question generation")

#     previous_questions = []
#     if load_conversation_fn:
#         previous_conversation = load_conversation_fn()
#         previous_questions = [item['text'] for item in previous_conversation if 'speaker' in item and item['speaker'] == 'bot']

#     resume_excerpt = resume_text if resume_text else "N/A"
#     jd_excerpt = jd_text if jd_text else "N/A"

#     prompt = f"""
# You are an intelligent AI interviewer conducting a real-time voice-based interview.

# The candidate has applied for the position of *{role}*


# ---  
#  *Resume Extract (Use this for 2 questions)*  
# {resume_excerpt}

#  *Job Description Extract (Use this for 5 questions)*  
# {jd_excerpt}


#  *Target Role*  
# {role}
# ---

# Your task is to generate *5 smart, unique, and personalized questions* broken down as follows:

# 1. *1 introductory question to open the interview*
# 2. *2 technical questions based on Job Description* (include 1 follow-up for the second question)
# 3. *1 question based on Resume details*
# 4. *1 behavioral question assessing mindset or situational judgment*
# 5. *1 closing or role-responsibility-based question to conclude the interview*


#  Guidelines:

# - Do NOT repeat or overlap topics
# - Avoid any questions from: {previous_questions}
# - Each question must add unique value to the interview

#  Format exactly like this:
# Main Question: [question here]
# Follow-ups: [follow-up 1]
# ---

# ONLY use the above format. Do NOT include labels like "Section", "Greeting".
# """

#     try:
#         response = client.chat.completions.create(
#             model="gpt-3.5-turbo",  # Or "gpt-4" / "gpt-4o" for better results
#             messages=[
#                 {"role": "system", "content": "You are an AI interview question generator."},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.7,
#             max_tokens=2000
#         )

#         script = response.choices[0].message.content.strip()
#         logger.debug("OpenAI response received")

#         questions = []
#         question_topics = []
#         current_block = {}

#         for line in script.split("\n"):
#             line = line.strip()
#             if line.startswith("Main Question:"):
#                 if current_block.get("main"):
#                     questions.append(current_block)
#                 current_block = {
#                     "main": line.replace("Main Question:", "").strip(),
#                     "follow_ups": []
#                 }
#             elif line.startswith("Follow-ups:"):
#                 follow_ups = line.replace("Follow-ups:", "").strip().split("|")
#                 current_block["follow_ups"] = [fq.strip() for fq in follow_ups if fq.strip()][:2]
#                 if "main" in current_block:
#                     question_topics.append(extract_topic(current_block["main"]))
#             elif line == "---":
#                 if current_block.get("main"):
#                     questions.append(current_block)
#                     current_block = {}

#         if current_block.get("main"):
#             questions.append(current_block)

#         # Return only first 8 smart questions for now
#         return questions[:8], question_topics[:8]

#     except Exception as e:
#         logger.error(f"Error generating questions with OpenAI: {str(e)}", exc_info=True)
#         logger.warning("Using fallback questions instead")

#         return get_fallback_questions(experience_level)


# def get_fallback_questions(experience_level):
#     if experience_level == "fresher":
#         questions = [
#             {
#                 "main": "Welcome to the interview. Could you tell us about your educational background?",
#                 "follow_ups": [
#                     "What specific courses did you find most valuable?",
#                     "How has your education prepared you for this role?"
#                 ]
#             },
#             {
#                 "main": "What programming languages are you most comfortable with?",
#                 "follow_ups": [
#                     "Can you describe a project where you used this language?",
#                     "How did you learn it?"
#                 ]
#             },
#             {
#                 "main": "Can you explain a technical concept you learned recently?",
#                 "follow_ups": [
#                     "How have you applied this concept in practice?",
#                     "What challenges did you face while learning it?"
#                 ]
#             },
#             {
#                 "main": "Describe a time you faced a challenge in a team project.",
#                 "follow_ups": [
#                     "What was your role in resolving it?",
#                     "What did you learn from the experience?"
#                 ]
#             }
#         ]
#     else:
#         questions = [
#             {
#                 "main": "Welcome to the interview. Can you summarize your professional experience?",
#                 "follow_ups": [
#                     "Which part of your experience is most relevant here?",
#                     "What projects are you most proud of?"
#                 ]
#             },
#             {
#                 "main": "What technical challenges have you faced recently?",
#                 "follow_ups": [
#                     "How did you overcome them?",
#                     "What tools did you use?"
#                 ]
#             },
#             {
#                 "main": "Describe a situation where you led a project or a team.",
#                 "follow_ups": [
#                     "What challenges did you face in leadership?",
#                     "What did the team accomplish?"
#                 ]
#             },
#             {
#                 "main": "What's a major professional achievement you're proud of?",
#                 "follow_ups": [
#                     "What impact did it have?",
#                     "What did you learn from it?"
#                 ]
#             }
#         ]

#     question_topics = [extract_topic(q["main"]) for q in questions]
#     return questions, question_topics





# question_generator.py 
import logging
import re
from openai import OpenAI
from config import Config
from services.cohere.client import client 
from services.cohere.prompt_builder import extract_topic

# Initialize OpenAI client
client = OpenAI(api_key=Config.OPENAI_API_KEY)

logger = logging.getLogger(__name__)


def generate_initial_questions(role, experience_level, years_experience, jd_text, resume_text, load_conversation_fn=None):
    logger.debug("Starting OpenAI question generation")

    previous_questions = []
    if load_conversation_fn:
        previous_conversation = load_conversation_fn()
        previous_questions = [item['text'] for item in previous_conversation if 'speaker' in item and item['speaker'] == 'bot']

    resume_excerpt = resume_text if resume_text else "N/A"
    jd_excerpt = jd_text if jd_text else "N/A"

#     prompt = f"""
# You are an intelligent AI interviewer conducting a real-time voice-based interview.

# The candidate has applied for the position of *{role}*


# ---  
#  *Resume Extract (Use this for 2 questions)*  
# {resume_excerpt}

#  *Job Description Extract (Use this for 5 questions)*  
# {jd_excerpt}



#  *Target Role*  
# {role}
# ---

# Your task is to generate *10 smart, unique, and personalized questions* broken down as follows:

# 1. *2 technical questions from Resume*
# 2. *1 technical questions from Job Description*
# 3. *1 questions based on Experience*
# 4. *1 questions based on Role responsibilities & expectations*

#  Guidelines:
# - Each main question must be followed by 2 intelligent follow-ups (use chain of thought)
# - Do NOT repeat or overlap topics
# - Avoid any questions from: {previous_questions}
# - Each question must add unique value to the interview

#  Format exactly like this:
# Main Question: [question here]
# Follow-ups: [follow-up 1] | [follow-up 2]
# ---

# ONLY use the above format. Do NOT include labels like "Section", "Greeting".
# """
    prompt = f"""
You are an intelligent AI interviewer conducting a real-time voice-based interview.

The candidate has applied for the position of *{role}*.

---

*Resume Extract* (Use for 2 questions):  
{resume_excerpt}

*Job Description Extract* (Use for 2 questions):  
{jd_excerpt}

*Target Role*:  
{role}

---

Your task is to generate a *6-question smart interview sequence* broken down as follows:

1. Introduction Question — icebreaker type (no follow-up)
2. 1 technical question from Job Description + 1 follow-up
3. 1 technical question from Resume + 1 follow-up
4. 1 closing or reflection question (no follow-up)

Guidelines:
- Ensure JD and Resume questions are insightful and specific.
- Use only 1 follow-up for each technical question.
- Do NOT ask follow-ups for the intro or ending questions.
- Avoid question repetition and ensure flow is natural.
- Do NOT include any questions from: {previous_questions}

Output Format **strictly like this**:
Q1: [Main Question]  
Q2: [Main Question]  
 Follow-up: [Follow-up Question]  
Q3: [Main Question]  
 Follow-up: [Follow-up Question]  
Q4: [Main Question]  

ONLY follow this format. Do not include any extra text like greetings or sections.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Or "gpt-4" / "gpt-4o" for better results
            messages=[
                {"role": "system", "content": "You are an AI interview question generator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )

        script = response.choices[0].message.content.strip()
        logger.debug("OpenAI response received")

        questions = []
        question_topics = []
        current_block = {}

        for line in script.split("\n"):
            line = line.strip()
            if line.startswith("Main Question:"):
                if current_block.get("main"):
                    questions.append(current_block)
                current_block = {
                    "main": line.replace("Main Question:", "").strip(),
                    "follow_ups": []
                }
            elif line.startswith("Follow-ups:"):
                follow_ups = line.replace("Follow-ups:", "").strip().split("|")
                current_block["follow_ups"] = [fq.strip() for fq in follow_ups if fq.strip()][:2]
                if "main" in current_block:
                    question_topics.append(extract_topic(current_block["main"]))
            elif line == "---":
                if current_block.get("main"):
                    questions.append(current_block)
                    current_block = {}

        if current_block.get("main"):
            questions.append(current_block)

        # Return only first 8 smart questions for now
        return questions[:8], question_topics[:8]

    except Exception as e:
        logger.error(f"Error generating questions with OpenAI: {str(e)}", exc_info=True)
        logger.warning("Using fallback questions instead")

        return get_fallback_questions(experience_level)


def get_fallback_questions(experience_level):
    if experience_level == "fresher":
        questions = [
            {
                "main": "Welcome to the interview. Could you tell us about your educational background?",
                "follow_ups": [
                    "What specific courses did you find most valuable?",
                    "How has your education prepared you for this role?"
                ]
            },
            {
                "main": "What programming languages are you most comfortable with?",
                "follow_ups": [
                    "Can you describe a project where you used this language?",
                    "How did you learn it?"
                ]
            },
            {
                "main": "Can you explain a technical concept you learned recently?",
                "follow_ups": [
                    "How have you applied this concept in practice?",
                    "What challenges did you face while learning it?"
                ]
            },
            {
                "main": "Describe a time you faced a challenge in a team project.",
                "follow_ups": [
                    "What was your role in resolving it?",
                    "What did you learn from the experience?"
                ]
            }
        ]
    else:
        questions = [
            {
                "main": "Welcome to the interview. Can you summarize your professional experience?",
                "follow_ups": [
                    "Which part of your experience is most relevant here?",
                    "What projects are you most proud of?"
                ]
            },
            {
                "main": "What technical challenges have you faced recently?",
                "follow_ups": [
                    "How did you overcome them?",
                    "What tools did you use?"
                ]
            },
            {
                "main": "Describe a situation where you led a project or a team.",
                "follow_ups": [
                    "What challenges did you face in leadership?",
                    "What did the team accomplish?"
                ]
            },
            {
                "main": "What's a major professional achievement you're proud of?",
                "follow_ups": [
                    "What impact did it have?",
                    "What did you learn from it?"
                ]
            }
        ]

    question_topics = [extract_topic(q["main"]) for q in questions]
    return questions, question_topics