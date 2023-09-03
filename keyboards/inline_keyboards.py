from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from filters.menu_filters import MenuCallbackFactory, AdminMenuCallbackFactory

from lexicon.lexicon_ru import LEXICON_RU
from services.database import get_question_options
from states.admin_states import Admin


def keyboard_create_task(themes: list[str]):
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    if themes:
        for button in themes:
            buttons.append(InlineKeyboardButton(
                text=button,
                callback_data=button)
            )
    kb_builder.row(*buttons, width=1)
    kb_builder.row(InlineKeyboardButton(
        text=LEXICON_RU['admin']['create_task']['button1'],
        callback_data='create_theme'))
    kb_builder.row(InlineKeyboardButton(
        text=LEXICON_RU['back_button'],
        callback_data=AdminMenuCallbackFactory(
            current_keyboard='create_task',
            next_keyboard="change_task"
        ).pack()
    )
    )
    return kb_builder.as_markup()


def keyboard_create_poll(themes: list[str]):
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    if themes:
        for button in themes:
            buttons.append(InlineKeyboardButton(
                text=button,
                callback_data=button)
            )
    kb_builder.row(*buttons, width=1)
    kb_builder.row(InlineKeyboardButton(
        text=LEXICON_RU['admin']['create_poll']['button1'],
        callback_data='create_theme'))
    kb_builder.row(InlineKeyboardButton(
        text=LEXICON_RU['back_button'],
        callback_data=AdminMenuCallbackFactory(
            current_keyboard='create_poll',
            next_keyboard="change_poll"
        ).pack()
    )
    )
    return kb_builder.as_markup()

def create_keyboard_options(options):
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    for option in options:
        button = InlineKeyboardButton(text=option[0],
                                      callback_data=f'answer_{option[1]}')
        buttons.append(button)
    kb_builder.row(*buttons, width=1)

    return kb_builder.as_markup()


def keyboard_get_task(themes: list[str]):
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    if themes:
        for button in themes:
            buttons.append(InlineKeyboardButton(
                text=button,
                callback_data=button)
            )
    kb_builder.row(*buttons, width=1)
    kb_builder.row(InlineKeyboardButton(
        text=LEXICON_RU['back_button'],
        callback_data=AdminMenuCallbackFactory(
            current_keyboard='get_task',
            next_keyboard="change_task"
        ).pack()
    )
    )
    return kb_builder.as_markup()


def keyboard_delete_task(themes: list[str]):
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    if themes:
        for button in themes:
            buttons.append(InlineKeyboardButton(
                text=button,
                callback_data=button)
            )
    kb_builder.row(*buttons, width=1)
    kb_builder.row(InlineKeyboardButton(
        text=LEXICON_RU['back_button'],
        callback_data=AdminMenuCallbackFactory(
            current_keyboard='delete_task',
            next_keyboard="change_task"
        ).pack()
    )
    )
    return kb_builder.as_markup()


def keyboard_get_themes_earn(themes: list[str]):
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    if themes:
        for button in themes:
            buttons.append(InlineKeyboardButton(
                text=button,
                callback_data=button)
            )
        kb_builder.row(*buttons, width=1)
    kb_builder.row(InlineKeyboardButton(
        text=LEXICON_RU['back_button'],
        callback_data=MenuCallbackFactory(
            current_keyboard='themes_earn',
            next_keyboard="pick_tasks"
        ).pack()
    )
    )
    return kb_builder.as_markup()


def keyboard_tasks_and_themes(obj):
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    if obj:
        for button in obj:
            buttons.append(InlineKeyboardButton(
                text=button[0] + ' (задание)' if button[1] == 'task' else button[0] + ' (опрос)',
                callback_data=button[1] + "_" + button[0]
            )
            )
            print(button[0], button[1])
        kb_builder.row(*buttons, width=1)
    kb_builder.row(InlineKeyboardButton(
            text=LEXICON_RU['back_button'],
            callback_data=MenuCallbackFactory(
                current_keyboard='themes_earn',
                next_keyboard="pick_tasks"
            ).pack()
        )
    )
    return kb_builder.as_markup()

start_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=LEXICON_RU['start_b2c'], callback_data='b2c'),
            InlineKeyboardButton(text=LEXICON_RU['start_b2b'], callback_data='b2b')
        ]
    ]
)

quiz_get_results_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=LEXICON_RU['quiz_get_result_button'], callback_data='get_result')
        ]
    ]
)

menu_keyboard = {
    'b2b': InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=LEXICON_RU['b2b']['menu_button1'], callback_data="none")
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['b2b']['menu_button2'], callback_data="none")
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['b2b']['menu_button3'], callback_data="none")
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['b2b']['menu_button4'], callback_data="none")
            ]
        ]
    ),
    'b2c': InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=LEXICON_RU['b2c']['menu_button1'], callback_data=MenuCallbackFactory(
                    current_keyboard='menu',
                    next_keyboard="my_score"
                ).pack()),
                InlineKeyboardButton(text=LEXICON_RU['b2c']['menu_button2'], callback_data=MenuCallbackFactory(
                    current_keyboard='menu',
                    next_keyboard="what_study"
                ).pack())
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['b2c']['menu_button3'], callback_data=MenuCallbackFactory(
                    current_keyboard='menu',
                    next_keyboard="eco_org"
                ).pack()),
                InlineKeyboardButton(text=LEXICON_RU['b2c']['menu_button4'], callback_data=MenuCallbackFactory(
                    current_keyboard='menu',
                    next_keyboard="have_idea"
                ).pack())
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['b2c']['menu_button5'], callback_data=MenuCallbackFactory(
                    current_keyboard='menu',
                    next_keyboard="back_quiz"
                ).pack())
            ]
        ]
    )
}

answer_quiz_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data='1'),
            InlineKeyboardButton(text="Нет", callback_data='0')
        ]
    ]
)

gift_quiz_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Получить", callback_data='gift')
        ]
    ]
)

callback_map = {
    "my_score": InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=LEXICON_RU['my_score']['button1'], callback_data=MenuCallbackFactory(
                    current_keyboard='my_score',
                    next_keyboard="earn_score"
                ).pack())
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['my_score']['button2'], callback_data=MenuCallbackFactory(
                    current_keyboard='my_score',
                    next_keyboard="buy_score"
                ).pack())
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['back_button'], callback_data=MenuCallbackFactory(
                    current_keyboard='my_score',
                    next_keyboard="menu_b2c"
                ).pack())
            ],
        ]
    ),
    "earn_score": InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=LEXICON_RU['earn_score']['button1'], callback_data="none")
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['earn_score']['button2'], callback_data=MenuCallbackFactory(
                    current_keyboard='earn_score',
                    next_keyboard="pick_tasks"
                ).pack())
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['back_button'], callback_data=MenuCallbackFactory(
                    current_keyboard='buy_score',
                    next_keyboard="my_score"
                ).pack())
            ],
        ]
    ),
    "buy_score": InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=LEXICON_RU['buy_score']['button1'], callback_data="none")
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['buy_score']['button2'], callback_data="none")
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['buy_score']['button3'], callback_data="none")
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['buy_score']['button4'], callback_data="none")
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['buy_score']['button5'], callback_data="none")
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['back_button'], callback_data=MenuCallbackFactory(
                    current_keyboard='buy_score',
                    next_keyboard="my_score"
                ).pack())
            ]
        ]
    ),
    'template_idea': InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=LEXICON_RU['template_idea']['button1'], callback_data="none")
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['template_idea']['button2'], callback_data="none")
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['template_idea']['button3'], callback_data="none")
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['back_button'], callback_data=MenuCallbackFactory(
                    current_keyboard='template_idea',
                    next_keyboard="have_idea"
                ).pack())
            ]
        ]
    ),
    "plan_idea": InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=LEXICON_RU['plan_idea']['button1'], callback_data="none")
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['plan_idea']['button2'], callback_data="none")
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['plan_idea']['button3'], callback_data="none")
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['back_button'], callback_data=MenuCallbackFactory(
                    current_keyboard='plan_idea',
                    next_keyboard="have_idea"
                ).pack())
            ]
        ]
    ),
    "what_study": InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=LEXICON_RU['what_study']['button1'], callback_data="none")
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['what_study']['button2'], callback_data="none")
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['what_study']['button3'], callback_data="none")
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['back_button'], callback_data=MenuCallbackFactory(
                    current_keyboard='what_study',
                    next_keyboard="menu_b2c"
                ).pack())
            ],
        ]
    ),
    "eco_org": InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=LEXICON_RU['eco_org']['button1'], callback_data="none")
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['eco_org']['button2'], callback_data="none")
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['back_button'], callback_data=MenuCallbackFactory(
                    current_keyboard='eco_org',
                    next_keyboard="menu_b2c"
                ).pack())
            ],
        ]
    ),
    "have_idea": InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=LEXICON_RU['have_idea']['button1'], callback_data=MenuCallbackFactory(
                    current_keyboard='have_idea',
                    next_keyboard="template_idea"
                ).pack())
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['have_idea']['button2'], callback_data=MenuCallbackFactory(
                    current_keyboard='have_idea',
                    next_keyboard="plan_idea"
                ).pack())
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['back_button'], callback_data=MenuCallbackFactory(
                    current_keyboard='have_idea',
                    next_keyboard="menu_b2c"
                ).pack())
            ],
        ]
    ),
    'pick_tasks': InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=LEXICON_RU['pick_tasks']['button1'], callback_data=MenuCallbackFactory(
                    current_keyboard='pick_tasks',
                    next_keyboard="get_favorites").pack()
                                     )
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['pick_tasks']['button2'], callback_data=MenuCallbackFactory(
                    current_keyboard='pick_tasks',
                    next_keyboard="get_completed").pack()
                                     )
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['pick_tasks']['button3'], callback_data=MenuCallbackFactory(
                    current_keyboard='pick_tasks',
                    next_keyboard="themes_earn").pack()
                                     )
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['back_button'], callback_data=MenuCallbackFactory(
                    current_keyboard='pick_tasks',
                    next_keyboard="earn_score").pack()
                                     )
            ]
        ]
    ),
    'themes_earn': keyboard_get_themes_earn,
    'task': InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=LEXICON_RU['task']['button1'], callback_data="solve")
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['task']['button2'], callback_data="favorites")
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['back_button'],
                                     callback_data=MenuCallbackFactory(current_keyboard='task',
                                                                       next_keyboard="pick_tasks").pack())
            ]
        ]
    ),
    'survey': InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=LEXICON_RU['task']['button1'], callback_data="solve")
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['task']['button2'], callback_data="favorites")
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['back_button'],
                                     callback_data=MenuCallbackFactory(current_keyboard='task',
                                                                       next_keyboard="pick_tasks").pack())
            ]
        ]
    ),
    'tasks': keyboard_tasks_and_themes,
    'menu_b2c': menu_keyboard['b2c'],
    'menu_b2b': menu_keyboard['b2b']
}

callback_map_admin = {
    'pick': InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=LEXICON_RU['admin']['pick']['button1'], callback_data="pick_user")
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['admin']['pick']['button2'], callback_data="pick_admin")
            ]
        ]
    ),
    'menu': InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=LEXICON_RU['admin']['menu']['button1'],
                                     callback_data=AdminMenuCallbackFactory(
                                         current_keyboard='menu',
                                         next_keyboard='change_task').pack()
                                     )
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['admin']['menu']['button2'],
                                     callback_data=AdminMenuCallbackFactory(
                                         current_keyboard='menu',
                                         next_keyboard='change_poll').pack()
                                     )
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['admin']['menu']['button3'],
                                     callback_data=AdminMenuCallbackFactory(
                                         current_keyboard='menu',
                                         next_keyboard='none').pack())
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['admin']['menu']['button4'],
                                     callback_data=AdminMenuCallbackFactory(
                                         current_keyboard='menu',
                                         next_keyboard='none').pack())
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['admin']['menu']['button5'],
                                     callback_data=AdminMenuCallbackFactory(
                                         current_keyboard='menu',
                                         next_keyboard='none').pack())
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['admin']['menu']['button6'],
                                     callback_data=AdminMenuCallbackFactory(
                                         current_keyboard='menu',
                                         next_keyboard='none').pack())
            ],
        ]
    ),
    'poll_option': InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Завершить вопрос", callback_data="end_options")
            ]
        ]
    ),
    'poll_question': InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Завершить опрос", callback_data="end_questions")
            ]
        ]
    ),
    'change_task': InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=LEXICON_RU['admin']['change_task']['button1'],
                                     callback_data=AdminMenuCallbackFactory(
                                         current_keyboard='change_task',
                                         next_keyboard="create_task").pack())
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['admin']['change_task']['button2'],
                                     callback_data=AdminMenuCallbackFactory(
                                         current_keyboard='change_task',
                                         next_keyboard="get_task").pack())
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['admin']['change_task']['button3'],
                                     callback_data=AdminMenuCallbackFactory(
                                         current_keyboard='change_task',
                                         next_keyboard="delete_task").pack())
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['back_button'], callback_data=AdminMenuCallbackFactory(
                    current_keyboard='change_task',
                    next_keyboard="menu").pack())
            ]
        ]
    ),
    'change_poll': InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=LEXICON_RU['admin']['change_poll']['button1'],
                                     callback_data=AdminMenuCallbackFactory(
                                         current_keyboard='change_poll',
                                         next_keyboard="create_poll").pack())
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['admin']['change_poll']['button2'],
                                     callback_data=AdminMenuCallbackFactory(
                                         current_keyboard='change_poll',
                                         next_keyboard="none").pack())
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['admin']['change_poll']['button3'],
                                     callback_data=AdminMenuCallbackFactory(
                                         current_keyboard='change_poll',
                                         next_keyboard="none").pack())
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['back_button'], callback_data=AdminMenuCallbackFactory(
                    current_keyboard='change_poll',
                    next_keyboard="menu").pack())
            ]
        ]
    ),
    'create_task': keyboard_create_task,
    'get_task': keyboard_get_task,
    'delete_task': keyboard_get_task,
    'create_poll': keyboard_create_poll
}
