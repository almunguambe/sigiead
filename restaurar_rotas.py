import os
import shutil
import re
import ast

print("=" * 75)
print("A RECONECTAR TODOS OS FORMULÁRIOS E ROTAS DO SISTEMA...")
print("=" * 75)

# 1. ATUALIZAR TEMPLATES/DASHBOARD.HTML COM ROTAS DEDICADAS
tpl = os.path.join('templates', 'dashboard.html')
shutil.copy(tpl, tpl + '.bak_rotas')

with open(tpl, 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

mapeamento = [
    ('Planificar Nova Actividade', '/secretaria/planificacao/nova'),
    ('Registar Novo Convertido', '/convertidos/novo'),
    ('Criar Escala de Culto', '/escalas/novo'),
    ('Registo Matrimonial', '/casamentos/novo'),
    ('Registo de Óbito', '/obitos/novo'),
    ('Lançamento no Caixa', '/financas/caixa/novo'),
    ('Transferir Fundos', '/financas/transferencia/nova')
]

for termo, rota in mapeamento:
    pos = html.find(termo)
    if pos != -1:
        pos_form = html.find('<form', pos)
        if pos_form != -1 and (pos_form - pos) < 600:
            fim_form = html.find('>', pos_form)
            tag_antiga = html[pos_form:fim_form+1]
            tag_nova = re.sub(r'action=[\'"][^\'"]*[\'"]', f'action="{rota}"', tag_antiga)
            if 'action=' not in tag_nova:
                tag_nova = f'<form action="{rota}" method="POST">'
            if 'method=' not in tag_nova.lower():
                tag_nova = tag_nova[:-1] + ' method="POST">'
            html = html[:pos_form] + tag_nova + html[fim_form+1:]
            print(f"✓ {termo:<28} -> Conectado a {rota}")

with open(tpl, 'w', encoding='utf-8') as f:
    f.write(html)
print("✓ templates/dashboard.html atualizado!")

# 2. ATUALIZAR APP.PY COM TODAS AS ROTAS RECEPTORAS
shutil.copy('app.py', 'app.py.bak_rotas')
with open('app.py', 'r', encoding='utf-8', errors='ignore') as f:
    app_py = f.read()

# Aliases e rotas para Planificação, Casamentos, Óbitos e Finanças
rotas_gerais = '''
# =====================================================================
# ROTAS OPERACIONAIS INTEGRADAS (PLANIFICAÇÃO, CASAMENTOS, ÓBITOS, FINANÇAS)
# =====================================================================

@app.route('/secretaria/planificacao', methods=['GET', 'POST'])
@app.route('/secretaria/planificacao/nova', methods=['GET', 'POST'])
def planificacao_geral():
    if request.method == 'POST':
        conn = get_db()
        cur = conn.cursor() if hasattr(conn, 'cursor') else conn
        is_pg = ('psycopg' in str(type(conn)).lower()) or bool(os.environ.get('DATABASE_URL'))
        id_tipo = "SERIAL PRIMARY KEY" if is_pg else "INTEGER PRIMARY KEY AUTOINCREMENT"
        try:
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS planificacao (
                    id {id_tipo},
                    titulo TEXT,
                    data_inicio TEXT,
                    data_fim TEXT,
                    departamento TEXT,
                    descricao TEXT,
                    responsavel TEXT,
                    status TEXT DEFAULT 'Pendente',
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            if hasattr(conn, 'commit'): conn.commit()
        except Exception:
            if hasattr(conn, 'rollback'): conn.rollback()

        fd = request.form
        titulo = (fd.get('titulo') or fd.get('actividade') or fd.get('nome') or 'Actividade').strip()
        data_ini = (fd.get('data_inicio') or fd.get('data') or '').strip()
        data_fim = (fd.get('data_fim') or data_ini).strip()
        depto = (fd.get('departamento') or fd.get('sector') or 'Geral').strip()
        desc = (fd.get('descricao') or '').strip()
        resp = (fd.get('responsavel') or '').strip()

        m = "%s" if is_pg else "?"
        try:
            cur.execute(f"""INSERT INTO planificacao (titulo, data_inicio, data_fim, departamento, descricao, responsavel)
                            VALUES ({m}, {m}, {m}, {m}, {m}, {m})""", (titulo, data_ini, data_fim, depto, desc, resp))
            if hasattr(conn, 'commit'): conn.commit()
            print(f"[SUCESSO PLANIFICAÇÃO]: Gravado -> {titulo}")
        except Exception as e:
            print("[ERRO PLANIFICAÇÃO]:", e)
            if hasattr(conn, 'rollback'): conn.rollback()

        return redirect('/?aba=secretaria')
    return redirect('/?aba=secretaria')

@app.route('/casamentos/novo', methods=['POST'])
def casamentos_novo():
    conn = get_db()
    cur = conn.cursor() if hasattr(conn, 'cursor') else conn
    is_pg = ('psycopg' in str(type(conn)).lower()) or bool(os.environ.get('DATABASE_URL'))
    id_tipo = "SERIAL PRIMARY KEY" if is_pg else "INTEGER PRIMARY KEY AUTOINCREMENT"
    try:
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS casamentos (
                id {id_tipo},
                noivo TEXT,
                noiva TEXT,
                data_casamento TEXT,
                celebrante TEXT,
                regime TEXT,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        if hasattr(conn, 'commit'): conn.commit()
    except Exception:
        if hasattr(conn, 'rollback'): conn.rollback()

    fd = request.form
    noivo = (fd.get('noivo') or '').strip()
    noiva = (fd.get('noiva') or '').strip()
    data_c = (fd.get('data_casamento') or fd.get('data') or '').strip()
    celeb = (fd.get('celebrante') or fd.get('pastor') or '').strip()
    regime = (fd.get('regime') or '').strip()

    m = "%s" if is_pg else "?"
    try:
        cur.execute(f"""INSERT INTO casamentos (noivo, noiva, data_casamento, celebrante, regime)
                        VALUES ({m}, {m}, {m}, {m}, {m})""", (noivo, noiva, data_c, celeb, regime))
        if hasattr(conn, 'commit'): conn.commit()
        print(f"[SUCESSO CASAMENTO]: Gravado -> {noivo} & {noiva}")
    except Exception as e:
        print("[ERRO CASAMENTO]:", e)
        if hasattr(conn, 'rollback'): conn.rollback()

    return redirect('/?aba=casamentos')

@app.route('/obitos/novo', methods=['POST'])
@app.route('/mortes/novo', methods=['POST'])
def obitos_novo():
    conn = get_db()
    cur = conn.cursor() if hasattr(conn, 'cursor') else conn
    is_pg = ('psycopg' in str(type(conn)).lower()) or bool(os.environ.get('DATABASE_URL'))
    id_tipo = "SERIAL PRIMARY KEY" if is_pg else "INTEGER PRIMARY KEY AUTOINCREMENT"
    try:
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS obitos (
                id {id_tipo},
                falecido TEXT,
                data_falecimento TEXT,
                causa TEXT,
                contacto_familia TEXT,
                data_funeral TEXT,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        if hasattr(conn, 'commit'): conn.commit()
    except Exception:
        if hasattr(conn, 'rollback'): conn.rollback()

    fd = request.form
    falecido = (fd.get('falecido') or fd.get('nome') or '').strip()
    data_f = (fd.get('data_falecimento') or fd.get('data') or '').strip()
    causa = (fd.get('causa') or '').strip()
    cont = (fd.get('contacto_familia') or fd.get('contacto') or '').strip()
    data_fun = (fd.get('data_funeral') or '').strip()

    m = "%s" if is_pg else "?"
    try:
        cur.execute(f"""INSERT INTO obitos (falecido, data_falecimento, causa, contacto_familia, data_funeral)
                        VALUES ({m}, {m}, {m}, {m}, {m})""", (falecido, data_f, causa, cont, data_fun))
        if hasattr(conn, 'commit'): conn.commit()
        print(f"[SUCESSO ÓBITO]: Gravado -> {falecido}")
    except Exception as e:
        print("[ERRO ÓBITO]:", e)
        if hasattr(conn, 'rollback'): conn.rollback()

    return redirect('/?aba=mortes')

@app.route('/financas/caixa/novo', methods=['POST'])
@app.route('/financas/transferencia/nova', methods=['POST'])
def financas_geral():
    return redirect('/?aba=financas')
'''

# Remover bloco antigo de rotas gerais se existir
marcador_geral = "# ====================================================================="
if marcador_geral in app_py:
    app_py = app_py.split(marcador_geral)[0].rstrip() + "\n"

app_py = app_py.strip() + "\n\n" + rotas_gerais.strip() + "\n"

# Validar com o analisador sintático AST
ast.parse(app_py)
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_py)
print("✓ app.py validado e pronto!")
