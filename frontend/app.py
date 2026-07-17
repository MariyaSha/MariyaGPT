import os

from dotenv import load_dotenv
from flask import Flask, render_template


load_dotenv()

app = Flask(__name__)

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000",
)


@app.get("/")
def home():
    return render_template(
        "home.html",
        backend_url=BACKEND_URL,
    )
    

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/register")
def register():
    return render_template(
        "register.html",
        backend_url=BACKEND_URL,
    )


@app.get("/chat")
@app.get("/chat/<int:conversation_id>")
def chat(conversation_id=None):
    return render_template(
        "chat.html",
        backend_url=BACKEND_URL,
        conversation_id=conversation_id,
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )