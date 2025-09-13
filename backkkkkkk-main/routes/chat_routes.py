from flask import Blueprint, request, jsonify
from utils.translator import translate_text
from models import supabase
import os, requests, uuid
from config import GEMINI_API_KEY

# Blueprint for chat
chat_bp = Blueprint("chat", __name__)

# Gemini API Endpoint
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# System prompt template
SYSTEM_PROMPT = """
You are ISH (Innovatrix Swasthya Health Bot), a highly knowledgeable and professional AI health assistant. 
Provide complete, medically accurate, and structured guidance including:
- Possible causes and conditions
- Suggested medications and dosages (general, non-prescriptive)
- Recommended tests/checkups
- Lifestyle/prevention advice
- Emergency guidance if required

User Context: {user_context}
User Question: {message}
Preferred Language: {lang}
"""

@chat_bp.route("/chat", methods=["POST"])
def chat():
    """
    Handles chat requests from frontend, calls Gemini API, 
    translates reply if needed, and saves chat history in Supabase.
    """
    data = request.get_json()
    if not data or "message" not in data or "lang" not in data:
        return jsonify({"error": "Missing required fields: message and lang"}), 400

    user_message = data["message"]
    language = data["lang"]
    session_id = data.get("session_id", str(uuid.uuid4()))

    # Build system prompt
    full_prompt = SYSTEM_PROMPT.replace("{user_context}", data.get("user_context", "")) \
                               .replace("{message}", user_message) \
                               .replace("{lang}", language)

    # Call Gemini API
    try:
        payload = {"contents": [{"parts": [{"text": full_prompt}]}]}
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            json=payload,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        gemini_data = response.json()

        bot_reply = (
            gemini_data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "Sorry, I couldn't process your request.")
        )
    except Exception as e:
        print("Gemini API error:", e)
        bot_reply = "I'm having trouble connecting to the AI service right now. Please try again later."

    # Translate reply into user's preferred language
    bot_reply = translate_text(bot_reply, language)

    # Save chat history into Supabase
    try:
        supabase.table("chat_history").insert({
            "session_id": session_id,
            "user_message": user_message,
            "bot_reply": bot_reply,
            "language": language
        }).execute()
    except Exception as db_error:
        print("Supabase DB error:", db_error)

    # Final response
    return jsonify({
        "reply": {"parts": [{"text": bot_reply}]},
        "session_id": session_id,
        "status": "success"
    }), 200
