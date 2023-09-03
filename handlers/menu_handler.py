from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InputMediaPhoto
from sqlalchemy.ext.asyncio import AsyncSession

from filters.menu_filters import MenuCallbackFactory
from keyboards.inline_keyboards import callback_map, create_keyboard_options
from lexicon.lexicon_ru import LEXICON_RU
from models.pool import Survey
from res.photo import PHOTO
from services.database import get_task_by_name, get_tasks_uid_by_name, \
    add_score_user, get_user_by_tg_id, get_user_score, add_task_status, get_all_themes_not_completed, get_task_status, \
    update_status_task, get_tasks_by_theme_not_completed, get_tasks_completed, get_tasks_favorite, \
    get_all_themes_not_completed_all_tables, get_tasks_and_themes_by_theme_not_completed, get_survey_by_title, \
    add_survey_complete, get_survey_by_id, get_question_options, get_survey_result, add_survey_result, \
    get_completed_tasks_and_surveys, get_favorite_tasks_and_surveys
from states.menu_states import Tasks

router = Router()


@router.callback_query(MenuCallbackFactory.filter(F.next_keyboard == 'none'))
@router.callback_query(F.data == 'none')
async def later(callback: CallbackQuery):
    await callback.answer(text="Данный раздел появиться позже")


@router.callback_query(MenuCallbackFactory.filter(F.next_keyboard == 'themes_earn'))
async def get_themes_for_earn(callback: CallbackQuery, callback_data: MenuCallbackFactory, state: FSMContext,
                              session: AsyncSession):
    themes = await get_all_themes_not_completed_all_tables(session, callback.from_user.id)
    if not themes:
        await callback.answer(text='Нет доступных тем')
        return
    await state.set_state(Tasks.get)
    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=PHOTO['my_score'],
            caption=LEXICON_RU['themes_earn']['message']
        ),
        reply_markup=callback_map[callback_data.next_keyboard](themes)
    )


@router.callback_query(MenuCallbackFactory.filter(F.next_keyboard == 'get_favorites'))
async def get_themes_for_earn(callback: CallbackQuery, callback_data: MenuCallbackFactory, state: FSMContext,
                              session: AsyncSession):
    tasks = await get_favorite_tasks_and_surveys(session, callback.from_user.id)
    if not tasks:
        await callback.answer(text='Нет доступных заданий')
        return
    await state.set_state(Tasks.tasks)
    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=PHOTO['favorite'],
            caption='Список избранных заданий и опросов'
        ),
        reply_markup=callback_map['tasks'](tasks)
    )


@router.callback_query(MenuCallbackFactory.filter(F.next_keyboard == 'get_completed'))
async def get_themes_for_earn(callback: CallbackQuery, callback_data: MenuCallbackFactory, state: FSMContext,
                              session: AsyncSession):
    tasks = await get_completed_tasks_and_surveys(session, callback.from_user.id)
    if not tasks:
        await callback.answer(text='Нет выполненных заданий')
        return
    resume: str = ''
    for obj in tasks:
        if obj[1] == 'task':
            task = await get_task_by_name(session, obj[0])
            resume += (
                    "Название: " + task.name +
                    "\nТип: Задание" +
                    '\nОписание: ' + task.description +
                    "\nТема: " + task.theme +
                    "\nБаллы за решение: " + str(task.value) + '\n\n'
            )
        else:
            survey = await get_survey_by_title(session, obj[0])
            resume += (
                    "Название: " + survey.title +
                    "\nТип: Опрос" +
                    "\nТема: " + survey.theme +
                    "\nБаллы за прохождение: " + str(survey.score) + '\n\n'
            )
    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=PHOTO['my_score'],
            caption=LEXICON_RU['themes_earn']['message']
        ),
        reply_markup=callback_map[callback_data.current_keyboard]
    )


@router.callback_query(MenuCallbackFactory.filter(F.next_keyboard == 'my_score'))
async def get_themes_for_earn(callback: CallbackQuery, callback_data: MenuCallbackFactory, session: AsyncSession):
    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=PHOTO[callback_data.next_keyboard],
            caption=LEXICON_RU[callback_data.next_keyboard]['message'].format(
                await get_user_score(session, callback.from_user.id))
        ),
        reply_markup=callback_map[callback_data.next_keyboard]
    )


@router.callback_query(MenuCallbackFactory.filter())
async def change_menu_keyboard(callback: CallbackQuery, callback_data: MenuCallbackFactory):
    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=PHOTO[callback_data.next_keyboard],
            caption=LEXICON_RU[callback_data.next_keyboard]['message']
        ),
        reply_markup=callback_map[callback_data.next_keyboard]
    )


@router.callback_query(StateFilter(Tasks.get, Tasks.tasks, Tasks.solve), MenuCallbackFactory.filter())
async def change_menu_keyboard(callback: CallbackQuery, callback_data: MenuCallbackFactory, state: FSMContext):
    await state.clear()
    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=PHOTO[callback_data.next_keyboard],
            caption=LEXICON_RU[callback_data.next_keyboard]['message']
        ),
        reply_markup=callback_map[callback_data.next_keyboard]
    )


@router.callback_query(StateFilter(Tasks.get))
async def get_task_names_for_earn(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    tasks = await get_tasks_and_themes_by_theme_not_completed(session, callback.from_user.id, callback.data)
    print(tasks)
    await state.set_state(Tasks.tasks)
    await callback.message.answer(text='Список доступных заданий', reply_markup=callback_map['tasks'](tasks))
    await callback.message.delete()


@router.callback_query(StateFilter(Tasks.tasks), F.data.startswith('task_'))
async def select_task_to_solve(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    task_name = callback.data.split('_')[1]
    task = await get_task_by_name(session, task_name)
    resume = (
            "Название: " + task.name +
            '\nОписание: ' + task.description +
            "\nТема: " + task.theme +
            "\nБаллы за решение: " + str(task.value)
    )
    await callback.message.edit_text(text=resume, reply_markup=callback_map['task'])
    await state.set_state(Tasks.solve)
    await state.set_data({'name': task.name, 'score': task.value, 'msg': callback.message})


@router.callback_query(StateFilter(Tasks.tasks), F.data.startswith('survey_'))
async def select_task_to_solve(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    survey_name = callback.data.split('_')[1]
    survey = await get_survey_by_title(session, survey_name)
    resume = (
            "Название: " + survey.title +
            "\nТема: " + survey.theme +
            "\nБаллы за прохождение: " + str(survey.score)
    )
    await state.set_state(Tasks.survey_pick)
    await callback.message.edit_text(text=resume, reply_markup=callback_map['task'])
    await state.set_data({'survey_id': survey.id})


@router.callback_query(StateFilter(Tasks.survey_pick), F.data == 'solve')
async def try_solve(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    survey_id = data.get('survey_id')
    survey = await get_survey_by_id(session, survey_id)
    questions = survey.questions
    question = questions[0]
    options = await get_question_options(session, question.id)
    await state.set_state(Tasks.survey_solve)
    await state.set_data({
        'survey_id': survey_id,
        'answers': [],
        'idx': 0
    })
    await callback.message.edit_text(text=question.text, reply_markup=create_keyboard_options(options))


@router.callback_query(StateFilter(Tasks.survey_pick), F.data == 'favorites')
async def try_solve(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    survey_id = data.get('survey_id')
    survey_result = await get_survey_result(session, callback.from_user.id, survey_id)
    if survey_result is None:
        await add_survey_result(session, callback.from_user.id, survey_id, 'favorite')
    await callback.answer(text="Опрос добавлен в избранное")


@router.callback_query(StateFilter(Tasks.survey_solve))
async def solving(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    survey_id = data.get('survey_id')
    survey = await get_survey_by_id(session, survey_id)
    option_id = int(callback.data.split('_')[1])
    data['idx'] += 1
    data['answers'].append([data['idx'], option_id])
    if data['idx'] >= len(survey.questions):
        await add_survey_complete(session, callback.from_user.id, survey.id, data['answers'])
        await add_score_user(session, callback.from_user.id, survey.score)
        user = await get_user_by_tg_id(session, callback.from_user.id)
        await state.clear()
        await callback.message.edit_text(text=f'Опрос пройден! Ваш баланс {user.score}',
                                         reply_markup=callback_map['menu_b2c'])
    question = survey.questions[data['idx']]
    keyboard = create_keyboard_options(question.options)
    await state.set_data(data)
    await callback.message.edit_text(text=question.text, keyboard=keyboard)


@router.callback_query(StateFilter(Tasks.solve), F.data == 'solve')
async def try_solve(callback: CallbackQuery):
    await callback.message.edit_text(
        text="Чтобы решить данное задание, напишите в чат код",
        reply_markup=callback_map['task']
    )


@router.callback_query(StateFilter(Tasks.solve), F.data == 'favorites')
async def favorite_solve(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    name = data.get('name', '')
    uid = await get_tasks_uid_by_name(session, name)
    task_status = await get_task_status(session, name, uid, callback.from_user.id)
    if task_status is None:
        await add_task_status(
            session=session,
            uid=await get_tasks_uid_by_name(session, name),
            name=name,
            user_id=callback.from_user.id,
            status='favorite'
        )
    await callback.answer(text="Задание добавлено в избранное")


@router.message(StateFilter(Tasks.solve), F.text.isdigit())
async def select_task_to_solve(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    name = data.get('name', '')
    score = data.get('score', 0)
    msg: Message = data.get('msg')
    uid = await get_tasks_uid_by_name(session, name)
    if int(message.text) == uid:
        await state.clear()
        await add_score_user(session, message.from_user.id, score)
        user = await get_user_by_tg_id(session, message.from_user.id)
        task_status = await get_task_status(session, name, uid, message.from_user.id)
        if task_status is None:
            await add_task_status(
                session=session,
                uid=uid,
                name=name,
                user_id=message.from_user.id,
                status='completed'
            )
        else:
            await update_status_task(session, message.from_user.id, name, uid, 'completed')

        await msg.answer_photo(photo=PHOTO['menu_b2c'], caption=f'Задание успешно выполнено! Ваш баланс {user.score}',
                               reply_markup=callback_map['menu_b2c'])
    else:
        await msg.edit_text(text="К сожалению, ваш ключ не совпадает, попробуйте еще раз",
                            reply_markup=callback_map['task'])
    await message.delete()


@router.message(StateFilter(Tasks.solve))
async def select_task_to_solve(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data.get('msg')
    if msg.text != "Пожалуйста, введите ключ":
        await msg.edit_text(text="Пожалуйста, введите ключ", reply_markup=callback_map['task'])
    await message.delete()
