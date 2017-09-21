import functools
from flask_login import LoginManager, login_manager, UserMixin, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, disconnect, emit
from flask import Flask, render_template, send_from_directory
import os

from StockServer import stock_manager
from StockServer.database_manager import DatabaseManager
from StockServer.portfolio_manager import PortfolioManager
from StockServer.stock_manager import StockManager
from StockServer.login_manager import Gatekeeper, User, HeatBeatManger
from flask import Flask, request, redirect, abort, Response
from StockServer.utils import *


def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped


class App:
    app = Flask(__name__)
    app.secret_key = "b'~\x8f\xa2\x14\x0b\x8aL9\x8c\x97\xa4Pky\x04e#W\x89{\x87\xcf\xb5D'"
    app.config.update(
        DEBUG=True,
        SECRET_KEY='secret_xxx'
    )

    gateKeeper = Gatekeeper(app=app)
    root_dir = os.path.dirname(os.getcwd())
    socket_io = SocketIO(app)


    db = DatabaseManager()

    # make some stocks
    print(db.make_stock(stock_manager.StockManager.generate_stock('Gramdma', 'GWEN'), overwrite=True))
    print(db.make_stock(stock_manager.StockManager.generate_stock('mistwood', 'GOLF'), overwrite=True))
    print(db.make_stock(stock_manager.StockManager.generate_stock('DinoPark', 'PARK'), overwrite=True))
    print(db.make_stock(stock_manager.StockManager.generate_stock('PersonalBusiness', 'DMI'), overwrite=True))

    print(db.make_portfolio(PortfolioManager.make_portfolio('Pooplord', 'POOP'), overwrite=True))
    print(db.make_portfolio(PortfolioManager.make_portfolio('Tammyc', 'GAREN'), overwrite=True))
    print(db.make_portfolio(PortfolioManager.make_portfolio('$ara', '!@#$'), overwrite=True))

    sm = StockManager(db=db)
    pm = PortfolioManager(sm=sm, db=db)
    hm = HeatBeatManger()



    @staticmethod
    @socket_io.on('exchange')
    @authenticated_only
    def exchange(data):
        return App.pm.trade(current_user.get_id(), data['action'], data['stock_id'], data['amount'])

    @staticmethod
    @socket_io.on('chat_message')
    @authenticated_only
    def handle_chat_message(data):
        print(data)
        emit('chat_message', current_user.get_id() + ": " + data)

    @staticmethod
    @socket_io.on('event')
    @authenticated_only
    def event(data):
        print(data)

    @staticmethod
    def heatbeat_ping():
        emit("heatbeat")


    @staticmethod
    @socket_io.on("heartbeat")
    @authenticated_only
    def heatbeat():
        App.hm.recived_pong(current_user.get_id())

    @staticmethod
    @app.route("/")
    def root():
        return "Hello World"

    @staticmethod
    @app.route("/register", methods=["POST"])
    def register():
        username = request.form['username']
        password = request.form['password']
        result = App.gateKeeper.register_user(username, password)
        if success(result):
            return redirect('/eventStream')
        return str(result)

    @staticmethod
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            result = App.gateKeeper.validate_user(username, password)
            print_dict(result)
            if success(result):
                return redirect('/eventStream')
            else:
                return abort(401)
        else:
            return send_from_directory(App.root_dir, 'login.html')


    # handle login failed
    @staticmethod
    @app.errorhandler(401)
    def page_not_found(e):
        return Response('<p>Login failed</p>')

    @staticmethod
    # callback to reload the user object
    @gateKeeper.login_manager.user_loader
    def load_user(user_id):
        return User(user_id)

    def update(self, value):
        with self.app.test_request_context():
            App.socket_io.emit('update', value)

    def __init__(self):
        self.app = App.app
        App.sm.set_update_call(self.update)
        App.hm.set_update_call(self.update)
        App.socket_io.run(App.app)




if __name__ == '__main__':
    a = App()
