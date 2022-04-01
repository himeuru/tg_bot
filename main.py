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
    print('callback to:', message.chat.id)
    global url_for_date, info_time, info_exp, info_id, info_name
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
    elif message.text == 'фото':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        today_button = types.KeyboardButton("фото дня")
        yesterday_button = types.KeyboardButton('вчерашнее фото дня')
        after_yesterday_button = types.KeyboardButton('позавчерашнее фото дня')
        back_button = types.KeyboardButton('⬅назад')
        markup.add(today_button, yesterday_button, after_yesterday_button, back_button)
        bot.send_message(message.chat.id, "выберите кнопку", reply_markup=markup)
    elif 'фото дня' in message.text:
        if message.text == 'фото дня':
            url_for_date = f'{api_url}&date={datetime.now().strftime("%Y-%m-%d")}'

            time = (datetime.now())
            sort_time = [str(time)[:-16].split('-'),  str(info_time).split('-')]
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
            url_for_date = f'{api_url}&date={(datetime.now()-timedelta(days=1)).strftime("%Y-%m-%d")}'
        elif message.text == 'позавчерашнее фото дня':
            url_for_date = f'{api_url}&date={(datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")}'

        response = requests.get(url_for_date)
        response.raise_for_status()
        data = response.json()
        url = data['url']
        title = data['title']
        explanation = data['explanation']
        print(url)
        if 'www.youtube.com' not in url:
            image_response = requests.get(url)

            image = Image.open(BytesIO(image_response.content))

            if not image_dir.exists():
                os.mkdir(image_dir)
            image.save(image_dir / f'{title}.{image.format}', image.format)

            image = Image.open(BytesIO(image_response.content))
            if image:
                print('image success')
                if len(explanation) > 900:
                    for i in range(len(explanation), 0, -1):
                        if str(explanation)[i - 1] == '.' and i <= 1000:
                            explanation = explanation[:i]
                            break
                    bot.send_photo(message.from_user.id, open(f'./images/{title}.{image.format}', 'rb'),
                                   f'name: {title} \nexplanation: {explanation}')
                else:
                    bot.send_photo(message.from_user.id, open(f'./images/{title}.{image.format}', 'rb'),
                               f'name: {title} \nexplanation: {explanation}')

        else:
            bot.send_message(message.from_user.id, url)

    elif message.text == '⬅назад':
        start(message)
    elif message.text == 'викторина':
        bot.send_message(message.chat.id, 'в разработке')
    elif message.text == 'альбом':
        album(message)
    elif message.text == 'мой опыт':
        bot.send_message(message.chat.id, f'у вас {int(info_exp)} опыта')

    elif message.text == 'кометы' or message.text.lower() in _comets:
        comets(message)
    elif message.text == 'туманности' or message.text.lower() in _nebulae:
        nebulae(message)
    elif message.text == 'спутники' or message.text.lower() in _satellites:
        satellites(message)
    elif message.text == 'солнечная система' or message.text.lower() in _solar:
        solar(message)
    elif message.text == 'звёзды' or message.text.lower() in _stars:
        stars(message)


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
                                          "Комета Чурюмова - Герасименко\n"
                                          "Комета Хейла - Боппа\n"
                                          "Комета Галлея\n"
                                          "Комета Холмса\n"
                                          "Комета Лавджоя\n"
                                          "Комета Темпеля\n"
                                          "Комета Вильда")
    if (str(message.text).split()[0]).lower() == 'комета':
        for comet in _comets:
            if message.text.lower() == comet:
                bot.send_photo(message.from_user.id, open(f'./images/comets/{comet}.jpg', 'rb'))


def nebulae(message):
    if message.text == 'туманности':
        bot.send_message(message.chat.id, "список туманностей: \n"
                                          "Биполярная туманность\n"
                                          "Мерцающая туманность\n"
                                          "Туманность бабочка\n"
                                          "Туманность гантель\n"
                                          "Туманность кольцо\n"
                                          "Туманность кошачий глаз\n"
                                          "Туманность маленькая гантель\n"
                                          "Туманность медуза\n"
                                          "Туманность призрак Юпитера\n"
                                          "Туманность призрак\n"
                                          "Туманность светящийся глаз\n"
                                          "Туманность сова\n"
                                          "Туманность улитка\n"
                                          "Туманность череп\n"
                                          "Туманность Эскимос")
    if (str(message.text).split()[0]).lower() == 'туманность':
        for nebula in _nebulae:
            if message.text.lower() == nebula:
                bot.send_photo(message.from_user.id, open(f'./images/nebulae/{nebula}.jpg', 'rb'))


def solar(message):
    if message.text == 'солнечная система':
        bot.send_message(message.chat.id, "список планет солнечной системы:\n"
                                          "Меркурий\n"
                                          "Венера\n"
                                          "Земля\n"
                                          "Марс\n"
                                          "Юпитер\n"
                                          "Сатурн\n"
                                          "Уран\n"
                                          "Нептун")

    if message.text.lower() in _solar:
        for planet in _solar:
            if message.text.lower() == planet:
                bot.send_photo(message.from_user.id, open(f'./images/solar_system/{planet}.jpg', 'rb'))


def stars(message):
    if message.text.lower() == 'звёзды':
        bot.send_message(message.chat.id, 'звёзды:\n'
                                          'эридана\n'
                                          'ez водолея\n'
                                          'глизе 832\n'
                                          'глизе 876\n'
                                          'lhs 288\n'
                                          'процион\n'
                                          'солнце\n'
                                          'сириус\n'
                                          'проксима центавра')
    if message.text.lower() in _stars:
        for star in _stars:
            if message.text.lower() == star:
                bot.send_photo(message.from_user.id, open(f'./images/stars/{star}.jpg', 'rb'))


def satellites(message):
    if message.text == 'спутники':
        bot.send_message(message.chat.id, 'спутники:\n'
                                          'Земли: Луна\n'
                                          '\n'
                                          'Марса: Деймос, Фобос\n'
                                          '\n'
                                          'Юпитера: Амальтея, Ананке, Ганимед, Гималия, Европа,\n'
                                          'Ио, Каллисто, Карме, Леда, Лиситея, Пасифе, Синопе, Элара,\n'
                                          'Сатурна: Титан, Япет, Рея, Тефия, Диона, Энцелад, Мимас,\n'
                                          'Гиперион, Феба, Янус, Эпиметей\n'
                                          '\n'
                                          'Урана: Титания, Оберон, Ариэль, Умбриэль, Миранда, Пак,\n'
                                          'Джульетта, Порция, Крессида, Дездемона, Розалинда, Белинда,\n'
                                          'Корделия, Офелия, Бианка, Калибан, Сикоракса, Пердита,\n'
                                          'Сетебос, Стефано, Просперо, Фердинанд, Маб, Купидон, Маргарита\n'
                                          '\n'
                                          'Нептуна: Тритон, Нереида, Ларисса, Протей, Деспина, Галатея,\n'
                                          'Таласса, Наяда, Галимеда, Псамафа')

    if message.text.lower() in _satellites:
        for satellite in _satellites:
            if message.text.lower() == satellite:
                bot.send_photo(message.from_user.id, open(f'./images/satellites/{satellite}.jpg', 'rb'))


if __name__ == '__main__':
    bot.infinity_polling()
