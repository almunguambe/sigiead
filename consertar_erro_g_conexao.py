import os
import re
import py_compile
import subprocess

print("=" * 80)
print("A CORRIGIR IMPORTAÇÃO DE 'g' E CONEXÃO SEGURA NO ARRANQUE DO APP.PY...")
print("=" * 80)

caminho_app = 'app.py'

with open(caminho_app, 'r', encoding='utf-8') as f:
    codigo = f.read()

# 1. GARANTIR IMPORTAÇÃO DE 'g' E 'has_request_context' DE FLASK
if "from flask import" in codigo:
    # Capturar a linha de import do flask
    m_import = re.search(r"from flask import ([^\n]+)", codigo)
    if m_import:
        itens_importados = [i.strip() for i in m_import.group(1).split(",")]
        for item in ["g", "has_request_context"]:
            if item not in itens_importados:
                itens_importados.append(item)
        nova_linha_import = "from flask import " + ", ".join(itens_importados)
        codigo = codigo[:m_import.start()] + nova_linha_import + codigo[m_import.end():]
        print("✓ Importações 'g' e 'has_request_context' garantidas no topo de app.py!")
else:
    codigo = "from flask import g, has_request_context\n" + codigo

# 2. DEFINIR get_db() RESISTENTE TANTO AO ARRANQUE QUANTO ÀS REQUISIÇÕES
bloco_db_seguro = '''def get_db():
    if has_request_context():
        if 'db' not in g:
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
        # Conexão direta durante o arranque (inicializar_banco) fora do contexto web
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
                pass'''

# Substituir get_db e teardown
padrao_get_db = r"def get_db\(\):[\s\S]*?(?=\ndef executar_comando|\ndef consultar_todos|\Z)"
if re.search(padrao_get_db, codigo):
    codigo = re.sub(padrao_get_db, bloco_db_seguro + "\n\n", codigo, count=1)
    print("✓ Função get_db() blindada contra arranques fora de contexto web!")

with open(caminho_app, 'w', encoding='utf-8') as f:
    f.write(codigo)

# 3. TESTE ESTRITO DE COMPILAÇÃO
try:
    py_compile.compile(caminho_app, doraise=True)
    print("✓ app.py compilado com ZERO erros de sintaxe!")
except Exception as e:
    print(f"Erro detectado em app.py: {e}")
    exit(1)

# 4. ENVIAR PARA O GITHUB E O RENDER
print("=" * 80)
print("A ENVIAR ATUALIZAÇÃO PARA O GITHUB & RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "app.py"], check=True)
subprocess.run(["git", "commit", "-m", "Fix NameError g: suportar inicializacao fora de contexto e reuso em requisicoes"], check=True)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("=" * 80)
print(">>> ATUALIZAÇÃO CONCLUÍDA COM TOTAL SUCESSO! <<<")
print("=" * 80)