def tets_flask():
    app = Flask(__name__)
    app.secret_key = "b'~\x8f\xa2\x14\x0b\x8aL9\x8c\x97\xa4Pky\x04e#W\x89{\x87\xcf\xb5D'"
    oauth = OAuth2Provider(app)