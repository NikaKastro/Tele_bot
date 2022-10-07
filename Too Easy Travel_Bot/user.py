class User:
    """Класс пользователь. Описывает методы взаимодействия пользователя с чат-ботом."""
    all_users = dict()

    def __init__(self, user_id):
        self.user_id = user_id
        self.city = None
        self.destination_id = None
        self.user_command = None
        self.sort_order = None
        self.count_hotel = None
        self.check_in = None
        self.check_out = None
        self.price_min = None
        self.price_max = None
        self.distance_from_centre = None
        self.count_photo = None

        User.add_user(user_id, self)

    def get_sort_order(self):
        return self.sort_order

    def get_city(self):
        return self.city

    def get_check_in(self):
        return self.check_in

    def get_check_out(self):
        return self.check_out

    def get_user_id(self):
        return self.user_id

    def get_command(self):
        return self.user_command

    @staticmethod
    def get_user(user_id):
        if User.all_users.get(user_id) is None:
            new_user = User(user_id)
            return new_user
        return User.all_users.get(user_id)

    @classmethod
    def add_user(cls, user_id, user):
        cls.all_users[user_id] = user

    @staticmethod
    def del_user(user_id):
        if User.all_users.get(user_id) is not None:
            del User.all_users[user_id]

    def get_user_params_search(self):
        user_params_search = {'sortOrder': self.sort_order, 'destinationId': self.destination_id,
                              'pageSize': self.count_hotel, 'checkIn': self.check_in, 'checkOut': self.check_out,
                              'photo': self.count_photo, 'priceMin': self.price_min, 'priceMax': self.price_max,
                              'distance': self.distance_from_centre}
        return user_params_search