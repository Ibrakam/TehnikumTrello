import logging

import requests
from fastapi import FastAPI

from db import get_db, MessageModel

app = FastAPI(docs_url='/')


@app.post('/add_message')
async def add_message_func(message_text: str, chat_id: int):
    url = f"https://api.telegram.org/bot6556699640:AAH3DRK5qHprJaSMECaTIYD9juHCyVEMKoE/sendMessage"
    # url = f"https://api.telegram.org/bot7397326527:AAHZTPHh5xanjTM9wSMcZYQZV9Tuo8A-0WQ/sendMessage"

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
