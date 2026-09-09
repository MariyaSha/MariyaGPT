import os

import psycopg
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def main() -> None:
    insert_user(
        username="mariya",
        email="mariya@pythonsimplified.org",
        password="no.js",
    )

    insert_user(
        username="batman",
        email="batman@gotham.com",
        password="catwomans_hips",
    )

    print()
    print("Users inserted successfully.")


def insert_user(
    username: str,
    email: str,
    password: str,
) -> None:
    """Insert a single user into the database."""

    password_hash = generate_password_hash(
        password
    )

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (
                    username,
                    email,
                    password_hash
                )
                VALUES (%s, %s, %s);
                """,
                (
                    username,
                    email,
                    password_hash,
                ),
            )

    print(f"Created user: {username}")

if __name__ == "__main__":
    main()