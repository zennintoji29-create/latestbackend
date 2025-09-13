import base64

def encode_image_to_base64(file_bytes):
    return base64.b64encode(file_bytes).decode("utf-8")

def calculate_score(correct_answers, total_questions):
    if total_questions == 0:
        return 0
    return round((correct_answers / total_questions) * 100, 2)
