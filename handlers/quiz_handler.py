from aiogram import F
from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import InputMediaPhoto
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.inline_keyboards import menu_keyboard, answer_quiz_keyboard, gift_quiz_keyboard, \
    quiz_get_results_keyboard, create_keyboard_options, callback_map
from lexicon.lexicon_ru import LEXICON_RU
from res.photo import PHOTO
from services.database import get_survey_by_id, get_user_by_tg_id, add_survey_complete, add_score_user
from states.start_states import Quiz
# from utils.quiz_utils import calculate_yes_percent

router = Router()


@router.callback_query(StateFilter(Quiz.activate))
async def quiz_check(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    survey_id = data.get('survey_id')
    survey = await get_survey_by_id(session, survey_id)
    option_id = int(callback.data)
    data['answers'].append([survey.questions[data['idx']].question_id, option_id])
    data['idx'] += 1
    if data['idx'] >= len(survey.questions):
        await add_survey_complete(session, callback.from_user.id, survey.survey_id, data['answers'])
        await add_score_user(session, callback.from_user.id, survey.score)
        await state.set_state(Quiz.result)
        await callback.message.edit_caption(caption=LEXICON_RU['quiz_get_result'], reply_markup=quiz_get_results_keyboard)
        return
    question = survey.questions[data['idx']]
    keyboard = create_keyboard_options(question.options)
    await state.set_data(data)
    await callback.message.edit_caption(caption=question.text, reply_markup=keyboard)


@router.callback_query(StateFilter(Quiz.result), F.data == 'get_result')
async def return_quiz_result(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    status = data.get('status', '')
    user = await get_user_by_tg_id(session, callback.from_user.id)
    await state.set_state(Quiz.gift)
    await callback.message.edit_caption(caption=LEXICON_RU['person']['quiz_gift'], reply_markup=gift_quiz_keyboard)


@router.callback_query(StateFilter(Quiz.gift), F.data == 'gift')
async def send_gift(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    user = await get_user_by_tg_id(session, callback.from_user.id)
    await add_score_user(session, callback.from_user.id, 10)
    await callback.message.edit_media(media=InputMediaPhoto(media=PHOTO['menu_b2c'], caption=f'Вы получили баллы! Ваш баланс: {user.score}\n\n' + LEXICON_RU['menu_message']), reply_markup=menu_keyboard['person'])
    await state.clear()