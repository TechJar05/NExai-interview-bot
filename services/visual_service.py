# # services/visual_service.py

# import logging
# from services.cohere.client import co

# logger = logging.getLogger(__name__)

# def analyze_visual_response(frame_base64: str, conversation_context: list) -> str:
#     """
#     Analyzes the candidate's visual frame (as base64 string) along with recent conversation context,
#     and returns a short professional visual feedback using Cohere.
#     """
#     logger.debug("Analyzing visual response with Cohere")

#     try:
#         recent_context = conversation_context[-3:] if len(conversation_context) > 3 else conversation_context

#         prompt = f"""
# Analyze this interview candidate's appearance and environment.

# Context from conversation:
# {recent_context}

# Please provide a brief professional feedback on:
# 1. Professional appearance (if visible)
# 2. Body language and posture
# 3. Environment appropriateness
# 4. Any visual distractions

# Keep the response under 50 words. Return only the comment, no titles or extra labels.
# """
#         response = co.generate(
#             model="command-r-plus",
#             prompt=prompt,
#             max_tokens=200,
#             temperature=0.2
#         )
#         feedback = response.generations[0].text.strip()
#         logger.debug(f"Visual feedback received: {feedback}")
#         return feedback

#     except Exception as e:
#         logger.error(f"Error in visual analysis: {str(e)}", exc_info=True)
#         return None







# import logging
# import base64
# from openai import OpenAI

# logger = logging.getLogger(__name__)

# # Initialize the OpenAI client
# client = OpenAI()

# def analyze_visual_response(frame_base64: str, conversation_context: list) -> str:
#     """
#     Analyzes a candidate's visual frame (base64 image) with conversation context
#     using OpenAI's gpt-4o (Vision). Returns concise professional feedback.
#     """
#     logger.debug("Starting visual analysis with OpenAI Vision...")

#     try:
#         # Use last 3 messages of conversation context
#         recent_context = conversation_context[-3:] if len(conversation_context) > 3 else conversation_context
#         context_text = "\n".join(
#             f"{item.get('speaker', 'user').capitalize()}: {item.get('text', '')}" for item in recent_context
#         )

#         # Prepare base64 image URL
#         image_url = f"data:image/jpeg;base64,{frame_base64}"

#         response = client.chat.completions.create(
#             model="gpt-4o",  # Vision model
#             temperature=0.2,
#             max_tokens=150,
#             messages=[
#                 {
#                     "role": "system",
#                     "content": (
#                         "You are a professional HR interview observer. Based on a candidate's image and recent conversation, "
#                         "give concise feedback on visual cues like body language, attire, and background. Keep it short and professional."
#                     )
#                 },
#                 {
#                     "role": "user",
#                     "content": [
#                         {
#                             "type": "text",
#                             "text": (
#                                 f"Context:\n{context_text}\n\n"
#                                 "Image below shows the candidate during the interview. "
#                                 "Please give a short (max 50 words) visual feedback:"
#                             )
#                         },
#                         {
#                             "type": "image_url",
#                             "image_url": {"url": image_url}
#                         }
#                     ]
#                 }
#             ]
#         )

#         feedback = response.choices[0].message.content.strip()
#         logger.debug(f"Visual feedback: {feedback}")
#         return feedback

#     except Exception as e:
#         logger.error(f"Error analyzing visual input: {str(e)}", exc_info=True)
#         return None




# services/visual_service.py

import logging

from services.cohere.client import client

logger = logging.getLogger(__name__)
from services.cohere.client import client
def analyze_visual_response(frame_base64, conversation_context: list) -> str:
    """
    Analyzes the candidate's visual frame (as base64 string) along with recent conversation context,
    and returns a short professional visual feedback using Cohere.
    """
    logger.debug("Analyzing visual response with Cohere")

    try:
        # Use the last 3 conversation context items for relevance
        recent_context = conversation_context[-3:] if len(conversation_context) > 3 else conversation_context

        prompt = f"""
Analyze this interview candidate's appearance and environment.

Context from conversation:
{recent_context}

Please provide a brief professional feedback on:
1. Professional appearance (if visible)
2. Body language and posture
3. Environment appropriateness
4. Any visual distractions

Keep the response under 50 words. Return only the comment, no titles or extra labels.
"""
        # Ensure both 'messages' and 'model' are provided correctly
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Use the correct model
            messages=[{"role": "system", "content": "Analyze the visual data and provide feedback."}, 
                      {"role": "user", "content": f"Visual Frame: {frame_base64}"}, 
                      {"role": "user", "content": prompt}],  # Append the conversation context and visual data
            max_tokens=200,
            temperature=0.2
        )
        feedback = response.generations[0].text.strip()  # Ensure the text is clean and has no unwanted labels
        logger.debug(f"Visual feedback received: {feedback}")
        return feedback

    except Exception as e:
        logger.error(f"Error in visual analysis: {str(e)}", exc_info=True)
        return None
