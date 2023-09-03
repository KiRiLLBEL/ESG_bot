from aiogram import F
from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import InputMediaPhoto
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.inline_keyboards import menu_keyboard, answer_quiz_keyboard, gift_quiz_keyboard, \
    quiz_get_results_keyboard
from lexicon.lexicon_ru import LEXICON_RU
from res.photo import PHOTO
from services.database import add_answer, get_all_no_quiz_answers, add_score_user, get_user_by_tg_id, user_quiz_solved
from states.start_states import Quiz
from utils.quiz_utils import calculate_yes_percent

router = Router()


@router.callback_query(StateFilter(Quiz.activate))
async def quiz_check(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    answer = callback.data if callback.data is not None else ""
    data = await state.get_data()
    current_index = data.get('index', 0)
    status = data.get('status', '')
    await add_answer(
        session=session,
        user_id=callback.from_user.id,
        question_index=current_index,
        status=status,
        answer=(bool(int(answer)))
    )
    if current_index + 1 < len(LEXICON_RU[status]['quiz_questions']):
        next_index = current_index + 1
        await state.update_data(status=status, index=next_index)
        await callback.message.edit_caption(
            caption=LEXICON_RU[status]['quiz_questions'][next_index],
            reply_markup=answer_quiz_keyboard
        )
    else:
        await state.set_state(Quiz.result)
        await state.set_data({'status': status})
        await callback.message.edit_caption(caption=LEXICON_RU['quiz_get_result'], reply_markup=quiz_get_results_keyboard)


@router.callback_query(StateFilter(Quiz.result), F.data == 'get_result')
async def return_quiz_result(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    status = data.get('status', '')
    yes_percent = await calculate_yes_percent(session, callback.from_user.id, status)
    text = LEXICON_RU[status]['quiz_result'].format(yes_percent) + '\n'
    results = await get_all_no_quiz_answers(session, callback.from_user.id)
    if not results:
        text += LEXICON_RU[status]['quiz_success'] + '\n'
    else:
        advice: str = "Советы:\n"
        cnt: int = 1
        for result in results:
            advice += str(cnt) + '. ' + LEXICON_RU[status]['quiz_advices'][result.question_index] + '\n'
            cnt += 1
        text += advice + '\n'
    user = await get_user_by_tg_id(session, callback.from_user.id)
    if status == 'b2c' and not user.quiz:
        await state.set_state(Quiz.gift)
        await callback.message.edit_caption(caption=text + LEXICON_RU['b2c']['quiz_gift'], reply_markup=gift_quiz_keyboard)
    else:
        await state.clear()
        await callback.message.edit_caption(caption=LEXICON_RU['menu_message'], reply_markup=menu_keyboard['b2b'])


@router.callback_query(StateFilter(Quiz.gift), F.data == 'gift')
async def send_gift(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    user = await get_user_by_tg_id(session, callback.from_user.id)
    await add_score_user(session, callback.from_user.id, 5)
    await user_quiz_solved(session, callback.from_user.id)
    await callback.message.edit_media(media=InputMediaPhoto(media=PHOTO['bonus'], caption=f'Вы получили баллы! Ваш баланс: {user.score}\n\n' + LEXICON_RU['menu_message']), reply_markup=menu_keyboard['b2c'])
    await state.clear()