from typing import Optional

from sqlalchemy import distinct, not_, exists
from sqlalchemy.sql.elements import and_

from models.base import Base
from models.task import Task
from models.task_status import TaskStatus
from models.user import User
from models.quiz import QuizAnswer
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession


async def init_models(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def get_user_by_tg_id(session: AsyncSession, user_id: int) -> Optional[User]:
    stmt = select(User).where(User.user_id == user_id)
    result = await session.execute(stmt)
    return result.scalars().first()


async def get_all_no_quiz_answers(session: AsyncSession, user_id: int):
    stmt = select(QuizAnswer).where(QuizAnswer.user_id == user_id, QuizAnswer.answer == False)
    result = await session.execute(stmt)
    return result.scalars().all()


async def register_user(session: AsyncSession, user_id: int, name: str, score: int, status: str) -> bool:
    result = await session.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()
    if user is not None:
        return False
    else:
        new_user = User(user_id=user_id, name=name, status=status, score=score)
        session.add(new_user)
        await session.commit()
        return True


async def add_score_user(session: AsyncSession, user_id: int, add_score: int) -> bool:
    user = await session.execute(select(User).where(User.user_id == user_id))
    user = user.scalar_one_or_none()
    if user:
        user.score += add_score
        await session.commit()


async def add_answer(session: AsyncSession, user_id: int, question_index: int, status: str, answer: bool):
    quiz_answer = QuizAnswer(
        user_id=user_id,
        question_index=question_index,
        status=status,
        answer=answer
    )
    session.add(quiz_answer)
    await session.commit()


async def delete_quiz(session: AsyncSession, user_id: int):
    await session.execute(QuizAnswer.__table__.delete().where(QuizAnswer.user_id == user_id))


async def get_user_name(session: AsyncSession, user_id: int) -> str:
    result = await session.execute(select(User.name).where(User.user_id == user_id))
    name = result.scalar_one_or_none()
    return name


async def get_task_status(session: AsyncSession, name: str, uid: int, user_id: int):
    result = await session.execute(
        select(TaskStatus).where(TaskStatus.name == name, TaskStatus.uid == uid, TaskStatus.user_id == user_id))
    task = result.scalar_one_or_none()
    return task


async def update_status_task(session: AsyncSession, user_id: int, name: str, uid: int, status: str) -> bool:
    result = await get_task_status(session, name, uid, user_id)
    result.status = status
    await session.commit()


async def get_all_themes(session: AsyncSession):
    result = await session.execute(select(distinct(Task.theme)))
    return result.scalars().all()


async def theme_exists(session: AsyncSession, theme: str):
    result = await session.execute(select(Task).where(Task.theme == theme))
    task = result.scalars().first()
    if task is not None:
        return True
    else:
        return False


async def add_task(session: AsyncSession, uid: int, name: str, description: str, theme: str, value: int):
    task = Task(uid=uid, name=name, description=description, theme=theme, value=value)
    session.add(task)
    await session.commit()


async def get_tasks_by_theme(session: AsyncSession, theme: str):
    result = await session.execute(select(Task.name).where(Task.theme == theme))
    return result.scalars().all()


async def get_tasks_uid_by_name(session: AsyncSession, name: str):
    result = await session.execute(select(Task.uid).where(Task.name == name))
    uid = result.scalar_one_or_none()
    return uid


async def get_task_by_name(session: AsyncSession, name: str):
    result = await session.execute(select(Task).where(Task.name == name))
    task = result.scalar_one_or_none()
    return task


async def get_user_score(session: AsyncSession, user_id: int):
    result = await session.execute(select(User.score).where(User.user_id == user_id))
    score = result.scalar_one_or_none()
    return score


async def add_task_status(session: AsyncSession, user_id: int, uid: int, name: str, status: str):
    task = TaskStatus(uid=uid, name=name, user_id=user_id, status=status)
    session.add(task)
    await session.commit()


async def get_all_themes_not_completed(session: AsyncSession, user_id: int):
    subquery = select(TaskStatus.uid).where(and_(TaskStatus.user_id == user_id, TaskStatus.status == 'completed'))
    result = await session.execute(select(Task.theme.distinct()).where(
        not_(exists(subquery.where(Task.uid == TaskStatus.uid).where(Task.name == TaskStatus.name)))))
    themes = result.scalars().all()
    return themes


async def get_tasks_by_theme_not_completed(session: AsyncSession, user_id: int, theme: str):
    subquery = select(TaskStatus.uid).where(and_(TaskStatus.user_id == user_id, TaskStatus.status == 'completed'))
    result = await session.execute(select(Task.name.distinct()).where(Task.theme == theme,
                                                                      not_(exists(subquery.where(
                                                                          Task.uid == TaskStatus.uid).where(
                                                                          Task.name == TaskStatus.name)))))
    tasks = result.scalars().all()
    return tasks

async def get_tasks_completed(session: AsyncSession, user_id: int):
    result = await session.execute(select(Task).where(exists(select(TaskStatus).where(
        and_(TaskStatus.user_id == user_id, TaskStatus.status == 'completed', Task.uid == TaskStatus.uid,
             Task.name == TaskStatus.name)))))
    tasks = result.scalars().all()
    return tasks

async def get_tasks_favorite(session: AsyncSession, user_id: int):
    result = await session.execute(select(Task.name).where(exists(select(TaskStatus).where(
        and_(TaskStatus.user_id == user_id, TaskStatus.status == 'favorite', Task.uid == TaskStatus.uid,
             Task.name == TaskStatus.name)))))
    tasks = result.scalars().all()
    return tasks
