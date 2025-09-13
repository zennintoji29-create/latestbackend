# workers/reminder.py
import time
from datetime import datetime, timezone
from models import supabase
from utils.twilio_client import send_whatsapp, send_sms

CHECK_INTERVAL = 60  # check every 1 minute

while True:
    try:
        now = datetime.now(timezone.utc)
        # fetch due reminders
        response = supabase.table("reminders").select("*").eq("sent", False).lte("reminder_time", now.isoformat()).execute()
        reminders = response.data or []

        for r in reminders:
            msg = r["message"]
            phone = r["phone_number"]
            channel = r.get("channel", "whatsapp")

            success = send_whatsapp(phone, msg) if channel == "whatsapp" else send_sms(phone, msg)

            if success:
                supabase.table("reminders").update({"sent": True}).eq("id", r["id"]).execute()
                print(f"✅ Reminder sent to {phone}")
    except Exception as e:
        print("Reminder Worker Error:", e)

    time.sleep(CHECK_INTERVAL)
