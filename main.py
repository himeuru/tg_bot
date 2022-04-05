import os
import requests
from datetime import datetime, timedelta
from telebot import types, telebot
from io import BytesIO
from PIL import Image
from data.cfg import *
from data import db_session
from data.db_session import Info, __factory
from dictionaries import _comets, _nebulae, _solar, _stars, _satellites

bot = telebot.TeleBot(bot_token)
session = __factory()
db_sess = db_session.create_session()
info = Info()
main_btns, album_btns, photo_btns = True, False, False
comets_btn, nebulae_btn, solar_btn, stars_btn, satellites_btn = False, False, False, False, False


@bot.message_handler(commands=['start'])
def start(message):
    params = []
    global info_id, info_name, info_exp, info_time
    for param in session.query(Info).filter(Info.id == message.chat.id):
        params = str(param).split(',')
        info_id = params[0][2:-1]
        info_name = params[1][1:-1]
        info_exp = params[2][1:-1]
        info_time = params[3][1:-2]

    if len(params) == 0:
        info.exp, info_exp = 0, 0
        info.daily_photo_time, info_time = str(datetime.now() - timedelta(days=1))[:-16], \
                                           str(datetime.now() - timedelta(days=1))[:-16]
        info.id, info_id = message.chat.id, message.chat.id
        info.name, info_name = message.from_user.username, message.from_user.username
        db_sess.add(info)
        db_sess.commit()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    photo_choose_button = types.KeyboardButton("фото")
    quiz_button = types.KeyboardButton("викторина")
    album_button = types.KeyboardButton("альбом")
    exp_button = types.KeyboardButton("мой опыт")
    markup.add(photo_choose_button, quiz_button, album_button, exp_button)
    bot.send_message(message.chat.id, "выберите кнопку", reply_markup=markup)


@bot.message_handler(content_types=['text'])
def callback(message):
    print('callback to:', message.chat.id, message.chat.username)

    global info_id, info_name, info_exp, info_time, main_btns, album_btns, photo_btns, comets_btn, nebulae_btn, \
        solar_btn, stars_btn, satellites_btn
    params = []
    for param in session.query(Info).filter(Info.id == message.chat.id):
        params = str(param).split(',')
        info_id = params[0][2:-1]
        info_name = params[1][1:-1]
        info_exp = params[2][1:-1]
        info_time = params[3][1:-2]
    if len(params) == 0:
        info.exp, info_exp = 0, 0
        info.daily_photo_time, info_time = str(datetime.now() - timedelta(days=1))[:-16], \
                                           str(datetime.now() - timedelta(days=1))[:-16]
        info.id, info_id = message.chat.id, message.chat.id
        info.name, info_name = message.from_user.username, message.from_user.username
        db_sess.add(info)
        db_sess.commit()

    if main_btns:
        if message.text == 'фото':
            main_btns, photo_btns = False, True
            photo_msg(message)
        elif message.text == 'викторина':
            bot.send_message(message.chat.id, 'в разработке')
        elif message.text == 'альбом':
            main_btns, album_btns = False, True
            album(message)
        elif message.text == 'мой опыт':
            bot.send_message(message.chat.id, f'у вас {int(info_exp)} опыта')
    elif album_btns:
        if message.text == 'кометы' or message.text.lower() in _comets or (
                message.text.isdigit() and 0 <= int(message.text) - 1 < len(_comets) and comets_btn):
            comets_btn, nebulae_btn, solar_btn, stars_btn, satellites_btn = True, False, False, False, False
            comets(message)
        elif message.text == 'туманности' or message.text.lower() in _nebulae or (
                message.text.isdigit() and 0 <= int(message.text) - 1 < len(_nebulae) and nebulae_btn):
            comets_btn, nebulae_btn, solar_btn, stars_btn, satellites_btn = False, True, False, False, False
            nebulae(message)
        elif message.text == 'спутники' or message.text.lower() in _satellites or (
                ('.' in message.text) and (int(message.text[0]) - 1 < len(_satellites)) and satellites_btn):
            comets_btn, nebulae_btn, solar_btn, stars_btn, satellites_btn = False, False, False, False, True
            satellites(message)
        elif message.text == 'солнечная система' or message.text.lower() in _solar or (
                message.text.isdigit() and 0 <= int(message.text) - 1 < len(_solar) and solar_btn):
            comets_btn, nebulae_btn, solar_btn, stars_btn, satellites_btn = False, False, True, False, False
            solar(message)
        elif message.text == 'звёзды' or message.text.lower() in _stars or (
                message.text.isdigit() and 0 <= int(message.text) - 1 < len(_stars) and stars_btn):
            comets_btn, nebulae_btn, solar_btn, stars_btn, satellites_btn = False, False, False, True, False
            stars(message)
        elif message.text == '⬅назад':
            comets_btn, nebulae_btn, solar_btn, stars_btn, satellites_btn, main_btns, album_btns = \
                False, False, False, False, False, True, False
            start(message)
    elif photo_btns:
        if 'фото дня' in message.text:
            daily_photo_msg(message)
        elif message.text == '⬅назад':
            main_btns, photo_btns = True, False
            start(message)


def daily_photo_msg(message):
    global url_for_date, info_exp
    if message.text == 'фото дня':
        url_for_date = f'{api_url}&date={datetime.now().strftime("%Y-%m-%d")}'
        time = (datetime.now())
        sort_time = [str(time)[:-16].split('-'), str(info_time).split('-')]
        res = sorted(sort_time, key=lambda x: (x[0], x[1], x[2]))
        if res[0] == str(info_time).split('-') and res[0] != res[1]:
            info.daily_photo_time = str(time)[:-16]
            info.name = info_name
            info.exp = int(info_exp) + 5
            db_sess.execute(f"""UPDATE information SET exp='{info.exp}', daily_photo_time='{info.daily_photo_time}' 
                        WHERE id='{info_id}'""")
            db_sess.commit()
            info_exp = info.exp
            bot.send_message(message.chat.id, "вы получили 5 опыта")
    elif message.text == 'вчерашнее фото дня':
        url_for_date = f'{api_url}&date={(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")}'
    elif message.text == 'позавчерашнее фото дня':
        url_for_date = f'{api_url}&date={(datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")}'
    try:
        response = requests.get(url_for_date)
        response.raise_for_status()
        data = response.json()
        url = data['url']
        title = data['title']
        explanation = data['explanation']
        print(url)
    except Exception:
        url = False
    if url:
        if 'www.youtube.com' not in url:
            image_response = requests.get(url)

            image = Image.open(BytesIO(image_response.content))

            if not image_dir.exists():
                os.mkdir(image_dir)
            image.save(image_dir / f'{title}.{image.format}', image.format)

            image = Image.open(BytesIO(image_response.content))
            if image:
                print('image success')
                if len(explanation) > 950:
                    for i in range(len(explanation), 0, -1):
                        if str(explanation)[i - 1] == '.' and i <= 950:
                            explanation = explanation[:i]
                            break
                    bot.send_photo(message.from_user.id, open(f'./images/{title}.{image.format}', 'rb'),
                                   f'name: {title} \nexplanation: {explanation}')
                else:
                    bot.send_photo(message.from_user.id, open(f'./images/{title}.{image.format}', 'rb'),
                                   f'name: {title} \nexplanation: {explanation}')

        elif 'www.youtube.com' in url:
            bot.send_message(message.from_user.id, url)
    else:
        bot.send_message(message.from_user.id, 'сегодняшнее фото ещё не загружено')


def photo_msg(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    today_button = types.KeyboardButton("фото дня")
    yesterday_button = types.KeyboardButton('вчерашнее фото дня')
    after_yesterday_button = types.KeyboardButton('позавчерашнее фото дня')
    back_button = types.KeyboardButton('⬅назад')
    markup.add(today_button, yesterday_button, after_yesterday_button, back_button)
    bot.send_message(message.chat.id, "выберите кнопку", reply_markup=markup)


def album(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    comets_button = types.KeyboardButton("кометы")
    nebulae_button = types.KeyboardButton("туманности")
    satellites_button = types.KeyboardButton("спутники")
    solar_system_button = types.KeyboardButton("солнечная система")
    stars_button = types.KeyboardButton("звёзды")
    back_button = types.KeyboardButton('⬅назад')
    markup.add(comets_button, nebulae_button, satellites_button, solar_system_button, stars_button, back_button)
    bot.send_message(message.chat.id, "выберите кнопку", reply_markup=markup)


def comets(message):
    if message.text == 'кометы':
        bot.send_message(message.chat.id, "список комет: \n"
                                          "1 Комета Чурюмова - Герасименко\n"
                                          "2 Комета Хейла - Боппа\n"
                                          "3 Комета Галлея\n"
                                          "4 Комета Холмса\n"
                                          "5 Комета Лавджоя\n"
                                          "6 Комета Темпеля\n"
                                          "7 Комета Вильда")
    if (str(message.text).split()[0]).lower() == 'комета':
        for comet in _comets:
            if message.text.lower() == comet:
                bot.send_photo(message.from_user.id, open(f'./images/comets/{comet}.jpg', 'rb'), comet)

    elif (message.text.isdigit()) and (int(message.text) - 1 < len(_comets)) and comets_btn:
        bot.send_photo(message.from_user.id, open(f'./images/comets/{_comets[int(message.text) - 1]}.jpg', 'rb'),
                       _comets[int(message.text) - 1])


def nebulae(message):
    if message.text == 'туманности':
        bot.send_message(message.chat.id, "список туманностей: \n"
                                          "1 Биполярная туманность\n"
                                          "2 Мерцающая туманность\n"
                                          "3 Туманность бабочка\n"
                                          "4 Туманность гантель\n"
                                          "5 Туманность кольцо\n"
                                          "6 Туманность кошачий глаз\n"
                                          "7 Туманность маленькая гантель\n"
                                          "8 Туманность медуза\n"
                                          "9 Туманность призрак Юпитера\n"
                                          "10 Туманность призрак\n"
                                          "11 Туманность светящийся глаз\n"
                                          "12 Туманность сова\n"
                                          "13 Туманность улитка\n"
                                          "14 Туманность череп\n"
                                          "15 Туманность Эскимос")
    if (str(message.text).split()[0]).lower() == 'туманность':
        for nebula in _nebulae:
            if message.text.lower() == nebula:
                bot.send_photo(message.from_user.id, open(f'./images/nebulae/{nebula}.jpg', 'rb'), nebula)

    elif (message.text.isdigit()) and (int(message.text) - 1 < len(_nebulae)) and nebulae_btn:
        bot.send_photo(message.from_user.id, open(f'./images/nebulae/{_nebulae[int(message.text) - 1]}.jpg', 'rb'),
                       _nebulae[int(message.text) - 1])


def solar(message):
    if message.text == 'солнечная система':
        bot.send_message(message.chat.id, "список планет солнечной системы:\n"
                                          "1 Меркурий\n"
                                          "2 Венера\n"
                                          "3 Земля\n"
                                          "4 Марс\n"
                                          "5 Юпитер\n"
                                          "6 Сатурн\n"
                                          "7 Уран\n"
                                          "8 Нептун")

    if message.text.lower() in _solar:
        for planet in _solar:
            if message.text.lower() == planet:
                bot.send_photo(message.from_user.id, open(f'./images/solar_system/{planet}.jpg', 'rb'))

    elif (message.text.isdigit()) and (int(message.text) - 1 < len(_solar)) and solar_btn:
        bot.send_photo(message.from_user.id, open(f'./images/solar_system/{_solar[int(message.text) - 1]}.jpg', 'rb'),
                       _solar[int(message.text) - 1])


def stars(message):
    if message.text.lower() == 'звёзды':
        bot.send_message(message.chat.id, 'звёзды:\n'
                                          '1 эридана\n'
                                          '2 ez водолея\n'
                                          '3 глизе 832\n'
                                          '4 глизе 876\n'
                                          '5 lhs 288\n'
                                          '6 процион\n'
                                          '7 солнце\n'
                                          '8 сириус\n'
                                          '9 проксима центавра')
    if message.text.lower() in _stars:
        for star in _stars:
            if message.text.lower() == star:
                bot.send_photo(message.from_user.id, open(f'./images/stars/{star}.jpg', 'rb'))

    elif (message.text.isdigit()) and (int(message.text) - 1 < len(_stars)) and stars_btn:
        bot.send_photo(message.from_user.id, open(f'./images/stars/{_stars[int(message.text) - 1]}.jpg', 'rb'),
                       _stars[int(message.text) - 1])


def satellites(message):
    if message.text == 'спутники':
        bot.send_message(message.chat.id, 'спутники:\n'
                                          'Земли: 1.1 Луна\n'
                                          '\n'
                                          'Марса: 2.1 Деймос, 2.2 Фобос\n'
                                          '\n'
                                          'Юпитера: 3.1 Амальтея, 3.2 Ананке, 3.3 Ганимед, 3.4 Гималия, 3.5 Европа,\n'
                                          '3.6 Ио, 3.7 Каллисто, 3.8 Карме, 3.9 Леда, 3.10 Лиситея, 3.11 Пасифе,\n'
                                          '3.11 Синопе, 3.12 Элара\n'
                                          '\n'
                                          'Сатурна: 4.1 Титан, 4.2 Япет, 4.3 Рея, 4.4 Тефия, 4.5 Диона, 4.6 Энцелад,\n'
                                          '4.7 Мимас, 4,8 Гиперион, 4.9 Феба, 4.10 Янус, 4.11 Эпиметей\n'
                                          '\n'
                                          'Урана: 5.1 Титания, 5.2 Оберон, 5.3 Ариэль, 5.4 Умбриэль, 5.5 Миранда,\n'
                                          '5.6 Пак, 5.7 Джульетта, 5.8 Порция, 5.9 Крессида, 5.10 Дездемона,\n'
                                          '5.11 Розалинда, 5.12 Белинда, 5.13 Корделия, 5.14 Офелия, 5.15 Бианка,\n'
                                          '5.16 Калибан, 5.17 Сикоракса, 5.18 Пердита, 5.19 Сетебос, 5.20 Стефано,\n'
                                          '5.21 Просперо, 5.22 Фердинанд, 5.23 Маб, 5.24 Купидон, 5.25 Маргарита\n'
                                          '\n'
                                          'Нептуна: 6.1 Тритон, 6.2 Нереида, 6.3 Ларисса, 6.4 Протей,\n'
                                          '6.5 Деспина, 6.6 Галатея, 6.7 Таласса, 6.8 Наяда, 6.9 Галимеда, 6.10 Псамафа')

    if message.text.lower() in _satellites:
        for satellite in _satellites:
            if message.text.lower() == satellite:
                bot.send_photo(message.from_user.id, open(f'./images/satellites/{satellite}.jpg', 'rb'))

    elif ('.' in message.text) and (int(message.text[0]) - 1 < len(_satellites)) and satellites_btn:
        try:
            bot.send_photo(message.from_user.id, open(
                f'./images/satellites/{_satellites[int(message.text[0]) - 1][int(message.text[2:]) - 1]}.jpg', 'rb'),
                           _satellites[int(message.text[0]) - 1][int(message.text[2:]) - 1])
        except Exception:
            print('wrong input')


if __name__ == '__main__':
    bot.infinity_polling()
