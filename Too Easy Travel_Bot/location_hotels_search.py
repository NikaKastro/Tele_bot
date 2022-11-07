import requests
import json
import logging
from typing import Optional, Union
from datetime import datetime

logging.basicConfig(filename="bad_request.log", level=logging.INFO, encoding="utf-8")

X_RAPIDAPI_KEY = ?


def location_search(user_city: dict) -> Optional[dict]:
    """
    Функция для поиска города по названию.
    :param user_city: строка - название города.
    :return: данные в формате json.
    """
    url = "https://hotels4.p.rapidapi.com/locations/v2/search"
    headers = {
        "X-RapidAPI-Key": X_RAPIDAPI_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }
    querystring = {"query": user_city, "locale": "ru_RU",
                   "currency": "USD"}
    return api_request(url, querystring, headers)


def hotels_search(user_params_search: dict) -> Optional[dict]:
    """
    Функция для поиска отелей в указанном пользователем городе.
    :param user_params_search: параметры поиска.
    :return:  данные в формате json.
    """
    url = "https://hotels4.p.rapidapi.com/properties/list"
    querystring = {"destinationId": "118894", "pageNumber": "1", "pageSize": "5", "checkIn": "2022-09-16",
                   "checkOut": "2022-09-17", "adults1": "1", "sortOrder": "PRICE", "locale": "ru_RU", "currency": "USD"}
    headers = {
        "X-RapidAPI-Key": X_RAPIDAPI_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }
    querystring.update(user_params_search)

    return api_request(url, querystring, headers)


def photos_search(id_hotel: dict) -> Optional[dict]:
    """
        Функция для поиска фотографий отеля.
        :param id_hotel: параметры поиска.
        :return:  данные в формате json.
        """
    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

    querystring = {"id": id_hotel}

    headers = {
        "X-RapidAPI-Key": X_RAPIDAPI_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }
    return api_request(url, querystring, headers)


def api_request(url: str, querystring: dict, headers: dict) -> Optional[dict]:
    """
    Функция для отправки запроса к API.
    :param url: адрес страницы запроса.
    :param querystring: параметры запроса.
    :param headers: конфигурация доступа к API.
    :return: ответ от сервера.
    """
    try:
        response = requests.request("GET", url, headers=headers, params=querystring, timeout=20)
        if response.status_code == 200:
            result = json.loads(response.text)
        else:
            result = None
    except requests.Timeout as time_end:
        logging.exception(time_end)
        result = None
    except requests.RequestException as er:
        logging.exception(er)
        result = None
    return result


def make_location_answer(message: Optional[dict]) -> Union[str, list]:
    """
    Функция для подготовки ответа пользователю по найденным городам.
    :param message: параметры запроса.
    :return: строка с указанием вида ошибки или список найденных городов по запросу.
    """
    location_answer = location_search(message)
    try:
        if location_answer is None:
            return 'bad_request'
        elif len(location_answer.get('suggestions')[0].get('entities')) < 1:
            return 'locations_not_found'
        else:
            answer_user_list = []
            for item in location_answer.get('suggestions')[0].get('entities'):
                answer_dict = dict()
                answer_dict["destinationId"] = item["destinationId"]
                answer_dict["name"] = item["name"]
                answer_user_list.append(answer_dict)
            return answer_user_list
    except AttributeError as log:
        logging.error(str(log))
        return 'bad_list_value'


def make_hotel_answer(message: dict) -> Union[str, list]:
    """
    Функция для подготовки ответа пользователю по найденным отелям в городе.
    :param message: параметры запроса.
    :return: строка с указанием вида ошибки или список найденных отелей по запросу.
    """
    hotels = hotels_search(message)
    count_day = get_count_day(message)
    if hotels is None:
        return 'bad_request'
    elif len(hotels.get("data").get('body').get('searchResults').get('results')) < 1:
        return 'hotels_not_found'
    else:
        answer_hotels = []
        count_photo = message.get("photo")
        try:
            for item in hotels.get("data").get('body').get('searchResults').get('results'):
                if message.get("distance") is not None:
                    hotel_distance = item.get("landmarks")[0].get("distance").split(" ")[0].replace(",", ".")
                    if float(message.get("distance")) < float(hotel_distance):
                        continue
                answer_dict = dict()
                answer_dict["name"] = item.get("name")
                answer_dict["starRating"] = item.get("starRating")
                answer_dict["address"] = item.get("address").get("streetAddress")
                answer_dict["distanceFromCentre"] = item.get("landmarks")[0].get("distance")
                answer_dict["price"] = item.get('ratePlan').get("price").get("current")
                total_price = round(item.get('ratePlan').get("price").get("exactCurrent"), 0) * count_day
                answer_dict["totalPrice"] = str(total_price)+"$"
                if count_photo is not None:
                    photos = photos_search(item.get("id"))
                    print(photos)
                    photos_dict = dict()
                    for photo in range(int(count_photo)):
                        photos_dict["Url " + str(photo)] = photos.get("hotelImages")[photo].get("baseUrl")\
                            .replace("{size}", "z")
                    answer_dict["photo"] = photos_dict
                answer_hotels.append(answer_dict)
        except AttributeError as log:
            logging.error(str(log))
            for item in hotels.get("data").get('body').get('searchResults').get('results'):
                answer_dict = dict()
                answer_dict["name"] = item.get("name")
                answer_dict["starRating"] = item.get("starRating")
                answer_dict["address"] = item.get("address").get("streetAddress")
                answer_hotels.append(answer_dict)
            return answer_hotels
        return answer_hotels


def get_count_day(message: dict) -> int:
    """
    Функция для расчета количества дней пребывания.
    :param message: словарь с параметрами.
    :return: количество дней пребывания.
    """
    check_out = datetime.strptime(message.get("checkOut"), "%Y-%m-%d")
    check_in = datetime.strptime(message.get("checkIn"), "%Y-%m-%d")
    count_day = check_out - check_in
    return count_day.days
