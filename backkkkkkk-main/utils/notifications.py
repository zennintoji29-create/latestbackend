from supabase import create_client
import os
from twilio.rest import Client

# Supabase
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY"))

# Twilio
twilio_client = Client(os.getenv("TWILIO_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
FROM_WHATSAPP = os.getenv("TWILIO_WHATSAPP_FROM")

def send_whatsapp(to_number, body):
    try:
        message = twilio_client.messages.create(
            from_=FROM_WHATSAPP,
            to=f"whatsapp:{to_number}",
            body=body
        )
        print("✅ Sent:", message.sid)
    except Exception as e:
        print("❌ Error:", e)

def send_due_reminders():
    """Fetch upcoming vaccines and send WhatsApp reminders."""
    from datetime import date
    today = date.today()

    # Find unsent reminders
    result = supabase.table("vaccine_schedules") \
        .select("id, vaccine_name, scheduled_date, user_id, reminder_sent") \
        .eq("reminder_sent", False).execute()

    for row in result.data:
        if str(row["scheduled_date"]) == str(today):  # due today
            # Get phone from users
            user = supabase.table("users").select("phone").eq("id", row["user_id"]).single().execute()
            phone = user.data["phone"]

            msg = f"💉 Reminder: Your vaccine '{row['vaccine_name']}' is scheduled for today."
            send_whatsapp(phone, msg)

            # mark reminder sent
            supabase.table("vaccine_schedules").update({"reminder_sent": True}).eq("id", row["id"]).execute()
