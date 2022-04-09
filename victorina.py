import logging

#  https://docs-python.ru/packages/biblioteka-python-telegram-bot-python/
from telegram import (
    Poll,
    ParseMode,
    KeyboardButton,
    KeyboardButtonPollType,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)

from telegram.ext import (
    Updater,
    CommandHandler,
    PollAnswerHandler,
    PollHandler,
    MessageHandler,
    Filters,
)

# подключение логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


#  ОПРЕДЕЛЕНИЕ ФУНКЦИЙ ОБРАТНОГО ВЫЗОВА
def start(update, _):
    #  Информация о том, что может сделать этот бот
    update.message.reply_text(
        'Введите `/poll` для участия в опросе, `/quiz` для участия в викторине или `/preview`'
        ' чтобы создать собственный опрос/викторину'
    )


def poll(update, context):
    #  Отправка заранее подготовленного опроса

    # Вопрос опроса и его ответы.
    questions = "Как дела?"
    answer = ["Нормально", "Хорошо", "Отлично", "Супер!"]
    # Отправляем опрос в чат
    message = context.bot.send_poll(
        update.effective_chat.id, questions, answer,
        is_anonymous=False, allows_multiple_answers=True,
    )
    # Сохраним информацию опроса в `bot_data` для последующего
    # использования в функции `receive_poll_answer`
    payload = {  # ключом словаря с данными будет `id` опроса
        message.poll.id: {
            "questions": questions,
            "message_id": message.message_id,
            "chat_id": update.effective_chat.id,
            "answers": 0,
        }
    }
    # сохранение промежуточных результатов в `bot_data`
    context.bot_data.update(payload)


def receive_poll_answer(update, context):
    #  Итоги опроса пользователей

    answer = update.poll_answer
    poll_id = answer.poll_id
    try:
        questions = context.bot_data[poll_id]["questions"]
    except KeyError:  # Это ответ на старый опрос
        return
    selected_options = answer.option_ids
    answer_string = ""
    # подсчет и оформление результатов
    for question_id in selected_options:
        if question_id != selected_options[-1]:
            answer_string += questions[question_id] + " и "
        else:
            answer_string += questions[question_id]
    context.bot.send_message(
        context.bot_data[poll_id]["chat_id"],
        f"{update.effective_user.mention_html()} => {answer_string}!",
        parse_mode=ParseMode.HTML,
    )
    # изменение промежуточных результатов в `bot_data`
    context.bot_data[poll_id]["answers"] += 1
    # Закрываем опрос после того, как проголосовали три участника
    if context.bot_data[poll_id]["answers"] == 3:
        context.bot.stop_poll(
            context.bot_data[poll_id]["chat_id"], context.bot_data[poll_id]["message_id"]
        )


def quiz(update, context):
    """Отправка заранее определенную викторину"""
    # Вопрос викторины и ответы
    questions = 'Сатурн'
    answer = ['Планета', 'Напиток', 'Марка машины', 'Версия windows']
    message = update.effective_message.reply_poll(
        questions, answer, type=Poll.QUIZ, correct_option_id=0
    )
    questions = 'Какая страна первой запустила спутник?'
    answer = ['СССР', 'США', 'Китай', 'Япония']
    message = update.effective_message.reply_poll(
        questions, answer, type=Poll.QUIZ, correct_option_id=0
    )

    questions = 'Кто является первой женщиной-космонавтом?'
    answer = ['Майли Сайрус', 'Элис Уолтон', 'Ада Лавлейс', 'Валентина Терешкова']
    message = update.effective_message.reply_poll(
        questions, answer, type=Poll.QUIZ, correct_option_id=3
    )

    questions = 'Как назывался корабль, на котором 12 апреля 1961 года Юрий Гагарин совершил первый полёт в космос?'
    answer = ['Союз', 'Восток', 'Север', 'Дружба']
    message = update.effective_message.reply_poll(
        questions, answer, type=Poll.QUIZ, correct_option_id=1
    )

    questions = 'Какой ученый является изобретателем космической ракеты?'
    answer = ['Королёв', 'Энштейн', 'Циолковский', 'Гей-Люсак']
    message = update.effective_message.reply_poll(
        questions, answer, type=Poll.QUIZ, correct_option_id=2
    )

    questions = 'Что в переводе с греческого означает "комета"?'
    answer = ['Взлёт веры', 'Небесный огонь', 'Хвостатая звезда', 'Око бога']
    message = update.effective_message.reply_poll(
        questions, answer, type=Poll.QUIZ, correct_option_id=2
    )

    questions = 'Какие планеты солнечной системы вращаются в направлении, противоположном Земле?'
    answer = ['Венера и Уран', 'Меркурий и Нептун', 'Марс и Юпитер', 'Меркурий и Уран']
    message = update.effective_message.reply_poll(
        questions, answer, type=Poll.QUIZ, correct_option_id=0
    )

    questions = 'Какие планеты солнечной системы вращаются в направлении, противоположном Земле?'
    answer = ['302км', '293км', '400км', '341км']
    message = update.effective_message.reply_poll(
        questions, answer, type=Poll.QUIZ, correct_option_id=0
    )

    questions = 'Что является причиной образования кратеров на Луне?'
    answer = ['Луноход', 'Метеориты', 'Инопланетяне', 'Спутники прилетевшие с Земли']
    message = update.effective_message.reply_poll(
        questions, answer, type=Poll.QUIZ, correct_option_id=1
    )

    questions = 'Кто стал первым "космическим туристом"?'
    answer = ['Деннис Тито', 'Рой Гриффин', 'Александр Ефремов', 'Джосеф Окс']
    message = update.effective_message.reply_poll(
        questions, answer, type=Poll.QUIZ, correct_option_id=1
    )

    questions = 'Как звали человека, который первым высадился на Луну?'
    answer = ['Деннис Тито', 'Рой Гриффин', 'Нил Армстронг', 'Джосеф Окс']
    message = update.effective_message.reply_poll(
        questions, answer, type=Poll.QUIZ, correct_option_id=2
    )

    questions = 'Как называется ближайшая к Солнцу планета?'
    answer = ['Марс', 'Венера', 'Уран', 'Меркурий']
    message = update.effective_message.reply_poll(
        questions, answer, type=Poll.QUIZ, correct_option_id=3
    )

    # Сохраним промежуточные данные викторины в `bot_data` для использования в `receive_quiz_answer`
    payload = {  # ключом словаря с данными будет `id` викторины
        message.poll.id: {"chat_id": update.effective_chat.id, "message_id": message.message_id}
    }
    context.bot_data.update(payload)


def receive_quiz_answer(update, context):
    """Закрываем викторину после того, как ее прошли три участника"""
    # бот может получать обновления уже закрытого опроса, которые уже не волнуют
    if update.poll.is_closed:
        return
    if update.poll.total_voter_count == 1:
        try:
            quiz_data = context.bot_data[update.poll.id]
        except KeyError:  # Это означает, что это ответ из старой викторины
            return
        context.bot.stop_poll(quiz_data["chat_id"], quiz_data["message_id"])


def preview(update, _):
    """Позволяет создать викторину или опрос пользователям чата"""
    # При использовании, без указания типа, позволяет пользователю
    # выбрать то, что он хочет создать - викторину или опрос
    button = [[KeyboardButton("Нажми меня!", request_poll=KeyboardButtonPollType())]]
    message = "Нажмите кнопку, для предварительного просмотра вашего опроса"
    # использование `one_time_keyboard=True` скрывает клавиатуру
    update.effective_message.reply_text(
        message, reply_markup=ReplyKeyboardMarkup(button, one_time_keyboard=True)
    )


def receive_poll(update, _):
    """
        При получении ответа на пользовательский опрос/викторину,
        отвечаем на него закрытым опросом, копируя полученный опрос
    """
    actual_poll = update.effective_message.poll
    # Нужно только `question` и `options`, все остальные
    # параметры не имеют значения для закрытого опроса
    update.effective_message.reply_poll(
        question=actual_poll.question,
        options=[o.text for o in actual_poll.options],
        # с `is_closed=True` опрос/викторина немедленно закрывается
        is_closed=True,
        reply_markup=ReplyKeyboardRemove(),
    )


def help_handler(update, _):
    """Отображение справочного сообщения"""
    update.message.reply_text("Используйте /quiz, /poll или /preview для тестирования этого бота.")


if __name__ == '__main__':
    updater = Updater("5273072249:AAF2OLkMgDNCUtEhdAftkoNhRRCDwfEyn9k")
    dispatcher = updater.dispatcher

    # определяем соответствующие обработчики
    dispatcher.add_handler(CommandHandler('start', start))
    # команда `/pool`
    dispatcher.add_handler(CommandHandler('poll', poll))
    # обработчик ответа на опрос
    dispatcher.add_handler(PollAnswerHandler(receive_poll_answer))
    # команда `/quiz`
    dispatcher.add_handler(CommandHandler('quiz', quiz))
    # обработчик ответа на викторину
    dispatcher.add_handler(PollHandler(receive_quiz_answer))
    # команда `/preview`
    dispatcher.add_handler(CommandHandler('preview', preview))
    # обработчик создания пользовательского опроса/викторины
    dispatcher.add_handler(MessageHandler(Filters.poll, receive_poll))
    dispatcher.add_handler(CommandHandler('help', help_handler))

    # Запуск бота
    updater.start_polling()
    updater.idle()

