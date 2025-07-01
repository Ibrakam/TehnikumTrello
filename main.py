import asyncio
import logging
from config import dp, bot
from db import Base, engine
from handlers.main import router
import requests
from fastapi import FastAPI
from hypercorn.asyncio import serve
from hypercorn.config import Config

from db import get_db, MessageModel

app = FastAPI(docs_url='/')


async def run_bot() -> None:
    dp.include_router(router)
    await bot.delete_webhook()
    await dp.start_polling(bot)
    while True:
        await asyncio.sleep(1)


async def run_api():
    config = Config()
    config.bind = ["0.0.0.0:8000"]
    await serve(app, config)


@app.post('/add_message')
async def add_message_func(message_text: str, chat_id: int):
    url = f"https://api.telegram.org/bot/sendMessage"
    # url = f"https://api.telegram.org/bot/sendMessage"

    # Параметры запроса
    payload = {
        "chat_id": chat_id,
        "text": message_text
    }

    # Отправляем POST запрос
    response = requests.post(url, data=payload)

    # Проверяем статус ответа
    if response.status_code == 200:
        print("Сообщение успешно отправлено!")
        print(response.json())
        message_id = response.json()['result']['message_id']
        db = next(get_db())
        new_message = MessageModel(message_id=message_id, message_text=message_text)
        db.add(new_message)
        db.commit()
        logging.info(f"Сообщение с id {new_message.id} успешно добавлено в базу данных")
        return {"message": f"Сообщение с id {message_id}{new_message.id} успешно добавлено в базу данных"}

    else:

        print(f"Ошибка при отправке сообщения: {response.status_code}")
        print(response.text)
        return None


#
#
async def main():
    bot_task = asyncio.create_task(run_bot())
    api_task = asyncio.create_task(run_api())

    await asyncio.gather(bot_task, api_task)


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting bot and API...")
    asyncio.run(main())
