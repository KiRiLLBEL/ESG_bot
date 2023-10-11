from aiogram import Router, Bot, F
from aiogram.enums import ContentType
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.inline_keyboards import callback_map_admin
from lexicon.lexicon_ru import LEXICON_RU
from services.database import get_tasks_by_theme, get_tasks_uid_by_name, delete_tasks, theme_exists, add_task
from states.admin_states import Admin, callback_error_input
from utils.quiz_utils import generate_random_uid

router = Router()


@router.callback_query(StateFilter(Admin.task_theme_delete))
async def get_task_for_delete(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    tasks = await get_tasks_by_theme(session, callback.data)
    if not tasks:
        await callback.answer(text='Нет созданных заданий')
        return
    await state.set_state(Admin.task_tasks_delete)
    await callback.message.edit_reply_markup(reply_markup=callback_map_admin['delete_task'](tasks))


@router.callback_query(StateFilter(Admin.task_tasks_delete))
async def delete_task(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    uid = await get_tasks_uid_by_name(session, callback.data)
    await delete_tasks(session, uid, callback.data)
    await state.set_state(Admin.join)
    await callback.message.edit_text(text=LEXICON_RU['menu_message'], reply_markup=callback_map_admin['menu'])


@router.callback_query(StateFilter(Admin.task_get))
async def get_task_names(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    tasks = await get_tasks_by_theme(session, callback.data)
    if not tasks:
        await callback.answer(text='Нет созданных заданий')
        return
    await state.set_state(Admin.task_tasks)
    await callback.message.edit_reply_markup(reply_markup=callback_map_admin['get_task'](tasks))


@router.callback_query(StateFilter(Admin.task_tasks))
async def get_task_uid(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    uid = await get_tasks_uid_by_name(session, callback.data)
    await callback.message.answer(text=f"Ключ этой задачи - {uid}")
    await state.set_state(Admin.join)
    await callback.message.answer(text=LEXICON_RU['menu_message'], reply_markup=callback_map_admin['menu'])
    await callback.message.delete()


@router.callback_query(StateFilter(Admin.task_theme), F.data == 'create_theme')
async def create_task_add_theme(callback: CallbackQuery, state: FSMContext):
    msg = await callback.message.answer(text="Введите тему")
    await state.set_data({"theme": callback.data, "msg": msg.message_id})
    await callback.message.delete()


@router.callback_query(StateFilter(Admin.task_theme))
async def create_task_pick_theme(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Admin.task_name)
    msg = await callback.message.answer(text='Введите имя задачи')
    await state.set_data({"theme": callback.data, "msg": msg.message_id})
    await callback.message.delete()


@router.message(StateFilter(Admin.task_theme), F.content_type == ContentType.TEXT)
async def create_task_add_name(message: Message, state: FSMContext, bot: Bot, session: AsyncSession):
    data = await state.get_data()
    msg = data.get('msg')
    if await theme_exists(session, message.text):
        await bot.edit_message_text(chat_id=message.from_user.id, message_id=msg,
                                    text='Тема уже существует. Введите другую тему')
        await message.delete()
        return
    await state.set_state(Admin.task_name)
    await state.set_data({"theme": message.text, "msg": msg})
    await bot.edit_message_text(chat_id=message.from_user.id, message_id=msg,
                                text='Введите название задачи (не длиннее 64 символов)')
    await message.delete()


@router.message(StateFilter(Admin.task_name), F.content_type == ContentType.TEXT, F.text.len() < 64)
async def create_task_add_description(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    theme: str = data.get('theme', '')
    msg = data.get('msg')
    await state.set_state(Admin.task_description)
    await state.set_data({"name": message.text, "theme": theme, "msg": msg})
    await message.delete()
    await bot.edit_message_text(chat_id=message.from_user.id, message_id=msg, text='Введите описание задачи')


@router.message(StateFilter(Admin.task_description), F.content_type == ContentType.TEXT)
async def create_task_add_score(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    theme: str = data.get('theme', '')
    name: str = data.get('name', '')
    msg = data.get('msg')
    await state.set_state(Admin.task_score)
    await state.set_data({"name": name, "theme": theme, "description": message.text, "msg": msg})
    await bot.edit_message_text(chat_id=message.from_user.id, message_id=msg,
                                text='Введите количество баллов за выполнение задачи')
    await message.delete()


@router.message(StateFilter(Admin.task_score), F.text.isdigit())
async def create_task_add_final(message: Message, state: FSMContext, bot: Bot, session: AsyncSession):
    data = await state.get_data()
    theme: str = data.get('theme', '')
    name: str = data.get('name', '')
    description: str = data.get('description', '')
    msg = data.get('msg')
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
    await bot.edit_message_text(chat_id=message.from_user.id, message_id=msg,
                                text=f'Задача успешно создана. UID = {uid}', reply_markup=callback_map_admin['menu'])
    await message.delete()

@router.message(StateFilter(*callback_error_input))
async def error_create_theme(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    msg = data.get('msg')
    await bot.delete_message(chat_id=message.from_user.id, message_id=msg)
    str_state = str(await state.get_state())
    keyboard = callback_map_admin.get(str_state, None)
    if keyboard is None:
        msg = await message.answer(text=f'Пожалуйста введите текст\n\n{LEXICON_RU["admin"][str(await state.get_state())]["message"]}')
    else:
        msg = await message.answer(text=f'Пожалуйста введите текст\n\n{LEXICON_RU["admin"][str(await state.get_state())]["message"]}', reply_markup=keyboard)
    await message.delete()
    data['msg'] = msg.message_id
    await state.set_data(data)