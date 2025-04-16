import random
from fastapi import APIRouter, Header, Depends
from app.chatbot.spacy_intent import detect_intent
from app.routes.account_routes import get_user_id_from_token
from app.database import get_db
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models.account import Account
from app.models.transaction import Transaction
from app.chatbot.faq import get_faq_response, faq_responses
from app.chatbot.parser import extract_transfer_details
from app.chatbot.spacy_parser import extract_entities_spacy
from app.chatbot.sentiment_analyzer import analyze_sentiment

router = APIRouter(prefix="/api/chat", tags=["Auth", "Chatbot"])

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

PENDING_TRANSFERS = {}
PENDING_FAQ_SUGGESTIONS = {}
PENDING_ESCALATIONS = {} 
PENDING_ACCOUNT_CREATION = {}

@router.post("/", response_model=ChatResponse)
def chat_endpoint(
    request: ChatRequest,
    token: str = Header(...),
    db: Session = Depends(get_db)
):
    user_id = get_user_id_from_token(token, db)
    message = request.message.strip()
    sentiment = analyze_sentiment(message)
    if sentiment == "negative":
        PENDING_ESCALATIONS[user_id] = True
        return {"reply": "I'm sensing some frustration. Would you like to speak with an agent?"}

    confirmation_phrases = ["yes", "confirm", "go ahead", "please do", "proceed"]
    cancel_phrases = ["no", "cancel", "nevermind", "stop"]

    # Confirmation logic
    if message.lower() in confirmation_phrases:
        if user_id in PENDING_FAQ_SUGGESTIONS:
            pending_faq = PENDING_FAQ_SUGGESTIONS.pop(user_id, None)
            return {"reply": faq_responses.get(pending_faq, "Hmm, I couldn’t find that answer anymore.")}

        if user_id in PENDING_ESCALATIONS:
            PENDING_ESCALATIONS.pop(user_id)
            return {"reply": "I've forwarded your request. An agent will contact you shortly via email or phone. Is there anything else I can help you with in the meantime?"}

        if user_id in PENDING_TRANSFERS:
            pending = PENDING_TRANSFERS.get(user_id)
            if pending and pending.get("intent") == "transfer_money":
                amount = pending.get("amount")
                from_acc = pending.get("from_account")
                to_acc = pending.get("to_account")

                if not all([from_acc, to_acc]):
                    return {"reply": "Please specify both source and destination accounts."}
                if amount is None:
                    return {"reply": "How much would you like to transfer?"}

                PENDING_TRANSFERS.pop(user_id)
                return perform_transfer(user_id, from_acc, to_acc, amount, db)

        if user_id in PENDING_ACCOUNT_CREATION:
            pending = PENDING_ACCOUNT_CREATION.pop(user_id)
            try:
                account_type = pending.get("account_type")
                deposit = pending.get("deposit")
                new_account = Account(
                    user_id=user_id,
                    account_number = generate_unique_account_number(db),
                    account_type=account_type,
                    balance=deposit
                )
                db.add(new_account)
                db.commit()
                return {"reply": f"✅ A new {account_type} account has been created with ${deposit:.2f}!"}
            except:
                db.rollback()
                return {"reply": "Something went wrong while creating your account. Please try again later."}

        return {"reply": "🤔 I don’t have anything to confirm right now."}

    if message.lower() in cancel_phrases:
        cancelled = False
        for pending_dict in [PENDING_FAQ_SUGGESTIONS, PENDING_TRANSFERS, PENDING_ACCOUNT_CREATION, PENDING_ESCALATIONS]:
            if user_id in pending_dict:
                pending_dict.pop(user_id, None)
                cancelled = True
        return {"reply": "❌ Action cancelled." if cancelled else "There is no pending action to cancel."}

    # FAQ Handling
    faq_reply, suggested_question = get_faq_response(message)
    if faq_reply:
        if suggested_question:
            PENDING_FAQ_SUGGESTIONS[user_id] = suggested_question
        else:
            PENDING_FAQ_SUGGESTIONS.pop(user_id, None)
        return {"reply": faq_reply}
    
    # Account Creation Continuation
    if user_id in PENDING_ACCOUNT_CREATION:
        pending = PENDING_ACCOUNT_CREATION[user_id]
        if pending["account_type"] is None:
            pending["account_type"] = message.lower()
            return {"reply": "Got it! How much would you like to deposit initially?"}
        elif pending["deposit"] is None:
            try:
                deposit = float(message)
                if deposit < 0:
                    return {"reply": "Amount must be a positive number."}
                pending["deposit"] = deposit
                return {"reply": f"🧾 You want to create a {pending['account_type']} account with ${deposit:.2f}. Should I proceed? (yes/no)"}
            except ValueError:
                return {"reply": "Please enter a valid number for the deposit amount."}

    # Transfer Parsing
    parsed = extract_transfer_details(message)
    if parsed:
        reply = (
            f"Got it! You want to transfer ${parsed['amount']:.2f} "
            f"from {parsed['from_account'].title()} to {parsed['to_account'].title()}."
        )
        return {"reply": reply}

    parsed = extract_entities_spacy(message)
    if parsed:
        amount = parsed.get("amount")
        from_acc = parsed.get("from_account")
        to_acc = parsed.get("to_account")

        if user_id in PENDING_TRANSFERS:
            existing = PENDING_TRANSFERS[user_id]
            if existing.get("intent") == "transfer_money":
                amount = amount or existing.get("amount")
                from_acc = from_acc or existing.get("from_account")
                to_acc = to_acc or existing.get("to_account")

        if any([amount, from_acc, to_acc]):
            PENDING_TRANSFERS[user_id] = {
                "intent": "transfer_money",
                "amount": amount,
                "from_account": from_acc,
                "to_account": to_acc
            }
            if all([amount, from_acc, to_acc]):
                return {"reply": f"🔁 You want to transfer ${amount:.2f} from {from_acc.title()} to {to_acc.title()}. Should I proceed? (yes/no)"}

            missing = []
            if not amount:
                missing.append("the amount")
            if not from_acc:
                missing.append("from which account")
            if not to_acc:
                missing.append("to which account")
            return {"reply": f"👍 Got some details. Please tell me {' and '.join(missing)}."}

    intent = detect_intent(message.lower())
    print(f"User ID: {user_id}, Message: {message}, Intent: {intent}")

    if intent == "check_balance":
        accounts = db.query(Account).filter(Account.user_id == user_id).all()
        if not accounts:
            return {"reply": "You don't have any accounts yet."}
        reply_lines = ["💼 Account Balances:"]
        for acc in accounts:
            reply_lines.append(f"• {acc.account_type.title()} ({acc.account_number}): ${acc.balance:.2f}")
        return {"reply": "\n".join(reply_lines)}

    elif intent == "transfer_money":
        return {"reply": "To transfer funds, please go to the Transfer tab or specify the amount and accounts clearly."}

    elif intent == "view_transactions":
        user_accounts = db.query(Account.account_number).filter(Account.user_id == user_id).all()
        account_numbers = [acc.account_number for acc in user_accounts]
        transactions = (
            db.query(Transaction)
            .filter((Transaction.from_account.in_(account_numbers)) |
                    (Transaction.to_account.in_(account_numbers)))
            .order_by(Transaction.timestamp.desc())
            .limit(5)
            .all()
        )
        if not transactions:
            return {"reply": "📭 You don’t have any recent transactions."}

        reply_lines = ["📄 Your Last 5 Transactions:"]
        for i, t in enumerate(transactions, start=1):
            reply_lines.append(
                f"{i}. 🕒 {t.timestamp.date()} | 💵 ${t.amount:.2f}\n   From: {t.from_account} → To: {t.to_account}"
            )
        return {"reply": f"Here are your last 5 transactions:\n{chr(10).join(reply_lines)}"}

    elif intent == "account_summary":
        count = db.query(Account).filter(Account.user_id == user_id).count()
        return {"reply": f"You have {count} account(s)."}

    elif intent == "create_account":
        PENDING_ACCOUNT_CREATION[user_id] = {
            "intent": "create_account",
            "account_type": None,
            "deposit": None
        }
        return {"reply": "Sure! What type of account would you like to create? (e.g., chequing, savings)\nYou can also mention an initial deposit if you'd like."}

    elif intent == "greeting":
        return {"reply": "Hello! 👋 How can I assist you with your banking today?"}

    elif intent == "goodbye":
        return {"reply": "You're welcome! Have a great day 😊"}

    elif intent == "bot_capabilities":
        return {
            "reply": (
                "🤖 Here's what I can help you with:\n"
                "• 💼 Check your account balances\n"
                "• 🔁 Transfer money between your accounts\n"
                "• 📄 View your recent transactions\n"
                "• ❓ Answer FAQs like working hours and support info\n"
                "• 💬 Understand your follow-ups and guide you step-by-step\n"
                "• 🔐 Detect frustration and offer to connect with an agent\n"
                "\nJust type naturally, and I’ll do my best to assist you!"
            )
        }

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
            "amount": None,
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
    

def generate_unique_account_number(db: Session) -> int:
    while True:
        account_number = random.randint(1000000000, 9999999999)
        existing = db.query(Account).filter_by(account_number=account_number).first()
        if not existing:
            return account_number
