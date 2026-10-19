import os
import psycopg2

URL_SUPABASE = "postgresql://postgres.okkdueivpeefwqdktdjs:MunguambeAnselmo@aws-1-eu-central-1.pooler.supabase.com:5432/postgres?sslmode=require"

print("=" * 80)
print("A CONECTAR AO SUPABASE VIA POOLER (aws-1) E A CRIAR AS TABELAS DO SIGIEAD...")
print("=" * 80)

try:
    conn = psycopg2.connect(URL_SUPABASE)
    cur = conn.cursor()
    print("✓ Ligação ao Supabase estabelecida com sucesso!")

    # 1. Criar tabelas essenciais no PostgreSQL do Supabase
    tabelas = [
        """CREATE TABLE IF NOT EXISTS congregacoes (
            id SERIAL PRIMARY KEY, nome TEXT, provincia TEXT, distrito TEXT, bairro TEXT, pastor_responsavel TEXT, criado_em TEXT
        );""",
        """CREATE TABLE IF NOT EXISTS usuarios_sistema (
            id SERIAL PRIMARY KEY, nome TEXT, usuario TEXT UNIQUE, senha TEXT, 
            nivel TEXT, perfil TEXT, congregacao_id INT DEFAULT 1, provincia TEXT, distrito TEXT, criado_em TEXT
        );""",
        """CREATE TABLE IF NOT EXISTS membros (
            id SERIAL PRIMARY KEY, congregacao_id INT DEFAULT 1, nome TEXT, contacto TEXT, bi TEXT, cargo TEXT, 
            departamento TEXT, estado_civil TEXT, zona TEXT, celula TEXT, ano_conversao TEXT, data_batismo TEXT, 
            local_residencia TEXT, bairro TEXT, genero TEXT DEFAULT 'Masculino', foto TEXT, criado_em TEXT
        );""",
        """CREATE TABLE IF NOT EXISTS planificacao (
            id SERIAL PRIMARY KEY, congregacao_id INT DEFAULT 1, actividade TEXT, titulo TEXT, nome_actividade TEXT, 
            departamento TEXT, tipo_evento TEXT, data_prevista TEXT, data_inicio TEXT, data_execucao TEXT, 
            frequencia TEXT, responsavel TEXT, contacto TEXT, status TEXT, feedback TEXT, dificuldades TEXT, 
            perspectivas TEXT, participantes_homens INT DEFAULT 0, participantes_mulheres INT DEFAULT 0, 
            participantes_jovens INT DEFAULT 0, participantes_criancas INT DEFAULT 0, total_participantes INT DEFAULT 0, criado_em TEXT
        );""",
        """CREATE TABLE IF NOT EXISTS novos_convertidos (
            id SERIAL PRIMARY KEY, congregacao_id INT DEFAULT 1, nome TEXT, telefone TEXT, bairro TEXT, 
            data_decisao TEXT, quem_convidou TEXT, culto_origem TEXT, status_discipulado TEXT, criado_em TEXT
        );""",
        """CREATE TABLE IF NOT EXISTS cultos (
            id SERIAL PRIMARY KEY, congregacao_id INT DEFAULT 1, data_culto TEXT, tipo_culto TEXT, 
            homens_adultos INT DEFAULT 0, mulheres_adultas INT DEFAULT 0, jovens_rapazes INT DEFAULT 0, 
            jovens_mocas INT DEFAULT 0, criancas_meninos INT DEFAULT 0, criancas_meninas INT DEFAULT 0, 
            visitantes_homens INT DEFAULT 0, visitantes_mulheres INT DEFAULT 0, apelos INT DEFAULT 0, 
            total_presentes INT DEFAULT 0, pregador TEXT, tema_mensagem TEXT, criado_em TEXT
        );""",
        """CREATE TABLE IF NOT EXISTS caixa (
            id SERIAL PRIMARY KEY, congregacao_id INT DEFAULT 1, tipo TEXT, categoria TEXT, valor REAL, 
            descricao TEXT, data_movimento TEXT, conta TEXT, destino_tipo TEXT, departamento TEXT, proposito TEXT, criado_em TEXT
        );""",
        """CREATE TABLE IF NOT EXISTS doutrina (
            id SERIAL PRIMARY KEY, congregacao_id INT DEFAULT 1, nome_aluno TEXT, classe TEXT, professor TEXT, 
            licao_atual TEXT, data_inicio TEXT, presencas INT DEFAULT 1, situacao TEXT, usuario TEXT, 
            senha TEXT, aproveitamento REAL DEFAULT 0.0, criado_em TEXT
        );""",
        """CREATE TABLE IF NOT EXISTS casamentos (
            id SERIAL PRIMARY KEY, congregacao_id INT DEFAULT 1, tipo TEXT, noivo TEXT, noiva TEXT, 
            data_casamento TEXT, ministro TEXT, regime TEXT, certidao TEXT, criado_em TEXT
        );""",
        """CREATE TABLE IF NOT EXISTS obitos (
            id SERIAL PRIMARY KEY, congregacao_id INT DEFAULT 1, nome_falecido TEXT, genero TEXT, 
            categoria TEXT, data_falecimento TEXT, local_funeral TEXT, causa TEXT, contacto_familia TEXT, criado_em TEXT
        );""",
        """CREATE TABLE IF NOT EXISTS opcoes_sistema (
            id SERIAL PRIMARY KEY, categoria TEXT, valor TEXT
        );""",
        """CREATE TABLE IF NOT EXISTS progresso_licoes (
            id SERIAL PRIMARY KEY, aluno_id INT, licao_id TEXT, resumo_aluno TEXT, 
            nota_teste REAL DEFAULT 0, status TEXT, criado_em TEXT
        );""",
        """CREATE TABLE IF NOT EXISTS duvidas_alunos (
            id SERIAL PRIMARY KEY, aluno_id INT, licao_id TEXT, pergunta TEXT, 
            resposta_sistema TEXT, resposta_professor TEXT, professor_nome TEXT, criado_em TEXT
        );""",
        """CREATE TABLE IF NOT EXISTS balanco_anual (
            id SERIAL PRIMARY KEY, congregacao_id INT DEFAULT 1, ano INT, constrangimento_1 TEXT, 
            constrangimento_2 TEXT, constrangimento_3 TEXT, perspectiva_1 TEXT, perspectiva_2 TEXT, 
            perspectiva_3 TEXT, atualizado_em TEXT
        );"""
    ]

    for sql in tabelas:
        cur.execute(sql)
    conn.commit()
    print("✓ Todas as 14 tabelas foram criadas/verificadas com sucesso no Supabase!")

    # 2. Inserir congregação inicial e utilizadores padrão se não existirem
    cur.execute("SELECT id FROM congregacoes WHERE id = 1;")
    if not cur.fetchone():
        cur.execute("""INSERT INTO congregacoes (id, nome, provincia, distrito, bairro, pastor_responsavel, criado_em)
                       VALUES (1, 'Igreja de Chicuque', 'Inhambane', 'Maxixe (Cidade/Distrito)', 'Chicuque', 'Pastor Dirigente', '2026-10-19 22:00');""")
        conn.commit()
        print("✓ Congregação 'Igreja de Chicuque' inserida!")

    cur.execute("SELECT id FROM usuarios_sistema WHERE usuario = 'admin';")
    if not cur.fetchone():
        cur.execute("""INSERT INTO usuarios_sistema (nome, usuario, senha, nivel, perfil, congregacao_id, provincia, distrito, criado_em)
                       VALUES ('Administrador Geral', 'admin', 'admin123', 'geral', 'admin', 1, 'Inhambane', 'Maxixe (Cidade/Distrito)', '2026-10-19 22:00');""")
        cur.execute("""INSERT INTO usuarios_sistema (nome, usuario, senha, nivel, perfil, congregacao_id, provincia, distrito, criado_em)
                       VALUES ('Secretaria Executiva', 'secretaria', 'sec123', 'secretaria', 'secretario', 1, 'Inhambane', 'Maxixe (Cidade/Distrito)', '2026-10-19 22:00');""")
        cur.execute("""INSERT INTO usuarios_sistema (nome, usuario, senha, nivel, perfil, congregacao_id, provincia, distrito, criado_em)
                       VALUES ('Tesouraria da Igreja', 'tesouraria', 'tesouro123', 'tesouraria', 'tesoureiro', 1, 'Inhambane', 'Maxixe (Cidade/Distrito)', '2026-10-19 22:00');""")
        cur.execute("""INSERT INTO usuarios_sistema (nome, usuario, senha, nivel, perfil, congregacao_id, provincia, distrito, criado_em)
                       VALUES ('Pastor Presidente', 'pastor', 'pastor123', 'lideranca', 'lideranca', 1, 'Inhambane', 'Maxixe (Cidade/Distrito)', '2026-10-19 22:00');""")
        conn.commit()
        print("✓ Contas padrão (admin, secretaria, tesouraria, pastor) ativadas no Supabase!")

    cur.close()
    conn.close()
    print("=" * 80)
    print(">>> SUCESSO! A BASE DE DADOS SUPABASE ESTÁ 100% OPERACIONAL! <<<")
    print("=" * 80)

except Exception as e:
    print(f"\n[ERRO NA CONEXÃO]: {e}")