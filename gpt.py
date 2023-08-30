import openai
import os
from dotenv import load_dotenv
# from async_openai import OpenAI

env = load_dotenv(".env")
if not env:
    exit("Создайте файл .env")


def send_request(query: str) -> str:
    openai.api_key = os.getenv("GPT_TOKEN")
    
    MODEL = "gpt-4"
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


# async def async_send_request(query: str) -> str:
#     OpenAI.configure(
#         api_key=os.getenv("GPT_TOKEN"),
        
#     )
#     result = await OpenAI.completions.async_create(
#         prompt=query,
#         max_tokens=4,
#         stream=True
#     )
#     print(result)