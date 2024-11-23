from aiogram.fsm.state import StatesGroup, State


class Form(StatesGroup):
    set_topic = State()
    get_topic = State()
    admin_true = State()
    msg = State()
    choice = State()

class Builder(StatesGroup):
    get_text = State()
    get_img = State()
    get_video = State()
    get_url = State()
    get_time_start = State()
    get_time_del = State()
    choice_topic = State()
    done = State()

class Url(StatesGroup):
    url = State()
    name = State()

class Topic(StatesGroup):
    menu = State()

