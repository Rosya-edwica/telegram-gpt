from aiogram import Bot, executor, Dispatcher, types
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

from datetime import datetime, timedelta
import os

import gpt

    
bot = Bot(os.getenv("BOT_TOKEN"))
dp = Dispatcher(bot)

scheduler = AsyncIOScheduler()
scheduler.start()


@dp.message_handler(commands='start')
async def run_bot(message: types.Message):
    await message.answer('Привет от GPT-4! Я могу ответить на все твои вопросы')

@dp.message_handler()
async def echo(message: types.Message):
    msg = await bot.send_message(message.chat.id, "⏳ Подготовка ответа...", reply_to_message_id=message.message_id)
    gpt_answer = gpt.send_request(message.text)
    
    date = datetime.now() + timedelta(seconds=1) 
    print(f"Message: {message.text}\nAnswer: {gpt_answer}")
    scheduler.add_job(change_message, "date", run_date=date, kwargs={"message": msg, "text": gpt_answer + f"\n\nВремя выполнения запроса: {end_time}"})


async def change_message(message: types.Message, text: str):
    await message.edit_text(text)


if __name__ == "__main__":
    env = load_dotenv(".env")
    if not env:
        exit("Создайте файл .env")
    executor.start_polling(dp, skip_updates=True)
