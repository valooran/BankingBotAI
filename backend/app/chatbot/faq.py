faq_responses = {
    "what is your customer care number": "📞 Our customer care number is 1800-123-456.",
    "how to open an account": "🏦 You can open a new account from your dashboard under 'Accounts'.",
    "what are your working hours": "🕘 Our digital services are available 24/7. Branches operate 9 AM to 4 PM.",
    "how to reset password": "🔐 Go to the login screen and click 'Forgot Password' to reset it.",
    "how do i contact support": "📧 You can also email us at support@bankingbot.ai."
} #expand if needed

def get_faq_response(message: str) -> str | None:
    message = message.lower().strip()
    for question, answer in faq_responses.items():
        if question in message:
            return answer
    return None
