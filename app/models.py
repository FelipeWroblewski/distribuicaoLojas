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

    def puxar_nome(self):
        return self.nome

class Dag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dag = db.Column(db.String, nullable=False)
    schedule = db.Column(db.String, nullable=False)

class Colunas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_coluna = db.Column(db.String, nullable=False)
    tipo_dado = db.Column(db.String, nullable=False)

class Origem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sistema_origem = db.Column(db.String, nullable=False)
    tabela_origem = db.Column(db.String, nullable=False)

class Tabela(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_tabela = db.Column(db.String, nullable=False)
    descricao_tabela = db.Column(db.String, nullable=True)
    esquema = db.Column(db.String, nullable=False)
    Dag_id = db.Column(db.Integer, db.ForeignKey('dag.id'), nullable=False)
    Colunas_id = db.Column(db.Integer, db.ForeignKey('colunas.id'), nullable=False)
    Origem_id = db.Column(db.Integer, db.ForeignKey('origem.id'), nullable=False)
