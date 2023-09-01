from aiogram.fsm.state import State, StatesGroup

class Admin(StatesGroup):
    join = State()
    theme = State()
    name = State()
    description = State()
    score = State()
    get = State()
    tasks = State()