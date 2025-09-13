from flask import Blueprint, request, jsonify
from models import supabase
from utils.notifications import schedule_whatsapp_reminder
import uuid
from datetime import datetime, timedelta

vaccine_bp = Blueprint("vaccine", __name__)

# Register a vaccine
@vaccine_bp.route("/register-vaccine", methods=["POST"])
def register_vaccine():
    data = request.get_json()
    user_id = data.get("user_id")
    vaccine_name = data.get("vaccine_name")
    date_str = data.get("date")  # expected format: YYYY-MM-DD

    if not all([user_id, vaccine_name, date_str]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        vaccine_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    vaccine_id = str(uuid.uuid4())
    try:
        supabase.table("vaccine_schedule").insert({
            "id": vaccine_id,
            "user_id": user_id,
            "vaccine_name": vaccine_name,
            "date": str(vaccine_date)
        }).execute()

        # Schedule WhatsApp notification 1 day before
        reminder_time = vaccine_date - timedelta(days=1)
        schedule_whatsapp_reminder(user_id, vaccine_name, str(reminder_time))

        return jsonify({
            "status": "success",
            "vaccine_id": vaccine_id,
            "message": f"Vaccine '{vaccine_name}' scheduled for {vaccine_date}"
        }), 200

    except Exception as e:
        print("Supabase DB error:", e)
        return jsonify({"error": "Failed to register vaccine"}), 500


# Fetch all vaccines for a user
@vaccine_bp.route("/vaccine-schedule/<user_id>", methods=["GET"])
def get_user_vaccines(user_id):
    try:
        res = supabase.table("vaccine_schedule").select("*").eq("user_id", user_id).order("date", asc=True).execute()
        vaccines = res.data or []
        return jsonify({"vaccines": vaccines}), 200
    except Exception as e:
        print("Supabase DB error:", e)
        return jsonify({"error": "Failed to fetch vaccines"}), 500
