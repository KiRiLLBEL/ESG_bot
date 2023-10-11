from aiogram import Router, F, Bot
from aiogram.enums import ContentType
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.inline_keyboards import callback_map_admin
from lexicon.lexicon_ru import LEXICON_RU
from services.database import theme_exists_pool, add_survey
from states.admin_states import Admin

router = Router()

@router.callback_query(StateFilter(Admin.pool_main_pick), F.data.in_(['b2b', 'b2c']))
async def pick_theme_for_main_poll(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Admin.pool_score)
    msg = await callback.message.answer(text='Введите количество баллов за опрос')
    await state.set_data({"name": callback.data, "theme": "main", "msg": msg.message_id})
    await callback.message.delete()

@router.callback_query(StateFilter(Admin.pool_theme), F.data == 'create_theme')
async def create_task_add_theme(callback: CallbackQuery, state: FSMContext):
    msg = await callback.message.answer(text="Введите тему")
    await state.set_data({"theme": callback.data, "msg": msg.message_id})
    await callback.message.delete()


@router.callback_query(StateFilter(Admin.pool_theme))
async def create_task_pick_theme(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Admin.pool_name)
    msg = await callback.message.answer(text='Введите название опроса')
    await state.set_data({"theme": callback.data, "msg": msg.message_id})
    await callback.message.delete()


@router.message(StateFilter(Admin.pool_theme), F.content_type == ContentType.TEXT)
async def create_poll_add_name(message: Message, state: FSMContext, bot: Bot, session: AsyncSession):
    data = await state.get_data()
    msg = data.get('msg')
    if await theme_exists_pool(session, message.text):
        await bot.edit_message_text(chat_id=message.from_user.id, message_id=msg,
                                    text='Тема уже существует. Введите другую тему')
        await message.delete()
        return
    await state.set_state(Admin.pool_name)
    await state.set_data({"theme": message.text, "msg": msg})
    await bot.edit_message_text(chat_id=message.from_user.id, message_id=msg,
                                text='Введите название опроса (не длиннее 64 символов)')
    await message.delete()


@router.message(StateFilter(Admin.pool_name), F.content_type == ContentType.TEXT, F.text.len() < 64)
async def create_task_add_description(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    theme: str = data.get('theme', '')
    msg = data.get('msg')
    await state.set_state(Admin.pool_score)
    await state.set_data({"name": message.text, "theme": theme, "msg": msg})
    await bot.edit_message_text(chat_id=message.from_user.id, message_id=msg, text='Введите количество баллов за опрос')
    await message.delete()




@router.message(StateFilter(Admin.pool_score), F.text.isdigit())
async def create_pool_add_score(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    theme: str = data.get('theme', '')
    name: str = data.get('name', '')
    msg = data.get('msg')
    await state.set_state(Admin.pool_questions)
    await state.set_data({
        "name": name,
        "theme": theme,
        "score": int(message.text),
        "msg": msg,
        "questions": [],
        "current_question": None,
        "current_options": []
    })
    await message.delete()
    await bot.edit_message_text(chat_id=message.from_user.id, message_id=msg, text='Введите вопрос',
                                reply_markup=callback_map_admin['Admin:pool_questions'])

@router.message(StateFilter(Admin.pool_questions), F.content_type == ContentType.TEXT)
async def create_question(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    print(data)
    msg = data.get('msg')
    await state.set_state(Admin.pool_options)
    if data['current_question']:
        data['questions'].append({'text': data['current_question'], 'options': data['current_options']})
        data['current_options'] = []
    data['current_question'] = message.text
    await state.set_data(data)
    await bot.edit_message_text(chat_id=message.from_user.id, message_id=msg,
                                text="Введите текст варианта ответа или нажмите кнопку завершить, чтобы закончить "
                                     "вопрос",
                                reply_markup=callback_map_admin['Admin:pool_options'])
    await message.delete()



@router.callback_query(StateFilter(Admin.pool_questions), F.data == 'end_questions')
async def questions_text(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    if not data['current_options']:
        await callback.message.edit_text(text="Опрос должен иметь хотя бы один вопрос. Введите текст вопроса:",
                                         reply_markup=callback_map_admin['Admin:pool_questions'])
    else:
        if data['current_question']:
            data['questions'].append({'text': data['current_question'], 'options': data['current_options']})
            data['current_options'] = []
        await add_survey(session, data)
        await callback.message.edit_text(text=LEXICON_RU['admin']['menu']['message'],
                                         reply_markup=callback_map_admin['menu'])
        await callback.answer(text='Опрос успешно создан')
        await state.set_state(Admin.join)


@router.message(StateFilter(Admin.pool_options), F.content_type == ContentType.TEXT)
async def options_text(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    print(data)
    msg = data.get('msg')
    if not data['current_options']:
        await bot.edit_message_text(chat_id=message.from_user.id, message_id=msg,
                                    text="Введите текст следующего варианта ответа или нажмите кнопку завершить, "
                                         "чтобы закончить вопрос",
                                    reply_markup=callback_map_admin['Admin:pool_options'])
    data['current_options'].append(message.text)
    await state.set_data(data)
    await message.delete()


@router.callback_query(StateFilter(Admin.pool_options), F.data == 'end_options')
async def end_options(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    print(data)
    if not data['current_options']:
        await callback.message.edit_text(
            text="Вопрос должен иметь хотя бы один вариант ответа. Введите текст варианта ответа:",
            reply_markup=callback_map_admin['Admin:pool_options'])
    else:
        await callback.message.edit_text(
            text="Введите текст следующего вопроса нажмите кнопку завершить, чтобы закончить опрос:",
            reply_markup=callback_map_admin['Admin:pool_questions'])
        await state.set_state(Admin.pool_questions)
        await state.set_data(data)
