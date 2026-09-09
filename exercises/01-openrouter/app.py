import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY"
)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

response = client.chat.completions.create(
    model="nvidia/nemotron-nano-9b-v2:free",
    messages=[
        {
            "role": "user",
            "content": (
                "In one sentence, tell me why Python is so popular."
            ),
        }
    ],
)
print("Model Response:", response.choices[0].message.content)