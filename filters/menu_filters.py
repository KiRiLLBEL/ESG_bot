from aiogram.filters.callback_data import CallbackData


class MenuCallbackFactory(CallbackData, prefix='menu'):
    current_keyboard: str
    next_keyboard: str
