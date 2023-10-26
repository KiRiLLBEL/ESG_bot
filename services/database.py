import datetime
from typing import Optional

from sqlalchemy import distinct, not_, exists, delete, union, update
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.elements import and_, or_, literal

from models.base import Base
from models.learn import LearnMaterial, LearnTheme, LearnCourse
from models.theme import Theme
from models.event import Event, EventTheme, UserEvent
from models.user_task import UserTask
from models.task import Task
from models.user_survey import UserSurvey, AnswerSurvey
from models.user import User
from models.product import Product, ShoppingSession, CartItem, Order
from models.survey import Survey, Question, Option

from models.base import Base
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from datetime import date



async def init_models(engine: AsyncEngine):
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

async def get_user_by_tg_id(session: AsyncSession, user_id: int) -> Optional[User]:
    stmt = select(User).where(User.user_id == user_id)
    result = await session.execute(stmt)
    return result.scalars().first()

async def get_events(session: AsyncSession):
    stmt = select(Event).options(selectinload(Event.theme))
    result = await session.execute(stmt)
    events = result.scalars().all()
    return events


async def register_user(session: AsyncSession, user_id: int, username: str, score: int, status: str, level: int) -> bool:
    result = await session.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()
    if user is not None:
        return False
    else:
        new_user = User(user_id=user_id, username=username, status=status, score=score, level=level, reg_data=datetime.date.today())
        session.add(new_user)
        await session.commit()
        return True

async def add_survey(session: AsyncSession, data):
    survey = Survey(title=data['name'], theme_id=data['theme'], score=data['score'], type=data['type'])
    for question_data in data['questions']:
        question = Question(text=question_data['text'], survey=survey)
        for option_text in question_data['options']:
            option = Option(text=option_text, question=question)
            session.add(option)
    session.add(survey)
    await session.commit()

async def get_task_by_id(session: AsyncSession, task_id: int):
    result = await session.execute(select(Task).options(selectinload(Task.theme)).where(Task.task_id == task_id))
    task = result.scalars().first()
    return task

async def add_score_user(session: AsyncSession, user_id: int, add_score: int) -> bool:
    user = await session.execute(select(User).where(User.user_id == user_id))
    user = user.scalar_one_or_none()
    if user:
        user.score += add_score
        await session.commit()


async def get_user_task(session: AsyncSession, user_id: int, task_id: int):
    result = await session.execute(
        select(UserTask).where(UserTask.task_id == task_id, UserTask.user_id == user_id))
    task = result.scalar_one_or_none()
    return task

async def get_user_event(session: AsyncSession, user_id: int, event_id: int):
    result = await session.execute(
        select(UserEvent).where(UserEvent.event_id == event_id, UserEvent.user_id == user_id))
    task = result.scalar_one_or_none()
    return task


async def update_user_task(session: AsyncSession, user_id: int, task_id: int, status: str):
    result = await get_user_task(session=session, user_id=user_id, task_id=task_id)
    result.status = status
    await session.commit()


async def get_themes_with_tasks(session: AsyncSession):
    stmt = select(Theme).where(
        exists().where(Task.theme_id == Theme.theme_id)
    )
    result = await session.execute(stmt)
    themes = result.scalars().all()
    return themes

async def get_themes_with_surveys(session: AsyncSession):
    stmt = select(Theme).where(exists().where(Theme.theme_id == Survey.theme_id))
    result = await session.execute(stmt)
    themes = result.scalars().all()
    return themes


async def get_themes_with_surveys(session: AsyncSession):
    stmt = select(Theme).where(
        exists().where(Survey.theme_id == Theme.theme_id)
    )
    result = await session.execute(stmt)
    themes = result.scalars().all()
    return themes

async def get_all_themes(session: AsyncSession):
    stmt = select(Theme)
    result = await session.execute(stmt)
    themes = result.scalars().all()
    return themes

async def get_all_event_themes(session: AsyncSession):
    stmt = select(EventTheme)
    result = await session.execute(stmt)
    themes = result.scalars().all()
    return themes

async def theme_exists(session: AsyncSession, theme_title: str):
    result = await session.execute(select(Theme).where(Theme.title == theme_title))
    task = result.scalars().first()
    if task is not None:
        return True
    else:
        return False

async def event_theme_exists(session: AsyncSession, theme_title: str):
    result = await session.execute(select(EventTheme).where(EventTheme.title == theme_title))
    task = result.scalars().first()
    if task is not None:
        return True
    else:
        return False


async def theme_exists_by_id(session: AsyncSession, id: int):
    result = await session.execute(select(Theme).where(Theme.theme_id == id))
    task = result.scalars().first()
    if task is not None:
        return True
    else:
        return False


async def add_task(session: AsyncSession, title: str, description: str, value: int, theme_id: int):
    task = Task(title=title, description=description, value=value, theme_id=theme_id)
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task.task_id

async def add_theme(session: AsyncSession, theme_title: str):
    new_theme = Theme(title=theme_title)
    session.add(new_theme)
    await session.commit()
    await session.refresh(new_theme)
    return new_theme.theme_id

async def add_event_theme(session: AsyncSession, theme_title: str):
    new_theme = EventTheme(title=theme_title)
    session.add(new_theme)
    await session.commit()
    await session.refresh(new_theme)
    return new_theme.event_theme_id

async def add_theme_by_id(session: AsyncSession, id: int):
    new_theme = Theme(theme_id=id, title="main")
    session.add(new_theme)
    await session.commit()
    await session.refresh(new_theme)
    return new_theme.theme_id


async def get_tasks_by_theme_id(session: AsyncSession, theme_id: int):
    stmt = select(Task).join(Theme).where(Theme.theme_id == theme_id)
    result = await session.execute(stmt)
    tasks = result.scalars().all()
    return tasks

async def get_surveys_by_theme_id(session: AsyncSession, theme_id: int):
    stmt = select(Survey).join(Theme).where(Theme.theme_id == theme_id)
    result = await session.execute(stmt)
    surveys = result.scalars().all()
    return surveys

async def add_event(session: AsyncSession, title: str, description: str, place: str, organizer: str, image_url: str, date: str, capacity: int, value: int, theme_id: int):
    event = Event(title=title, description=description, place=place, capacity=capacity, date=date, organizer=organizer, image_url=image_url, value=value, theme_id=theme_id)
    session.add(event)
    await session.commit()
    await session.refresh(event)
    return event.event_id

async def get_user_score(session: AsyncSession, user_id: int):
    result = await session.execute(select(User.score).where(User.user_id == user_id))
    score = result.scalar_one_or_none()
    return score


async def add_user_task(session: AsyncSession, user_id: int, task_id: int, status: str):
    task = UserTask(user_id=user_id, task_id=task_id, status=status, date=date.today())
    session.add(task)
    await session.commit()


async def get_tasks_and_surveys(session: AsyncSession, user_id: int, theme_id: int):
    # Запрос для заданий
    tasks_query = select(Task, literal('task').label('type')).join(Theme, Theme.theme_id == Task.theme_id) \
        .outerjoin(UserTask, and_(UserTask.task_id == Task.task_id, UserTask.user_id == user_id)) \
        .where(
        and_(
            Theme.theme_id == theme_id,
            or_(
                UserTask.status.in_(["active", "favorite"]),
                UserTask.status.is_(None)
            )
        )
    )

    # Запрос для опросов
    surveys_query = select(Survey, literal('survey').label('type')).join(Theme, Theme.theme_id == Survey.theme_id) \
        .outerjoin(UserSurvey, and_(UserSurvey.survey_id == Survey.survey_id, UserSurvey.user_id == user_id)) \
        .where(
        and_(
            Theme.theme_id == theme_id,
            or_(
                UserSurvey.status.in_(["active", "favorite"]),
                UserSurvey.status.is_(None)
            )
        )
    )

    tasks = await session.execute(tasks_query)
    surveys = await session.execute(surveys_query)

    return tasks.fetchall() + surveys.fetchall()


async def delete_tasks(session: AsyncSession, id: int):
    await session.execute(delete(Task).where((Task.task_id == id)))
    await session.execute(delete(UserTask).where(
        (UserTask.task_id == id) & (UserTask.status != 'complete')))
    await session.commit()

async def update_task_title(session: AsyncSession, task_id: int, new_title: str):
    await session.execute(update(Task).where(Task.task_id == task_id).values(title=new_title))
    await session.commit()

async def update_task_description(session: AsyncSession, task_id: int, new_description: str):
    await session.execute(update(Task).where(Task.task_id == task_id).values(description=new_description))
    await session.commit()

async def update_task_value(session: AsyncSession, task_id: int, new_value: int):
    await session.execute(update(Task).where(Task.task_id == task_id).values(value=new_value))
    await session.commit()

async def update_option_text(session: AsyncSession, option_id: int, new_text: str):
    await session.execute(update(Option).where(Option.option_id == option_id).values(text=new_text))
    await session.commit()

async def update_question_text(session: AsyncSession, question_id: int, new_text: str):
    await session.execute(update(Question).where(Question.question_id == question_id).values(text=new_text))
    await session.commit()

async def theme_exists_survey(session: AsyncSession, theme: str):
    result = await session.execute(select(Theme).where(Theme.title == theme))
    survey = result.scalars().first()
    return survey is not None

async def get_user_survey(session: AsyncSession, user_id: int, survey_id: int):
    result = await session.execute(select(UserSurvey).where(UserSurvey.user_id == user_id).where(UserSurvey.survey_id == survey_id))
    survey_result = result.scalars().first()
    return survey_result

async def add_survey_complete(session: AsyncSession, user_id: int, survey_id: int, answers):
    user_survey: UserSurvey = await get_user_survey(session, user_id, survey_id)
    if user_survey is None:
        user_survey = UserSurvey(user_id=user_id, survey_id=survey_id, status='complete', date=date.today())
        session.add(user_survey)
        await session.commit()
    else:
        user_survey.status = 'complete'
        await session.commit()
    for ans in answers:
        answer = AnswerSurvey(users_surveys_id=user_survey.users_surveys_id, question_id=ans[0], option_id=ans[1])
        session.add(answer)
    await session.commit()

async def add_user_survey(session: AsyncSession, user_id: int, survey_id: int, status: str):
    survey_result = UserSurvey(user_id=user_id, survey_id=survey_id, status=status, date=date.today())
    session.add(survey_result)
    await session.commit()
async def add_user_event(session: AsyncSession, user_id: int, event_id: int, status: str):
    user_event = UserEvent(user_id=user_id, event_id=event_id, status=status)
    session.add(user_event)
    await session.commit()


async def get_first_unattempted_survey(session: AsyncSession, user_id: int, survey_type: str):
    result = await session.execute(
        select(Survey).outerjoin(UserSurvey).options(selectinload(Survey.questions).selectinload(Question.options)).where(
            and_(
                Survey.type == survey_type,
                or_(
                    UserSurvey.user_id != user_id,
                    UserSurvey.user_id.is_(None)
                )
            )
        ).order_by(Survey.survey_id).limit(1)
    )
    survey = result.scalars().first()
    return survey

async def get_unattempted_themes(session: AsyncSession, user_id: int):
    stmt = select(Theme).distinct().options(
        selectinload(Theme.tasks).joinedload(Task.users_tasks),
        selectinload(Theme.surveys).joinedload(Survey.users_survey)
    ).filter(
        Theme.title != "main",
        or_(
            exists().where(Task.theme_id == Theme.theme_id),
            exists().where(Survey.theme_id == Theme.theme_id)
        )
    )

    result = await session.execute(stmt)
    themes = result.scalars().all()

    return themes

#
#
async def get_survey_by_id(session: AsyncSession, survey_id: int) -> Survey:
    result = await session.execute(select(Survey).options(selectinload(Survey.questions).selectinload(Question.options), selectinload(Survey.theme)).where(Survey.survey_id == survey_id))
    survey = result.scalars().first()
    return survey

async def get_option_by_id(session: AsyncSession, option_id: int) -> Option:
    result = await session.execute(select(Option).options(selectinload(Option.question).selectinload(Question.options)).where(Option.option_id == option_id))
    option = result.scalars().first()
    return option

async def get_question_by_id(session: AsyncSession, question_id: int) -> Question:
    result = await session.execute(select(Question).options(selectinload(Question.survey).selectinload(Survey.questions)).where(Question.question_id == question_id))
    question = result.scalars().first()
    return question

async def delete_option_and_answers(session: AsyncSession, option_id: int):
    # Удалить все ответы, связанные с данным вариантом ответа
    await session.execute(delete(AnswerSurvey).where(AnswerSurvey.option_id == option_id))
    # Удалить сам вариант ответа
    await session.execute(delete(Option).where(Option.option_id == option_id))
    await session.commit()

async def delete_question_and_answers(session: AsyncSession, question_id: int):
    # Удалить все ответы, связанные с данным вопросом
    await session.execute(delete(AnswerSurvey).where(AnswerSurvey.question_id == question_id))
    # Удалить все варианты ответов, связанные с данным вопросом
    await session.execute(delete(Option).where(Option.question_id == question_id))
    # Удалить сам вопрос
    await session.execute(delete(Question).where(Question.question_id == question_id))
    await session.commit()


async def get_completed_surveys_and_tasks(session: AsyncSession, user_id: int):
    completed_surveys = select(Survey.survey_id.label('id'), literal('survey').label('type')).join(UserSurvey).where(
        and_(
            UserSurvey.user_id == user_id,
            UserSurvey.status == 'complete',
            Survey.type.notin_(['business', 'person'])
        )
    )

    # Получить все завершенные задания пользователя
    completed_tasks = select(Task.task_id.label('id'), literal('task').label('type')).join(UserTask).where(
        and_(
            UserTask.user_id == user_id,
            UserTask.status == 'complete'
        )
    )

    result = await session.execute(completed_tasks.union_all(completed_surveys))
    return result.fetchall()


async def get_favorite_surveys_and_tasks(session: AsyncSession, user_id: int):
    # Получить все избранные опросы пользователя
    favorite_surveys = select(Survey, literal('survey').label('type')).join(UserSurvey).where(
        and_(
            UserSurvey.user_id == user_id,
            UserSurvey.status == 'favorite'
        )
    )

    # Получить все избранные задания пользователя
    favorite_tasks = select(Task, literal('task').label('type')).join(UserTask).where(
        and_(
            UserTask.user_id == user_id,
            UserTask.status == 'favorite'
        )
    )

    surveys = await session.execute(favorite_surveys)
    tasks = await session.execute(favorite_tasks)

    return surveys.fetchall() + tasks.fetchall()

async def get_favorite_event(session: AsyncSession, user_id: int):
    stmt = select(Event).options(selectinload(Event.theme)).join(UserEvent, UserEvent.event_id == Event.event_id) \
        .where(
        and_(
            UserEvent.user_id == user_id,
            UserEvent.status == 'favorite'
        )
    )

    result = await session.execute(stmt)
    events = result.scalars().all()
    return events

async def add_product(session: AsyncSession, title: str, price: int, image_url: str):
    product = Product(title=title, price=price, image_url=image_url)
    session.add(product)
    await session.commit()

async def get_products_as_pages(session: AsyncSession, offset: int, limit: int):
    result = await session.execute(
        select(Product).order_by(Product.product_id).offset(offset).limit(limit)
    )
    return result.scalars().all()
#
async def get_product_by_id(session: AsyncSession, product_id: int):
    result = await session.execute(select(Product).where(Product.product_id == product_id))
    return result.scalar_one_or_none()
#
async def decrease_score(session: AsyncSession, user_id: int, decrement: int):
    user = await session.get(User, user_id)
    if user:
        user.score -= decrement
        await session.commit()
