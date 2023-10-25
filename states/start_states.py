from aiogram.fsm.state import State, StatesGroup


class Start(StatesGroup):
    registration = State()
    registration_b2b = State()
    registration_b2c = State()


register_state = {
    'business': Start.registration_b2b,
    'person': Start.registration_b2c
}


class Quiz(StatesGroup):
    activate = State()
    result = State()
    gift = State()
