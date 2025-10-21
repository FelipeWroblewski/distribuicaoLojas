import pandas as pd
from sqlalchemy.sql import text
from app import db
from app.models import Tabela
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