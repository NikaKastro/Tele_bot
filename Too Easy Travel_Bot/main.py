import telebot

easy_travel_bot = telebot.TeleBot("5486223307:AAF5Eybbh41RAJtunGck0UOWkmCWAh4zS1k")


@easy_travel_bot.message_handler(commands=['start'])
def start(message):
    easy_travel_bot.send_message(message.chat.id, "Привет", parse_mode="html")


@easy_travel_bot.message_handler(commands=['help'])
def help(message):
    easy_travel_bot.send_message(message.chat.id, "Вы можете ввести следующие "
                                                  "команды:\n/start\n/help\n/lowprice\n"
                                                  "/highprice\n/bestdeal\n/history", parse_mode="html")


@easy_travel_bot.message_handler(commands=['lowprice'])
def lowprice(message):
    easy_travel_bot.send_message(message.chat.id, "В каком городе искать самый дешевый отель?", parse_mode="html")


@easy_travel_bot.message_handler(commands=['highprice'])
def highprice(message):
    easy_travel_bot.send_message(message.chat.id, "В каком городе искать самый дорогой отель?", parse_mode="html")


@easy_travel_bot.message_handler(commands=['bestdeal'])
def bestdeal(message):
    easy_travel_bot.send_message(message.chat.id, "В каком городе искать оптимальный отель?", parse_mode="html")


@easy_travel_bot.message_handler(commands=['history'])
def history(message):
    easy_travel_bot.send_message(message.chat.id, "Посмотрим историю поиска?", parse_mode="html")


easy_travel_bot.polling(none_stop=True, interval=0)
