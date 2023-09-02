from aiogram import F
from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.filters.command import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ContentType, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from filters.start_filters import StatusInMessage
from keyboards.inline_keyboards import menu_keyboard, answer_quiz_keyboard, callback_map_admin
from keyboards.reply_keyboards import start_keyboard, remove_keyboard
from lexicon.lexicon_ru import LEXICON_RU
from services.database import get_user_by_tg_id, register_user, delete_quiz
from states.start_states import Start, Quiz, register_state
from states.admin_states import Admin
from config_data.config import load_config


router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext, session: AsyncSession) -> None:
    if message.from_user.id in load_config().tg_bot.admin_ids:
        await state.set_state(Admin.pick)
        await message.answer(text='Вы админ. Выберите режим работы с ботом', reply_markup=callback_map_admin['pick'])
        return
    user = await get_user_by_tg_id(session=session, user_id=message.from_user.id)
    if user is None:
        await state.set_state(Start.registration)
        await message.answer(text=LEXICON_RU['register'], reply_markup=start_keyboard)
    else:
        await message.answer(text=LEXICON_RU[user.status]['return'], reply_markup=menu_keyboard[user.status])


@router.callback_query(StateFilter(Admin.pick), F.data == 'pick_user')
async def picked_user(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await state.clear()
    user = await get_user_by_tg_id(session=session, user_id=callback.from_user.id)
    if user is None:
        await state.set_state(Start.registration)
        await callback.message.answer(text=LEXICON_RU['register'], reply_markup=start_keyboard)
    else:
        await callback.message.answer(text=LEXICON_RU[user.status]['return'], reply_markup=menu_keyboard[user.status])
    await callback.message.delete()

@router.callback_query(StateFilter(Admin.pick), F.data == 'pick_admin')
async def picked_user(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Admin.join)
    await callback.message.answer(text=LEXICON_RU['menu_message'], reply_markup=callback_map_admin['menu'])
    await callback.message.delete()

@router.message(StateFilter(Start.registration), StatusInMessage())
async def register_start_handler(message: Message, state: FSMContext, status: str) -> None:
    await state.set_state(register_state[status])
    await message.answer(text=LEXICON_RU[status]['register_message'], reply_markup=remove_keyboard)


@router.message(StateFilter(register_state['b2b']), F.content_type == ContentType.TEXT)
@router.message(StateFilter(register_state['b2c']), F.content_type == ContentType.TEXT)
async def register_handler(message: Message, state: FSMContext, session: AsyncSession) -> None:
    status = 'b2b' if await state.get_state() == Start.registration_b2b else 'b2c'
    await register_user(session=session, user_id=message.from_user.id, name=message.text, score=0, status=status)
    await message.answer(text=LEXICON_RU['registration_complete'])
    await message.answer(text=LEXICON_RU[status]['quiz_start'])
    await message.answer(text=LEXICON_RU[status]['quiz_questions'][0], reply_markup=answer_quiz_keyboard)
    await state.set_state(Quiz.activate)
    await delete_quiz(session, message.from_user.id)
    await state.set_data({'status': status, 'index': 0})
