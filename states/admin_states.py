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
