from app import app, db, socketio
from flask import render_template, send_from_directory, url_for, request, redirect, jsonify, flash, current_app, send_file, make_response
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import CadastrarSala, CadastroArmario, CadastroFerramenta, EditarInformacoes, EditarInformacoesArmario, EditarInformacoesFerramentas, EditarInformacoesSalas, LoginForm, ScanearForm, UserForm, CadastrarSuporte
from app.models import User, Salas, Armario, Ferramentas, FerramentasSuporte, Message, Group, GroupUser, GroupMessage
from datetime import datetime
from flask_socketio import join_room, leave_room, emit
from fpdf import FPDF

from sqlalchemy import desc
from werkzeug.utils import secure_filename
import os
import base64
import uuid
import random
import barcode
from barcode import Code128
from barcode.writer import ImageWriter

#############################################
######## LOGIN PAGE #########################
#############################################
@app.route('/', methods=['GET', 'POST'])
def homepage():
    form = LoginForm()

    # LOGIN
    if form.validate_on_submit():
        try:
            # Tentando obter o usuário via login (substitua por sua lógica de login)
            user = form.login()

            if user:  # Se o login for bem-sucedido
                login_user(user, remember=True)
                return redirect(url_for('home'))  # Redireciona para a página inicial
             # Mensagem de erro se o login falhar

        except Exception as e:
            print("aaa")

    # Renderiza a mesma página com o formulário e mensagens flash
    return render_template('index2.html', form=form, usuario=current_user)