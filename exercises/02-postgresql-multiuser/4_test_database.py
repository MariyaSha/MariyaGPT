import os

import psycopg
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def test_database() -> None:
    """Retrieve and display all stored conversations."""

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    users.username,
                    conversations.title,
                    messages.role,
                    messages.content
                FROM users
                JOIN conversations
                    ON conversations.user_id = users.id
                JOIN messages
                    ON messages.conversation_id =
                        conversations.id
                ORDER BY
                    users.id,
                    conversations.id,
                    messages.id;
                """
            )

            rows = cursor.fetchall()

    current_user = None
    current_conversation = None

    for username, title, role, content in rows:
        if username != current_user:
            current_user = username
            current_conversation = None

            print()
            print("=" * 60)
            print(username.upper())
            print("=" * 60)

        if title != current_conversation:
            current_conversation = title

            print()
            print(f"Conversation: {title}")
            print("-" * 60)

        speaker = (
            username.capitalize()
            if role == "user"
            else "Assistant"
        )

        print()
        print(f"{speaker}:")
        print(content)

    print()
    print("Database test complete.")


if __name__ == "__main__":
    test_database()