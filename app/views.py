import traceback
from app import app, db, socketio
from flask import Flask, abort, render_template, send_from_directory, url_for, request, redirect, jsonify, flash, current_app, send_file, make_response, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import LoginForm, TabelaForm, OrigemForm, ColunasForm, DagForm
from app.models import User, Tabela, Dag, Colunas, Origem
from datetime import datetime
from flask_socketio import join_room, leave_room, emit
from fpdf import FPDF
from sqlalchemy.orm import joinedload
from sqlalchemy import desc
from werkzeug.utils import secure_filename
import os
import re
import sys
import base64
import pandas as pd
import uuid
import random
import barcode
import streamlit as st
import psycopg2
from datetime import date, timedelta
#from ydata_profiling import ProfileReport
from barcode import Code128
from barcode.writer import ImageWriter

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')

@app.after_request
def add_header(response):
    response.cache_control.no_store = True
    return response

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

@app.context_processor
def inject_user():
    return dict(current_user=current_user)

#Função de logout
@app.route('/sair')
def logout():
    logout_user()
    return redirect(url_for('homepage'))

#############################################
######## PAGE HOME ##########################
#############################################

# HOMEPAGE
@app.route('/home/')
@login_required
def home():
    return render_template('homepage2.html')

#############################################
######## PAGE ESQUEMA API ###############
#############################################

# ESTOQUE DE PRODUTOS
@app.route('/esquemaApi/<string:nome_esquema>', methods=['GET'])
@login_required
def esquemaApi(nome_esquema):
    tabelas_do_esquema = get_tabelas_por_esquema(nome_esquema)

    return render_template('Esquemas/esquemaApi.html', esquema_atual=nome_esquema, tabelas=tabelas_do_esquema)

#############################################
######## PAGE ESQUEMA COMERCIAL ###############
#############################################

# ESTOQUE DE PRODUTOS
@app.route('/esquemaComercial/')
@login_required
def esquemaComercial():
    return render_template('Esquemas/esquemaComercial.html')

#############################################
######## PAGE ESQUEMA ESTOQUE ###############
#############################################

# ESTOQUE DE PRODUTOS
@app.route('/esquemaEstoque/')
@login_required
def esquemaEstoque():
    return render_template('Esquemas/esquemaEstoque.html')

#############################################
######## PAGE ESQUEMA EVENTOS ###############
#############################################

# ESTOQUE DE PRODUTOS
@app.route('/esquemaEventos/')
@login_required
def esquemaEventos():
    return render_template('Esquemas/esquemaEventos.html')

#############################################
######## PAGE ESQUEMA LIVE ###############
#############################################

# ESTOQUE DE PRODUTOS
@app.route('/esquemaLive/')
@login_required
def esquemaLive():
    return render_template('Esquemas/esquemaLive.html')

#############################################
######## PAGE ESQUEMA MARFT ###############
#############################################

# ESTOQUE DE PRODUTOS
@app.route('/esquemaMarft/')
@login_required
def esquemaMarft():
    return render_template('Esquemas/esquemaMarft.html')

#############################################
######## PAGE ESQUEMA PPCP ###############
#############################################

# ESTOQUE DE PRODUTOS
@app.route('/esquemaPpcp/')
@login_required
def esquemaPpcp():
    return render_template('Esquemas/esquemaPpcp.html')

#############################################
######## PAGE ESQUEMA RH ###############
#############################################

# ESTOQUE DE PRODUTOS
@app.route('/esquemaRh/')
@login_required
def esquemaRh():
    return render_template('Esquemas/esquemaRh.html')

#############################################
######## PAGE ESQUEMA RH_SCI ###############
#############################################

# ESTOQUE DE PRODUTOS
@app.route('/esquemaRh_sci/')
@login_required
def esquemaRh_sci():
    return render_template('Esquemas/esquemaRh_sci.html')

#############################################
######## PAGE ESQUEMA SUPRIMENTOS ###############
#############################################

# ESTOQUE DE PRODUTOS
@app.route('/esquemaSuprimentos/')
@login_required
def esquemaSuprimentos():
    return render_template('Esquemas/esquemaSuprimentos.html')

#############################################
######## PAGE ESQUEMA SUSTENTABILIDADE ###############
#############################################

# ESTOQUE DE PRODUTOS
@app.route('/esquemaSustentabilidade/')
@login_required
def esquemaSustentabilidade():
    return render_template('Esquemas/esquemaSustentabilidade.html')

#############################################
######## PAGE ESQUEMA TI ###############
#############################################

# ESTOQUE DE PRODUTOS
@app.route('/esquemaTi/')
@login_required
def esquemaTi():
    return render_template('Esquemas/esquemaTi.html')

################################################
######## PAGE DISTRIBUICAO DE PRODUTOS #########
################################################

@app.route('/distribuicao/')
@login_required
def distribuicao():
    return render_template('distribuicao.html', tabelaDistribuicao="")  # começa vazio

################################################
#### FUNÇÃO PARA SEPARAR AS TABELAS DO FORM ####
################################################
@app.route('/processarTabela', methods=['GET', 'POST'])
@login_required
def processarTabela():
    print(">>> ENTROU NO ENDPOINT /processarTabela")
    form = TabelaForm()

    print("Tipo de requisição:", request.method)
    if request.method == 'POST':
        print("Formulário submetido via POST.")
    else:
        print("Requisição GET recebida.")
    
    if form.validate_on_submit():
        print("Formulário validado com sucesso.")
    else:
        print("Erros de validação:", form.errors)

    try:
        from sqlalchemy.orm import joinedload 
        
        tabelas = Tabela.query.options(
            joinedload(Tabela.dag),
            joinedload(Tabela.origem)
        ).all()
    except Exception as e:
        # MUDANÇA CRÍTICA: Usando o logger do Flask com exc_info=True
        app.logger.error(">>> ERRO CRÍTICO DURANTE A BUSCA DE TABELAS (GET/LOAD)")
        # Este comando irá imprimir a pilha de chamadas completa (traceback)
        app.logger.error("Rastreamento Completo da Exceção:", exc_info=True)
        
        tabelas = []

    if form.validate_on_submit():
        # DIAGNOSTICO 1: O FORMULÁRIO FOI SUBMETIDO E PASSOU NA VALIDAÇÃO?
        print("DIAGNOSTICO 1: Form submetido e validado com sucesso. Prosseguindo...")
        
        nome_esquema = form.esquema.data
        sql_query = form.create_table_sql.data
        
        # DIAGNOSTICO 2: VERIFICAR SE A QUERY NÃO ESTÁ VAZIA
        if not sql_query or not nome_esquema:
            flash("O campo SQL ou Esquema está vazio.", "danger")
            return render_template('formTabela.html', form=form, tabelas=tabelas)

        try:
            colunas_analisadas = parse_create_table_sql(sql_query)
        except Exception as e:
            # DIAGNOSTICO 3: O PARSER FALHOU?
            print(f">>> DIAGNOSTICO 3: ERRO CRÍTICO NO PARSER SQL: {e}")
            flash(f"Falha na análise da query SQL. Erro: {e}", "danger")
            return render_template('formTabela.html', form=form, tabelas=tabelas)

        # DIAGNOSTICO 4: QUANTAS COLUNAS FORAM ANALISADAS?
        print(f"DIAGNOSTICO 4: {len(colunas_analisadas)} colunas analisadas com sucesso.")

        try: 
            # ... (código para criar Dag, Origem, Tabela, Colunas) ...
            
            # DIAGNOSTICO 5: CHEGOU NO COMMIT?
            print("DIAGNOSTICO 5: Tentando db.session.commit()...")
            
            db.session.commit()
            
            # DIAGNOSTICO 6: COMMIT SUCESSO?
            print("DIAGNOSTICO 6: SUCESSO! Dados salvos.")

            flash("Tabela criada com sucesso!", "success")
            return redirect(url_for('esquemaApi', nome_esquema=nome_esquema))
            
        except Exception as e:
            db.session.rollback() 
            # DIAGNOSTICO 7: ERRO NO COMMIT. ONDE ESTÁ A EXCEÇÃO?
            print("=================================================================")
            print(f">>> DIAGNOSTICO 7: ERRO AO SALVAR NO BANCO (COMMIT FAILED): {e}")
            print("=================================================================")
            
            flash(f"Ocorreu um erro de banco de dados. Verifique o console. Detalhes: {e}", "danger")
            return render_template('formTabela.html', form=form, tabelas=tabelas)
            
    else:
        # DIAGNOSTICO 8: O FORMULÁRIO NÃO PASSOU NA VALIDAÇÃO (GET ou POST falhou a validação)
        print("DIAGNOSTICO 8: Requisição GET ou validação do formulário falhou.")
        # Se você está vendo este print no POST, olhe os erros de validação no seu console:
        for field, errors in form.errors.items():
             print(f"Erro de validação no campo '{field}': {errors}")

    return render_template('formTabela.html', form=form, tabelas=tabelas)

##################################################
#### FUNÇÃO PARA CRIAR DADOS DA TABELA COLUNAS####
##################################################

import re

def parse_create_table_sql(sql_query):

    sql_query = re.sub(r'--.*', '', sql_query)
    sql_query = re.sub(r'/\*.*?\*/', '', sql_query, flags=re.DOTALL)
    
    # Normaliza espaços
    sql_query = re.sub(r'\s+', ' ', sql_query).strip()
    
    match = re.search(r'\((.*)\)', sql_query, re.IGNORECASE | re.DOTALL)
    
    if not match:
        
        return []

    table_body = match.group(1).strip()

    column_definitions = table_body.split(',')
    
    columns = []
    
    for definition in column_definitions:
        
        clean_def = definition.strip()
        if not clean_def:
            continue

        
        match_col = re.match(r'^\s*"?([a-zA-Z_][a-zA-Z0-9_]*)"?\s+(.+)$', clean_def, re.IGNORECASE | re.DOTALL)
        
        if match_col:
            col_name = match_col.group(1)
            type_and_constraints = match_col.group(2).strip()
            
            
            columns.append({
                'nome': col_name,
                'tipo': type_and_constraints
            })
        else:
            
            if 'primary key' in clean_def.lower() or 'foreign key' in clean_def.lower() or 'constraint' in clean_def.lower():
                continue

            
            print(f"Aviso: Não foi possível analisar a definição de coluna: {clean_def}")


    return columns
    
##################################################
#### FUNÇÃO PARA VISUALIZAR DADOS DA TABELA#######
##################################################

def get_tabelas_por_esquema(nome_esquema):

    from sqlalchemy.orm import joinedload
    
    tabelas = Tabela.query.options(
        joinedload(Tabela.dag),
        joinedload(Tabela.origem)
    ).filter_by(esquema=nome_esquema).all()
    
    return tabelas

################################################
######## FUNÇÃO PARA PUXAR ARQUIVO CSV##########
################################################

@app.route('/distribuicao/upload', methods=['POST'])
@login_required
def upload_distribuicao():
    file = request.files.get("file")
    if not file:
        return "Nenhum arquivo enviado", 400

    filename = file.filename.lower()
    if filename.endswith(".csv"):
        df = pd.read_csv(file, sep=";", encoding="utf-8", engine="python")
    elif filename.endswith((".xlsx", ".xls")):
        df = pd.read_excel(file)
    else:
        return "Formato de arquivo não suportado", 400

    # SALVA TEMPORARIAMENTE para processar depois
    RELATORIOS_TEMP['df_estoque'] = df

    tabela_html = df.to_html(index=False, classes="csv-table")
    return tabela_html



def conectar():
    # Conectar ao banco de dados
    try:
        conn = psycopg2.connect(
            database = "DW_LIVE", 
            user = "Live", 
            host= 'dw.liveoficial.ind.br',
            password = "p28ke8spLQDX47vdlHvR",
            port = 5432)
    except Exception as e:
        return None
    return conn

def le_arquivo_csv(caminho_arquivo):
    try:
        df = pd.read_csv(caminho_arquivo, sep=";", encoding='utf-8')
        return df
    except Exception as e:
        return None
    
def salvar_arquivo_csv(df, caminho_arquivo):
    try:
        df.to_csv(caminho_arquivo, sep=";", index=False, encoding='utf-8')
    except Exception as e:
        print(f"Erro ao salvar o arquivo {caminho_arquivo}: {e}")


def transformar_dados(df):
    enviar_df = df[df['enviar/receber'] == 'Enviar'].copy()
    receber_df = df[df['enviar/receber'] == 'Receber'].copy()

    # Ordena os dados conforme solicitado
    enviar_df.sort_values(by=['loja', 'Ref_Cor', 'tamanho', 'enviar/receber'], ascending=[True, True, True, False], inplace=True)
    receber_df.sort_values(by=['loja', 'Ref_Cor', 'tamanho', 'enviar/receber'], ascending=[True, True, True, False], inplace=True)
    
    lista_movimentacoes = []
    produtos = df[['Ref_Cor', 'tamanho']].drop_duplicates()
    
    for _, produto in produtos.iterrows():
        ref_cor = produto['Ref_Cor']
        tamanho = produto['tamanho']
        qtde_mov = 1

        # 1. Filtra os DataFrames corrigindo o warning
        enviadores = df[(df['Ref_Cor'] == ref_cor) & (df['tamanho'] == tamanho) & (df['enviar/receber'] == 'Enviar')].copy()
        recebedores = df[(df['Ref_Cor'] == ref_cor) & (df['tamanho'] == tamanho) & (df['enviar/receber'] == 'Receber')].copy()

        # 2. Ordena os DataFrames
        enviadores = enviadores.sort_values(by='movimentar', ascending=False)
        recebedores = recebedores.sort_values(by='movimentar', ascending=True)


        while (not enviadores.empty) and (not recebedores.empty):
            enviar_loja = enviadores.iloc[0]
            receber_loja = recebedores.iloc[0]
            qtde_mov = min(enviar_loja['movimentar'], receber_loja['movimentar'])
            

            if qtde_mov > 0:
                lista_movimentacoes.append({
                    'de_loja': enviar_loja['loja'],
                    'para_loja': receber_loja['loja'],
                    'Ref_Cor': ref_cor,
                    'tamanho': tamanho,
                    'qtde': qtde_mov
                })
                # Atualiza os DataFrames
                enviadores.loc[enviadores.index[0], 'movimentar'] -= qtde_mov
                recebedores.loc[recebedores.index[0], 'movimentar'] -= qtde_mov

                # Remove linhas com qtde zero
                enviadores = enviadores[enviadores['movimentar'] > 0]
                recebedores = recebedores[recebedores['movimentar'] > 0]
            else: 
                break
            #breakpoint()
    movimentacoes_df = pd.DataFrame(lista_movimentacoes)
    return movimentacoes_df



def detalhes_produto(df_produtos_unicos):
    conn = conectar()
    if conn is None or df_produtos_unicos.empty:
        return pd.DataFrame(columns=['Ref_Cor', 'tamanho', 'sku', 'descricao', 'segmento'])

    # Cria uma lista de tuplas '(Ref_Cor, tamanho)' para usar na cláusula WHERE IN
    produtos_tuplas = [tuple(x) for x in df_produtos_unicos.to_numpy()]
    
    query = """
        SELECT
            prod.cd_referencia || prod.cd_cor as "Ref_Cor",
            prod.cd_tamanho as "tamanho",
            prod.nivel_estrutura || '.' || prod.cd_referencia || '.' || prod.cd_tamanho || '.' || prod.cd_cor as "sku",
            prod.desc_segmento as "segmento",
            prod.desc_produto as "descricao"
        FROM live.dproduto prod
        WHERE (prod.cd_referencia || prod.cd_cor, prod.cd_tamanho) IN %s
    """
    try:
        df_detalhes = pd.read_sql_query(query, conn, params=(tuple(produtos_tuplas),))
    finally:
        conn.close()
    
    df_detalhes.drop_duplicates(subset=['Ref_Cor', 'tamanho'], keep='first', inplace=True)
    return df_detalhes

def cronograma_envio(df_movimentacoes, prazo_envio, min_envio, data_inicio, max_rotas):
    # --- Parte 1: Agendamento das Rotas (Lógica Alterada) ---
    somas_por_rota = df_movimentacoes.groupby(['de_loja', 'para_loja'])['qtde'].sum().reset_index()
    
    # Usa a variável min_envio para filtrar as rotas
    rotas_para_agendar = somas_por_rota[somas_por_rota['qtde'] >= min_envio].copy()

    print("Somas por rota:")
    print(somas_por_rota)
    print("Rotas que passam no min_envio:")
    print(rotas_para_agendar)

    rotas_para_agendar.sort_values(by=['de_loja', 'qtde'], ascending=[True, False], inplace=True)
    

    # Dicionário para rastrear o estado de cada loja remetente
    estado_lojas = {}
    datas_envio_agendadas = []

    for _, rota in rotas_para_agendar.iterrows():
        de_loja = rota['de_loja']
        
        # Inicializa o estado da loja se for a primeira vez
        if de_loja not in estado_lojas:
            estado_lojas[de_loja] = {'ultima_data': data_inicio, 'envios_no_dia': 0}

        # Verifica se a loja já fez 2 envios na última data registrada
        if estado_lojas[de_loja]['envios_no_dia'] >= max_rotas:
            # Calcula a próxima data de envio baseada no prazo
            nova_data = estado_lojas[de_loja]['ultima_data'] + timedelta(days=prazo_envio + 1)
            estado_lojas[de_loja]['ultima_data'] = nova_data
            estado_lojas[de_loja]['envios_no_dia'] = 0 # Zera a contagem para o novo dia

        # A data de envio para a rota atual é a 'ultima_data' registrada para a loja
        data_envio_atual = estado_lojas[de_loja]['ultima_data']
        datas_envio_agendadas.append(data_envio_atual)

        # Incrementa o contador de envios para o dia atual
        estado_lojas[de_loja]['envios_no_dia'] += 1

    rotas_para_agendar['prazo'] = datas_envio_agendadas

    # --- Parte 2: Detalhamento dos Produtos ---
    # Busca detalhes de todos os produtos necessários de uma só vez
    produtos_unicos = df_movimentacoes[['Ref_Cor', 'tamanho']].drop_duplicates()
    df_detalhes_produtos = detalhes_produto(produtos_unicos)
    # Junta as movimentações com os detalhes dos produtos
    
    print(df_detalhes_produtos.head())


    df_com_detalhes = pd.merge(
        df_movimentacoes,
        df_detalhes_produtos,
        on=['Ref_Cor', 'tamanho'],
        how='left'
    )

    # Junta o resultado com as rotas agendadas para adicionar o prazo
    df_final = pd.merge(
        df_com_detalhes,
        rotas_para_agendar[['de_loja', 'para_loja', 'prazo']],
        on=['de_loja', 'para_loja'],
        how='left' # Mantém apenas as movimentações de rotas que foram agendadas
    )
    df_final['prazo'] = df_final['prazo'].fillna(data_inicio)

    # --- Parte 3: Formatação Final ---
    df_final.rename(columns={
        'de_loja': 'loja_origem',
        'para_loja': 'loja_destino',
        'qtde': 'quantidade'
    }, inplace=True)

    colunas_finais = ['loja_origem', 'loja_destino', 'prazo', 'segmento', 'sku', 'descricao', 'quantidade']
    df_final = df_final[colunas_finais]

    # Agrupa por SKU para somar as quantidades dentro de cada envio
    df_final = df_final.groupby(
        ['loja_origem', 'loja_destino', 'prazo', 'segmento', 'sku', 'descricao']
    ).agg(
        quantidade=('quantidade', 'sum')
    ).reset_index()

    return rotas_para_agendar, df_final.sort_values(by=['loja_origem', 'loja_destino', 'prazo'])



def distribuicao_hub(df_estoque):

    # 1. Separar lojas que enviam e que recebem
    enviadores = df_estoque[df_estoque['enviar/receber'] == 'Enviar'].copy()
    recebedores = df_estoque[df_estoque['enviar/receber'] == 'Receber'].copy()

    # 2. Calcular o estoque total consolidado no Hub
    # O estoque do hub é a soma de tudo que as lojas 'enviadoras' possuem.
    hub_estoque = enviadores.groupby(['Ref_Cor', 'tamanho'])['movimentar'].sum()

    # 3. Distribuir do Hub para as lojas que precisam
    lista_recebimentos = []
    for _, loja_que_recebe in recebedores.iterrows():
        ref_cor = loja_que_recebe['Ref_Cor']
        tamanho = loja_que_recebe['tamanho']
        qtde_necessaria = loja_que_recebe['movimentar']

        # Verifica o estoque disponível no hub para este item específico
        estoque_disponivel_hub = hub_estoque.get((ref_cor, tamanho), 0)

        # A quantidade a enviar é o mínimo entre o que a loja precisa e o que o hub tem
        qtde_a_enviar = min(qtde_necessaria, estoque_disponivel_hub)

        if qtde_a_enviar > 0:
            # Registra o que a loja vai receber
            lista_recebimentos.append({
                'loja': loja_que_recebe['loja'],
                'Ref_Cor': ref_cor,
                'tamanho': tamanho,
                'movimentar': qtde_a_enviar,
                'enviar/receber': 'Receber'
            })
            # Atualiza (diminui) o estoque do hub
            hub_estoque[(ref_cor, tamanho)] -= qtde_a_enviar

    # 4. Criar os DataFrames de retorno
    # DataFrame com o que cada loja efetivamente recebeu
    df_recebido_pelas_lojas = pd.DataFrame(lista_recebimentos)
    # DataFrame com o estoque que sobrou no hub
    df_estoque_hub = hub_estoque[hub_estoque > 0].reset_index()
    
    if not df_estoque_hub.empty:
        df_estoque_hub['loja'] = 'HUB'
        df_estoque_hub['enviar/receber'] = 'Estoque Final'
        # Reordenar colunas para manter o padrão
        df_estoque_hub = df_estoque_hub[['loja', 'Ref_Cor', 'tamanho', 'movimentar', 'enviar/receber']]
    
    return df_recebido_pelas_lojas, df_estoque_hub



def converter_lojas_para_cnpj(df_transferencia):
    conn = conectar()
    if conn is None:
        return df_transferencia

    query = """
        SELECT
            loj.desc_apelido,
            SUBSTRING(loj.pk_cnpj, 1, 8) || '.' ||
            SUBSTRING(loj.pk_cnpj, 9, 4) || '.' ||
            SUBSTRING(loj.pk_cnpj, 13, 2) AS cnpj_formatado
        FROM live.dlojas loj;
    """
    try:
        df_lojas_cnpj = pd.read_sql_query(query, conn)
    finally:
        conn.close()

    # Cria um dicionário de mapeamento: {nome_loja: cnpj}
    mapa_cnpj = pd.Series(df_lojas_cnpj.cnpj_formatado.values, index=df_lojas_cnpj.desc_apelido).to_dict()

    df_convertido = df_transferencia.copy()
    
    # Aplica o mapeamento, mantendo o nome original se o CNPJ não for encontrado
    df_convertido['loja_origem'] = df_convertido['loja_origem'].map(mapa_cnpj).fillna(df_convertido['loja_origem'])
    df_convertido['loja_destino'] = df_convertido['loja_destino'].map(mapa_cnpj).fillna(df_convertido['loja_destino'])
    
    return df_convertido




if __name__ == '__main__':
    st.title("De/Para Estoque")
    caminho_arquivo = 'estoques_distribuir.csv'

    df_estoque = le_arquivo_csv(caminho_arquivo)
    if df_estoque is None:
        st.error("Não foi possível carregar o arquivo. Verifique o caminho ou o formato.")
        exit()

    df_recebido_hub, df_sobra_hub = distribuicao_hub(df_estoque)
    df_transformado = transformar_dados(df_estoque)
    #df_otimizado = otimiza_transferencias(df_transformado)
    
    ###########################################
    data_inicio = date(2025, 9, 22) #prazo!
    prazo_envio = 7
    min_itens_envio = 10
    max_rotas = 4
    ###########################################
    
    df_cronograma, dados_transferencia = cronograma_envio(df_transformado, prazo_envio, min_itens_envio, data_inicio, max_rotas)
    print(dados_transferencia)
    dados_transferencia_orion = converter_lojas_para_cnpj(dados_transferencia)

    #salvar_arquivo_csv(df_recebido_hub, 'hub_itens_recebidos_lojas.csv')
    #salvar_arquivo_csv(df_sobra_hub, 'hub_estoque_restante.csv')
    #salvar_arquivo_csv(df_transformado, 'estoque_distribuido.csv')
    salvar_arquivo_csv(df_cronograma, 'Cronograma_envio.csv')
    salvar_arquivo_csv(dados_transferencia, 'transferencias_entre_lojas.csv')
    salvar_arquivo_csv(dados_transferencia_orion, 'dados_transferencia.csv')
    
    #analise_dados(dados_transferencia, 'analise_estoque_inicial.html')

    #st.dataframe(df_transformado, use_container_width=True)    
    st.write("### Cronograma de Envios")
    st.dataframe(df_cronograma, use_container_width=True)

################################################
####### FUNÇÃO PARA PROCESSAR OS DADOS##########
################################################

from app.views import (
    le_arquivo_csv, distribuicao_hub, transformar_dados,
    cronograma_envio, converter_lojas_para_cnpj
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Armazena temporariamente os relatórios
RELATORIOS_TEMP = {}

# Upload do CSV e exibição da tabela
@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    file = request.files.get('arquivo')
    if not file:
        return "Nenhum arquivo enviado", 400

    caminho_arquivo = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(caminho_arquivo)

    df_estoque = le_arquivo_csv(caminho_arquivo)
    if df_estoque is None:
        return "Erro ao ler CSV", 400

    # Salva temporariamente para processar depois
    RELATORIOS_TEMP['df_estoque'] = df_estoque

    # Retorna tabela para front
    return df_estoque.to_json(orient='records')

# Processa os dados e gera os relatórios
@app.route('/processar', methods=['POST'])
def processar():
    df_estoque = RELATORIOS_TEMP.get('df_estoque')
    if df_estoque is None:
        return "Nenhum arquivo carregado", 400

    # 1️⃣ Distribuição Hub
    df_recebido_hub, df_sobra_hub = distribuicao_hub(df_estoque)

    # 2️⃣ Transformar dados e cronograma
    df_transformado = transformar_dados(df_estoque)
    data_inicio = date(2025, 9, 22)
    prazo_envio = 7
    min_itens_envio = 10
    max_rotas = 4

    df_cronograma, dados_transferencia = cronograma_envio(
        df_transformado, prazo_envio, min_itens_envio, data_inicio, max_rotas
    )

    # 3️⃣ Relatório para exportar
    dados_transferencia_orion = converter_lojas_para_cnpj(dados_transferencia)

    # Salva todos os relatórios temporariamente
    RELATORIOS_TEMP['df_recebido_hub'] = df_recebido_hub
    RELATORIOS_TEMP['df_sobra_hub'] = df_sobra_hub
    RELATORIOS_TEMP['df_cronograma'] = df_cronograma
    RELATORIOS_TEMP['dados_transferencia'] = dados_transferencia
    RELATORIOS_TEMP['dados_transferencia_orion'] = dados_transferencia_orion

    # Retorna apenas os 2 primeiros para exibir na tela
    return jsonify({
        "df_cronograma": df_cronograma.to_dict(orient='records'),
        "dados_transferencia": dados_transferencia.to_dict(orient='records')
    })

# Download do terceiro relatório
@app.route('/exportar_csv')
def exportar_csv():
    dados_transferencia_orion = RELATORIOS_TEMP.get('dados_transferencia_orion')

    if dados_transferencia_orion is None:
        return "Nenhum relatório gerado", 400

    caminho = os.path.join(UPLOAD_FOLDER, "dados_transferencia.csv")
    dados_transferencia_orion.to_csv(caminho, sep=";", index=False)
    return send_file(caminho, as_attachment=True)