from fuzzywuzzy import fuzz

faq_responses = {
    "what is your customer care number": "📞 Our customer care number is 1800-123-456.",
    "what are your working hours": "🕘 Our digital services are available 24/7. Branches operate 9 AM to 4 PM.",
    "how to reset password": "🔐 Go to the login screen and click 'Forgot Password' to reset it.",
    "how do i contact support": "📧 You can also email us at support@bankingbot.ai."
}

def get_faq_response(message: str, threshold: int = 75, suggestion_threshold: int = 60) -> tuple[str | None, str | None]:
    message = message.lower().strip()
    best_match_question = None
    best_match_answer = None
    highest_score = 0

    for question, answer in faq_responses.items():
        score = fuzz.partial_ratio(message, question)
        if score > highest_score:
            best_match_question = question
            best_match_answer = answer
            highest_score = score

    if highest_score >= threshold:
        return best_match_answer, None
    elif highest_score >= suggestion_threshold:
        return f"🤔 Did you mean: \"{best_match_question}\"?", best_match_question
    
    return None, None

