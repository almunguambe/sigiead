import os
import shutil
import re
import ast
import jinja2

print("=" * 70)
print("A BLINDAR GRAVAÇÃO DE CONVERTIDOS, HISTÓRICO E CÁLCULO DE CULTOS...")
print("=" * 70)

# -------------------------------------------------------------
# 1. BLINDAGEM DO TEMPLATE (DASHBOARD.HTML)
# -------------------------------------------------------------
tpl_dash = os.path.join('templates', 'dashboard.html')
shutil.copy(tpl_dash, tpl_dash + '.bak_final')

with open(tpl_dash, 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

# A) Assegurar caixa de total e cálculo em tempo real de Cultos
caixa_total = '<input type="number" id="total_presentes_display" name="total_presentes" value="0" readonly style="width: 85%; padding: 6px; font-size: 20px; font-weight: bold; text-align: center; border: 2px solid #93c5fd; border-radius: 8px; color: #1e40af; background: #eff6ff;">'

if 'Calculado ao Gravar' in html:
    html = re.sub(r'<div[^>]*>\s*Calculado ao Gravar\s*</div>', caixa_total, html, count=1)
elif 'total_presentes_display' not in html:
    html = re.sub(r'(Total de Presentes[\s\S]*?)(<div[^>]*>[\s\S]*?</div>)', r'\1\n' + caixa_total, html, count=1)

script_calculo_cultos = """
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
if 'somarPresencasTempoReal' not in html:
    html = html + "\n" + script_calculo_cultos

# B) Assegurar que a tabela de Acompanhamento Espiritual lista os convertidos
if '{% for' not in html[html.find('Acompanhamento Espiritual'):html.find('Acompanhamento Espiritual')+1000]:
    tabela_convertidos_dinamica = """
            <table style="width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 13px;">
                <thead>
                    <tr style="border-bottom: 2px solid #e2e8f0; text-align: left; color: #475569;">
                        <th style="padding: 10px 8px;">Nome</th>
                        <th style="padding: 10px 8px;">Contacto</th>
                        <th style="padding: 10px 8px;">Estado Espiritual</th>
                    </tr>
                </thead>
                <tbody>
                    {% if convertidos %}
                        {% for c in convertidos %}
                        <tr style="border-bottom: 1px solid #f1f5f9;">
                            <td style="padding: 12px 8px; font-weight: bold; color: #1e293b;">{{ c.nome }}</td>
                            <td style="padding: 12px 8px; color: #475569;">{{ c.telefone or c.contato or '---' }}</td>
                            <td style="padding: 12px 8px;">
                                <span style="background-color: #dcfce7; color: #166534; padding: 4px 10px; border-radius: 6px; font-weight: bold; font-size: 12px;">
                                    {{ c.status_discipulado or 'Acompanhamento' }}
                                </span>
                            </td>
                        </tr>
                        {% endfor %}
                    {% else %}
                        <tr>
                            <td colspan="3" style="text-align: center; padding: 35px; color: #94a3b8;">
                                Nenhum novo convertido registado ainda.
                            </td>
                        </tr>
                    {% endif %}
                </tbody>
            </table>
    """
    pos_acomp = html.find('Acompanhamento Espiritual')
    if pos_acomp != -1:
        fim_card = html.find('</div>', pos_acomp)
        # Substitui conteúdo estático pelo dinâmico
        html = html[:pos_acomp + len('Acompanhamento Espiritual</h3>')] + tabela_convertidos_dinamica + html[fim_card:]

with open(tpl_dash, 'w', encoding='utf-8') as f:
    f.write(html)
print("✓ templates/dashboard.html atualizado e pronto!")

# -------------------------------------------------------------
# 2. BLINDAGEM DO BACKEND (APP.PY) COM ZERO ERRO DE INDENTAÇÃO
# -------------------------------------------------------------
shutil.copy('app.py', 'app.py.bak_final')
with open('app.py', 'r', encoding='utf-8', errors='ignore') as f:
    app_py = f.read()

# Garantir importações básicas no topo
if 'import re' not in app_py[:250]:
    app_py = "import re\nimport os\n" + app_py

# Bloco de rotas blindadas contra 400 Bad Request + Injetor Global
novas_rotas_e_contexto = '''
# =====================================================================
# ROTAS BLINDADAS: NOVOS CONVERTIDOS, CULTOS E INJEÇÃO GLOBAL
# =====================================================================

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
        if hasattr(conn, 'rollback'):
            try: conn.rollback()
            except: pass

    fd = request.form
    nome = (fd.get('nome') or fd.get('nome_completo') or fd.get('nome_convertido') or 'Sem Nome').strip()
    telefone = (fd.get('telefone') or fd.get('contato') or fd.get('contacto') or '').strip()
    bairro = (fd.get('bairro') or fd.get('residencia') or '').strip()
    data_decisao = (fd.get('data_decisao') or fd.get('data') or fd.get('data_conversao') or '').strip()
    quem_convidou = (fd.get('quem_convidou') or fd.get('convidado_por') or fd.get('discipulador') or '').strip()
    culto_origem = (fd.get('culto_origem') or fd.get('tipo_culto') or 'Geral').strip()

    from datetime import datetime
    if not data_decisao:
        data_decisao = datetime.now().strftime('%Y-%m-%d')

    m = "%s" if is_pg else "?"
    sql = f"""INSERT INTO novos_convertidos 
              (nome, telefone, bairro, data_decisao, quem_convidou, culto_origem, status_discipulado)
              VALUES ({m}, {m}, {m}, {m}, {m}, {m}, {m})"""
    try:
        cur.execute(sql, (nome, telefone, bairro, data_decisao, quem_convidou, culto_origem, 'Acompanhamento'))
        if hasattr(conn, 'commit'): conn.commit()
        print(f"[SUCESSO CONVERTIDO]: Registado com sucesso: {nome}")
    except Exception as e:
        print("[ERRO GRAVAÇÃO CONVERTIDO]:", e)
        if hasattr(conn, 'rollback'):
            try: conn.rollback()
            except: pass

    return redirect('/?aba=convertidos')

@app.route('/cultos/novo', methods=['POST'])
def cultos_novo():
    conn = get_db()
    cur = conn.cursor() if hasattr(conn, 'cursor') else conn
    is_pg = ('psycopg' in str(type(conn)).lower()) or bool(os.environ.get('DATABASE_URL'))
    id_tipo = "SERIAL PRIMARY KEY" if is_pg else "INTEGER PRIMARY KEY AUTOINCREMENT"
    
    try:
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS cultos (
                id {id_tipo},
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

    m = "%s" if is_pg else "?"
    sql = f"""INSERT INTO cultos 
             (data_culto, tipo_culto, homens_adultos, mulheres_adultas, jovens_rapazes, jovens_mocas, 
              criancas_meninos, criancas_meninas, visitantes_homens, visitantes_mulheres, 
              apelos, total_presentes, pregador, tema_mensagem)
             VALUES ({m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m})"""
    try:
        cur.execute(sql, (data_culto, tipo_culto, ha, ma, jr, jm, cm, cf, vh, vm, apelos, total, pregador, tema))
        if hasattr(conn, 'commit'): conn.commit()
        print(f"[SUCESSO CULTO]: Registado com Total={total}")
    except Exception as e:
        print("[ERRO GRAVAÇÃO CULTO]:", e)
        if hasattr(conn, 'rollback'):
            try: conn.rollback()
            except: pass

    return redirect('/?aba=cultos')

@app.context_processor
def injetar_listas_tabelas():
    dados = {'cultos': [], 'convertidos': [], 'novos_convertidos': []}
    try:
        conn = get_db()
        cur = conn.cursor() if hasattr(conn, 'cursor') else conn
        try:
            cur.execute("SELECT * FROM cultos ORDER BY id DESC LIMIT 50")
            if cur.description:
                cols = [c[0] for c in cur.description]
                dados['cultos'] = [dict(zip(cols, r)) for r in cur.fetchall()]
        except Exception: pass

        try:
            cur.execute("SELECT * FROM novos_convertidos ORDER BY id DESC LIMIT 50")
            if cur.description:
                cols_nc = [c[0] for c in cur.description]
                res_nc = [dict(zip(cols_nc, r)) for r in cur.fetchall()]
                dados['convertidos'] = res_nc
                dados['novos_convertidos'] = res_nc
        except Exception: pass
    except Exception: pass
    return dados
'''

# Remover rotas antigas duplicadas no final se existirem
app_py = re.sub(r'# =+[\s\n]*# ROTAS BLINDADAS[\s\S]*', '', app_py)
app_py = app_py.strip() + "\n\n" + novas_rotas_e_contexto.strip() + "\n"

# Validação estrita com AST (Garante 0 erros de sintaxe e indentação)
try:
    ast.parse(app_py)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(app_py)
    print("✓ app.py validado e gravado com 0 erros de compilação!")
except SyntaxError as e_ast:
    print(f"❌ Erro de compilação: {e_ast}")
    shutil.copy('app.py.bak_final', 'app.py')
    exit(1)

print("=" * 70)
print("✓ PROCESSO CONCLUÍDO COM SUCESSO TOTAL!")
print("=" * 70)
