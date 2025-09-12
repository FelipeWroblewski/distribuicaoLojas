from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from flask import url_for

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=False, default="Indivíduo Indigente")
    email = db.Column(db.String, nullable=False)
    senha = db.Column(db.String, nullable=True)
    adm = db.Column(db.Boolean, default=False)
    foto = db.Column(db.String, nullable=True)
    ultimo_visto = db.Column(db.DateTime, default=lambda: datetime.now())

    def puxar_nome(self):
        return self.nome