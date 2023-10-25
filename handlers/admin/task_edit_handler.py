from aiogram import Router, Bot, F
from aiogram.enums import ContentType
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from filters.menu_filters import AdminMenuCallbackFactory
from keyboards.inline_keyboards import callback_map_admin
from lexicon.lexicon_ru import LEXICON_RU
from services.database import get_tasks_by_theme_id, delete_tasks, theme_exists, add_task, \
    add_theme, get_task_by_id, update_task_title, update_task_value, update_task_description
from states.admin_states import Admin, callback_error_input

router = Router()

@router.callback_query(StateFilter(Admin.edit_task))
async def get_task_names(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    tasks = await get_tasks_by_theme_id(session, int(callback.data))
    if not tasks:
        await callback.answer(text='Нет созданных заданий')
        return
    await state.set_state(Admin.task_tasks)
    await callback.message.edit_reply_markup(reply_markup=callback_map_admin['edit_task'](tasks))


@router.callback_query(StateFilter(Admin.task_tasks))
async def get_task_uid(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    id = int(callback.data)
    task = await get_task_by_id(session, id)
    await callback.message.answer(text=f"Ключ этой задачи: {id}\nНазвание: {task.title}\nОписание: {task.description}\nБаллы: {task.value}\n\n{LEXICON_RU['admin']['task_choose_edit']['message']}", reply_markup=callback_map_admin['task_choose_edit'])
    await state.set_state(Admin.task_choose_edit)
    await state.set_data({"task_id": id})
    await callback.message.delete()

@router.callback_query(StateFilter(Admin.task_choose_edit), AdminMenuCallbackFactory.filter(F.next_keyboard == 'task_editor'))
async def get_task_uid(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    await state.set_state(Admin.task_editor)
    await state.set_data(data)
    print(str(await state.get_state()))
    await callback.message.answer(text=LEXICON_RU['admin']['task_editor']['message'], reply_markup=callback_map_admin['task_editor'])
    await callback.message.delete()

@router.callback_query(StateFilter(Admin.task_editor),  AdminMenuCallbackFactory.filter(F.next_keyboard == 'change_task_title'))
async def get_task_uid(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await state.set_state(Admin.task_edit_title)
    data = await state.get_data()
    message = await callback.message.answer(text="Введите новое название")
    data['msg'] = message.message_id
    await state.set_data(data)
    await callback.message.delete()

@router.message(StateFilter(Admin.task_edit_title), F.content_type == ContentType.TEXT, F.text.len() < 64)
async def create_task_add_description(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    data = await state.get_data()
    id = data.get('task_id', 0)
    msg = data.get('msg', 0)
    await state.set_state(Admin.join)
    await update_task_title(session, id, message.text)
    await message.delete()
    await bot.edit_message_text(chat_id=message.from_user.id, message_id=msg,
                                text=f'Название задачи успешно изменено', reply_markup=callback_map_admin['menu'])

@router.callback_query(StateFilter(Admin.task_editor),   AdminMenuCallbackFactory.filter(F.next_keyboard == 'change_task_value'))
async def get_task_uid(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await state.set_state(Admin.task_edit_value)
    data = await state.get_data()
    id = data.get('task_id', 0)
    msg = data.get('msg', 0)
    message = await callback.message.answer(text="Введите новую ценность задания")
    data['msg'] = message.message_id
    await state.set_data(data)
    await callback.message.delete()

@router.message(StateFilter(Admin.task_edit_value), F.text.isdigit())
async def create_task_add_description(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    data = await state.get_data()
    id = data.get('task_id', 0)
    msg = data.get('msg', 0)
    await state.set_state(Admin.join)
    await update_task_value(session, id, int(message.text))
    await message.delete()
    await bot.edit_message_text(chat_id=message.from_user.id, message_id=msg,
                                text=f'Стоимость задачи успешно изменена', reply_markup=callback_map_admin['menu'])

@router.callback_query(StateFilter(Admin.task_editor), AdminMenuCallbackFactory.filter(F.next_keyboard == 'change_task_description'))
async def get_task_uid(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await state.set_state(Admin.task_edit_description)
    data = await state.get_data()
    id = data.get('task_id', 0)
    msg = data.get('msg', 0)
    message = await callback.message.answer(text="Введите новое описание задачи")
    data['msg'] = message.message_id
    await state.set_data(data)
    await callback.message.delete()

@router.message(StateFilter(Admin.task_edit_description), F.content_type == ContentType.TEXT, F.text.len() < 64)
async def create_task_add_description(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    data = await state.get_data()
    id = data.get('task_id', 0)
    msg = data.get('msg', 0)
    await state.set_state(Admin.join)
    await update_task_description(session, id, message.text)
    await message.delete()
    await bot.edit_message_text(chat_id=message.from_user.id, message_id=msg,
                                text=f'Описание задачи успешно изменено', reply_markup=callback_map_admin['menu'])


@router.callback_query(StateFilter(Admin.task_choose_edit), AdminMenuCallbackFactory.filter(F.next_keyboard == 'menu'))
async def get_task_uid(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    id = data.get('task_id', 0)
    await delete_tasks(session, id)
    await state.set_state(Admin.join)
    await callback.message.answer(text="Задание успешно удален", reply_markup=callback_map_admin['menu'])
    await callback.message.delete()

@router.callback_query(StateFilter(Admin.task_choose_edit))
async def get_task_uid(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await state.set_state(Admin.join)
    await callback.message.answer(text=LEXICON_RU['admin']['menu']['message'], reply_markup=callback_map_admin['menu'])
    await callback.message.delete()

@router.callback_query(StateFilter(Admin.task_theme), F.data == 'create_theme')
async def create_task_add_theme(callback: CallbackQuery, state: FSMContext):
    msg = await callback.message.answer(text="Введите тему")
    await state.set_data({"theme": 0, "msg": msg.message_id})
    await callback.message.delete()


@router.callback_query(StateFilter(Admin.task_theme))
async def create_task_pick_theme(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Admin.task_name)
    msg = await callback.message.answer(text='Введите имя задачи')
    await state.set_data({"theme": int(callback.data), "msg": msg.message_id})
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
    theme_id = await add_theme(session, message.text)
    await state.set_data({"theme": theme_id, "msg": msg})
    await bot.edit_message_text(chat_id=message.from_user.id, message_id=msg,
                                text='Введите название задачи (не длиннее 64 символов)')
    await message.delete()


@router.message(StateFilter(Admin.task_name), F.content_type == ContentType.TEXT, F.text.len() < 64)
async def create_task_add_description(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    theme = data.get('theme', 0)
    msg = data.get('msg')
    await state.set_state(Admin.task_description)
    await state.set_data({"name": message.text, "theme": theme, "msg": msg})
    await message.delete()
    await bot.edit_message_text(chat_id=message.from_user.id, message_id=msg, text='Введите описание задачи')


@router.message(StateFilter(Admin.task_description), F.content_type == ContentType.TEXT)
async def create_task_add_score(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    theme = data.get('theme', 0)
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
    theme_id = data.get('theme', 0)
    name: str = data.get('name', '')
    description: str = data.get('description', '')
    msg = data.get('msg')
    id = await add_task(
        session=session,
        title=name,
        theme_id=theme_id,
        description=description,
        value=int(message.text)
    )
    await state.set_state(Admin.join)
    await bot.edit_message_text(chat_id=message.from_user.id, message_id=msg,
                                text=f'Задача успешно создана. UID = {id}', reply_markup=callback_map_admin['menu'])
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