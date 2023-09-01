from aiogram import F
from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.inline_keyboards import callback_map_admin
from lexicon.lexicon_ru import LEXICON_RU
from services.database import get_all_themes, theme_exists, add_task, get_tasks_by_theme, get_tasks_uid_by_name
from states.admin_states import Admin
from utils.quiz_utils import generate_random_uid

router = Router()

@router.callback_query(StateFilter(Admin.join), F.data == 'create_task')
async def create_task_themes(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    themes = await get_all_themes(session)
    await state.set_state(Admin.theme)
    await callback.message.edit_reply_markup(reply_markup=callback_map_admin['create_task'](themes))

@router.callback_query(StateFilter(Admin.join), F.data == 'get_task')
async def get_task_themes(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    themes = await get_all_themes(session)
    if not themes:
        await callback.answer(text='Нет созданных заданий')
        return
    await state.set_state(Admin.get)
    await callback.message.edit_reply_markup(reply_markup=callback_map_admin['get_task'](themes))

@router.callback_query(StateFilter(Admin.get))
async def get_task_names(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    tasks = await get_tasks_by_theme(session, callback.data)
    print(tasks)
    await state.set_state(Admin.tasks)
    await callback.message.edit_reply_markup(reply_markup=callback_map_admin['get_task'](tasks))


@router.callback_query(StateFilter(Admin.tasks))
async def get_task_uid(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    uid = await get_tasks_uid_by_name(session, callback.data)
    await callback.message.answer(text=f"Ключ этой задачи - {uid}")
    await state.set_state(Admin.join)
    await callback.message.answer(text=LEXICON_RU['menu_message'], reply_markup=callback_map_admin['menu'])
    await callback.message.delete()

@router.callback_query(StateFilter(Admin.theme), F.data == 'create_theme')
async def create_task_add_theme(callback: CallbackQuery):
    await callback.message.answer(text="Введите тему")
    await callback.message.delete()


@router.callback_query(StateFilter(Admin.theme))
async def create_task_pick_theme(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Admin.name)
    await state.set_data({"theme": callback.data})
    await callback.message.answer(text='Введите имя задачи')
    await callback.message.delete()


@router.message(StateFilter(Admin.theme))
async def create_task_add_name(message: Message, state: FSMContext, session: AsyncSession):
    if await theme_exists(session, message.text):
        await message.answer(text='Тема уже существует. Введите другую тему')
        return
    await state.set_state(Admin.name)
    await state.set_data({"theme": message.text})
    await message.answer(text='Введите имя задачи')


@router.message(StateFilter(Admin.name))
async def create_task_add_description(message: Message, state: FSMContext):
    data = await state.get_data()
    theme: str = data.get('theme', '')
    await state.set_state(Admin.description)
    await state.set_data({"name": message.text, "theme": theme})
    await message.answer(text='Введите описание задачи')

@router.message(StateFilter(Admin.description))
async def create_task_add_score(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    theme: str = data.get('theme', '')
    name: str = data.get('name', '')
    await state.set_state(Admin.score)
    await state.set_data({"name": name, "theme": theme, "description": message.text})
    await message.answer(text='Введите количество баллов за выполнение задачи')

@router.message(StateFilter(Admin.score), F.text.isdigit())
async def create_task_add_final(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    theme: str = data.get('theme', '')
    name: str = data.get('name', '')
    description: str = data.get('description', '')
    uid = generate_random_uid()
    await add_task(
        session=session,
        uid=uid,
        name=name,
        description=description,
        theme=theme,
        value=int(message.text)
    )
    await state.set_state(Admin.join)
    await message.answer(text=f'Задача успешно создана. UID = {uid}')
    await message.answer(text=LEXICON_RU['menu_message'], reply_markup=callback_map_admin['menu'])

@router.message(StateFilter(Admin.score))
async def create_task_add_final_error(message: Message):
    await message.answer(text='Введите число')