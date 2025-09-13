from flask import Blueprint, request, jsonify
import base64, requests
from utils.translator import translate_text
from config import GEMINI_API_KEY

image_bp = Blueprint("image", __name__)
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

@image_bp.route("/analyze-image", methods=["POST"])
def analyze_image():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image_file = request.files["image"]
    language = request.form.get("lang", "en")
    user_message = request.form.get("message", "Please analyze this medical image.")

    try:
        image_bytes = image_file.read()
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        payload = {
            "contents": [
                {"parts": [
                    {"text": f"You are a medical AI. {user_message}. Provide professional, evidence-based guidance."},
                    {"inline_data": {"mime_type": image_file.mimetype, "data": image_b64}}
                ]}
            ]
        }

        headers = {"Content-Type": "application/json"}
        response = requests.post(f"{GEMINI_API_URL}?key={GEMINI_API_KEY}", json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        gemini_data = response.json()
        ai_reply = gemini_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "Sorry, I couldn't process your image.")
    except Exception as e:
        print("Gemini Vision API error:", e)
        ai_reply = "I'm having trouble analyzing the image right now. Please try again later."

    ai_reply = translate_text(ai_reply, language)
    return jsonify({"advice": ai_reply}), 200
