from aiogram.filters import BaseFilter
from aiogram.types import Message
from lexicon.lexicon_ru import LEXICON_RU


class StatusInMessage(BaseFilter):
    async def __call__(self, message: Message) -> bool | dict[str, str]:
        if message.text == LEXICON_RU['start_b2b']:
            return {'status': 'b2b'}
        elif message.text == LEXICON_RU['start_b2c']:
            return {'status': 'b2c'}
        else:
            return False
