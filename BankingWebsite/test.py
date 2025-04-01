from flask import Flask, request, jsonify
import openai

app = Flask(__name__)

# Replace with your actual API Key
OPENAI_API_KEY = "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"
openai.api_key = OPENAI_API_KEY

@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.json
    user_message = data.get("message", "")

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a helpful banking assistant."},
                  {"role": "user", "content": user_message}]
    )

    return jsonify({"response": response["choices"][0]["message"]["content"]})

if __name__ == '__main__':
    app.run(debug=True)
