import telebot
import re
from location_hotels_search import make_location_answer, make_hotel_answer
from typing import Any

from datetime import datetime
from telebot import types

easy_travel_bot = telebot.TeleBot("5486223307:AAF5Eybbh41RAJtunGck0UOWkmCWAh4zS1k")
user_params_search = {}


@easy_travel_bot.message_handler(commands=['start'])
def start(message: Any) -> None:
    """
    Отправляет пользователю приветственное сообщение.
    :type message: object
    """
    easy_travel_bot.send_message(message.chat.id, "Too Easy Travel -  номер один в сфере организации самых разных "
                                                  "туров.&#127758\n "
                                                  "С нами, вы сможете найти выгодные предложения "
                                                  "различных хостелов и отелей мира!\n А главное, прямо здесь и "
                                                  "сейчас!&#128522\n "
                                                  "Выберите подходящую команду из меню нашего бота "
                                                  "или воспользуйтесь командой /help", parse_mode="html")


@easy_travel_bot.message_handler(commands=['help'])
def help(message: Any) -> None:
    """
    Отправляет пользователю инструкции и ссылки на соответствующие команды.
    :rtype: object
    """
    easy_travel_bot.send_message(message.chat.id, "Вы можете ввести следующие "
                                                  "команды:\n/start - расскажет о нас.&#127796\n/help "
                                                  "- покажет, что я умею.&#128578\n/lowprice - "
                                                  "для поиска самой выгодной цены в городе.&#128176\n"
                                                  "/highprice - когда хочется немного роскоши.&#128521\n/bestdeal "
                                                  "-  самая лучшая цена и расположение.&#128526\n/history - "
                                                  "а тут можно найти всё, что искали ранее.", parse_mode="html")


@easy_travel_bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def lowprice_highprice(message: Any) -> None:
    """
    Добавляет параметры в словарь для поиска и отравляет пользователю сообщение для следующего шага диалога.
    :rtype: object
    """
    if message.text == "/lowprice":
        user_params_search["sortOrder"] = "PRICE"
        if "priceMin" in user_params_search:
            del user_params_search["priceMin"]
            del user_params_search["priceMax"]
    elif message.text == "/bestdeal":
        user_params_search["sortOrder"] = "DISTANCE_FROM_LANDMARK"
    else:
        user_params_search["sortOrder"] = "PRICE_HIGHEST_FIRST"
        if "priceMin" in user_params_search:
            del user_params_search["priceMin"]
            del user_params_search["priceMax"]
    easy_travel_bot.send_message(message.chat.id, "В каком городе искать отели?", parse_mode="html")
    easy_travel_bot.register_next_step_handler(message, get_city)


@easy_travel_bot.message_handler(commands=['history'])
def history(message: Any) -> None:
    easy_travel_bot.send_message(message.chat.id, "Посмотрим историю поиска?", parse_mode="html")


@easy_travel_bot.message_handler(content_types=["text"])
def get_text_messages(message: Any)-> None:
    """
    Отправляет пользователю сообщение о необходимости ввести команду. Направляется в случае некорректного ввода.
    :rtype: object
    """
    easy_travel_bot.send_message(message.chat.id, "Я не понимаю что мне делать&#128580,\n"
                                                  "выберите команду, пожалуйста.&#128522", parse_mode="html")


@easy_travel_bot.callback_query_handler(func=lambda call: True)
def callback_worker(call: Any) -> None:
    """
    Обрабатывает ввод пользователя с клавиатуры.
    :rtype: object
    """
    if call.data == "yes":
        easy_travel_bot.send_message(call.message.chat.id, "Сколько фотографий отеля выводить? "
                                                           "(максимум 10)", parse_mode="html")
        easy_travel_bot.register_next_step_handler(call.message, get_count_photo)

    elif call.data == "no":
        easy_travel_bot.send_message(call.message.chat.id, "Хорошо. Ищем без фотографий.&#128146",
                                     parse_mode="html")
        if "photo" in user_params_search:
            del user_params_search["photo"]
        send_user_hotels(user_params_search, call.message)
    elif re.fullmatch(r"\d+", call.data):
        user_params_search["destinationId"] = call.data
        print(user_params_search)
        if user_params_search.get("sortOrder") == "DISTANCE_FROM_LANDMARK":
            get_range_price(call.message)
        else:
            get_count_hotel(call.message)
    elif call.data == "cancel":
        easy_travel_bot.send_message(call.message.chat.id, "Жаль, что не удалось помочь.&#128532\n "
                                                           "Вы можете попробовать еще раз!&#127757", parse_mode="html")
        return


def get_city(message: Any) -> None:
    """
    Проверяет полученный от пользователя город на корректность ввода,
    в случае успешной проверки, вызывает функцию поиска локации.
    Отправляет пользователю сообщения в случае возникновения ошибок.
    :rtype: object
    """
    if message.text.replace("-", "").isalpha():
        user_city = make_location_answer(message.text)
        if user_city == 'locations_not_found':
            easy_travel_bot.send_message(message.chat.id, "По запросу ничего не найдено.&#128532\n"
                                                          "Возможно вы допустили ошибку в названии?\n "
                                                          "Введите название еще раз.", parse_mode="html")
            easy_travel_bot.register_next_step_handler(message, get_city)
        elif user_city == 'bad_request':
            easy_travel_bot.send_message(message.chat.id, "Не могу получить ответ от сервера.&#128532\n"
                                                          "Попробуйте воспользоваться поиском позже.",
                                         parse_mode="html")
        elif user_city == 'bad_list_value':
            easy_travel_bot.send_message(message.chat.id, "Что-то пошло не так на сервере.\n"
                                                          "Попробуйте позже.", parse_mode="html")
        else:
            if len(user_city) > 1:
                get_callback_city(user_city, message)
            else:
                user_params_search["destinationId"] = user_city[0].get("destinationId")
                easy_travel_bot.register_next_step_handler(message, get_count_hotel)
    else:
        easy_travel_bot.send_message(message.chat.id,
                                     "Название города должно состоять только из букв <b>А-Яя</b> и &#10134\n"
                                     "Давайте попробуем еще раз. Введите заново команду и город.",
                                     parse_mode="html")


def get_range_price(message: Any) -> None:
    """
    Запрашивает диапазон цен от пользователя.
    :rtype: object
    """
    easy_travel_bot.send_message(message.chat.id, "Введите диапазон цен от 0 до 10 000 за одну ночь. "
                                                  "В формате NN-NN+", parse_mode="html")
    easy_travel_bot.register_next_step_handler(message, get_distance)


def get_distance(message: Any) -> None:
    """
    Проверяет диапазон цен, запрашивает расстояние от центра.
    :rtype: object
    """
    if len(message.text.split(sep="-")) == 2 and message.text.split(sep="-")[0].isdigit() and \
            message.text.split(sep="-")[1].isdigit():
        user_range = message.text.split(sep="-")
        user_params_search["priceMin"] = user_range[0]
        user_params_search["priceMax"] = user_range[1]
        if int(user_range[0]) >= 0 and int(user_range[1]) <= 10000:
            easy_travel_bot.send_message(message.chat.id, "На каком расстоянии от центра искать?", parse_mode="html")
            easy_travel_bot.register_next_step_handler(message, check_distance)
        else:
            easy_travel_bot.send_message(message.chat.id, "Цена должна быть в диапазоне от 0 до 10 000. "
                                                          "Введите диапазон заново.", parse_mode="html")
            easy_travel_bot.register_next_step_handler(message, get_distance)
            return
    else:
        easy_travel_bot.send_message(message.chat.id, f"Диапазон цен должен быть целыми числами, разделяться ,-, "
                                                      "Введите диапазон заново.", parse_mode="html")
        easy_travel_bot.register_next_step_handler(message, get_distance)
        return


def check_distance(message: Any) -> None:
    """
    Проверяет дистанцию на корректный ввод.
    :rtype: object
    """
    try:
        float(message.text)

        get_count_hotel(message)
    except ValueError:
        easy_travel_bot.send_message(message.chat.id, "Расстояние должно быть числом. Введите ещё раз.",
                                     parse_mode="html")
        easy_travel_bot.register_next_step_handler(message, check_distance)
        return


def get_count_hotel(message: Any) -> None:
    """
    Запрашивает количество отелей у пользователя.
    :rtype: object
    """
    easy_travel_bot.send_message(message.chat.id, "Сколько отелей вывести в результате? Максимум 10.",
                                 parse_mode="html")
    easy_travel_bot.register_next_step_handler(message, get_check_in)


def get_check_in(message: Any) -> None:
    """
    Проверяет количество отлей и запрашивает дату заезда.
    :rtype: object
    """
    if message.text.isdigit() and 0 < int(message.text) <= 10:
        user_params_search["pageSize"] = message.text
        easy_travel_bot.send_message(message.chat.id, "Введите дату <b>заезда</b> в формате YYYY-MM-DD.",
                                     parse_mode="html")
        easy_travel_bot.register_next_step_handler(message, get_check_out)

    else:
        easy_travel_bot.send_message(message.chat.id, "Количество отелей должно быть целым числом и не более 10. "
                                                      "Введите число заново.", parse_mode="html")
        easy_travel_bot.register_next_step_handler(message, get_check_in)
        return


def get_check_out(message: Any) -> None:
    """
        Запрашивает дату отъезда. При проверке даты отправляет пользователю соответствующие сообщения.
        :rtype: object
        """
    if check_date(message.text) is True:
        if datetime.now() <= datetime.strptime(message.text, "%Y-%m-%d"):
            user_params_search["checkIn"] = message.text
            easy_travel_bot.send_message(message.chat.id, "Введите дату <b>отъезда</b> в формате YYYY-MM-DD.",
                                         parse_mode="html")
            easy_travel_bot.register_next_step_handler(message, check_check_out)
        else:
            easy_travel_bot.send_message(message.chat.id, "Дата заезда должна быть равной сегодняшнему числу "
                                                          "или быть позже. "
                                                          "Введите дату снова.", parse_mode="html")
            easy_travel_bot.register_next_step_handler(message, get_check_out)
    else:
        easy_travel_bot.send_message(message.chat.id, "Неверный формат даты. "
                                                      "Введите дату снова.", parse_mode="html")
        easy_travel_bot.register_next_step_handler(message, get_check_out)
        return


def check_check_out(message: Any) -> None:
    """
        Проверяет дату отъезда и отправляет пользователю соответствующие сообщения.
        :rtype: object
        """
    if check_date(message.text) is True:
        if datetime.strptime(user_params_search.get("checkIn"), "%Y-%m-%d") \
                < datetime.strptime(message.text, "%Y-%m-%d"):
            user_params_search["checkOut"] = message.text
            get_callback_photo(message)

        else:
            easy_travel_bot.send_message(message.chat.id, "Дата отъезда не может быть раньше или равна дате заезда. "
                                                          "Введите дату снова.", parse_mode="html")
            easy_travel_bot.register_next_step_handler(message, check_check_out)
    else:
        easy_travel_bot.send_message(message.chat.id, "Неверный формат даты. "
                                                      "Введите дату снова.", parse_mode="html")
        easy_travel_bot.register_next_step_handler(message, check_check_out)
        return


def get_callback_photo(message: Any) -> None:
    """
    Отправляет пользователю клавиатуру с вопросом о необходимости поиска фотографий.
    :rtype: object
    """
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Да', callback_data='yes'))
    keyboard.add(types.InlineKeyboardButton(text='Нет', callback_data='no'))
    question = "Выводить фотографии найденных отелей?"
    easy_travel_bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)


def get_callback_city(user_city, message: Any) -> None:
    """
    Отправляет пользователю клавиатуру с найденными городами.
    :rtype: object
    """
    keyboard = types.InlineKeyboardMarkup()
    for city in user_city:
        keyboard.add(types.InlineKeyboardButton(text=city.get('name'), callback_data=city.get('destinationId')))
    keyboard.add(telebot.types.InlineKeyboardButton(text='Выйти. Подходящего города нет.',
                                                    callback_data='cancel'))
    question = "Нашлось несколько вариантов.&#128521 Уточните поиск."
    easy_travel_bot.send_message(message.from_user.id, text=question, reply_markup=keyboard, parse_mode="html")


def get_count_photo(massage_count_photo: Any) -> None:
    """
    Получает и проверяет количество фотографий.
    :rtype: object
    """
    if massage_count_photo.text.isdigit() and int(massage_count_photo.text) <= 10:
        user_params_search["photo"] = massage_count_photo.text
        send_user_hotels(user_params_search, massage_count_photo)
    else:
        easy_travel_bot.send_message(massage_count_photo.chat.id, "Количество фотографий должно быть целым числом "
                                                                  "и не более 10. Попробуйте заново.",
                                     parse_mode="html")
        get_callback_photo(massage_count_photo)
        return


def send_user_hotels(user_search: dict, message: Any) -> None:
    """
    Формирует и отправляет результат пользователю.
    :rtype: object
    """
    hotels_list = make_hotel_answer(user_search)
    print(hotels_list)
    if hotels_list == 'bad_request':
        easy_travel_bot.send_message(message.chat.id, "Не могу получить ответ от сервера.&#128532\n"
                                                      "Попробуйте позже.", parse_mode="html")
    elif hotels_list == 'hotels_not_found':
        easy_travel_bot.send_message(message.chat.id, "К сожалению, в этом городе нет вариантов размещения.&#128532\n"
                                                      "Попробуйте заново. Выберите другую локацию или даты проживания.",
                                     parse_mode="html")
    else:
        easy_travel_bot.send_message(message.chat.id, "Посмотрим какие отели нашлись:", parse_mode="html")
        for hotel in hotels_list:
            name = hotel.get("name")
            star_rating = "&#11088" * int(hotel.get("starRating"))
            address = hotel.get("address")
            distance_from_centre = hotel.get("distanceFromCentre")
            price = hotel.get("price")
            total_price = hotel.get("totalPrice")
            send = f"Название: {name}\nРейтинг: {star_rating}\nАдрес: {address}\n" \
                   f"Расстояние от центра: {distance_from_centre}\n" \
                   f"Цена за одну ночь: {price}\nОбщая стоимость за всё время пребывания: {total_price}"
            easy_travel_bot.send_message(message.chat.id, send, parse_mode="html")
            if "photo" in hotel:
                for item in hotel.get("photo").values():
                    easy_travel_bot.send_message(message.chat.id, item, parse_mode="html")


def check_date(message_date: Any) -> bool:
    """
    Проверяет дату на соответствие формату.
    :rtype: object
    """
    try:
        if message_date != datetime.strptime(message_date, "%Y-%m-%d").strftime('%Y-%m-%d'):
            raise ValueError
        return True
    except ValueError:
        return False


easy_travel_bot.polling(none_stop=True, interval=0)
