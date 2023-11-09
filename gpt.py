import openai
import os
import asyncio
import aiohttp
from dotenv import load_dotenv
from openai import error

from typing import NamedTuple

env = load_dotenv(".env")
if not env:
    exit("Создайте файл .env")
CURRENCY_URL = "https://api.freecurrencyapi.com/v1/latest?apikey=fca_live_WZtJCfg56qk6Rgghma1AwLKRCvXtnp4ez6p4456N&currencies=RUB"
QUESTION_TOKEN_PRICE = 0.03 / 1000
ANSWER_TOKEN_PRICE = 0.06 / 1000

class Cost(NamedTuple):
    Dollar: float
    Ruble: float
    Dollar_1000: float
    Ruble_1000: float

class Answer(NamedTuple):
    Question: str
    Text: str
    Cost: Cost
    QuestionTokens: int
    AnswerTokens: int

async def send_request(query: str) -> Answer | str:
    "Строка в случае ошибки"
    openai.api_key = os.getenv("GPT_TOKEN")
    
    MODEL = "gpt-4"
    try:
        response = await openai.ChatCompletion.acreate(
            model=MODEL,
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": query,
                },
            ],
        )
    except BaseException as err:
        match type(err):
            case error.RateLimitError:
                return "Превышен лимит запросов. Нужно проверить баланс на OpenAI"
            case error.APIConnectionError:
                return "Не удалось подключиться к OpenAI. Попробуйте снова позже или измените свой запрос"
            case error.AuthenticationError:
                return "Ошибка авторизации OpenAI"
            case error.InvalidRequestError:
                return "Не удалось подключиться к OpenAI. Измените свой запрос"
            case error.ServiceUnavailableError:
                return "OpenAI пока недоступен"
            case error.PermissionError:
                return "OpenAI не разрешает провести запрос. Нужно проверить аккаунт пользователя OpenAI"
            case _:
                return f"Не удалось подключиться к GPT. Текст ошибки: {err}"

    # answers = [i["message"]["content"] for i in response["choices"]][0]
    question_tokens = response.usage.prompt_tokens
    answer_tokens = response.usage.completion_tokens
    return Answer(
        Question=query,
        Text=[i["message"]["content"] for i in response["choices"]][0],
        AnswerTokens=answer_tokens,
        QuestionTokens=question_tokens,
        Cost=await getRequestCost(question_tokens, answer_tokens)
    )


async def getRequestCost(question_tokens: int, answer_tokens: int) -> Cost:
    dollar_cost = question_tokens * QUESTION_TOKEN_PRICE + answer_tokens * ANSWER_TOKEN_PRICE
    dollar_cost_1000 = dollar_cost * 1000

    ruble_cost = await convertDollarToRuble(dollar_cost)
    ruble_cost_1000 = ruble_cost * 1000
    return Cost(
        Dollar=round(dollar_cost, 5),
        Ruble=round(ruble_cost, 3),
        Dollar_1000=round(dollar_cost_1000, 3),
        Ruble_1000=round(ruble_cost_1000, 3)
    )

async def convertDollarToRuble(num: int | float) -> float:
    currency = await getCurrentRUR()   
    if currency is None:
        return 0 
    return currency * num


async def getCurrentRUR() -> float:
    async with aiohttp.ClientSession() as req:
        async with req.get(CURRENCY_URL) as response:
            data = await response.json()
            currency = data["data"]["RUB"]
            return currency