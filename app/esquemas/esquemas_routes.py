# ARQUIVO: app/esquemas/routes.py

from flask import Blueprint, render_template, abort
# Importe o serviço
from app.services.data_service import get_tabelas_por_esquema 
from flask_login import login_required

esquemas_bp = Blueprint('esquemas', __name__, url_prefix='/esquemas', template_folder='templates')

# Lista de esquemas permitidos
ESQUEMAS_PERMITIDOS = [
    'Api', 'Comercial', 'Estoque', 'Eventos', 'Live',
    'Marft', 'Ppcp', 'Rh', 'Rh_sci', 'Suprimentos',
    'Sustentabilidade', 'Ti'
]

# Rota única: agora a URL será /esquemas/<nome_esquema_url>
@esquemas_bp.route('/<string:nome_esquema_url>', methods=['GET'])
@login_required
def esquema_dinamico(nome_esquema_url):
    
    # 1. Trata e normaliza o nome
    nome_template = nome_esquema_url.replace('_', '').title()
    template_name = f'esquemas/esquema{nome_template}.html'
    
    # 2. VALIDAÇÃO DE SEGURANÇA (CRUCIAL):
    if nome_template not in ESQUEMAS_PERMITIDOS:
         # Retorna um erro 404 se o esquema não for permitido
         abort(404) 

    # 3. Lógica Comum (DRY)
    tabelas_do_esquema = get_tabelas_por_esquema(nome_esquema_url) 

    # 4. Renderiza
    return render_template(
        template_name, 
        esquema_atual=nome_esquema_url, 
        tabelas=tabelas_do_esquema
    )