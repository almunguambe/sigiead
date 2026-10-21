import os
import sqlite3
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, g, has_request_context

app = Flask(__name__)

# =============================================================================
# DIVISÃO TERRITORIAL OFICIAL DE MOÇAMBIQUE (PROVÍNCIAS E DISTRITOS)
# =============================================================================
DIVISAO_TERRITORIAL = {
    "Inhambane": [
        "Maxixe (Cidade/Distrito)", "Inhambane (Cidade)", "Homoíne", "Jangamo",
        "Massinga", "Morrumbene", "Vilankulo", "Zavala", "Inharrime",
        "Panda", "Funhalouro", "Mabote", "Govuro"
    ],
    "Gaza": [
        "Xai-Xai (Cidade)", "Chókwè", "Bilene", "Chibuto", "Mandlakazi",
        "Guijá", "Mabalane", "Chigubo", "Chicualacuala", "Massingir", "Massangena", "Limpopo"
    ],
    "Maputo Província": [
        "Matola (Cidade)", "Boane", "Marracuene", "Manhiça", "Moamba", "Namaacha", "Matutuíne"
    ],
    "Maputo Cidade": [
        "KaMpfumo", "Nlhamankulu", "KaMaxakeni", "KaMavota", "KaMubukwana", "KaTembe", "KaNyaka"
    ],
    "Sofala": [
        "Beira (Cidade)", "Dondo", "Nhamatanda", "Búzi", "Gorongosa", "Cheringoma",
        "Marromeu", "Caia", "Chemba", "Machanga", "Muanza", "Chibabava"
    ],
    "Manica": [
        "Chimoio (Cidade)", "Gondola", "Manica", "Mossurize", "Sussundenga", "Báruè",
        "Guro", "Macossa", "Tambara", "Vanduzi", "Macate"
    ],
    "Tete": [
        "Tete (Cidade)", "Moatize", "Angónia", "Tsangano", "Mutarara", "Changara",
        "Cahora Bassa", "Magoe", "Zumbo", "Marávia", "Chifunde", "Macanga", "Dôa", "Marara"
    ],
    "Zambézia": [
        "Quelimane (Cidade)", "Mocuba", "Gurué", "Alto Molócue", "Milange", "Morrumbala",
        "Maganja da Costa", "Namacurra", "Nicoadala", "Pebane", "Gilé", "Ile", "Inhassunge",
        "Lugela", "Mopeia", "Chinde", "Derre", "Luabo", "Mulevala", "Molumbo"
    ],
    "Nampula": [
        "Nampula (Cidade)", "Nacala-Porto", "Angoche", "Ilha de Moçambique", "Monapo",
        "Meconta", "Mogovolas", "Murrupula", "Ribaue", "Malema", "Moma", "Mossuril",
        "Muecate", "Nacala-a-Velha", "Eráti", "Memba", "Lalaua", "Larde", "Liúpo"
    ],
    "Niassa": [
        "Lichinga (Cidade)", "Cuamba", "Mandimba", "Lago (Metangula)", "Sanga", "Mavago",
        "Marrupa", "Majune", "Mecanhelas", "Muembe", "Ngauma", "Nipepe", "Chimbonila"
    ],
    "Cabo Delgado": [
        "Pemba (Cidade)", "Montepuez", "Mocímboa da Praia", "Palma", "Mueda", "Chiúre",
        "Ancuabe", "Balama", "Namuno", "Meluco", "Macomia", "Quissanga", "Ibo", "Muidumbe"
    ]
}

from ensino_dados import CURRICULO_CLASSES, TODAS_LICOES, MAPA_LICOES
app.secret_key = os.environ.get('SECRET_KEY', 'iead_mz_multitenant_2026')

DATABASE_URL = os.environ.get('DATABASE_URL')

# =============================================================================
# MOTOR DE BASE DE DADOS HÍBRIDO (SUPABASE / POSTGRESQL & SQLITE)
# =============================================================================
import os
import sqlite3

DATABASE_URL = os.environ.get('DATABASE_URL', '').strip()
USAR_POSTGRES = bool(DATABASE_URL and 'postgres' in DATABASE_URL.lower())

if USAR_POSTGRES:
    import psycopg2
    from psycopg2.extras import RealDictCursor

def get_db():
    if has_request_context():
        conexao_valida = False
        if 'db' in g:
            try:
                if USAR_POSTGRES:
                    conexao_valida = (getattr(g.db, 'closed', 1) == 0)
                else:
                    conexao_valida = True
            except Exception:
                conexao_valida = False
        
        if not conexao_valida:
            if USAR_POSTGRES:
                import psycopg2
                g.db = psycopg2.connect(DATABASE_URL)
                g.db.autocommit = True
            else:
                import sqlite3
                g.db = sqlite3.connect('banco.db')
                g.db.row_factory = sqlite3.Row
        return g.db
    else:
        if USAR_POSTGRES:
            import psycopg2
            conn = psycopg2.connect(DATABASE_URL)
            conn.autocommit = True
            return conn
        else:
            import sqlite3
            conn = sqlite3.connect('banco.db')
            conn.row_factory = sqlite3.Row
            return conn

@app.teardown_appcontext
def fechar_conexao_db(exception=None):
    if has_request_context():
        db = g.pop('db', None)
        if db is not None:
            try:
                db.close()
            except Exception:
                pass

def executar_comando(sql, params=()):
    conn = get_db()
    try:
        if USAR_POSTGRES:
            with conn.cursor() as cur:
                if params:
                    sql_pg = sql.replace('?', '%s')
                    cur.execute(sql_pg, params)
                else:
                    cur.execute(sql)
        else:
            with conn:
                if params:
                    conn.execute(sql, params)
                else:
                    conn.execute(sql)
    except Exception as e:
        print(f"[ERRO DB EXECUTAR]: {e} | SQL: {sql}")
        if USAR_POSTGRES:
            try:
                conn.rollback()
            except Exception:
                pass
        raise e
    finally:
        if not has_request_context():
            try:
                conn.close()
            except Exception:
                pass

def consultar_todos(sql, params=()):
    conn = get_db()
    try:
        if USAR_POSTGRES:
            import psycopg2.extras
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                if params:
                    sql_pg = sql.replace('?', '%s')
                    cur.execute(sql_pg, params)
                else:
                    cur.execute(sql)
                res = cur.fetchall()
                return [dict(r) for r in res]
        else:
            cur = conn.cursor()
            if params:
                cur.execute(sql, params)
            else:
                cur.execute(sql)
            res = cur.fetchall()
            return [dict(r) for r in res]
    except Exception as e:
        print(f"[ERRO DB CONSULTAR TODOS]: {e} | SQL: {sql}")
        if USAR_POSTGRES:
            try:
                conn.rollback()
            except Exception:
                pass
        return []
    finally:
        if not has_request_context():
            try:
                conn.close()
            except Exception:
                pass

def consultar_um(sql, params=()):
    conn = get_db()
    try:
        if USAR_POSTGRES:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                if params:
                    sql_pg = sql.replace('?', '%s')
                    cur.execute(sql_pg, params)
                else:
                    cur.execute(sql)
                res = cur.fetchone()
                return dict(res) if res else None
        else:
            cur = conn.cursor()
            if params:
                cur.execute(sql, params)
            else:
                cur.execute(sql)
            res = cur.fetchone()
            return dict(res) if res else None
    except Exception as e:
        print(f"[ERRO DB CONSULTAR UM]: {e} | SQL: {sql}")
        if USAR_POSTGRES:
            try:
                conn.rollback()
            except Exception:
                pass
        return None
    finally:
        if not has_request_context():
            try:
                conn.close()
            except Exception:
                pass

def migrar_colunas_doutrina():
    conn = get_db()
    colunas = [
        ('licao_atual', "TEXT DEFAULT 'Lição 1'"),
        ('congregacao_id', "INTEGER DEFAULT 1"),
        ('classe', "TEXT DEFAULT 'Discipulado'"),
        ('professor', "TEXT DEFAULT 'Pastor Dirigente'"),
        ('data_inicio', "TEXT"),
        ('presencas', "INTEGER DEFAULT 0"),
        ('situacao', "TEXT DEFAULT 'Em Formação'"),
        ('usuario', "TEXT"),
        ('senha', "TEXT"),
        ('aproveitamento', "REAL DEFAULT 0.0"),
        ('criado_em', "TEXT")
    ]
    try:
        if USAR_POSTGRES:
            with conn.cursor() as cur:
                for col_name, col_def in colunas:
                    try:
                        cur.execute(f"ALTER TABLE doutrina ADD COLUMN IF NOT EXISTS {col_name} {col_def};")
                    except Exception:
                        pass
        else:
            cur = conn.cursor()
            cur.execute("PRAGMA table_info(doutrina)")
            existentes = [r[1] for r in cur.fetchall()]
            for col_name, col_def in colunas:
                if col_name not in existentes:
                    try:
                        cur.execute(f"ALTER TABLE doutrina ADD COLUMN {col_name} {col_def}")
                    except Exception:
                        pass
    except Exception as e:
        print(f"[AVISO MIGRACAO]: {e}")
    finally:
        if not has_request_context():
            try:
                conn.close()
            except Exception:
                pass

def inicializar_banco():
    is_pg = bool(DATABASE_URL)
    conn = get_db()
    cur = conn.cursor()
    pk = "SERIAL PRIMARY KEY" if is_pg else "INTEGER PRIMARY KEY AUTOINCREMENT"

    tabelas = [
        f"""CREATE TABLE IF NOT EXISTS congregacoes (
            id {pk}, nome TEXT, provincia TEXT, distrito TEXT, bairro TEXT, pastor_responsavel TEXT, criado_em TEXT
        );""",
        f"""CREATE TABLE IF NOT EXISTS usuarios_sistema (
            id {pk}, nome TEXT, usuario TEXT UNIQUE, senha TEXT, 
            nivel TEXT, perfil TEXT, congregacao_id INT DEFAULT 1, provincia TEXT, distrito TEXT, criado_em TEXT
        );""",
        f"""CREATE TABLE IF NOT EXISTS membros (id {pk}, congregacao_id INT DEFAULT 1, nome TEXT);""",
        f"""CREATE TABLE IF NOT EXISTS planificacao (id {pk}, congregacao_id INT DEFAULT 1, actividade TEXT);""",
        f"""CREATE TABLE IF NOT EXISTS novos_convertidos (id {pk}, congregacao_id INT DEFAULT 1, nome TEXT);""",
        f"""CREATE TABLE IF NOT EXISTS cultos (id {pk}, congregacao_id INT DEFAULT 1, data_culto TEXT);""",
        f"""CREATE TABLE IF NOT EXISTS caixa (id {pk}, congregacao_id INT DEFAULT 1, valor REAL);""",
        f"""CREATE TABLE IF NOT EXISTS doutrina (id {pk}, congregacao_id INT DEFAULT 1, nome_aluno TEXT);""",
        f"""CREATE TABLE IF NOT EXISTS casamentos (id {pk}, congregacao_id INT DEFAULT 1, noivo TEXT);""",
        f"""CREATE TABLE IF NOT EXISTS obitos (id {pk}, congregacao_id INT DEFAULT 1, nome_falecido TEXT);""",
        f"""CREATE TABLE IF NOT EXISTS opcoes_sistema (id {pk}, categoria TEXT, valor TEXT);""",
        f"""CREATE TABLE IF NOT EXISTS progresso_licoes (
            id {pk}, aluno_id INT, licao_id TEXT, resumo_aluno TEXT, nota_teste REAL DEFAULT 0, status TEXT, criado_em TEXT
        );""",
        f"""CREATE TABLE IF NOT EXISTS duvidas_alunos (
            id {pk}, aluno_id INT, licao_id TEXT, pergunta TEXT, resposta_sistema TEXT, resposta_professor TEXT, professor_nome TEXT, criado_em TEXT
        );""",
        f"""CREATE TABLE IF NOT EXISTS balanco_anual (
            id {pk}, congregacao_id INT DEFAULT 1, ano INT, constrangimento_1 TEXT, constrangimento_2 TEXT, constrangimento_3 TEXT,
            perspectiva_1 TEXT, perspectiva_2 TEXT, perspectiva_3 TEXT, atualizado_em TEXT
        );"""
    ]
    for sql in tabelas:
        try:
            cur.execute(sql)
            if hasattr(conn, 'commit'): conn.commit()
        except: pass

    if not is_pg:
        for t in ['membros', 'planificacao', 'novos_convertidos', 'cultos', 'caixa', 'doutrina', 'casamentos', 'obitos', 'balanco_anual']:
            try: cur.execute(f"ALTER TABLE {t} ADD COLUMN congregacao_id INT DEFAULT 1;")
            except: pass

        for col, tipo in [
            ('nome', 'TEXT'), ('contacto', 'TEXT'), ('bi', 'TEXT'), ('cargo', 'TEXT'),
            ('departamento', 'TEXT'), ('estado_civil', 'TEXT'), ('zona', 'TEXT'),
            ('celula', 'TEXT'), ('ano_conversao', 'TEXT'), ('data_batismo', 'TEXT'),
            ('local_residencia', 'TEXT'), ('bairro', 'TEXT'), ('genero', 'TEXT DEFAULT "Masculino"'), ('foto', 'TEXT'), ('criado_em', 'TEXT')
        ]:
            try: cur.execute(f"ALTER TABLE membros ADD COLUMN {col} {tipo};")
            except: pass

        for col, tipo in [
            ('tipo', 'TEXT'), ('categoria', 'TEXT'), ('valor', 'REAL'),
            ('descricao', 'TEXT'), ('data_movimento', 'TEXT'), ('conta', 'TEXT'),
            ('destino_tipo', 'TEXT'), ('departamento', 'TEXT'), ('proposito', 'TEXT'), ('criado_em', 'TEXT')
        ]:
            try: cur.execute(f"ALTER TABLE caixa ADD COLUMN {col} {tipo};")
            except: pass

        for col, tipo in [
            ('usuario', 'TEXT'), ('senha', 'TEXT'), ('aproveitamento', 'REAL DEFAULT 0'),
            ('classe', 'TEXT'), ('professor', 'TEXT'), ('situacao', 'TEXT DEFAULT "Em Formação"')
        ]:
            try: cur.execute(f"ALTER TABLE doutrina ADD COLUMN {col} {tipo};")
            except: pass

        for col, tipo in [
            ('tipo', 'TEXT'), ('noivo', 'TEXT'), ('noiva', 'TEXT'), ('data_casamento', 'TEXT'),
            ('ministro', 'TEXT'), ('regime', 'TEXT'), ('certidao', 'TEXT'), ('criado_em', 'TEXT')
        ]:
            try: cur.execute(f"ALTER TABLE casamentos ADD COLUMN {col} {tipo};")
            except: pass

        for col, tipo in [
            ('nome_falecido', 'TEXT'), ('genero', 'TEXT'), ('categoria', 'TEXT'),
            ('data_falecimento', 'TEXT'), ('local_funeral', 'TEXT'), ('causa', 'TEXT'), ('contacto_familia', 'TEXT'), ('criado_em', 'TEXT')
        ]:
            try: cur.execute(f"ALTER TABLE obitos ADD COLUMN {col} {tipo};")
            except: pass

        if hasattr(conn, 'commit'): conn.commit()
    conn.close()

    if not consultar_um("SELECT id FROM congregacoes WHERE id = 1"):
        sql_c = """INSERT INTO congregacoes (id, nome, provincia, distrito, bairro, pastor_responsavel, criado_em)
                    VALUES (1, 'Igreja de Chicuque', 'Inhambane', 'Maxixe (Cidade/Distrito)', 'Chicuque', 'Pastor Dirigente', ?)"""
        executar_comando(sql_c, (datetime.now().strftime('%Y-%m-%d %H:%M'),))

    perfis_padrao = [
        ('Administrador Geral', 'admin', 'admin123', 'geral', 'admin', 1, 'Inhambane', 'Maxixe (Cidade/Distrito)'),
        ('Pastor Presidente', 'pastor', 'pastor123', 'lideranca', 'lideranca', 1, 'Inhambane', 'Maxixe (Cidade/Distrito)'),
        ('Secretaria Executiva', 'secretaria', 'sec123', 'secretaria', 'secretario', 1, 'Inhambane', 'Maxixe (Cidade/Distrito)'),
        ('Tesouraria da Igreja', 'tesouraria', 'tesouro123', 'tesouraria', 'tesoureiro', 1, 'Inhambane', 'Maxixe (Cidade/Distrito)')
    ]
    for n, u, s, niv, perf, cid, prov, dist in perfis_padrao:
        existente = consultar_um("SELECT id FROM usuarios_sistema WHERE usuario = ?", (u,))
        if not existente:
            sql_u = """INSERT INTO usuarios_sistema (nome, usuario, senha, nivel, perfil, congregacao_id, provincia, distrito, criado_em)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
            executar_comando(sql_u, (n, u, s, niv, perf, cid, prov, dist, datetime.now().strftime('%Y-%m-%d %H:%M')))
        else:
            executar_comando("UPDATE usuarios_sistema SET perfil = ?, nivel = ? WHERE id = ?", (perf, niv, existente['id']))

    if not consultar_um("SELECT id FROM doutrina WHERE LOWER(usuario) = ?", ('anselmo',)):
        sql_al = """INSERT INTO doutrina 
                    (congregacao_id, nome_aluno, classe, professor, licao_atual, data_inicio, presencas, situacao, usuario, senha, aproveitamento, criado_em)
                    VALUES (1, 'Anselmo Munguambe', 'Classe I - Primeiros Passos', 'Pastor Dirigente', 'Lição 1 - O Pecado e o Perdão', '2026-01-01', 1, 'Em Formação', ?, ?, 0.0, ?)"""
        executar_comando(sql_al, ('anselmo', '123456', datetime.now().strftime('%Y-%m-%d %H:%M')))

inicializar_banco()

# Garantir conta de professor ativa
if not consultar_um("SELECT id FROM usuarios_sistema WHERE usuario = 'professor'"):
    executar_comando("INSERT INTO usuarios_sistema (nome, usuario, senha, nivel, perfil, congregacao_id, criado_em) VALUES ('Professor de Doutrina', 'professor', 'prof123', 'local', 'professor', 1, '2026-10-19 23:00')")


# Garantir nome correto de Chicuque como congregação com suas zonas
executar_comando("UPDATE congregacoes SET nome = 'Igreja de Chicuque' WHERE id = 1 OR nome LIKE ?", ('%Sede Regional%',))


# =============================================================================
# CURRÍCULO DE ENSINO: CONTEÚDO INTEGRAL DO MANUAL DA IEADAO
# =============================================================================
# Curriculo importado de ensino_dados.py

# =============================================================================
# CONTEXT PROCESSOR: DADOS ISOLADOS POR CONGREGAÇÃO (MULTI-TENANT)
# =============================================================================
@app.context_processor
def injetar_dados():
    u_id = session.get('usuario_id')
    user = consultar_um("SELECT * FROM usuarios_sistema WHERE id = ?", (u_id,)) if u_id else None
    cid = session.get('congregacao_id', 1)
    
    cong = consultar_um("SELECT * FROM congregacoes WHERE id = ?", (cid,)) or {
        'id': 1, 'nome': 'Assembleia de Deus', 'distrito': 'Maxixe (Cidade/Distrito)', 'provincia': 'Inhambane', 'pastor_responsavel': 'Pastor Dirigente'
    }

    # TODAS AS CONSULTAS ESTÃO ISOLADAS POR CONGREGAÇÃO
    membros = consultar_todos("SELECT * FROM membros WHERE congregacao_id = ? ORDER BY id DESC", (cid,))
    planos = consultar_todos("SELECT * FROM planificacao WHERE congregacao_id = ? ORDER BY id DESC", (cid,))
    cultos = consultar_todos("SELECT * FROM cultos WHERE congregacao_id = ? ORDER BY id DESC", (cid,))
    convertidos = consultar_todos("SELECT * FROM novos_convertidos WHERE congregacao_id = ? ORDER BY id DESC", (cid,))
    caixa = consultar_todos("SELECT * FROM caixa WHERE congregacao_id = ? ORDER BY id DESC", (cid,))
    doutrina = consultar_todos("SELECT * FROM doutrina ORDER BY id DESC")
    casamentos = consultar_todos("SELECT * FROM casamentos WHERE congregacao_id = ? ORDER BY id DESC", (cid,))
    obitos = consultar_todos("SELECT * FROM obitos WHERE congregacao_id = ? ORDER BY id DESC", (cid,))
    
    # Utilizadores desta congregação
    if user and user.get('perfil') == 'admin' and user.get('usuario') == 'admin':
        usuarios_todos = consultar_todos("SELECT id, nome, usuario, perfil, nivel, congregacao_id, criado_em FROM usuarios_sistema ORDER BY id ASC")
    else:
        usuarios_todos = consultar_todos("SELECT id, nome, usuario, perfil, nivel, congregacao_id, criado_em FROM usuarios_sistema WHERE congregacao_id = ? ORDER BY id ASC", (cid,))
    
    congregacoes_todas = consultar_todos("SELECT * FROM congregacoes ORDER BY provincia, distrito, nome ASC")
    duvidas_pendentes = consultar_todos("SELECT * FROM duvidas_alunos ORDER BY id DESC")
    opcoes_lista = consultar_todos("SELECT * FROM opcoes_sistema ORDER BY categoria, valor ASC")

    opcoes_map = {}
    for op in opcoes_lista:
        opcoes_map.setdefault(op['categoria'], []).append(op)

    # Demografia isolada
    total_homens = len([m for m in membros if str(m.get('genero') or '').lower() in ['masculino', 'homem', 'h']])
    total_mulheres = len(membros) - total_homens
    total_criancas = len([m for m in membros if str(m.get('estado_civil') or '').lower() == 'criança' or 'esperança' in str(m.get('departamento') or '').lower()])
    total_jovens = len([m for m in membros if 'jov' in str(m.get('departamento') or '').lower() or 'jovem' in str(m.get('cargo') or '').lower()])
    total_adultos = max(0, len(membros) - total_criancas - total_jovens)
    total_batizados = len([m for m in membros if m.get('data_batismo')])
    total_nao_batizados = len(membros) - total_batizados

    zonas_contagem = {}
    celulas_contagem = {}
    cargos_contagem = {}
    for m in membros:
        z = m.get('zona') or 'Zona 1 - Central'
        zonas_contagem[z] = zonas_contagem.get(z, 0) + 1
        c = m.get('celula') or 'Célula Betel'
        celulas_contagem[c] = celulas_contagem.get(c, 0) + 1
        cg = m.get('cargo') or 'Membro em Comunhão'
        cargos_contagem[cg] = cargos_contagem.get(cg, 0) + 1

    total_pres = sum([int(c.get('total_presentes') or 0) for c in cultos])
    media_culto = int(total_pres / len(cultos)) if cultos else 0

    # Finanças isoladas
    total_entradas = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Entrada'])
    total_saidas = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Saída'])
    saldo_caixa = total_entradas - total_saidas

    entradas_caixa_fisico = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Entrada' and 'banco' not in str(c.get('conta', '')).lower()])
    saidas_caixa_fisico = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Saída' and 'banco' not in str(c.get('conta', '')).lower()])
    saldo_caixa_fisico = entradas_caixa_fisico - saidas_caixa_fisico

    entradas_banco = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Entrada' and 'banco' in str(c.get('conta', '')).lower()])
    saidas_banco = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Saída' and 'banco' in str(c.get('conta', '')).lower()])
    saldo_banco = entradas_banco - saidas_banco

    geral_in = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Entrada' and str(c.get('destino_tipo', 'Igreja Geral')) == 'Igreja Geral'])
    geral_out = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Saída' and str(c.get('destino_tipo', 'Igreja Geral')) == 'Igreja Geral'])

    mae_in = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Entrada' and str(c.get('destino_tipo', '')) == 'Igreja Mãe'])
    mae_out = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Saída' and str(c.get('destino_tipo', '')) == 'Igreja Mãe'])

    depto_in = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Entrada' and str(c.get('destino_tipo', '')) == 'Departamento'])
    depto_out = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Saída' and str(c.get('destino_tipo', '')) == 'Departamento'])

    total_dizimos = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Entrada' and 'dízimo' in str(c.get('categoria', '')).lower()])
    total_ofertas = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Entrada' and 'oferta' in str(c.get('categoria', '')).lower()])
    total_missoes = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Entrada' and ('miss' in str(c.get('categoria', '')).lower() or 'evangel' in str(c.get('categoria', '')).lower())])
    total_construcao = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Entrada' and ('constru' in str(c.get('categoria', '')).lower() or 'obra' in str(c.get('categoria', '')).lower() or 'tijol' in str(c.get('categoria', '')).lower() or 'cimento' in str(c.get('categoria', '')).lower())])
    taxa_gasto = int((total_saidas / total_entradas * 100)) if total_entradas > 0 else 0

    categorias_caixa_valores = {}
    for c in caixa:
        cat = c.get('categoria') or 'Geral'
        categorias_caixa_valores[cat] = categorias_caixa_valores.get(cat, 0.0) + float(c.get('valor') or 0)

    planos_executados = len([p for p in planos if p.get('status') == 'Executado'])
    taxa_execucao = int((planos_executados / len(planos) * 100)) if planos else 0

    return {
        'usuario_logado': user,
        'usuarios_todos': usuarios_todos,
        'congregacao': cong,
        'congregacoes_todas': congregacoes_todas,
        'divisao_territorial': DIVISAO_TERRITORIAL,
        'membros': membros, 'planificacoes': planos, 'cronograma': planos,
        'cultos': cultos, 'convertidos': convertidos, 'caixa': caixa,
        'doutrina': doutrina, 'casamentos': casamentos, 'obitos': obitos,
        'duvidas_pendentes': duvidas_pendentes, 'opcoes': opcoes_map,
        'demografia': {
            'total_almas': len(membros) + len(convertidos),
            'membros_cadastrados': len(membros),
            'homens': total_homens,
            'mulheres': total_mulheres,
            'perc_mulheres': int((total_mulheres / len(membros) * 100)) if membros else 50,
            'perc_homens': int((total_homens / len(membros) * 100)) if membros else 50,
            'criancas': total_criancas,
            'jovens': total_jovens,
            'adultos': total_adultos,
            'batizados': total_batizados,
            'nao_batizados': total_nao_batizados,
            'novos_convertidos': len(convertidos),
            'total_cultos': len(cultos),
            'media_culto': media_culto,
            'total_casamentos': len(casamentos),
            'total_obitos': len(obitos),
            'zonas': zonas_contagem,
            'celulas': celulas_contagem,
            'cargos': cargos_contagem,
            'planos_total': len(planos),
            'planos_executados': planos_executados,
            'taxa_execucao': taxa_execucao
        },
        'kpis': {
            'total_membros': len(membros),
            'total_planos': len(planos),
            'planos_executados': planos_executados,
            'taxa_execucao': taxa_execucao,
            'total_cultos': len(cultos),
            'media_assistencia': media_culto,
            'total_convertidos': len(convertidos),
            'total_entradas': total_entradas,
            'total_saidas': total_saidas,
            'saldo_caixa': saldo_caixa,
            'saldo_caixa_fisico': saldo_caixa_fisico,
            'saldo_banco': saldo_banco,
            'geral_in': geral_in, 'geral_out': geral_out,
            'mae_in': mae_in, 'mae_out': mae_out,
            'depto_in': depto_in, 'depto_out': depto_out,
            'total_dizimos': total_dizimos, 'total_ofertas': total_ofertas,
            'total_missoes': total_missoes, 'total_construcao': total_construcao, 'taxa_gasto': taxa_gasto,
            'categorias_caixa': categorias_caixa_valores,
            'total_doutrina': len(doutrina)
        }
    }

# =============================================================================
# ROTAS DE AUTENTICAÇÃO, LOGOUT E NAVEGAÇÃO SEGURA POR PERFIS
# =============================================================================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/ensino/logout')
def aluno_logout():
    session.clear()
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('usuario', '').strip()
        s = request.form.get('senha', '').strip()
        user = None
        
        # Tentativa 1: PostgreSQL / Supabase (%s)
        try:
            user = consultar_um("SELECT * FROM usuarios_sistema WHERE LOWER(usuario) = LOWER(%s) AND senha = %s", (u, s))
        except Exception:
            # Tentativa 2: SQLite (?)
            try:
                user = consultar_um("SELECT * FROM usuarios_sistema WHERE LOWER(usuario) = LOWER(?) AND senha = ?", (u, s))
            except Exception as err:
                print("Erro na consulta de login:", err)
                user = None

        if user:
            session['usuario'] = dict(user)
            perfil = str(user.get('perfil', '')).lower()
            
            # Se for professor, entra direto em Doutrina
            if any(p in perfil for p in ['prof', 'docente', 'instrutor']):
                return redirect('/?aba=doutrina')
            
            # Administrador entra no Dashboard geral
            return redirect('/?aba=dashboard')
        
        flash('Utilizador ou palavra-passe incorretos.', 'danger')
    return render_template('login.html')


@app.route('/')
def index():
    if not session.get('usuario'):
        return redirect(url_for('login'))
    
    usuario = session.get('usuario')
    doutrina = consultar_todos("SELECT * FROM doutrina ORDER BY id DESC")
    try:
        duvidas = consultar_todos("SELECT * FROM duvidas_alunos ORDER BY id DESC")
    except Exception:
        duvidas = []
    return render_template('area_professor.html',
                           usuario_logado=usuario,
                           doutrina=doutrina,
                           duvidas=duvidas)


@app.route('/ensino/aulas')
def sala_aulas_virtual():
    if not session.get('usuario'):
        return redirect(url_for('login'))
    usuario = session.get('usuario')
    try:
        doutrina = consultar_todos("SELECT * FROM doutrina ORDER BY id DESC")
    except Exception:
        doutrina = []
    return render_template('ensino_aulas.html',
                           usuario_logado=usuario,
                           doutrina=doutrina)

