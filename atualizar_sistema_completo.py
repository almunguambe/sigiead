import os
import shutil

print("=" * 80)
print("A ATUALIZAR O SISTEMA IEAD CHICUQUE COM TODAS AS NOVAS FUNCIONALIDADES...")
print("=" * 80)

# =============================================================================
# 1. ATUALIZAR APP.PY (DASHBOARDS, SELETORES DINÂMICOS, FEEDBACK E RELATÓRIO)
# =============================================================================
app_code = '''import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'iead_chicuque_chave_secreta_2026')

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db():
    if DATABASE_URL:
        import psycopg2
        import psycopg2.extras
        return psycopg2.connect(DATABASE_URL)
    else:
        conn = sqlite3.connect('igreja.db')
        conn.row_factory = sqlite3.Row
        return conn

def executar_comando(sql, params=()):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(sql, params)
        if hasattr(conn, 'commit'):
            conn.commit()
    except Exception as e:
        if hasattr(conn, 'rollback'):
            conn.rollback()
        print(f"[ERRO SQL]: {e}")
    finally:
        cur.close()
        conn.close()

def consultar_todos(sql, params=()):
    conn = get_db()
    cur = conn.cursor()
    dados = []
    try:
        cur.execute(sql, params)
        if cur.description:
            cols = [c[0].lower() for c in cur.description]
            for r in cur.fetchall():
                dados.append(dict(zip(cols, r)))
    except Exception as e:
        print(f"[ERRO CONSULTA]: {e}")
    finally:
        cur.close()
        conn.close()
    return dados

def consultar_um(sql, params=()):
    res = consultar_todos(sql, params)
    return res[0] if res else None

# -----------------------------------------------------------------------------
# MIGRAÇÕES E ESTRUTURAÇÃO DO BANCO
# -----------------------------------------------------------------------------
def inicializar_banco():
    is_pg = bool(DATABASE_URL)
    pk = "SERIAL PRIMARY KEY" if is_pg else "INTEGER PRIMARY KEY AUTOINCREMENT"
    
    tabelas = [
        f"""CREATE TABLE IF NOT EXISTS membros (
            id {pk}, nome TEXT, contacto TEXT, bi TEXT, cargo TEXT, departamento TEXT,
            data_nascimento TEXT, estado_civil TEXT, data_batismo TEXT, bairro TEXT, criado_em TEXT
        );""",
        f"""CREATE TABLE IF NOT EXISTS planificacao (
            id {pk}, actividade TEXT, titulo TEXT, nome_actividade TEXT, departamento TEXT,
            tipo_evento TEXT, data_prevista TEXT, data_inicio TEXT, frequencia TEXT,
            responsavel TEXT, contacto TEXT, status TEXT DEFAULT 'Planeado',
            feedback TEXT, participantes_homens INT DEFAULT 0, participantes_mulheres INT DEFAULT 0,
            participantes_jovens INT DEFAULT 0, participantes_criancas INT DEFAULT 0,
            total_participantes INT DEFAULT 0, data_execucao TEXT, criado_em TEXT
        );""",
        f"""CREATE TABLE IF NOT EXISTS novos_convertidos (
            id {pk}, nome TEXT, telefone TEXT, bairro TEXT, data_decisao TEXT,
            quem_convidou TEXT, culto_origem TEXT, status_discipulado TEXT DEFAULT 'Acompanhamento', criado_em TEXT
        );""",
        f"""CREATE TABLE IF NOT EXISTS cultos (
            id {pk}, data_culto TEXT, tipo_culto TEXT, homens_adultos INT DEFAULT 0,
            mulheres_adultas INT DEFAULT 0, jovens_rapazes INT DEFAULT 0, jovens_mocas INT DEFAULT 0,
            criancas_meninos INT DEFAULT 0, criancas_meninas INT DEFAULT 0, visitantes_homens INT DEFAULT 0,
            visitantes_mulheres INT DEFAULT 0, apelos INT DEFAULT 0, total_presentes INT DEFAULT 0,
            pregador TEXT, tema_mensagem TEXT, criado_em TEXT
        );""",
        f"""CREATE TABLE IF NOT EXISTS caixa (
            id {pk}, tipo TEXT, categoria TEXT, valor REAL, descricao TEXT, data_movimento TEXT, criado_em TEXT
        );""",
        f"""CREATE TABLE IF NOT EXISTS doutrina (
            id {pk}, nome_aluno TEXT, classe TEXT, professor TEXT, licao_atual TEXT,
            data_inicio TEXT, presencas INT DEFAULT 0, situacao TEXT DEFAULT 'Em Formação', criado_em TEXT
        );""",
        f"""CREATE TABLE IF NOT EXISTS opcoes_sistema (
            id {pk}, categoria TEXT, valor TEXT
        );"""
    ]
    for tab in tabelas:
        executar_comando(tab)

    # Migrações seguras de colunas caso as tabelas já existam
    if is_pg:
        cols_plan = [
            ("feedback", "TEXT"), ("participantes_homens", "INT DEFAULT 0"),
            ("participantes_mulheres", "INT DEFAULT 0"), ("participantes_jovens", "INT DEFAULT 0"),
            ("participantes_criancas", "INT DEFAULT 0"), ("total_participantes", "INT DEFAULT 0"),
            ("data_execucao", "TEXT")
        ]
        for col, tipo in cols_plan:
            try: executar_comando(f"ALTER TABLE planificacao ADD COLUMN IF NOT EXISTS {col} {tipo};")
            except: pass
    else:
        for col in ["feedback", "participantes_homens", "participantes_mulheres", "participantes_jovens", "participantes_criancas", "total_participantes", "data_execucao"]:
            try: executar_comando(f"ALTER TABLE planificacao ADD COLUMN {col} TEXT;")
            except: pass

    # Inserir seletores padrão se a tabela estiver vazia
    total_opcoes = consultar_um("SELECT COUNT(*) as tot FROM opcoes_sistema")
    if not total_opcoes or total_opcoes.get('tot', 0) == 0:
        opcoes_iniciais = [
            ('departamento', 'Juventude Cristã'), ('departamento', 'Círculo de Oração'),
            ('departamento', 'Escola Dominical'), ('departamento', 'Evangelismo & Missões'),
            ('departamento', 'Louvor & Adoração'), ('departamento', 'Direcção Geral'),
            ('cargo', 'Membro em Comunhão'), ('cargo', 'Activista / Obreiro'),
            ('cargo', 'Diácono / Diaconisa'), ('cargo', 'Presbítero'),
            ('cargo', 'Evangelista'), ('cargo', 'Pastor'),
            ('tipo_evento', 'Seminário'), ('tipo_evento', 'Retiro Espiritual'),
            ('tipo_evento', 'Aniversário de Departamento'), ('tipo_evento', 'Cruzada Evangelística'),
            ('tipo_evento', 'Vigília de Oração'), ('tipo_evento', 'Conferência Geral'),
            ('tipo_culto', 'Culto de Domingo'), ('tipo_culto', 'Estudo Bíblico / Doutrina'),
            ('tipo_culto', 'Culto de Oração'), ('tipo_culto', 'Santa Ceia'), ('tipo_culto', 'Culto de Jovens'),
            ('categoria_caixa', 'Dízimos'), ('categoria_caixa', 'Oferta de Culto'),
            ('categoria_caixa', 'Oferta de Missões'), ('categoria_caixa', 'Fundo de Construção'),
            ('categoria_caixa', 'Despesa Operacional'), ('categoria_caixa', 'Acção Social'),
            ('classe_doutrina', 'Preparação para Batismo nas Águas'),
            ('classe_doutrina', 'Discipulado de Novos Convertidos'),
            ('classe_doutrina', 'Formação Ministerial')
        ]
        m = "%s" if is_pg else "?"
        for cat, val in opcoes_iniciais:
            executar_comando(f"INSERT INTO opcoes_sistema (categoria, valor) VALUES ({m}, {m})", (cat, val))

inicializar_banco()

# -------------------------------------------------------------
# CONTEXT PROCESSOR: DADOS GERAIS, OPÇÕES E INDICADORES (KPIs)
# -------------------------------------------------------------
@app.context_processor
def injetar_dados():
    membros = consultar_todos("SELECT * FROM membros ORDER BY id DESC")
    planos = consultar_todos("SELECT * FROM planificacao ORDER BY id DESC")
    cultos = consultar_todos("SELECT * FROM cultos ORDER BY id DESC")
    convertidos = consultar_todos("SELECT * FROM novos_convertidos ORDER BY id DESC")
    caixa = consultar_todos("SELECT * FROM caixa ORDER BY id DESC")
    doutrina = consultar_todos("SELECT * FROM doutrina ORDER BY id DESC")
    opcoes_lista = consultar_todos("SELECT * FROM opcoes_sistema ORDER BY categoria, valor ASC")

    # Mapear seletores por categoria
    opcoes_map = {}
    for op in opcoes_lista:
        cat = op['categoria']
        if cat not in opcoes_map:
            opcoes_map[cat] = []
        opcoes_map[cat].append(op)

    # Indicadores do Painel (Dashboard Executivo)
    total_entradas = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Entrada'])
    total_saidas = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Saída'])
    saldo_caixa = total_entradas - total_saidas

    planos_executados = len([p for p in planos if p.get('status') == 'Executado'])
    taxa_execucao = int((planos_executados / len(planos) * 100)) if planos else 0

    total_presentes_cultos = sum([int(c.get('total_presentes') or 0) for c in cultos])
    media_assistencia = int(total_presentes_cultos / len(cultos)) if cultos else 0

    return {
        'membros': membros,
        'planificacoes': planos,
        'cronograma': planos,
        'cultos': cultos,
        'convertidos': convertidos,
        'caixa': caixa,
        'doutrina': doutrina,
        'opcoes': opcoes_map,
        'kpis': {
            'total_membros': len(membros),
            'total_planos': len(planos),
            'planos_executados': planos_executados,
            'taxa_execucao': taxa_execucao,
            'total_cultos': len(cultos),
            'media_assistencia': media_assistencia,
            'total_convertidos': len(convertidos),
            'total_entradas': total_entradas,
            'total_saidas': total_saidas,
            'saldo_caixa': saldo_caixa,
            'total_candidatos_batismo': len(doutrina)
        }
    }

# -------------------------------------------------------------
# ROTAS PRINCIPAIS
# -------------------------------------------------------------
@app.route('/')
def index():
    aba = request.args.get('aba', 'dashboard')
    id_relatar = request.args.get('relatar_id')
    plano_para_relatar = None
    if id_relatar:
        plano_para_relatar = consultar_um("SELECT * FROM planificacao WHERE id = " + ("%s" if DATABASE_URL else "?"), (id_relatar,))
    return render_template('dashboard.html', aba_ativa=aba, plano_relatar=plano_para_relatar)

# 1. Membros
@app.route('/membros/novo', methods=['POST'])
def membros_gravar():
    fd = request.form
    m = "%s" if DATABASE_URL else "?"
    sql = f"""INSERT INTO membros (nome, contacto, bi, cargo, departamento, data_nascimento, estado_civil, data_batismo, bairro, criado_em)
              VALUES ({m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m})"""
    params = (
        fd.get('nome', '').strip(), fd.get('contacto', '').strip(), fd.get('bi', '').strip(),
        fd.get('cargo', 'Membro').strip(), fd.get('departamento', 'Geral').strip(),
        fd.get('data_nascimento', '').strip(), fd.get('estado_civil', 'Solteiro(a)').strip(),
        fd.get('data_batismo', '').strip(), fd.get('bairro', '').strip(),
        datetime.now().strftime('%Y-%m-%d %H:%M')
    )
    executar_comando(sql, params)
    return redirect('/?aba=membros')

# Relatório 100% Completo de Cadastro (Página Imprimível / PDF)
@app.route('/membros/relatorio-geral')
def membros_relatorio_geral():
    membros = consultar_todos("SELECT * FROM membros ORDER BY nome ASC")
    return render_template('relatorio_membros.html', membros=membros, agora=datetime.now().strftime('%d/%m/%Y às %H:%M'))

# 2. Planificação: Criação
@app.route('/secretaria/planificacao', methods=['GET', 'POST'])
@app.route('/secretaria/planificacao/nova', methods=['GET', 'POST'])
def secretaria_gravar():
    if request.method == 'POST':
        fd = request.form
        act = (fd.get('actividade') or fd.get('nome_actividade') or 'Actividade').strip()
        dep = fd.get('departamento', 'Geral').strip()
        tipo = fd.get('tipo_evento', 'Evento').strip()
        dt = (fd.get('data_prevista') or datetime.now().strftime('%Y-%m-%d')).strip()
        freq = fd.get('frequencia', 'Pontual / Única').strip()
        resp = fd.get('responsavel', '').strip()
        cont = fd.get('contacto', '').strip()
        m = "%s" if DATABASE_URL else "?"
        sql = f"""INSERT INTO planificacao 
                  (actividade, titulo, nome_actividade, departamento, tipo_evento, data_prevista, data_inicio, frequencia, responsavel, contacto, status, criado_em)
                  VALUES ({m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, 'Planeado', {m})"""
        executar_comando(sql, (act, act, act, dep, tipo, dt, dt, freq, resp, cont, datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=secretaria')

# 2. Planificação: Prestação de Contas & Feedback de Execução
@app.route('/secretaria/planificacao/relatar', methods=['POST'])
def secretaria_relatar():
    fd = request.form
    plano_id = fd.get('plano_id')
    feedback = fd.get('feedback', '').strip()
    data_exec = fd.get('data_execucao', datetime.now().strftime('%Y-%m-%d')).strip()
    
    def to_int(k):
        v = fd.get(k)
        return int(v) if v and v.isdigit() else 0

    h, m_mulher = to_int('participantes_homens'), to_int('participantes_mulheres')
    jov, cri = to_int('participantes_jovens'), to_int('participantes_criancas')
    total = h + m_mulher + jov + cri

    m = "%s" if DATABASE_URL else "?"
    sql = f"""UPDATE planificacao SET 
              status = 'Executado',
              feedback = {m},
              data_execucao = {m},
              participantes_homens = {m},
              participantes_mulheres = {m},
              participantes_jovens = {m},
              participantes_criancas = {m},
              total_participantes = {m}
              WHERE id = {m}"""
    executar_comando(sql, (feedback, data_exec, h, m_mulher, jov, cri, total, plano_id))
    return redirect('/?aba=secretaria')

# 3. Cultos
@app.route('/cultos/novo', methods=['POST'])
def cultos_gravar():
    fd = request.form
    def n(k):
        v = fd.get(k)
        return int(v) if v and v.isdigit() else 0

    dt = fd.get('data_culto', datetime.now().strftime('%Y-%m-%d')).strip()
    tipo = fd.get('tipo_culto', 'Domingo').strip()
    ha, ma = n('homens_adultos'), n('mulheres_adultas')
    jr, jm = n('jovens_rapazes'), n('jovens_mocas')
    cm, cf = n('criancas_meninos'), n('criancas_meninas')
    vh, vm = n('visitantes_homens'), n('visitantes_mulheres')
    apelos = n('apelos')
    tot = ha + ma + jr + jm + cm + cf + vh + vm
    preg = fd.get('pregador', '').strip()
    tema = fd.get('tema_mensagem', '').strip()

    m = "%s" if DATABASE_URL else "?"
    sql = f"""INSERT INTO cultos 
              (data_culto, tipo_culto, homens_adultos, mulheres_adultas, jovens_rapazes, jovens_mocas,
               criancas_meninos, criancas_meninas, visitantes_homens, visitantes_mulheres, apelos, total_presentes, pregador, tema_mensagem, criado_em)
              VALUES ({m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m})"""
    executar_comando(sql, (dt, tipo, ha, ma, jr, jm, cm, cf, vh, vm, apelos, tot, preg, tema, datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=cultos')

# 4. Novos Convertidos
@app.route('/convertidos/novo', methods=['POST'])
def convertidos_gravar():
    fd = request.form
    nome = fd.get('nome', 'Sem Nome').strip()
    tel = fd.get('telefone', '').strip()
    bairro = fd.get('bairro', '').strip()
    dt = fd.get('data_decisao', datetime.now().strftime('%Y-%m-%d')).strip()
    conv = fd.get('quem_convidou', '').strip()
    orig = fd.get('culto_origem', 'Domingo').strip()

    m = "%s" if DATABASE_URL else "?"
    sql = f"""INSERT INTO novos_convertidos 
              (nome, telefone, bairro, data_decisao, quem_convidou, culto_origem, status_discipulado, criado_em)
              VALUES ({m}, {m}, {m}, {m}, {m}, {m}, 'Acompanhamento', {m})"""
    executar_comando(sql, (nome, tel, bairro, dt, conv, orig, datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=convertidos')

# 5. Caixa & Tesouraria
@app.route('/financas/caixa/novo', methods=['POST'])
def caixa_gravar():
    fd = request.form
    tipo = fd.get('tipo', 'Entrada').strip()
    cat = fd.get('categoria', 'Dízimos').strip()
    try: val = float(fd.get('valor') or 0)
    except: val = 0.0
    desc = fd.get('descricao', '').strip()
    dt = fd.get('data_movimento', datetime.now().strftime('%Y-%m-%d')).strip()

    m = "%s" if DATABASE_URL else "?"
    sql = f"INSERT INTO caixa (tipo, categoria, valor, descricao, data_movimento, criado_em) VALUES ({m}, {m}, {m}, {m}, {m}, {m})"
    executar_comando(sql, (tipo, cat, val, desc, dt, datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=financas')

# 6. Doutrina & Batismo
@app.route('/doutrina/novo', methods=['POST'])
def doutrina_gravar():
    fd = request.form
    aluno = fd.get('nome_aluno', 'Aluno').strip()
    classe = fd.get('classe', 'Preparação para Batismo').strip()
    prof = fd.get('professor', 'Pastor').strip()
    licao = fd.get('licao_atual', 'Lição 1').strip()
    dt = fd.get('data_inicio', datetime.now().strftime('%Y-%m-%d')).strip()

    m = "%s" if DATABASE_URL else "?"
    sql = f"""INSERT INTO doutrina 
              (nome_aluno, classe, professor, licao_atual, data_inicio, presencas, situacao, criado_em)
              VALUES ({m}, {m}, {m}, {m}, {m}, 1, 'Em Formação', {m})"""
    executar_comando(sql, (aluno, classe, prof, licao, dt, datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=doutrina')

# 7. Gestor de Seletores (Adicionar / Remover Opções pelo Administrador)
@app.route('/config/opcoes/adicionar', methods=['POST'])
def opcoes_adicionar():
    cat = request.form.get('categoria', '').strip()
    val = request.form.get('valor', '').strip()
    if cat and val:
        m = "%s" if DATABASE_URL else "?"
        executar_comando(f"INSERT INTO opcoes_sistema (categoria, valor) VALUES ({m}, {m})", (cat, val))
    return redirect('/?aba=configuracoes')

@app.route('/config/opcoes/remover/<int:id>', methods=['POST', 'GET'])
def opcoes_remover(id):
    m = "%s" if DATABASE_URL else "?"
    executar_comando(f"DELETE FROM opcoes_sistema WHERE id = {m}", (id,))
    return redirect('/?aba=configuracoes')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
'''

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_code)
print("✓ app.py atualizado com todas as rotas e migrações!")

# =============================================================================
# 2. CRIAR O TEMPLATE DO RELATÓRIO 100% COMPLETO DE MEMBRESIA (PDF/A4)
# =============================================================================
relatorio_html = '''<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <title>Relatório Oficial de Membresia - IEAD Chicuque</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @media print {
            .no-print { display: none !important; }
            body { background: white !important; padding: 0 !important; }
            @page { size: A4 portrait; margin: 15mm; }
        }
    </style>
</head>
<body class="bg-slate-100 p-8 font-sans text-slate-800">
    <div class="max-w-4xl mx-auto bg-white p-8 rounded-2xl shadow print:shadow-none print:p-0">
        <!-- BARRA DE IMPRESSÃO -->
        <div class="no-print flex justify-between items-center pb-6 mb-6 border-b">
            <a href="/?aba=membros" class="text-sm font-bold text-indigo-700 hover:underline">← Voltar ao Sistema</a>
            <button onclick="window.print()" class="px-5 py-2.5 bg-indigo-800 hover:bg-indigo-900 text-white font-bold rounded-xl shadow cursor-pointer text-sm">
                🖨️ Imprimir Relatório / Guardar em PDF
            </button>
        </div>

        <!-- CABEÇALHO OFICIAL DA IGREJA -->
        <div class="text-center pb-6 border-b-2 border-slate-800 mb-6">
            <h1 class="text-xl font-black uppercase tracking-wider text-slate-900">ASSEMBLEIA DE DEUS EM MOÇAMBIQUE</h1>
            <h2 class="text-sm font-bold uppercase tracking-wide text-slate-700">MINISTÉRIO THAVANE • SEDE REGIONAL DE CHICUQUE - MAXIXE</h2>
            <p class="text-xs text-slate-500 mt-1">Secretaria-Geral & Registo Oficial de Membresia • Emissão: {{ agora }}</p>
        </div>

        <div class="flex justify-between items-center mb-6 bg-slate-50 p-4 rounded-xl border border-slate-200">
            <div>
                <span class="text-xs uppercase font-bold text-slate-500">Documento:</span>
                <p class="text-base font-extrabold text-indigo-950">LIVRO DE REGISTO GERAL DE MEMBROS</p>
            </div>
            <div class="text-right">
                <span class="text-xs uppercase font-bold text-slate-500">Efetivo Cadastrado:</span>
                <p class="text-base font-extrabold text-indigo-700">{{ membros|length }} Membros Ativos</p>
            </div>
        </div>

        <!-- TABELA GERAL COMPLETA -->
        <table class="w-full text-left text-xs border border-slate-200 border-collapse mb-8">
            <thead>
                <tr class="bg-slate-100 border-b border-slate-300 text-slate-700 font-bold uppercase text-[10px]">
                    <th class="p-2.5 border-r">Nº</th>
                    <th class="p-2.5 border-r">Nome Completo</th>
                    <th class="p-2.5 border-r">BI / Documento</th>
                    <th class="p-2.5 border-r">Contacto</th>
                    <th class="p-2.5 border-r">Cargo Ministerial</th>
                    <th class="p-2.5 border-r">Departamento</th>
                    <th class="p-2.5">Bairro / Residência</th>
                </tr>
            </thead>
            <tbody>
                {% for m in membros %}
                <tr class="border-b border-slate-200 hover:bg-slate-50">
                    <td class="p-2.5 border-r font-bold text-slate-500">{{ loop.index }}</td>
                    <td class="p-2.5 border-r font-extrabold text-slate-900">{{ m.nome }}</td>
                    <td class="p-2.5 border-r text-slate-700">{{ m.bi or '---' }}</td>
                    <td class="p-2.5 border-r text-slate-700">{{ m.contacto or '---' }}</td>
                    <td class="p-2.5 border-r font-semibold text-indigo-900">{{ m.cargo }}</td>
                    <td class="p-2.5 border-r text-slate-700">{{ m.departamento }}</td>
                    <td class="p-2.5 text-slate-700">{{ m.bairro or '---' }}</td>
                </tr>
                {% else %}
                <tr>
                    <td colspan="7" class="p-6 text-center text-slate-400">Nenhum membro registado.</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>

        <!-- ASSINATURAS E CARIMBO -->
        <div class="grid grid-cols-2 gap-12 mt-16 pt-8 border-t border-slate-300 text-center text-xs">
            <div>
                <div class="w-48 mx-auto border-b border-slate-500 mb-1.5"></div>
                <p class="font-bold text-slate-800">O Secretário da Igreja</p>
                <p class="text-[10px] text-slate-400">IEAD Sede Chicuque</p>
            </div>
            <div>
                <div class="w-48 mx-auto border-b border-slate-500 mb-1.5"></div>
                <p class="font-bold text-slate-800">O Pastor Presidente</p>
                <p class="text-[10px] text-slate-400">Ministério Thavane</p>
            </div>
        </div>
    </div>
</body>
</html>
'''

with open(os.path.join('templates', 'relatorio_membros.html'), 'w', encoding='utf-8') as f:
    f.write(relatorio_html)
print("✓ templates/relatorio_membros.html criado com sucesso!")

# =============================================================================
# 3. ATUALIZAR O DASHBOARD.HTML COM TODAS AS TELAS E SELECTORES DINÂMICOS
# =============================================================================
dashboard_html = '''<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IEAD Chicuque - Gestão Eclesiástica Integrada</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.getRegistrations().then(function(regs) {
                for (let r of regs) r.unregister();
            });
        }
    </script>
</head>
<body class="bg-slate-100 text-slate-800 font-sans min-h-screen flex">

    <!-- MENU LATERAL -->
    <aside class="w-64 bg-slate-900 text-white flex flex-col justify-between min-h-screen shrink-0 shadow-xl">
        <div>
            <div class="p-5 border-b border-slate-800 flex items-center gap-3">
                <div class="w-11 h-11 rounded-full bg-white text-slate-900 flex items-center justify-center font-black text-lg shrink-0 shadow">AD</div>
                <div>
                    <h1 class="font-extrabold text-sm tracking-wide leading-tight">ASSEMBLEIA<br>DE DEUS</h1>
                    <p class="text-[11px] text-blue-300 mt-0.5">Sede Chicuque • Gestão 360°</p>
                </div>
            </div>

            <nav class="p-3 space-y-1 text-xs font-semibold">
                <div class="px-3 py-2 text-[10px] font-bold uppercase tracking-wider text-slate-400">Painel Principal</div>
                
                <a href="/?aba=dashboard" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'dashboard' %}bg-indigo-600 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                    <span>📊</span><span>Painel & Metas</span>
                </a>

                <div class="px-3 pt-3 pb-1 text-[10px] font-bold uppercase tracking-wider text-slate-400">Geral & Frequência</div>

                <a href="/?aba=membros" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'membros' %}bg-indigo-600 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                    <span>👥</span><span>1. Membros ({{ kpis.total_membros }})</span>
                </a>

                <a href="/?aba=secretaria" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'secretaria' %}bg-indigo-600 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                    <span>📋</span><span>2. Secretaria & Planos</span>
                </a>

                <a href="/?aba=cultos" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'cultos' %}bg-indigo-600 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                    <span>⛪</span><span>3. Cultos & Presenças</span>
                </a>

                <a href="/?aba=convertidos" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'convertidos' %}bg-indigo-600 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                    <span>🌱</span><span>4. Novos Convertidos</span>
                </a>

                <div class="px-3 pt-3 pb-1 text-[10px] font-bold uppercase tracking-wider text-emerald-400">Finanças & Ensino</div>

                <a href="/?aba=financas" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'financas' %}bg-indigo-600 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                    <span>💰</span><span>5. Movimentos de Caixa</span>
                </a>

                <a href="/?aba=doutrina" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'doutrina' %}bg-indigo-600 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                    <span>📖</span><span>6. Doutrina & Batismo</span>
                </a>

                <div class="px-3 pt-3 pb-1 text-[10px] font-bold uppercase tracking-wider text-purple-400">Administração</div>

                <a href="/?aba=configuracoes" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'configuracoes' %}bg-purple-700 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                    <span>⚙️</span><span>Gestor de Seletores</span>
                </a>
            </nav>
        </div>

        <div class="p-4 border-t border-slate-800 text-xs text-slate-400 flex items-center justify-between">
            <div>
                <p class="font-bold text-white">admin</p>
                <p class="text-[11px] text-amber-400">Pastor / Administração</p>
            </div>
            <span class="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
        </div>
    </aside>

    <!-- ÁREA PRINCIPAL -->
    <main class="flex-1 p-6 overflow-y-auto">

        <!-- ========================================================= -->
        <!-- ABA: DASHBOARD GERAL / RAIO-X 360°                        -->
        <!-- ========================================================= -->
        {% if aba_ativa == 'dashboard' %}
        <div class="bg-indigo-950 text-white p-6 rounded-2xl shadow mb-6">
            <h2 class="text-2xl font-black">📊 Painel Geral & Raio-X Eclesiástico</h2>
            <p class="text-xs text-indigo-300 mt-1">Visão estatística unificada em tempo real da Assembleia de Deus - Sede Chicuque</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
            <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200">
                <div class="text-slate-500 text-xs font-bold uppercase">Membros Cadastrados</div>
                <div class="text-3xl font-black text-indigo-950 mt-1">{{ kpis.total_membros }}</div>
                <div class="text-xs text-emerald-600 font-semibold mt-1">👥 Efetivo Total em Comunhão</div>
            </div>

            <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200">
                <div class="text-slate-500 text-xs font-bold uppercase">Execução de Planos</div>
                <div class="text-3xl font-black text-blue-700 mt-1">{{ kpis.taxa_execucao }}%</div>
                <div class="text-xs text-slate-500 font-semibold mt-1">{{ kpis.planos_executados }} de {{ kpis.total_planos }} actividades concluídas</div>
            </div>

            <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200">
                <div class="text-slate-500 text-xs font-bold uppercase">Média Presenças / Culto</div>
                <div class="text-3xl font-black text-amber-600 mt-1">{{ kpis.media_assistencia }}</div>
                <div class="text-xs text-slate-500 font-semibold mt-1">Total de {{ kpis.total_cultos }} cultos registados</div>
            </div>

            <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200">
                <div class="text-slate-500 text-xs font-bold uppercase">Saldo Geral de Caixa</div>
                <div class="text-3xl font-black {% if kpis.saldo_caixa >= 0 %}text-emerald-700{% else %}text-rose-700{% endif %} mt-1">
                    {{ "%.2f"|format(kpis.saldo_caixa) }} MT
                </div>
                <div class="text-xs text-slate-500 font-semibold mt-1">Entradas: {{ "%.2f"|format(kpis.total_entradas) }} MT</div>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-sm text-slate-800 border-b pb-3 mb-3">🌱 Novos Convertidos para Discipulado</h3>
                <div class="space-y-3">
                    {% for c in convertidos[:5] %}
                    <div class="flex justify-between items-center text-xs p-2.5 rounded-xl bg-slate-50">
                        <div>
                            <div class="font-bold text-slate-800">{{ c.nome }}</div>
                            <div class="text-[11px] text-slate-400">Decisão: {{ c.data_decisao }} • {{ c.bairro }}</div>
                        </div>
                        <span class="bg-emerald-100 text-emerald-800 px-2.5 py-1 rounded-full font-bold">{{ c.status_discipulado }}</span>
                    </div>
                    {% else %}
                    <p class="text-xs text-slate-400 text-center py-4">Nenhum convertido pendente.</p>
                    {% endfor %}
                </div>
            </div>

            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-sm text-slate-800 border-b pb-3 mb-3">📖 Candidatos ao Batismo (Escola Doutrinária)</h3>
                <div class="space-y-3">
                    {% for d in doutrina[:5] %}
                    <div class="flex justify-between items-center text-xs p-2.5 rounded-xl bg-slate-50">
                        <div>
                            <div class="font-bold text-slate-800">{{ d.nome_aluno }}</div>
                            <div class="text-[11px] text-slate-400">{{ d.classe }} • {{ d.licao_atual }}</div>
                        </div>
                        <span class="bg-amber-100 text-amber-800 px-2.5 py-1 rounded-full font-bold">{{ d.situacao }}</span>
                    </div>
                    {% else %}
                    <p class="text-xs text-slate-400 text-center py-4">Nenhum candidato em formação.</p>
                    {% endfor %}
                </div>
            </div>
        </div>
        {% endif %}

        <!-- ========================================================= -->
        <!-- ABA 1: MEMBROS & RELATÓRIO COMPLETO                       -->
        <!-- ========================================================= -->
        {% if aba_ativa == 'membros' %}
        <div class="bg-indigo-900 text-white p-5 rounded-2xl shadow mb-6 flex justify-between items-center">
            <div>
                <h2 class="text-xl font-extrabold">👥 Cadastro Geral de Membresia</h2>
                <p class="text-xs text-indigo-200 mt-1">Registo oficial com geração automática de relatório 100% completo</p>
            </div>
            <a href="/membros/relatorio-geral" target="_blank" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl text-xs shadow flex items-center gap-2">
                📄 Gerar Relatório 100% Completo (A4 / PDF)
            </a>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div class="lg:col-span-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">➕ Cadastrar Novo Membro</h3>
                <form action="/membros/novo" method="POST" class="space-y-3 text-xs">
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Nome Completo *</label>
                        <input type="text" name="nome" required placeholder="Nome do Membro" class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                    </div>
                    <div class="grid grid-cols-2 gap-2">
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">BI / Documento</label>
                            <input type="text" name="bi" placeholder="Nº de BI" class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                        </div>
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Contacto</label>
                            <input type="text" name="contacto" placeholder="+258..." class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                        </div>
                    </div>
                    <div class="grid grid-cols-2 gap-2">
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Cargo Ministerial</label>
                            <select name="cargo" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-semibold">
                                {% for op in opcoes.get('cargo', []) %}
                                <option value="{{ op.valor }}">{{ op.valor }}</option>
                                {% else %}
                                <option value="Membro em Comunhão">Membro em Comunhão</option>
                                {% endfor %}
                            </select>
                        </div>
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Departamento</label>
                            <select name="departamento" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-semibold">
                                {% for op in opcoes.get('departamento', []) %}
                                <option value="{{ op.valor }}">{{ op.valor }}</option>
                                {% else %}
                                <option value="Geral">Geral</option>
                                {% endfor %}
                            </select>
                        </div>
                    </div>
                    <div class="grid grid-cols-2 gap-2">
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Bairro / Residência</label>
                            <input type="text" name="bairro" placeholder="Ex: Chicuque" class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                        </div>
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Estado Civil</label>
                            <select name="estado_civil" class="w-full h-10 px-2 border rounded-xl bg-slate-50">
                                <option value="Solteiro(a)">Solteiro(a)</option>
                                <option value="Casado(a)">Casado(a)</option>
                                <option value="Viúvo(a)">Viúvo(a)</option>
                            </select>
                        </div>
                    </div>
                    <button type="submit" class="w-full py-3 bg-emerald-700 hover:bg-emerald-800 text-white font-bold rounded-xl shadow cursor-pointer transition">
                        Gravar Ficha de Membro
                    </button>
                </form>
            </div>

            <div class="lg:col-span-8 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">📋 Membros Registados ({{ membros|length }})</h3>
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse text-xs">
                        <thead>
                            <tr class="border-b-2 border-slate-200 text-slate-500">
                                <th class="py-2 px-2">Nome</th>
                                <th class="py-2 px-2">BI</th>
                                <th class="py-2 px-2">Contacto</th>
                                <th class="py-2 px-2">Cargo & Depto</th>
                                <th class="py-2 px-2">Bairro</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for m in membros %}
                            <tr class="border-b border-slate-100 hover:bg-slate-50">
                                <td class="py-2.5 px-2 font-bold text-slate-800">{{ m.nome }}</td>
                                <td class="py-2.5 px-2 text-slate-600">{{ m.bi or '---' }}</td>
                                <td class="py-2.5 px-2 text-slate-600">{{ m.contacto or '---' }}</td>
                                <td class="py-2.5 px-2">
                                    <span class="bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded font-bold">{{ m.cargo }}</span>
                                    <span class="text-slate-500 ml-1">• {{ m.departamento }}</span>
                                </td>
                                <td class="py-2.5 px-2 text-slate-600">{{ m.bairro or '---' }}</td>
                            </tr>
                            {% else %}
                            <tr><td colspan="5" class="py-8 text-center text-slate-400">Nenhum membro registado.</td></tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- ========================================================= -->
        <!-- ABA 2: SECRETARIA, PLANOS & FEEDBACK DE EXECUÇÃO          -->
        <!-- ========================================================= -->
        {% if aba_ativa == 'secretaria' %}
        <div class="bg-indigo-900 text-white p-5 rounded-2xl shadow mb-6">
            <h2 class="text-xl font-extrabold">📋 Secretaria & Planificação de Actividades</h2>
            <p class="text-xs text-indigo-200 mt-1">Planeamento e prestação de contas com feedback e assistência por género</p>
        </div>

        <!-- FORMULÁRIO DE PRESTAÇÃO DE CONTAS / FEEDBACK (SE SELECIONADO) -->
        {% if plano_relatar %}
        <div class="bg-amber-50 border-2 border-amber-300 p-6 rounded-2xl shadow mb-6">
            <div class="flex justify-between items-center mb-3">
                <h3 class="font-extrabold text-base text-amber-900">📝 Prestação de Contas: {{ plano_relatar.actividade }}</h3>
                <a href="/?aba=secretaria" class="text-xs font-bold text-amber-800 underline">Cancelar</a>
            </div>
            <form action="/secretaria/planificacao/relatar" method="POST" class="space-y-3.5 text-xs">
                <input type="hidden" name="plano_id" value="{{ plano_relatar.id }}">
                
                <div>
                    <label class="block font-bold text-slate-700 mb-1">Feedback do que foi realizado (Relatório Ministerial) *</label>
                    <textarea name="feedback" required rows="3" placeholder="Descreva os resultados, o impacto espiritual, objectivos alcançados..." class="w-full p-3 border rounded-xl bg-white"></textarea>
                </div>

                <div class="p-3 bg-white rounded-xl border border-amber-200">
                    <div class="font-bold text-slate-700 uppercase mb-2">Assistência / Participantes Divididos por Género</div>
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
                        <div>
                            <label class="block text-slate-500 mb-1">Homens</label>
                            <input type="number" name="participantes_homens" value="0" min="0" class="w-full h-9 px-2 border rounded-lg font-bold">
                        </div>
                        <div>
                            <label class="block text-slate-500 mb-1">Mulheres</label>
                            <input type="number" name="participantes_mulheres" value="0" min="0" class="w-full h-9 px-2 border rounded-lg font-bold">
                        </div>
                        <div>
                            <label class="block text-slate-500 mb-1">Jovens</label>
                            <input type="number" name="participantes_jovens" value="0" min="0" class="w-full h-9 px-2 border rounded-lg font-bold">
                        </div>
                        <div>
                            <label class="block text-slate-500 mb-1">Crianças</label>
                            <input type="number" name="participantes_criancas" value="0" min="0" class="w-full h-9 px-2 border rounded-lg font-bold">
                        </div>
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block font-semibold text-slate-700 mb-1">Data Real da Execução</label>
                        <input type="date" name="data_execucao" required class="w-full h-10 px-2 border rounded-xl bg-white">
                    </div>
                    <div class="flex items-end">
                        <button type="submit" class="w-full h-10 bg-emerald-700 hover:bg-emerald-800 text-white font-bold rounded-xl shadow cursor-pointer">
                            ✅ Concluir e Gravar Feedback
                        </button>
                    </div>
                </div>
            </form>
        </div>
        {% endif %}

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div class="lg:col-span-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">📌 Planificar Nova Actividade</h3>
                <form action="/secretaria/planificacao/nova" method="POST" class="space-y-3.5 text-xs">
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Departamento</label>
                        <select name="departamento" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-bold">
                            {% for op in opcoes.get('departamento', []) %}
                            <option value="{{ op.valor }}">{{ op.valor }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Tipo de Evento</label>
                        <select name="tipo_evento" class="w-full h-10 px-2 border rounded-xl bg-slate-50">
                            {% for op in opcoes.get('tipo_evento', []) %}
                            <option value="{{ op.valor }}">{{ op.valor }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Nome da Actividade *</label>
                        <input type="text" name="actividade" required placeholder="Ex: Seminário de Liderança" class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                    </div>
                    <div class="grid grid-cols-2 gap-2">
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Data Prevista</label>
                            <input type="date" name="data_prevista" required class="w-full h-10 px-2 border rounded-xl bg-slate-50">
                        </div>
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Frequência</label>
                            <select name="frequencia" class="w-full h-10 px-2 border rounded-xl bg-slate-50">
                                <option value="Pontual / Única">Pontual / Única</option>
                                <option value="Semanal">Semanal</option>
                                <option value="Mensal">Mensal</option>
                            </select>
                        </div>
                    </div>
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Responsável Directo</label>
                        <input type="text" name="responsavel" placeholder="Nome do Responsável" class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                    </div>
                    <button type="submit" class="w-full py-3 bg-indigo-800 hover:bg-indigo-900 text-white font-bold rounded-xl shadow cursor-pointer transition">
                        Gravar Planificação
                    </button>
                </form>
            </div>

            <div class="lg:col-span-8 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">📊 Cronograma & Prestação de Contas ({{ planificacoes|length }})</h3>
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse text-xs">
                        <thead>
                            <tr class="border-b-2 border-slate-200 text-slate-500">
                                <th class="py-2.5 px-2">Actividade / Depto</th>
                                <th class="py-2.5 px-2">Data</th>
                                <th class="py-2.5 px-2">Status</th>
                                <th class="py-2.5 px-2">Resultados / Assistência</th>
                                <th class="py-2.5 px-2 text-right">Ação</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for p in planificacoes %}
                            <tr class="border-b border-slate-100 hover:bg-slate-50">
                                <td class="py-3 px-2">
                                    <div class="font-bold text-indigo-900">{{ p.actividade or p.titulo }}</div>
                                    <div class="text-[11px] text-slate-500">{{ p.departamento }} • {{ p.tipo_evento }}</div>
                                </td>
                                <td class="py-3 px-2 font-semibold text-slate-700">{{ p.data_prevista }}</td>
                                <td class="py-3 px-2">
                                    {% if p.status == 'Executado' %}
                                    <span class="bg-emerald-100 text-emerald-800 px-2.5 py-1 rounded-full font-bold text-[11px]">✅ Executado</span>
                                    {% else %}
                                    <span class="bg-blue-100 text-blue-800 px-2.5 py-1 rounded-full font-bold text-[11px]">Planeado</span>
                                    {% endif %}
                                </td>
                                <td class="py-3 px-2">
                                    {% if p.status == 'Executado' %}
                                    <div class="font-bold text-slate-800">{{ p.total_participantes or 0 }} Participantes</div>
                                    <div class="text-[10px] text-slate-500">H: {{ p.participantes_homens }} | M: {{ p.participantes_mulheres }} | J: {{ p.participantes_jovens }} | C: {{ p.participantes_criancas }}</div>
                                    {% if p.feedback %}<p class="text-[11px] text-slate-600 italic mt-0.5 max-w-xs truncate">"{{ p.feedback }}"</p>{% endif %}
                                    {% else %}
                                    <span class="text-slate-400">Pendente de execução</span>
                                    {% endif %}
                                </td>
                                <td class="py-3 px-2 text-right">
                                    {% if p.status != 'Executado' %}
                                    <a href="/?aba=secretaria&relatar_id={{ p.id }}" class="px-3 py-1.5 bg-amber-600 hover:bg-amber-700 text-white rounded-lg font-bold text-[11px] shadow inline-block">
                                        📝 Relatar
                                    </a>
                                    {% else %}
                                    <span class="text-emerald-700 font-bold text-[11px]">Concluído</span>
                                    {% endif %}
                                </td>
                            </tr>
                            {% else %}
                            <tr><td colspan="5" class="py-8 text-center text-slate-400">Nenhuma actividade planificada.</td></tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- ========================================================= -->
        <!-- ABA 3: CULTOS & PRESENÇAS                                 -->
        <!-- ========================================================= -->
        {% if aba_ativa == 'cultos' %}
        <div class="bg-indigo-900 text-white p-5 rounded-2xl shadow mb-6">
            <h2 class="text-xl font-extrabold">⛪ Registo de Cultos & Estatística de Presenças</h2>
            <p class="text-xs text-indigo-200 mt-1">Estatística oficial de cultos e vidas no altar</p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div class="lg:col-span-5 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">📝 Lançar Culto</h3>
                <form action="/cultos/novo" method="POST" class="space-y-3 text-xs">
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Data *</label>
                            <input type="date" name="data_culto" required class="w-full h-10 px-2 border rounded-xl bg-slate-50">
                        </div>
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Tipo de Culto</label>
                            <select name="tipo_culto" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-bold">
                                {% for op in opcoes.get('tipo_culto', []) %}
                                <option value="{{ op.valor }}">{{ op.valor }}</option>
                                {% endfor %}
                            </select>
                        </div>
                    </div>

                    <div class="p-3 bg-slate-50 rounded-xl border border-slate-200 space-y-2">
                        <div class="font-bold text-slate-700 text-[11px] uppercase">Contagem de Frequência</div>
                        <div class="grid grid-cols-2 gap-2">
                            <div><label class="text-slate-500">Homens</label><input type="number" name="homens_adultos" value="0" min="0" oninput="somarCulto()" class="campo-soma w-full h-8 px-2 border rounded bg-white"></div>
                            <div><label class="text-slate-500">Mulheres</label><input type="number" name="mulheres_adultas" value="0" min="0" oninput="somarCulto()" class="campo-soma w-full h-8 px-2 border rounded bg-white"></div>
                            <div><label class="text-slate-500">Jovens (R)</label><input type="number" name="jovens_rapazes" value="0" min="0" oninput="somarCulto()" class="campo-soma w-full h-8 px-2 border rounded bg-white"></div>
                            <div><label class="text-slate-500">Jovens (M)</label><input type="number" name="jovens_mocas" value="0" min="0" oninput="somarCulto()" class="campo-soma w-full h-8 px-2 border rounded bg-white"></div>
                            <div><label class="text-slate-500">Crianças (M)</label><input type="number" name="criancas_meninos" value="0" min="0" oninput="somarCulto()" class="campo-soma w-full h-8 px-2 border rounded bg-white"></div>
                            <div><label class="text-slate-500">Crianças (F)</label><input type="number" name="criancas_meninas" value="0" min="0" oninput="somarCulto()" class="campo-soma w-full h-8 px-2 border rounded bg-white"></div>
                            <div><label class="text-slate-500">Visitantes (H)</label><input type="number" name="visitantes_homens" value="0" min="0" oninput="somarCulto()" class="campo-soma w-full h-8 px-2 border rounded bg-white"></div>
                            <div><label class="text-slate-500">Visitantes (M)</label><input type="number" name="visitantes_mulheres" value="0" min="0" oninput="somarCulto()" class="campo-soma w-full h-8 px-2 border rounded bg-white"></div>
                        </div>
                        <div class="grid grid-cols-2 gap-2 pt-2 border-t">
                            <div>
                                <label class="font-bold text-amber-700">🔥 Apelos</label>
                                <input type="number" name="apelos" value="0" min="0" class="w-full h-9 px-2 border-2 border-amber-300 rounded bg-amber-50 font-bold text-center">
                            </div>
                            <div>
                                <label class="font-bold text-blue-800">📊 Total</label>
                                <input type="number" id="total_presentes" name="total_presentes" value="0" readonly class="w-full h-9 px-2 border-2 border-blue-400 rounded bg-blue-50 font-extrabold text-center text-blue-900">
                            </div>
                        </div>
                    </div>

                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Pregador</label>
                            <input type="text" name="pregador" placeholder="Pregador" class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                        </div>
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Tema / Texto</label>
                            <input type="text" name="tema_mensagem" placeholder="Ex: Salmo 23" class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                        </div>
                    </div>

                    <button type="submit" class="w-full py-3 bg-indigo-700 hover:bg-indigo-800 text-white font-bold rounded-xl shadow cursor-pointer transition">
                        Gravar Relatório de Culto
                    </button>
                </form>
            </div>

            <div class="lg:col-span-7 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">📚 Histórico de Cultos ({{ cultos|length }})</h3>
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse text-xs">
                        <thead>
                            <tr class="border-b-2 border-slate-200 text-slate-500">
                                <th class="py-2.5 px-2">Data</th>
                                <th class="py-2.5 px-2">Culto & Pregador</th>
                                <th class="py-2.5 px-2 text-center">Presentes</th>
                                <th class="py-2.5 px-2 text-center">Apelos</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for c in cultos %}
                            <tr class="border-b border-slate-100 hover:bg-slate-50">
                                <td class="py-3 px-2 font-semibold text-slate-700">{{ c.data_culto }}</td>
                                <td class="py-3 px-2">
                                    <div class="font-bold text-slate-800">{{ c.tipo_culto }}</div>
                                    <div class="text-[11px] text-slate-500">{{ c.pregador or '---' }}</div>
                                </td>
                                <td class="py-3 px-2 text-center">
                                    <span class="bg-blue-100 text-blue-900 px-3 py-1 rounded-full font-bold">{{ c.total_presentes }}</span>
                                </td>
                                <td class="py-3 px-2 text-center">
                                    <span class="bg-amber-100 text-amber-800 px-2.5 py-1 rounded-full font-bold">{{ c.apelos }}</span>
                                </td>
                            </tr>
                            {% else %}
                            <tr><td colspan="4" class="py-8 text-center text-slate-400">Nenhum culto registado.</td></tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- ========================================================= -->
        <!-- ABA 4: NOVOS CONVERTIDOS                                  -->
        <!-- ========================================================= -->
        {% if aba_ativa == 'convertidos' %}
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div class="lg:col-span-5 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">🌱 Registar Novo Convertido</h3>
                <form action="/convertidos/novo" method="POST" class="space-y-3.5 text-xs">
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Nome Completo *</label>
                        <input type="text" name="nome" required placeholder="Nome do Convertido" class="w-full h-11 px-3 border rounded-xl bg-blue-50/50">
                    </div>
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Contacto / Telefone</label>
                        <input type="text" name="telefone" placeholder="+258..." class="w-full h-11 px-3 border rounded-xl bg-blue-50/50">
                    </div>
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Data da Decisão</label>
                        <input type="date" name="data_decisao" required class="w-full h-11 px-3 border rounded-xl bg-white">
                    </div>
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Bairro / Residência</label>
                        <input type="text" name="bairro" placeholder="Ex: Chicuque" class="w-full h-11 px-3 border rounded-xl bg-blue-50/50">
                    </div>
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Quem Convidou / Discipulador</label>
                        <input type="text" name="quem_convidou" placeholder="Nome do Discipulador" class="w-full h-11 px-3 border rounded-xl bg-blue-50/50">
                    </div>
                    <button type="submit" class="w-full py-3.5 bg-emerald-700 hover:bg-emerald-800 text-white font-bold rounded-xl shadow cursor-pointer text-sm">
                        Registar para Discipulado
                    </button>
                </form>
            </div>

            <div class="lg:col-span-7 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">Acompanhamento Espiritual ({{ convertidos|length }})</h3>
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse text-xs">
                        <thead>
                            <tr class="border-b-2 border-slate-200 text-slate-600 bg-slate-50">
                                <th class="py-3 px-3">Nome</th>
                                <th class="py-3 px-3">Contacto</th>
                                <th class="py-3 px-3">Bairro</th>
                                <th class="py-3 px-3">Estado</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for c in convertidos %}
                            <tr class="border-b border-slate-100 hover:bg-slate-50">
                                <td class="py-3.5 px-3 font-bold text-slate-800">{{ c.nome }}<div class="text-[11px] font-normal text-slate-400">{{ c.data_decisao }}</div></td>
                                <td class="py-3.5 px-3 text-slate-600">{{ c.telefone or '---' }}</td>
                                <td class="py-3.5 px-3 text-slate-600">{{ c.bairro or '---' }}</td>
                                <td class="py-3.5 px-3"><span class="bg-emerald-100 text-emerald-800 px-3 py-1 rounded-full font-bold text-[11px]">{{ c.status_discipulado }}</span></td>
                            </tr>
                            {% else %}
                            <tr><td colspan="4" class="py-10 text-center text-slate-400">Nenhum novo convertido registado.</td></tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- ========================================================= -->
        <!-- ABA 5: FINANÇAS & CAIXA                                   -->
        <!-- ========================================================= -->
        {% if aba_ativa == 'financas' %}
        <div class="bg-emerald-900 text-white p-5 rounded-2xl shadow mb-6">
            <h2 class="text-xl font-extrabold">💰 Tesouraria & Movimentos de Caixa</h2>
            <p class="text-xs text-emerald-200 mt-1">Dízimos, ofertas e despesas da IEAD Chicuque</p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div class="lg:col-span-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">➕ Lançamento no Caixa</h3>
                <form action="/financas/caixa/novo" method="POST" class="space-y-3.5 text-xs">
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Tipo</label>
                            <select name="tipo" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-bold">
                                <option value="Entrada">🟢 Entrada (+)</option>
                                <option value="Saída">🔴 Saída (-)</option>
                            </select>
                        </div>
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Data</label>
                            <input type="date" name="data_movimento" required class="w-full h-10 px-2 border rounded-xl bg-slate-50">
                        </div>
                    </div>
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Categoria</label>
                        <select name="categoria" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-semibold">
                            {% for op in opcoes.get('categoria_caixa', []) %}
                            <option value="{{ op.valor }}">{{ op.valor }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Valor (MZN) *</label>
                        <input type="number" step="0.01" name="valor" required placeholder="Ex: 2500.00" class="w-full h-10 px-3 border rounded-xl bg-slate-50 font-bold text-sm">
                    </div>
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Descrição</label>
                        <input type="text" name="descricao" placeholder="Detalhes..." class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                    </div>
                    <button type="submit" class="w-full py-3 bg-emerald-700 hover:bg-emerald-800 text-white font-bold rounded-xl shadow cursor-pointer transition">
                        Gravar Movimento
                    </button>
                </form>
            </div>

            <div class="lg:col-span-8 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">📊 Livro Caixa ({{ caixa|length }})</h3>
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse text-xs">
                        <thead>
                            <tr class="border-b-2 border-slate-200 text-slate-500">
                                <th class="py-2.5 px-2">Data</th>
                                <th class="py-2.5 px-2">Tipo</th>
                                <th class="py-2.5 px-2">Categoria & Descrição</th>
                                <th class="py-2.5 px-2 text-right">Valor</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for cx in caixa %}
                            <tr class="border-b border-slate-100 hover:bg-slate-50">
                                <td class="py-3 px-2 text-slate-600">{{ cx.data_movimento }}</td>
                                <td class="py-3 px-2"><span class="{% if cx.tipo == 'Entrada' %}bg-emerald-100 text-emerald-800{% else %}bg-rose-100 text-rose-800{% endif %} px-2 py-0.5 rounded font-bold">{{ cx.tipo }}</span></td>
                                <td class="py-3 px-2 font-bold">{{ cx.categoria }}<div class="text-[11px] text-slate-400 font-normal">{{ cx.descricao }}</div></td>
                                <td class="py-3 px-2 text-right font-extrabold {% if cx.tipo == 'Entrada' %}text-emerald-700{% else %}text-rose-700{% endif %}">
                                    {{ "%.2f"|format(cx.valor or 0) }} MT
                                </td>
                            </tr>
                            {% else %}
                            <tr><td colspan="4" class="py-8 text-center text-slate-400">Nenhum movimento no caixa.</td></tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- ========================================================= -->
        <!-- ABA 6: DOUTRINA & CANDIDATOS AO BATISMO                   -->
        <!-- ========================================================= -->
        {% if aba_ativa == 'doutrina' %}
        <div class="bg-amber-900 text-white p-5 rounded-2xl shadow mb-6">
            <h2 class="text-xl font-extrabold">📖 Escola de Doutrina & Candidatos ao Batismo</h2>
            <p class="text-xs text-amber-200 mt-1">Preparação batismal e formação discipular oficial</p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div class="lg:col-span-5 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">🎓 Inscrever Candidato</h3>
                <form action="/doutrina/novo" method="POST" class="space-y-3.5 text-xs">
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Nome do Candidato *</label>
                        <input type="text" name="nome_aluno" required placeholder="Nome completo" class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                    </div>
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Classe</label>
                        <select name="classe" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-bold">
                            {% for op in opcoes.get('classe_doutrina', []) %}
                            <option value="{{ op.valor }}">{{ op.valor }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Lição Atual</label>
                        <input type="text" name="licao_atual" value="Lição 1 - A Salvação" class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                    </div>
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Professor</label>
                            <input type="text" name="professor" placeholder="Pr. / Diác." class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                        </div>
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Data Início</label>
                            <input type="date" name="data_inicio" required class="w-full h-10 px-2 border rounded-xl bg-slate-50">
                        </div>
                    </div>
                    <button type="submit" class="w-full py-3 bg-amber-700 hover:bg-amber-800 text-white font-bold rounded-xl shadow cursor-pointer transition">
                        Gravar Candidato
                    </button>
                </form>
            </div>

            <div class="lg:col-span-7 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">📋 Candidatos em Formação ({{ doutrina|length }})</h3>
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse text-xs">
                        <thead>
                            <tr class="border-b-2 border-slate-200 text-slate-500">
                                <th class="py-2.5 px-2">Nome</th>
                                <th class="py-2.5 px-2">Classe</th>
                                <th class="py-2.5 px-2">Progresso</th>
                                <th class="py-2.5 px-2">Situação</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for d in doutrina %}
                            <tr class="border-b border-slate-100 hover:bg-slate-50">
                                <td class="py-3 px-2 font-bold text-slate-800">{{ d.nome_aluno }}</td>
                                <td class="py-3 px-2 text-slate-600">{{ d.classe }}</td>
                                <td class="py-3 px-2 font-semibold text-amber-900">{{ d.licao_atual }}</td>
                                <td class="py-3 px-2"><span class="bg-amber-100 text-amber-800 px-2 py-0.5 rounded font-bold text-[11px]">{{ d.situacao }}</span></td>
                            </tr>
                            {% else %}
                            <tr><td colspan="4" class="py-8 text-center text-slate-400">Nenhum candidato inscrito.</td></tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- ========================================================= -->
        <!-- ABA 7: GESTOR DE SELETORES (PERSONALIZAÇÃO TOTAL PELO ADM) -->
        <!-- ========================================================= -->
        {% if aba_ativa == 'configuracoes' %}
        <div class="bg-purple-950 text-white p-5 rounded-2xl shadow mb-6">
            <h2 class="text-xl font-extrabold">⚙️ Gestor de Seletores & Configurações do Sistema</h2>
            <p class="text-xs text-purple-300 mt-1">Adicione ou remova campos e opções dos menus pendentes sem mexer em código</p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div class="lg:col-span-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">➕ Adicionar Nova Opção</h3>
                <form action="/config/opcoes/adicionar" method="POST" class="space-y-4 text-xs">
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Qual lista deseja atualizar? *</label>
                        <select name="categoria" required class="w-full h-11 px-3 border rounded-xl bg-slate-50 font-bold">
                            <option value="departamento">📁 Departamentos da Igreja</option>
                            <option value="cargo">✝️ Cargos Ministeriais</option>
                            <option value="tipo_evento">🎪 Tipos de Eventos / Actividades</option>
                            <option value="tipo_culto">⛪ Tipos de Cultos</option>
                            <option value="categoria_caixa">💰 Categorias do Caixa / Tesouraria</option>
                            <option value="classe_doutrina">📖 Classes de Doutrina</option>
                        </select>
                    </div>
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Nome da Nova Opção *</label>
                        <input type="text" name="valor" required placeholder="Ex: Grupo de Intercessão" class="w-full h-11 px-3 border rounded-xl bg-slate-50">
                    </div>
                    <button type="submit" class="w-full py-3.5 bg-purple-700 hover:bg-purple-800 text-white font-bold rounded-xl shadow cursor-pointer text-sm transition">
                        Gravar Nova Opção
                    </button>
                </form>
            </div>

            <div class="lg:col-span-8 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">📋 Seletores Ativos no Sistema</h3>
                
                <div class="space-y-6 text-xs">
                    {% for cat, itens in opcoes.items() %}
                    <div class="border rounded-xl p-4 bg-slate-50">
                        <div class="font-black text-slate-700 uppercase tracking-wider mb-2.5 flex justify-between items-center">
                            <span>📌 {{ cat.replace('_', ' ').title() }}</span>
                            <span class="text-[10px] bg-slate-200 text-slate-700 px-2 py-0.5 rounded-full font-bold">{{ itens|length }} opções</span>
                        </div>
                        <div class="flex flex-wrap gap-2">
                            {% for op in itens %}
                            <span class="inline-flex items-center gap-2 bg-white border border-slate-200 px-3 py-1.5 rounded-lg text-slate-800 font-semibold shadow-sm">
                                {{ op.valor }}
                                <a href="/config/opcoes/remover/{{ op.id }}" onclick="return confirm('Remover esta opção?')" class="text-rose-500 hover:text-rose-700 font-bold ml-1 text-sm leading-none" title="Remover">×</a>
                            </span>
                            {% endfor %}
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
        {% endif %}

    </main>

    <script>
        function somarCulto() {
            var inputs = document.querySelectorAll('.campo-soma');
            var tot = 0;
            inputs.forEach(function(i) { tot += (parseInt(i.value, 10) || 0); });
            var el = document.getElementById('total_presentes');
            if (el) el.value = tot;
        }
    </script>
</body>
</html>
'''

with open(os.path.join('templates', 'dashboard.html'), 'w', encoding='utf-8') as f:
    f.write(dashboard_html)
print("✓ templates/dashboard.html atualizado com Dashboards, Relatórios, Prestação de Contas e Seletores!")

print("=" * 80)
print("SISTEMA TOTALMENTE ATUALIZADO COM SUCESSO!")
print("=" * 80)