from pathlib import Path

from flask import Flask
from flask_restful import Api
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager


SAVE_IMAGE: bool = True
BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)
app.config.update({
    'SECRET_KEY': 'd25f7a9f987b3551b946dd40bdb209fbb1e07d1c',
    'SQLALCHEMY_TRACK_MODIFICATIONS': True,
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///site.db',
    'WTF_CSRF_ENABLED': False
})

login_manager = LoginManager(app)
login_manager.login_view = 'login'

jwt = JWTManager(app)
db = SQLAlchemy(app)
api = Api(app)


from web import routs

api.add_resource(routs.LoginAPI, '/api/auth/login', endpoint='login')
api.add_resource(routs.SignupAPI, '/api/auth/signup', endpoint='signup')
api.add_resource(routs.ExtractTextAPI, '/api/image-to-text', endpoint='image_to_text')
