import re
import py_compile

print("=" * 80)
print("A IMPLEMENTAR MOTOR UNIVERSAL POSTGRESQL/SUPABASE EM APP.PY...")
print("=" * 80)

caminho_app = 'app.py'
with open(caminho_app, 'r', encoding='utf-8') as f:
    codigo = f.read()

# Novo bloco robusto de acesso à base de dados com auto-tradução de ? para %s e commit garantido
novo_motor_db = '''# =============================================================================
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
    if USAR_POSTGRES:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True  # Garante gravação imediata no Supabase
        return conn
    else:
        conn = sqlite3.connect('igreja.db')
        conn.row_factory = sqlite3.Row
        return conn

def executar_comando(sql, params=()):
    conn = get_db()
    try:
        if USAR_POSTGRES:
            # Converte marcadores SQLite (?) para marcadores PostgreSQL (%s)
            sql_pg = sql.replace('?', '%s')
            with conn.cursor() as cur:
                cur.execute(sql_pg, params)
            conn.commit()
        else:
            with conn:
                conn.execute(sql, params)
    except Exception as e:
        print(f"[ERRO DB EXECUTAR]: {e} | SQL: {sql}")
        raise e
    finally:
        conn.close()

def consultar_todos(sql, params=()):
    conn = get_db()
    try:
        if USAR_POSTGRES:
            sql_pg = sql.replace('?', '%s')
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql_pg, params)
                res = cur.fetchall()
                return [dict(r) for r in res]
        else:
            cur = conn.cursor()
            cur.execute(sql, params)
            res = cur.fetchall()
            return [dict(r) for r in res]
    except Exception as e:
        print(f"[ERRO DB CONSULTAR TODOS]: {e} | SQL: {sql}")
        return []
    finally:
        conn.close()

def consultar_um(sql, params=()):
    conn = get_db()
    try:
        if USAR_POSTGRES:
            sql_pg = sql.replace('?', '%s')
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql_pg, params)
                res = cur.fetchone()
                return dict(res) if res else None
        else:
            cur = conn.cursor()
            cur.execute(sql, params)
            res = cur.fetchone()
            return dict(res) if res else None
    except Exception as e:
        print(f"[ERRO DB CONSULTAR UM]: {e} | SQL: {sql}")
        return None
    finally:
        conn.close()
'''

# Substitui as antigas funções get_db, executar_comando, consultar_todos e consultar_um
padrao_antigo = r"def get_db\(\):[\s\S]*?def consultar_um\(sql, params=\(\)\):[\s\S]*?finally:\s*conn\.close\(\)"

if re.search(padrao_antigo, codigo):
    codigo = re.sub(padrao_antigo, novo_motor_db, codigo)
    with open(caminho_app, 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✓ Funções de base de dados atualizadas com autocommit e tradução automática de parâmetros!")
else:
    print("Aviso: Padrão exato não encontrado por regex. A aplicar injeção segura de cabeçalho...")
    # Se não coincidir exatamente, substitui desde a primeira menção de get_db
    partes = codigo.split("def get_db():")
    resto = partes[1]
    fim_consultar_um = resto.find("def inicializar_banco():")
    if fim_consultar_um != -1:
        codigo = partes[0] + novo_motor_db + "\n\n" + resto[fim_consultar_um:]
        with open(caminho_app, 'w', encoding='utf-8') as f:
            f.write(codigo)
        print("✓ Motor de banco de dados substituído com sucesso!")

# Validação imediata de compilação
try:
    py_compile.compile(caminho_app, doraise=True)
    print("✓ app.py compilado sem nenhum erro!")
except Exception as e:
    print(f"Erro em app.py: {e}")
    exit(1)

print("=" * 80)
print(">>> PRONTO! EXECUTE OS COMANDOS GIT PARA SUBIR A CORREÇÃO! <<<")
print("=" * 80)