from aiogram import F
from aiogram import Router
from aiogram.enums import ContentType
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from filters.menu_filters import AdminMenuCallbackFactory
from keyboards.inline_keyboards import callback_map_admin
from lexicon.lexicon_ru import LEXICON_RU
from services.database import get_all_themes, theme_exists, add_task, get_tasks_by_theme, get_tasks_uid_by_name, \
    delete_tasks, theme_exists_pool, add_survey, get_all_themes_all_table, add_product
from states.admin_states import Admin
from utils.quiz_utils import generate_random_uid

router = Router()


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


@router.callback_query(StateFilter(Admin.join), AdminMenuCallbackFactory.filter(F.next_keyboard == 'create_product'))
async def create_task_themes(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Admin.product_name)
    await state.set_data({'msg': callback.message})
    await callback.message.edit_text(text='Введите название товара (не длиннее 64 символов)')


@router.message(StateFilter(Admin.product_name), F.content_type == ContentType.TEXT,  F.text.len() < 64)
async def add_name_product(message: Message, state: FSMContext):
    data = await state.get_data()
    msg: Message = data.get('msg')
    await state.set_state(Admin.product_score)
    msg = await msg.edit_text(text='Введите стоимость продукта')
    await state.set_data({"name": message.text, "msg": msg})
    await message.delete()


@router.message(StateFilter(Admin.product_name))
async def error_message(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data.get('msg')
    if msg.text != 'Вы должны ввести текст\n\nВведите название товара (не длиннее 64 символов)':
        msg = await msg.edit_text(text='Вы должны ввести текст\n\nВведите название товара (не длиннее 64 символов)')
    data['msg'] = msg
    await state.set_data(data)
    await message.delete()


@router.message(StateFilter(Admin.product_score), F.text.isdigit())
async def add_name_product(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data.get('msg')
    await state.set_state(Admin.product_image)
    msg = await msg.edit_text(text='Введите ссылку на изображение товара')
    await state.set_data({"name": data['name'], "msg": msg, 'price': int(message.text)})
    await message.delete()


@router.message(StateFilter(Admin.product_score))
async def create_task_add_final_error(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data.get('msg')
    if msg.text != 'Введите число':
        msg = await msg.edit_text(text='Введите число')
    data['msg'] = msg
    await state.set_data(data)
    await message.delete()


@router.message(StateFilter(Admin.product_image), F.content_type == ContentType.TEXT)
async def add_name_product(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    msg = data.get('msg')
    await add_product(session, data['name'], data['price'], message.text)
    await msg.edit_text(text='Товар успешно создан', reply_markup=callback_map_admin['menu'])
    await state.set_state(Admin.join)
    await message.delete()


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


@router.callback_query(StateFilter(Admin.task_theme_delete))
async def get_task_for_delete(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    tasks = await get_tasks_by_theme(session, callback.data)
    if not tasks:
        await callback.answer(text='Нет созданных заданий')
        return
    await state.set_state(Admin.task_tasks_delete)
    await callback.message.edit_reply_markup(reply_markup=callback_map_admin['delete_task'](tasks))


@router.callback_query(StateFilter(Admin.task_tasks_delete))
async def delete_task(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    uid = await get_tasks_uid_by_name(session, callback.data)
    await delete_tasks(session, uid, callback.data)
    await state.set_state(Admin.join)
    await callback.message.edit_text(text=LEXICON_RU['menu_message'], reply_markup=callback_map_admin['menu'])


@router.callback_query(StateFilter(Admin.task_get))
async def get_task_names(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    tasks = await get_tasks_by_theme(session, callback.data)
    if not tasks:
        await callback.answer(text='Нет созданных заданий')
        return
    await state.set_state(Admin.task_tasks)
    await callback.message.edit_reply_markup(reply_markup=callback_map_admin['get_task'](tasks))


@router.callback_query(StateFilter(Admin.task_tasks))
async def get_task_uid(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    uid = await get_tasks_uid_by_name(session, callback.data)
    await callback.message.answer(text=f"Ключ этой задачи - {uid}")
    await state.set_state(Admin.join)
    await callback.message.answer(text=LEXICON_RU['menu_message'], reply_markup=callback_map_admin['menu'])
    await callback.message.delete()


@router.callback_query(StateFilter(Admin.task_theme), F.data == 'create_theme')
async def create_task_add_theme(callback: CallbackQuery, state: FSMContext):
    msg = await callback.message.answer(text="Введите тему")
    await state.set_data({"theme": callback.data, "msg": msg})
    await callback.message.delete()


@router.callback_query(StateFilter(Admin.pool_theme), F.data == 'create_theme')
async def create_task_add_theme(callback: CallbackQuery, state: FSMContext):
    msg = await callback.message.answer(text="Введите тему")
    await state.set_data({"theme": callback.data, "msg": msg})
    await callback.message.delete()


@router.callback_query(StateFilter(Admin.task_theme))
async def create_task_pick_theme(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Admin.task_name)
    msg = await callback.message.answer(text='Введите имя задачи')
    await state.set_data({"theme": callback.data, "msg": msg})
    await callback.message.delete()


@router.callback_query(StateFilter(Admin.pool_theme))
async def create_task_pick_theme(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Admin.pool_name)
    msg = await callback.message.answer(text='Введите название опроса')
    await state.set_data({"theme": callback.data, "msg": msg})
    await callback.message.delete()


@router.message(StateFilter(Admin.pool_theme), F.content_type == ContentType.TEXT)
async def create_poll_add_name(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    msg = data.get('msg')
    if await theme_exists_pool(session, message.text):
        await msg.edit_text(text='Тема уже существует. Введите другую тему')
        await message.delete()
        return
    await state.set_state(Admin.pool_name)
    await state.set_data({"theme": message.text, "msg": msg})
    await msg.edit_text(text='Введите название опроса (не длиннее 64 символов)')
    await message.delete()


@router.message(StateFilter(Admin.task_theme), F.content_type == ContentType.TEXT)
async def create_task_add_name(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    msg = data.get('msg')
    if await theme_exists(session, message.text):
        await msg.edit_text(text='Тема уже существует. Введите другую тему')
        await message.delete()
        return
    await state.set_state(Admin.task_name)
    await state.set_data({"theme": message.text, "msg": msg})
    await msg.edit_text(text='Введите название задачи (не длиннее 64 символов)')
    await message.delete()


@router.message(StateFilter(Admin.pool_name), F.content_type == ContentType.TEXT,  F.text.len() < 64)
async def create_task_add_description(message: Message, state: FSMContext):
    data = await state.get_data()
    theme: str = data.get('theme', '')
    msg = data.get('msg')
    await state.set_state(Admin.pool_score)
    await state.set_data({"name": message.text, "theme": theme, "msg": msg})
    await msg.edit_text(text='Введите количество баллов за опрос')
    await message.delete()


@router.message(StateFilter(Admin.pool_name))
async def error_message(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data.get('msg')
    if msg.text != 'Вы должны ввести текст\n\nВведите название опроса (не длиннее 64 символов)':
        await msg.edit_text(text='Вы должны ввести текст\n\nВведите название опроса (не длиннее 64 символов)')
    await message.delete()


@router.message(StateFilter(Admin.pool_score), F.text.isdigit())
async def create_pool_add_score(message: Message, state: FSMContext):
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
    await msg.edit_text(text='Введите вопрос', reply_markup=callback_map_admin['poll_question'])


@router.message(StateFilter(Admin.pool_score))
async def create_task_add_final_error(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data.get('msg')
    if msg.text != 'Введите число':
        await msg.edit_text(text='Введите число')
    await message.delete()


@router.message(StateFilter(Admin.pool_questions), F.content_type == ContentType.TEXT)
async def create_question(message: Message, state: FSMContext):
    data = await state.get_data()
    print(data)
    msg = data.get('msg')
    await state.set_state(Admin.pool_options)
    if data['current_question']:
        data['questions'].append({'text': data['current_question'], 'options': data['current_options']})
        data['current_options'] = []
    data['current_question'] = message.text
    await state.set_data(data)
    await msg.edit_text(text="Введите текст варианта ответа или нажмите кнопку завершить, чтобы закончить вопрос",
                        reply_markup=callback_map_admin['poll_option'])
    await message.delete()


@router.message(StateFilter(Admin.pool_questions))
async def error_message(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data.get('msg')
    if msg.text != 'Вы должны ввести текст\n\nВведите вопрос':
        await msg.edit_text(text='Вы должны ввести текст\n\nВведите вопрос')
    await message.delete()


@router.callback_query(StateFilter(Admin.pool_questions), F.data == 'end_questions')
async def questions_text(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    print(data)
    msg = data.get('msg')
    if not data['current_options']:
        await msg.edit_text("Опрос должен иметь хотя бы один вопрос. Введите текст вопроса:",
                            reply_markup=callback_map_admin['poll_question'])
    else:
        if data['current_question']:
            data['questions'].append({'text': data['current_question'], 'options': data['current_options']})
            data['current_options'] = []
        await add_survey(session, data)
        await msg.edit_text(text=LEXICON_RU['admin']['menu']['message'], reply_markup=callback_map_admin['menu'])
        await callback.answer(text='Опрос успешно создан')
        await state.set_state(Admin.join)


@router.message(StateFilter(Admin.pool_options), F.content_type == ContentType.TEXT)
async def options_text(message: Message, state: FSMContext):
    data = await state.get_data()
    print(data)
    msg = data.get('msg')
    if not data['current_options']:
        await msg.edit_text(
            "Введите текст следующего варианта ответа или нажмите кнопку завершить, чтобы закончить вопрос",
            reply_markup=callback_map_admin['poll_option'])
    data['current_options'].append(message.text)
    await state.set_data(data)
    await message.delete()


@router.message(StateFilter(Admin.pool_options))
async def error_message(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data.get('msg')
    if msg.text != 'Вы должны ввести текст\n\nВведите текст варианта ответа или нажмите кнопку завершить, чтобы закончить вопрос':
        await msg.edit_text(
            text='Вы должны ввести текст\n\nВведите текст варианта ответа или нажмите кнопку завершить, чтобы закончить вопрос')
    await message.delete()


@router.callback_query(StateFilter(Admin.pool_options), F.data == 'end_options')
async def end_options(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    print(data)
    msg = data.get('msg')
    if not data['current_options']:
        await msg.edit_text("Вопрос должен иметь хотя бы один вариант ответа. Введите текст варианта ответа:",
                            reply_markup=callback_map_admin['poll_option'])
    else:
        await msg.edit_text("Введите текст следующего вопроса нажмите кнопку завершить, чтобы закончить опрос:",
                            reply_markup=callback_map_admin['poll_question'])
        await state.set_state(Admin.pool_questions)
        await state.set_data(data)


@router.message(StateFilter(Admin.task_name), F.content_type == ContentType.TEXT,  F.text.len() < 64)
async def create_task_add_description(message: Message, state: FSMContext):
    data = await state.get_data()
    theme: str = data.get('theme', '')
    msg = data.get('msg')
    await state.set_state(Admin.task_description)
    await state.set_data({"name": message.text, "theme": theme, "msg": msg})
    await message.delete()
    await msg.edit_text(text='Введите описание задачи')


@router.message(StateFilter(Admin.task_name))
async def error_message(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data.get('msg')
    if msg.text != 'Вы должны ввести текст\n\nВведите название задачи (не длиннее 64 символов)':
        await msg.edit_text(text='Вы должны ввести текст\n\nВведите название задачи (не длиннее 64 символов)')
    await message.delete()


@router.message(StateFilter(Admin.task_description), F.content_type == ContentType.TEXT)
async def create_task_add_score(message: Message, state: FSMContext):
    data = await state.get_data()
    theme: str = data.get('theme', '')
    name: str = data.get('name', '')
    msg = data.get('msg')
    await state.set_state(Admin.task_score)
    await state.set_data({"name": name, "theme": theme, "description": message.text, "msg": msg})
    await msg.edit_text(text='Введите количество баллов за выполнение задачи')
    await message.delete()


@router.message(StateFilter(Admin.task_description))
async def error_message(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data.get('msg')
    if msg.text != 'Вы должны ввести текст\n\nВведите описание задачи':
        await msg.edit_text(text='Вы должны ввести текст\n\nВведите описание задачи')
    await message.delete()


@router.message(StateFilter(Admin.task_score), F.text.isdigit())
async def create_task_add_final(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    theme: str = data.get('theme', '')
    name: str = data.get('name', '')
    description: str = data.get('description', '')
    msg = data.get('msg')
    uid = generate_random_uid()
    await add_task(
        session=session,
        uid=uid,
        name=name,
        description=description,
        theme=theme,
        value=int(message.text)
    )
    await state.set_state(Admin.join)
    await msg.edit_text(text=f'Задача успешно создана. UID = {uid}', reply_markup=callback_map_admin['menu'])
    await message.delete()


@router.message(StateFilter(Admin.task_score))
async def create_task_add_final_error(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data.get('msg')
    if msg.text != 'Введите число':
        await msg.edit_text(text='Введите число')
    await message.delete()
