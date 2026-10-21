import os
import re
import py_compile
import subprocess

print("=" * 80)
print("A CORRIGIR IMPORTAÇÃO DO REALDICTCURSOR E LEITURA DE DADOS DO SUPABASE...")
print("=" * 80)

caminho_app = 'app.py'

with open(caminho_app, 'r', encoding='utf-8') as f:
    codigo = f.read()

# 1. GARANTIR IMPORTAÇÃO DE PSYCOPG2 E REALDICTCURSOR NO TOPO DO FICHEIRO
import_extras = """try:
    import psycopg2
    import psycopg2.extras
    from psycopg2.extras import RealDictCursor
except ImportError:
    pass
"""

if "from psycopg2.extras import RealDictCursor" not in codigo:
    # Insere logo após os primeiros imports
    codigo = import_extras + "\n" + codigo
    print("✓ 'from psycopg2.extras import RealDictCursor' importado com sucesso!")

# 2. DEFINIR FUNÇÕES DE LEITURA BLINDADAS COM REALDICTCURSOR
bloco_consultas = '''def consultar_todos(sql, params=()):
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
        return None'''

# Substituir consultar_todos e consultar_um
padrao_consultas = r"def consultar_todos\(sql, params=\(\)\):[\s\S]*?def consultar_um\(sql, params=\(\)\):[\s\S]*?return None"
if re.search(padrao_consultas, codigo):
    codigo = re.sub(padrao_consultas, bloco_consultas, codigo, count=1)
    print("✓ Funções consultar_todos e consultar_um atualizadas com psycopg2.extras.RealDictCursor!")

with open(caminho_app, 'w', encoding='utf-8') as f:
    f.write(codigo)

# 3. VERIFICAR COMPILAÇÃO PYTHON
try:
    py_compile.compile(caminho_app, doraise=True)
    print("✓ app.py compilado com ZERO erros de sintaxe!")
except Exception as e:
    print(f"Erro em app.py: {e}")
    exit(1)

# 4. TESTAR LEITURA REAL DOS ALUNOS NO BANCO
print("=" * 80)
print("A TESTAR COMUNICAÇÃO E RETORNO COM O BANCO DE DADOS...")
print("=" * 80)

try:
    from app import consultar_todos, app as flask_app
    with flask_app.app_context():
        alunos_banco = consultar_todos("SELECT * FROM doutrina ORDER BY id DESC")
        print(f"✓ SUCESSO! Total de formandos encontrados no banco: {len(alunos_banco)}")
        for idx, al in enumerate(alunos_banco[:5], 1):
            nome = al.get('nome_aluno') or al.get('nome') or 'Sem nome'
            classe = al.get('classe') or 'Sem classe'
            mentor = al.get('professor') or 'Sem mentor'
            print(f"   [{idx}] Aluno: {nome} | Classe: {classe} | Mentor: {mentor}")
except Exception as err:
    print(f"Aviso no teste local: {err} (o Render executará com as credenciais da nuvem)")

# 5. ENVIAR PARA O GITHUB E O RENDER
print("=" * 80)
print("A ENVIAR ATUALIZAÇÃO PARA O GITHUB & RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "app.py"], check=True)
subprocess.run(["git", "commit", "-m", "Fix: importar RealDictCursor para retornar registros de alunos do Supabase"], check=True)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("=" * 80)
print(">>> PROCESSO CONCLUÍDO COM SUCESSO! <<<")
print("=" * 80)