


# # services/scoring_service.py

# import logging
# import json
# import re
# from services.cohere.client import client  # OpenAI client

# logger = logging.getLogger(__name__)

# def evaluate_response(answer: str, question: str, role: str, experience_level: str, visual_feedback: str = None) -> float:
#     """
#     Evaluates a candidate's answer using OpenAI and returns a score from 1 to 10.
#     """

#     logger.debug(f"Evaluating response for question: {question[:60]}...")

#     # System-level instruction for OpenAI
#     system_instruction = """
# You are an expert AI interviewer.

# Score the candidate's answer strictly based on these 5 criteria:
# 1. Relevance
# 2. Knowledge depth
# 3. Clarity
# 4. Use of examples
# 5. Professionalism

# Return ONLY this valid JSON:
# {
#   "relevance": <1-10>,
#   "knowledge_depth": <1-10>,
#   "clarity": <1-10>,
#   "examples": <1-10>,
#   "professionalism": <1-10>,
#   "final_rating": <average as float>,
#   "answer_quality": "<Excellent|Good|Average|Poor>"
# }

# DO NOT explain or add any comments outside the JSON.
# """

#     user_prompt = f"""
# Evaluate the answer below for a {role} ({experience_level}) interview.

# Question: "{question}"
# Answer: "{answer.strip()}"
# Visual feedback: "{visual_feedback or 'N/A'}"

# Return only valid JSON.
# """

#     try:
#         response = client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": system_instruction},
#                 {"role": "user", "content": user_prompt}
#             ],
#             max_tokens=300,
#             temperature=0.3
#         )

#         rating_text = response.choices[0].message.content.strip()
#         logger.debug(f"OpenAI raw rating:\n{rating_text}")

#         # Attempt to parse JSON output
#         try:
#             rating_json = json.loads(rating_text)
#             final_score = float(rating_json.get("final_rating", 5))
#             return max(1.0, min(10.0, final_score))
#         except json.JSONDecodeError:
#             match = re.search(r'"final_rating"\s*:\s*(\d+(\.\d+)?)', rating_text)
#             if match:
#                 fallback = float(match.group(1))
#                 return max(1.0, min(10.0, fallback))
#             logger.warning("Could not parse rating JSON. Returning 5.0")
#             return 5.0

#     except Exception as e:
#         logger.error(f"Error in evaluate_response: {str(e)}", exc_info=True)
#         return 5.0






# services/scoring_service.py
import logging
import json
import re
from services.cohere.client import client  # OpenAI client

logger = logging.getLogger(__name__)

def evaluate_response(answer: str, question: str, role: str, experience_level: str, visual_feedback: str = None) -> float:
    """
    Evaluates a candidate's answer using OpenAI and returns a score from 1 to 10.
    Now optimized to reward effort, practical details, and technologies mentioned.
    """

    logger.debug(f"Evaluating response for question: {question[:60]}...")

    if not answer.strip():
        logger.warning(f"No answer provided for question: {question[:60]}... Assigning 0.0 score.")
        return 0.0

    system_instruction = """
You are a supportive and generous AI interviewer.

Scoring rules:
- Focus on rewarding effort, content, and real-world project experience.
- Do NOT penalize spelling, grammar, or minor mistakes.
- If the answer mentions technologies, tools, project details, or personal experience:
  → Assign HIGH scores (8 to 10).
- If the answer shows effort and partial relevance:
  → Assign good scores (7+).
- ONLY assign low scores (below 5) if:
  - The answer is empty or completely nonsensical.

Think like a helpful interviewer who appreciates practical experience.

strict rules: 
1. If the candidate's answer has very little semantic similarity with the question, still provide good scores.
2. If the candidate lacks depth/examples, avoid penalizing heavily; provide average to good scores.
3. Example: Even if an answer is partially irrelevant but lists technologies, give high marks.

Return ONLY valid JSON:
{
  "relevance": <1-10>,
  "knowledge_depth": <1-10>,
  "clarity": <1-10>,
  "examples": <1-10>,
  "professionalism": <1-10>,
  "final_rating": <average as float>,
  "answer_quality": "<Excellent|Good|Average|Poor>"
}

Do not explain or comment. Only return JSON.
"""

    user_prompt = f"""
Score the following answer generously. Assume the candidate has explained a real project or work experience.

Prioritize effort, technologies mentioned, and practical experience over grammatical correctness.

Question: "{question}"
Answer: "{answer.strip()}"
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=300,
            temperature=0.3
        )

        rating_text = response.choices[0].message.content.strip()
        logger.debug(f"OpenAI raw rating:\n{rating_text}")

        try:
            rating_json = json.loads(rating_text)
            final_score = float(rating_json.get("final_rating", 8))
            return max(1.0, min(10.0, final_score))

        except json.JSONDecodeError:
            match = re.search(r'"final_rating"\s*:\s*(\d+(\.\d+)?)', rating_text)
            if match:
                fallback = float(match.group(1))
                return max(1.0, min(10.0, fallback))
            logger.warning("Could not parse rating JSON. Returning 8.0")
            return 8.0

    except Exception as e:
        logger.error(f"Error in evaluate_response: {str(e)}", exc_info=True)
        return 8.0