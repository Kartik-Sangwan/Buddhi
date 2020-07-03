from flask import Flask, session
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

import os

app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://srgnjmwphcsgad:44b5e2ed731d875e936f7a603f6276ec767e6f04999d78f2803443d8f2bb27cc@ec2-52-7-39-178.compute-1.amazonaws.com:5432/ddrr83pesoni9k'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://acfdpdofaelhim:7069b1654eaad7bf00a0fcfd3bd8e6866b9b153f2f2545fd2737392e8351a957@ec2-52-7-39-178.compute-1.amazonaws.com:5432/dmvjhc44eloou'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'imployie@gmail.com'
app.config['MAIL_PASSWORD'] = 'Wewillrockyou'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
from main import routes
from main import plaid_server