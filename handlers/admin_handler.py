from aiogram import F
from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from filters.menu_filters import AdminMenuCallbackFactory
from handlers.admin import survey_edit_handler, task_edit_handler, product_edit_handler, event_edit_handler
from keyboards.inline_keyboards import callback_map_admin
from lexicon.lexicon_ru import LEXICON_RU
from services.database import get_themes_with_tasks, get_all_themes, get_themes_with_surveys, get_all_event_themes
from states.admin_states import Admin

router = Router()
router.include_router(survey_edit_handler.router)
router.include_router(event_edit_handler.router)
router.include_router(product_edit_handler.router)
router.include_router(task_edit_handler.router)


@router.callback_query(StateFilter(Admin.join), AdminMenuCallbackFactory.filter(F.next_keyboard == 'create_task'))
async def create_task_themes(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    themes = await get_all_themes(session)
    await state.set_state(Admin.task_theme)
    await callback.message.edit_reply_markup(reply_markup=callback_map_admin['create_task'](themes))

@router.callback_query(StateFilter(Admin.join), AdminMenuCallbackFactory.filter(F.next_keyboard == 'create_survey'))
async def create_task_themes(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    themes = await get_all_themes(session)
    await state.set_state(Admin.survey_theme)
    await callback.message.edit_reply_markup(reply_markup=callback_map_admin['create_survey'](themes))

@router.callback_query(StateFilter(Admin.join), AdminMenuCallbackFactory.filter(F.next_keyboard == 'create_event'))
async def create_task_themes(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    themes = await get_all_event_themes(session)
    await state.set_state(Admin.event_theme)
    await callback.message.edit_reply_markup(reply_markup=callback_map_admin['create_event'](themes))

@router.callback_query(StateFilter(Admin.join), AdminMenuCallbackFactory.filter(F.next_keyboard == 'get_survey_themes'))
async def create_task_themes(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    themes = await get_themes_with_surveys(session)
    if not themes:
        await callback.answer(text='Нет созданных заданий')
        return
    await state.set_state(Admin.survey_edit_pick_theme)
    await callback.message.edit_reply_markup(reply_markup=callback_map_admin['get_survey_themes'](themes))

@router.callback_query(StateFilter(Admin.join), AdminMenuCallbackFactory.filter(F.next_keyboard == 'change_main_survey'))
async def create_task_themes(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Admin.survey_main_pick)
    await callback.message.edit_text(text=LEXICON_RU['admin']['change_main_survey']['message'], reply_markup=callback_map_admin['change_main_survey'])


@router.callback_query(StateFilter(Admin.join), AdminMenuCallbackFactory.filter(F.next_keyboard == 'create_product'))
async def create_task_themes(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Admin.product_name)
    await state.set_data({'msg': callback.message.message_id})
    await callback.message.edit_text(text='Введите название товара (не длиннее 64 символов)')


@router.callback_query(StateFilter(Admin.join), AdminMenuCallbackFactory.filter(F.next_keyboard == 'edit_task'))
async def get_task_themes(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    themes = await get_themes_with_tasks(session)
    if not themes:
        await callback.answer(text='Нет созданных заданий')
        return
    await state.set_state(Admin.edit_task)
    await callback.message.edit_reply_markup(reply_markup=callback_map_admin['get_themes'](themes))

@router.callback_query(
    StateFilter(Admin),
    AdminMenuCallbackFactory.filter(F.current_keyboard == 'back'))
async def change_menu_keyboard(callback: CallbackQuery, callback_data: AdminMenuCallbackFactory, state: FSMContext):
    if await state.get_state() != Admin.join:
        await state.set_state(Admin.join)
    await callback.message.edit_text(
        text=LEXICON_RU['admin'][callback_data.next_keyboard]['message'],
        reply_markup=callback_map_admin[callback_data.next_keyboard]
    )

@router.callback_query(
    StateFilter(Admin.join, Admin.edit_task, Admin.task_tasks, Admin.task_theme, Admin.survey_theme),
    AdminMenuCallbackFactory.filter())
async def change_menu_keyboard(callback: CallbackQuery, callback_data: AdminMenuCallbackFactory, state: FSMContext):
    if await state.get_state() != Admin.join:
        await state.set_state(Admin.join)
    await callback.message.edit_text(
        text=LEXICON_RU['admin'][callback_data.next_keyboard]['message'],
        reply_markup=callback_map_admin[callback_data.next_keyboard]
    )

