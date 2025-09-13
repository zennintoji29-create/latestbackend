from flask import Blueprint, request, jsonify
from models import supabase
import uuid

doctor_bp = Blueprint("doctor", __name__)

# ---------------- Register a Doctor ----------------
@doctor_bp.route("/doctor-register", methods=["POST"])
def register_doctor():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    specialization = data.get("specialization")
    phone = data.get("phone")

    if not all([name, email, specialization, phone]):
        return jsonify({"error": "Missing required fields"}), 400

    doctor_id = str(uuid.uuid4())
    try:
        supabase.table("doctors").insert({
            "id": doctor_id,
            "name": name,
            "email": email,
            "specialization": specialization,
            "phone": phone
        }).execute()
        return jsonify({"status": "success", "doctor_id": doctor_id}), 200
    except Exception as e:
        print("Supabase DB error:", e)
        return jsonify({"error": "Failed to register doctor"}), 500

# ---------------- Fetch Emergency Doctor ----------------
@doctor_bp.route("/emergency-doctor/<specialization>", methods=["GET"])
def emergency_doctor(specialization):
    try:
        res = supabase.table("doctors").select("*").eq("specialization", specialization).limit(1).execute()
        doctor = res.data[0] if res.data else None
        if doctor:
            return jsonify({
                "status": "success",
                "doctor_name": doctor["name"],
                "doctor_contact": doctor["phone"],
                "specialization": doctor["specialization"]
            }), 200
        else:
            return jsonify({"error": f"No doctor found for specialization '{specialization}'"}), 404
    except Exception as e:
        print("Supabase DB error:", e)
        return jsonify({"error": "Failed to fetch doctor"}), 500
