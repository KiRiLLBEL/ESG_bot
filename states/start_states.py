from aiogram.fsm.state import State, StatesGroup


class Start(StatesGroup):
    registration = State()
    registration_b2b = State()
    registration_b2c = State()


register_state = {
    'b2b': Start.registration_b2b,
    'b2c': Start.registration_b2c
}


class Quiz(StatesGroup):
    activate = State()
    result = State()
    gift = State()
