import openai
import os
from dotenv import load_dotenv

env = load_dotenv(".env")
if not env:
    exit("Создайте файл .env")


def send_request(query: str) -> str:
    openai.api_key = os.getenv("GPT_TOKEN")
    
    MODEL = "gpt-3.5-turbo"
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": query,
            },
        ],
        temperature=0,
    )
    answers = [i["message"]["content"] for i in response["choices"]]
    return answers[0]
