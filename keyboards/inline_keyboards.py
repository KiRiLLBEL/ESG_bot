from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from filters.menu_filters import MenuCallbackFactory, AdminMenuCallbackFactory
from lexicon.lexicon_ru import LEXICON_RU
from models.product import Product


def keyboard_create_task(themes):
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    if themes:
        for button in themes:
            buttons.append(InlineKeyboardButton(
                text=button.title,
                callback_data=f'{button.theme_id}')
            )
    kb_builder.row(*buttons, width=1)
    kb_builder.row(InlineKeyboardButton(
        text=LEXICON_RU['admin']['create_task']['button1'],
        callback_data='create_theme'))
    kb_builder.row(InlineKeyboardButton(
        text=LEXICON_RU['back_button'],
        callback_data=AdminMenuCallbackFactory(
            current_keyboard='back',
            next_keyboard="change_task"
        ).pack()
    )
    )
    return kb_builder.as_markup()

def keyboard_create_event(themes):
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    if themes:
        for button in themes:
            buttons.append(InlineKeyboardButton(
                text=button.title,
                callback_data=f'{button.event_theme_id}')
            )
    kb_builder.row(*buttons, width=1)
    kb_builder.row(InlineKeyboardButton(
        text=LEXICON_RU['admin']['create_event']['button1'],
        callback_data='create_theme'))
    kb_builder.row(InlineKeyboardButton(
        text=LEXICON_RU['back_button'],
        callback_data=AdminMenuCallbackFactory(
            current_keyboard='back',
            next_keyboard="change_event"
        ).pack()
    )
    )
    return kb_builder.as_markup()


def keyboard_create_survey(themes):
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    if themes:
        for button in themes:
            buttons.append(InlineKeyboardButton(
                text=button.title,
                callback_data=str(button.theme_id))
            )
    kb_builder.row(*buttons, width=1)
    kb_builder.row(InlineKeyboardButton(
        text=LEXICON_RU['admin']['create_survey']['button1'],
        callback_data='create_theme'))
    kb_builder.row(InlineKeyboardButton(
        text=LEXICON_RU['back_button'],
        callback_data=AdminMenuCallbackFactory(
            current_keyboard='back',
            next_keyboard="change_survey"
        ).pack()
    )
    )
    return kb_builder.as_markup()

def keyboard_survey_pagination(current_page, total_pages, question):
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = [InlineKeyboardButton(text=f"Изменить ответ №{i + 1}", callback_data=f'opt:{option.option_id}') for i, option in enumerate(question.options)]
    line: list[InlineKeyboardButton] = []
    kb_builder.row(InlineKeyboardButton(text='Изменить вопрос', callback_data=f'que:{question.question_id}'), width=1)
    if current_page > 1:
        line.append(InlineKeyboardButton(text='⬅️', callback_data=f'page:{current_page - 1}'))

    line.append(InlineKeyboardButton(text=f'Вопрос {current_page} из {total_pages}', callback_data='current_page'))

    if current_page < total_pages:
        line.append(InlineKeyboardButton(text='➡️', callback_data=f'page:{current_page + 1}'))

    kb_builder.row(*buttons, width=1)
    kb_builder.row(*line, width=3)
    kb_builder.row(InlineKeyboardButton(text=LEXICON_RU['back_button'], callback_data=AdminMenuCallbackFactory(
        current_keyboard='back',
        next_keyboard="change_survey"
    ).pack()), width=1)
    return kb_builder.as_markup()

def keyboard_get_surveys(surveys):
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    if surveys:
        for button in surveys:
            buttons.append(InlineKeyboardButton(
                text=button.title,
                callback_data=str(button.survey_id))
            )
    kb_builder.row(*buttons, width=1)
    kb_builder.row(InlineKeyboardButton(
        text=LEXICON_RU['back_button'],
        callback_data=AdminMenuCallbackFactory(
            current_keyboard='back',
            next_keyboard="change_survey"
        ).pack()
    )
    )
    return kb_builder.as_markup()



def keyboard_survey_themes(themes):
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    if themes:
        for button in themes:
            buttons.append(InlineKeyboardButton(
                text=button.title,
                callback_data=str(button.theme_id))
            )
    kb_builder.row(*buttons, width=1)
    kb_builder.row(InlineKeyboardButton(
        text=LEXICON_RU['back_button'],
        callback_data=AdminMenuCallbackFactory(
            current_keyboard='back',
            next_keyboard="change_survey"
        ).pack()
    )
    )
    return kb_builder.as_markup()

def keyboard_poster_pagination(current_page, total_pages, event):
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    line: list[InlineKeyboardButton] = []
    if current_page > 1:
        line.append(InlineKeyboardButton(text='⬅️', callback_data=f'evpage:{current_page - 1}'))

    line.append(InlineKeyboardButton(text=f'Мероприятие {current_page} из {total_pages}', callback_data='current_page_ev'))

    if current_page < total_pages:
        line.append(InlineKeyboardButton(text='➡️', callback_data=f'evpage:{current_page + 1}'))

    kb_builder.row(*line, width=3)
    kb_builder.row(InlineKeyboardButton(text="Добавить в избранное", callback_data="favorites_event"), width=1)
    kb_builder.row(InlineKeyboardButton(text=LEXICON_RU['back_button'], callback_data=MenuCallbackFactory(
        current_keyboard='back',
        next_keyboard="eco_org"
    ).pack()), width=1)
    return kb_builder.as_markup()

def keyboard_fav_event_pagination(current_page, total_pages, event):
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    line: list[InlineKeyboardButton] = []
    if current_page > 1:
        line.append(InlineKeyboardButton(text='⬅️', callback_data=f'evfpage:{current_page - 1}'))

    line.append(InlineKeyboardButton(text=f'Мероприятие {current_page} из {total_pages}', callback_data='current_page_ev'))

    if current_page < total_pages:
        line.append(InlineKeyboardButton(text='➡️', callback_data=f'evfpage:{current_page + 1}'))

    kb_builder.row(*line, width=3)
    kb_builder.row(InlineKeyboardButton(text=LEXICON_RU['back_button'], callback_data=MenuCallbackFactory(
        current_keyboard='back',
        next_keyboard="eco_org"
    ).pack()), width=1)
    return kb_builder.as_markup()


def create_keyboard_options(options):
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    for option in options:
        button = InlineKeyboardButton(text=option.text,
                                      callback_data=f'{option.option_id}')
        buttons.append(button)
    kb_builder.row(*buttons, width=1)

    return kb_builder.as_markup()


def keyboard_get_task(tasks):
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    if tasks:
        for button in tasks:
            buttons.append(InlineKeyboardButton(
                text=button.title,
                callback_data=str(button.task_id))
            )
    kb_builder.row(*buttons, width=1)
    kb_builder.row(InlineKeyboardButton(
        text=LEXICON_RU['back_button'],
        callback_data=AdminMenuCallbackFactory(
            current_keyboard='back',
            next_keyboard="change_task"
        ).pack()
    )
    )
    return kb_builder.as_markup()

def keyboard_get_themes(themes):
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    if themes:
        for button in themes:
            buttons.append(InlineKeyboardButton(
                text=button.title,
                callback_data=str(button.theme_id))
            )
    kb_builder.row(*buttons, width=1)
    kb_builder.row(InlineKeyboardButton(
        text=LEXICON_RU['back_button'],
        callback_data=AdminMenuCallbackFactory(
            current_keyboard='back',
            next_keyboard='change_task'
        ).pack()
    )
    )
    return kb_builder.as_markup()


def keyboard_get_themes_earn(themes):
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    if themes:
        for button in themes:
            buttons.append(InlineKeyboardButton(
                text=button.title,
                callback_data=f'{button.theme_id}')
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
            print(obj)
            buttons.append(InlineKeyboardButton(
                text=button[0].title + ' (задание)' if button[1] == 'task' else button[0].title + ' (опрос)',
                callback_data=button[1] + "_" + str(button[0].task_id if button[1] == 'task' else button[0].survey_id)
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

def create_pagination_keyboard(current_page: int, total_pages: int, product: Product):
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []

    if current_page > 1:
        buttons.append(InlineKeyboardButton(text='⬅️', callback_data=f'page:{current_page - 1}'))

    buttons.append(InlineKeyboardButton(text=f'Страница {current_page} из {total_pages}', callback_data='current_page'))

    if current_page < total_pages:
        buttons.append(InlineKeyboardButton(text='➡️', callback_data=f'page:{current_page + 1}'))


    kb_builder.row(*buttons, width=3)
    kb_builder.row(InlineKeyboardButton(text='Купить', callback_data=f'buy:{product.product_id}'), width=1)
    kb_builder.row(InlineKeyboardButton(text=LEXICON_RU['back_button'], callback_data=MenuCallbackFactory(
                    current_keyboard='earn_score',
                    next_keyboard="buy_score"
                ).pack()), width=1)
    return kb_builder.as_markup()


start_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=LEXICON_RU['start_b2c'], callback_data='person'),
            InlineKeyboardButton(text=LEXICON_RU['start_b2b'], callback_data='business')
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
    'business': InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=LEXICON_RU['business']['menu_button1'], callback_data="none")
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['business']['menu_button2'], callback_data="none")
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['business']['menu_button3'], callback_data="none")
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['business']['menu_button4'], callback_data="none")
            ]
        ]
    ),
    'person': InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=LEXICON_RU['person']['menu_button1'], callback_data=MenuCallbackFactory(
                    current_keyboard='menu',
                    next_keyboard="my_score"
                ).pack()),
                InlineKeyboardButton(text=LEXICON_RU['person']['menu_button2'], callback_data=MenuCallbackFactory(
                    current_keyboard='menu',
                    next_keyboard="what_study"
                ).pack())
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['person']['menu_button3'], callback_data=MenuCallbackFactory(
                    current_keyboard='menu',
                    next_keyboard="eco_org"
                ).pack()),
                InlineKeyboardButton(text=LEXICON_RU['person']['menu_button4'], callback_data=MenuCallbackFactory(
                    current_keyboard='menu',
                    next_keyboard="have_idea"
                ).pack())
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['person']['menu_button5'], callback_data=MenuCallbackFactory(
                    current_keyboard='menu',
                    next_keyboard="none"
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
                InlineKeyboardButton(text=LEXICON_RU['buy_score']['button1'], callback_data=MenuCallbackFactory(
                    current_keyboard='buy_score',
                    next_keyboard="merch"
                ).pack())
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
                InlineKeyboardButton(text=LEXICON_RU['what_study']['button1'], callback_data=MenuCallbackFactory(
                    current_keyboard='what_study',
                    next_keyboard="video_course"
                ).pack())
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['what_study']['button2'], callback_data=MenuCallbackFactory(
                    current_keyboard='what_study',
                    next_keyboard="books"
                ).pack())
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['what_study']['button3'], callback_data=MenuCallbackFactory(
                    current_keyboard='what_study',
                    next_keyboard="eco_states"
                ).pack())
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['what_study']['button4'], callback_data=MenuCallbackFactory(
                    current_keyboard='what_study',
                    next_keyboard="for_me"
                ).pack())
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['what_study']['button5'], callback_data=MenuCallbackFactory(
                    current_keyboard='what_study',
                    next_keyboard="appointment"
                ).pack())
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['back_button'], callback_data=MenuCallbackFactory(
                    current_keyboard='what_study',
                    next_keyboard="menu_b2c"
                ).pack())
            ],
        ]
    ),
    "video_course": InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=LEXICON_RU['back_button'], callback_data=MenuCallbackFactory(
                    current_keyboard='video_course',
                    next_keyboard="what_study"
                ).pack())
            ]
        ]
    ),
    "books": InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=LEXICON_RU['back_button'], callback_data=MenuCallbackFactory(
                    current_keyboard='books',
                    next_keyboard="what_study"
                ).pack())
            ]
        ]
    ),
    "eco_states": InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=LEXICON_RU['back_button'], callback_data=MenuCallbackFactory(
                    current_keyboard='eco_states',
                    next_keyboard="what_study"
                ).pack())
            ]
        ]
    ),
    "for_me": InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=LEXICON_RU['back_button'], callback_data=MenuCallbackFactory(
                    current_keyboard='for_me',
                    next_keyboard="what_study"
                ).pack())
            ]
        ]
    ),
    "appointment": InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=LEXICON_RU['back_button'], callback_data=MenuCallbackFactory(
                    current_keyboard='appointment',
                    next_keyboard="what_study"
                ).pack())
            ]
        ]
    ),
    "eco_org": InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=LEXICON_RU['eco_org']['button1'], callback_data=MenuCallbackFactory(
                    current_keyboard='eco_org',
                    next_keyboard="poster"
                ).pack())
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['eco_org']['button2'], callback_data=MenuCallbackFactory(
                    current_keyboard='eco_org',
                    next_keyboard="produce_meet"
                ).pack())
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['eco_org']['button3'], callback_data=MenuCallbackFactory(
                    current_keyboard='eco_org',
                    next_keyboard="get_favorite_events"
                ).pack())
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['back_button'], callback_data=MenuCallbackFactory(
                    current_keyboard='eco_org',
                    next_keyboard="menu_b2c"
                ).pack())
            ],
        ]
    ),
    "poster": keyboard_poster_pagination,
    "get_favorite_events": keyboard_fav_event_pagination,
    "produce_meet": InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=LEXICON_RU['back_button'], callback_data=MenuCallbackFactory(
                    current_keyboard='produce_meet',
                    next_keyboard="eco_org"
                ).pack())
            ]
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
                    current_keyboard='back',
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
    'menu_b2c': menu_keyboard['person'],
    'menu_b2b': menu_keyboard['business']
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
                                         next_keyboard='change_survey').pack()
                                     )
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['admin']['menu']['button3'],
                                     callback_data=AdminMenuCallbackFactory(
                                         current_keyboard='menu',
                                         next_keyboard='change_product').pack())
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['admin']['menu']['button4'],
                                     callback_data=AdminMenuCallbackFactory(
                                         current_keyboard='menu',
                                         next_keyboard='change_event').pack())
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
                                         next_keyboard='edit_task').pack())
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['back_button'], callback_data=AdminMenuCallbackFactory(
                    current_keyboard='back',
                    next_keyboard="menu").pack())
            ]
        ]
    ),
    'change_survey': InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=LEXICON_RU['admin']['change_survey']['button1'],
                                     callback_data=AdminMenuCallbackFactory(
                                         current_keyboard='change_survey',
                                         next_keyboard='create_survey').pack())
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['admin']['change_survey']['button2'],
                                     callback_data=AdminMenuCallbackFactory(
                                         current_keyboard='change_survey',
                                         next_keyboard="get_survey_themes").pack())
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['admin']['change_survey']['button3'],
                                     callback_data=AdminMenuCallbackFactory(
                                         current_keyboard='change_survey',
                                         next_keyboard="change_main_survey").pack())
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['back_button'], callback_data=AdminMenuCallbackFactory(
                    current_keyboard='back',
                    next_keyboard="menu").pack())
            ]
        ]
    ),
    'change_product': InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=LEXICON_RU['admin']['change_product']['button1'], callback_data=AdminMenuCallbackFactory(
                    current_keyboard='change_product',
                    next_keyboard="create_product").pack())
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['admin']['change_product']['button2'], callback_data=AdminMenuCallbackFactory(
                    current_keyboard='change_product',
                    next_keyboard="none").pack())
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['admin']['change_product']['button3'], callback_data=AdminMenuCallbackFactory(
                    current_keyboard='change_product',
                    next_keyboard="none").pack())
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['admin']['change_product']['button4'], callback_data=AdminMenuCallbackFactory(
                    current_keyboard='change_product',
                    next_keyboard="none").pack())
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['back_button'], callback_data=AdminMenuCallbackFactory(
                    current_keyboard='back',
                    next_keyboard="menu").pack())
            ]
        ]
    ),
    'change_event': InlineKeyboardMarkup(
          inline_keyboard=[
              [
                  InlineKeyboardButton(text=LEXICON_RU['admin']['change_event']['button1'], callback_data=AdminMenuCallbackFactory(
                        current_keyboard='change_event',
                        next_keyboard="create_event").pack())
              ],
              [
                  InlineKeyboardButton(text=LEXICON_RU['admin']['change_event']['button2'], callback_data=AdminMenuCallbackFactory(
                        current_keyboard='change_event',
                        next_keyboard="none").pack())
              ],
              [
                    InlineKeyboardButton(text=LEXICON_RU['back_button'], callback_data=AdminMenuCallbackFactory(
                        current_keyboard='back',
                        next_keyboard='menu').pack())
              ]
          ]
    ),
    'create_event': keyboard_create_event,
    'create_product': InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=LEXICON_RU['back_button'], callback_data=AdminMenuCallbackFactory(
                    current_keyboard='back',
                    next_keyboard='change_product').pack())
            ]
        ]
    ),
    'create_task': keyboard_create_task,
    'get_themes':keyboard_get_themes,
    'edit_task': keyboard_get_task,
    'create_survey': keyboard_create_survey,
    'get_survey_themes': keyboard_survey_themes,
    'edit_survey': keyboard_get_surveys,
    'edit_question': InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Изменить текст вопроса", callback_data="edit_question")
            ],
            [
                InlineKeyboardButton(text="Удалить вопрос", callback_data="delete_question")
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['back_button'], callback_data=AdminMenuCallbackFactory(
                        current_keyboard='back',
                        next_keyboard="change_survey"
                    ).pack())
            ]
        ]
    ),
    'edit_option': InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Изменить текст ответа", callback_data="edit_option")
            ],
            [
                InlineKeyboardButton(text="Удалить ответ", callback_data="delete_option")
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['back_button'], callback_data=AdminMenuCallbackFactory(
                        current_keyboard='back',
                        next_keyboard="change_survey"
                ).pack())
            ]
        ]
    ),
    'task_choose_edit': InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Измените задание", callback_data=AdminMenuCallbackFactory(
                    current_keyboard='task_choose_edit',
                    next_keyboard='task_editor').pack())
            ],
            [
                InlineKeyboardButton(text="Удалить задание", callback_data=AdminMenuCallbackFactory(
                    current_keyboard='task_choose_edit',
                    next_keyboard='menu').pack())
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['back_button'], callback_data=AdminMenuCallbackFactory(
                    current_keyboard='back',
                    next_keyboard='change_task').pack())
            ]
        ]
    ),
    'task_editor': InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Изменить название", callback_data=AdminMenuCallbackFactory(
                    current_keyboard='task_editor',
                    next_keyboard='change_task_title').pack())
            ],
            [
                InlineKeyboardButton(text="Изменить баллы за задание", callback_data=AdminMenuCallbackFactory(
                    current_keyboard='task_editor',
                    next_keyboard='change_task_value').pack())
            ],
            [
                InlineKeyboardButton(text="Изменить описание задания", callback_data=AdminMenuCallbackFactory(
                    current_keyboard='task_editor',
                    next_keyboard='change_task_description').pack())
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['back_button'], callback_data=AdminMenuCallbackFactory(
                    current_keyboard='back',
                    next_keyboard='task_choose_edit').pack())
            ]
        ]
    ),
    'change_main_survey': InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=LEXICON_RU['admin']['change_main_survey']['button1'], callback_data='person')
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['admin']['change_main_survey']['button2'], callback_data='business')
            ],
            [
                InlineKeyboardButton(text=LEXICON_RU['back_button'], callback_data=AdminMenuCallbackFactory(
                    current_keyboard='back',
                    next_keyboard='change_survey').pack())
            ]
        ]
    ),
    'Admin:survey_options': InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Завершить вопрос", callback_data="end_options")
            ]
        ]
    ),
    'Admin:survey_questions': InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Завершить опрос", callback_data="end_questions")
            ]
        ]
    )
}
