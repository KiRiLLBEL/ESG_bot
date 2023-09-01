from aiogram import F
from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.inline_keyboards import menu_keyboard, answer_quiz_keyboard, gift_quiz_keyboard
from keyboards.reply_keyboards import remove_keyboard, quiz_get_results_keyboard
from lexicon.lexicon_ru import LEXICON_RU
from services.database import add_answer, get_all_no_quiz_answers, add_score_user
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
        await callback.message.edit_text(
            text=LEXICON_RU[status]['quiz_questions'][next_index],
            reply_markup=answer_quiz_keyboard
        )
    else:
        await state.set_state(Quiz.result)
        await state.set_data({'status': status})
        await callback.message.answer(LEXICON_RU['quiz_get_result'], reply_markup=quiz_get_results_keyboard)
        await callback.message.delete()


@router.message(StateFilter(Quiz.result), F.text == LEXICON_RU['quiz_get_result_button'])
async def return_quiz_result(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    status = data.get('status', '')
    yes_percent = await calculate_yes_percent(session, message.from_user.id, status)
    await message.answer(text=LEXICON_RU[status]['quiz_result'].format(yes_percent), reply_markup=remove_keyboard)
    results = await get_all_no_quiz_answers(session, message.from_user.id)
    if not results:
        await message.answer(text=LEXICON_RU[status]['quiz_success'])
    else:
        advice: str = "Советы:\n"
        cnt: int = 1
        for result in results:
            advice += str(cnt) + '. ' + LEXICON_RU[status]['quiz_advices'][result.question_index] + '\n'
            cnt += 1
        await message.answer(text=advice)
    if status == 'b2c':
        await state.set_state(Quiz.gift)
        await message.answer(text=LEXICON_RU['b2c']['quiz_gift'], reply_markup=gift_quiz_keyboard)
    else:
        await state.clear()
        await message.answer(text=LEXICON_RU['menu_message'], reply_markup=menu_keyboard['b2b'])


@router.callback_query(StateFilter(Quiz.gift), F.data == 'gift')
async def send_gift(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.message.answer_photo(photo=FSInputFile("res/bonus.png"), caption="Вы получили баллы!")
    await callback.message.answer(text=LEXICON_RU['menu_message'], reply_markup=menu_keyboard['b2c'])
    await add_score_user(session, callback.from_user.id, 5)
    await callback.message.delete()
    await state.clear()
