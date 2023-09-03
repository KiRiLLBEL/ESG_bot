from aiogram.fsm.state import State, StatesGroup

class Tasks(StatesGroup):
    get = State()
    tasks = State()
    solve = State()
    survey_solve = State()
    survey_pick = State()