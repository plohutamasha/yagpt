import asyncio
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import ClientSession
from aiogram.filters.command import Command

load_dotenv()

YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет! Я бот, который отвечает с помощью YandexGPT. Спроси меня.")


@dp.message(F.text)
async def process_message(message: types.Message):

    user_message = message.text
    answer = await get_yandexgpt_response(user_message)
    await message.answer(answer)


async def get_yandexgpt_response(text: str):
    async with ClientSession() as session:
        async with session.post(
            url='https://llm.api.cloud.yandex.net/foundationModels/v1/completion',
            headers={
                'Authorization': f'Api-Key {YANDEX_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
              "modelUri": "gpt://b1gtaeb50nrj2otgpbgv/yandexgpt-lite",
              "completionOptions": {
                "stream": False,
                "temperature": 0.7,
                "maxTokens": "1000"
              },
              "messages": [
                {
                  "role": "system",
                  "text": text
                }
              ]
            }
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data['result']['alternatives'][0]['message']['text']
            else:
                return f"Произошла ошибка"


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
