from flask_wtf import FlaskForm
from app import db, bcrypt,app
from wtforms import StringField, SubmitField, PasswordField, FileField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, ValidationError

from app.models import User

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
       