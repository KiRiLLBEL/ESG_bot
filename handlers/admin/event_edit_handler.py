from datetime import datetime

from aiogram import Router, Bot, F
from aiogram.enums import ContentType
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from filters.menu_filters import AdminMenuCallbackFactory
from keyboards.inline_keyboards import callback_map_admin
from lexicon.lexicon_ru import LEXICON_RU
from services.database import event_theme_exists, add_event_theme, add_event
from states.admin_states import Admin

router = Router()

@router.callback_query(StateFilter(Admin.event_theme), F.data == 'create_theme')
async def create_task_add_theme(callback: CallbackQuery, state: FSMContext):
    msg = await callback.message.answer(text="Введите тему")
    await state.set_data({"theme": 0, "msg": msg.message_id})
    await callback.message.delete()


@router.callback_query(StateFilter(Admin.event_theme))
async def create_task_pick_theme(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Admin.event_title)
    msg = await callback.message.answer(text='Введите название мероприятия (не длиннее 64 символов)')
    await state.set_data({"theme": int(callback.data), "msg": msg.message_id})
    await callback.message.delete()


@router.message(StateFilter(Admin.event_theme), F.content_type == ContentType.TEXT)
async def create_task_add_name(message: Message, state: FSMContext, bot: Bot, session: AsyncSession):
    data = await state.get_data()
    msg = data.get('msg')
    if await event_theme_exists(session, message.text):
        await bot.edit_message_text(chat_id=message.from_user.id, message_id=msg,
                                    text='Тема уже существует. Введите другую тему')
        await message.delete()
        return
    await state.set_state(Admin.event_title)
    theme_id = await add_event_theme(session, message.text)
    await state.set_data({"theme": theme_id, "msg": msg})
    await bot.edit_message_text(chat_id=message.from_user.id, message_id=msg,
                                text='Введите название мероприятия (не длиннее 64 символов)')
    await message.delete()

@router.message(StateFilter(Admin.event_title), F.content_type == ContentType.TEXT, F.text.len() < 64)
async def create_task_add_description(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    msg = data.get('msg')
    await state.set_state(Admin.event_description)
    data['title'] = message.text
    await state.set_data(data)
    await message.delete()
    await bot.edit_message_text(chat_id=message.from_user.id, message_id=msg, text='Введите описание мероприятия')

@router.message(StateFilter(Admin.event_description), F.content_type == ContentType.TEXT)
async def create_task_add_description(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    msg = data.get('msg')
    await state.set_state(Admin.event_place)
    data['description'] = message.text
    await state.set_data(data)
    await message.delete()
    await bot.edit_message_text(chat_id=message.from_user.id, message_id=msg, text='Введите место проведения')

@router.message(StateFilter(Admin.event_place), F.content_type == ContentType.TEXT)
async def create_task_add_description(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    msg = data.get('msg')
    await state.set_state(Admin.event_organizer)
    data['place'] = message.text
    await state.set_data(data)
    await message.delete()
    await bot.edit_message_text(chat_id=message.from_user.id, message_id=msg, text='Введите организатора')

@router.message(StateFilter(Admin.event_organizer), F.content_type == ContentType.TEXT)
async def create_task_add_description(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    msg = data.get('msg')
    await state.set_state(Admin.event_image_url)
    data['organizer'] = message.text
    await state.set_data(data)
    await message.delete()
    await bot.edit_message_text(chat_id=message.from_user.id, message_id=msg, text='Введите ссылку на изображение')

@router.message(StateFilter(Admin.event_image_url), F.content_type == ContentType.TEXT, F.text.regexp(r'http(s)?://\S+'))
async def create_task_add_description(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    msg = data.get('msg')
    await state.set_state(Admin.event_capacity)
    data['image_url'] = message.text
    await state.set_data(data)
    await message.delete()
    await bot.edit_message_text(chat_id=message.from_user.id, message_id=msg, text='Введите вместимость мероприятия')


@router.message(StateFilter(Admin.event_capacity),  F.text.isdigit())
async def create_task_add_description(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    msg = data.get('msg')
    await state.set_state(Admin.event_value)
    data['capacity'] = int(message.text)
    await state.set_data(data)
    await message.delete()
    await bot.edit_message_text(chat_id=message.from_user.id, message_id=msg, text='Введите баллы за мероприятие')

@router.message(StateFilter(Admin.event_value),  F.text.isdigit())
async def create_task_add_description(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    msg = data.get('msg')
    await state.set_state(Admin.event_date)
    data['value'] = int(message.text)
    await state.set_data(data)
    await message.delete()
    await bot.edit_message_text(chat_id=message.from_user.id, message_id=msg, text='Введите дату проведения мероприятия в формате ГГГГ-ММ-ДД.')

@router.message(StateFilter(Admin.event_date), F.content_type == ContentType.TEXT)
async def create_task_add_description(message: Message, state: FSMContext, bot: Bot, session: AsyncSession):
    data = await state.get_data()
    msg = data.get('msg')
    await state.set_state(Admin.event_capacity)
    try:
        data['date'] = datetime.strptime(message.text, '%Y-%m-%d').date()
    except ValueError:
        await bot.delete_message(chat_id=message.from_user.id, message_id=msg)
        msg = await message.answer(text="Неверный формат даты. Пожалуйста, используйте формат ГГГГ-ММ-ДД.")
        data['msg'] = msg.message_id
        await state.set_data(data)
        await message.delete()
        return
    await add_event(
        session=session,
        title=data['title'],
        description=data['description'],
        place=data['place'],
        capacity=data['capacity'],
        date=data['date'],
        organizer=data['organizer'],
        image_url=data['image_url'],
        value=data['value'],
        theme_id=data['theme']
    )
    await state.set_state(Admin.join)
    await bot.edit_message_text(chat_id=message.from_user.id, message_id=msg, text=f'Мероприятие успешно создано', reply_markup=callback_map_admin['menu'])
    await message.delete()
