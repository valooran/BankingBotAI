from fastapi import APIRouter, Header, Depends
from app.chatbot.spacy_intent import detect_intent
from app.routes.account_routes import get_user_id_from_token
from app.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str

router = APIRouter(prefix="/api/chat", tags=["Auth"])

@router.post("/")
def chat_endpoint(
    request: ChatRequest,
    token: str = Header(...),
    db: Session = Depends(get_db)
):
    user_id = get_user_id_from_token(token, db)
    intent = detect_intent(request.message)

    if intent == "check_balance":
        account = db.execute(
            text("SELECT * FROM accounts WHERE user_id = :uid LIMIT 1"),
            {"uid": user_id}
        ).fetchone()
        if account:
            return {"reply": f"Your current balance is ${account.balance}."}
        else:
            return {"reply": "You don't have any accounts yet."}

    elif intent == "transfer_money":
        return {"reply": "To transfer money, please go to the Transfer tab."}

    elif intent == "show_transactions":
        return {"reply": "To view recent transactions, visit the Transactions tab."}

    elif intent == "greeting":
        return {"reply": "Hello! How can I help you today?"}

    elif intent == "goodbye":
        return {"reply": "Goodbye! Have a great day."}

    else:
        return {"reply": "Sorry, I didn't understand that. Can you rephrase?"}