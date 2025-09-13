from twilio.rest import Client
import os

# Load from environment variables
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")  # Your Twilio phone number / sandbox number

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_sms(to_number: str, message: str):
    """
    Send SMS message using Twilio
    """
    try:
        msg = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=to_number
        )
        print(f"SMS sent: SID={msg.sid}")
        return True
    except Exception as e:
        print(f"Twilio SMS Error: {e}")
        return False

def send_whatsapp(to_number: str, message: str):
    """
    Send WhatsApp message using Twilio sandbox (need to join sandbox first).
    Example to_number: 'whatsapp:+91xxxxxxxxxx'
    """
    try:
        msg = client.messages.create(
            body=message,
            from_="whatsapp:" + TWILIO_PHONE_NUMBER,
            to="whatsapp:" + to_number
        )
        print(f"WhatsApp sent: SID={msg.sid}")
        return True
    except Exception as e:
        print(f"Twilio WhatsApp Error: {e}")
        return False
