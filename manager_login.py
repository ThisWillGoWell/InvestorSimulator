
from flask_login import LoginManager, login_manager, UserMixin, login_user, login_required, logout_user, current_user

from StockServer.manager_database import DatabaseManager
from utils import  *

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
    def __init__(self, username):
        self.id = username

    def __repr__(self):
        return self.id


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
            username = request.form['username']
            password = request.form['password']
            result = gateKeeper.validate_user(username, password)
            if success(result):
                return redirect(request.args.get("next"))
            else:
                return abort(401)
        else:
            return Response('''
            <form action="" method="post">
                <p><input type=text name=username>
                <p><input type=password name=password>
                <p><input type=submit value=Login>
            </form>
            ''')


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