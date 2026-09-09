import os

import psycopg
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

MODEL = "nvidia/nemotron-nano-9b-v2:free"


def get_response(prompt: str) -> str:
    """Send a prompt to OpenRouter."""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response.choices[0].message.content


def main() -> None:
    mariya_conversation = create_conversation(
        username="mariya",
        title="Why Python Is Popular",
    )

    insert_message(
        conversation_id=mariya_conversation,
        prompt="Why is Python so popular? Answer in one sentence.",
    )

    insert_message(
        conversation_id=mariya_conversation,
        prompt="Why is JavaScript so lame?",
    )

    batman_clown_conversation = create_conversation(
        username="batman",
        title="Best Justice Strategy",
    )

    insert_message(
        conversation_id=batman_clown_conversation,
        prompt="How do I catch a psychotic clown running around Gotham City?",
    )

    batman_pr_conversation = create_conversation(
        username="batman",
        title="Bruce Wayne's PR Problem",
    )

    insert_message(
        conversation_id=batman_pr_conversation,
        prompt="What is the best thing Bruce Wayne can do to make the media lose interest in him?",
    )

    print("All conversations inserted.")


def create_conversation(
    username: str,
    title: str,
) -> int:
    """Create a conversation and return its ID."""

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id
                FROM users
                WHERE username = %s;
                """,
                (username,),
            )

            user_id = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO conversations (
                    user_id,
                    title
                )
                VALUES (%s, %s)
                RETURNING id;
                """,
                (
                    user_id,
                    title,
                ),
            )

            return cursor.fetchone()[0]


def insert_message(
    conversation_id: int,
    prompt: str,
) -> None:
    """Store a user message and the model response."""

    response = get_response(prompt)

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO messages (
                    conversation_id,
                    role,
                    content
                )
                VALUES
                    (%s, 'user', %s),
                    (%s, 'assistant', %s);
                """,
                (
                    conversation_id,
                    prompt,
                    conversation_id,
                    response,
                ),
            )

    print(f"Saved message in conversation {conversation_id}")


if __name__ == "__main__":
    main()