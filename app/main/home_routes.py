import traceback
from app import app, db, socketio
from flask import Blueprint, Flask, abort, render_template, send_from_directory, url_for, request, redirect, jsonify, flash, current_app, send_file, make_response, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import LoginForm, TabelaForm, OrigemForm, ColunasForm, DagForm
from app.models import User, Tabela, Dag, Colunas, Origem
from datetime import datetime
from flask_socketio import join_room, leave_room, emit
from fpdf import FPDF
from sqlalchemy.orm import joinedload
from sqlalchemy import desc, text
from werkzeug.utils import secure_filename
import pandas as pd
import streamlit as st
from datetime import date, timedelta

from app.services.data_service import get_dashboard_data

home_bp = Blueprint('main', __name__, url_prefix='/', template_folder='templates')


@home_bp.route('/home/')
@login_required
def home():
    try:
        data = get_dashboard_data()
    except Exception as e:
        return jsonify({"erro": f"Falha na conexão ou processamento de dados do DB. Detalhes: {str(e)}"}), 500

    return render_template(
        'homepage.html', 
        numero_tabelas=data['numero_tabelas'], 
        numero_esquemas=data['numero_esquemas'], 
        ultima_atualizacao=data['ultima_atualizacao'], 
        logs_atualizacao=data['logs_atualizacao']
    )