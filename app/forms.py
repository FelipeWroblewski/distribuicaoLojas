from flask_wtf import FlaskForm
from app import db, bcrypt,app
from wtforms import BooleanField, FieldList, FormField, StringField, SubmitField, PasswordField, FileField, TextAreaField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, ValidationError

from app.models import User, Dag, Colunas, Origem, Tabela

# Login do Usuario
class LoginForm(FlaskForm):
    email = StringField('E-Mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    remember_me = BooleanField('Lembrar-me')
    btnSubmit = SubmitField('Login')

    def login(self):
        user = User.query.filter_by(email=self.email.data).first()
        if user:
            if (user.senha == self.senha.data):
                    return user
            else:
                    raise Exception('Senha Incorreta!!!')
        else:
            raise Exception('Usuario nao encontrado')

class DagForm(FlaskForm):
    dag = StringField('DAG', validators=[DataRequired(), Length(min=2, max=40)])
    schedule = StringField('Schedule', validators=[DataRequired(), Length(min=2, max=50)])

class ColunasForm(FlaskForm):
    nome_coluna = StringField('Nome da Coluna')
    tipo_dado = StringField('Tipo de Dado')

class OrigemForm(FlaskForm):
    sistema_origem = StringField('Sistema Origem', validators=[DataRequired(), Length(min=2, max=30)])
    tabela_origem = StringField('Tabela Origem', validators=[DataRequired(), Length(min=2, max=50)])

class TabelaForm(FlaskForm):
    nome_tabela = StringField('Nome da Tabela', validators=[DataRequired(), Length(min=2, max=40)])
    descricao_tabela = StringField('Descrição da Tabela', validators=[DataRequired(), Length(min=2, max=200)])
    esquema = StringField('Esquema da Tabela', validators=[DataRequired(), Length(min=2, max=40)])

    dag = FormField(DagForm)
    origem = FormField(OrigemForm)
    create_table_sql = TextAreaField('Query SQL CREATE TABLE', 
                                     description="Cole aqui o SQL completo de CREATE TABLE.")

    btnSubmit = SubmitField('Salvar Tabela')

    
       