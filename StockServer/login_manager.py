
from flask_login import LoginManager, login_manager, UserMixin, login_user, login_required, logout_user, current_user
from threading import Thread, Lock
from StockServer.database_manager import DatabaseManager
from StockServer.utils import *
import time
import json



class Gatekeeper:
    clients = {}

    def __init__(self, app=None, database=DatabaseManager()):
        login_manager = LoginManager()
        login_manager.init_app(app)
        login_manager.login_view = "login"
        self.login_manager = login_manager
        self.database = database

    def validate_user(self, username, password):
        """
        Validates the user, logs them in if success
        :param username: username
        :param password: password
        :return: response object
        """

        result = self.database.validate_user(username, password)
        if success(result):
            login_user(User(username))
            return return_object_success("User has been logged in")
        return result

    def register_user(self, username, password):
        """
        Registers the user, logs them in if success
        :param username:
        :param password:
        :return: a response object
        """
        result = self.database.add_user(username, password)
        if success(result):
            return return_object_success("User has been logged in")
        return result

    @staticmethod
    def login(username):
        user = User(username)
        login_user(user)


class User(UserMixin):
    """
    Class to represent a user for the auth system
    """
    def __init__(self, trader_id):
        self.id = trader_id

    def __repr__(self):
        return self.id

class HeatBeatManger():
    """
    Class responsible for manaeing the heartbeat
    """

    @staticmethod
    def standard_update(data):
        print(data)

    def __init__(self):
        self.heatBeatTimer = self.HeatBeatTimer(self)
        self.active_clients = {}
        self.active_client_lock = Lock()
        self.update_notify = HeatBeatManger.standard_update

    def active_list_json(self):
        return

    def set_update_call(self, new_function):
        self.update_notify = new_function

    def recieved_pong(self, client_id):
        self.lock_active_clients()
        self.active_clients[client_id] = time.time()
        self.unlock_active_clients()

    def lock_active_clients(self):
        self.active_client_lock.acquire()

    def unlock_active_clients(self):
        self.active_client_lock.release()

    class HeatBeatTimer(Thread):
        update_timeout = .250
        active_timeout = 1

        def __init__(self, heart_beat_manager):
            Thread.__init__(self)
            self.hm = heart_beat_manager

        def run(self):
            while True:
                self.hm.lock_active_clients()
                for client in self.hm.active_clients:
                    if time.time() - self.hm.active_clients[client] > self.hm.active_timeout:
                        del(self.hm.active_clients[client])
                        #self.hm.update_notify(self.)
                self.hm.unlock_active_clients()
                time.sleep(self.update_timeout)




if __name__ == '__main__':
    from flask import Flask, request, redirect, abort, Response

    app = Flask(__name__)
    app.secret_key = "b'~\x8f\xa2\x14\x0b\x8aL9\x8c\x97\xa4Pky\x04e#W\x89{\x87\xcf\xb5D'"
    app.config.update(
        DEBUG=True,
        SECRET_KEY='secret_xxx'
    )
    gateKeeper = Gatekeeper(app=app)


    # some protected url
    @app.route('/')
    @login_required
    def home():
        return Response("Hello World!")

    @app.route("/register", methods=["POST"])
    def register():
        username = request.form['username']
        password = request.form['password']
        result = gateKeeper.register_user(username,password)
        if success(result):
            return redirect(request.args.get("next"))
        return str(result)


    # somewhere to login
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == 'POST':
            action = request.form['action']
            username = request.form['username']
            password = request.form['password']

            if action == 'login':
                result = gateKeeper.validate_user(username, password)
            else:
                result = gateKeeper.register_user(username, password)

            if success(result):
                return redirect(request.args.get("next"))
            else:
                return abort(401)


    @app.route("/logout")
    @login_required
    def logout():
        print(current_user)
        logout_user()
        return Response('<p>Logged out</p>')


    # handle login failed
    @app.errorhandler(401)
    def page_not_found(e):
        return Response('<p>Login failed</p>')


    # callback to reload the user object
    @gateKeeper.login_manager.user_loader
    def load_user(userid):
        return User(userid)


    app.run()