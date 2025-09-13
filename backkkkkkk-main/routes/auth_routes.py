from flask import Blueprint, request, jsonify
from models import supabase
import uuid

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register-user", methods=["POST"])
def register_user():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    password = data.get("password")
    if not all([name, email, phone, password]):
        return jsonify({"error": "Missing required fields"}), 400

    user_id = str(uuid.uuid4())
    try:
        supabase.table("users").insert({
            "id": user_id,
            "name": name,
            "email": email,
            "phone": phone,
            "password": password
        }).execute()
        return jsonify({"status": "success", "user_id": user_id}), 200
    except Exception as e:
        print("Supabase DB error:", e)
        return jsonify({"error": "Failed to register user"}), 500

@auth_bp.route("/login", methods=["POST"])
def login_user():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    if not all([email, password]):
        return jsonify({"error": "Missing email or password"}), 400

    try:
        res = supabase.table("users").select("*").eq("email", email).eq("password", password).execute()
        user = res.data[0] if res.data else None
        if user:
            return jsonify({"status": "success", "user_id": user["id"]}), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        print("Supabase DB error:", e)
        return jsonify({"error": "Login failed"}), 500
