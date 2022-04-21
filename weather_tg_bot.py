import datetime
from main import bot, start
from pyowm.owm import OWM
from pyowm.utils.config import get_default_config

config_dict = get_default_config()
owm = OWM('c1761cec9eb349eee4b599c04816adeb', config_dict)
config_dict['language'] = 'ru'


@bot.message_handler(content_types=['text'])
def weather(message):
    mesg = bot.send_message(message.chat.id, 'В каком городе хотим узнать погоду?\n'
                                             '(напишите назад для выхода)')
    bot.register_next_step_handler(mesg, findd)


def findd(message):
    if message.text.lower() == 'назад':
        start(message)
    else:
        try:
            mgr = owm.weather_manager()
            observation = mgr.weather_at_place(message.text)
            w = observation.weather
            temp = w.temperature('celsius')['temp']
            today = datetime.datetime.today()
            answer = 'Сегодня, ' + (
                today.strftime("%d/%m/%Y")) + ' ' + 'в городе ' + message.text.capitalize() + ' ' + w.detailed_status + '.\n'
            answer += 'Температура в районе ' + str(temp) + ' по Цельсию.' + '\n\n'
            if temp < 5:
                answer += 'Сейчас на улице холодно, одевайся тепло!'
            elif temp < 17:
                answer += 'Сейчас на улице прохладно, одевайся потеплее!'
            else:
                answer += 'Погода просто каеф! Одевайся как душе угодно!'
            bot.send_message(message.chat.id, answer)
        except Exception:
            bot.send_message(message.chat.id, 'Я ещё не знаю такого города :(\nДавай посмотрим погоду в другом месте?')
