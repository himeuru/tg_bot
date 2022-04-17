import datetime
import math
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

STATE = None
BIRTH_YEAR = 1
BIRTH_MONTH = 2
BIRTH_DAY = 3


def start(update, context):
    first_name = update.message.chat.first_name
    update.message.reply_text(f"Привет, {first_name}!")
    start_getting_birthday_info(update, context)


def start_getting_birthday_info(update, context):
    global STATE
    STATE = BIRTH_YEAR
    update.message.reply_text(
        f"Биоритм — это циклические явления в жизнедеятельности любого живого организма. У человека их три: физический,"
        f" эмоциональный и интеллектуальный. Наличие биоритмов не зависит от расы, национальности, социального положения"
        f" и места нахождения человека. Их количество и продолжительность едины для всех."
        f" Кроме того, все ритмы человека связаны со сменой дня и ночи. \nИзучение биологических ритмов имеет важное"
        f" практическое значение для медицины, так как реакция человека на лечебно-профилактические процедуры, а также"
        f" на действие препаратов может отличаться в зависимости от того, на какой период они приходятся. \n \n"
        f"Для космического анализа твоего биоритма, мне нужно узнать твой год рождения, так какой же он...? ")


def received_birth_year(update, context):
    global STATE

    try:
        today = datetime.date.today()
        year = int(update.message.text)
        if year > today.year:
            raise ValueError("Ошибка!")
        context.user_data['birth_year'] = year
        update.message.reply_text(f"Хорошо, теперь мне нужно знать месяц (в численной форме)")
        STATE = BIRTH_MONTH
    except:
        update.message.reply_text("Забавно, но кажись это не так...")


def received_birth_month(update, context):
    global STATE
    try:
        today = datetime.date.today()
        month = int(update.message.text)
        if month > 12 or month < 1:
            raise ValueError("Ошибка!")
        context.user_data['birth_month'] = month
        update.message.reply_text(f"Здорово! И теперь день...")
        STATE = BIRTH_DAY
    except:
        update.message.reply_text("Забавно, но кажись это не так...")


def received_birth_day(update, context):
    global STATE
    try:
        today = datetime.date.today()
        dd = int(update.message.text)
        yyyy = context.user_data['birth_year']
        mm = context.user_data['birth_month']
        birthday = datetime.date(year=yyyy, month=mm, day=dd)
        if today - birthday < datetime.timedelta(days=0):
            raise ValueError("Ошибка!")
        context.user_data['birthday'] = birthday
        STATE = None
        update.message.reply_text(f'Хорошо, ты родился в {birthday},'
                                  f' чтобы узнать свои биоритмы и провести их анализ напиши мне команду /biorhythm')
    except:
        update.message.reply_text("Забавно, но кажись это не так...")


def text(update, context):
    global STATE
    if STATE == BIRTH_YEAR:
        return received_birth_year(update, context)
    if STATE == BIRTH_MONTH:
        return received_birth_month(update, context)
    if STATE == BIRTH_DAY:
        return received_birth_day(update, context)


def biorhythm(update, context):
    print("Окей")
    user_biorhythm = calculate_biorhythm(
        context.user_data['birthday'])
    update.message.reply_text(f"Физический: {user_biorhythm['phisical']}")
    update.message.reply_text(f"Эмоциональный: {user_biorhythm['emotional']}")
    update.message.reply_text(f"Интеллектуальный: {user_biorhythm['intellectual']}")


def calculate_biorhythm(birthdate):
    today = datetime.date.today()
    delta = today - birthdate
    days = delta.days
    phisical = math.sin(2 * math.pi * (days / 23))
    emotional = math.sin(2 * math.pi * (days / 28))
    intellectual = math.sin(2 * math.pi * (days / 33))
    biorhythm = {}
    biorhythm['phisical'] = int(phisical * 10000) / 100
    biorhythm['emotional'] = int(emotional * 10000) / 100
    biorhythm['intellectual'] = int(intellectual * 10000) / 100
    biorhythm['phisical_critical_day'] = (phisical == 0)
    biorhythm['emotional_critical_day'] = (emotional == 0)
    biorhythm['intellectual_critical_day'] = (intellectual == 0)
    return biorhythm


def main():
    TOKEN = "5273072249:AAF2OLkMgDNCUtEhdAftkoNhRRCDwfEyn9k"
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("biorhythm", biorhythm))
    dispatcher.add_handler(MessageHandler(Filters.text, text))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
