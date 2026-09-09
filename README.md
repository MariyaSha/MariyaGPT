# MariyaGPT

A free full-stack AI chat application with a Flask frontend, FastAPI
backend, PostgreSQL database, OpenRouter LLM provider, OpenAI Python
SDK, and NVIDIA Nemotron open-weights LLM.

The complete application is split into three main folders, with two
optional exercises included separately:

``` text
MariyaGPT/
├── frontend/
├── backend/
├── database/
└── exercises/
    ├── 01-openrouter/
    └── 02-postgresql-multiuser/
```

## Video Tutorial 🎥

Click the video below for a complete step-by-step tutorial on deploying MariyaGPT to production with Sevalla.

<a href="" target="_blank">
  <img width="600" alt="Deploy LLM Easily Thumbnail" src="https://github.com/user-attachments/assets/d0992b2e-47c0-4de0-aedd-2577cb899e33" />
</a>

## Application Preview

<img width="1200" alt="MariyaGPT application interfaces" src="https://github.com/user-attachments/assets/86acbb51-cec4-4c45-9835-839333fbd334" />

# Run locally

## 1. Clone MariyaGPT

``` bash
git clone git@github.com:MariyaSha/MariyaGPT.git
cd MariyaGPT
```

## 2. Set up PostgreSQL

MariyaGPT needs a PostgreSQL database for users, conversations, and
messages.

If PostgreSQL is not installed on Ubuntu/WSL:

``` bash
sudo apt update
sudo apt install postgresql
```

Open PostgreSQL:

``` bash
sudo -u postgres psql
```

Set a password for the default `postgres` user:

``` sql
ALTER USER postgres WITH PASSWORD 'YOUR_PASSWORD';
```

Create a database:

``` sql
CREATE DATABASE mariyagpt;
```

Exit PostgreSQL:

``` text
\q
```

Now create the MariyaGPT tables using the included schema:

``` bash
cd database

psql \
-h localhost \
-U postgres \
-d mariyagpt \
-f schema.sql
```

Enter the PostgreSQL password you created when prompted.

## 3. Configure the backend

Navigate to the backend:

``` bash
cd ../backend
```

Open the included `.env` file and replace the placeholders with your own
values:

``` env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/mariyagpt
OPENROUTER_API_KEY=YOUR_OPENROUTER_API_KEY
FRONTEND_URL=http://localhost:5000
SESSION_SECRET=YOUR_SESSION_SECRET
COOKIE_SECURE=false
COOKIE_SAMESITE=lax
```

You can generate a session secret with:

``` bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Install the backend requirements:

``` bash
pip install -r requirements.txt
```

Start the backend:

``` bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Keep this terminal running.

## 4. Configure the frontend

Open a second terminal and navigate to:

``` bash
cd MariyaGPT/frontend
```

Open the included `.env` file and set the backend URL:

``` env
BACKEND_URL=http://localhost:8000
```

Install the frontend requirements:

``` bash
pip install -r requirements.txt
```

Start the frontend:

``` bash
flask --app app run --host 0.0.0.0 --port 5000
```

Open:

``` text
http://localhost:5000
```

MariyaGPT should now be running locally.

## 5. Optional exercises

The `exercises` folder contains two small examples used in the video to
explain how parts of MariyaGPT work before putting everything together.

### 1. OpenRouter example

A minimal example showing how to connect Python to an LLM through
OpenRouter.

[View the OpenRouter exercise](./exercises/01-openrouter)

### 2. PostgreSQL multi-user example

A step-by-step example showing how to store multiple users,
conversations, and messages in PostgreSQL.

[View the PostgreSQL exercise](./exercises/02-postgresql-multiuser)

# Deploy via Sevalla

Fork this repository to your own GitHub account before deploying it so
your application can use your own code and future updates.

⭐ [Deploy your MariyaGPT fork with Sevalla](https://sevalla.com/?utm_source=pythonsimplified&utm_medium=Referral&utm_campaign=youtube)

## 1. Deploy PostgreSQL

In Sevalla:

1.  Create a new **PostgreSQL** database.
2.  Keep the database in the same location you plan to use for the
    backend.
3.  Open **Networking** and enable the **External Connection**.
4.  Copy the external database `HOST`, `USER`, `PORT`, and `DATABASE`
    values.

From the local `database` folder, run:

``` bash
psql \
-h HOST \
-U USER \
-p PORT \
-d DATABASE \
-f schema.sql
```

Replace the uppercase placeholders with the External Connection details
from Sevalla.

After the command finishes, the `users`, `conversations`, and `messages`
tables should appear in Sevalla Studio.

## 2. Deploy the backend

Create a new Sevalla application from your forked GitHub repository.

Enable **Auto Deploy**.

### Connect PostgreSQL

From the backend application's **Overview**:

**Add Internal Connection → select your PostgreSQL database**

Enable the option to add the database connection details as environment
variables.

The application expects the connection string to be named:

``` text
DATABASE_URL
```

If Sevalla creates it under a different variable name, rename it to
`DATABASE_URL`.

### Backend environment variables

Add:

``` env
COOKIE_SAMESITE=none
COOKIE_SECURE=true
SESSION_SECRET=YOUR_SESSION_SECRET
OPENROUTER_API_KEY=YOUR_OPENROUTER_API_KEY
FRONTEND_URL=none
```

`DATABASE_URL` should already come from the internal PostgreSQL
connection.

`FRONTEND_URL` is temporary at this stage. You will replace it with the
real frontend domain after creating the frontend application.

To generate a session secret:

``` bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

### Backend build settings

Go to:

**Settings → Build Strategy → Update Build Strategy**

Set the build path to:

``` text
backend
```

Then go to:

**Processes → ⋮ → Update Process**

Use:

``` bash
uvicorn app:app --host 0.0.0.0 --port 8080
```

## 3. Deploy the frontend

Create another Sevalla application from the **same GitHub repository**.

Enable **Auto Deploy** again.

### Frontend environment variable

Copy the backend application's **Domain** from its Overview page.

In the frontend application, add:

``` env
BACKEND_URL=https://YOUR-BACKEND-DOMAIN
```

Do **not** include a trailing `/`.

Now copy the frontend application's **Domain**.

Return to the backend environment variables and replace the temporary
`FRONTEND_URL` value with:

``` env
FRONTEND_URL=https://YOUR-FRONTEND-DOMAIN
```

Again, do **not** include a trailing `/`.

### Frontend build settings

Go to:

**Settings → Build Strategy → Update Build Strategy**

Set the build path to:

``` text
frontend
```

Then go to:

**Processes → ⋮ → Update Process**

Use:

``` bash
gunicorn --bind 0.0.0.0:8080 app:app
```

## 4. Automatic horizontal scaling

The frontend and backend can be scaled independently.

For each application:

**Processes → ⋮ → Update Process → Scaling → Horizontal Auto Scaling**

Choose the minimum and maximum instance count and the resource threshold
you want Sevalla to use.

## 5. Deploy

Deploy the backend first.

Once the backend is live, deploy the frontend.

Open the frontend domain and register a new user. You should now be able
to log in, create conversations, chat with the LLM through OpenRouter,
and keep the conversation history in PostgreSQL.

## 6. Update the live application

With **Auto Deploy** enabled, push future changes to the GitHub branch
connected to Sevalla:

``` bash
git add .
git status
git commit -m "your update"
git push origin main
```

Sevalla will detect the GitHub change and redeploy the affected
application.

## Tech stack

-   Python
-   Flask
-   FastAPI
-   PostgreSQL
-   OpenRouter
-   OpenAI Python SDK
-   NVIDIA Nemotron
-   GitHub
-   Sevalla

## License

MIT License
