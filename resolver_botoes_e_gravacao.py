import os
import shutil
import re
import ast
import jinja2

print("=" * 70)
print("A APLICAR CORREÇÃO DEFINITIVA DOS BOTÕES, CÁLCULO E GRAVAÇÃO...")
print("=" * 70)

# -------------------------------------------------------------
# 1. CORRIGIR TEMPLATES/DASHBOARD.HTML
# -------------------------------------------------------------
tpl_dash = os.path.join('templates', 'dashboard.html')
shutil.copy(tpl_dash, tpl_dash + '.bak_botoes_ok')

with open(tpl_dash, 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

# A) Atribuir tag <form action="/convertidos/novo" method="POST"> a Novos Convertidos
idx_btn_conv = html.find('Registar para Discipulado')
if idx_btn_conv != -1:
    idx_bloco_conv = html.rfind('Registar Novo Convertido', 0, idx_btn_conv)
    if idx_bloco_conv != -1:
        # Procura a tag anterior mais próxima antes do primeiro input
        idx_primeiro_input = html.find('<input', idx_bloco_conv)
        if idx_primeiro_input != -1 and idx_primeiro_input < idx_btn_conv:
            # Verifica se já não tem um form próprio
            trecho_meio = html[idx_bloco_conv:idx_primeiro_input]
            if '<form' not in trecho_meio:
                html = html[:idx_primeiro_input] + '<form action="/convertidos/novo" method="POST">\n                            ' + html[idx_primeiro_input:]
                print("✓ Tag <form action=\"/convertidos/novo\" method=\"POST\"> associada a Novos Convertidos!")

# B) Ativar a caixa e o cálculo em tempo real em Cultos
caixa_total = '<input type="number" id="total_presentes_display" name="total_presentes" value="0" readonly style="width: 85%; padding: 6px; font-size: 20px; font-weight: bold; text-align: center; border: 2px solid #93c5fd; border-radius: 8px; color: #1e40af; background: #eff6ff;">'

if 'Calculado ao Gravar' in html:
    html = re.sub(r'<div[^>]*>\s*Calculado ao Gravar\s*</div>', caixa_total, html, count=1)
    print("✓ Caixa de Total de Presentes em tempo real atualizada no formulário!")
elif 'total_presentes_display' not in html:
    html = re.sub(r'(Total de Presentes[\s\S]*?)(<div[^>]*>[\s\S]*?</div>)', r'\1\n' + caixa_total, html, count=1)
    print("✓ Caixa de Total de Presentes mapeada!")

# C) Injetar Script Universal de Cálculo em Tempo Real (Puro JS, sem travas)
script_calculo = """
<!-- ================= SCRIPT DE SOMA EM TEMPO REAL ================= -->
<script>
function somarPresencasTempoReal() {
    var campos = [
        'homens_adultos', 'mulheres_adultas',
        'jovens_rapazes', 'jovens_mocas',
        'criancas_meninos', 'criancas_meninas',
        'visitantes_homens', 'visitantes_mulheres'
    ];
    var total = 0;
    campos.forEach(function(nome) {
        var inp = document.querySelector('input[name="' + nome + '"]');
        if (inp) {
            total += (parseInt(inp.value, 10) || 0);
        }
    });
    var disp = document.getElementById('total_presentes_display');
    if (disp) {
        disp.value = total;
    }
}

document.addEventListener('input', function(e) {
    if (e.target && e.target.type === 'number' && e.target.name !== 'apelos' && e.target.name !== 'total_presentes') {
        somarPresencasTempoReal();
    }
});

document.addEventListener('DOMContentLoaded', function() {
    somarPresencasTempoReal();
});
</script>
"""

html = re.sub(r'<!-- ================= SCRIPT DE SOMA EM TEMPO REAL ================= -->[\s\S]*?</script>', '', html)
html = html + "\n" + script_calculo

# Validar compilação do Jinja2
try:
    jinja2.Environment().parse(html)
    with open(tpl_dash, 'w', encoding='utf-8') as f:
        f.write(html)
    print("✓ templates/dashboard.html validado e gravado sem erros de template!")
except Exception as e_jinja:
    print(f"⚠️ Aviso no Jinja2: {e_jinja}")
    with open(tpl_dash, 'w', encoding='utf-8') as f:
        f.write(html)

# -------------------------------------------------------------
# 2. CORRIGIR APP.PY (BLINDAGEM POSTGRESQL + GRAVAÇÃO E LEITURA)
# -------------------------------------------------------------
shutil.copy('app.py', 'app.py.bak_botoes_ok')
with open('app.py', 'r', encoding='utf-8', errors='ignore') as f:
    app_code = f.read()

# A) Substituição segura de AUTOINCREMENT sem depender de import re
app_code = app_code.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
app_code = app_code.replace("integer primary key autoincrement", "SERIAL PRIMARY KEY")

# Remover chamadas quebradas a re.sub na linha de execute
app_code = re.sub(r'sql\s*=\s*re\.sub\(.*?\)\n', '', app_code)

# B) Assegurar import re e import os no topo
if 'import re' not in app_code[:200]:
    app_code = "import re\nimport os\n" + app_code

# C) Garantir a rota /convertidos/novo com commit explícito
rota_convertidos = '''
@app.route('/convertidos/novo', methods=['POST'])
def novo_convertido():
    conn = get_db()
    cur = conn.cursor() if hasattr(conn, 'cursor') else conn
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS novos_convertidos (
                id SERIAL PRIMARY KEY,
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
        if hasattr(conn, 'rollback'):
            try: conn.rollback()
            except: pass

    nome = (request.form.get('nome') or '').strip()
    telefone = (request.form.get('telefone') or '').strip()
    bairro = (request.form.get('bairro') or '').strip()
    data_decisao = (request.form.get('data_decisao') or '').strip()
    quem_convidou = (request.form.get('quem_convidou') or '').strip()

    is_pg = ('psycopg' in str(type(conn)).lower()) or bool(os.environ.get('DATABASE_URL'))
    m = "%s" if is_pg else "?"

    sql = f"""INSERT INTO novos_convertidos (nome, telefone, bairro, data_decisao, quem_convidou)
              VALUES ({m}, {m}, {m}, {m}, {m})"""
    try:
        cur.execute(sql, (nome, telefone, bairro, data_decisao, quem_convidou))
        if hasattr(conn, 'commit'): conn.commit()
        print(f"[SUCESSO CONVERTIDO]: Gravado {nome}")
    except Exception as e:
        print("[ERRO CONVERTIDO]:", e)
        if hasattr(conn, 'rollback'):
            try: conn.rollback()
            except: pass

    return redirect('/?aba=convertidos')
'''

# D) Garantir a rota /cultos/novo com cálculo e commit
rota_cultos = '''
@app.route('/cultos/novo', methods=['POST'])
def cultos_novo():
    conn = get_db()
    cur = conn.cursor() if hasattr(conn, 'cursor') else conn
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS cultos (
                id SERIAL PRIMARY KEY,
                data_culto TEXT,
                tipo_culto TEXT,
                homens_adultos INTEGER DEFAULT 0,
                mulheres_adultas INTEGER DEFAULT 0,
                jovens_rapazes INTEGER DEFAULT 0,
                jovens_mocas INTEGER DEFAULT 0,
                criancas_meninos INTEGER DEFAULT 0,
                criancas_meninas INTEGER DEFAULT 0,
                visitantes_homens INTEGER DEFAULT 0,
                visitantes_mulheres INTEGER DEFAULT 0,
                apelos INTEGER DEFAULT 0,
                total_presentes INTEGER DEFAULT 0,
                pregador TEXT,
                tema_mensagem TEXT,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        if hasattr(conn, 'commit'): conn.commit()
    except Exception:
        if hasattr(conn, 'rollback'):
            try: conn.rollback()
            except: pass

    fd = request.form
    def n(k):
        v = fd.get(k)
        if v not in (None, ''):
            try: return int(v)
            except: pass
        return 0

    from datetime import datetime
    data_culto = (fd.get('data_culto') or '').strip()
    if not data_culto or data_culto in ('mm/dd/yyyy', '---'):
        data_culto = datetime.now().strftime('%Y-%m-%d')

    tipo_culto = (fd.get('tipo_culto') or 'Domingo Manhã').strip()
    ha = n('homens_adultos')
    ma = n('mulheres_adultas')
    jr = n('jovens_rapazes')
    jm = n('jovens_mocas')
    cm = n('criancas_meninos')
    cf = n('criancas_meninas')
    vh = n('visitantes_homens')
    vm = n('visitantes_mulheres')
    apelos = n('apelos')

    soma = ha + ma + jr + jm + cm + cf + vh + vm
    tot_form = n('total_presentes')
    total = tot_form if tot_form > 0 else soma

    pregador = (fd.get('pregador') or '---').strip()
    tema = (fd.get('tema_mensagem') or '').strip()

    is_pg = ('psycopg' in str(type(conn)).lower()) or bool(os.environ.get('DATABASE_URL'))
    m = "%s" if is_pg else "?"

    sql = f"""INSERT INTO cultos 
             (data_culto, tipo_culto, homens_adultos, mulheres_adultas, jovens_rapazes, jovens_mocas, 
              criancas_meninos, criancas_meninas, visitantes_homens, visitantes_mulheres, 
              apelos, total_presentes, pregador, tema_mensagem)
             VALUES ({m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m})"""
    try:
        cur.execute(sql, (data_culto, tipo_culto, ha, ma, jr, jm, cm, cf, vh, vm, apelos, total, pregador, tema))
        if hasattr(conn, 'commit'): conn.commit()
        print(f"[SUCESSO CULTO]: Gravado Total={total}")
    except Exception as e:
        print("[ERRO CULTO]:", e)
        if hasattr(conn, 'rollback'):
            try: conn.rollback()
            except: pass

    return redirect('/?aba=cultos')
'''

# Substituição cirúrgica das duas rotas no app.py
def substituir_funcao(codigo, nome_func, novo_bloco):
    padrao = rf"(@app\.route\([^)]*'{re.escape(nome_func)}'[^)]*\)\s*\ndef\s+[a-zA-Z0-9_]+\s*\([^)]*\):[\s\S]*?)(?=\n@app\.route|\ndef |\Z)"
    if re.search(padrao, codigo):
        return re.sub(padrao, novo_bloco.strip() + "\n\n", codigo, count=1)
    return codigo + "\n\n" + novo_bloco.strip() + "\n"

app_code = substituir_funcao(app_code, '/convertidos/novo', rota_convertidos)
app_code = substituir_funcao(app_code, '/cultos/novo', rota_cultos)

# E) Assegurar que cultos e convertidos são passados como dicionários no dashboard()
leitura_dados = """
    # Leitura robusta em formato dicionário para o Jinja2
    cultos = []
    convertidos = []
    try:
        cur.execute("SELECT * FROM cultos ORDER BY id DESC LIMIT 50")
        if cur.description:
            cols = [c[0] for c in cur.description]
            cultos = [dict(zip(cols, r)) for r in cur.fetchall()]
    except Exception: pass

    try:
        cur.execute("SELECT * FROM novos_convertidos ORDER BY id DESC LIMIT 50")
        if cur.description:
            cols_nc = [c[0] for c in cur.description]
            convertidos = [dict(zip(cols_nc, r)) for r in cur.fetchall()]
    except Exception: pass
"""

if 'SELECT * FROM cultos ORDER BY id DESC' not in app_code:
    app_code = re.sub(
        r'(\n\s*)(return\s+render_template\s*\(\s*[\'\"]dashboard\.html[\'\"])',
        r'\1' + leitura_dados.strip() + r'\1\2',
        app_code,
        count=1
    )

# Garantir passagem de parâmetros no render_template
if 'cultos=cultos' not in app_code:
    app_code = re.sub(r"(return\s+render_template\s*\(\s*['\"]dashboard\.html['\"]\s*,)", r"\1 cultos=cultos, ", app_code)
if 'convertidos=convertidos' not in app_code:
    app_code = re.sub(r"(return\s+render_template\s*\(\s*['\"]dashboard\.html['\"]\s*,)", r"\1 convertidos=convertidos, ", app_code)

# Validar com o analisador sintático do Python (AST)
try:
    ast.parse(app_code)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(app_code)
    print("✓ app.py validado e pronto com 0 erros de compilação!")
except SyntaxError as e_ast:
    print(f"❌ Erro de compilação: {e_ast}")
    shutil.copy('app.py.bak_botoes_ok', 'app.py')
    exit(1)

print("=" * 70)
print("✓ PROCESSO CONCLUÍDO COM SUCESSO TOTAL!")
print("=" * 70)
