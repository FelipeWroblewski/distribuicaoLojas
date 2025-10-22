from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_user, current_user, logout_user
from app.forms import LoginForm
from app.models import User 

# 1. Cria o Blueprint (o contêiner para as rotas de auth)
auth_bp = Blueprint('auth', __name__, url_prefix='/', template_folder='templates')


@auth_bp.route('/', methods=['GET', 'POST'])
def login(): 
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
        
    form = LoginForm()

    if form.validate_on_submit():
        try:
            user = form.login() 

            if user:
                login_user(user, remember=form.remember_me.data) 
                return redirect(url_for('main.home'))
            
        except Exception as e:
            print(f"Erro durante o login: {e}")

    return render_template('index2.html', form=form, usuario=current_user)


@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login')) 

@auth_bp.context_processor
def inject_user():
    return dict(current_user=current_user)