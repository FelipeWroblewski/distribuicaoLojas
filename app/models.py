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

    # Relacionamento com Tabela (um DAG pode ter várias Tabelas)
    tabelas = db.relationship('Tabela', back_populates='dag', lazy=True)


class Origem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sistema_origem = db.Column(db.String, nullable=False)
    tabela_origem = db.Column(db.String, nullable=False)

    # Relacionamento com Tabela (uma origem pode ter várias Tabelas)
    tabelas = db.relationship('Tabela', back_populates='origem', lazy=True)


class Tabela(db.Model):

    __tablename__ = 'tabela'

    id = db.Column(db.Integer, primary_key=True)
    nome_tabela = db.Column(db.String, nullable=False)
    descricao_tabela = db.Column(db.String, nullable=True)
    esquema = db.Column(db.String, nullable=False)

    dag_id = db.Column(db.Integer, db.ForeignKey('dag.id', name="fk_tabela_dag"), nullable=False)
    origem_id = db.Column(db.Integer, db.ForeignKey('origem.id', name="fk_tabela_origem"), nullable=False)

    dag = db.relationship('Dag', back_populates='tabelas')
    origem = db.relationship('Origem', back_populates='tabelas')

    # Relacionamento com Colunas (uma tabela pode ter várias colunas)
    colunas = db.relationship('Colunas', back_populates='tabela', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"Tabela('{self.nome_tabela}')"
    
    # def contarEsquemas(esquema):
    #     return esquema.query.count()


class Colunas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_coluna = db.Column(db.String(100), nullable=False)
    tipo_dado = db.Column(db.String(50), nullable=False)

    tabela_id = db.Column(db.Integer, db.ForeignKey('tabela.id', name="fk_colunas_tabela"), nullable=False)
    tabela = db.relationship('Tabela', back_populates='colunas')

    def contarColunas():
        return Colunas.query.count()
