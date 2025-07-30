import logging
import re
from openai import OpenAI
from config import Config
from services.cohere.client import client  # assuming this is a fallback NLP client
from services.cohere.prompt_builder import extract_topic

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=Config.OPENAI_API_KEY)

def generate_initial_questions(role, experience_level, years_experience, jd_text, resume_text, load_conversation_fn=None):
    logger.debug("Starting OpenAI question generation")

    previous_questions = []
    if load_conversation_fn:
        previous_conversation = load_conversation_fn()
        previous_questions = [item['text'] for item in previous_conversation if 'speaker' in item and item['speaker'] == 'bot']

    resume_excerpt = resume_text or "N/A"
    jd_excerpt = jd_text or "N/A"

    prompt = f"""
You are an intelligent AI interviewer conducting a real-time voice-based interview.

The candidate has applied for the position of *{role}*

---  
 *Resume Extract*  
{resume_excerpt}

 *Job Description Extract*  
{jd_excerpt}

 *Target Role*  
{role}
---

Your task is to generate *4 smart, unique, and personalized questions* broken down as follows:

1. One *introduction question* from this list:
   - "Tell me about yourself."
   - "Can you tell me a little about yourself?"
   - "Please introduce yourself."

   🔁 Also include *one follow-up* from:
   - "What are your long-range and short-range goals/objectives?"
   - "What do you consider your 3 greatest strengths? Provide me an example of when you used your strengths."
   - "What is your greatest weakness?"
   - "What qualifications do you have that make you think you will be successful?"
   - "Why should we hire you?"
   - "Why did you decide to seek a job with us?"
   - "In what type of work environment do you perform best?..."
   - "Tell me about the best supervisor you worked with..."
   - "In what ways do you think you can make a contribution..."

2. *two technical questions* based on the JD and resume (followed by a meaningful follow-up each)

3. One *behavioral question*

4. One *ending question* preceded by a short closing statement:
   - "Thanks for sharing your responses so far."
   - Then ask one of:
     - "Is there anything else you’d like to add?"
     - "What excites you most about joining our team?"
     - etc.

📋 Format your output exactly like this (no extra characters):

Question 1: <Intro question>   
Question 2: <Technical Q1>  
Follow-up 2: <Follow-up Q1>  
Question 3: <Technical Q2>  
Follow-up 3: <Follow-up Q2>   
Question 4: <Behavioral question>  
Question 5: <Ending question>  

💡 Avoid repeating these recent questions: {previous_questions[-5:] if previous_questions else "None"}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Use "gpt-4" or "gpt-4o" for best results
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

        pattern = re.compile(r"Question\s+(\d+):\s*(.*)\nFollow-up\s+\1:\s*(.*)")
        matches = pattern.findall(script)

        for main_index, main_q, follow_up in matches:
            question_data = {
                "main": main_q.strip(),
                "follow_ups": [follow_up.strip()]
            }
            questions.append(question_data)
            topic = extract_topic(main_q.strip())
            question_topics.append(topic)

        # If behavior and closing questions weren't included with follow-ups
        remaining_lines = [line.strip() for line in script.splitlines() if line.strip().startswith("Question") and f"Question {len(matches)+1}:" in line]
        for line in remaining_lines:
            if ":" in line:
                _, qtext = line.split(":", 1)
                questions.append({"main": qtext.strip(), "follow_ups": []})
                question_topics.append(extract_topic(qtext.strip()))

        return questions[:8], question_topics[:8]

    except Exception as e:
        logger.error(f"Error generating questions with OpenAI: {str(e)}", exc_info=True)
        logger.warning("Using fallback questions instead")
        return get_fallback_questions(experience_level)


def get_fallback_questions(experience_level):
    # Simple fallback logic
    if experience_level == "fresher":
        questions = [
            {
                "main": "Tell me about your educational background.",
                "follow_ups": [
                    "Which courses did you find most useful?",
                    "What inspired you to pursue this field?"
                ]
            },
            {
                "main": "Describe a project you've worked on recently.",
                "follow_ups": [
                    "What challenges did you face?",
                    "What was your role in the team?"
                ]
            }
        ]
    else:
        questions = [
            {
                "main": "Can you walk me through your recent professional experience?",
                "follow_ups": [
                    "Which accomplishments are you most proud of?",
                    "What are your biggest strengths in this role?"
                ]
            }
        ]
    topics = [extract_topic(q["main"]) for q in questions]
    return questions, topics




# # question_generator.py 
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
# Experience Level: *{experience_level}, Years of Experience: **{years_experience}*

# ---  
#  *Resume Extract (Use this for 2 questions)*  
# {resume_excerpt}

#  *Job Description Extract (Use this for 5 questions)*  
# {jd_excerpt}

#  *Experience Info*  
# Level: {experience_level}  
# Years: {years_experience}

#  *Target Role*  
# {role}
# ---

# Your task is to generate *20 smart, unique, and personalized questions* broken down as follows:

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