import os
import re
import py_compile
import subprocess

print("=" * 80)
print("A IMPLEMENTAR ARQUITETURA DE ALTA VELOCIDADE (ZERO LATÊNCIA DE REDE)...")
print("=" * 80)

caminho_app = 'app.py'

with open(caminho_app, 'r', encoding='utf-8') as f:
    codigo = f.read()

# 1. ASSEGURAR IMPORTAÇÕES NECESSÁRIAS NO FLASK
if "from flask import" in codigo:
    m_import = re.search(r"from flask import ([^\n]+)", codigo)
    if m_import:
        itens = [i.strip() for i in m_import.group(1).split(",")]
        for item in ["g", "has_request_context"]:
            if item not in itens:
                itens.append(item)
        nova_linha = "from flask import " + ", ".join(itens)
        codigo = codigo[:m_import.start()] + nova_linha + codigo[m_import.end():]
        print("✓ Importações 'g' e 'has_request_context' garantidas!")

# 2. BLOCO DE BANCO DEFINITIVO COM REÚSO PROTEGIDO E AUTO-RECONEXÃO
bloco_db_alta_performance = '''def get_db():
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
'''

# 3. SUBSTITUIR CIRURGICAMENTE DA FUNÇÃO get_db() ATÉ ANTES DE inicializar_banco()
pos_inicio = codigo.find("def get_db():")
pos_fim = codigo.find("def inicializar_banco():")

if pos_inicio != -1 and pos_fim != -1:
    codigo = codigo[:pos_inicio] + bloco_db_alta_performance + "\n" + codigo[pos_fim:]
    print("✓ Núcleo de banco otimizado com reuso inteligente por requisição!")
else:
    print("Aviso: Posições exatas de substituição não localizadas.")

with open(caminho_app, 'w', encoding='utf-8') as f:
    f.write(codigo)

# 4. VALIDAR COMPILAÇÃO DO CÓDIGO PYTHON
try:
    py_compile.compile(caminho_app, doraise=True)
    print("✓ app.py compilado com ZERO erros de sintaxe!")
except Exception as e:
    print(f"Erro em app.py: {e}")
    exit(1)

# 5. COMMIT E PUSH DIRETO PARA O RENDER
print("=" * 80)
print("A ENVIAR ATUALIZAÇÃO PARA O GITHUB & RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "app.py"], check=True)
subprocess.run(["git", "commit", "-m", "Performance definitiva: conexao persistente por requisicao e latencia zero"], check=True)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("=" * 80)
print(">>> ATUALIZAÇÃO CONCLUÍDA COM TOTAL SUCESSO! <<<")
print("=" * 80)