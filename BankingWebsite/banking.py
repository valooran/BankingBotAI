from flask import Flask, render_template, request, redirect, url_for, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import re, json

app = Flask(__name__)

# Load TinyLlama model
model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
chatbot = pipeline("text-generation", model=model, tokenizer=tokenizer)

# Mock user database
users = {"admin": "admin"}

# Memory/state
user_name = None
onboarded = False
collecting_account_info = False
account_type = None
pending_account_data = {}

# Chat memory for TinyLlama
conversation_history = []
MAX_HISTORY = 3

# Phrase groups for "Did you mean..."
PHRASE_GROUPS = {
    "account_balance": [
        "account balance", "check balance", "current balance", "savings balance",
        "my balance", "view my account", "account info", "account statement", "account summary"
    ],
    "transfer_money": [
        "transfer", "transfer money", "send money", "make a payment", "fund transfer",
        "how to send money", "online transfer", "neft", "imps", "upi", "rtgs"
    ],
    "credit_card": [
        "credit card", "apply credit card", "credit card benefits", "card services",
        "card limit", "lost card", "report stolen card", "credit score"
    ],
    "loan": [
        "loan eligibility", "apply for loan", "loan details", "loan requirements",
        "home loan", "personal loan", "car loan", "loan interest", "loan application"
    ]
}

def is_valid_email(email):
    return bool(re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email))

def is_valid_phone(phone):
    return bool(re.fullmatch(r"\d{10}", phone))

def save_account(data):
    with open("accounts.json", "a") as f:
        f.write(json.dumps(data) + "\n")

@app.route('/')
def login_page():
    return render_template("index.html")

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    if username in users and users[username] == password:
        return redirect(url_for("homepage"))
    return "Invalid credentials", 401

@app.route('/homepage')
def homepage():
    return render_template("homepage.html")

@app.route('/chatbot', methods=['POST'])
def chatbot_route():
    global user_name, onboarded, collecting_account_info, account_type, pending_account_data, conversation_history

    data = request.json
    user_message = data.get("message", "").strip()
    lower_msg = user_message.lower()

    # --- Name Capture ---
    if not onboarded:
        name_patterns = [
            r"my name is ([a-zA-Z]+)",
            r"you can call me ([a-zA-Z]+)",
            r"call me ([a-zA-Z]+)",
            r"i am ([a-zA-Z]+)"
        ]
        for pattern in name_patterns:
            match = re.search(pattern, lower_msg)
            if match:
                user_name = match.group(1).capitalize()
                onboarded = True
                return jsonify({"response": f"Nice to meet you, {user_name}! 👋 How can I assist you today?"})

        greetings = ["hi", "hello", "hey", "yo", "greetings"]
        if lower_msg.strip().isalpha() and lower_msg not in greetings and len(lower_msg) < 20:
            user_name = user_message.capitalize()
            onboarded = True
            return jsonify({"response": f"Nice to meet you, {user_name}! 👋 How can I assist you today?"})
        elif lower_msg in greetings and not onboarded:
            return jsonify({"response": "Hi there! 👋 I didn’t catch your name. What should I call you?"})

    # --- Account Creation Flow ---
    if any(phrase in lower_msg for phrase in [
        "create account", "open account", "register", "new account", "start account",
        "how to create an account", "sign up for account", "create savings account", "create checking account",
        "open savings account", "open checking account", "apply for savings", "apply for checking"
    ]):
        collecting_account_info = True
        if "savings" in lower_msg:
            account_type = "savings"
            return jsonify({"response": "Great! You're applying for a savings account. Please provide your email address. 📧"})
        elif "checking" in lower_msg:
            account_type = "checking"
            return jsonify({"response": "Great! You're applying for a checking account. Please provide your email address. 📧"})
        else:
            account_type = None
            return jsonify({"response": f"{user_name}, I can help with that! What type of account do you want to create? Please specify if it's a savings or checking account."})

    if collecting_account_info and account_type:
        if "email" not in pending_account_data:
            if is_valid_email(user_message):
                pending_account_data["email"] = user_message
                return jsonify({"response": "Great! Now please provide your phone number. 📱"})
            else:
                return jsonify({"response": "Hmm, that doesn’t look like a valid email. Please enter a valid email address like name@example.com."})
        elif "phone" not in pending_account_data:
            if is_valid_phone(user_message):
                pending_account_data["phone"] = user_message
                pending_account_data["name"] = user_name or "Unknown"
                save_account(pending_account_data)
                collecting_account_info = False
                pending_account_data = {}
                return jsonify({"response": f"🎉 {user_name}, your {account_type} account has been successfully created (simulated). Welcome to ABC Bank! 🏦"})
            else:
                return jsonify({"response": "Please enter a valid 10-digit phone number (e.g., 9876543210). 📱"})

    # --- Static Banking Queries ---
    if any(phrase in lower_msg for phrase in PHRASE_GROUPS["account_balance"]):
        return jsonify({"response": f"{user_name}, your current balance is ₹50,000. (Simulated) 💰"})

    if any(phrase in lower_msg for phrase in PHRASE_GROUPS["transfer_money"]):
        return jsonify({"response": f"{user_name}, you can simulate a money transfer in the 'Transfers' section. 💸 For real transfers, log in to online banking."})

    if any(phrase in lower_msg for phrase in [
        "services you offer", "what do you offer", "available services", "banking services",
        "types of accounts", "bank features", "digital banking"
    ]):
        return jsonify({"response": "We offer savings accounts, fixed deposits, loans, credit cards, online banking, and 24/7 support. 🏦"})

    if any(phrase in lower_msg for phrase in PHRASE_GROUPS["credit_card"]):
        return jsonify({"response": "ABC Bank offers Platinum, Gold, and Cashback credit cards with travel perks and up to 2% cashback. 💳"})

    if any(phrase in lower_msg for phrase in PHRASE_GROUPS["loan"]):
        return jsonify({"response": "Loan eligibility depends on your income and credit score. 📝 Check our loan calculator for estimates."})

    if any(trigger in lower_msg for trigger in ["help", "faq", "menu", "what can you do", "commands"]):
        return jsonify({
            "response": (
                "🧾 Here's what I can help you with:\n"
                "• 🏦 Open a new account\n"
                "• 💳 Credit card info\n"
                "• 💸 Check your account balance\n"
                "• 📈 Loan eligibility\n"
                "• 📞 Contact support\n"
                "• 🔄 Reset chat anytime\n"
                "• ❓ Ask me any banking-related question"
            )
        })

    if any(word in lower_msg for word in ["ok", "okay", "thanks", "thank you", "thankyou", "thx", "great", "awesome", "cool", "nice"]):
        return jsonify({"response": f"😊 Glad I could help, {user_name}! Let me know if you need anything else."})

    # --- Smart "Did You Mean..." Suggestion ---
    matched_keywords = []
    for group, phrases in PHRASE_GROUPS.items():
        for phrase in phrases:
            if phrase in lower_msg:
                matched_keywords.extend(phrases)
                break
    if matched_keywords:
        return jsonify({
            "response": (
                "🤔 Did you mean one of these?\n"
                + "\n• " + "\n• ".join(matched_keywords)
            )
        })

    # --- Fallback to TinyLlama ---
    try:
        conversation_history.append({"user": user_message})

        prompt = (
            "You are ABC, a virtual banking assistant working for ABC Bank. "
            "You help customers with banking-related queries, including account types, credit cards, loans, interest rates, and services. "
            "Keep your responses short, professional, and friendly. "
            "Do not answer questions unrelated to banking. "
            "If the phrase is unclear or outside the scope, always list the help menu"
            "If the question is unclear or outside your scope, politely guide the user back to banking topics.\n\n"
        )

        for turn in conversation_history[-MAX_HISTORY:]:
            prompt += f"Customer: {turn['user']}\n"
            if 'bot' in turn:
                prompt += f"Assistant: {turn['bot']}\n"
        prompt += "Assistant:"

        response = chatbot(prompt, max_new_tokens=120, do_sample=True, temperature=0.6)
        generated = response[0]["generated_text"]
        reply = generated.split("Assistant:")[-1].strip().split("Customer:")[0].strip()

        conversation_history[-1]["bot"] = reply
        if user_name:
            reply = f"{user_name}, {reply}"

        return jsonify({"response": reply})

    except Exception as e:
        print("Error:", e)
        return jsonify({"response": "Sorry, something went wrong while generating the response."})

@app.route('/reset', methods=['POST'])
def reset_chat():
    global user_name, onboarded, collecting_account_info, account_type, pending_account_data, conversation_history
    user_name = None
    onboarded = False
    collecting_account_info = False
    account_type = None
    pending_account_data = {}
    conversation_history = []
    return jsonify({"response": "Chat has been reset. 👋 What should I call you?"})

if __name__ == '__main__':
    app.run(debug=True)
