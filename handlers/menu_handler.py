from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from filters.menu_filters import MenuCallbackFactory
from keyboards.inline_keyboards import callback_map
from lexicon.lexicon_ru import LEXICON_RU
from services.database import get_task_by_name, get_tasks_uid_by_name, \
    add_score_user, get_user_by_tg_id, get_user_score, add_task_status, get_all_themes_not_completed, get_task_status, \
    update_status_task, get_tasks_by_theme_not_completed, get_tasks_completed, get_tasks_favorite
from states.menu_states import Tasks

router = Router()


@router.callback_query(MenuCallbackFactory.filter(F.next_keyboard == 'themes_earn'))
async def get_themes_for_earn(callback: CallbackQuery, callback_data: MenuCallbackFactory, state: FSMContext,
                              session: AsyncSession):
    themes = await get_all_themes_not_completed(session, callback.from_user.id)
    if not themes:
        await callback.answer(text='Нет доступных заданий')
        return
    await state.set_state(Tasks.get)
    await callback.message.edit_text(
        text=LEXICON_RU['themes_earn']['message'],
        reply_markup=callback_map[callback_data.next_keyboard](themes)
    )

@router.callback_query(MenuCallbackFactory.filter(F.next_keyboard == 'get_favorites'))
async def get_themes_for_earn(callback: CallbackQuery, callback_data: MenuCallbackFactory, state: FSMContext,
                              session: AsyncSession):
    tasks = await get_tasks_favorite(session, callback.from_user.id)
    if not tasks:
        await callback.answer(text='Нет доступных заданий')
        return
    await state.set_state(Tasks.tasks)
    await callback.message.edit_text(text='Список доступных заданий', reply_markup=callback_map['themes_earn'](tasks))

@router.callback_query(MenuCallbackFactory.filter(F.next_keyboard == 'get_completed'))
async def get_themes_for_earn(callback: CallbackQuery, callback_data: MenuCallbackFactory, state: FSMContext,
                              session: AsyncSession):
    tasks = await get_tasks_completed(session, callback.from_user.id)
    if not tasks:
        await callback.answer(text='Нет доступных заданий')
        return
    resume: str = ''
    for task in tasks:
        resume += (
                "Название: " + task.name +
                '\nОписание: ' + task.description +
                "\nТема: " + task.theme +
                "\nБаллы за решение: " + str(task.value) + '\n\n'
        )
    await callback.message.edit_text(
        text=resume,
        reply_markup=callback_map[callback_data.current_keyboard]
    )


@router.callback_query(MenuCallbackFactory.filter(F.next_keyboard == 'my_score'))
async def get_themes_for_earn(callback: CallbackQuery, callback_data: MenuCallbackFactory, session: AsyncSession):
    await callback.message.edit_text(
        text=LEXICON_RU['my_score']['message'].format(
            await get_user_score(
                session, callback.from_user.id
            )
        ),
        reply_markup=callback_map[callback_data.next_keyboard]
    )


@router.callback_query(MenuCallbackFactory.filter())
async def change_menu_keyboard(callback: CallbackQuery, callback_data: MenuCallbackFactory):
    await callback.message.edit_text(
        text=LEXICON_RU[callback_data.next_keyboard]['message'],
        reply_markup=callback_map[callback_data.next_keyboard]
    )


@router.callback_query(StateFilter(Tasks.get, Tasks.tasks, Tasks.solve), MenuCallbackFactory.filter())
async def change_menu_keyboard(callback: CallbackQuery, callback_data: MenuCallbackFactory, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        text=LEXICON_RU[callback_data.next_keyboard]['message'],
        reply_markup=callback_map[callback_data.next_keyboard]
    )


@router.callback_query(StateFilter(Tasks.get))
async def get_task_names_for_earn(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    tasks = await get_tasks_by_theme_not_completed(session, callback.from_user.id, callback.data)
    await state.set_state(Tasks.tasks)
    await callback.message.edit_text(text='Список доступных заданий', reply_markup=callback_map['themes_earn'](tasks))


@router.callback_query(StateFilter(Tasks.tasks))
async def select_task_to_solve(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    task = await get_task_by_name(session, callback.data)
    resume = (
            "Название: " + task.name +
            '\nОписание: ' + task.description +
            "\nТема: " + task.theme +
            "\nБаллы за решение: " + str(task.value)
    )
    await callback.message.edit_text(text=resume, reply_markup=callback_map['task'])
    await state.set_state(Tasks.solve)
    await state.set_data({'name': task.name, 'score': task.value, 'msg': callback.message})


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
    await callback.answer()

@router.message(StateFilter(Tasks.solve), F.text.isdigit())
async def select_task_to_solve(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    name = data.get('name', '')
    score = data.get('score', 0)
    msg = data.get('msg')
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
        await msg.edit_text(text=f'Задание успешно выполнено! Ваш баланс {user.score}',
                            reply_markup=callback_map['menu_b2c'])
    else:
        await msg.edit_text(text="К сожалению, ваш ключ не совпадает, попробуйте еще раз",
                            reply_markup=callback_map['task'])
    await message.delete()


@router.message(StateFilter(Tasks.solve))
async def select_task_to_solve(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data.get('msg')
    await msg.edit_text(text="Пожалуйста, введите ключ", reply_markup=callback_map['task'])
    await message.delete()
