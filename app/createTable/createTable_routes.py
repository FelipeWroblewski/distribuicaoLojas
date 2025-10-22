from flask import Blueprint, render_template, redirect, url_for, flash, current_app, jsonify, abort
from flask_login import login_required
from app.forms import TabelaForm 
# Importação da Camada de Serviço
from app.services.data_service import get_tabelas_por_esquema, get_todas_tabelas, criar_tabela_completa 
from app.models import Tabela 

# Defina o Blueprint. 
# url_prefix='/createTable' significa que todas as rotas neste BP começarão com /createTable
createTableBp = Blueprint(
    'createTable', 
    __name__, 
    url_prefix='/createTable', 
    template_folder='templates' # A pasta 'templates' deve estar DENTRO do diretório deste arquivo
) 

# Se você quer a URL final como /createTable (e não /createTable/processarTabela), 
# use apenas '/' no route.

@createTableBp.route('/', methods=['GET', 'POST']) 
@login_required
def processarTabela():
    form = TabelaForm()

    try:
        # 1. CHAMA SERVIÇO: Busca todas as tabelas
        tabelas = get_todas_tabelas() 
    except Exception as e:
        current_app.logger.error(">>> ERRO CRÍTICO DURANTE A BUSCA DE TABELAS (GET/LOAD):", exc_info=True)
        flash("Erro ao carregar lista de tabelas. Verifique o log do servidor.", "danger")
        tabelas = []

    if form.validate_on_submit():
        
        # 2. LÓGICA DE CONTROLE: Verifica campos críticos
        if not form.esquema.data or not form.create_table_sql.data:
            flash("O campo SQL ou Esquema está vazio.", "danger")
            return render_template('formTabela.html', form=form, tabelas=tabelas)

        try:
            # 3. CHAMA SERVIÇO: Persistência
            criar_tabela_completa(form)
            
            flash("Tabela e Colunas criadas com sucesso a partir da query SQL!", "success")
            
            # 4. Redirecionamento 
            # Garanta que 'esquemas.esquema_dinamico' é o nome correto do endpoint do seu outro Blueprint
            return redirect(url_for('esquemas.esquema_dinamico', nome_esquema_url=form.esquema.data))
            
        except Exception as e:
            # Trata o erro de serviço
            flash(f"Ocorreu um erro ao salvar os dados. Detalhes: {str(e)}", "danger")
            current_app.logger.error(f"Erro ao salvar nova tabela: {e}", exc_info=True)
            return render_template('formTabela.html', form=form, tabelas=tabelas)
            
    # Lida com validação falha e renderiza a página GET
    if form.errors:
        for field, errors in form.errors.items():
            current_app.logger.debug(f"Erro de validação no campo '{field}': {errors}")

    # 🚨 CORREÇÃO CRÍTICA DO TEMPLATE PATH:
    # Se 'formTabela.html' está diretamente dentro de 'templates', use apenas o nome do arquivo.
    # Se 'formTabela.html' está em 'templates/createTable/', use 'createTable/formTabela.html'.
    # Vou assumir a estrutura simples: templates/formTabela.html
    return render_template('formTabela.html', form=form, tabelas=tabelas)
