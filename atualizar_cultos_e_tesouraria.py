import os

print("=" * 80)
print("A ATUALIZAR CULTOS (GÉNERO CRIANÇAS) E SEPARAÇÃO DE TESOURARIA...")
print("=" * 80)

# =============================================================================
# 1. ATUALIZAR APP.PY
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

def inicializar_banco():
    is_pg = bool(DATABASE_URL)
    pk = "SERIAL PRIMARY KEY" if is_pg else "INTEGER PRIMARY KEY AUTOINCREMENT"
    
    tabelas = [
        f"""CREATE TABLE IF NOT EXISTS membros (
            id {pk}, nome TEXT, contacto TEXT, bi TEXT, cargo TEXT, departamento TEXT,
            data_nascimento TEXT, estado_civil TEXT, ano_conversao TEXT, data_batismo TEXT,
            zona TEXT, celula TEXT, local_residencia TEXT, bairro TEXT, criado_em TEXT
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

    # Inserir seletores padrão se vazio
    total_opcoes = consultar_um("SELECT COUNT(*) as tot FROM opcoes_sistema")
    if not total_opcoes or total_opcoes.get('tot', 0) == 0:
        opcoes_iniciais = [
            ('departamento', 'Juventude Cristã'), ('departamento', 'Círculo de Oração'),
            ('departamento', 'Escola Dominical'), ('departamento', 'Evangelismo & Missões'),
            ('departamento', 'Louvor & Adoração'), ('departamento', 'Direcção Geral'),
            ('cargo', 'Membro em Comunhão'), ('cargo', 'Activista / Obreiro'),
            ('cargo', 'Diácono / Diaconisa'), ('cargo', 'Presbítero'),
            ('cargo', 'Evangelista'), ('cargo', 'Pastor'),
            ('zona', 'Zona 1 - Central / Chicuque'), ('zona', 'Zona 2 - Hospital'),
            ('zona', 'Zona 3 - Estrada Nacional'), ('zona', 'Zona 4 - Expansão'),
            ('celula', 'Célula Betel'), ('celula', 'Célula Ebenézer'),
            ('celula', 'Célula Jerusalém'), ('celula', 'Célula Peniel'),
            ('estado_civil', 'Criança'), ('estado_civil', 'Solteiro(a)'),
            ('estado_civil', 'Casado(a)'), ('estado_civil', 'Viúvo(a)'),
            ('tipo_evento', 'Seminário'), ('tipo_evento', 'Retiro Espiritual'),
            ('tipo_evento', 'Aniversário de Departamento'), ('tipo_evento', 'Cruzada Evangelística'),
            ('tipo_culto', 'Culto de Domingo'), ('tipo_culto', 'Estudo Bíblico / Doutrina'),
            ('tipo_culto', 'Culto de Oração'), ('tipo_culto', 'Santa Ceia'),
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

@app.context_processor
def injetar_dados():
    membros = consultar_todos("SELECT * FROM membros ORDER BY id DESC")
    planos = consultar_todos("SELECT * FROM planificacao ORDER BY id DESC")
    cultos = consultar_todos("SELECT * FROM cultos ORDER BY id DESC")
    convertidos = consultar_todos("SELECT * FROM novos_convertidos ORDER BY id DESC")
    caixa = consultar_todos("SELECT * FROM caixa ORDER BY id DESC")
    doutrina = consultar_todos("SELECT * FROM doutrina ORDER BY id DESC")
    opcoes_lista = consultar_todos("SELECT * FROM opcoes_sistema ORDER BY categoria, valor ASC")

    opcoes_map = {}
    for op in opcoes_lista:
        opcoes_map.setdefault(op['categoria'], []).append(op)

    total_entradas = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Entrada'])
    total_saidas = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Saída'])
    saldo_caixa = total_entradas - total_saidas
    
    total_dizimos = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Entrada' and 'dízimo' in str(c.get('categoria', '')).lower()])
    total_ofertas = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Entrada' and 'oferta' in str(c.get('categoria', '')).lower()])
    total_missoes = sum([float(c.get('valor') or 0) for c in caixa if 'miss' in str(c.get('categoria', '')).lower() or 'constru' in str(c.get('categoria', '')).lower()])
    taxa_gasto = int((total_saidas / total_entradas * 100)) if total_entradas > 0 else 0

    categorias_caixa_valores = {}
    for c in caixa:
        cat = c.get('categoria') or 'Geral'
        v = float(c.get('valor') or 0)
        categorias_caixa_valores[cat] = categorias_caixa_valores.get(cat, 0.0) + v

    aptos_batismo = [d for d in doutrina if 'apto' in str(d.get('situacao', '')).lower() or 'conclu' in str(d.get('licao_atual', '')).lower()]
    em_formacao = [d for d in doutrina if d not in aptos_batismo]
    classes_contagem = {}
    for d in doutrina:
        cls = d.get('classe') or 'Geral'
        classes_contagem[cls] = classes_contagem.get(cls, 0) + 1

    planos_executados = len([p for p in planos if p.get('status') == 'Executado'])
    taxa_execucao = int((planos_executados / len(planos) * 100)) if planos else 0
    total_pres = sum([int(c.get('total_presentes') or 0) for c in cultos])
    media_assistencia = int(total_pres / len(cultos)) if cultos else 0

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
            'total_dizimos': total_dizimos,
            'total_ofertas': total_ofertas,
            'total_missoes': total_missoes,
            'taxa_gasto': taxa_gasto,
            'categorias_caixa': categorias_caixa_valores,
            'total_doutrina': len(doutrina),
            'total_aptos_batismo': len(aptos_batismo),
            'total_em_formacao': len(em_formacao),
            'aptos_lista': aptos_batismo,
            'classes_contagem': classes_contagem
        }
    }

@app.route('/')
def index():
    aba = request.args.get('aba', 'dashboard')
    id_relatar = request.args.get('relatar_id')
    plano_para_relatar = None
    if id_relatar:
        m = "%s" if DATABASE_URL else "?"
        plano_para_relatar = consultar_um(f"SELECT * FROM planificacao WHERE id = {m}", (id_relatar,))
    return render_template('dashboard.html', aba_ativa=aba, plano_relatar=plano_para_relatar)

@app.route('/membros/novo', methods=['POST'])
def membros_gravar():
    fd = request.form
    m = "%s" if DATABASE_URL else "?"
    sql = f"""INSERT INTO membros 
              (nome, contacto, bi, cargo, departamento, estado_civil, zona, celula, ano_conversao, data_batismo, local_residencia, bairro, criado_em)
              VALUES ({m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m})"""
    local = (fd.get('local_residencia') or fd.get('bairro') or '').strip()
    params = (
        fd.get('nome', '').strip(), fd.get('contacto', '').strip(), fd.get('bi', '').strip(),
        fd.get('cargo', 'Membro em Comunhão').strip(), fd.get('departamento', 'Geral').strip(),
        fd.get('estado_civil', 'Solteiro(a)').strip(), fd.get('zona', 'Zona 1 - Central').strip(),
        fd.get('celula', 'Geral').strip(), fd.get('ano_conversao', '').strip(),
        fd.get('data_batismo', '').strip(), local, local, datetime.now().strftime('%Y-%m-%d %H:%M')
    )
    executar_comando(sql, params)
    return redirect('/?aba=membros')

@app.route('/membros/relatorio-geral')
def membros_relatorio_geral():
    membros = consultar_todos("SELECT * FROM membros ORDER BY nome ASC")
    return render_template('relatorio_membros.html', membros=membros, agora=datetime.now().strftime('%d/%m/%Y às %H:%M'))

@app.route('/membros/<int:id>/cartao')
def membros_cartao(id):
    m = "%s" if DATABASE_URL else "?"
    membro = consultar_um(f"SELECT * FROM membros WHERE id = {m}", (id,))
    if not membro: return redirect('/?aba=membros')
    return render_template('cartao_membro.html', m=m, agora=datetime.now().strftime('%Y'))

@app.route('/membros/<int:id>/batismo')
def membros_batismo(id):
    m = "%s" if DATABASE_URL else "?"
    membro = consultar_um(f"SELECT * FROM membros WHERE id = {m}", (id,))
    if not membro or not membro.get('data_batismo'):
        return "<script>alert('Este membro ainda não possui data de batismo registada!'); window.location.href='/?aba=membros';</script>"
    return render_template('cartao_batismo.html', m=m, data_extenso=datetime.now().strftime('%d de %B de %Y'))

@app.route('/membros/<int:id>/recomendacao')
def membros_recomendacao(id):
    m = "%s" if DATABASE_URL else "?"
    membro = consultar_um(f"SELECT * FROM membros WHERE id = {m}", (id,))
    if not membro: return redirect('/?aba=membros')
    return render_template('carta_recomendacao.html', m=m, data_extenso=datetime.now().strftime('%d de %B de %Y'))

@app.route('/secretaria/planificacao/nova', methods=['POST'])
def secretaria_gravar():
    fd = request.form
    act = (fd.get('actividade') or 'Actividade').strip()
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
              status = 'Executado', feedback = {m}, data_execucao = {m},
              participantes_homens = {m}, participantes_mulheres = {m},
              participantes_jovens = {m}, participantes_criancas = {m},
              total_participantes = {m} WHERE id = {m}"""
    executar_comando(sql, (feedback, data_exec, h, m_mulher, jov, cri, total, plano_id))
    return redirect('/?aba=secretaria')

# CULTOS & PRESENÇAS: CONTAGEM COM CRIANÇAS POR GÉNERO
@app.route('/cultos/novo', methods=['POST'])
def cultos_gravar():
    fd = request.form
    def n(k):
        v = fd.get(k)
        return int(v) if v and v.isdigit() else 0
    dt = fd.get('data_culto', datetime.now().strftime('%Y-%m-%d')).strip()
    tipo = fd.get('tipo_culto', 'Culto de Domingo').strip()
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

@app.route('/convertidos/novo', methods=['POST'])
def convertidos_gravar():
    fd = request.form
    nome = fd.get('nome', 'Sem Nome').strip()
    tel = fd.get('telefone', '').strip()
    bairro = fd.get('bairro', '').strip()
    dt = fd.get('data_decisao', datetime.now().strftime('%Y-%m-%d')).strip()
    conv = fd.get('quem_convidou', '').strip()
    orig = fd.get('culto_origem', 'Culto de Domingo').strip()
    m = "%s" if DATABASE_URL else "?"
    sql = f"""INSERT INTO novos_convertidos 
              (nome, telefone, bairro, data_decisao, quem_convidou, culto_origem, status_discipulado, criado_em)
              VALUES ({m}, {m}, {m}, {m}, {m}, {m}, 'Acompanhamento', {m})"""
    executar_comando(sql, (nome, tel, bairro, dt, conv, orig, datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=convertidos')

# CAIXA & TESOURARIA: REDIRECIONA PARA A ABA DA TESOUREIRA
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
    return redirect('/?aba=tesouraria')

@app.route('/doutrina/novo', methods=['POST'])
def doutrina_gravar():
    fd = request.form
    aluno = fd.get('nome_aluno', 'Aluno').strip()
    classe = fd.get('classe', 'Preparação para Batismo nas Águas').strip()
    prof = fd.get('professor', 'Pastor').strip()
    licao = fd.get('licao_atual', 'Lição 1 - A Salvação').strip()
    dt = fd.get('data_inicio', datetime.now().strftime('%Y-%m-%d')).strip()
    m = "%s" if DATABASE_URL else "?"
    sql = f"""INSERT INTO doutrina 
              (nome_aluno, classe, professor, licao_atual, data_inicio, presencas, situacao, criado_em)
              VALUES ({m}, {m}, {m}, {m}, {m}, 1, 'Em Formação', {m})"""
    executar_comando(sql, (aluno, classe, prof, licao, dt, datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=doutrina')

@app.route('/doutrina/aprovar/<int:id>')
def doutrina_aprovar(id):
    m = "%s" if DATABASE_URL else "?"
    executar_comando(f"UPDATE doutrina SET situacao = 'Apto para o Batismo', licao_atual = '✅ Concluído com Sucesso' WHERE id = {m}", (id,))
    return redirect('/?aba=doutrina')

@app.route('/config/opcoes/adicionar', methods=['POST'])
def opcoes_adicionar():
    cat = request.form.get('categoria', '').strip()
    val = request.form.get('valor', '').strip()
    if cat and val:
        m = "%s" if DATABASE_URL else "?"
        executar_comando(f"INSERT INTO opcoes_sistema (categoria, valor) VALUES ({m}, {m})", (cat, val))
    return redirect('/?aba=configuracoes')

@app.route('/config/opcoes/remover/<int:id>')
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
print("✓ app.py atualizado com sucesso!")

# =============================================================================
# 2. ATUALIZAR TEMPLATES/DASHBOARD.HTML COM CRIANÇAS/GÉNERO E SEPARAÇÃO DE TESOURARIA
# =============================================================================
tpl_path = os.path.join('templates', 'dashboard.html')

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
                <div class="px-3 py-2 text-[10px] font-bold uppercase tracking-wider text-slate-400">Visão Geral</div>
                
                <a href="/?aba=dashboard" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'dashboard' %}bg-indigo-600 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                    <span>📊</span><span>Painel Geral & Metas</span>
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

                <div class="px-3 pt-3 pb-1 text-[10px] font-bold uppercase tracking-wider text-emerald-400">Finanças & Tesouraria</div>

                <!-- 5. DASHBOARD FINANCEIRO EXECUTIVO -->
                <a href="/?aba=financas" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'financas' %}bg-emerald-700 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                    <span>📊</span><span>5. Dashboard Financeiro</span>
                </a>

                <!-- 6. MÓDULO EXCLUSIVO DA TESOUREIRA -->
                <a href="/?aba=tesouraria" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'tesouraria' %}bg-amber-600 text-white shadow-md{% else %}text-amber-300 hover:bg-slate-800{% endif %}">
                    <span>🔐</span><span>6. Caixa & Lançamentos</span>
                </a>

                <div class="px-3 pt-3 pb-1 text-[10px] font-bold uppercase tracking-wider text-amber-400">Ensino & Parâmetros</div>

                <a href="/?aba=doutrina" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'doutrina' %}bg-amber-700 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                    <span>📖</span><span>7. Doutrina & Batismo</span>
                </a>

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
        <!-- ABA: PAINEL GERAL & METAS                                 -->
        <!-- ========================================================= -->
        {% if aba_ativa == 'dashboard' %}
        <div class="bg-indigo-950 text-white p-6 rounded-2xl shadow mb-6">
            <h2 class="text-2xl font-black">📊 Painel Geral & Raio-X Eclesiástico</h2>
            <p class="text-xs text-indigo-300 mt-1">Visão estatística unificada da Assembleia de Deus - Sede Chicuque</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
            <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200">
                <div class="text-slate-500 text-xs font-bold uppercase">Membros Cadastrados</div>
                <div class="text-3xl font-black text-indigo-950 mt-1">{{ kpis.total_membros }}</div>
                <div class="text-xs text-emerald-600 font-semibold mt-1">👥 Efetivo em Comunhão</div>
            </div>
            <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200">
                <div class="text-slate-500 text-xs font-bold uppercase">Execução de Planos</div>
                <div class="text-3xl font-black text-blue-700 mt-1">{{ kpis.taxa_execucao }}%</div>
                <div class="text-xs text-slate-500 font-semibold mt-1">{{ kpis.planos_executados }} de {{ kpis.total_planos }} actividades</div>
            </div>
            <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200">
                <div class="text-slate-500 text-xs font-bold uppercase">Média / Culto</div>
                <div class="text-3xl font-black text-amber-600 mt-1">{{ kpis.media_assistencia }}</div>
                <div class="text-xs text-slate-500 font-semibold mt-1">Total de {{ kpis.total_cultos }} cultos</div>
            </div>
            <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200">
                <div class="text-slate-500 text-xs font-bold uppercase">Saldo Geral Caixa</div>
                <div class="text-3xl font-black {% if kpis.saldo_caixa >= 0 %}text-emerald-700{% else %}text-rose-700{% endif %} mt-1">
                    {{ "%.2f"|format(kpis.saldo_caixa) }} MT
                </div>
                <div class="text-xs text-slate-500 font-semibold mt-1">Entradas: {{ "%.2f"|format(kpis.total_entradas) }} MT</div>
            </div>
        </div>
        {% endif %}

        <!-- ========================================================= -->
        <!-- ABA 1: MEMBROS & RELATÓRIOS OFICIAIS                     -->
        <!-- ========================================================= -->
        {% if aba_ativa == 'membros' %}
        <div class="bg-indigo-900 text-white p-5 rounded-2xl shadow mb-6 flex justify-between items-center">
            <div>
                <h2 class="text-xl font-extrabold">👥 Cadastro Geral de Membresia</h2>
                <p class="text-xs text-indigo-200 mt-1">Registo oficial com geração automática de credenciais e certificados</p>
            </div>
            <a href="/membros/relatorio-geral" target="_blank" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl text-xs shadow flex items-center gap-2">
                📄 Gerar Livro Geral Completo (A4 / PDF)
            </a>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div class="lg:col-span-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">➕ Cadastrar Ficha Oficial</h3>
                <form action="/membros/novo" method="POST" class="space-y-3 text-xs">
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Nome Completo *</label>
                        <input type="text" name="nome" required placeholder="Nome completo do membro" class="w-full h-10 px-3 border rounded-xl bg-slate-50 font-bold">
                    </div>
                    <div class="grid grid-cols-2 gap-2">
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">BI / Cédula</label>
                            <input type="text" name="bi" placeholder="Nº de Documento" class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                        </div>
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Contacto / WhatsApp</label>
                            <input type="text" name="contacto" placeholder="+258..." class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                        </div>
                    </div>
                    <div class="grid grid-cols-3 gap-2">
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Estado Civil *</label>
                            <select name="estado_civil" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-bold text-indigo-900">
                                {% for op in opcoes.get('estado_civil', []) %}
                                <option value="{{ op.valor }}">{{ op.valor }}</option>
                                {% else %}
                                <option value="Criança">👶 Criança</option>
                                <option value="Solteiro(a)">Solteiro(a)</option>
                                <option value="Casado(a)">Casado(a)</option>
                                <option value="Viúvo(a)">Viúvo(a)</option>
                                {% endfor %}
                            </select>
                        </div>
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Zona</label>
                            <select name="zona" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-semibold">
                                {% for op in opcoes.get('zona', []) %}<option value="{{ op.valor }}">{{ op.valor }}</option>{% endfor %}
                            </select>
                        </div>
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Célula</label>
                            <select name="celula" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-semibold">
                                {% for op in opcoes.get('celula', []) %}<option value="{{ op.valor }}">{{ op.valor }}</option>{% endfor %}
                            </select>
                        </div>
                    </div>
                    <div class="grid grid-cols-2 gap-2">
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Cargo Ministerial</label>
                            <select name="cargo" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-semibold">
                                {% for op in opcoes.get('cargo', []) %}<option value="{{ op.valor }}">{{ op.valor }}</option>{% endfor %}
                            </select>
                        </div>
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Departamento</label>
                            <select name="departamento" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-semibold">
                                {% for op in opcoes.get('departamento', []) %}<option value="{{ op.valor }}">{{ op.valor }}</option>{% endfor %}
                            </select>
                        </div>
                    </div>
                    <div class="grid grid-cols-2 gap-2">
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Ano Conversão</label>
                            <input type="number" name="ano_conversao" placeholder="Ex: 2021" class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                        </div>
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Data Batismo</label>
                            <input type="date" name="data_batismo" class="w-full h-10 px-2 border rounded-xl bg-emerald-50 border-emerald-300">
                        </div>
                    </div>
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Residência (Bairro / Local)</label>
                        <input type="text" name="local_residencia" placeholder="Ex: Chicuque - Perto do Hospital" class="w-full h-10 px-3 border rounded-xl bg-slate-50">
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
                                <th class="py-2 px-2">Membro</th>
                                <th class="py-2 px-2">Zona & Célula</th>
                                <th class="py-2 px-2">Cargo & Depto</th>
                                <th class="py-2 px-2">Batismo</th>
                                <th class="py-2 px-2 text-right">Documentos</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for m in membros %}
                            <tr class="border-b border-slate-100 hover:bg-slate-50">
                                <td class="py-2.5 px-2">
                                    <div class="font-bold text-slate-900">{{ m.nome }}</div>
                                    <div class="text-[10px] text-slate-400">{{ m.estado_civil or '---' }} • {{ m.local_residencia or m.bairro or '---' }}</div>
                                </td>
                                <td class="py-2.5 px-2 text-slate-600">
                                    <div class="font-semibold">{{ m.zona or 'Zona Geral' }}</div>
                                    <div class="text-[10px] text-slate-400">{{ m.celula or '---' }}</div>
                                </td>
                                <td class="py-2.5 px-2">
                                    <span class="bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded font-bold text-[11px]">{{ m.cargo }}</span>
                                    <div class="text-[10px] text-slate-500 mt-0.5">{{ m.departamento }}</div>
                                </td>
                                <td class="py-2.5 px-2">
                                    {% if m.data_batismo %}
                                    <span class="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full font-bold text-[10px]">🌊 {{ m.data_batismo }}</span>
                                    {% else %}
                                    <span class="text-slate-400 text-[10px] italic">Não Batizado</span>
                                    {% endif %}
                                </td>
                                <td class="py-2.5 px-2 text-right space-x-1">
                                    <a href="/membros/{{ m.id }}/cartao" target="_blank" class="px-2 py-1 bg-indigo-600 hover:bg-indigo-700 text-white rounded font-bold text-[10px] shadow inline-block" title="Cartão de Membro">🪪 Cartão</a>
                                    {% if m.data_batismo %}
                                    <a href="/membros/{{ m.id }}/batismo" target="_blank" class="px-2 py-1 bg-emerald-600 hover:bg-emerald-700 text-white rounded font-bold text-[10px] shadow inline-block" title="Certificado de Batismo">🌊 Batismo</a>
                                    {% endif %}
                                    <a href="/membros/{{ m.id }}/recomendacao" target="_blank" class="px-2 py-1 bg-amber-600 hover:bg-amber-700 text-white rounded font-bold text-[10px] shadow inline-block" title="Carta de Recomendação">📜 Carta</a>
                                </td>
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
        <!-- ABA 2: SECRETARIA & PLANIFICAÇÃO                          -->
        <!-- ========================================================= -->
        {% if aba_ativa == 'secretaria' %}
        <div class="bg-indigo-900 text-white p-5 rounded-2xl shadow mb-6"><h2 class="text-xl font-extrabold">📋 Secretaria & Planificação de Actividades</h2></div>
        {% if plano_relatar %}
        <div class="bg-amber-50 border-2 border-amber-300 p-6 rounded-2xl shadow mb-6">
            <h3 class="font-extrabold text-base text-amber-900 mb-3">📝 Prestação de Contas: {{ plano_relatar.actividade }}</h3>
            <form action="/secretaria/planificacao/relatar" method="POST" class="space-y-3.5 text-xs">
                <input type="hidden" name="plano_id" value="{{ plano_relatar.id }}">
                <div><label class="block font-bold text-slate-700 mb-1">Feedback do que foi realizado *</label><textarea name="feedback" required rows="3" class="w-full p-3 border rounded-xl bg-white"></textarea></div>
                <div class="grid grid-cols-4 gap-3 bg-white p-3 rounded-xl border border-amber-200">
                    <div><label class="block text-slate-500">Homens</label><input type="number" name="participantes_homens" value="0" min="0" class="w-full h-9 px-2 border rounded font-bold"></div>
                    <div><label class="block text-slate-500">Mulheres</label><input type="number" name="participantes_mulheres" value="0" min="0" class="w-full h-9 px-2 border rounded font-bold"></div>
                    <div><label class="block text-slate-500">Jovens</label><input type="number" name="participantes_jovens" value="0" min="0" class="w-full h-9 px-2 border rounded font-bold"></div>
                    <div><label class="block text-slate-500">Crianças</label><input type="number" name="participantes_criancas" value="0" min="0" class="w-full h-9 px-2 border rounded font-bold"></div>
                </div>
                <div class="grid grid-cols-2 gap-3 pt-2">
                    <div><label class="block font-semibold text-slate-700 mb-1">Data Real</label><input type="date" name="data_execucao" required class="w-full h-10 px-2 border rounded-xl bg-white"></div>
                    <div class="flex items-end"><button type="submit" class="w-full h-10 bg-emerald-700 hover:bg-emerald-800 text-white font-bold rounded-xl shadow cursor-pointer">✅ Concluir Feedback</button></div>
                </div>
            </form>
        </div>
        {% endif %}
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div class="lg:col-span-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">📌 Planificar Actividade</h3>
                <form action="/secretaria/planificacao/nova" method="POST" class="space-y-3.5 text-xs">
                    <div><label class="block font-semibold mb-1">Departamento</label><select name="departamento" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-bold">{% for op in opcoes.get('departamento', []) %}<option value="{{ op.valor }}">{{ op.valor }}</option>{% endfor %}</select></div>
                    <div><label class="block font-semibold mb-1">Tipo de Evento</label><select name="tipo_evento" class="w-full h-10 px-2 border rounded-xl bg-slate-50">{% for op in opcoes.get('tipo_evento', []) %}<option value="{{ op.valor }}">{{ op.valor }}</option>{% endfor %}</select></div>
                    <div><label class="block font-semibold mb-1">Nome Actividade *</label><input type="text" name="actividade" required class="w-full h-10 px-3 border rounded-xl bg-slate-50"></div>
                    <div class="grid grid-cols-2 gap-2">
                        <div><label class="block font-semibold mb-1">Data Prevista</label><input type="date" name="data_prevista" required class="w-full h-10 px-2 border rounded-xl bg-slate-50"></div>
                        <div><label class="block font-semibold mb-1">Frequência</label><select name="frequencia" class="w-full h-10 px-2 border rounded-xl bg-slate-50"><option value="Pontual / Única">Pontual / Única</option><option value="Semanal">Semanal</option><option value="Mensal">Mensal</option></select></div>
                    </div>
                    <div><label class="block font-semibold mb-1">Responsável</label><input type="text" name="responsavel" class="w-full h-10 px-3 border rounded-xl bg-slate-50"></div>
                    <button type="submit" class="w-full py-3 bg-indigo-800 hover:bg-indigo-900 text-white font-bold rounded-xl shadow cursor-pointer">Gravar Planificação</button>
                </form>
            </div>
            <div class="lg:col-span-8 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">📊 Cronograma ({{ planificacoes|length }})</h3>
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse text-xs">
                        <thead><tr class="border-b-2 border-slate-200 text-slate-500"><th class="py-2.5 px-2">Actividade</th><th class="py-2.5 px-2">Data</th><th class="py-2.5 px-2">Status</th><th class="py-2.5 px-2 text-right">Ação</th></tr></thead>
                        <tbody>
                            {% for p in planificacoes %}
                            <tr class="border-b border-slate-100 hover:bg-slate-50">
                                <td class="py-3 px-2 font-bold text-indigo-900">{{ p.actividade }}<div class="text-[11px] text-slate-500">{{ p.departamento }}</div></td>
                                <td class="py-3 px-2">{{ p.data_prevista }}</td>
                                <td class="py-3 px-2">{% if p.status == 'Executado' %}<span class="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-bold">✅ Executado</span>{% else %}<span class="bg-blue-100 text-blue-800 px-2 py-0.5 rounded font-bold">Planeado</span>{% endif %}</td>
                                <td class="py-3 px-2 text-right">{% if p.status != 'Executado' %}<a href="/?aba=secretaria&relatar_id={{ p.id }}" class="px-2.5 py-1 bg-amber-600 text-white rounded font-bold">📝 Relatar</a>{% else %}<span class="text-emerald-700 font-bold">Concluído</span>{% endif %}</td>
                            </tr>
                            {% else %}
                            <tr><td colspan="4" class="py-8 text-center text-slate-400">Nenhuma actividade planificada.</td></tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- ========================================================= -->
        <!-- ABA 3: CULTOS COM CRIANÇAS POR GÉNERO                     -->
        <!-- ========================================================= -->
        {% if aba_ativa == 'cultos' %}
        <div class="bg-indigo-900 text-white p-5 rounded-2xl shadow mb-6">
            <h2 class="text-xl font-extrabold">⛪ Registo de Cultos & Estatística Completa de Presenças</h2>
            <p class="text-xs text-indigo-200 mt-1">Estatística oficial discriminada por género em todas as faixas etárias</p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div class="lg:col-span-5 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">📝 Lançar Culto</h3>
                <form action="/cultos/novo" method="POST" class="space-y-3 text-xs">
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block font-semibold mb-1">Data *</label>
                            <input type="date" name="data_culto" required class="w-full h-10 px-2 border rounded-xl bg-slate-50">
                        </div>
                        <div>
                            <label class="block font-semibold mb-1">Tipo de Culto</label>
                            <select name="tipo_culto" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-bold">
                                {% for op in opcoes.get('tipo_culto', []) %}<option value="{{ op.valor }}">{{ op.valor }}</option>{% endfor %}
                            </select>
                        </div>
                    </div>

                    <!-- GRADE DE CONTAGEM COMPLETA POR GÉNERO -->
                    <div class="p-3 bg-slate-50 rounded-xl border border-slate-200 space-y-2">
                        <div class="font-bold text-slate-700 text-[11px] uppercase tracking-wider">Assistência Discriminada por Género</div>
                        
                        <div class="grid grid-cols-2 gap-2">
                            <div><label class="text-slate-500 font-semibold">👨 Homens Adultos</label><input type="number" name="homens_adultos" value="0" min="0" oninput="somarCulto()" class="campo-soma w-full h-8 px-2 border rounded bg-white font-bold"></div>
                            <div><label class="text-slate-500 font-semibold">👩 Mulheres Adultas</label><input type="number" name="mulheres_adultas" value="0" min="0" oninput="somarCulto()" class="campo-soma w-full h-8 px-2 border rounded bg-white font-bold"></div>
                            <div><label class="text-slate-500 font-semibold">👦 Jovens (Rapazes)</label><input type="number" name="jovens_rapazes" value="0" min="0" oninput="somarCulto()" class="campo-soma w-full h-8 px-2 border rounded bg-white font-bold"></div>
                            <div><label class="text-slate-500 font-semibold">👧 Jovens (Moças)</label><input type="number" name="jovens_mocas" value="0" min="0" oninput="somarCulto()" class="campo-soma w-full h-8 px-2 border rounded bg-white font-bold"></div>
                            
                            <!-- CRIANÇAS DIVIDIDAS POR GÉNERO -->
                            <div class="bg-blue-50/60 p-1.5 rounded-lg border border-blue-200">
                                <label class="text-blue-900 font-bold text-[11px] block">👶 Crianças (Meninos)</label>
                                <input type="number" name="criancas_meninos" value="0" min="0" oninput="somarCulto()" class="campo-soma w-full h-8 px-2 border border-blue-300 rounded bg-white font-bold text-blue-900">
                            </div>
                            <div class="bg-pink-50/60 p-1.5 rounded-lg border border-pink-200">
                                <label class="text-pink-900 font-bold text-[11px] block">👧 Crianças (Meninas)</label>
                                <input type="number" name="criancas_meninas" value="0" min="0" oninput="somarCulto()" class="campo-soma w-full h-8 px-2 border border-pink-300 rounded bg-white font-bold text-pink-900">
                            </div>

                            <!-- VISITANTES DIVIDIDOS POR GÉNERO -->
                            <div><label class="text-slate-500">Visitantes (H)</label><input type="number" name="visitantes_homens" value="0" min="0" oninput="somarCulto()" class="campo-soma w-full h-8 px-2 border rounded bg-white"></div>
                            <div><label class="text-slate-500">Visitantes (M)</label><input type="number" name="visitantes_mulheres" value="0" min="0" oninput="somarCulto()" class="campo-soma w-full h-8 px-2 border rounded bg-white"></div>
                        </div>

                        <div class="grid grid-cols-2 gap-2 pt-2 border-t">
                            <div>
                                <label class="font-bold text-amber-700">🔥 Vidas no Altar (Apelos)</label>
                                <input type="number" name="apelos" value="0" min="0" class="w-full h-9 px-2 border-2 border-amber-300 rounded bg-amber-50 font-bold text-center">
                            </div>
                            <div>
                                <label class="font-bold text-blue-800">📊 Total de Presentes</label>
                                <input type="number" id="total_presentes" name="total_presentes" value="0" readonly class="w-full h-9 px-2 border-2 border-blue-400 rounded bg-blue-50 font-extrabold text-center text-blue-900 text-sm">
                            </div>
                        </div>
                    </div>

                    <div class="grid grid-cols-2 gap-3">
                        <div><label class="block font-semibold mb-1">Pregador</label><input type="text" name="pregador" placeholder="Nome do Pregador" class="w-full h-10 px-3 border rounded-xl bg-slate-50"></div>
                        <div><label class="block font-semibold mb-1">Tema / Texto</label><input type="text" name="tema_mensagem" placeholder="Ex: Isaías 40:31" class="w-full h-10 px-3 border rounded-xl bg-slate-50"></div>
                    </div>

                    <button type="submit" class="w-full py-3 bg-indigo-700 hover:bg-indigo-800 text-white font-bold rounded-xl shadow cursor-pointer">
                        Gravar Relatório de Culto
                    </button>
                </form>
            </div>

            <div class="lg:col-span-7 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">📚 Histórico de Cultos ({{ cultos|length }})</h3>
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs">
                        <thead>
                            <tr class="border-b-2 border-slate-200 text-slate-500">
                                <th class="py-2.5 px-2">Data</th>
                                <th class="py-2.5 px-2">Culto & Pregador</th>
                                <th class="py-2.5 px-2 text-center">Crianças (M/F)</th>
                                <th class="py-2.5 px-2 text-center">Total</th>
                                <th class="py-2.5 px-2 text-center">Apelos</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for c in cultos %}
                            <tr class="border-b border-slate-100 hover:bg-slate-50">
                                <td class="py-3 px-2 font-semibold">{{ c.data_culto }}</td>
                                <td class="py-3 px-2 font-bold text-slate-800">{{ c.tipo_culto }}<div class="text-[11px] text-slate-400">{{ c.pregador or '---' }}</div></td>
                                <td class="py-3 px-2 text-center font-bold text-slate-600">
                                    👦 {{ c.criancas_meninos or 0 }} | 👧 {{ c.criancas_meninas or 0 }}
                                </td>
                                <td class="py-3 px-2 text-center font-black text-blue-900 bg-blue-50/50 rounded-lg">{{ c.total_presentes }}</td>
                                <td class="py-3 px-2 text-center font-black text-amber-700">{{ c.apelos }}</td>
                            </tr>
                            {% else %}
                            <tr><td colspan="5" class="py-8 text-center text-slate-400">Nenhum culto registado.</td></tr>
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
                    <div><label class="block font-semibold mb-1">Nome Completo *</label><input type="text" name="nome" required class="w-full h-11 px-3 border rounded-xl bg-blue-50/50"></div>
                    <div><label class="block font-semibold mb-1">Contacto</label><input type="text" name="telefone" class="w-full h-11 px-3 border rounded-xl bg-blue-50/50"></div>
                    <div><label class="block font-semibold mb-1">Data Decisão</label><input type="date" name="data_decisao" required class="w-full h-11 px-3 border rounded-xl bg-white"></div>
                    <div><label class="block font-semibold mb-1">Bairro</label><input type="text" name="bairro" class="w-full h-11 px-3 border rounded-xl bg-blue-50/50"></div>
                    <button type="submit" class="w-full py-3.5 bg-emerald-700 hover:bg-emerald-800 text-white font-bold rounded-xl shadow cursor-pointer">Registar para Discipulado</button>
                </form>
            </div>
            <div class="lg:col-span-7 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">Acompanhamento Espiritual ({{ convertidos|length }})</h3>
                <table class="w-full text-left text-xs">
                    <thead><tr class="border-b-2 border-slate-200 text-slate-500"><th class="py-3 px-3">Nome</th><th class="py-3 px-3">Contacto</th><th class="py-3 px-3">Bairro</th><th class="py-3 px-3">Estado</th></tr></thead>
                    <tbody>
                        {% for c in convertidos %}
                        <tr class="border-b border-slate-100 hover:bg-slate-50"><td class="py-3 px-3 font-bold">{{ c.nome }}</td><td class="py-3 px-3">{{ c.telefone or '---' }}</td><td class="py-3 px-3">{{ c.bairro or '---' }}</td><td class="py-3 px-3"><span class="bg-emerald-100 text-emerald-800 px-2.5 py-1 rounded-full font-bold">{{ c.status_discipulado }}</span></td></tr>
                        {% else %}
                        <tr><td colspan="4" class="py-8 text-center text-slate-400">Nenhum convertido registado.</td></tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
        {% endif %}

        <!-- ========================================================= -->
        <!-- ABA 5: DASHBOARD FINANCEIRO (SOMENTE LEITURA PASTORAL)    -->
        <!-- ========================================================= -->
        {% if aba_ativa == 'financas' %}
        <div class="bg-emerald-950 text-white p-6 rounded-2xl shadow mb-6 flex justify-between items-center">
            <div>
                <h2 class="text-2xl font-black">📊 Dashboard Financeiro & Transparência</h2>
                <p class="text-xs text-emerald-300 mt-1">Visão analítica das finanças da IEAD Chicuque (Modo Consulta e Auditoria)</p>
            </div>
            <div class="text-right flex items-center gap-4">
                <div>
                    <span class="text-[10px] uppercase font-bold text-emerald-300 block">Saldo em Caixa</span>
                    <span class="text-2xl font-black text-white">{{ "%.2f"|format(kpis.saldo_caixa) }} MT</span>
                </div>
                <a href="/?aba=tesouraria" class="px-3.5 py-2 bg-amber-500 hover:bg-amber-600 text-slate-950 font-black rounded-xl text-xs shadow flex items-center gap-1.5">
                    <span>🔐</span><span>Ir para Lançamentos da Tesoureira</span>
                </a>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
            <div class="bg-white p-5 rounded-2xl shadow-sm border-l-4 border-emerald-500 border-slate-200">
                <div class="text-slate-500 text-xs font-bold uppercase">Entradas Totais</div>
                <div class="text-2xl font-black text-emerald-700 mt-1">+ {{ "%.2f"|format(kpis.total_entradas) }} MT</div>
                <div class="text-[11px] text-slate-400 mt-1">Dízimos e Ofertas</div>
            </div>
            <div class="bg-white p-5 rounded-2xl shadow-sm border-l-4 border-rose-500 border-slate-200">
                <div class="text-slate-500 text-xs font-bold uppercase">Saídas & Despesas</div>
                <div class="text-2xl font-black text-rose-700 mt-1">- {{ "%.2f"|format(kpis.total_saidas) }} MT</div>
                <div class="text-[11px] text-slate-400 mt-1">Taxa de consumo: {{ kpis.taxa_gasto }}%</div>
            </div>
            <div class="bg-white p-5 rounded-2xl shadow-sm border-l-4 border-indigo-500 border-slate-200">
                <div class="text-slate-500 text-xs font-bold uppercase">Total em Dízimos</div>
                <div class="text-2xl font-black text-indigo-900 mt-1">{{ "%.2f"|format(kpis.total_dizimos) }} MT</div>
                <div class="text-[11px] text-slate-400 mt-1">Fidelidade Ministerial</div>
            </div>
            <div class="bg-white p-5 rounded-2xl shadow-sm border-l-4 border-amber-500 border-slate-200">
                <div class="text-slate-500 text-xs font-bold uppercase">Missões & Obras</div>
                <div class="text-2xl font-black text-amber-700 mt-1">{{ "%.2f"|format(kpis.total_missoes) }} MT</div>
                <div class="text-[11px] text-slate-400 mt-1">Campanhas e Construção</div>
            </div>
        </div>

        <!-- GRÁFICO DE DISTRIBUIÇÃO DAS RECEITAS -->
        <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 mb-8">
            <h3 class="font-bold text-sm text-slate-800 uppercase tracking-wider mb-4">📊 Distribuição por Categoria Financeira</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                {% for cat, val in kpis.categorias_caixa.items() %}
                <div class="p-3 bg-slate-50 rounded-xl border border-slate-200">
                    <div class="flex justify-between items-center mb-1.5 font-bold">
                        <span class="text-slate-700">{{ cat }}</span>
                        <span class="text-indigo-950 font-extrabold">{{ "%.2f"|format(val) }} MT</span>
                    </div>
                    <div class="w-full bg-slate-200 h-2 rounded-full overflow-hidden">
                        {% set perc = (val / kpis.total_entradas * 100)|int if kpis.total_entradas > 0 else 10 %}
                        <div class="bg-emerald-600 h-2 rounded-full" style="width: {{ [perc, 100]|min }}%"></div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>

        <!-- LIVRO RAZÃO COMPLETO (AUDITORIA PASTORAL) -->
        <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
            <h3 class="font-bold text-base mb-4 border-b pb-2">📋 Livro Razão de Movimentos ({{ caixa|length }} registos)</h3>
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
                            <td class="py-3 px-2">
                                <span class="{% if cx.tipo == 'Entrada' %}bg-emerald-100 text-emerald-800{% else %}bg-rose-100 text-rose-800{% endif %} px-2.5 py-1 rounded-full font-bold text-[11px]">{{ cx.tipo }}</span>
                            </td>
                            <td class="py-3 px-2 font-bold">{{ cx.categoria }}<div class="text-[11px] text-slate-400 font-normal">{{ cx.descricao }}</div></td>
                            <td class="py-3 px-2 text-right font-extrabold {% if cx.tipo == 'Entrada' %}text-emerald-700{% else %}text-rose-700{% endif %}">
                                {{ "%.2f"|format(cx.valor or 0) }} MT
                            </td>
                        </tr>
                        {% else %}
                        <tr><td colspan="4" class="py-8 text-center text-slate-400">Nenhum movimento gravado.</td></tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
        {% endif %}

        <!-- ========================================================= -->
        <!-- ABA 6: CAIXA & TESOURARIA (ÁREA EXCLUSIVA DA TESOUREIRA)  -->
        <!-- ========================================================= -->
        {% if aba_ativa == 'tesouraria' %}
        <div class="bg-amber-950 text-white p-6 rounded-2xl shadow mb-6 flex justify-between items-center">
            <div>
                <div class="inline-flex items-center gap-2 bg-amber-500/20 text-amber-300 px-3 py-1 rounded-full text-[10px] font-black uppercase mb-1 border border-amber-400/30">
                    <span>🔐</span> ACESSO RESTRITO • GABINETE DA TESOURARIA
                </div>
                <h2 class="text-2xl font-black">Lançamentos de Caixa & Movimentação Financeira</h2>
                <p class="text-xs text-amber-200 mt-1">Módulo reservado para o lançamento e controlo diário da Tesoureira da Igreja</p>
            </div>
            <a href="/?aba=financas" class="px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-white font-bold rounded-xl text-xs shadow">
                📊 Ver Relatório & Dashboard
            </a>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <!-- FORMULÁRIO DE LANÇAMENTO EXCLUSIVO -->
            <div class="lg:col-span-5 bg-white p-6 rounded-2xl shadow-sm border-2 border-amber-300">
                <h3 class="font-extrabold text-base mb-4 border-b pb-2 text-amber-950 flex items-center gap-2">
                    <span>✍️</span> Lançar Entrada ou Saída de Caixa
                </h3>
                <form action="/financas/caixa/novo" method="POST" class="space-y-4 text-xs">
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">Tipo de Movimento *</label>
                            <select name="tipo" class="w-full h-11 px-2 border-2 border-slate-200 rounded-xl bg-slate-50 font-black text-sm">
                                <option value="Entrada">🟢 Entrada (+)</option>
                                <option value="Saída">🔴 Saída (-)</option>
                            </select>
                        </div>
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">Data da Operação *</label>
                            <input type="date" name="data_movimento" required class="w-full h-11 px-2 border-2 border-slate-200 rounded-xl bg-slate-50 font-bold">
                        </div>
                    </div>

                    <div>
                        <label class="block font-bold text-slate-700 mb-1">Categoria Contábil *</label>
                        <select name="categoria" class="w-full h-11 px-2 border-2 border-slate-200 rounded-xl bg-slate-50 font-bold text-slate-800">
                            {% for op in opcoes.get('categoria_caixa', []) %}
                            <option value="{{ op.valor }}">{{ op.valor }}</option>
                            {% endfor %}
                        </select>
                    </div>

                    <div>
                        <label class="block font-bold text-slate-700 mb-1">Valor do Movimento (MZN) *</label>
                        <input type="number" step="0.01" name="valor" required placeholder="Ex: 5000.00" class="w-full h-12 px-3 border-2 border-emerald-400 rounded-xl bg-emerald-50/50 font-black text-emerald-950 text-lg">
                    </div>

                    <div>
                        <label class="block font-bold text-slate-700 mb-1">Descrição / Justificativo</label>
                        <textarea name="descricao" rows="2" placeholder="Ex: Dízimo do culto de domingo / Compra de material..." class="w-full p-2.5 border-2 border-slate-200 rounded-xl bg-slate-50"></textarea>
                    </div>

                    <button type="submit" class="w-full py-3.5 bg-emerald-700 hover:bg-emerald-800 text-white font-extrabold rounded-xl shadow cursor-pointer text-sm transition">
                        💾 Confirmar e Lançar no Caixa
                    </button>
                </form>
            </div>

            <!-- REGISTO DOS ÚLTIMOS LANÇAMENTOS FEITOS -->
            <div class="lg:col-span-7 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2 text-slate-800 flex justify-between items-center">
                    <span>📋 Últimos Lançamentos Efetuados</span>
                    <span class="text-xs bg-slate-100 text-slate-600 px-2.5 py-1 rounded-full font-bold">Total: {{ caixa|length }}</span>
                </h3>
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs">
                        <thead>
                            <tr class="border-b-2 border-slate-200 text-slate-500">
                                <th class="py-2.5 px-2">Data</th>
                                <th class="py-2.5 px-2">Tipo</th>
                                <th class="py-2.5 px-2">Categoria</th>
                                <th class="py-2.5 px-2 text-right">Valor</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for cx in caixa[:15] %}
                            <tr class="border-b border-slate-100 hover:bg-slate-50">
                                <td class="py-2.5 px-2 text-slate-600 font-semibold">{{ cx.data_movimento }}</td>
                                <td class="py-2.5 px-2">
                                    <span class="{% if cx.tipo == 'Entrada' %}bg-emerald-100 text-emerald-800{% else %}bg-rose-100 text-rose-800{% endif %} px-2 py-0.5 rounded font-bold text-[10px]">{{ cx.tipo }}</span>
                                </td>
                                <td class="py-2.5 px-2 font-bold text-slate-800">{{ cx.categoria }}</td>
                                <td class="py-2.5 px-2 text-right font-black {% if cx.tipo == 'Entrada' %}text-emerald-700{% else %}text-rose-700{% endif %}">
                                    {{ "%.2f"|format(cx.valor or 0) }} MT
                                </td>
                            </tr>
                            {% else %}
                            <tr><td colspan="4" class="py-8 text-center text-slate-400">Nenhum lançamento efetuado ainda.</td></tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- ========================================================= -->
        <!-- ABA 7: DOUTRINA & BATISMO                                 -->
        <!-- ========================================================= -->
        {% if aba_ativa == 'doutrina' %}
        <div class="bg-amber-950 text-white p-6 rounded-2xl shadow mb-6 flex justify-between items-center">
            <div>
                <h2 class="text-2xl font-black">📖 Dashboard de Doutrina & Preparação Batismal</h2>
                <p class="text-xs text-amber-300 mt-1">Acompanhamento e aprovação de formandos para o Batismo nas Águas</p>
            </div>
            <div class="text-right">
                <span class="text-xs uppercase font-bold text-amber-300">Aptos para Batismo</span>
                <div class="text-2xl font-black text-emerald-400">✅ {{ kpis.total_aptos_batismo }} Candidatos</div>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
            <div class="bg-white p-5 rounded-2xl shadow-sm border-l-4 border-amber-600 border-slate-200">
                <div class="text-slate-500 text-xs font-bold uppercase">Total Formandos</div>
                <div class="text-2xl font-black text-slate-900 mt-1">{{ kpis.total_doutrina }} Alunos</div>
            </div>
            <div class="bg-white p-5 rounded-2xl shadow-sm border-l-4 border-emerald-500 border-slate-200">
                <div class="text-slate-500 text-xs font-bold uppercase">Prontos p/ Batismo</div>
                <div class="text-2xl font-black text-emerald-700 mt-1">{{ kpis.total_aptos_batismo }} Vidas</div>
            </div>
            <div class="bg-white p-5 rounded-2xl shadow-sm border-l-4 border-blue-500 border-slate-200">
                <div class="text-slate-500 text-xs font-bold uppercase">Em Formação</div>
                <div class="text-2xl font-black text-blue-700 mt-1">{{ kpis.total_em_formacao }} Alunos</div>
            </div>
            <div class="bg-white p-5 rounded-2xl shadow-sm border-l-4 border-purple-500 border-slate-200">
                <div class="text-slate-500 text-xs font-bold uppercase">Classes Ativas</div>
                <div class="text-2xl font-black text-purple-700 mt-1">{{ kpis.classes_contagem|length }} Classes</div>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div class="lg:col-span-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">🎓 Inscrever Formando</h3>
                <form action="/doutrina/novo" method="POST" class="space-y-3.5 text-xs">
                    <div>
                        <label class="block font-semibold mb-1">Nome Completo *</label>
                        <input type="text" name="nome_aluno" required placeholder="Nome do formando" class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                    </div>
                    <div>
                        <label class="block font-semibold mb-1">Classe *</label>
                        <select name="classe" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-bold">
                            {% for op in opcoes.get('classe_doutrina', []) %}<option value="{{ op.valor }}">{{ op.valor }}</option>{% endfor %}
                        </select>
                    </div>
                    <div>
                        <label class="block font-semibold mb-1">Lição Atual</label>
                        <input type="text" name="licao_atual" value="Lição 1 - A Salvação e Fé" class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                    </div>
                    <div class="grid grid-cols-2 gap-3">
                        <div><label class="block font-semibold mb-1">Instrutor</label><input type="text" name="professor" placeholder="Pr. / Diác." class="w-full h-10 px-3 border rounded-xl bg-slate-50"></div>
                        <div><label class="block font-semibold mb-1">Data Início</label><input type="date" name="data_inicio" required class="w-full h-10 px-2 border rounded-xl bg-slate-50"></div>
                    </div>
                    <button type="submit" class="w-full py-3 bg-amber-700 hover:bg-amber-800 text-white font-bold rounded-xl shadow cursor-pointer">Gravar Inscrição</button>
                </form>
            </div>

            <div class="lg:col-span-8 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">📋 Lista de Formandos & Aprovação</h3>
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs">
                        <thead><tr class="border-b-2 border-slate-200 text-slate-500"><th class="py-2.5 px-2">Candidato</th><th class="py-2.5 px-2">Classe</th><th class="py-2.5 px-2">Progresso</th><th class="py-2.5 px-2">Situação</th><th class="py-2.5 px-2 text-right">Ação</th></tr></thead>
                        <tbody>
                            {% for d in doutrina %}
                            <tr class="border-b border-slate-100 hover:bg-slate-50">
                                <td class="py-3 px-2 font-bold">{{ d.nome_aluno }}</td>
                                <td class="py-3 px-2">{{ d.classe }}</td>
                                <td class="py-3 px-2 font-semibold text-amber-900">{{ d.licao_atual }}</td>
                                <td class="py-3 px-2">{% if 'apto' in d.situacao|lower %}<span class="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-bold">✅ Apto Batismo</span>{% else %}<span class="bg-amber-100 text-amber-800 px-2 py-0.5 rounded font-bold">Em Formação</span>{% endif %}</td>
                                <td class="py-3 px-2 text-right">{% if 'apto' not in d.situacao|lower %}<a href="/doutrina/aprovar/{{ d.id }}" class="px-3 py-1 bg-emerald-600 text-white rounded font-bold">🌊 Aprovar</a>{% else %}<span class="text-emerald-700 font-bold">Homologado</span>{% endif %}</td>
                            </tr>
                            {% else %}
                            <tr><td colspan="5" class="py-8 text-center text-slate-400">Nenhum formando inscrito.</td></tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- ========================================================= -->
        <!-- ABA 8: GESTOR DE SELETORES                                -->
        <!-- ========================================================= -->
        {% if aba_ativa == 'configuracoes' %}
        <div class="bg-purple-950 text-white p-5 rounded-2xl shadow mb-6"><h2 class="text-xl font-extrabold">⚙️ Gestor de Seletores</h2></div>
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div class="lg:col-span-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">➕ Adicionar Opção</h3>
                <form action="/config/opcoes/adicionar" method="POST" class="space-y-4 text-xs">
                    <div>
                        <label class="block font-semibold mb-1">Qual lista deseja atualizar? *</label>
                        <select name="categoria" required class="w-full h-11 px-3 border rounded-xl bg-slate-50 font-bold">
                            <option value="departamento">📁 Departamentos</option>
                            <option value="cargo">✝️ Cargos Ministeriais</option>
                            <option value="zona">📍 Zonas da Igreja</option>
                            <option value="celula">🏠 Células Familiares</option>
                            <option value="estado_civil">💍 Estado Civil</option>
                            <option value="tipo_evento">🎪 Tipos de Eventos</option>
                            <option value="tipo_culto">⛪ Tipos de Cultos</option>
                            <option value="categoria_caixa">💰 Categorias Caixa</option>
                            <option value="classe_doutrina">📖 Classes Doutrina</option>
                        </select>
                    </div>
                    <div><label class="block font-semibold mb-1">Nome da Opção *</label><input type="text" name="valor" required class="w-full h-11 px-3 border rounded-xl bg-slate-50"></div>
                    <button type="submit" class="w-full py-3.5 bg-purple-700 hover:bg-purple-800 text-white font-bold rounded-xl shadow cursor-pointer">Gravar Opção</button>
                </form>
            </div>
            <div class="lg:col-span-8 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">📋 Seletores Activos</h3>
                <div class="space-y-4 text-xs">
                    {% for cat, itens in opcoes.items() %}
                    <div class="border rounded-xl p-3 bg-slate-50">
                        <div class="font-black text-slate-700 uppercase mb-2">{{ cat.replace('_', ' ').title() }}</div>
                        <div class="flex flex-wrap gap-2">
                            {% for op in itens %}
                            <span class="inline-flex items-center gap-1.5 bg-white border px-2.5 py-1 rounded-lg text-slate-800 font-semibold shadow-sm">
                                {{ op.valor }}
                                <a href="/config/opcoes/remover/{{ op.id }}" onclick="return confirm('Remover opção?')" class="text-rose-500 hover:text-rose-700 font-bold ml-1 text-sm leading-none">×</a>
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

    <!-- SCRIPT DE SOMA AUTOMÁTICA DE CULTOS (INCLUINDO MENINOS E MENINAS) -->
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

with open(tpl_path, 'w', encoding='utf-8') as f:
    f.write(dashboard_html)

print("✓ templates/dashboard.html atualizado!")
print("=" * 80)
print("INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
print("=" * 80)