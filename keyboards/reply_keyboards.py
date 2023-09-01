from aiogram.types import (KeyboardButton, ReplyKeyboardMarkup,
                           ReplyKeyboardRemove)

from lexicon.lexicon_ru import LEXICON_RU

start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=LEXICON_RU['start_b2c']),
            KeyboardButton(text=LEXICON_RU['start_b2b'])
        ]
    ],
    resize_keyboard=True
)

quiz_get_results_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=LEXICON_RU['quiz_get_result_button'])
        ]
    ],
    resize_keyboard=True
)

remove_keyboard = ReplyKeyboardRemove()
