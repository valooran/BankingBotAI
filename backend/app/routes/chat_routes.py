from fastapi import APIRouter, Header, Depends
from app.chatbot.spacy_intent import detect_intent
from app.routes.account_routes import get_user_id_from_token
from app.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from app.models.account import Account
from app.models.transaction import Transaction

router = APIRouter(prefix="/api/chat", tags=["Auth", "Chatbot"])
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

@router.post("/", response_model=ChatResponse)
def chat_endpoint(
    request: ChatRequest,
    token: str = Header(...),
    db: Session = Depends(get_db)
):
    user_id = get_user_id_from_token(token, db)
    message = request.message.strip()
    intent = detect_intent(message.lower())

    if intent == "check_balance":
        accounts = db.query(Account).filter(Account.user_id == user_id).all()
        if not accounts:
            return {"reply": "You don't have any accounts yet."}
        reply_lines = ["💼 Account Balances:"]
        for acc in accounts:
            reply_lines.append(f"• {acc.account_type.title()} ({acc.account_number}): ${acc.balance:.2f}")
        reply = "\n".join(reply_lines)
        return {"reply": reply}

    elif intent == "transfer_money":
        return {"reply": "To transfer funds, please go to the Transfer tab or specify the amount and accounts clearly."}

    elif intent == "show_transactions":
        user_accounts = db.query(Account.account_number).filter(Account.user_id == user_id).all()
        account_numbers = [acc.account_number for acc in user_accounts]
        transactions = (
            db.query(Transaction)
            .filter(
                (Transaction.from_account.in_(account_numbers)) |
                (Transaction.to_account.in_(account_numbers))
            )
            .order_by(Transaction.timestamp.desc())
            .limit(5)
            .all()
        )
        # Transactions response
        if not transactions:
            return {"reply": "📭 You don’t have any recent transactions."}

        reply_lines = ["📄 Your Last 5 Transactions:"]
        for i, t in enumerate(transactions, start=1):
            reply_lines.append(
                f"{i}. 🕒 {t.timestamp.date()} | 💵 ${t.amount:.2f}\n   From: {t.from_account} → To: {t.to_account}"
            )
        reply = "\n".join(reply_lines)
        return {"reply": f"Here are your last 5 transactions:\n{reply}"}

    elif intent == "account_summary":
        count = db.query(Account).filter(Account.user_id == user_id).count()
        return {"reply": f"You have {count} account(s)."}

    elif intent == "greeting":
        return {"reply": "Hello! 👋 How can I assist you with your banking today?"}

    elif intent == "goodbye":
        return {"reply": "You're welcome! Have a great day 😊"}

    else:
        return {"reply": "Sorry, I didn’t quite understand that. Try asking about your balance, accounts, transactions, or transfer instructions."}
