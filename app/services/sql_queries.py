from sqlalchemy import text


sql_ultimas_updates = text("""
        SELECT
            n.nspname AS esquema,
            c.relname AS nome_tabela,
            -- Calcula a data mais recente de qualquer atividade de manutenção.
            GREATEST(
                stat.last_vacuum, 
                stat.last_analyze, 
                stat.last_autovacuum, 
                stat.last_autoanalyze
            ) AS ultima_atividade_tabela,
            -- Mostra o número de tuplas (linhas) inseridas desde a última coleta de estatísticas
            stat.n_tup_ins AS tuplas_inseridas
        FROM
            pg_stat_all_tables stat
        JOIN
            pg_class c ON c.oid = stat.relid
        JOIN
            pg_namespace n ON n.oid = c.relnamespace
        WHERE
            c.relkind IN ('r') -- Apenas tabelas reais
            AND n.nspname NOT IN ('pg_catalog', 'information_schema', 'pg_toast') -- Exclui esquemas do sistema
        ORDER BY
            ultima_atividade_tabela DESC -- Ordena da mais recente para a mais antiga
        LIMIT 10; -- Limita a, por exemplo, as 10 atualizações mais recentes
    """)

sql_data_atualizacao = text("""
        SELECT
            TO_CHAR(MAX(ultima_atividade), 'DD/MM/YYYY HH24:MI:SS') AS ultima_atualizacao_dw_formatada
        FROM
            (
                SELECT
                    GREATEST(
                        stat.last_vacuum, 
                        stat.last_analyze,
                        stat.last_autovacuum,
                        stat.last_autoanalyze,
                        NOW()
                    ) AS ultima_atividade
                FROM
                    pg_stat_all_tables stat
                JOIN
                    pg_class c ON c.oid = stat.relid
                JOIN
                    pg_namespace n ON n.oid = c.relnamespace
                WHERE
                    c.relkind IN ('r') 
                    AND n.nspname NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
            ) AS subquery;
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

