from flask import Flask, session
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

import os

app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://srgnjmwphcsgad:44b5e2ed731d875e936f7a603f6276ec767e6f04999d78f2803443d8f2bb27cc@ec2-52-7-39-178.compute-1.amazonaws.com:5432/ddrr83pesoni9k'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'sunitasangwan121@gmail.com'
app.config['MAIL_PASSWORD'] = 'kakpro123'
mail = Mail(app)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
from main import routes
from main import plaid_server