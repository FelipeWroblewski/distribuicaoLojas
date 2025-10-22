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

detailsTable_bp = Blueprint('detailsTable', __name__, url_prefix='/', template_folder='templates')

@detailsTable_bp.route('/tabela/detalhes/<int:tabela_id>', methods=['GET'])
@login_required
def detalhesTabela(tabela_id):
    from sqlalchemy.orm import joinedload

    tabela = Tabela.query.options(
        joinedload(Tabela.dag),
        joinedload(Tabela.origem)
    ).filter_by(id=tabela_id).first_or_404()

    colunas = tabela.colunas
    return render_template('tabela_detalhes.html', tabela=tabela, colunas=colunas)