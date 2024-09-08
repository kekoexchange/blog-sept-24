from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object('blog_app.config.Config')

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

# user_loader callback
@login_manager.user_loader
def load_user(user_id):
    from .models import User 
    return User.query.get(int(user_id))

from . import routes