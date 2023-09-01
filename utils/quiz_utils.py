import random
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from models.quiz import QuizAnswer
from lexicon.lexicon_ru import LEXICON_RU


async def calculate_yes_percent(session: AsyncSession, user_id: int, status: str) -> float:
    yes_count: int = (await session.execute(
        select(func.count()).where(
            QuizAnswer.user_id == user_id,
            QuizAnswer.answer == True
        )
    )).scalar()
    yes_percent = yes_count / len(LEXICON_RU[status]['quiz_questions']) * 100
    return yes_percent

def generate_random_uid():
    uid = random.randint(100000, 999999)
    return uid
