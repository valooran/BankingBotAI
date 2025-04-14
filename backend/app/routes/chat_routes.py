from fastapi import APIRouter, Header, Depends
from app.chatbot.spacy_intent import detect_intent
from app.routes.account_routes import get_user_id_from_token
from app.database import get_db
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models.account import Account
from app.models.transaction import Transaction
from app.chatbot.faq import get_faq_response
from app.chatbot.parser import extract_transfer_details
from app.chatbot.spacy_parser import extract_entities_spacy

router = APIRouter(prefix="/api/chat", tags=["Auth", "Chatbot"])
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

PENDING_TRANSFERS = {}

@router.post("/", response_model=ChatResponse)
def chat_endpoint(
    request: ChatRequest,
    token: str = Header(...),
    db: Session = Depends(get_db)
):
    user_id = get_user_id_from_token(token, db)
    message = request.message.strip()
    
    confirmation_phrases = ["yes", "confirm", "go ahead", "please do", "proceed"]
    cancel_phrases = ["no", "cancel", "nevermind", "stop"]

    # Check if user is responding to a pending transfer
    if message.lower() in confirmation_phrases:
        pending = PENDING_TRANSFERS.get(user_id)
        if pending and pending.get("intent") == "transfer_money":
            amount = pending.get("amount")
            from_acc = pending.get("from_account")
            to_acc = pending.get("to_account")

            if not all([from_acc, to_acc]):
                return {"reply": "Please specify both source and destination accounts."}

            if amount is None:
                return {"reply": "How much would you like to transfer?"}

            # amount is known — proceed
            PENDING_TRANSFERS.pop(user_id)
            return perform_transfer(user_id, from_acc, to_acc, amount, db)

        return {"reply": "I don’t have a pending transfer to confirm."}

    # Cancel if user says no
    if message.lower() in cancel_phrases:
        if user_id in PENDING_TRANSFERS:
            PENDING_TRANSFERS.pop(user_id, None)
            return {"reply": "Transfer cancelled."}
        else:
            return {"reply": "There is no transfer to cancel."}
    
    #checking for FAQ match
    faq_reply = get_faq_response(message)
    if faq_reply:
        return {"reply": faq_reply}
    
    #entity recognition - rule based parsing
    parsed = extract_transfer_details(message)
    if parsed:
        reply = (
            f"Got it! You want to transfer ${parsed['amount']:.2f} "
            f"from {parsed['from_account'].title()} to {parsed['to_account'].title()}."
        )
        return {"reply": reply}
    
    # spaCy-based parser for flexible phrasing
    parsed = extract_entities_spacy(message)

    if parsed:
        # Step 1: Start with newly extracted info
        amount = parsed.get("amount")
        from_acc = parsed.get("from_account")
        to_acc = parsed.get("to_account")

        # Step 2: Merge with previously stored partial info (if any)
        if user_id in PENDING_TRANSFERS:
            existing = PENDING_TRANSFERS[user_id]
            if existing.get("intent") == "transfer_money":
                amount = amount or existing.get("amount")
                from_acc = from_acc or existing.get("from_account")
                to_acc = to_acc or existing.get("to_account")

        # Step 3: Store updated state
        if any([amount, from_acc, to_acc]):
            PENDING_TRANSFERS[user_id] = {
                "intent": "transfer_money",
                "amount": amount,
                "from_account": from_acc,
                "to_account": to_acc
            }

            if amount and from_acc and to_acc:
                return {
                    "reply": f"🔁 You want to transfer ${amount:.2f} from {from_acc.title()} to {to_acc.title()}. Should I proceed? (yes/no)"
                }

            # Step 4: Ask for remaining info
            missing = []
            if not amount:
                missing.append("the amount")
            if not from_acc:
                missing.append("from which account")
            if not to_acc:
                missing.append("to which account")

            return {
                "reply": f"👍 Got some details. Please tell me {' and '.join(missing)}."
            }
    
    intent = detect_intent(message.lower())
    print(f"User ID: {user_id}, Message: {message}, Intent: {intent}") #REMOVE LATER

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

    elif intent == "view_transactions":
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

def perform_transfer(user_id, from_type, to_type, amount, db):
    accounts = db.query(Account).filter(Account.user_id == user_id).all()

    from_acc = next((a for a in accounts if a.account_type.lower() == from_type), None)
    to_acc = next((a for a in accounts if a.account_type.lower() == to_type), None)

    if not from_acc or not to_acc:
        return {"reply": "One of the specified accounts doesn't exist."}
    if from_acc.account_number == to_acc.account_number:
        return {"reply": "Cannot transfer to the same account."}
    if from_acc.balance < amount:
        PENDING_TRANSFERS[user_id] = {
            "intent": "transfer_money",
            "amount": None,  # Reset amount to ask again
            "from_account": from_type,
            "to_account": to_type
        }

        return {
            "reply": (
                f"Insufficient funds. Your {from_type.title()} account has only ${from_acc.balance:.2f}.\n"
                f"Would you like to transfer a smaller amount instead?"
            )
        }

    try:
        from_acc.balance -= amount
        to_acc.balance += amount

        db.add(Transaction(
            from_account=from_acc.account_number,
            to_account=to_acc.account_number,
            amount=amount
        ))
        db.commit()

        return {"reply": f"Successfully transferred ${amount:.2f} from {from_type.title()} to {to_type.title()}."}
    except:
        db.rollback()
        return {"reply": "Transfer failed due to an internal error."}
