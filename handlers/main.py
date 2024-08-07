import logging

from aiogram.enums import ReactionTypeType
from aiogram.types import Message, MessageReactionUpdated, ReactionTypeEmoji
from aiogram import F, Router, Bot
from trello import TrelloClient

from config import TRELLO_API_KEY, TRELLO_API_SECRET, TRELLO_BOARD_ID, TRELLO_TOKEN
from db import get_db, MessageModel

router = Router()

trello_client = TrelloClient(
    api_key=TRELLO_API_KEY,
    api_secret=TRELLO_API_SECRET,
    token=TRELLO_TOKEN
)


def get_message(message_id):
    with next(get_db()) as db:
        message = db.query(MessageModel).filter(MessageModel.message_id == message_id).first()
        logging.info(f'{message}')
        return message.message_text if message else None

def get_m():
    with next(get_db()) as db:
        messages = db.query(MessageModel).all()
        logging.info(f'{[i.message_id for i in messages]}')
        return messages





@router.message_reaction()
async def message_reaction_handler(reaction: MessageReactionUpdated, bot: Bot):
    reaction_ = reaction.new_reaction
    print(get_m())
    print(reaction)
    emoji = [react.emoji for react in reaction_]
    old_emoji = [react.emoji for react in reaction.old_reaction]
    # if emoji[0] == "🖋️":
    # if emoji[0] == "🔥"
    if "✍" in emoji:
        message = get_message(reaction.message_id)

        # Извлечение информации из сообщения
        lines = message.split('\n')
        course = next((line.split(':')[1] for line in lines if line.startswith("Курс:")), "Неизвестно")
        date = next((line.split(':')[1] for line in lines if line.startswith("Дата:")), "Неизвестно")
        feedback = next((line.split(':')[1] for line in lines if line.startswith("Отзыв:")), "Нет отзыва")
        url_feedback = f"https://t.me/c/{reaction.chat.id}/{reaction.message_id}"

	# Создание карточки в Trello
        board = trello_client.get_board(TRELLO_BOARD_ID)
        lists = board.list_lists()
        print(lists)
        target_list = lists[0]  # Выберите нужный список

        card = target_list.add_card(
            name=f"Отзыв о курсе {course} дата {date} отзыв: {feedback}",
            desc=feedback,
            url_source=f"{url_feedback}"
        )

        await bot.set_message_reaction(
            chat_id=reaction.chat.id,
            message_id=reaction.message_id,
            reaction=[ReactionTypeEmoji(emoji="👀")]
        )

        logging.info(f"Создана карточка в Trello: {card.short_url}")

# logging.info(f"Создана карточка в Trello: {card.short_url}")
