import pandas as pd
from sqlalchemy.sql import text
from app import db
import re
from sqlalchemy.orm import joinedload
from app.models import Colunas, Dag, Origem, Tabela
from .sql_queries import sql_ultimas_updates, sql_data_atualizacao, sql_quantidade

def _format_updates_dataframe(df_updates):
    """Trata e formata as colunas de data/hora do DataFrame de atualizações."""
    if 'ultima_atividade_tabela' in df_updates.columns:
        # Converte para datetime e trata NaT (Not a Time)
        df_updates['ultima_atividade_tabela'] = pd.to_datetime(df_updates['ultima_atividade_tabela'])
        
        # Formata a coluna para string, tratando NaT
        df_updates['ultima_atividade_tabela'] = df_updates['ultima_atividade_tabela'].apply(
            lambda x: x.strftime('%d/%m/%Y %H:%M:%S') if pd.notnull(x) else 'Sem data'
        )
    
    return df_updates.to_dict('records')


def get_dashboard_data():
    """Busca todos os dados necessários para o dashboard do banco de dados."""
    
    postgres_engine = db.get_engine(bind='postgres_empresa')
    
    with postgres_engine.connect() as connection:
        
        # 1. Quantidade de esquemas e tabelas
        res_quantidade = connection.execute(sql_quantidade)
        df_quantidade = pd.DataFrame(res_quantidade.fetchall(), columns=res_quantidade.keys())
        
        numero_esquemas = len(df_quantidade)
        numero_tabelas = df_quantidade['quantidade_tabelas'].sum()

        # 2. Últimas atualizações (Logs)
        res_updates = connection.execute(sql_ultimas_updates)
        df_updates = pd.DataFrame(res_updates.fetchall(), columns=res_updates.keys())
        logs_atualizacao = _format_updates_dataframe(df_updates)

        # 3. Data da última atualização geral
        res_atualizacao = connection.execute(sql_data_atualizacao)
        ultima_atualizacao_formatada = res_atualizacao.scalar_one_or_none()
        
        if ultima_atualizacao_formatada is None:
            ultima_atualizacao_formatada = "N/A"
            
        # 4. Dados de quantidade formatados (Para o seu gráfico, se necessário)
        # Retorna o df completo caso o gráfico precise de dados por esquema
        df_quantidade_list = df_quantidade.to_dict('records') 
        
    return {
        'numero_esquemas': numero_esquemas,
        'numero_tabelas': numero_tabelas,
        'ultima_atualizacao': ultima_atualizacao_formatada,
        'logs_atualizacao': logs_atualizacao,
        'dados_grafico': df_quantidade_list # Inclui o dado que pode ser usado pelo gráfico
    }

def get_tabelas_por_esquema(nome_esquema):
    """
    Busca todas as tabelas associadas a um esquema específico no banco de dados.
    ESTA É A FUNÇÃO QUE ESTAVA FALTANDO OU ESTAVA VAZIA.
    """
    try:
        # A lógica real de consulta ao banco de dados deve estar aqui.
        # Exemplo usando Flask-SQLAlchemy:
        tabelas = Tabela.query.filter_by(esquema=nome_esquema).all()
        
        # Formata o resultado para a rota
        return tabelas
        
    except Exception as e:
        # É importante capturar exceções de DB na camada de Serviço.
        print(f"Erro ao buscar tabelas para o esquema {nome_esquema}: {e}")
        # Lança uma exceção para que a camada de rota possa tratá-la (ex: retornar 500)
        raise Exception("Falha na conexão ou consulta ao banco de dados.")
    
def parse_create_table_sql(sql_query):
    """
    Analisa uma query SQL 'CREATE TABLE' para extrair nomes e tipos de colunas.
    Esta função é uma lógica de NEGÓCIO/ANÁLISE.
    """
    sql_query = re.sub(r'--.*', '', sql_query)
    sql_query = re.sub(r'/\*.*?\*/', '', sql_query, flags=re.DOTALL)
    
    # Normaliza espaços
    sql_query = re.sub(r'\s+', ' ', sql_query).strip()
    
    match = re.search(r'\((.*)\)', sql_query, re.IGNORECASE | re.DOTALL)
    
    if not match:
        raise ValueError("Query SQL inválida: Não foi encontrado o corpo da definição da tabela.")

    table_body = match.group(1).strip()
    column_definitions = table_body.split(',')
    
    columns = []
    
    for definition in column_definitions:
        clean_def = definition.strip()
        if not clean_def:
            continue

        # Tenta casar o padrão: NOME_COLUNA TIPO_DADO RESTRIÇÕES
        match_col = re.match(r'^\s*"?([a-zA-Z_][a-zA-Z0-9_]*)"?\s+(.+)$', clean_def, re.IGNORECASE | re.DOTALL)
        
        if match_col:
            col_name = match_col.group(1)
            type_and_constraints = match_col.group(2).strip()
            
            columns.append({
                'nome': col_name,
                'tipo': type_and_constraints
            })
        else:
            # Ignora restrições de nível de tabela (PRIMARY KEY, FOREIGN KEY, CONSTRAINT)
            if 'primary key' in clean_def.lower() or 'foreign key' in clean_def.lower() or 'constraint' in clean_def.lower():
                continue
            
            # Se não for uma restrição de tabela, levanta um erro para notificar o usuário
            raise ValueError(f"Não foi possível analisar a definição de coluna: {clean_def}")

    return columns


def criar_tabela_completa(form):
    """
    Cria e persiste Tabela, Dag, Origem e Colunas de forma transacional.
    Esta é a lógica de PERSISTÊNCIA/NEGÓCIO.
    """
    sql_query = form.create_table_sql.data
    
    # 1. Lógica de Negócio: Analisar a query SQL (reutiliza a função acima)
    colunas_analisadas = parse_create_table_sql(sql_query)
    
    if not colunas_analisadas:
        raise ValueError("Nenhuma coluna válida foi extraída da query SQL.")

    try:
        # --- CRIAÇÃO DOS RELACIONAMENTOS ---
        dag = Dag(
            dag=form.dag.dag.data,
            schedule=form.dag.schedule.data
        )
        origem = Origem(
            sistema_origem=form.origem.sistema_origem.data,
            tabela_origem=form.origem.tabela_origem.data
        )

        db.session.add(dag)
        db.session.add(origem)
        db.session.flush() # Obtém os IDs dos objetos Dag e Origem

        # --- CRIAÇÃO DA TABELA PRINCIPAL ---
        tabela = Tabela(
            nome_tabela=form.nome_tabela.data,
            descricao_tabela=form.descricao_tabela.data,
            esquema=form.esquema.data,
            dag=dag,
            origem=origem
        )
        db.session.add(tabela)
        db.session.flush() # Obtém o ID da Tabela

        # --- CRIAÇÃO DAS COLUNAS ---
        for col_info in colunas_analisadas:
            coluna = Colunas(
                nome_coluna=col_info['nome'],
                tipo_dado=col_info['tipo'], 
                tabela=tabela 
            )
            db.session.add(coluna)
            
        db.session.commit()
        return tabela

    except Exception as e:
        db.session.rollback()
        # Repassa o erro de volta para a camada de rota para que o 'flash' seja exibido
        raise Exception(f"Erro de Transação no Banco de Dados: {e}")


# =========================================================
# LÓGICA DE CONSULTA (Busca de Dados)
# =========================================================

def get_todas_tabelas():
    """
    Busca todas as tabelas com os relacionamentos Dag e Origem carregados.
    Esta é a lógica de CONSULTA.
    """
    # Usa joinedload para carregar os relacionamentos em uma única consulta (performance)
    tabelas = Tabela.query.options(
        joinedload(Tabela.dag),
        joinedload(Tabela.origem)
    ).all()
    return tabelas


def get_tabelas_por_esquema(nome_esquema):
    """
    Busca tabelas por nome de esquema (usada na rota dinâmica).
    """
    tabelas = Tabela.query.filter_by(esquema=nome_esquema).all()
    return tabelas