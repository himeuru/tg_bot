from telebot import TeleBot, types
from random import randint
from PIL import Image
from data.cfg import *


pictures = {
    0: './images/game/планеты.jpg',
    1: './images/game/остров.jpg',
    2: './images/game/космолёт.jpg',
}
states = {}
inventories = {}
bot = TeleBot(bot_token)


@bot.message_handler(commands=["game"])
def start_game(message):
    user = message.chat.id
    states[user] = 0
    inventories[user] = []
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    first_choose = types.KeyboardButton("1")
    second_choose = types.KeyboardButton("2")
    back_button = types.KeyboardButton('⬅назад')
    markup.add(first_choose, second_choose, back_button)
    bot.send_message(user, "Добро пожаловать в игру!\nВыберите путь", reply_markup=markup)
    process_state(user, states[user], inventories[user])


@bot.message_handler(content_types=['text'])
def user_answer(message):
    user = message.chat.id
    process_answer(user, message.text)


def process_state(user, state, inventory):
    image = Image.open(pictures[state])
    kb = types.InlineKeyboardMarkup()
    bot.send_photo(user, image)
    if state == 0:
        kb.add(types.InlineKeyboardButton(text="полететь направо", callback_data="1"))
        kb.add(types.InlineKeyboardButton(text="полететь налево", callback_data="2"))
        bot.send_message(user, "Вы в оказались в открытом космосе, перед вами две планеты.", reply_markup=kb)
    if state == 1:
        kb.add(types.InlineKeyboardButton(text="доплыть до островка", callback_data="1"))
        kb.add(types.InlineKeyboardButton(text="телепорт обратно на космолёт", callback_data="2"))
        bot.send_message(user, "К удивлению планета оказалась пригодной для жизни, но в большинстве преобладает вода,"
                               " вдали виднеется маленький островок.",
                         reply_markup=kb)
    if state == 2:
        bot.send_message(user, "Спасибо за игру! Вы выйграли.")


def process_answer(user, answer):
    if states[user] == 0:
        if answer == "1":
            states[user] = 1
        else:
            if "key" in inventories[user]:
                bot.send_message(user, "Вы спускаетесь на планету, её температура теперь не страшна вам. "
                                       " После недолгих поисков вы находите редкий образец метеорита."
                                       " Кажется, теперь вы можете возвращаться на космолёт.")
                states[user] = 2
            else:
                bot.send_message(user, "Планета слишком горячая чтоб спускаться на неё, и, кажется вам"
                                       " потребуется огнеупорный скафандр."
                                       "Придется вернуться обратно.")
                states[user] = 0
    elif states[user] == 1:
        if answer == "2":
            bot.send_message(user, "И правда, не стоит спускаться на неизвестную планету. Возвращаемся назад...")
            states[user] = 0
        else:
            bot.send_message(user, "Вы пробуете доплыть до этого островка...")
            chance = randint(0, 100)
            if chance > 30:
                bot.send_message(user, "Вода оказалось теплой, в капсуле на островке вы находите огнеупорный скафандр."
                                       " Стоит вернутся на космолёт и опробовать его в деле.")
                inventories[user].append("key")
                states[user] = 0
            else:
                bot.send_message(user, "Из-за перепадов давления начинается шторм, на полпути вас подхватывают волны"
                                       " и возвращают обратно.")
                states[user] = 1
    process_state(user, states[user], inventories[user])
