from aiogram.fsm.state import State, StatesGroup


class Admin(StatesGroup):
    pick = State()
    join = State()

    task_theme = State()
    task_name = State()
    task_description = State()
    task_score = State()
    task_get = State()
    task_tasks = State()
    task_theme_delete = State()
    task_tasks_delete = State()

    pool_theme = State()
    pool_name = State()
    pool_questions = State()
    pool_options = State()
    pool_score = State()
    pool_main_pick = State()

    product_name = State()
    product_score = State()
    product_image = State()


callback_error_input = [
    Admin.task_theme,
    Admin.task_name,
    Admin.task_description,
    Admin.task_score,
    Admin.pool_theme,
    Admin.pool_name,
    Admin.pool_score,
    Admin.pool_questions,
    Admin.pool_options,
    Admin.product_score,
    Admin.product_name,
]
