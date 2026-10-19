import os

print("=" * 80)
print("A ATUALIZAR CADASTRO E GERADORES DE CARTÕES E DOCUMENTOS...")
print("=" * 80)

# =============================================================================
# 1. ATUALIZAR APP.PY COM NOVOS CAMPOS E ROTAS DE DOCUMENTOS
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
# ESTRUTURA DO BANCO E MIGRAÇÕES
# -----------------------------------------------------------------------------
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

    # Migrações seguras das colunas novas
    novas_cols_membros = [
        ('zona', 'TEXT'), ('celula', 'TEXT'), ('ano_conversao', 'TEXT'),
        ('local_residencia', 'TEXT'), ('data_batismo', 'TEXT'), ('estado_civil', 'TEXT')
    ]
    for col, tipo in novas_cols_membros:
        if is_pg:
            try: executar_comando(f"ALTER TABLE membros ADD COLUMN IF NOT EXISTS {col} {tipo};")
            except: pass
        else:
            try: executar_comando(f"ALTER TABLE membros ADD COLUMN {col} {tipo};")
            except: pass

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
            ('estado_civil', 'Divorciado(a)'),
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

# -------------------------------------------------------------
# CONTEXT PROCESSOR: DADOS GERAIS E KPIS
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

# -------------------------------------------------------------
# ROTAS PRINCIPAIS
# -------------------------------------------------------------
@app.route('/')
def index():
    aba = request.args.get('aba', 'dashboard')
    id_relatar = request.args.get('relatar_id')
    plano_para_relatar = None
    if id_relatar:
        m = "%s" if DATABASE_URL else "?"
        plano_para_relatar = consultar_um(f"SELECT * FROM planificacao WHERE id = {m}", (id_relatar,))
    return render_template('dashboard.html', aba_ativa=aba, plano_relatar=plano_para_relatar)

# 1. Membros: Cadastro Completo
@app.route('/membros/novo', methods=['POST'])
def membros_gravar():
    fd = request.form
    m = "%s" if DATABASE_URL else "?"
    sql = f"""INSERT INTO membros 
              (nome, contacto, bi, cargo, departamento, estado_civil, zona, celula, ano_conversao, data_batismo, local_residencia, bairro, criado_em)
              VALUES ({m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m})"""
    
    local = (fd.get('local_residencia') or fd.get('bairro') or '').strip()
    params = (
        fd.get('nome', '').strip(),
        fd.get('contacto', '').strip(),
        fd.get('bi', '').strip(),
        fd.get('cargo', 'Membro em Comunhão').strip(),
        fd.get('departamento', 'Geral').strip(),
        fd.get('estado_civil', 'Solteiro(a)').strip(),
        fd.get('zona', 'Zona 1 - Central').strip(),
        fd.get('celula', 'Geral').strip(),
        fd.get('ano_conversao', '').strip(),
        fd.get('data_batismo', '').strip(),
        local,
        local,
        datetime.now().strftime('%Y-%m-%d %H:%M')
    )
    executar_comando(sql, params)
    return redirect('/?aba=membros')

# -------------------------------------------------------------
# ROTAS DE DOCUMENTOS OFICIAIS (COM LOGO E IMPRESSÃO EM ALTA RESOLUÇÃO)
# -------------------------------------------------------------

# A) Relatório Geral Completo da Membresia
@app.route('/membros/relatorio-geral')
def membros_relatorio_geral():
    membros = consultar_todos("SELECT * FROM membros ORDER BY nome ASC")
    return render_template('relatorio_membros.html', membros=membros, agora=datetime.now().strftime('%d/%m/%Y às %H:%M'))

# B) Cartão de Membro Oficial
@app.route('/membros/<int:id>/cartao')
def membros_cartao(id):
    m = "%s" if DATABASE_URL else "?"
    membro = consultar_um(f"SELECT * FROM membros WHERE id = {m}", (id,))
    if not membro:
        return redirect('/?aba=membros')
    return render_template('cartao_membro.html', m=membro, agora=datetime.now().strftime('%Y'))

# C) Cartão / Certificado de Batismo nas Águas
@app.route('/membros/<int:id>/batismo')
def membros_batismo(id):
    m = "%s" if DATABASE_URL else "?"
    membro = consultar_um(f"SELECT * FROM membros WHERE id = {m}", (id,))
    if not membro or not membro.get('data_batismo'):
        return "<script>alert('Este membro ainda não possui data de batismo registada!'); window.location.href='/?aba=membros';</script>"
    return render_template('cartao_batismo.html', m=membro, data_extenso=datetime.now().strftime('%d de %B de %Y'))

# D) Carta de Recomendação Pastoral
@app.route('/membros/<int:id>/recomendacao')
def membros_recomendacao(id):
    m = "%s" if DATABASE_URL else "?"
    membro = consultar_um(f"SELECT * FROM membros WHERE id = {m}", (id,))
    if not membro:
        return redirect('/?aba=membros')
    return render_template('carta_recomendacao.html', m=membro, data_extenso=datetime.now().strftime('%d de %B de %Y'))

# -------------------------------------------------------------
# DEMAIS ROTAS OPERACIONAIS
# -------------------------------------------------------------
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
print("✓ app.py: Rotas de cartões, batismo e recomendação criadas!")

# =============================================================================
# 2. CRIAR MODELO DO CARTÃO DE MEMBRO (FORMATO CREDENCIAL / CRACHÁ OFICIAL)
# =============================================================================
cartao_membro_html = '''<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <title>Cartão de Membro - {{ m.nome }}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @media print {
            .no-print { display: none !important; }
            body { background: white !important; padding: 0 !important; }
        }
    </style>
</head>
<body class="bg-slate-100 min-h-screen flex flex-col items-center justify-center p-6 font-sans">
    
    <div class="no-print mb-6 flex gap-4">
        <a href="/?aba=membros" class="px-4 py-2 bg-slate-800 text-white rounded-xl text-xs font-bold shadow">← Voltar</a>
        <button onclick="window.print()" class="px-5 py-2 bg-indigo-700 hover:bg-indigo-800 text-white rounded-xl text-xs font-bold shadow cursor-pointer">
            🖨️ Imprimir Cartão de Membro
        </button>
    </div>

    <!-- CARTÃO FRENTE E VERSO (TAMANHO PADRÃO CR80 / CARTEIRA) -->
    <div class="flex flex-col md:flex-row gap-6">
        
        <!-- FRENTE DO CARTÃO -->
        <div class="w-[360px] h-[225px] bg-gradient-to-br from-indigo-950 via-slate-900 to-indigo-900 text-white rounded-2xl shadow-2xl p-4 flex flex-col justify-between relative overflow-hidden border border-indigo-400/30">
            <!-- Padrão visual de fundo -->
            <div class="absolute -right-8 -bottom-8 w-32 h-32 bg-indigo-500/10 rounded-full blur-xl pointer-events-none"></div>
            
            <!-- TOPO: LOGO & CABEÇALHO -->
            <div class="flex items-center gap-3 border-b border-indigo-800/60 pb-2">
                <div class="w-10 h-10 rounded-full bg-white text-indigo-950 flex items-center justify-center font-black text-sm shrink-0 shadow">
                    AD
                </div>
                <div>
                    <h1 class="font-extrabold text-[11px] uppercase tracking-wider leading-tight text-white">ASSEMBLEIA DE DEUS</h1>
                    <p class="text-[9px] text-amber-400 font-bold uppercase tracking-widest leading-none">MINISTÉRIO THAVANE • SEDE CHICUQUE</p>
                    <p class="text-[8px] text-indigo-300">Cartão de Identificação Eclesiástica</p>
                </div>
            </div>

            <!-- CORPO DO CARTÃO -->
            <div class="flex gap-3 my-auto items-center">
                <div class="w-16 h-20 rounded-xl bg-indigo-900/80 border-2 border-indigo-400/50 flex flex-col items-center justify-center text-indigo-300 text-[10px] shrink-0 font-semibold shadow-inner">
                    <span>FOTO</span>
                    <span class="text-[8px] text-indigo-400">3x4</span>
                </div>
                <div class="space-y-1 text-left flex-1 min-w-0">
                    <div>
                        <div class="text-[8px] uppercase tracking-wider text-indigo-300 font-bold">Nome do Membro</div>
                        <div class="text-xs font-extrabold text-white truncate leading-tight">{{ m.nome }}</div>
                    </div>
                    <div class="grid grid-cols-2 gap-1 text-[9px]">
                        <div>
                            <span class="text-indigo-300 text-[7px] uppercase font-bold block">Cargo:</span>
                            <span class="font-bold text-amber-300">{{ m.cargo }}</span>
                        </div>
                        <div>
                            <span class="text-indigo-300 text-[7px] uppercase font-bold block">Estado Civil:</span>
                            <span class="text-white">{{ m.estado_civil or '---' }}</span>
                        </div>
                    </div>
                    <div class="grid grid-cols-2 gap-1 text-[9px]">
                        <div>
                            <span class="text-indigo-300 text-[7px] uppercase font-bold block">Depto:</span>
                            <span class="text-slate-200 truncate block">{{ m.departamento }}</span>
                        </div>
                        <div>
                            <span class="text-indigo-300 text-[7px] uppercase font-bold block">Célula:</span>
                            <span class="text-slate-200 truncate block">{{ m.celula or 'Geral' }}</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- RODAPÉ -->
            <div class="flex justify-between items-center text-[8px] border-t border-indigo-800/60 pt-1 text-indigo-300">
                <span>Zona: <b class="text-white">{{ m.zona or 'Central' }}</b></span>
                <span>BI: <b class="text-white">{{ m.bi or '---' }}</b></span>
                <span class="text-amber-400 font-bold">EMISSÃO {{ agora }}</span>
            </div>
        </div>

        <!-- VERSO DO CARTÃO -->
        <div class="w-[360px] h-[225px] bg-slate-900 text-white rounded-2xl shadow-2xl p-4 flex flex-col justify-between border border-slate-700 text-[9px]">
            <div class="text-center border-b border-slate-800 pb-1.5">
                <p class="font-extrabold text-[10px] text-indigo-300 uppercase">Credencial de Membro em Comunhão</p>
                <p class="text-[8px] text-slate-400">Assembleia de Deus - Sede Regional de Chicuque - Maxixe</p>
            </div>

            <div class="space-y-1.5 text-slate-300">
                <div class="flex justify-between border-b border-slate-800 pb-0.5">
                    <span class="text-slate-400">Ano de Conversão:</span>
                    <span class="font-bold text-white">{{ m.ano_conversao or '---' }}</span>
                </div>
                <div class="flex justify-between border-b border-slate-800 pb-0.5">
                    <span class="text-slate-400">Data de Batismo:</span>
                    <span class="font-bold text-emerald-400">{{ m.data_batismo or 'Não Batizado' }}</span>
                </div>
                <div class="flex justify-between border-b border-slate-800 pb-0.5">
                    <span class="text-slate-400">Residência:</span>
                    <span class="text-white truncate max-w-[200px]">{{ m.local_residencia or m.bairro or 'Chicuque' }}</span>
                </div>
                <div class="flex justify-between border-b border-slate-800 pb-0.5">
                    <span class="text-slate-400">Contacto:</span>
                    <span class="text-white">{{ m.contacto or '---' }}</span>
                </div>
            </div>

            <!-- ASSINATURA DO PASTOR -->
            <div class="pt-2 text-center">
                <div class="w-36 mx-auto border-b border-slate-500 mb-0.5"></div>
                <p class="text-[8px] font-bold text-white">Pastor Presidente / Sede Chicuque</p>
                <p class="text-[7px] text-slate-500 italic">"Um só Senhor, uma só fé, um só batismo" - Efésios 4:5</p>
            </div>
        </div>

    </div>
</body>
</html>
'''

with open(os.path.join('templates', 'cartao_membro.html'), 'w', encoding='utf-8') as f:
    f.write(cartao_membro_html)
print("✓ templates/cartao_membro.html criado com sucesso!")

# =============================================================================
# 3. CRIAR MODELO DO CERTIFICADO / CARTÃO DE BATISMO NAS ÁGUAS
# =============================================================================
cartao_batismo_html = '''<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <title>Certificado de Batismo - {{ m.nome }}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @media print {
            .no-print { display: none !important; }
            body { background: white !important; padding: 0 !important; }
            @page { size: A4 landscape; margin: 10mm; }
        }
    </style>
</head>
<body class="bg-slate-100 p-8 font-serif text-slate-900 min-h-screen flex flex-col items-center justify-center">

    <div class="no-print mb-6 flex gap-4 font-sans">
        <a href="/?aba=membros" class="px-4 py-2 bg-slate-800 text-white rounded-xl text-xs font-bold shadow">← Voltar</a>
        <button onclick="window.print()" class="px-5 py-2 bg-emerald-700 hover:bg-emerald-800 text-white rounded-xl text-xs font-bold shadow cursor-pointer">
            🖨️ Imprimir Certificado de Batismo / PDF
        </button>
    </div>

    <!-- CERTIFICADO OFICIAL FORMATO A4 LANDSCAPE -->
    <div class="w-full max-w-4xl bg-white p-12 rounded-3xl shadow-2xl border-8 border-double border-amber-600/60 relative overflow-hidden print:shadow-none print:border-amber-700">
        
        <!-- Fundo marca d'água -->
        <div class="absolute inset-0 flex items-center justify-center opacity-5 pointer-events-none">
            <span class="text-[180px] font-black">AD</span>
        </div>

        <!-- CABEÇALHO OFICIAL -->
        <div class="text-center border-b-2 border-amber-600/40 pb-6 mb-8">
            <div class="w-16 h-16 mx-auto rounded-full bg-indigo-950 text-white flex items-center justify-center font-sans font-black text-2xl shadow mb-2">
                AD
            </div>
            <h1 class="text-2xl font-black uppercase tracking-widest text-slate-950">ASSEMBLEIA DE DEUS EM MOÇAMBIQUE</h1>
            <h2 class="text-sm font-bold uppercase tracking-wider text-amber-800 mt-0.5">MINISTÉRIO THAVANE • SEDE REGIONAL DE CHICUQUE - MAXIXE</h2>
            <p class="text-xs italic text-slate-500 font-sans mt-1">Registo Oficial de Batismos nas Águas</p>
        </div>

        <!-- TÍTULO DO CERTIFICADO -->
        <div class="text-center my-6">
            <h3 class="text-3xl font-extrabold uppercase tracking-widest text-indigo-950 underline decoration-amber-500 underline-offset-8">
                CERTIFICADO DE BATISMO NAS ÁGUAS
            </h3>
        </div>

        <!-- TEXTO LITÚRGICO -->
        <div class="text-center max-w-2xl mx-auto space-y-4 my-8 text-base leading-relaxed text-slate-800">
            <p>
                Certificamos para os devidos efeitos eclesiásticos que o(a) irmão(ã)
            </p>
            <p class="text-2xl font-extrabold text-indigo-950 uppercase border-b-2 border-slate-300 pb-1 mx-8 font-sans">
                {{ m.nome }}
            </p>
            <p>
                Tendo professado a sua fé salvífica no Senhor e Salvador Jesus Cristo, desceu às águas batismais por imersão, em cumprimento do mandamento bíblico, em nome do <b>Pai, do Filho e do Espírito Santo</b>, no dia:
            </p>
            <p class="text-xl font-bold text-amber-900 font-sans">
                {{ m.data_batismo }}
            </p>
            <p class="text-xs italic text-slate-600 pt-2">
                "Fomos, pois, sepultados com ele na morte pelo batismo; para que, como Cristo ressuscitou dentre os mortos pela glória do Pai, assim andemos nós também em novidade de vida." — <b>Romanos 6:4</b>
            </p>
        </div>

        <!-- DADOS COMPLEMENTARES E ASSINATURAS -->
        <div class="grid grid-cols-2 gap-12 mt-12 pt-8 border-t border-slate-200 text-center font-sans text-xs">
            <div>
                <div class="w-56 mx-auto border-b border-slate-600 mb-1.5"></div>
                <p class="font-extrabold text-slate-900">Pastor Celebrante</p>
                <p class="text-[10px] text-slate-500">IEAD Sede Chicuque</p>
            </div>
            <div>
                <div class="w-56 mx-auto border-b border-slate-600 mb-1.5"></div>
                <p class="font-extrabold text-slate-900">Secretaria da Igreja</p>
                <p class="text-[10px] text-slate-500">Ministério Thavane</p>
            </div>
        </div>

        <div class="text-center font-sans text-[10px] text-slate-400 mt-6">
            Documento Eclesiástico Registado sob o BI nº {{ m.bi or 'S/N' }} • Chicuque, {{ data_extenso }}
        </div>
    </div>
</body>
</html>
'''

with open(os.path.join('templates', 'cartao_batismo.html'), 'w', encoding='utf-8') as f:
    f.write(cartao_batismo_html)
print("✓ templates/cartao_batismo.html criado com sucesso!")

# =============================================================================
# 4. CRIAR MODELO DA CARTA DE RECOMENDAÇÃO PASTORAL OFICIAL
# =============================================================================
carta_recomendacao_html = '''<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <title>Carta de Recomendação - {{ m.nome }}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @media print {
            .no-print { display: none !important; }
            body { background: white !important; padding: 0 !important; }
            @page { size: A4 portrait; margin: 15mm; }
        }
    </style>
</head>
<body class="bg-slate-100 p-8 font-serif text-slate-900 min-h-screen flex flex-col items-center justify-center">

    <div class="no-print mb-6 flex gap-4 font-sans">
        <a href="/?aba=membros" class="px-4 py-2 bg-slate-800 text-white rounded-xl text-xs font-bold shadow">← Voltar</a>
        <button onclick="window.print()" class="px-5 py-2 bg-indigo-700 hover:bg-indigo-800 text-white rounded-xl text-xs font-bold shadow cursor-pointer">
            🖨️ Imprimir Carta de Recomendação / PDF
        </button>
    </div>

    <!-- FOLHA OFICIAL TIMBRADA A4 -->
    <div class="w-full max-w-3xl bg-white p-12 rounded-2xl shadow-xl border border-slate-300 print:shadow-none print:border-none print:p-0">
        
        <!-- CABEÇALHO TIMBRADO -->
        <div class="text-center border-b-2 border-slate-800 pb-6 mb-8 font-sans">
            <div class="w-14 h-14 mx-auto rounded-full bg-indigo-950 text-white flex items-center justify-center font-black text-xl shadow mb-2">
                AD
            </div>
            <h1 class="text-xl font-black uppercase tracking-wider text-slate-950">ASSEMBLEIA DE DEUS EM MOÇAMBIQUE</h1>
            <h2 class="text-xs font-bold uppercase tracking-wide text-amber-800">MINISTÉRIO THAVANE • SEDE REGIONAL DE CHICUQUE - MAXIXE</h2>
            <p class="text-[11px] text-slate-500 mt-0.5">Gabinete Pastoral & Secretaria-Geral • Inhambane, Moçambique</p>
        </div>

        <!-- TÍTULO -->
        <div class="text-center my-6 font-sans">
            <h3 class="text-xl font-extrabold uppercase tracking-widest text-indigo-950 border-y border-slate-200 py-2 inline-block px-8">
                CARTA DE RECOMENDAÇÃO ECLESIÁSTICA
            </h3>
        </div>

        <div class="font-sans text-xs text-slate-500 mb-6 flex justify-between">
            <span>Ref: CR/{{ m.id }}/2026</span>
            <span>Data: {{ data_extenso }}</span>
        </div>

        <!-- CORPO DA CARTA -->
        <div class="space-y-4 text-justify text-sm leading-relaxed text-slate-800">
            <p>
                <b>À amada Igreja de Nosso Senhor Jesus Cristo e à sua Liderança Pastoral:</b>
            </p>
            <p>
                A Graça e a Paz de Nosso Senhor e Salvador Jesus Cristo vos sejam multiplicadas.
            </p>
            <p>
                Pela presente vimos, por meio desta, apresentar e mui fraternalmente recomendar à vossa comunhão e aos vossos santos cuidados o(a) nosso(a) estimado(a) irmão(ã) 
                <b class="text-indigo-950 uppercase font-sans">{{ m.nome }}</b>, 
                portador(a) do Documento de Identificação nº <b>{{ m.bi or 'pendente de homologação' }}</b>, 
                residente em <b>{{ m.local_residencia or m.bairro or 'Chicuque' }}</b>, 
                integrante da <b>{{ m.zona or 'Zona Central' }}</b> e da <b>{{ m.celula or 'Célula Geral' }}</b>.
            </p>
            <p>
                Declaramos que o(a) referido(a) irmão(ã) é membro em plena comunhão com este ministério, exercendo com zelo e dedicação a função de 
                <b class="text-indigo-900 font-sans">{{ m.cargo }}</b> no departamento de <b class="font-sans">{{ m.departamento }}</b>{% if m.data_batismo %}, tendo sido batizado(a) nas águas no dia <b>{{ m.data_batismo }}</b>{% endif %}. Durante a sua permanência connosco, manteve conduta cristã irrepreensível, digna do Evangelho de Cristo.
            </p>
            <p>
                Pedimos, pois, que o(a) recebais no Senhor como convém aos santos, prestando-lhe todo o auxílio espiritual de que necessitar na vossa congregação.
            </p>
            <p class="pt-2">
                "Recomendo-vos a nossa irmã... para que a recebais no Senhor, como convém aos santos..." — <b>Romanos 16:1-2</b>
            </p>
        </div>

        <!-- ESPAÇO PARA CARIMBO E ASSINATURA -->
        <div class="grid grid-cols-2 gap-12 mt-16 pt-8 border-t border-slate-300 text-center font-sans text-xs">
            <div>
                <div class="w-48 mx-auto border-b border-slate-600 mb-1.5"></div>
                <p class="font-extrabold text-slate-900">Pastor Presidente Regional</p>
                <p class="text-[10px] text-slate-500">Assembleia de Deus - Sede Chicuque</p>
            </div>
            <div>
                <div class="w-28 h-28 mx-auto border-2 border-dashed border-slate-300 rounded-full flex items-center justify-center text-[10px] text-slate-400 font-bold uppercase">
                    Carimbo Oficial
                </div>
            </div>
        </div>
    </div>
</body>
</html>
'''

with open(os.path.join('templates', 'carta_recomendacao.html'), 'w', encoding='utf-8') as f:
    f.write(carta_recomendacao_html)
print("✓ templates/carta_recomendacao.html criado com sucesso!")

# =============================================================================
# 5. ATUALIZAR TEMPLATES/DASHBOARD.HTML COM OS NOVOS CAMPOS E BOTÕES DE AÇÃO
# =============================================================================
with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    dash = f.read()

# Substituir o formulário de Membros para incluir todos os novos seletores e campos
form_membros_antigo = '''                <h3 class="font-bold text-base mb-4 border-b pb-2">➕ Cadastrar Novo Membro</h3>
                <form action="/membros/novo" method="POST" class="space-y-3 text-xs">
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Nome Completo *</label>
                        <input type="text" name="nome" required placeholder="Nome do Membro" class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                    </div>
                    <div class="grid grid-cols-2 gap-2">
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">BI</label>
                            <input type="text" name="bi" placeholder="Nº de BI" class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                        </div>
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Contacto</label>
                            <input type="text" name="contacto" placeholder="+258..." class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                        </div>
                    </div>
                    <div class="grid grid-cols-2 gap-2">
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Cargo</label>
                            <select name="cargo" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-semibold">
                                {% for op in opcoes.get('cargo', []) %}
                                <option value="{{ op.valor }}">{{ op.valor }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Departamento</label>
                            <select name="departamento" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-semibold">
                                {% for op in opcoes.get('departamento', []) %}
                                <option value="{{ op.valor }}">{{ op.valor }}</option>
                                {% endfor %}
                            </select>
                        </div>
                    </div>
                    <button type="submit" class="w-full py-3 bg-emerald-700 hover:bg-emerald-800 text-white font-bold rounded-xl shadow cursor-pointer transition">
                        Gravar Ficha de Membro
                    </button>
                </form>'''

form_membros_novo = '''                <h3 class="font-bold text-base mb-4 border-b pb-2">➕ Cadastrar Ficha Oficial de Membro</h3>
                <form action="/membros/novo" method="POST" class="space-y-3 text-xs">
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Nome Completo *</label>
                        <input type="text" name="nome" required placeholder="Nome completo do membro" class="w-full h-10 px-3 border rounded-xl bg-slate-50 focus:bg-white font-bold">
                    </div>
                    
                    <div class="grid grid-cols-2 gap-2">
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Nº Documento (BI)</label>
                            <input type="text" name="bi" placeholder="Nº de BI ou Cédula" class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                        </div>
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Contacto / WhatsApp</label>
                            <input type="text" name="contacto" placeholder="+258 84/82..." class="w-full h-10 px-3 border rounded-xl bg-slate-50">
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
                            <label class="block font-semibold text-slate-600 mb-1">Zona Eclesiástica</label>
                            <select name="zona" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-semibold">
                                {% for op in opcoes.get('zona', []) %}
                                <option value="{{ op.valor }}">{{ op.valor }}</option>
                                {% else %}
                                <option value="Zona 1 - Central">Zona 1 - Central</option>
                                {% endfor %}
                            </select>
                        </div>
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Célula Familiar</label>
                            <select name="celula" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-semibold">
                                {% for op in opcoes.get('celula', []) %}
                                <option value="{{ op.valor }}">{{ op.valor }}</option>
                                {% else %}
                                <option value="Célula Betel">Célula Betel</option>
                                <option value="Célula Ebenézer">Célula Ebenézer</option>
                                {% endfor %}
                            </select>
                        </div>
                    </div>

                    <div class="grid grid-cols-2 gap-2">
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Cargo Ministerial</label>
                            <select name="cargo" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-semibold">
                                {% for op in opcoes.get('cargo', []) %}
                                <option value="{{ op.valor }}">{{ op.valor }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Departamento</label>
                            <select name="departamento" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-semibold">
                                {% for op in opcoes.get('departamento', []) %}
                                <option value="{{ op.valor }}">{{ op.valor }}</option>
                                {% endfor %}
                            </select>
                        </div>
                    </div>

                    <div class="grid grid-cols-2 gap-2">
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Ano de Conversão</label>
                            <input type="number" name="ano_conversao" placeholder="Ex: 2022" class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                        </div>
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Data do Batismo nas Águas</label>
                            <input type="date" name="data_batismo" class="w-full h-10 px-2 border rounded-xl bg-emerald-50/70 border-emerald-300">
                        </div>
                    </div>

                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Local de Residência (Bairro / Ponto de Ref.)</label>
                        <input type="text" name="local_residencia" placeholder="Ex: Chicuque - Perto do Hospital" class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                    </div>

                    <button type="submit" class="w-full py-3 bg-emerald-700 hover:bg-emerald-800 text-white font-bold rounded-xl shadow cursor-pointer transition text-xs">
                        Gravar Ficha de Membro
                    </button>
                </form>'''

if form_membros_antigo in dash:
    dash = dash.replace(form_membros_antigo, form_membros_novo)

# Substituir a tabela de membros para incluir os botões diretos de emissão de Cartão, Batismo e Recomendação
tabela_membros_antiga = '''                <table class="w-full text-left border-collapse text-xs">
                        <thead><tr class="border-b-2 border-slate-200 text-slate-500"><th class="py-2 px-2">Nome</th><th class="py-2 px-2">BI</th><th class="py-2 px-2">Contacto</th><th class="py-2 px-2">Cargo & Depto</th></tr></thead>
                        <tbody>
                            {% for m in membros %}
                            <tr class="border-b border-slate-100 hover:bg-slate-50"><td class="py-2.5 px-2 font-bold text-slate-800">{{ m.nome }}</td><td class="py-2.5 px-2 text-slate-600">{{ m.bi or '---' }}</td><td class="py-2.5 px-2 text-slate-600">{{ m.contacto or '---' }}</td><td class="py-2.5 px-2 font-bold text-indigo-700">{{ m.cargo }} • {{ m.departamento }}</td></tr>
                            {% else %}
                            <tr><td colspan="4" class="py-8 text-center text-slate-400">Nenhum membro registado.</td></tr>
                            {% endfor %}
                        </tbody>
                    </table>'''

tabela_membros_nova = '''                <table class="w-full text-left border-collapse text-xs">
                        <thead>
                            <tr class="border-b-2 border-slate-200 text-slate-500">
                                <th class="py-2 px-2">Membro</th>
                                <th class="py-2 px-2">Zona & Célula</th>
                                <th class="py-2 px-2">Cargo & Depto</th>
                                <th class="py-2 px-2">Batismo</th>
                                <th class="py-2 px-2 text-right">Documentos Oficiais</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for m in membros %}
                            <tr class="border-b border-slate-100 hover:bg-slate-50">
                                <td class="py-2.5 px-2">
                                    <div class="font-bold text-slate-900">{{ m.nome }}</div>
                                    <div class="text-[10px] text-slate-400">{{ m.estado_civil or '---' }} • Res: {{ m.local_residencia or m.bairro or '---' }}</div>
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
                                    <span class="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full font-bold text-[10px]">
                                        🌊 {{ m.data_batismo }}
                                    </span>
                                    {% else %}
                                    <span class="text-slate-400 text-[10px] italic">Não Batizado</span>
                                    {% endif %}
                                </td>
                                <td class="py-2.5 px-2 text-right space-x-1">
                                    <a href="/membros/{{ m.id }}/cartao" target="_blank" class="px-2 py-1 bg-indigo-600 hover:bg-indigo-700 text-white rounded font-bold text-[10px] shadow inline-block" title="Imprimir Cartão de Membro">
                                        🪪 Cartão
                                    </a>
                                    {% if m.data_batismo %}
                                    <a href="/membros/{{ m.id }}/batismo" target="_blank" class="px-2 py-1 bg-emerald-600 hover:bg-emerald-700 text-white rounded font-bold text-[10px] shadow inline-block" title="Certificado de Batismo">
                                        🌊 Batismo
                                    </a>
                                    {% endif %}
                                    <a href="/membros/{{ m.id }}/recomendacao" target="_blank" class="px-2 py-1 bg-amber-600 hover:bg-amber-700 text-white rounded font-bold text-[10px] shadow inline-block" title="Carta de Recomendação">
                                        📜 Carta
                                    </a>
                                </td>
                            </tr>
                            {% else %}
                            <tr><td colspan="5" class="py-8 text-center text-slate-400">Nenhum membro registado.</td></tr>
                            {% endfor %}
                        </tbody>
                    </table>'''

if tabela_membros_antiga in dash:
    dash = dash.replace(tabela_membros_antiga, tabela_membros_nova)

# Adicionar as categorias Zona, Célula e Estado Civil no Gestor de Seletores do dashboard
dash = dash.replace(
    '<option value="classe_doutrina">📖 Classes Doutrina</option>',
    '<option value="classe_doutrina">📖 Classes Doutrina</option>\n                            <option value="zona">📍 Zonas da Igreja</option>\n                            <option value="celula">🏠 Células Familiares</option>\n                            <option value="estado_civil">💍 Estado Civil</option>'
)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(dash)

print("✓ templates/dashboard.html: Formulário ampliado e botões de documentos integrados!")
print("=" * 80)
print("INSTALAÇÃO CONCLUÍDA COM TOTAL SUCESSO!")
print("=" * 80)