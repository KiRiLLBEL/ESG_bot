from aiogram.fsm.state import State, StatesGroup


class Admin(StatesGroup):
    pick = State()
    join = State()

    task_theme = State()
    task_name = State()
    task_description = State()
    task_score = State()
    edit_task = State()
    task_tasks = State()
    task_choose_edit = State()
    task_editor = State()
    task_edit_title = State()
    task_edit_description = State()
    task_edit_value = State()

    survey_theme = State()
    survey_name = State()
    survey_questions = State()
    survey_options = State()
    survey_score = State()
    survey_main_pick = State()
    survey_edit_pick_theme = State()
    survey_edit_pick_survey = State()
    survey_edit_option = State()
    survey_edit_question = State()

    event_theme = State()
    event_title = State()
    event_description = State()
    event_place = State()
    event_organizer = State()
    event_image_url = State()
    event_capacity = State()
    event_value = State()
    event_date = State()

    product_name = State()
    product_score = State()
    product_image = State()


callback_error_input = [
    Admin.task_theme,
    Admin.task_name,
    Admin.task_edit_title,
    Admin.task_edit_value,
    Admin.task_edit_description,
    Admin.task_description,
    Admin.task_score,
    Admin.survey_theme,
    Admin.survey_name,
    Admin.survey_score,
    Admin.survey_questions,
    Admin.survey_options,
    Admin.product_score,
    Admin.product_name,
    Admin.survey_edit_option,
    Admin.survey_edit_question,
    Admin.event_theme,
    Admin.event_title,
    Admin.event_description,
    Admin.event_place,
    Admin.event_organizer,
    Admin.event_image_url,
    Admin.event_capacity,
    Admin.event_value
]
