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
from sqlalchemy import desc, text
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

from app.services.data_service import get_dashboard_data

from app.auth.auth_routes import auth_bp
from app.main.home_routes import home_bp
from app.esquemas.esquemas_routes import esquemas_bp
from app.detailsTable.detailsTable_routes import detailsTable_bp
from app.createTable.createTable_routes import createTableBp


UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')

@app.after_request
def add_header(response):
    response.cache_control.no_store = True
    return response

app.register_blueprint(auth_bp)

app.register_blueprint(home_bp)

app.register_blueprint(detailsTable_bp)

app.register_blueprint(esquemas_bp)

app.register_blueprint(createTableBp)

@app.route('/pesquisar', methods=['GET'])
@login_required
def pesquisar():
    termo_pesquisa = request.args.get('termo', '')

    app.logger.debug("-" * 50)
    app.logger.debug(f"[DEBUG 1] Termo recebido: '{termo_pesquisa}'")
    
    if not termo_pesquisa:
        return redirect(url_for('main.home'))

    # Gera o filtro SQL para pesquisa flexível (ex: '%termo%')
    filtro = f"%{termo_pesquisa}%"
    app.logger.debug(f"[DEBUG 2] Filtro de busca (LIKE): '{filtro}'")

    # TESTE DE CONEXÃO: Tenta buscar todos os itens para garantir que a tabela é acessível
    todos_itens = Tabela.query.all()
    app.logger.debug(f"[DEBUG 3] Total de itens na tabela 'tabela': {len(todos_itens)}")
    if len(todos_itens) == 0:
        app.logger.warning("[AVISO CRÍTICO] A tabela está vazia. Verifique a string de conexão ou se os dados foram commitados.")
    
    # --- PONTO CHAVE: EXECUÇÃO DA BUSCA ---
    tabela_encontrada = Tabela.query.filter(
        Tabela.nome_tabela.ilike(filtro)
    ).first()
    # --------------------------------------
    
    app.logger.debug(f"[DEBUG 4] Resultado da query: {tabela_encontrada}")

    if tabela_encontrada:
        # SUCESSO: Redireciona
        app.logger.debug(f"[DEBUG 5] SUCESSO! Redirecionando para ID: {tabela_encontrada.id}")
        app.logger.debug("-" * 50)
        return redirect(url_for('detailsTable.detalhesTabela', tabela_id=tabela_encontrada.id))
    else:
        # FALHA: Retorna para a home
        app.logger.debug(f"[DEBUG 5] FALHA. Objeto Tabela é None. Voltando para home.")
        app.logger.debug("-" * 50)
        return redirect(url_for('main.home'))


################################################
######## PAGE DISTRIBUICAO DE PRODUTOS #########
################################################

@app.route('/distribuicao/')
@login_required
def distribuicao():
    return render_template('distribuicao.html', tabelaDistribuicao="")  # começa vazio

################################################
#### FUNÇÃO PARA PROCESSAR AS TABELAS  #########
################################################


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

@app.route('/dados_grafico', methods=['GET'])
def dados_grafico():

    sql_tamanho = text("""
        SELECT
            nspname AS esquema,
            COALESCE(SUM(pg_total_relation_size(C.oid)), 0) AS tamanho_bytes,
            pg_size_pretty(COALESCE(SUM(pg_total_relation_size(C.oid)), 0)) AS tamanho_Formatado
        FROM pg_class C
            LEFT JOIN pg_namespace n
                ON n.oid = C.relnamespace
        WHERE nspname NOT IN ('pg_catalog', 'pg_toast', 'information_schema')
        GROUP BY nspname
          ORDER BY nspname ASC;
    """)

    sql_quantidade = text("""
        SELECT
            n.nspname AS esquema,
            COUNT(c.relname) AS quantidade_tabelas
        FROM
            pg_class c
        JOIN
            pg_namespace n ON n.oid = c.relnamespace
        WHERE
            c.relkind IN ('r')
            AND n.nspname NOT LIKE 'pg\_%' ESCAPE '\'
            AND n.nspname <> 'information_schema'
            AND n.nspname NOT IN ('pg_catalog', 'pg_toast', 'information_schema')
        GROUP BY
            n.nspname
        ORDER BY n.nspname ASC; 
    """)
    
    try:
        postgres_engine = db.get_engine(bind='postgres_empresa')
        
        with postgres_engine.connect() as connection:

            res_tamanho = connection.execute(sql_tamanho) 
            df_tamanho = pd.DataFrame(res_tamanho.fetchall(), columns=res_tamanho.keys())
            
            res_quantidade = connection.execute(sql_quantidade)
            df_quantidade = pd.DataFrame(res_quantidade.fetchall(), columns=res_quantidade.keys())

            df_tamanho = df_tamanho.set_index('esquema')
            df_quantidade = df_quantidade.set_index('esquema')      

            df_final = df_tamanho.join(df_quantidade, how='outer').fillna(0)  

            numero_esquemas = len(df_final)

            df_final = df_final.reset_index()
        
            df_final['tamanho_bytes'] = df_final['tamanho_bytes'].astype(int)
            df_final['quantidade_tabelas'] = df_final['quantidade_tabelas'].astype(int)
                        
            dados_grafico_json = df_final.to_dict(orient='records')
        
        return jsonify(dados_grafico_json)

    except Exception as e:
        return jsonify({"erro": f"Falha na conexão ao DB da empresa (bind). Detalhes: {str(e)}"}), 500

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