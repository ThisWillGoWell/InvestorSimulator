
import logging
from StockServer.manager_database import DatabaseManager
import random
from utils import *

class StockManager:
    volatility_min = 1
    volatility_max = 10
    volatility_min_turns = 1
    volatility_max_turns = 10

    volatility_mu = 0
    volatility_sigma = 0.1

    def __init__(self, database=DatabaseManager()):
        self.stocks = database.get_stocks()
        print(self.stocks)

    @staticmethod
    def generate_stock(name, id, current_price=10, volatility=5, target_price=10, change_percent=.5):
        """
        generate_stock will generate a basic stock
        :param name: the name of the stock
        :param id: the stock id
        :param current_price: the current price of the stock
        :param volatility: How quickly dose it change
        :param target_price: The target price of the stock
        :param change_percent: the chance the stock will rotate
        :return: a stock dictionary
        """
        return {'name': name,
                'id': id,
                'current_price': current_price,
                'volatility': volatility,
                'target_price': target_price,
                'change_percent': change_percent
                }

    @staticmethod
    def change_it(stock):
        """
        Change up some of the
        :param stock:
        :return:
        """
        logging.debug("updateing stock: %s" % stock)
        stock['target_price'] = round(random.randrange(int((stock['target_price'] * (1 - stock['volatility'] / 10.0))*100),
                                                 int((stock['target_price'] * (1 + stock['volatility'] / 10.0)) * 100), 1)/100.0,2)
        stock['volatility'] = random.randint(StockManager.volatility_min, StockManager.volatility_max)
        logging.debug("stock updated: %s" % stock)

    def simulate(self):
        """
        Run one iteration of the simulation
        :return:
        """
        for stock in self.stocks:
            if random.random() > stock['change_percent']:
                self.change_it(stock)
            stock['current_price'] = stock['current_price'] + ((stock['target_price'] - stock['current_price']) / map_num(stock['volatility'],
                                                                                                  StockManager.volatility_min,
                                                                                                  StockManager.volatility_max,
                                                                                                  StockManager.volatility_min_turns,
                                                                                                  StockManager.volatility_max_turns))
            if stock['current_price'] <= 0:
                stock['current_price'] = 0


if __name__ == '__main__':
    pass