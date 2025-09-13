import os
from datetime import date
from supabase import create_client
from twilio.rest import Client

# -------------------
# Supabase client
# -------------------
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY"))

# -------------------
# Twilio client
# -------------------
twilio_client = Client(os.getenv("TWILIO_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
FROM_WHATSAPP = os.getenv("TWILIO_WHATSAPP_FROM")


# -------------------
# Send WhatsApp message
# -------------------
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


# -------------------
# Send due reminders for today
# -------------------
def send_due_reminders():
    today = date.today()

    # Fetch unsent reminders
    result = supabase.table("vaccine_schedule") \
        .select("id, vaccine_name, date, user_id, reminder_sent") \
        .eq("reminder_sent", False).execute()

    for row in result.data:
        if str(row["date"]) == str(today):  # due today
            user = supabase.table("users").select("phone").eq("id", row["user_id"]).single().execute()
            phone = user.data["phone"]

            msg = f"💉 Reminder: Your vaccine '{row['vaccine_name']}' is scheduled for today."
            send_whatsapp(phone, msg)

            # mark reminder sent
            supabase.table("vaccine_schedule").update({"reminder_sent": True}).eq("id", row["id"]).execute()


# -------------------
# Schedule WhatsApp reminder (used by vaccine_routes)
# -------------------
def schedule_whatsapp_reminder(user_id, vaccine_name, reminder_date):
    """
    Schedule a WhatsApp reminder. For now, sends immediately.
    In production, you can integrate APScheduler or Celery to send at the reminder_date.
    """
    user = supabase.table("users").select("phone").eq("id", user_id).single().execute()
    phone = user.data["phone"]

    msg = f"💉 Reminder: Your vaccine '{vaccine_name}' is scheduled for {reminder_date}."
    send_whatsapp(phone, msg)

    # Optionally mark as scheduled/sent
    supabase.table("vaccine_schedule").update({"reminder_sent": True}).eq("user_id", user_id).execute()
