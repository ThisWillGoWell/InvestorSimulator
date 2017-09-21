import logging
from threading import Thread, Lock
import time

from StockServer.database_manager import DatabaseManager
import random
from StockServer.invest_utils import *
import json

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class StockManager:
    volatility_min = 1
    volatility_max = 10
    volatility_min_turns = 1
    volatility_max_turns = 10

    volatility_mu = 0
    volatility_sigma = 0.1

    @staticmethod
    def standard_update(data):
        print(data)

    def __init__(self, db):
        self.stocks = db.get_stocks()
        self.stocks_lock = Lock()
        stock_shuffler = self.StockShuffler(self)
        stock_shuffler.daemon = True
        stock_shuffler.start()

        self.update_notify = StockManager.standard_update

        print(self.stocks)

    @staticmethod
    def generate_stock(name, stock_id, current_price=10, volatility=5, target_price=10, change_percent=.5,
                       total_shares=100, open_shares=100):
        # type: (object, object, object, object, object, object, object, object) -> object
        """
        generate_stock will generate a basic stock
        :param name: the name of the stock
        :param stock_id: the stock stock_id
        :param current_price: the current price of the stock
        :param volatility: How quickly dose it change
        :param target_price: The target price of the stock
        :param change_percent: the chance the stock will rotate
        :return: a stock dictionary
        """
        return {'name': name,
                'stock_id': stock_id,
                'current_price': current_price,
                'volatility': volatility,
                'target_price': target_price,
                'change_percent': change_percent,
                'total_shares': total_shares,
                'open_shares': open_shares
                }

    @staticmethod
    def change_it(stock):
        """
        Change up some of the
        todo: parameter to control
        todo: make chance to to be more normally dis
        :param stock:
        :return:
        """
        stock['target_price'] = round(
            random.randrange(int((stock['target_price'] * (1 - stock['volatility'] / 11.0)) * 100),
                             int((stock['target_price'] * (1 + stock['volatility'] / 11.0)) * 100), 1) / 100.0, 2)
        stock['volatility'] = random.randint(StockManager.volatility_min, StockManager.volatility_max)

    def set_update_call(self, new_function):
        self.update_notify = new_function

    def get_stock(self, sock_id, as_object=False):
        for stock in self.stocks:
            if stock['stock_id'] == sock_id:
                if as_object:
                    return return_object_success(object=stock)
                return return_object_success(object=dict(stock))
        return return_object_error('Stock ID not found')

    def simulate(self):
        """
        Run one iteration of the simulation
        :return:
        """
        self.stocks_lock.acquire()
        logging.info("Simulating")
        for stock in self.stocks:
            if random.random() > stock['change_percent']:
                self.change_it(stock)
            stock['current_price'] = stock['current_price'] + (
                (stock['target_price'] - stock['current_price']) / map_num(stock['volatility'],
                                                                           StockManager.volatility_min,
                                                                           StockManager.volatility_max,
                                                                           StockManager.volatility_min_turns,
                                                                           StockManager.volatility_max_turns))
            if stock['current_price'] <= 0:
                stock['current_price'] = 0

        self.update_notify(self.get_stocks_json())

        self.stocks_lock.release()

    def get_stocks_json(self):
        new_stocks = []
        for s in self.stocks:
            new_stocks.append({'name': s['name'],
                               'stock_id': s['stock_id'],
                               'current_price': s['current_price'],
                               'total_shares': s['total_shares'],
                               'open_shares': s['open_shares']})

        return json.dumps({'current_stock_standings': new_stocks})

    def lock_stocks(self):
        self.stocks_lock.acquire()

    def unlock_stocks(self):
        self.stocks_lock.release()

    class StockShuffler(Thread):
        sleep_timeout = 3

        def __init__(self, stock_manager):
            Thread.__init__(self)
            self.stock_manager = stock_manager

        def run(self):
            # @todo sleep so we start shuffle on a whole min
            while True:
                self.stock_manager.simulate()
                time.sleep(self.sleep_timeout)


if __name__ == '__main__':
    db = DatabaseManager()
    print(db.make_stock(StockManager.generate_stock('Grandmas Life', 'GWEN'), overwrite=True))
    print(db.make_stock(StockManager.generate_stock('GOLF GOLF GOLF', 'GOLF'), overwrite=True))
    print(db.make_stock(StockManager.generate_stock('DinoPark', 'PARK'), overwrite=True))
    print(db.make_stock(StockManager.generate_stock('PersonalBusiness', 'DMI'), overwrite=True))
    sm = StockManager(db)
    while True:
        pass
