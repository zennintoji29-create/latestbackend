from flask import Flask
from flask_cors import CORS
from routes.chat_routes import chat_bp
from routes.image_routes import image_bp
from routes.doctor_routes import doctor_bp
from routes.vaccine_routes import vaccine_bp
from routes.auth_routes import auth_bp

app = Flask(__name__)
CORS(app)

# Register Blueprints
app.register_blueprint(chat_bp, url_prefix="/chat")
app.register_blueprint(image_bp, url_prefix="/image")
app.register_blueprint(doctor_bp, url_prefix="/doctor")
app.register_blueprint(vaccine_bp, url_prefix="/vaccine")
app.register_blueprint(auth_bp, url_prefix="/auth")

@app.route("/", methods=["GET"])
def home():
    return "ISH Bot Backend is running! Use /chat, /image, /doctor, /vaccine, /auth endpoints."

@app.route("/health", methods=["GET"])
def health_check():
    return {"status": "healthy", "service": "ISH Bot API"}

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
