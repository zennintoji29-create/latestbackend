from supabase import create_client
from config import SUPABASE_URL, SUPABASE_ANON_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def insert_chat(session_id, user_message, bot_reply, language, metadata={}):
    try:
        supabase.table("chat_history").insert({
            "session_id": session_id,
            "user_message": user_message,
            "bot_reply": bot_reply,
            "language": language,
            "metadata": metadata
        }).execute()
    except Exception as e:
        print("Supabase DB error:", e)
