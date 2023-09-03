from typing import Optional

from sqlalchemy import distinct, not_, exists, delete, union
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.elements import and_, or_

from models.base import Base
from models.pool import Survey, Question, Option
from models.pool_status import SurveyResult, Answer
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


async def register_user(session: AsyncSession, user_id: int, name: str, score: int, status: str, quiz: bool) -> bool:
    result = await session.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()
    if user is not None:
        return False
    else:
        new_user = User(user_id=user_id, name=name, status=status, score=score, quiz=quiz)
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


async def get_all_themes_not_completed_all_tables(session: AsyncSession, user_id: int):
    task_themes = select(Task.theme).where(
        or_(and_(TaskStatus.user_id == user_id, TaskStatus.status != 'completed'), TaskStatus.id == None)).outerjoin(
        TaskStatus, Task.uid == TaskStatus.uid).distinct()
    survey_themes = select(Survey.theme).where(
        or_(and_(SurveyResult.user_id == user_id, SurveyResult.status != 'completed'),
            SurveyResult.id == None)).outerjoin(SurveyResult, Survey.id == SurveyResult.survey_id).distinct()
    unique_themes = union(task_themes, survey_themes)
    result = await session.execute(unique_themes)
    return [row[0] for row in result.fetchall()]


async def get_tasks_by_theme_not_completed(session: AsyncSession, user_id: int, theme: str):
    subquery = select(TaskStatus.uid).where(and_(TaskStatus.user_id == user_id, TaskStatus.status == 'completed'))
    result = await session.execute(select(Task.name.distinct()).where(Task.theme == theme,
                                                                      not_(exists(subquery.where(
                                                                          Task.uid == TaskStatus.uid).where(
                                                                          Task.name == TaskStatus.name)))))
    tasks = result.scalars().all()
    return tasks


async def get_tasks_and_themes_by_theme_not_completed(session: AsyncSession, user_id: int, theme: str):
    tasks = select(Task.name).where(
        or_(and_(TaskStatus.user_id == user_id, TaskStatus.status != 'completed'), TaskStatus.id == None)).where(
        Task.theme == theme).outerjoin(TaskStatus, Task.uid == TaskStatus.uid)
    surveys = select(Survey.title).where(
        or_(and_(SurveyResult.user_id == user_id, SurveyResult.status != 'completed'), SurveyResult.id == None)).where(
        Survey.theme == theme).outerjoin(SurveyResult, Survey.id == SurveyResult.survey_id)
    result = await session.execute(union(tasks, surveys))
    return [(row[0], 'task' if row[0] in [task[0] for task in (await session.execute(tasks)).fetchall()] else 'survey')
            for row in result.fetchall()]


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


async def delete_tasks(session: AsyncSession, uid: int, name: str):
    await session.execute(delete(Task).where((Task.uid == uid) & (Task.name == name)))
    await session.execute(delete(TaskStatus).where(
        (TaskStatus.uid == uid) & (TaskStatus.name == name) & (TaskStatus.status != 'completed')))
    await session.commit()


async def get_pools_by_theme(session: AsyncSession, theme: str):
    result = await session.execute(select(Survey.title).where(Survey.theme == theme))
    surveys = result.scalars().all()
    return surveys


async def get_theme_pools(session: AsyncSession):
    result = await session.execute(select(Survey.theme.distinct()))
    themes = result.scalars().all()
    return themes


async def theme_exists_pool(session: AsyncSession, theme: str):
    result = await session.execute(select(Survey).where(Survey.theme == theme))
    survey = result.scalars().first()
    return survey is not None


async def add_survey(session: AsyncSession, data):
    survey = Survey(title=data['name'], theme=data['theme'], score=data['score'])
    for question_data in data['questions']:
        question = Question(text=question_data['text'], survey=survey)
        for option_text in question_data['options']:
            option = Option(text=option_text, question=question)
            session.add(option)
    session.add(survey)
    await session.commit()


async def get_all_themes_all_table(session: AsyncSession):
    task_themes = select(Task.theme).distinct()
    survey_themes = select(Survey.theme).distinct()
    unique_themes = union(task_themes, survey_themes)
    result = await session.execute(unique_themes)
    return result.scalars().all()


async def get_survey_by_title(session: AsyncSession, title: str):
    result = await session.execute(select(Survey).where(Survey.title == title))
    survey = result.scalars().first()
    return survey

async def get_survey_result(session: AsyncSession, user_id: int, survey_id: int):
    result = await session.execute(select(SurveyResult).where(SurveyResult.user_id == user_id).where(SurveyResult.survey_id == survey_id))
    survey_result = result.scalars().first()
    return survey_result

async def add_survey_complete(session: AsyncSession, user_id: int, survey_id: int, answers):
    survey_result: SurveyResult = await get_survey_result(session, user_id, survey_id)
    if survey_result is None:
        survey_result = SurveyResult(user_id=user_id, survey_id=survey_id, status='completed')
        session.add(survey_result)
        await session.commit()
    else:
        survey_result.status = 'completed'
        await session.commit()
    for ans in answers:
        answer = Answer(survey_result_id=survey_result.id, question_id=ans[0], option_id=ans[1])
        session.add(answer)
    await session.commit()

async def add_survey_result(session: AsyncSession, user_id: int, survey_id: int, status: str):
    survey_result = SurveyResult(user_id=user_id, survey_id=survey_id, status=status)
    session.add(survey_result)
    await session.commit()


async def get_survey_by_id(session: AsyncSession, survey_id: int) -> Survey:
    result = await session.execute(select(Survey).where(Survey.id == survey_id))
    survey = result.scalars().first()
    return survey


async def get_question_options(session: AsyncSession, question_id: int):
    result = await session.execute(select(Option).where(Option.question_id == question_id))
    options = result.scalars().all()
    return [(option.text, option.id) for option in options]

async def get_completed_tasks_and_surveys(session: AsyncSession, user_id: int):
    completed_tasks = select(Task.name).where(TaskStatus.user_id == user_id).where(TaskStatus.status == 'completed').join(TaskStatus, Task.uid == TaskStatus.uid)
    completed_surveys = select(Survey.title).where(SurveyResult.user_id == user_id).where(SurveyResult.status == 'completed').join(SurveyResult, Survey.id == SurveyResult.survey_id)
    result = await session.execute(completed_tasks.union(completed_surveys))
    return [(row[0], 'task' if row[0] in [task[0] for task in (await session.execute(completed_tasks)).fetchall()] else 'survey') for row in result.fetchall()]

async def get_favorite_tasks_and_surveys(session: AsyncSession, user_id: int):
    favorite_tasks = select(Task.name).where(TaskStatus.user_id == user_id).where(TaskStatus.status == 'favorite').join(TaskStatus, Task.uid == TaskStatus.uid)
    favorite_surveys = select(Survey.title).where(SurveyResult.user_id == user_id).where(SurveyResult.status == 'favorite').join(SurveyResult, Survey.id == SurveyResult.survey_id)
    result = await session.execute(favorite_tasks.union(favorite_surveys))
    return [(row[0], 'task' if row[0] in [task[0] for task in (await session.execute(favorite_tasks)).fetchall()] else 'survey') for row in result.fetchall()]
