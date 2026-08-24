import os
from collections.abc import Generator
from datetime import datetime

import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from openai import OpenAI
from psycopg.errors import UniqueViolation
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware
from werkzeug.security import (
    check_password_hash,
    generate_password_hash,
)


load_dotenv()

app = FastAPI(title="MariyaGPT API")


DATABASE_URL = os.getenv("DATABASE_URL")
OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY"
)

FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://127.0.0.1:5000",
)

SESSION_SECRET = os.getenv(
    "SESSION_SECRET",
    "local-development-secret-change-me",
)

COOKIE_SECURE = (
    os.getenv("COOKIE_SECURE", "false").lower()
    == "true"
)

COOKIE_SAMESITE = os.getenv(
    "COOKIE_SAMESITE",
    "lax",
)


if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not configured."
    )

if not OPENROUTER_API_KEY:
    raise RuntimeError(
        "OPENROUTER_API_KEY is not configured."
    )


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)


app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    session_cookie="mariyagpt_session",
    same_site=COOKIE_SAMESITE,
    https_only=COOKIE_SECURE,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    confirm_password: str


class MessageRequest(BaseModel):
    message: str


def require_user(request: Request) -> int:
    user_id = request.session.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Please log in again.",
        )

    return user_id


def get_user_by_username(username: str):
    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    username,
                    email,
                    password_hash
                FROM users
                WHERE username = %s;
                """,
                (username,),
            )

            return cursor.fetchone()


def get_user_by_email(email: str):
    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id
                FROM users
                WHERE email = %s;
                """,
                (email,),
            )

            return cursor.fetchone()


def create_user(
    username: str,
    email: str,
    password: str,
):
    password_hash = generate_password_hash(
        password
    )

    try:
        with psycopg.connect(
            DATABASE_URL
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO users (
                        username,
                        email,
                        password_hash
                    )
                    VALUES (%s, %s, %s)
                    RETURNING
                        id,
                        username,
                        email;
                    """,
                    (
                        username,
                        email,
                        password_hash,
                    ),
                )

                return cursor.fetchone()

    except UniqueViolation as error:
        raise HTTPException(
            status_code=409,
            detail=(
                "That username or email "
                "is already registered."
            ),
        ) from error


def create_conversation(user_id: int):
    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO conversations (user_id)
                VALUES (%s)
                RETURNING
                    id,
                    title,
                    created_at;
                """,
                (user_id,),
            )

            return cursor.fetchone()


def get_conversation(
    conversation_id: int,
    user_id: int,
):
    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    title,
                    created_at
                FROM conversations
                WHERE
                    id = %s
                    AND user_id = %s;
                """,
                (
                    conversation_id,
                    user_id,
                ),
            )

            return cursor.fetchone()


def get_conversations(user_id: int):
    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    title,
                    created_at,
                    chat_number
                FROM (
                    SELECT
                        id,
                        title,
                        created_at,
                        ROW_NUMBER() OVER (
                            ORDER BY created_at, id
                        ) AS chat_number
                    FROM conversations
                    WHERE user_id = %s
                ) AS numbered_conversations
                ORDER BY created_at DESC, id DESC;
                """,
                (user_id,),
            )

            return cursor.fetchall()


def save_message(
    conversation_id: int,
    role: str,
    content: str,
):
    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO messages (
                    conversation_id,
                    role,
                    content
                )
                VALUES (%s, %s, %s);
                """,
                (
                    conversation_id,
                    role,
                    content,
                ),
            )


def get_messages(conversation_id: int):
    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    role,
                    content,
                    created_at
                FROM messages
                WHERE conversation_id = %s
                ORDER BY created_at, id;
                """,
                (conversation_id,),
            )

            return cursor.fetchall()


def serialize_datetime(value: datetime) -> str:
    return value.isoformat()


def build_conversation_label(
    chat_number: int,
    created_at: datetime,
) -> str:
    local_time = created_at.astimezone()

    formatted_time = local_time.strftime(
        "%m/%d/%Y %I:%M %p"
    )

    formatted_time = formatted_time.replace(
        " 0",
        " ",
    ).lower()

    return (
        f"Chat {chat_number} - "
        f"{formatted_time}"
    )


@app.get("/")
def root():
    return {
        "message": "MariyaGPT API is running"
    }


@app.get("/api/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/api/register")
def register(
    data: RegisterRequest,
    request: Request,
):
    username = data.username.strip()
    email = data.email.strip().lower()

    if not username:
        raise HTTPException(
            status_code=400,
            detail="Username is required.",
        )

    if not email:
        raise HTTPException(
            status_code=400,
            detail="Email is required.",
        )

    if not data.password:
        raise HTTPException(
            status_code=400,
            detail="Password is required.",
        )

    if data.password != data.confirm_password:
        raise HTTPException(
            status_code=400,
            detail="Passwords do not match.",
        )

    if get_user_by_username(username):
        raise HTTPException(
            status_code=409,
            detail="Username already exists.",
        )

    if get_user_by_email(email):
        raise HTTPException(
            status_code=409,
            detail="Email already exists.",
        )

    user = create_user(
        username,
        email,
        data.password,
    )

    request.session["user_id"] = user[0]
    request.session["username"] = user[1]

    return {
        "message": "Registration successful.",
        "user": {
            "id": user[0],
            "username": user[1],
            "email": user[2],
        },
    }


@app.post("/api/login")
def login(
    data: LoginRequest,
    request: Request,
):
    username = data.username.strip()

    if not username or not data.password:
        raise HTTPException(
            status_code=400,
            detail=(
                "Username and password "
                "are required."
            ),
        )

    user = get_user_by_username(username)

    if (
        not user
        or not check_password_hash(
            user[3],
            data.password,
        )
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password.",
        )

    request.session["user_id"] = user[0]
    request.session["username"] = user[1]

    return {
        "message": "Login successful.",
        "user": {
            "id": user[0],
            "username": user[1],
            "email": user[2],
        },
    }


@app.get("/api/session")
def get_session(request: Request):
    user_id = request.session.get("user_id")
    username = request.session.get("username")

    if user_id is None:
        return {
            "logged_in": False,
            "user": None,
        }

    return {
        "logged_in": True,
        "user": {
            "id": user_id,
            "username": username,
        },
    }


@app.post("/api/logout")
def logout(request: Request):
    request.session.clear()

    return {
        "message": "Logout successful."
    }


@app.get("/api/conversations")
def list_conversations(request: Request):
    user_id = require_user(request)

    rows = get_conversations(user_id)

    conversations = []

    for row in rows:
        conversations.append(
            {
                "id": row[0],
                "title": row[1],
                "created_at":
                    serialize_datetime(row[2]),
                "chat_number": row[3],
                "label":
                    build_conversation_label(
                        row[3],
                        row[2],
                    ),
            }
        )

    return {
        "conversations": conversations
    }


@app.post("/api/conversations")
def new_conversation(request: Request):
    user_id = require_user(request)

    conversation = create_conversation(user_id)

    return {
        "conversation": {
            "id": conversation[0],
            "title": conversation[1],
            "created_at":
                serialize_datetime(
                    conversation[2]
                ),
        }
    }


@app.get(
    "/api/conversations/{conversation_id}/messages"
)
def list_messages(
    conversation_id: int,
    request: Request,
):
    user_id = require_user(request)

    conversation = get_conversation(
        conversation_id,
        user_id,
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    rows = get_messages(conversation_id)

    messages = []

    for row in rows:
        messages.append(
            {
                "role": row[0],
                "content": row[1],
                "created_at":
                    serialize_datetime(row[2]),
            }
        )

    return {
        "conversation": {
            "id": conversation[0],
            "title": conversation[1],
            "created_at":
                serialize_datetime(
                    conversation[2]
                ),
        },
        "messages": messages,
    }


@app.post(
    "/api/conversations/{conversation_id}/messages"
)
def stream_message(
    conversation_id: int,
    data: MessageRequest,
    request: Request,
):
    user_id = require_user(request)

    conversation = get_conversation(
        conversation_id,
        user_id,
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    user_message = data.message.strip()

    if not user_message:
        raise HTTPException(
            status_code=400,
            detail="Please enter a message.",
        )

    save_message(
        conversation_id,
        "user",
        user_message,
    )

    stored_messages = get_messages(
        conversation_id
    )

    openrouter_messages = [
        {
            "role": row[0],
            "content": row[1],
        }
        for row in stored_messages
    ]

    def generate() -> Generator[str, None, None]:
        complete_response = ""

        try:
            stream = client.chat.completions.create(
                model=(
                    "nvidia/"
                    "nemotron-3-super-120b-a12b:free"
                ),
                messages=openrouter_messages[-20:],
                stream=True,
                extra_body={
                    "provider": {
                        "sort": "latency"
                    }
                },
            )

            for chunk in stream:
                token = (
                    chunk.choices[0]
                    .delta.content
                )

                if token:
                    complete_response += token
                    yield token

            if complete_response:
                save_message(
                    conversation_id,
                    "assistant",
                    complete_response,
                )

        except Exception as error:
            print(
                "OpenRouter streaming error:",
                repr(error),
            )

            yield (
                "\n\n"
                "mariyaGPT could not complete "
                "the response."
            )

    return StreamingResponse(
        generate(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
