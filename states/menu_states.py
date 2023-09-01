from aiogram.fsm.state import State, StatesGroup

class Tasks(StatesGroup):
    get = State()
    tasks = State()
    solve = State()