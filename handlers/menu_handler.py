from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InputMediaPhoto
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from filters.menu_filters import MenuCallbackFactory
from keyboards.inline_keyboards import callback_map, create_keyboard_options, create_pagination_keyboard
from lexicon.lexicon_ru import LEXICON_RU
from models.product import Product
from res.photo import PHOTO
from services.database import add_score_user, get_user_by_tg_id, get_survey_by_id, get_user_survey, \
    get_unattempted_themes, get_products_as_pages, get_user_score, get_product_by_id, decrease_score, \
    get_favorite_surveys_and_tasks, get_completed_surveys_and_tasks, get_task_by_id, get_tasks_and_surveys, \
    add_survey_complete, add_user_survey, get_user_task, add_user_task, update_user_task, get_events, get_user_event, \
    add_user_event, get_favorite_event
from states.menu_states import Tasks

router = Router()


@router.callback_query(MenuCallbackFactory.filter(F.next_keyboard == 'none'))
@router.callback_query(F.data == 'none')
async def later(callback: CallbackQuery):
    await callback.answer(text="Данный раздел появиться позже")


@router.callback_query(MenuCallbackFactory.filter(F.next_keyboard == 'themes_earn'))
async def get_themes_for_earn(callback: CallbackQuery, callback_data: MenuCallbackFactory, state: FSMContext,
                              session: AsyncSession):
    themes = await get_unattempted_themes(session, callback.from_user.id)
    if not themes:
        await callback.answer(text='Нет доступных тем')
        return
    await state.set_state(Tasks.get)
    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=PHOTO['my_score'],
            caption=LEXICON_RU['themes_earn']['message']
        ),
        reply_markup=callback_map[callback_data.next_keyboard](themes)
    )

@router.callback_query(MenuCallbackFactory.filter(F.next_keyboard == 'poster'))
async def get_events_pag(callback: CallbackQuery, callback_data: MenuCallbackFactory, state: FSMContext,
                              session: AsyncSession):
    events = await get_events(session)
    if events == []:
        await callback.answer('Нет доступных мероприятий')
        return
    event = events[0]
    await state.set_data({'event_id': event.event_id})
    total_events = len(events)
    text = f"Название: {event.title}\nТемы: {event.theme.title}\nОписание: {event.description}\nРасположение: {event.place}\nВместимость: {event.capacity}\nДата проведения: {event.date}\nОрганизатор: {event.organizer}\nБаллы за посещение: {event.value}"
    await callback.message.answer_photo(
        photo=event.image_url,
        caption=text,
        reply_markup=callback_map['poster'](1, total_events, event)
    )


@router.callback_query(F.data == 'current_page_ev')
async def try_solve(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer("Вы можете добавить мероприятие в избранное")
@router.callback_query(F.data == 'favorites_event')
async def try_solve(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    event_id = data.get('event_id')
    user_event = await get_user_event(session, callback.from_user.id, event_id)
    if user_event is None:
        await add_user_event(session, callback.from_user.id, event_id, 'favorite')
    await callback.answer(text="Мероприятие добавлено в избранное")
@router.callback_query(MenuCallbackFactory.filter(F.next_keyboard == 'merch'))
async def get_products(callback: CallbackQuery, callback_data: MenuCallbackFactory, state: FSMContext,
                              session: AsyncSession):
    product = await get_products_as_pages(session, 0, 1)
    if product == []:
        await callback.answer('Нет доступных товаров')
        return
    product = product[0]
    total_products = await session.scalar(select(func.count(Product.product_id)))
    total_pages = (total_products + 1 - 1)
    text = f"Название: {product.title}\nЦена: {product.price}\n\nВаш баланс: {await get_user_score(session, callback.from_user.id)}"
    await callback.message.answer_photo(
        photo=product.image_url,
        caption=text,
        reply_markup=create_pagination_keyboard(1, total_pages, product)
    )
    await callback.message.delete()

@router.callback_query(F.data.startswith('evpage:'))
async def handle_page_callback(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    current_page = int(callback.data.split(':')[1])
    events = await get_events(session)
    event = events[current_page - 1]
    await state.set_data({'event_id': event.event_id})
    total_events = len(events)
    text = f"Название: {event.title}\nТемы: {event.theme.title}\nОписание: {event.description}\nРасположение: {event.place}\nВместимость: {event.capacity}\nДата проведения: {event.date}\nОрганизатор: {event.organizer}\nБаллы за посещение: {event.value}"
    await callback.message.answer_photo(
        photo=event.image_url,
        caption=text,
        reply_markup=callback_map['poster'](current_page, total_events, event)
    )
    await callback.message.delete()

@router.callback_query(F.data.startswith('page:'))
async def handle_page_callback(callback: CallbackQuery, session: AsyncSession):
    current_page = int(callback.data.split(':')[1])
    offset = (current_page - 1) * 1

    product = await get_products_as_pages(session, offset, 1)
    product = product[0]
    total_products = await session.scalar(select(func.count(Product.product_id)))
    total_pages = (total_products + 1 - 1)
    pagination_keyboard = create_pagination_keyboard(current_page, total_pages, product)
    text = f"Название: {product.title}\nЦена: {product.price}\n\nВаш баланс: {await get_user_score(session, callback.from_user.id)}"
    await callback.message.edit_media(media=InputMediaPhoto(
        media=product.image_url,
        caption=text),
        reply_markup=pagination_keyboard
    )

    if current_page > total_pages:
        await callback.answer(text='Товары закончились')
        await callback.message.delete()

@router.callback_query(F.data.startswith('buy:'))
async def handle_buy_callback(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    product_id = int(callback.data.split(':')[1])
    product: Product = await get_product_by_id(session, product_id)
    user = await get_user_by_tg_id(session, callback.from_user.id)
    if user.score - product.price >= 0:
        await decrease_score(session, callback.from_user.id, product.price)
        await callback.answer(text=f'Товар успешно приобретен! Ваш баланс: {await get_user_score(session, callback.from_user.id)}')
        text = f'Пользователь {callback.from_user.username} купил товар {product.title}'
        await bot.send_message(5482433377, text)
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=PHOTO['buy_score'],
                caption=LEXICON_RU['buy_score']['message'].format(await get_user_score(session, callback.from_user.id))
            ),
            reply_markup=callback_map['buy_score']
        )
    else:
        await callback.answer(text=f'Недостаточно средств: Ваш баланс: {await get_user_score(session, callback.from_user.id)}')

@router.callback_query(MenuCallbackFactory.filter(F.next_keyboard == 'get_favorites'))
async def get_themes_for_earn(callback: CallbackQuery, callback_data: MenuCallbackFactory, state: FSMContext,
                              session: AsyncSession):
    tasks = await get_favorite_surveys_and_tasks(session, callback.from_user.id)
    if not tasks:
        await callback.answer(text='Нет доступных заданий')
        return
    await state.set_state(Tasks.tasks)
    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=PHOTO['favorite'],
            caption='Список избранных заданий и опросов'
        ),
        reply_markup=callback_map['tasks'](tasks)
    )

@router.callback_query(MenuCallbackFactory.filter(F.next_keyboard == 'get_favorite_events'))
async def get_themes_for_earn(callback: CallbackQuery, callback_data: MenuCallbackFactory, state: FSMContext,
                              session: AsyncSession):
    events = await get_favorite_event(session, callback.from_user.id)
    if events == []:
        await callback.answer('Нет избранных мероприятий')
        return
    event = events[0]
    await state.set_data({'event_id': event.event_id})
    total_events = len(events)
    text = f"Название: {event.title}\nТемы: {event.theme.title}\nОписание: {event.description}\nРасположение: {event.place}\nВместимость: {event.capacity}\nДата проведения: {event.date}\nОрганизатор: {event.organizer}\nБаллы за посещение: {event.value}"
    await callback.message.answer_photo(
        photo=event.image_url,
        caption=text,
        reply_markup=callback_map['get_favorite_events'](1, total_events, event)
    )
    await callback.message.delete()

@router.callback_query(F.data.startswith('evfpage:'))
async def handle_page_callback(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    current_page = int(callback.data.split(':')[1])
    events = await get_favorite_event(session, callback.from_user.id)
    event = events[current_page - 1]
    await state.set_data({'event_id': event.event_id})
    total_events = len(events)
    text = f"Название: {event.title}\nТемы: {event.theme.title}\nОписание: {event.description}\nРасположение: {event.place}\nВместимость: {event.capacity}\nДата проведения: {event.date}\nОрганизатор: {event.organizer}\nБаллы за посещение: {event.value}"
    await callback.message.answer_photo(
        photo=event.image_url,
        caption=text,
        reply_markup=callback_map['get_favorite_events'](current_page, total_events, event)
    )
    await callback.message.delete()

@router.callback_query(MenuCallbackFactory.filter(F.next_keyboard == 'get_completed'))
async def get_themes_for_earn(callback: CallbackQuery, callback_data: MenuCallbackFactory, state: FSMContext,
                              session: AsyncSession):
    tasks = await get_completed_surveys_and_tasks(session, callback.from_user.id)
    if not tasks:
        await callback.answer(text='Нет выполненных заданий')
        return
    resume: str = ''
    for obj in tasks:
        if obj[1] == 'task':
            task = await get_task_by_id(session, int(obj[0]))
            resume += (
                    "Название: " + task.title +
                    "\nТип: Задание" +
                    '\nОписание: ' + task.description +
                    "\nТема: " + task.theme.title +
                    "\nБаллы за решение: " + str(task.value) +
                    f'\nДата выполнения: {(await get_user_task(session=session,user_id=callback.from_user.id, task_id=task.task_id)).date}\n\n'
            )
        else:
            survey = await get_survey_by_id(session, int(obj[0]))
            resume += (
                    "Название: " + survey.title +
                    "\nТип: Опрос" +
                    "\nТема: " + survey.theme.title +
                    "\nБаллы за прохождение: " + str(survey.score) +
                    f'\nДата выполнения: {(await get_user_survey(session=session, user_id=callback.from_user.id, survey_id=survey.survey_id)).date}\n\n'
            )
    try:
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=PHOTO['my_score'],
                caption=resume
            ),
            reply_markup=callback_map[callback_data.current_keyboard]
        )
    except TelegramBadRequest:
        await callback.answer("Это ваши выполненные задания")


@router.callback_query(MenuCallbackFactory.filter(F.next_keyboard.in_(['my_score', 'earn_score', 'buy_score', 'pick_tasks'])))
async def get_themes_for_earn(callback: CallbackQuery, callback_data: MenuCallbackFactory, session: AsyncSession):

    await callback.message.answer_photo(
            photo=PHOTO[callback_data.next_keyboard],
            caption=LEXICON_RU[callback_data.next_keyboard]['message'].format(
                await get_user_score(session, callback.from_user.id)),
        reply_markup=callback_map[callback_data.next_keyboard]
    )
    await callback.message.delete()


@router.callback_query(MenuCallbackFactory.filter())
async def change_menu_keyboard(callback: CallbackQuery, callback_data: MenuCallbackFactory):
    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=PHOTO[callback_data.next_keyboard],
            caption=LEXICON_RU[callback_data.next_keyboard]['message']
        ),
        reply_markup=callback_map[callback_data.next_keyboard]
    )


@router.callback_query(StateFilter(Tasks.get, Tasks.tasks, Tasks.solve), MenuCallbackFactory.filter())
async def change_menu_keyboard(callback: CallbackQuery, callback_data: MenuCallbackFactory, state: FSMContext):
    await state.clear()
    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=PHOTO[callback_data.next_keyboard],
            caption=LEXICON_RU[callback_data.next_keyboard]['message']
        ),
        reply_markup=callback_map[callback_data.next_keyboard]
    )


@router.callback_query(StateFilter(Tasks.get))
async def get_task_names_for_earn(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    tasks = await get_tasks_and_surveys(session, callback.from_user.id, int(callback.data))
    await state.set_state(Tasks.tasks)
    await callback.message.answer(text='Список доступных заданий', reply_markup=callback_map['tasks'](tasks))
    await callback.message.delete()


@router.callback_query(StateFilter(Tasks.tasks), F.data.startswith('task_'))
async def select_task_to_solve(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    task_id = int(callback.data.split('_')[1])
    task = await get_task_by_id(session, task_id)
    resume = (
            "Название: " + task.title +
            '\nОписание: ' + task.description +
            "\nТема: " + task.theme.title +
            "\nБаллы за решение: " + str(task.value)
    )
    await callback.message.edit_text(text=resume, reply_markup=callback_map['task'])
    await state.set_state(Tasks.solve)
    await state.set_data({'name': task.task_id, 'score': task.value, 'msg': callback.message.message_id})


@router.callback_query(StateFilter(Tasks.tasks), F.data.startswith('survey_'))
async def select_task_to_solve(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    survey_id = int(callback.data.split('_')[1])
    survey = await get_survey_by_id(session, survey_id)
    resume = (
            "Название: " + survey.title +
            "\nТема: " + survey.theme.title +
            "\nБаллы за прохождение: " + str(survey.score)
    )
    await state.set_state(Tasks.survey_pick)
    await callback.message.answer(text=resume, reply_markup=callback_map['task'])
    await callback.message.delete()
    await state.set_data({'survey_id': survey.survey_id})


@router.callback_query(StateFilter(Tasks.survey_pick), F.data == 'solve')
async def try_solve(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    survey_id = data.get('survey_id')
    survey = await get_survey_by_id(session, survey_id)
    questions = survey.questions
    question = questions[0]
    options = question.options
    await state.set_state(Tasks.survey_solve)
    await state.set_data({
        'survey_id': survey_id,
        'answers': [],
        'idx': 0
    })
    await callback.message.edit_text(text=question.text, reply_markup=create_keyboard_options(options))


@router.callback_query(StateFilter(Tasks.survey_pick), F.data == 'favorites')
async def try_solve(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    survey_id = data.get('survey_id')
    survey_result = await get_user_survey(session, callback.from_user.id, survey_id)
    if survey_result is None:
        await add_user_survey(session, callback.from_user.id, survey_id, 'favorite')
    await callback.answer(text="Опрос добавлен в избранное")


@router.callback_query(StateFilter(Tasks.survey_solve))
async def solving(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    survey_id = data.get('survey_id')
    survey = await get_survey_by_id(session, survey_id)
    option_id = int(callback.data)
    data['idx'] += 1
    data['answers'].append([data['idx'], option_id])
    if data['idx'] >= len(survey.questions):
        await add_survey_complete(session, callback.from_user.id, survey.survey_id, data['answers'])
        await add_score_user(session, callback.from_user.id, survey.score)
        user = await get_user_by_tg_id(session, callback.from_user.id)
        await state.clear()
        await callback.message.edit_text(text=f'Опрос пройден! Ваш баланс {user.score}',
                                         reply_markup=callback_map['menu_b2c'])
    question = survey.questions[data['idx']]
    keyboard = create_keyboard_options(question.options)
    await state.set_data(data)
    await callback.message.edit_text(text=question.text, keyboard=keyboard)


@router.callback_query(StateFilter(Tasks.solve), F.data == 'solve')
async def try_solve(callback: CallbackQuery):
    await callback.message.edit_text(
        text="Чтобы решить данное задание, напишите в чат код",
        reply_markup=callback_map['task']
    )


@router.callback_query(StateFilter(Tasks.solve), F.data == 'favorites')
async def favorite_solve(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    task_id = data.get('name', 0)
    task_status = await get_user_task(session, callback.from_user.id, task_id)
    if task_status is None:
        await add_user_task(
            session=session,
            task_id=task_id,
            user_id=callback.from_user.id,
            status='favorite'
        )
    await callback.answer(text="Задание добавлено в избранное")


@router.message(StateFilter(Tasks.solve), F.text.isdigit())
async def select_task_to_solve(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    data = await state.get_data()
    task_id = data.get('name', 0)
    score = data.get('score', 0)
    msg = data.get('msg')
    if int(message.text) == task_id:
        await state.clear()
        await add_score_user(session, message.from_user.id, score)
        user = await get_user_by_tg_id(session, message.from_user.id)
        task_status = await get_user_task(session, message.from_user.id, task_id)
        if task_status is None:
            await add_user_task(
                session=session,
                task_id=task_id,
                user_id=message.from_user.id,
                status='complete'
            )
        else:
            await update_user_task(session, message.from_user.id, task_id, 'complete')

        await bot.send_photo(chat_id=message.from_user.id, photo=PHOTO['menu_b2c'], caption=f'Задание успешно выполнено! Ваш баланс {user.score}',
                               reply_markup=callback_map['menu_b2c'])
    else:
        try:
            await bot.edit_message_text(message_id=msg, chat_id=message.from_user.id, text="К сожалению, ваш ключ не совпадает, попробуйте еще раз",
                                reply_markup=callback_map['task'])
        except TelegramBadRequest:
            pass
    await message.delete()


@router.message(StateFilter(Tasks.solve))
async def select_task_to_solve(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    msg = data.get('msg')
    await bot.edit_message_text(message_id=msg, chat_id=message.from_user.id,text="Пожалуйста, введите ключ", reply_markup=callback_map['task'])
    await message.delete()
