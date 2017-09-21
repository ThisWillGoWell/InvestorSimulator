
from pymongo import MongoClient
from utils import *


class DatabaseManager:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        db = client.learning_mongo
        db.clients.delete_many({})
        db.stocks.delete_many({})
        db.portfolios.delete_many({})

        self.clients = db.clients
        self.stocks = db.stocks
        self.portfolios = db.portfolios

    """
    Util Databases
    """
    @staticmethod
    def _exists(db, key, value):
        value = db.find_one({key: value})
        if value is None:
            return False, None
        return True, value


    @staticmethod
    def _update(db, object):
        print('update ' + str(db.update_one({'_id': object['_id']}, {'$set': object}, upsert=False)))

    """
    Users
    """
    def add_user(self, name, password):
        if not self._exists(self.clients, 'name', name)[0]:
            self.clients.insert_one({'name': name, 'password': password})
            return return_object_success('created user')
        else:
            return return_object_error('user already exists')

    def update_password(self, name, old_password, new_password):
        (there, obj) = self._exists(self.clients, "name", name)
        print(obj)
        if there:
            if obj['password'] == old_password:
                obj['password'] = new_password
                self._update(self.clients, obj)
        else:
            return return_object_error('passwords don\'t match')
        print(self._exists(self.clients, "name", name))

    def get_user(self, name):
        return return_object_success(object=self.clients.find_one({'name': name}))

    def validate_user(self, name, password):
        (there, obj) = self._exists(self.clients, "name", name)
        if there:
            if obj['password'] == password:
                return return_object_success("User is valid")
            else:
                return return_object_error("Password does not match")
        return return_object_error("User not found")


    """
    Portfolios
    """


    def get_all_portfolios(self):
        return [ele for ele in self.portfolios.find()]

    def update_portfolio(self, portfolio):
        result = self._update(self.portfolios, portfolio)

    def get_all_portfolios(self):
        return [ele for ele in self.portfolios.find()]

    def make_portfolio(self, portfolio_object, overwrite=False):
        (there, obj) = self._exists(self.portfolios, "trader_id", portfolio_object["trader_id"])
        if there and overwrite:
            for key in portfolio_object.keys():
                obj[key] = portfolio_object[key]
            self._update(self.portfolios, obj)
            return return_object_success("Portfolio updated")
        if there:
            return return_object_error("Portfolio already Exists")

        self.portfolios.insert_one(portfolio_object)
        return return_object_success(msg="Portfolio Created")


    """
    Stocks
    """

    def update_stock(self, stock_id, value):
        self.stocks.find_one({stock_id, value})
        return return_object_success(msg="stock updated")

    def get_stocks(self):
        return [ele for ele in self.stocks.find()]

    def get_all_users(self):
        return self.clients.find()

    def make_stock(self, stock_object, overwrite=False):
        (there, obj) = self._exists(self.stocks, "stock_id", stock_object["stock_id"])
        if there and overwrite:
            for key in stock_object.keys():
                obj[key] = stock_object[key]
            self._update(self.stocks, obj)
            return return_object_success("Stock updated")
        if there:
            return return_object_error("Stock already Exists")

        self.stocks.insert_one(stock_object)
        return return_object_success(msg="Stock Created")


if __name__ == '__main__':
    database = DatabaseManager()
    print(database.add_user('zack-braff', 'panda'))
    print(database.get_user('zack-braff'))
    print(database.update_password('zack-braff', 'panda', 'pandas'))
