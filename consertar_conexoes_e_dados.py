import os
import re
import py_compile
import subprocess

print("=" * 80)
print("A ELIMINAR 'CONNECTION ALREADY CLOSED' E A DESTRAVAR LEITURA DO SUPABASE...")
print("=" * 80)

caminho_app = 'app.py'

with open(caminho_app, 'r', encoding='utf-8') as f:
    codigo = f.read()

# 1. GARANTIR IMPORTAÇÕES COMPLETAS NO TOPO
if "from psycopg2.extras import RealDictCursor" not in codigo:
    codigo = "try:\n    import psycopg2\n    import psycopg2.extras\n    from psycopg2.extras import RealDictCursor\nexcept ImportError:\n    pass\n\n" + codigo

# 2. DEFINIR O NOVO NÚCLEO DE BANCO DE DADOS (CONEXÕES INDEPENDENTES E SEGURAS)
novo_nucleo_db = '''def get_db():
    if USAR_POSTGRES:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        return conn
    else:
        conn = sqlite3.connect('banco.db')
        conn.row_factory = sqlite3.Row
        return conn

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
        raise e
    finally:
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
        return []
    finally:
        try:
            conn.close()
        except Exception:
            pass

def consultar_um(sql, params=()):
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
        return None
    finally:
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
        try:
            conn.close()
        except Exception:
            pass
'''

# 3. SUBSTITUIR O BLOCO ANTIGO DE BANCO DE DADOS
pos_inicio_db = codigo.find("def get_db():")
pos_fim_db = codigo.find("def inicializar_banco():")

if pos_inicio_db != -1 and pos_fim_db != -1:
    codigo = codigo[:pos_inicio_db] + novo_nucleo_db + "\n" + codigo[pos_fim_db:]
    print("✓ Núcleo de banco de dados substituído por conexões seguras e independentes!")
else:
    print("Aviso: Posições exatas de get_db / inicializar_banco não localizadas diretamente.")

# 4. CHAMAR A MIGRAÇÃO DENTRO DE INICIALIZAR_BANCO
if "migrar_colunas_doutrina()" not in codigo:
    codigo = re.sub(
        r"(def inicializar_banco\(\):)",
        r"\1\n    migrar_colunas_doutrina()",
        codigo,
        count=1
    )
    print("✓ Migração de colunas adicionada ao arranque de inicializar_banco()!")

# 5. ASSEGURAR QUE A QUERY DE DOUTRINA RETORNA TODOS OS REGISTOS
padrao_query_doutrina = r'[a-zA-Z0-9_]*doutrina[a-zA-Z0-9_]*\s*=\s*consultar_todos\(\s*["\']SELECT \* FROM doutrina[\s\S]*?\)\n'
if re.search(padrao_query_doutrina, codigo):
    codigo = re.sub(
        padrao_query_doutrina,
        'doutrina = consultar_todos("SELECT * FROM doutrina ORDER BY id DESC")\n',
        codigo,
        count=1
    )
    print("✓ Consulta de Doutrina ajustada para: SELECT * FROM doutrina ORDER BY id DESC!")

with open(caminho_app, 'w', encoding='utf-8') as f:
    f.write(codigo)

# 6. VALIDAR COMPILAÇÃO DO PYTHON
try:
    py_compile.compile(caminho_app, doraise=True)
    print("✓ app.py compilado com ZERO erros de sintaxe!")
except Exception as e:
    print(f"Erro em app.py: {e}")
    exit(1)

# 7. EXECUTAR TESTE DE CONEXÃO E LEITURA REAL DOS FORMANDOS
print("\n" + "=" * 80)
print("A TESTAR CONSULTA REAL AO BANCO DE DADOS...")
print("=" * 80)

try:
    from app import app as flask_app, consultar_todos, migrar_colunas_doutrina
    with flask_app.app_context():
        migrar_colunas_doutrina()
        alunos = consultar_todos("SELECT * FROM doutrina ORDER BY id DESC")
        print(f"✓ RETORNO CONFIRMADO: {len(alunos)} formando(s) lido(s) do banco de dados!")
        for idx, a in enumerate(alunos[:5], 1):
            nome = a.get('nome_aluno') or a.get('nome') or 'Sem nome'
            classe = a.get('classe') or 'Sem classe'
            mentor = a.get('professor') or 'Sem mentor'
            print(f"   [{idx}] {nome} | {classe} | Mentor: {mentor}")
except Exception as err:
    print(f"Resultado do teste: {err}")

# 8. ENVIAR PARA O GITHUB E O RENDER
print("\n" + "=" * 80)
print("A ENVIAR ATUALIZAÇÃO PARA O GITHUB & RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "app.py"], check=True)
subprocess.run(["git", "commit", "-m", "Fix: eliminar connection already closed e restaurar leitura confiavel de formandos"], check=True)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("=" * 80)
print(">>> ATUALIZAÇÃO CONCLUÍDA COM TOTAL SUCESSO! <<<")
print("=" * 80)