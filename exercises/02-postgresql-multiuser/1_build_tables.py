import os

import psycopg
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def build_tables() -> None:
    """Reset and build the PostgreSQL tables for this demo."""

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DROP TABLE IF EXISTS messages;
                DROP TABLE IF EXISTS conversations;
                DROP TABLE IF EXISTS users;

                CREATE TABLE users (
                    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL
                        DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE conversations (
                    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    user_id INTEGER NOT NULL
                        REFERENCES users(id)
                        ON DELETE CASCADE,
                    title VARCHAR(100) NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL
                        DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE messages (
                    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    conversation_id INTEGER NOT NULL
                        REFERENCES conversations(id)
                        ON DELETE CASCADE,
                    role VARCHAR(20) NOT NULL
                        CHECK (role IN ('user', 'assistant')),
                    content TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL
                        DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

    print("Database tables ready.")
    print("Created: users, conversations, messages")

if __name__ == "__main__":
    build_tables()
