from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO
import os

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_BINDS'] = {
    'postgres_empresa': os.environ.get(
        'POSTGRES_URL',
        'postgresql://felipe_wr:vyXP8xvi8pOCl1n5W7v3@dw.liveoficial.ind.br:5432/DW_LIVE'
    )
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '939cb126900cd98a7a866c85fb55b55'

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'homepage'
bcrypt = Bcrypt(app)
socketio = SocketIO(app)



from app.auth.auth_routes import login
from app import views

