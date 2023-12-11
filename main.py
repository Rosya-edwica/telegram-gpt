from aiogram import Bot, executor, Dispatcher, types
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

from datetime import datetime, timedelta
import json
import os
from time import perf_counter
import gpt_stat
import gpt
from kafka_test import NewProducer

bot = Bot(os.getenv("BOT_TOKEN"))
dp = Dispatcher(bot)

scheduler = AsyncIOScheduler()
scheduler.start()


@dp.message_handler(commands='start')
async def run_bot(message: types.Message):
    await message.answer('Привет от GPT-4! Я могу ответить на все твои вопросы')

    
@dp.message_handler(commands="gpt_stat_all_time")
async def gpt_stat_all_time(message: types.Message):
    data = gpt_stat.get_cost_for_all_time()
    answer = ""
    sum_cost = 0
    for key, value in data.items():
        answer += f"{key}: {value} $\n" 
        sum_cost += value
    answer += f"\nИтог: {sum_cost}\n"
    await message.answer(answer)


@dp.message_handler()
async def echo(message: types.Message):
    start_time = perf_counter()
    msg = await bot.send_message(message.chat.id, "⏳ Подготовка ответа...", reply_to_message_id=message.message_id)
    gpt_answer = await gpt.send_request(message.text)

    date = datetime.now() + timedelta(seconds=1) 
    print(f"Message: {message.text}\nAnswer: {gpt_answer}")
    end_time = round(perf_counter() - start_time)
    if type(gpt_answer) == str:
        answer = f"Ошибка: {gpt_answer}"
    else:
        kafka_message = {
            "date": str(datetime.now()),
            "user_id": message.from_user.id,
            "user_name": message.from_user.username,
            "promt": message.text,
            "answer": gpt_answer.Text,
            "cost_usd": gpt_answer.Cost.Dollar,
            "cost_rub": gpt_answer.Cost.Ruble,
            "tokens": gpt_answer.AnswerTokens + gpt_answer.QuestionTokens,
            "time_exe": end_time
        }
        if producer is not None:
            producer.send(json.dumps(kafka_message))
        answer = "\n".join((
            gpt_answer.Text,
            f"\nВремя выполнения: {end_time}",
            f"Стоимость в долларах: {gpt_answer.Cost.Dollar}$",
            f"Стоимость в рублях: {gpt_answer.Cost.Ruble}₽",
            f"Стоимость в долларах (1000 запросов): {gpt_answer.Cost.Dollar_1000}$",
            f"Стоимость в рублях (1000 запросов): {gpt_answer.Cost.Ruble_1000} ₽",
            f"Количество токенов(вопрос): {gpt_answer.QuestionTokens}", 
            f"Количество токенов(ответ): {gpt_answer.AnswerTokens}",
        ))
    scheduler.add_job(change_message, "date", run_date=date, kwargs={"message": msg, "text": answer})


async def change_message(message: types.Message, text: str):
    await message.edit_text(text)


if __name__ == "__main__":
    try:
        producer = NewProducer()
    except BaseException as Err:
        print("Не удалось подключиться к кафке: ", Err)
        producer = None
    env = load_dotenv(".env")
    if not env:
        exit("Создайте файл .env")
    executor.start_polling(dp, skip_updates=True)
