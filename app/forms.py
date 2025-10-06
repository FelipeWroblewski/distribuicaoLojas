from flask_wtf import FlaskForm
from app import db, bcrypt,app
from wtforms import FieldList, FormField, StringField, SubmitField, PasswordField, FileField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, ValidationError

from app.models import User, Dag, Colunas, Origem, Tabela

# Login do Usuario
class LoginForm(FlaskForm):
    email = StringField('E-Mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])
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
    nome_coluna = StringField('Nome da Coluna', validators=[DataRequired(), Length(min=1, max=50)])
    tipo_dado = StringField('Tipo de Dado', validators=[DataRequired(), Length(min=1, max=50)])

class OrigemForm(FlaskForm):
    sistema_origem = StringField('Sistema Origem', validators=[DataRequired(), Length(min=2, max=30)])
    tabela_origem = StringField('Tabela Origem', validators=[DataRequired(), Length(min=2, max=50)])

class TabelaForm(FlaskForm):
    nome_tabela = StringField('Nome da Tabela', validators=[DataRequired(), Length(min=2, max=40)])
    descricao_tabela = StringField('Descrição da Tabela', validators=[DataRequired(), Length(min=2, max=200)])
    esquema = StringField('Esquema da Tabela', validators=[DataRequired(), Length(min=2, max=40)])

    dag = FormField(DagForm)
    origem = FormField(OrigemForm)
    colunas = FieldList(FormField(ColunasForm), min_entries=1, max_entries=50)

    btnSubmit = SubmitField('Salvar Tabela')

    
       