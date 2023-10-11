from aiogram import F, Bot
from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from filters.menu_filters import AdminMenuCallbackFactory
from handlers.admin import pool_edit_handler, task_edit_handler, product_edit_handler
from keyboards.inline_keyboards import callback_map_admin
from lexicon.lexicon_ru import LEXICON_RU
from services.database import get_all_themes, get_all_themes_all_table
from states.admin_states import Admin, callback_error_input

router = Router()
router.include_router(pool_edit_handler.router)
router.include_router(task_edit_handler.router)
router.include_router(product_edit_handler.router)


@router.callback_query(StateFilter(Admin.join), AdminMenuCallbackFactory.filter(F.next_keyboard == 'create_task'))
async def create_task_themes(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    themes = await get_all_themes_all_table(session)
    await state.set_state(Admin.task_theme)
    await callback.message.edit_reply_markup(reply_markup=callback_map_admin['create_task'](themes))


@router.callback_query(StateFilter(Admin.join), AdminMenuCallbackFactory.filter(F.next_keyboard == 'create_poll'))
async def create_task_themes(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    themes = await get_all_themes_all_table(session)
    await state.set_state(Admin.pool_theme)
    await callback.message.edit_reply_markup(reply_markup=callback_map_admin['create_poll'](themes))

@router.callback_query(StateFilter(Admin.join), AdminMenuCallbackFactory.filter(F.next_keyboard == 'change_main_poll'))
async def create_task_themes(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Admin.pool_main_pick)
    await callback.message.edit_text(text=LEXICON_RU['admin']['change_main_poll']['message'], reply_markup=callback_map_admin['change_main_poll'])


@router.callback_query(StateFilter(Admin.join), AdminMenuCallbackFactory.filter(F.next_keyboard == 'create_product'))
async def create_task_themes(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Admin.product_name)
    await state.set_data({'msg': callback.message.message_id})
    await callback.message.edit_text(text='Введите название товара (не длиннее 64 символов)')


@router.callback_query(StateFilter(Admin.join), AdminMenuCallbackFactory.filter(F.next_keyboard == 'get_task'))
async def get_task_themes(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    themes = await get_all_themes(session)
    if not themes:
        await callback.answer(text='Нет созданных заданий')
        return
    await state.set_state(Admin.task_get)
    await callback.message.edit_reply_markup(reply_markup=callback_map_admin['get_task'](themes))


@router.callback_query(StateFilter(Admin.join), AdminMenuCallbackFactory.filter(F.next_keyboard == 'delete_task'))
async def get_task_themes(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    themes = await get_all_themes(session)
    if not themes:
        await callback.answer(text='Нет созданных заданий')
        return
    await state.set_state(Admin.task_theme_delete)
    await callback.message.edit_reply_markup(reply_markup=callback_map_admin['delete_task'](themes))


@router.callback_query(
    StateFilter(Admin.join, Admin.task_get, Admin.task_theme, Admin.task_theme_delete, Admin.pool_theme),
    AdminMenuCallbackFactory.filter())
async def change_menu_keyboard(callback: CallbackQuery, callback_data: AdminMenuCallbackFactory, state: FSMContext):
    if await state.get_state() != Admin.join:
        await state.set_state(Admin.join)
    await callback.message.edit_text(
        text=LEXICON_RU['admin'][callback_data.next_keyboard]['message'],
        reply_markup=callback_map_admin[callback_data.next_keyboard]
    )

