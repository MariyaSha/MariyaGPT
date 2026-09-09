# PostgreSQL Multi-User Example

This mini-project shows how MariyaGPT can store different users and keep their conversations separate inside PostgreSQL.

It demonstrates:

- multiple users;
- hashed passwords;
- multiple conversations per user;
- user and assistant messages;
- retrieving complete conversation histories.

## Demo Data

The example creates two users:

- Mariya, with a conversation about Python;
- Batman, with two separate conversations.

The assistant responses are generated through OpenRouter and then stored in PostgreSQL together with each user's prompts.

## Setup

1. Create an empty PostgreSQL database.

2. Rename `.env.example` to `.env`.

3. Add your PostgreSQL connection string and OpenRouter API key:

```env
DATABASE_URL=postgresql://YOUR_USERNAME:YOUR_PASSWORD@localhost:YOUR_PORT/DATABASENAME
OPENROUTER_API_KEY=YOUR_API_KEY
```

4. Install the dependencies:

```bash
pip install -r requirements.txt
```

## Run the Exercise

Run the files in order.

### 1. Build the Database Tables

```bash
python 1_build_tables.py
```

This creates the following tables:

- `users`
- `conversations`
- `messages`

> Running this file again deletes and recreates these three tables, so use it only with the database created for this exercise.

### 2. Insert the Users

```bash
python 2_insert_users.py
```

This adds the demo users and stores their passwords as hashes instead of plaintext.

### 3. Create the Conversations

```bash
python 3_insert_conversations.py
```

This sends the example prompts to OpenRouter and stores both the prompts and LLM responses in PostgreSQL.

### 4. Read the Stored Conversations

```bash
python 4_test_database.py
```

This retrieves the users, conversations, and messages from PostgreSQL and rebuilds each conversation in the terminal.
