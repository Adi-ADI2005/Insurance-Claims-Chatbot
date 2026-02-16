from flask import Flask, render_template, request, jsonify
import requests
from transformers import pipeline

app = Flask(__name__)

# ================= SCALE DOWN =================

SCALEDOWN_URL = "https://api.scaledown.xyz/compress/raw/"
API_KEY = "JbqmaZoCy270C6K6Kz4nf1sqhy36ZCtw1joPBK7N"

headers = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

# ================= AI MODEL =================

generator = pipeline(
    "text-generation",
    model="distilgpt2"
)

SYSTEM_CONTEXT = """
You are an intelligent insurance recommendation assistant.

Provide personalized guidance for:
Health Insurance
Life Insurance
Education Insurance

Explain benefits, advantages, disadvantages.
Keep answers professional and clear.

Do not repeat questions.
"""

# ================= SCALE DOWN =================

def compress_prompt(user_msg):

    payload = {
        "context": SYSTEM_CONTEXT,
        "prompt": user_msg,
        "model": "gpt-4o",
        "scaledown": {"rate": "auto"}
    }

    try:
        response = requests.post(SCALEDOWN_URL, headers=headers, json=payload)
        result = response.json()

        if "compressed_prompt" in result:
            return result["compressed_prompt"]

    except:
        pass

    return user_msg

# ================= SIMPLE RECOMMENDATION LOGIC =================

def recommend(age, income, goal):

    if goal == "health":
        return "Health Insurance is best for you. Covers hospital bills and emergencies."

    if goal == "life":
        return "Life Insurance is recommended to protect your family financially."

    if goal == "education":
        return "Education Insurance helps secure your child’s future education."

    return "Please select a valid insurance type."

# ================= ROUTES =================

@app.route("/")
def home():
    return render_template("chatbot.html")

@app.route("/chat", methods=["POST"])
def chat():

    data = request.json or {}

    # SAFE INPUT HANDLING
    age = int(data.get("age", 25))   # default age = 25
    income = data.get("income", "medium")
    goal = data.get("goal", "health")
    message = data.get("message", "")

    recommendation = recommend(age, income, goal)

    compressed = compress_prompt(message)

    final_prompt = SYSTEM_CONTEXT + "\nUser: " + compressed + "\nBot:"

    output = generator(
        final_prompt,
        max_new_tokens=150,
        temperature=0.6,
        repetition_penalty=1.3,
        do_sample=True
    )

    reply = output[0]["generated_text"].replace(final_prompt, "").strip()

    final_answer = f"""
PERSONAL RECOMMENDATION:
{recommendation}

AI EXPLANATION:
{reply}
"""

    return jsonify({"reply": final_answer})


if __name__ == "__main__":
    app.run(debug=True)
