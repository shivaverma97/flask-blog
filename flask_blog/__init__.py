from flask import Flask               # in CMD install flask using pip, then setup virtualenv and open dir and activate scripts of
                                                          #virtualenv made, setup environment variable, set FLASK_APP=(.py file name) and then use flask run
import os
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail


app = Flask(__name__)
        # open cmd, import secrets, secrets.token_hex(length of secret code), run the code
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # for non logged in users, it wont throw error on trying to access the account page now, it will redirect to login required
login_manager.login_message_category = 'info'  # used to enhance the look of our login required message for above line func
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('server_mail')
app.config['MAIL_PASSWORD'] = os.environ.get('server_pass')
mail = Mail(app)

from flask_blog import routes

