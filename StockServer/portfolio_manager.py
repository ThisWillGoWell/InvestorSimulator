from threading import Lock
from utils import *
from StockServer.utils import *
import json

buy_action_string = 'buy'
sell_action_string = 'sell'


class PortfolioManager:

    def __init__(self, db, sm):
        self.portfolios = db.get_all_portfolios()
        self.sm = sm
        self.portfolio_lock = Lock()

    @staticmethod
    def make_portfolio(trader_id, name, cash=100):
        return {
            'trader_id':trader_id,
            'stocks': {},
            'name': name,
            'cash': cash

        }

    # todo average_buy price with transaction history
    @staticmethod
    def portfolio_stock(stock_id, current_price, amount):
        return {
            'stock_id':      stock_id,
            'current_price': current_price,
            'amount_owned': amount
        }

    def get_portfolio(self, trader_id, as_object=False):
        for port in self.portfolios:
            if port['trader_id'] == trader_id:
                if as_object:
                    return return_object_success(object=port)
                return return_object_success(object=dict(port))
        return return_object_error("Stock Not Found")

    def lock_portfolios(self):
        self.portfolio_lock.aquire()

    def unlock_portfolios(self):
        self.portfolio_lock.release()

    def process_trade(self, trader_id, action,  stock_id, amount):
        self.sm.lock_stocks()
        self.lock_portfolios()
        trade_result = self.trade(trader_id, action, stock_id, amount)

        self.sm.unlock_stocks()
        self.unlock_portfolios()
        return trade_result

    def trade(self, trader_id, action,  stock_id, amount):
        stock_result = self.sm.get_stock(stock_id, as_object=True)
        portfolio_result = self.get_portfolio(trader_id, as_object=True)
        if not success(stock_result):
            return stock_result

        if not success(portfolio_result):
            return portfolio_result

        stock = stock_result['object']
        portfolio =  portfolio_result['object']

        if action == buy_action_string:
            # Check if there are enough stocks to buy
            if stock['open_shares'] < amount:
                return return_object_error("Not enough stocks exist")

            # Check if the user has enough money
            if stock['current_price'] * amount > portfolio['cash']:
                return return_object_error("User does not have enough money")

            # Process the trade
            stock['open_shares'] -= amount
            portfolio['cash'] -= stock['current_price'] * amount

            # does the user not have the stock?
            if not stock['stock_id'] in portfolio['stocks']:
                # make a new stock
                portfolio['stocks'][stock['stock_id']] = \
                    self.portfolio_stock(stock_id=stock['stock_id'],
                                         current_price=stock['current_price'],
                                         amount=amount)

            else:
                # current price is updated on shuffle
                portfolio_stock = portfolio['stocks'][stock['stock_id']]
                portfolio_stock['amount_owned'] += amount

            return return_object_success("Buy complete")

        elif action == sell_action_string:
            # err if stock not in portfolio
            if not stock['stock_id'] in portfolio['stocks']:
                return return_object_error("Sock not found in portfolio")
            portfolio_stock = portfolio['stocks'][stock['stock_id']]

            # err if not enough stocks
            if portfolio_stock['amount_owned'] < amount:
                return return_object_error("Not enough stocks in portfolio")

            # finish the transaction
            portfolio_stock['amount_owned'] -= amount
            portfolio['cash'] += portfolio_stock['current_price'] * amount

            return return_object_success("Sell complete")

        return return_object_error("Action not found")

    def get_portfolio_json(self):
        portfolios = []
        for p in self.portfolios:
            portfolios.append({
                'trader_id': p['trader_id'],
                'stocks': p['stocks'],
                'name': p['name'],
                'cash': p['cash']
            })
        return json.dumps({'current_portfolio_standings': portfolios})

if __name__ == '__main__':
    import database_manager
    import stock_manager

    db = database_manager.DatabaseManager()

    # make some stocks
    print(db.make_stock(stock_manager.StockManager.generate_stock('Gramdma', 'GWEN'), overwrite=True))
    print(db.make_stock(stock_manager.StockManager.generate_stock('mistwood', 'GOLF'), overwrite=True))
    print(db.make_stock(stock_manager.StockManager.generate_stock('DinoPark', 'PARK'), overwrite=True))
    print(db.make_stock(stock_manager.StockManager.generate_stock('PersonalBusiness', 'DMI'), overwrite=True))

    print(db.make_portfolio(PortfolioManager.make_portfolio('Pooplord', 'POOP'), overwrite=True))
    print(db.make_portfolio(PortfolioManager.make_portfolio('Tammyc', 'GAREN'), overwrite=True))
    print(db.make_portfolio(PortfolioManager.make_portfolio('$ara', '!@#$'), overwrite=True))

    # Stat the managers
    sm = stock_manager.StockManager(database=db)
    pm = PortfolioManager(db=db, sm=sm)

    print(sm.get_stocks_json())

    pm.trade('Pooplord', buy_action_string,'GWEN',5)

    print(sm.get_stocks_json())
    # @todo write this test, see why stock_id not being changed
