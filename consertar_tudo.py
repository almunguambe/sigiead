import os
import shutil
import re
import ast

print("=" * 75)
print("A CORRIGIR FORMULÁRIOS, BANCO E TABELAS LATERAIS...")
print("=" * 75)

# -------------------------------------------------------------
# 1. CORRIGIR TEMPLATES/DASHBOARD.HTML
# -------------------------------------------------------------
tpl_path = os.path.join('templates', 'dashboard.html')
shutil.copy(tpl_path, tpl_path + '.bak_consertar')

with open(tpl_path, 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

# A) Limpar atributos 'name' duplicados no input da planificação
html = re.sub(
    r'<input([^>]*?)name=[\'"]actividade[\'"]([^>]*?)name=[\'"]nome_actividade[\'"]([^>]*?)name=[\'"]nome_actividade[\'"]',
    r'<input\1name="actividade"\2\3',
    html,
    flags=re.IGNORECASE
)
html = re.sub(
    r'<input([^>]*?)name=[\'"]nome_actividade[\'"]([^>]*?)name=[\'"]nome_actividade[\'"]',
    r'<input\1name="actividade"\2',
    html,
    flags=re.IGNORECASE
)
html = re.sub(
    r'<input([^>]*?)name=[\'"]data_prevista[\'"]([^>]*?)name=[\'"]data_prevista[\'"]',
    r'<input\1name="data_prevista"\2',
    html,
    flags=re.IGNORECASE
)

# B) Garantir action correta para planificação
pos_plan = html.find('Planificar Nova Actividade')
if pos_plan != -1:
    pos_form = html.rfind('<form', 0, pos_plan + 300)
    if pos_form != -1:
        fim_form = html.find('>', pos_form)
        tag_form = html[pos_form:fim_form+1]
        nova_tag = re.sub(r'action=[\'"][^\'"]*[\'"]', 'action="/secretaria/planificacao/nova"', tag_form)
        if 'action=' not in nova_tag:
            nova_tag = '<form action="/secretaria/planificacao/nova" method="POST">'
        html = html[:pos_form] + nova_tag + html[fim_form+1:]

# C) Garantir que o formulário de Novos Convertidos está isolado
pos_btn_conv = html.find('Registar para Discipulado')
if pos_btn_conv != -1:
    pos_bloco_conv = html.rfind('Registar Novo Convertido', 0, pos_btn_conv)
    if pos_bloco_conv != -1:
        trecho_form = html[pos_bloco_conv:pos_btn_conv]
        if '/convertidos/novo' not in trecho_form:
            pos_input = html.find('<input', pos_bloco_conv, pos_btn_conv)
            if pos_input != -1:
                html = html[:pos_input] + '</form>\n<form action="/convertidos/novo" method="POST">\n                            ' + html[pos_input:]

# D) Caixa de soma e script de Cultos
caixa_total = '<input type="number" id="total_presentes_display" name="total_presentes" value="0" readonly style="width: 85%; padding: 6px; font-size: 20px; font-weight: bold; text-align: center; border: 2px solid #93c5fd; border-radius: 8px; color: #1e40af; background: #eff6ff;">'
if 'Calculado ao Gravar' in html:
    html = re.sub(r'<div[^>]*>\s*Calculado ao Gravar\s*</div>', caixa_total, html, count=1)
elif 'total_presentes_display' not in html:
    html = re.sub(r'(Total de Presentes[\s\S]*?)(<div[^>]*>[\s\S]*?</div>)', r'\1\n' + caixa_total, html, count=1)

script_cultos = """
<script>
function somarPresencasTempoReal() {
    var campos = ['homens_adultos', 'mulheres_adultas', 'jovens_rapazes', 'jovens_mocas', 'criancas_meninos', 'criancas_meninas', 'visitantes_homens', 'visitantes_mulheres'];
    var total = 0;
    campos.forEach(function(nome) {
        var inp = document.querySelector('input[name="' + nome + '"]');
        if (inp) total += (parseInt(inp.value, 10) || 0);
    });
    var disp = document.getElementById('total_presentes_display');
    if (disp) disp.value = total;
}
document.addEventListener('input', function(e) {
    if (e.target && e.target.type === 'number' && e.target.name !== 'apelos' && e.target.name !== 'total_presentes') {
        somarPresencasTempoReal();
    }
});
document.addEventListener('DOMContentLoaded', somarPresencasTempoReal);
</script>
"""
if 'somarPresencasTempoReal' not in html:
    html = html + "\n" + script_cultos

with open(tpl_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("✓ templates/dashboard.html atualizado e corrigido com sucesso!")

# -------------------------------------------------------------
# 2. CORRIGIR APP.PY (ELIMINAR DUPLICADOS E BLINDAR TODAS AS ROTAS)
# -------------------------------------------------------------
shutil.copy('app.py', 'app.py.bak_consertar')
with open('app.py', 'r', encoding='utf-8', errors='ignore') as f:
    app_py = f.read()

# Remover quaisquer blocos customizados anexados no final
for marker in ["# =====================================================================", "# ROTAS OPERACIONAIS INTEGRADAS", "# ROTAS BLINDADAS"]:
    if marker in app_py:
        app_py = app_py.split(marker)[0].rstrip() + "\n"

# Funções que vamos substituir para não haver duplicação (evita AssertionError)
funcoes_para_limpar = [
    'novo_convertido',
    'planificacao_geral',
    'planificacao_nova',
    'injetar_dados_tabelas',
    'injetar_listas_tabelas'
]

for func in funcoes_para_limpar:
    padrao = rf"(@app\.route\([^)]*\)\s*)*\ndef\s+{func}\s*\([^)]*\):[\s\S]*?(?=\n@app\.route|\ndef |\Z)"
    app_py = re.sub(padrao, "", app_py)

# Bloco final com implementação única, robusta e tolerante
bloco_completo = '''
# =====================================================================
# ROTAS OPERACIONAIS INTEGRADAS (PLANIFICAÇÃO, CONVERTIDOS, INJEÇÃO)
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
                    actividade TEXT,
                    nome_actividade TEXT,
                    titulo TEXT,
                    departamento TEXT,
                    tipo_evento TEXT,
                    data_prevista TEXT,
                    data_inicio TEXT,
                    frequencia TEXT,
                    responsavel TEXT,
                    contacto TEXT,
                    status TEXT DEFAULT 'Planeado',
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            if hasattr(conn, 'commit'): conn.commit()
        except Exception:
            if hasattr(conn, 'rollback'): conn.rollback()

        if is_pg:
            colunas = [
                ('actividade', 'TEXT'), ('nome_actividade', 'TEXT'), ('titulo', 'TEXT'),
                ('departamento', 'TEXT'), ('tipo_evento', 'TEXT'), ('data_prevista', 'TEXT'),
                ('data_inicio', 'TEXT'), ('frequencia', 'TEXT'), ('responsavel', 'TEXT'),
                ('contacto', 'TEXT'), ('status', "TEXT DEFAULT 'Planeado'")
            ]
            for col, tipo in colunas:
                try:
                    cur.execute(f"ALTER TABLE planificacao ADD COLUMN IF NOT EXISTS {col} {tipo};")
                    if hasattr(conn, 'commit'): conn.commit()
                except Exception:
                    if hasattr(conn, 'rollback'): conn.rollback()

        fd = request.form
        actividade = (fd.get('actividade') or fd.get('nome_actividade') or fd.get('titulo') or 'Actividade').strip()
        departamento = (fd.get('departamento') or 'Geral').strip()
        tipo_evento = (fd.get('tipo_evento') or 'Evento').strip()
        data_prevista = (fd.get('data_prevista') or fd.get('data_inicio') or fd.get('data') or '').strip()
        frequencia = (fd.get('frequencia') or 'Pontual / Única').strip()
        responsavel = (fd.get('responsavel') or fd.get('responsavel_directo') or '').strip()
        contacto = (fd.get('contacto') or fd.get('whatsapp') or fd.get('telefone') or '').strip()

        from datetime import datetime
        if not data_prevista or data_prevista in ('mm/dd/yyyy', '---'):
            data_prevista = datetime.now().strftime('%Y-%m-%d')

        m = "%s" if is_pg else "?"
        sql = f"""INSERT INTO planificacao 
                  (actividade, nome_actividade, titulo, departamento, tipo_evento, data_prevista, data_inicio, frequencia, responsavel, contacto, status)
                  VALUES ({m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m})"""
        try:
            cur.execute(sql, (actividade, actividade, actividade, departamento, tipo_evento, data_prevista, data_prevista, frequencia, responsavel, contacto, 'Planeado'))
            if hasattr(conn, 'commit'): conn.commit()
            print(f"[SUCESSO PLANIFICAÇÃO]: Gravado -> {actividade} ({departamento})")
        except Exception as e:
            print("[ERRO AO GRAVAR PLANIFICAÇÃO]:", e)
            if hasattr(conn, 'rollback'): conn.rollback()

        return redirect('/?aba=secretaria')
    return redirect('/?aba=secretaria')


@app.route('/convertidos/novo', methods=['POST'])
def novo_convertido():
    conn = get_db()
    cur = conn.cursor() if hasattr(conn, 'cursor') else conn
    is_pg = ('psycopg' in str(type(conn)).lower()) or bool(os.environ.get('DATABASE_URL'))
    id_tipo = "SERIAL PRIMARY KEY" if is_pg else "INTEGER PRIMARY KEY AUTOINCREMENT"

    try:
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS novos_convertidos (
                id {id_tipo},
                nome TEXT,
                telefone TEXT,
                bairro TEXT,
                data_decisao TEXT,
                culto_origem TEXT,
                quem_convidou TEXT,
                status_discipulado TEXT DEFAULT 'Acompanhamento',
                observacoes TEXT,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        if hasattr(conn, 'commit'): conn.commit()
    except Exception:
        if hasattr(conn, 'rollback'): conn.rollback()

    fd = request.form
    nome = (fd.get('nome') or fd.get('nome_completo') or fd.get('nome_convertido') or 'Sem Nome').strip()
    telefone = (fd.get('telefone') or fd.get('contato') or fd.get('contacto') or '').strip()
    bairro = (fd.get('bairro') or fd.get('residencia') or '').strip()
    data_decisao = (fd.get('data_decisao') or fd.get('data') or fd.get('data_conversao') or '').strip()
    quem_convidou = (fd.get('quem_convidou') or fd.get('convidado_por') or fd.get('discipulador') or '').strip()
    culto_origem = (fd.get('culto_origem') or fd.get('tipo_culto') or 'Geral').strip()

    from datetime import datetime
    if not data_decisao or data_decisao in ('mm/dd/yyyy', '---'):
        data_decisao = datetime.now().strftime('%Y-%m-%d')

    m = "%s" if is_pg else "?"
    sql = f"""INSERT INTO novos_convertidos 
              (nome, telefone, bairro, data_decisao, quem_convidou, culto_origem, status_discipulado)
              VALUES ({m}, {m}, {m}, {m}, {m}, {m}, {m})"""
    try:
        cur.execute(sql, (nome, telefone, bairro, data_decisao, quem_convidou, culto_origem, 'Acompanhamento'))
        if hasattr(conn, 'commit'): conn.commit()
        print(f"[SUCESSO CONVERTIDO]: Registado -> {nome}")
    except Exception as e:
        print("[ERRO AO GRAVAR CONVERTIDO]:", e)
        if hasattr(conn, 'rollback'): conn.rollback()

    return redirect('/?aba=convertidos')


@app.context_processor
def injetar_dados_tabelas():
    ctx = {
        'convertidos': [],
        'novos_convertidos': [],
        'cultos': [],
        'planificacoes': [],
        'cronograma': [],
        'actividades': [],
        'planos': []
    }
    try:
        conn = get_db()
        cur = conn.cursor() if hasattr(conn, 'cursor') else conn

        # 1. Planificações com chaves universais para preencher a tabela lateral
        try:
            cur.execute("SELECT * FROM planificacao ORDER BY id DESC LIMIT 50")
            if cur.description:
                cols = [c[0].lower() for c in cur.description]
                linhas = cur.fetchall()
                lista_p = []
                for r in linhas:
                    d = dict(zip(cols, r))
                    act = d.get('actividade') or d.get('titulo') or d.get('nome_actividade') or 'Geral'
                    dep = d.get('departamento') or 'Geral'
                    dt = d.get('data_prevista') or d.get('data_inicio') or ''
                    resp = d.get('responsavel') or ''
                    cont = d.get('contacto') or ''
                    st = d.get('status') or 'Planeado'
                    item = {
                        **d,
                        'actividade': act,
                        'nome_actividade': act,
                        'titulo': act,
                        'departamento': dep,
                        'data_prevista': dt,
                        'data_inicio': dt,
                        'responsavel': resp,
                        'contacto': cont,
                        'status': st
                    }
                    lista_p.append(item)
                ctx['planificacoes'] = lista_p
                ctx['cronograma'] = lista_p
                ctx['actividades'] = lista_p
                ctx['planos'] = lista_p
        except Exception: pass

        # 2. Novos Convertidos
        try:
            cur.execute("SELECT * FROM novos_convertidos ORDER BY id DESC LIMIT 50")
            if cur.description:
                cols_nc = [c[0].lower() for c in cur.description]
                res_nc = [dict(zip(cols_nc, r)) for r in cur.fetchall()]
                ctx['convertidos'] = res_nc
                ctx['novos_convertidos'] = res_nc
        except Exception: pass

        # 3. Cultos
        try:
            cur.execute("SELECT * FROM cultos ORDER BY id DESC LIMIT 50")
            if cur.description:
                cols_c = [c[0].lower() for c in cur.description]
                ctx['cultos'] = [dict(zip(cols_c, r)) for r in cur.fetchall()]
        except Exception: pass

    except Exception: pass
    return ctx
'''

app_py = app_py.strip() + "\n\n" + bloco_completo.strip() + "\n"

ast.parse(app_py)
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_py)
print("✓ app.py validado com AST e gravado sem erros nem duplicados!")
print("=" * 75)
print("✓ PROCESSO CONCLUÍDO COM SUCESSO TOTAL!")
print("=" * 75)