from aiogram import Router, F, Bot
from aiogram.enums import ContentType
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.inline_keyboards import callback_map_admin, keyboard_survey_pagination
from lexicon.lexicon_ru import LEXICON_RU
from services.database import theme_exists_survey, add_survey, add_theme, theme_exists_by_id, add_theme_by_id, \
    get_surveys_by_theme_id, get_survey_by_id, get_option_by_id, get_question_by_id, delete_option_and_answers, \
    update_option_text, update_question_text, delete_question_and_answers
from states.admin_states import Admin

router = Router()

@router.callback_query(StateFilter(Admin.survey_main_pick), F.data.in_(['business', 'person']))
async def pick_theme_for_main_poll(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    if not await theme_exists_by_id(session, 0):
        await add_theme_by_id(session, 0)
    await state.set_state(Admin.survey_score)
    msg = await callback.message.answer(text='Введите количество баллов за опрос')
    await state.set_data({"name": callback.data, "type": callback.data, "msg": msg.message_id, "theme": 0})
    await callback.message.delete()

@router.callback_query(StateFilter(Admin.survey_theme), F.data == 'create_theme')
async def create_task_add_theme(callback: CallbackQuery, state: FSMContext):
    msg = await callback.message.answer(text="Введите тему")
    await state.set_data({"theme": callback.data, "msg": msg.message_id})
    await callback.message.delete()


@router.callback_query(StateFilter(Admin.survey_theme))
async def create_task_pick_theme(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Admin.survey_name)
    msg = await callback.message.answer(text='Введите название опроса')
    await state.set_data({"theme": int(callback.data), "msg": msg.message_id})
    await callback.message.delete()

@router.callback_query(StateFilter(Admin.survey_edit_pick_theme))
async def create_task_pick_theme(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    surveys = await get_surveys_by_theme_id(session, int(callback.data))
    await state.set_state(Admin.survey_edit_pick_survey)
    await callback.message.edit_reply_markup(reply_markup=callback_map_admin['edit_survey'](surveys))

@router.callback_query(StateFilter(Admin.survey_edit_pick_survey), F.data == 'current_page')
async def handle_page_callback(callback: CallbackQuery):
    await callback.answer(text="Вы можете изменять вопросы и ответы")
@router.callback_query(StateFilter(Admin.survey_edit_pick_survey), F.data.startswith('page:'))
async def handle_page_callback(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    current_page = int(callback.data.split(':')[1])
    data = await state.get_data()
    survey_id = data['survey_id']
    survey = await get_survey_by_id(session, survey_id)
    total_question = len(survey.questions)
    question = survey.questions[current_page - 1]
    text = f"Вопрос: {question.text}\n"
    for i, ans in enumerate(question.options):
        text += f"Ответ №{i + 1}: {ans.text}\n"
    await callback.message.edit_text(text=text, reply_markup=keyboard_survey_pagination(current_page, total_question, question))

@router.callback_query(StateFilter(Admin.survey_edit_pick_survey), F.data.startswith('opt:'))
async def handle_page_callback(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    option_id = int(callback.data.split(':')[1])
    option = await get_option_by_id(session, option_id)
    await state.set_state(Admin.survey_edit_option)
    data = await state.get_data()
    data['option_id'] = option_id
    await state.set_data(data)
    await callback.message.edit_text(text=f"Текст ответа: {option.text}", reply_markup=callback_map_admin['edit_option'])

@router.callback_query(StateFilter(Admin.survey_edit_option), F.data == 'edit_option')
async def handle_page_callback(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    message = await callback.message.answer(text="Введите новый текст ответа")
    data['msg'] = message.message_id
    await state.set_data(data)
    await callback.message.delete()

@router.message(StateFilter(Admin.survey_edit_option), F.content_type == ContentType.TEXT, F.text.len() < 64)
async def create_task_add_description(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    data = await state.get_data()
    id = data.get('option_id', 0)
    msg = data.get('msg', 0)
    await state.set_state(Admin.join)
    await update_option_text(session, id, message.text)
    await message.delete()
    await bot.edit_message_text(chat_id=message.from_user.id, message_id=msg,
                                text=f'Текст вопроса успешно изменен', reply_markup=callback_map_admin['menu'])



@router.callback_query(StateFilter(Admin.survey_edit_option), F.data == 'delete_option')
async def handle_page_callback(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    option_id = data['option_id']
    option = await get_option_by_id(session, option_id)
    question = option.question
    if len(question.options) < 2:
        await callback.answer(text="Ответов на вопрос должно быть больше одного")
        return
    else:
        await delete_option_and_answers(session, option_id)
    await state.set_state(Admin.join)
    await callback.message.edit_text(text=LEXICON_RU['admin']['menu']['message'],
                                     reply_markup=callback_map_admin['menu'])

@router.callback_query(StateFilter(Admin.survey_edit_pick_survey), F.data.startswith('que:'))
async def handle_page_callback(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    question_id = int(callback.data.split(':')[1])
    question = await get_question_by_id(session, question_id)
    await state.set_state(Admin.survey_edit_question)
    data = await state.get_data()
    data['question_id'] = question_id
    await state.set_data(data)
    await callback.message.edit_text(text=f"Текст вопроса: {question.text}", reply_markup=callback_map_admin['edit_question'])

@router.callback_query(StateFilter(Admin.survey_edit_question), F.data == 'edit_question')
async def handle_page_callback(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    message = await callback.message.answer(text="Введите новый текст вопроса")
    data['msg'] = message.message_id
    await state.set_data(data)
    await callback.message.delete()

@router.message(StateFilter(Admin.survey_edit_question), F.content_type == ContentType.TEXT)
async def create_task_add_description(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    data = await state.get_data()
    id = data.get('question_id', 0)
    msg = data.get('msg', 0)
    await state.set_state(Admin.join)
    await update_question_text(session, id, message.text)
    await message.delete()
    await bot.edit_message_text(chat_id=message.from_user.id, message_id=msg,
                                text=f'Текст вопроса успешно изменен', reply_markup=callback_map_admin['menu'])



@router.callback_query(StateFilter(Admin.survey_edit_question), F.data == 'delete_question')
async def handle_page_callback(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    question_id = data['question_id']
    question = await get_question_by_id(session, question_id)
    survey = question.survey
    if len(survey.questions) < 2:
        await callback.answer(text="Вопросов должно быть больше одного")
        return
    else:
        await delete_question_and_answers(session, question_id)
    await state.set_state(Admin.join)
    await callback.message.edit_text(text=LEXICON_RU['admin']['menu']['message'],
                                     reply_markup=callback_map_admin['menu'])


@router.callback_query(StateFilter(Admin.survey_edit_pick_survey))
async def create_task_pick_theme(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    survey = await get_survey_by_id(session, int(callback.data))
    await state.set_data({"survey_id": survey.survey_id})
    total_question = len(survey.questions)
    question = survey.questions[0]
    text = f"Вопрос: {question.text}\n"
    for i, ans in enumerate(question.options):
        text += f"Ответ №{i + 1}: {ans.text}\n"
    await callback.message.edit_text(text=text, reply_markup=keyboard_survey_pagination(1, total_question, question))


@router.message(StateFilter(Admin.survey_theme), F.content_type == ContentType.TEXT)
async def create_poll_add_name(message: Message, state: FSMContext, bot: Bot, session: AsyncSession):
    data = await state.get_data()
    msg = data.get('msg')
    if await theme_exists_survey(session, message.text):
        await bot.edit_message_text(chat_id=message.from_user.id, message_id=msg,
                                    text='Тема уже существует. Введите другую тему')
        await message.delete()
        return
    await state.set_state(Admin.survey_name)
    id = await add_theme(session, message.text)
    await state.set_data({"theme": int(id), "msg": msg})
    await bot.edit_message_text(chat_id=message.from_user.id, message_id=msg,
                                text='Введите название опроса (не длиннее 64 символов)')
    await message.delete()


@router.message(StateFilter(Admin.survey_name), F.content_type == ContentType.TEXT, F.text.len() < 64)
async def create_task_add_description(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    theme = data.get('theme', 0)
    msg = data.get('msg')
    await state.set_state(Admin.survey_score)
    await state.set_data({"name": message.text, "theme": theme, "msg": msg, "type": "task"})
    await bot.edit_message_text(chat_id=message.from_user.id, message_id=msg, text='Введите количество баллов за опрос')
    await message.delete()




@router.message(StateFilter(Admin.survey_score), F.text.isdigit())
async def create_survey_add_score(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    theme = data.get('theme', 0)
    name: str = data.get('name', '')
    msg = data.get('msg')
    type = data.get('type')
    await state.set_state(Admin.survey_questions)
    await state.set_data({
        "name": name,
        "theme": theme,
        "score": int(message.text),
        "msg": msg,
        "type": type,
        "questions": [],
        "current_question": None,
        "current_options": []
    })
    await message.delete()
    await bot.edit_message_text(chat_id=message.from_user.id, message_id=msg, text='Введите вопрос',
                                reply_markup=callback_map_admin['Admin:survey_questions'])

@router.message(StateFilter(Admin.survey_questions), F.content_type == ContentType.TEXT)
async def create_question(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    print(data)
    msg = data.get('msg')
    await state.set_state(Admin.survey_options)
    if data['current_question']:
        data['questions'].append({'text': data['current_question'], 'options': data['current_options']})
        data['current_options'] = []
    data['current_question'] = message.text
    await state.set_data(data)
    await bot.edit_message_text(chat_id=message.from_user.id, message_id=msg,
                                text="Введите текст варианта ответа или нажмите кнопку завершить, чтобы закончить "
                                     "вопрос",
                                reply_markup=callback_map_admin['Admin:survey_options'])
    await message.delete()



@router.callback_query(StateFilter(Admin.survey_questions), F.data == 'end_questions')
async def questions_text(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    if not data['current_options']:
        await callback.message.edit_text(text="Опрос должен иметь хотя бы один вопрос. Введите текст вопроса:",
                                         reply_markup=callback_map_admin['Admin:survey_questions'])
    else:
        if data['current_question']:
            data['questions'].append({'text': data['current_question'], 'options': data['current_options']})
            data['current_options'] = []
        await add_survey(session, data)
        await callback.message.edit_text(text=LEXICON_RU['admin']['menu']['message'],
                                         reply_markup=callback_map_admin['menu'])
        await callback.answer(text='Опрос успешно создан')
        await state.set_state(Admin.join)


@router.message(StateFilter(Admin.survey_options), F.content_type == ContentType.TEXT)
async def options_text(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    print(data)
    msg = data.get('msg')
    if not data['current_options']:
        await bot.edit_message_text(chat_id=message.from_user.id, message_id=msg,
                                    text="Введите текст следующего варианта ответа или нажмите кнопку завершить, "
                                         "чтобы закончить вопрос",
                                    reply_markup=callback_map_admin['Admin:survey_options'])
    data['current_options'].append(message.text)
    await state.set_data(data)
    await message.delete()


@router.callback_query(StateFilter(Admin.survey_options), F.data == 'end_options')
async def end_options(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    print(data)
    if not data['current_options']:
        await callback.message.edit_text(
            text="Вопрос должен иметь хотя бы один вариант ответа. Введите текст варианта ответа:",
            reply_markup=callback_map_admin['Admin:survey_options'])
    else:
        await callback.message.edit_text(
            text="Введите текст следующего вопроса нажмите кнопку завершить, чтобы закончить опрос:",
            reply_markup=callback_map_admin['Admin:survey_questions'])
        await state.set_state(Admin.survey_questions)
        await state.set_data(data)
