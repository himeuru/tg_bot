import datetime
import telebot
from pyowm.owm import OWM
from pyowm.utils.config import get_default_config

bot = telebot.TeleBot("5273072249:AAF2OLkMgDNCUtEhdAftkoNhRRCDwfEyn9k", parse_mode='html')

# language
config_dict = get_default_config()
owm = OWM('c1761cec9eb349eee4b599c04816adeb', config_dict)
config_dict['language'] = 'ru'


@bot.message_handler(commands=['start'])
def welcome(message):
    if message.text == '/start':
        bot.send_message(message.chat.id,
                         'Добро пожаловать, {0.first_name}! \n'
                         'Я - <b>{1.first_name}</b>, твой персональный ассистент.\n'
                         '/help - список моих возможностей'.format(message.from_user, bot.get_me()))


@bot.message_handler(commands=['help'])
def help(message):
    if message.text == '/help@PPTlo_bot' or '/help':
        bot.send_message(message.chat.id,
                         'Вот список моих возможностей:\n'
                         '/weather - узнать погоды\n'
                         '/hi - приветствие\n'
                         '/joke - поведать анекдот\n'
                         '/ppt - узнать расписание занятий\n'
                         '/music - самые популярные песни за последнюю неделю\n'
                         '/mood - поднять себе настроение\n'
                         '/bus - узнать расписание автобусов')


@bot.message_handler(commands=['joke'])
def joke(message):
    if message.text == '/joke':
        bot.send_message(message.chat.id, 'Колобок повесился')


@bot.message_handler(commands=['hi'])
def hi(message):
    if message.text == '/hi':
        bot.send_message(message.chat.id, 'Приветствую, /help - для вывода моих возможностей')


@bot.message_handler(commands=['weather'])
def weather(message):
    if message.text == '/weather':
        mesg = bot.send_message(message.chat.id, 'В каком городе хотим узнать погоду?')
        bot.register_next_step_handler(mesg, findd)


def findd(message):
    try:
        mgr = owm.weather_manager()
        observation = mgr.weather_at_place(message.text)
        w = observation.weather
        temp = w.temperature('celsius')['temp']
        today = datetime.datetime.today()
        answer = 'Сегодня, ' + (
            today.strftime("%d/%m/%Y")) + ' ' + 'в городе ' + message.text + ' ' + w.detailed_status + '\n'
        answer += 'Температура в районе ' + str(temp) + ' по Цельсию.' + '\n\n'
        if temp < 5:
            answer += 'Сейчас на улице холодно, одевайся тепло!'
        elif temp < 17:
            answer += 'Сейчас на улице прохладно, одевайся потеплее!'
        else:
            answer += 'Погода просто каеф! Одевайся как душе угодно!'
            bot.send_message(message.chat.id, answer)
    except:
        bot.send_message(message.chat.id, 'Я ещё не знаю такого города :(\nДавай посмотрим погоду в другом месте?')


bot.polling(none_stop=True)
