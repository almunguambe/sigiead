import os
import sys
import jinja2

print("=" * 80)
print("A RECONSTRUIR O SISTEMA COM O LOGO OFICIAL, MULTI-CONGREGAÇÃO E 36 DISTRITOS...")
print("=" * 80)

os.makedirs('templates', exist_ok=True)
env = jinja2.Environment()

# =============================================================================
# 1. TEMPLATE DO LOGO OFICIAL DA ASSEMBLEIA DE DEUS (SVG VETORIAL DE ALTA DEFINIÇÃO)
# =============================================================================
logo_svg_html = """<!-- LOGO OFICIAL: IGREJA EVANGÉLICA ASSEMBLEIA DE DEUS EM MOÇAMBIQUE -->
<div class="inline-flex items-center justify-center select-none">
    <svg viewBox="0 0 450 450" class="w-full h-full max-w-[180px] max-h-[180px] drop-shadow-md" xmlns="http://www.w3.org/2000/svg">
        <!-- Círculo de Base -->
        <circle cx="225" cy="225" r="215" fill="#ffffff" stroke="#0044cc" stroke-width="4"/>
        
        <!-- Texto em Arco Superior: IGREJA EVANGÉLICA ASSEMBLEIA DE DEUS -->
        <path id="textArc" d="M 50,225 A 175,175 0 1,1 400,225" fill="none"/>
        <text font-family="Arial, Helvetica, sans-serif" font-size="21" font-weight="900" fill="#000000" letter-spacing="1.5">
            <textPath href="#textArc" startOffset="50%" text-anchor="middle">
                IGREJA EVANGÉLICA ASSEMBLEIA DE DEUS
            </textPath>
        </text>

        <!-- Silhueta Vetorial do Mapa de Moçambique (Laranja Oficial) -->
        <path d="M 235,120 
                 C 260,115 315,115 320,135 
                 C 325,160 325,185 300,195 
                 C 275,205 260,230 250,265 
                 C 240,290 255,340 240,365 
                 C 230,380 205,385 190,370 
                 C 175,355 195,315 210,290 
                 C 225,265 220,240 200,215 
                 C 180,190 215,160 220,135 Z" 
              fill="#ff4d22" stroke="#d6340c" stroke-width="2"/>

        <!-- Cruz Latina em Azul Real -->
        <rect x="233" y="90" width="14" height="270" fill="#0044cc"/>
        <rect x="180" y="140" width="120" height="14" fill="#0044cc"/>

        <!-- Letra ALFA (A) em Azul Real -->
        <path d="M 120,310 L 165,150 L 195,150 L 235,310 L 195,310 L 183,260 L 145,260 L 138,310 Z 
                 M 152,225 L 176,225 L 164,175 Z" 
              fill="#0044cc"/>

        <!-- Letra ÓMEGA (Ω) em Azul Real -->
        <path d="M 235,310 L 255,310 L 255,285 C 245,275 235,255 235,230 C 235,185 265,160 305,160 C 345,160 375,185 375,230 C 375,255 365,275 355,285 L 355,310 L 375,310 L 375,325 L 325,325 L 325,310 L 335,310 C 345,300 350,285 350,230 C 350,198 332,180 305,180 C 278,180 260,198 260,230 C 260,285 265,300 275,310 L 285,310 L 285,325 L 235,325 Z" 
              fill="#0044cc"/>
    </svg>
</div>
"""

with open(os.path.join('templates', 'logo_ad.html'), 'w', encoding='utf-8') as f:
    f.write(logo_svg_html)
print("✓ templates/logo_ad.html: Logotipo oficial vetorizado!")

# =============================================================================
# 2. ATUALIZAR APP.PY COM OS 36 DISTRITOS, MULTI-TENANT E CORREÇÃO DO ERRO 500
# =============================================================================
app_code = '''import os
import sqlite3
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'iead_mz_nacional_2026_chave')

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
        if hasattr(conn, 'commit'): conn.commit()
    except Exception as e:
        if hasattr(conn, 'rollback'): conn.rollback()
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

# ESTRUTURA TERRITORIAL OFICIAL: 36 DISTRITOS
DIVISAO_TERRITORIAL = {
    'Inhambane': [
        'Funhalouro', 'Govuro', 'Homoíne', 'Inhambane (Cidade/Distrito)',
        'Inharrime', 'Inhassoro', 'Jangamo', 'Mabote', 'Massinga',
        'Maxixe (Cidade/Distrito)', 'Morrumbene', 'Panda', 'Vilanculos', 'Zavala'
    ],
    'Gaza': [
        'Bilene', 'Chibuto', 'Chicualacuala', 'Chigubo', 'Chókwè',
        'Chongoene', 'Guijá', 'Limpopo', 'Mabalane', 'Manjacaze',
        'Mapai', 'Massangena', 'Massingir', 'Xai-Xai'
    ],
    'Maputo': [
        'Boane', 'Magude', 'Manhiça', 'Marracuene',
        'Matola (Capital Provincial)', 'Matutuíne', 'Moamba', 'Namaacha'
    ]
}

def inicializar_banco():
    is_pg = bool(DATABASE_URL)
    conn = get_db()
    cur = conn.cursor()
    pk = "SERIAL PRIMARY KEY" if is_pg else "INTEGER PRIMARY KEY AUTOINCREMENT"

    tabelas = [
        f"""CREATE TABLE IF NOT EXISTS congregacoes (
            id {pk}, nome TEXT, provincia TEXT, distrito TEXT, bairro TEXT, pastor_responsavel TEXT, criado_em TEXT
        );""",
        f"""CREATE TABLE IF NOT EXISTS usuarios_sistema (
            id {pk}, nome TEXT, usuario TEXT UNIQUE, senha TEXT, 
            nivel TEXT, perfil TEXT, congregacao_id INT DEFAULT 1, provincia TEXT, distrito TEXT, criado_em TEXT
        );""",
        f"""CREATE TABLE IF NOT EXISTS membros (id {pk}, congregacao_id INT DEFAULT 1, nome TEXT);""",
        f"""CREATE TABLE IF NOT EXISTS planificacao (id {pk}, congregacao_id INT DEFAULT 1, actividade TEXT);""",
        f"""CREATE TABLE IF NOT EXISTS novos_convertidos (id {pk}, congregacao_id INT DEFAULT 1, nome TEXT);""",
        f"""CREATE TABLE IF NOT EXISTS cultos (id {pk}, congregacao_id INT DEFAULT 1, data_culto TEXT);""",
        f"""CREATE TABLE IF NOT EXISTS caixa (id {pk}, congregacao_id INT DEFAULT 1, valor REAL);""",
        f"""CREATE TABLE IF NOT EXISTS doutrina (id {pk}, congregacao_id INT DEFAULT 1, nome_aluno TEXT);""",
        f"""CREATE TABLE IF NOT EXISTS casamentos (id {pk}, congregacao_id INT DEFAULT 1, noivo TEXT);""",
        f"""CREATE TABLE IF NOT EXISTS obitos (id {pk}, congregacao_id INT DEFAULT 1, nome_falecido TEXT);""",
        f"""CREATE TABLE IF NOT EXISTS opcoes_sistema (id {pk}, categoria TEXT, valor TEXT);""",
        f"""CREATE TABLE IF NOT EXISTS progresso_licoes (
            id {pk}, aluno_id INT, licao_id TEXT, resumo_aluno TEXT, nota_teste REAL DEFAULT 0, status TEXT, criado_em TEXT
        );""",
        f"""CREATE TABLE IF NOT EXISTS duvidas_alunos (
            id {pk}, aluno_id INT, licao_id TEXT, pergunta TEXT, resposta_sistema TEXT, resposta_professor TEXT, professor_nome TEXT, criado_em TEXT
        );""",
        f"""CREATE TABLE IF NOT EXISTS balanco_anual (
            id {pk}, congregacao_id INT DEFAULT 1, ano INT, constrangimento_1 TEXT, constrangimento_2 TEXT, constrangimento_3 TEXT,
            perspectiva_1 TEXT, perspectiva_2 TEXT, perspectiva_3 TEXT, atualizado_em TEXT
        );"""
    ]
    for sql in tabelas:
        try:
            cur.execute(sql)
            if hasattr(conn, 'commit'): conn.commit()
        except: pass

    if not is_pg:
        for t in ['membros', 'planificacao', 'novos_convertidos', 'cultos', 'caixa', 'doutrina', 'casamentos', 'obitos', 'balanco_anual']:
            try: cur.execute(f"ALTER TABLE {t} ADD COLUMN congregacao_id INT DEFAULT 1;")
            except: pass

        for col, tipo in [
            ('nome', 'TEXT'), ('contacto', 'TEXT'), ('bi', 'TEXT'), ('cargo', 'TEXT'),
            ('departamento', 'TEXT'), ('estado_civil', 'TEXT'), ('zona', 'TEXT'),
            ('celula', 'TEXT'), ('ano_conversao', 'TEXT'), ('data_batismo', 'TEXT'),
            ('local_residencia', 'TEXT'), ('bairro', 'TEXT'), ('genero', 'TEXT DEFAULT "Masculino"'), ('criado_em', 'TEXT')
        ]:
            try: cur.execute(f"ALTER TABLE membros ADD COLUMN {col} {tipo};")
            except: pass

        for col, tipo in [
            ('tipo', 'TEXT'), ('categoria', 'TEXT'), ('valor', 'REAL'),
            ('descricao', 'TEXT'), ('data_movimento', 'TEXT'), ('conta', 'TEXT'),
            ('destino_tipo', 'TEXT'), ('departamento', 'TEXT'), ('proposito', 'TEXT'), ('criado_em', 'TEXT')
        ]:
            try: cur.execute(f"ALTER TABLE caixa ADD COLUMN {col} {tipo};")
            except: pass

        for col, tipo in [
            ('usuario', 'TEXT'), ('senha', 'TEXT'), ('aproveitamento', 'REAL DEFAULT 0'),
            ('classe', 'TEXT'), ('professor', 'TEXT'), ('situacao', 'TEXT DEFAULT "Em Formação"')
        ]:
            try: cur.execute(f"ALTER TABLE doutrina ADD COLUMN {col} {tipo};")
            except: pass

        for col, tipo in [
            ('tipo', 'TEXT'), ('noivo', 'TEXT'), ('noiva', 'TEXT'), ('data_casamento', 'TEXT'),
            ('ministro', 'TEXT'), ('regime', 'TEXT'), ('certidao', 'TEXT'), ('criado_em', 'TEXT')
        ]:
            try: cur.execute(f"ALTER TABLE casamentos ADD COLUMN {col} {tipo};")
            except: pass

        for col, tipo in [
            ('nome_falecido', 'TEXT'), ('genero', 'TEXT'), ('categoria', 'TEXT'),
            ('data_falecimento', 'TEXT'), ('local_funeral', 'TEXT'), ('causa', 'TEXT'), ('contacto_familia', 'TEXT'), ('criado_em', 'TEXT')
        ]:
            try: cur.execute(f"ALTER TABLE obitos ADD COLUMN {col} {tipo};")
            except: pass

        if hasattr(conn, 'commit'): conn.commit()
    conn.close()

    # Inserir congregação sede padrão
    m = "%s" if is_pg else "?"
    if not consultar_um("SELECT id FROM congregacoes WHERE id = 1"):
        sql_c = f"""INSERT INTO congregacoes (id, nome, provincia, distrito, bairro, pastor_responsavel, criado_em)
                    VALUES (1, 'Sede Regional de Chicuque', 'Inhambane', 'Maxixe (Cidade/Distrito)', 'Chicuque', 'Pastor Dirigente', {m})"""
        executar_comando(sql_c, (datetime.now().strftime('%Y-%m-%d %H:%M'),))

    # Inserir utilizadores institucionais com RBAC
    perfis_padrao = [
        ('Administrador Geral', 'admin', 'admin123', 'geral', 'admin', 1, 'Inhambane', 'Maxixe (Cidade/Distrito)'),
        ('Pastor Dirigente', 'pastor', 'pastor123', 'geral', 'pastor', 1, 'Inhambane', 'Maxixe (Cidade/Distrito)'),
        ('Secretaria Geral', 'secretaria', 'sec123', 'secretaria', 'secretario', 1, 'Inhambane', 'Maxixe (Cidade/Distrito)'),
        ('Tesouraria da Igreja', 'tesouraria', 'tesouro123', 'tesouraria', 'tesoureiro', 1, 'Inhambane', 'Maxixe (Cidade/Distrito)'),
        ('Direcção Distrital Maxixe', 'distrital', 'distrito123', 'distrital', 'distrital', 1, 'Inhambane', 'Maxixe (Cidade/Distrito)'),
        ('Direcção Provincial Inhambane', 'provincial', 'provincia123', 'provincial', 'provincial', 1, 'Inhambane', 'Todos')
    ]
    for n, u, s, niv, perf, cid, prov, dist in perfis_padrao:
        if not consultar_um(f"SELECT id FROM usuarios_sistema WHERE usuario = {m}", (u,)):
            sql_u = f"""INSERT INTO usuarios_sistema (nome, usuario, senha, nivel, perfil, congregacao_id, provincia, distrito, criado_em)
                        VALUES ({m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m})"""
            executar_comando(sql_u, (n, u, s, niv, perf, cid, prov, dist, datetime.now().strftime('%Y-%m-%d %H:%M')))

inicializar_banco()

# CONTROLO DE AUTENTICAÇÃO E AUTORIZAÇÃO (RBAC)
def login_obrigatorio(f):
    @wraps(f)
    def decorado(*args, **kwargs):
        if not session.get('usuario_id'):
            return redirect('/login')
        return f(*args, **kwargs)
    return decorado

def apenas_tesouraria(f):
    @wraps(f)
    def decorado(*args, **kwargs):
        p = session.get('usuario_perfil', '')
        if p not in ['tesoureiro', 'admin']:
            return "<script>alert('Acesso negado! O módulo de caixa e finanças é estritamente exclusivo da Tesouraria.'); window.location.href='/?aba=dashboard';</script>"
        return f(*args, **kwargs)
    return decorado

# CONTEXTO GLOBAL INJETADO NOS TEMPLATES
@app.context_processor
def injetar_global():
    u_id = session.get('usuario_id')
    user = consultar_um("SELECT * FROM usuarios_sistema WHERE id = %s" % u_id) if u_id else None
    cid = user.get('congregacao_id', 1) if user else session.get('congregacao_id', 1)
    
    cong = consultar_um("SELECT * FROM congregacoes WHERE id = %s" % cid) or {
        'id': 1, 'nome': 'Sede Regional de Chicuque', 'distrito': 'Maxixe (Cidade/Distrito)', 'provincia': 'Inhambane', 'bairro': 'Chicuque'
    }

    m = "%s" if DATABASE_URL else "?"
    membros = consultar_todos(f"SELECT * FROM membros WHERE congregacao_id = {m} ORDER BY id DESC", (cid,))
    planos = consultar_todos(f"SELECT * FROM planificacao WHERE congregacao_id = {m} ORDER BY id DESC", (cid,))
    cultos = consultar_todos(f"SELECT * FROM cultos WHERE congregacao_id = {m} ORDER BY id DESC", (cid,))
    convertidos = consultar_todos(f"SELECT * FROM novos_convertidos WHERE congregacao_id = {m} ORDER BY id DESC", (cid,))
    caixa = consultar_todos(f"SELECT * FROM caixa WHERE congregacao_id = {m} ORDER BY id DESC", (cid,))
    doutrina = consultar_todos(f"SELECT * FROM doutrina WHERE congregacao_id = {m} ORDER BY id DESC", (cid,))
    casamentos = consultar_todos(f"SELECT * FROM casamentos WHERE congregacao_id = {m} ORDER BY id DESC", (cid,))
    obitos = consultar_todos(f"SELECT * FROM obitos WHERE congregacao_id = {m} ORDER BY id DESC", (cid,))
    duvidas_pendentes = consultar_todos("SELECT * FROM duvidas_alunos WHERE resposta_professor IS NULL OR resposta_professor = '' ORDER BY id DESC")
    opcoes_lista = consultar_todos("SELECT * FROM opcoes_sistema ORDER BY categoria, valor ASC")

    opcoes_map = {}
    for op in opcoes_lista:
        opcoes_map.setdefault(op['categoria'], []).append(op)

    # CÁLCULO DEMOGRÁFICO PURO (COM AS CHAVES 'zonas', 'celulas' E 'cargos')
    total_homens = 0
    total_mulheres = 0
    total_criancas = 0
    total_jovens = 0
    total_adultos = 0
    total_batizados = 0
    total_nao_batizados = 0

    zonas_contagem = {}
    celulas_contagem = {}
    cargos_contagem = {}

    for mb in membros:
        gen = str(mb.get('genero') or '').lower()
        if gen in ['f', 'feminino', 'mulher']: total_mulheres += 1
        else: total_homens += 1

        ec = str(mb.get('estado_civil') or '').lower()
        dep = str(mb.get('departamento') or '').lower()
        if ec == 'criança' or 'esperança' in dep or 'crian' in dep:
            total_criancas += 1
        elif 'jov' in dep or 'juventude' in dep:
            total_jovens += 1
        else:
            total_adultos += 1

        if mb.get('data_batismo'): total_batizados += 1
        else: total_nao_batizados += 1

        z = mb.get('zona') or 'Zona Central'
        zonas_contagem[z] = zonas_contagem.get(z, 0) + 1

        cel = mb.get('celula') or 'Geral'
        celulas_contagem[cel] = celulas_contagem.get(cel, 0) + 1

        cg = mb.get('cargo') or 'Membro em Comunhão'
        cargos_contagem[cg] = cargos_contagem.get(cg, 0) + 1

    total_pres = sum([int(c.get('total_presentes') or 0) for c in cultos])
    media_culto = int(total_pres / len(cultos)) if cultos else 0

    # FINANÇAS SEPARADAS
    tin = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Entrada'])
    tout = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Saída'])

    planos_exec = len([p for p in planos if str(p.get('status') or '').lower() == 'executado'])
    taxa_exec = int((planos_exec / len(planos) * 100)) if planos else 0

    return {
        'usuario_logado': user,
        'congregacao': cong,
        'divisao_territorial': DIVISAO_TERRITORIAL,
        'membros': membros, 'planificacoes': planos, 'cultos': cultos,
        'convertidos': convertidos, 'caixa': caixa, 'doutrina': doutrina,
        'casamentos': casamentos, 'obitos': obitos, 'duvidas_pendentes': duvidas_pendentes,
        'opcoes': opcoes_map,
        'demografia': {
            'total_almas': len(membros) + len(convertidos),
            'membros_cadastrados': len(membros),
            'homens': total_homens,
            'mulheres': total_mulheres,
            'perc_homens': int((total_homens / len(membros) * 100)) if membros else 50,
            'perc_mulheres': int((total_mulheres / len(membros) * 100)) if membros else 50,
            'criancas': total_criancas,
            'jovens': total_jovens,
            'adultos': total_adultos,
            'batizados': total_batizados,
            'nao_batizados': total_nao_batizados,
            'novos_convertidos': len(convertidos),
            'total_cultos': len(cultos),
            'media_culto': media_culto,
            'total_casamentos': len(casamentos),
            'total_obitos': len(obitos),
            'zonas': zonas_contagem,
            'celulas': celulas_contagem,
            'cargos': cargos_contagem,
            'planos_total': len(planos),
            'planos_executados': planos_exec,
            'taxa_execucao': taxa_exec
        },
        'kpis': {
            'saldo_caixa': tin - tout,
            'total_entradas': tin,
            'total_saidas': tout
        }
    }

# =============================================================================
# ROTAS DE AUTENTICAÇÃO E NAVEGAÇÃO
# =============================================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        usuario = request.form.get('usuario', '').strip().lower()
        senha = request.form.get('senha', '').strip()
        m = "%s" if DATABASE_URL else "?"
        u = consultar_um(f"SELECT * FROM usuarios_sistema WHERE LOWER(usuario) = {m} AND senha = {m}", (usuario, senha))
        if u:
            session['usuario_id'] = u['id']
            session['usuario_nome'] = u['nome']
            session['usuario_perfil'] = u['perfil']
            session['usuario_nivel'] = u['nivel']
            session['congregacao_id'] = u['congregacao_id']

            if u['perfil'] == 'distrital':
                return redirect('/distrital/dashboard')
            elif u['perfil'] == 'provincial':
                return redirect('/provincial/dashboard')
            elif u['perfil'] == 'tesoureiro':
                return redirect('/?aba=tesouraria')
            return redirect('/?aba=dashboard')
        else:
            erro = "Credenciais inválidas! Verifique o utilizador e a palavra-passe."
    return render_template('login.html', erro=erro)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# =============================================================================
# PAINEL DA CONGREGAÇÃO LOCAL
# =============================================================================
@app.route('/')
@login_obrigatorio
def index():
    aba = request.args.get('aba', 'dashboard')
    id_relatar = request.args.get('relatar_id')
    plano_para_relatar = None
    if id_relatar:
        m = "%s" if DATABASE_URL else "?"
        plano_para_relatar = consultar_um(f"SELECT * FROM planificacao WHERE id = {m}", (id_relatar,))
    return render_template('dashboard.html', aba_ativa=aba, plano_relatar=plano_para_relatar)

# -------------------------------------------------------------
# CADASTROS LOCAIS
# -------------------------------------------------------------
@app.route('/membros/novo', methods=['POST'])
@login_obrigatorio
def membros_gravar():
    fd = request.form
    cid = session.get('congregacao_id', 1)
    local = (fd.get('local_residencia') or fd.get('bairro') or '').strip()
    genero = fd.get('genero', 'Masculino').strip()
    m = "%s" if DATABASE_URL else "?"
    sql = f"""INSERT INTO membros 
              (congregacao_id, nome, contacto, bi, cargo, departamento, estado_civil, zona, celula, ano_conversao, data_batismo, local_residencia, bairro, genero, criado_em)
              VALUES ({m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m})"""
    executar_comando(sql, (cid, fd.get('nome'), fd.get('contacto'), fd.get('bi'), fd.get('cargo'), fd.get('departamento'), fd.get('estado_civil'), fd.get('zona'), fd.get('celula'), fd.get('ano_conversao'), fd.get('data_batismo'), local, local, genero, datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=membros')

@app.route('/actos/casamento/novo', methods=['POST'])
@login_obrigatorio
def actos_casamento():
    fd = request.form
    cid = session.get('congregacao_id', 1)
    m = "%s" if DATABASE_URL else "?"
    sql = f"INSERT INTO casamentos (congregacao_id, tipo, noivo, noiva, data_casamento, ministro, regime, certidao, criado_em) VALUES ({m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m})"
    executar_comando(sql, (cid, fd.get('tipo'), fd.get('noivo'), fd.get('noiva'), fd.get('data_casamento'), fd.get('ministro'), fd.get('regime'), fd.get('certidao'), datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=actos')

@app.route('/actos/casamento/remover/<int:id>')
@login_obrigatorio
def actos_casamento_remover(id):
    m = "%s" if DATABASE_URL else "?"
    executar_comando(f"DELETE FROM casamentos WHERE id = {m}", (id,))
    return redirect('/?aba=actos')

@app.route('/actos/obito/novo', methods=['POST'])
@login_obrigatorio
def actos_obito():
    fd = request.form
    cid = session.get('congregacao_id', 1)
    m = "%s" if DATABASE_URL else "?"
    sql = f"INSERT INTO obitos (congregacao_id, nome_falecido, genero, categoria, data_falecimento, local_funeral, causa, contacto_familia, criado_em) VALUES ({m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m})"
    executar_comando(sql, (cid, fd.get('nome_falecido'), fd.get('genero'), fd.get('categoria'), fd.get('data_falecimento'), fd.get('local_funeral'), fd.get('causa'), fd.get('contacto_familia'), datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=actos')

@app.route('/actos/obito/remover/<int:id>')
@login_obrigatorio
def actos_obito_remover(id):
    m = "%s" if DATABASE_URL else "?"
    executar_comando(f"DELETE FROM obitos WHERE id = {m}", (id,))
    return redirect('/?aba=actos')

# TESOURARIA COM BLOQUEIO EXCLUSIVO (APENAS TESOUREIRO E ADMIN)
@app.route('/financas/caixa/novo', methods=['POST'])
@login_obrigatorio
@apenas_tesouraria
def caixa_gravar():
    fd = request.form
    cid = session.get('congregacao_id', 1)
    tipo = fd.get('tipo', 'Entrada').strip()
    conta = fd.get('conta', 'Caixa Físico').strip()
    try: val = float(fd.get('valor') or 0)
    except: val = 0.0
    dt = fd.get('data_movimento', datetime.now().strftime('%Y-%m-%d')).strip()
    desc = fd.get('descricao', '').strip()
    destino_tipo = fd.get('destino_tipo', 'Igreja Geral').strip()
    depto = fd.get('departamento', 'Geral').strip()
    proposito = fd.get('proposito', '').strip()

    if tipo == 'Entrada':
        categoria = fd.get('categoria', 'Dízimos') if destino_tipo == 'Igreja Geral' else f"Entrada: {depto}"
    else:
        categoria = fd.get('categoria_saida_geral', 'Despesa') if destino_tipo == 'Igreja Geral' else f"Saída: {depto}"

    m = "%s" if DATABASE_URL else "?"
    sql = f"""INSERT INTO caixa (congregacao_id, tipo, categoria, valor, descricao, data_movimento, conta, destino_tipo, departamento, proposito, criado_em)
              VALUES ({m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m})"""
    executar_comando(sql, (cid, tipo, categoria, val, desc, dt, conta, destino_tipo, depto, proposito, datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=tesouraria')

@app.route('/secretaria/planificacao/nova', methods=['POST'])
@login_obrigatorio
def secretaria_gravar():
    fd = request.form
    cid = session.get('congregacao_id', 1)
    m = "%s" if DATABASE_URL else "?"
    sql = f"INSERT INTO planificacao (congregacao_id, actividade, titulo, departamento, tipo_evento, data_prevista, status, criado_em) VALUES ({m}, {m}, {m}, {m}, {m}, {m}, 'Planeado', {m})"
    executar_comando(sql, (cid, fd.get('actividade'), fd.get('actividade'), fd.get('departamento'), fd.get('tipo_evento'), fd.get('data_prevista'), datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=secretaria')

@app.route('/secretaria/planificacao/relatar', methods=['POST'])
@login_obrigatorio
def secretaria_relatar():
    fd = request.form
    plano_id = fd.get('plano_id')
    feedback = fd.get('feedback', '').strip()
    data_exec = fd.get('data_execucao', datetime.now().strftime('%Y-%m-%d')).strip()
    def to_int(k):
        v = fd.get(k)
        return int(v) if v and v.isdigit() else 0
    tot = to_int('participantes_homens') + to_int('participantes_mulheres') + to_int('participantes_jovens') + to_int('participantes_criancas')
    m = "%s" if DATABASE_URL else "?"
    sql = f"UPDATE planificacao SET status = 'Executado', feedback = {m}, data_execucao = {m}, total_participantes = {m} WHERE id = {m}"
    executar_comando(sql, (feedback, data_exec, tot, plano_id))
    return redirect('/?aba=secretaria')

@app.route('/doutrina/novo', methods=['POST'])
@login_obrigatorio
def doutrina_gravar():
    fd = request.form
    cid = session.get('congregacao_id', 1)
    m = "%s" if DATABASE_URL else "?"
    sql = f"INSERT INTO doutrina (congregacao_id, nome_aluno, classe, professor, licao_atual, usuario, senha, criado_em) VALUES ({m}, {m}, {m}, {m}, 'Lição 1', {m}, {m}, {m})"
    executar_comando(sql, (cid, fd.get('nome_aluno'), fd.get('classe'), fd.get('professor'), fd.get('usuario'), fd.get('senha'), datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=doutrina')

@app.route('/cultos/novo', methods=['POST'])
@login_obrigatorio
def cultos_gravar():
    fd = request.form
    cid = session.get('congregacao_id', 1)
    m = "%s" if DATABASE_URL else "?"
    tot = int(fd.get('total_presentes') or 0)
    sql = f"INSERT INTO cultos (congregacao_id, data_culto, tipo_culto, total_presentes, apelos, pregador, criado_em) VALUES ({m}, {m}, {m}, {m}, {m}, {m}, {m})"
    executar_comando(sql, (cid, fd.get('data_culto'), fd.get('tipo_culto'), tot, int(fd.get('apelos') or 0), fd.get('pregador'), datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=cultos')

@app.route('/convertidos/novo', methods=['POST'])
@login_obrigatorio
def convertidos_gravar():
    fd = request.form
    cid = session.get('congregacao_id', 1)
    m = "%s" if DATABASE_URL else "?"
    sql = f"INSERT INTO novos_convertidos (congregacao_id, nome, telefone, bairro, data_decisao, criado_em) VALUES ({m}, {m}, {m}, {m}, {m}, {m})"
    executar_comando(sql, (cid, fd.get('nome'), fd.get('telefone'), fd.get('bairro'), fd.get('data_decisao'), datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=convertidos')

# =============================================================================
# CONSOLIDAÇÃO DISTRITAL E PROVINCIAL (AGREGAÇÃO DE TODAS AS CONGREGAÇÕES)
# =============================================================================
@app.route('/distrital/dashboard')
@login_obrigatorio
def distrital_dashboard():
    u_id = session.get('usuario_id')
    u = consultar_um("SELECT * FROM usuarios_sistema WHERE id = %s" % u_id)
    distrito = u.get('distrito', 'Maxixe (Cidade/Distrito)')

    m = "%s" if DATABASE_URL else "?"
    congs = consultar_todos(f"SELECT * FROM congregacoes WHERE distrito = {m}", (distrito,))
    c_ids = [str(c['id']) for c in congs] or ['0']
    in_c = ",".join(c_ids)

    tot_membros = consultar_um(f"SELECT COUNT(*) as t FROM membros WHERE congregacao_id IN ({in_c})")['t']
    tot_convertidos = consultar_um(f"SELECT COUNT(*) as t FROM novos_convertidos WHERE congregacao_id IN ({in_c})")['t']
    tot_casamentos = consultar_um(f"SELECT COUNT(*) as t FROM casamentos WHERE congregacao_id IN ({in_c})")['t']
    tot_obitos = consultar_um(f"SELECT COUNT(*) as t FROM obitos WHERE congregacao_id IN ({in_c})")['t']
    tot_cultos = consultar_um(f"SELECT COUNT(*) as t FROM cultos WHERE congregacao_id IN ({in_c})")['t']

    return render_template(
        'distrital_dashboard.html',
        distrito=distrito,
        congregações=congs,
        totais={'membros': tot_membros, 'convertidos': tot_convertidos, 'casamentos': tot_casamentos, 'obitos': tot_obitos, 'cultos': tot_cultos}
    )

@app.route('/provincial/dashboard')
@login_obrigatorio
def provincial_dashboard():
    u_id = session.get('usuario_id')
    u = consultar_um("SELECT * FROM usuarios_sistema WHERE id = %s" % u_id)
    provincia = u.get('provincia', 'Inhambane')

    m = "%s" if DATABASE_URL else "?"
    congs = consultar_todos(f"SELECT * FROM congregacoes WHERE provincia = {m}", (provincia,))
    c_ids = [str(c['id']) for c in congs] or ['0']
    in_c = ",".join(c_ids)

    tot_membros = consultar_um(f"SELECT COUNT(*) as t FROM membros WHERE congregacao_id IN ({in_c})")['t']
    tot_convertidos = consultar_um(f"SELECT COUNT(*) as t FROM novos_convertidos WHERE congregacao_id IN ({in_c})")['t']
    tot_casamentos = consultar_um(f"SELECT COUNT(*) as t FROM casamentos WHERE congregacao_id IN ({in_c})")['t']
    tot_obitos = consultar_um(f"SELECT COUNT(*) as t FROM obitos WHERE congregacao_id IN ({in_c})")['t']

    return render_template(
        'provincial_dashboard.html',
        provincia=provincia,
        congregações=congs,
        totais={'membros': tot_membros, 'convertidos': tot_convertidos, 'casamentos': tot_casamentos, 'obitos': tot_obitos}
    )

# Portal do Aluno
@app.route('/ensino/login')
def portal_login():
    return redirect('/login')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
'''

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_code)
print("✓ app.py: Arquitetura multi-tenant, dicionário demográfico corrigido e RBAC configurados!")

# =============================================================================
# 3. CRIAR A TELA DE LOGIN INSTITUCIONAL COM O NOVO LOGOTIPO
# =============================================================================
login_html = """<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login Oficial - Igreja Evangélica Assembleia de Deus</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .login-bg { background: radial-gradient(circle at 50% 10%, #1e1b4b 0%, #090d16 100%); }
    </style>
</head>
<body class="login-bg min-h-screen flex items-center justify-center p-4 font-sans text-slate-800">

    <div class="max-w-md w-full bg-white/95 backdrop-blur-md p-8 rounded-3xl shadow-2xl border border-indigo-900/30 space-y-6">
        
        <!-- BRASÃO E CABEÇALHO OFICIAL -->
        <div class="text-center space-y-2">
            <div class="w-32 h-32 mx-auto flex items-center justify-center">
                {% include 'logo_ad.html' %}
            </div>
            <h1 class="text-base font-black uppercase text-slate-900 tracking-wide mt-2">
                IGREJA EVANGÉLICA ASSEMBLEIA DE DEUS
            </h1>
            <p class="text-[11px] font-bold text-amber-700 uppercase">
                Sistema Integrado de Gestão Eclesiástica em Moçambique
            </p>
            <p class="text-[10px] italic text-slate-500 font-serif">
                "Quando orardes, lembrai-vos de Moçambique! Remember Mozambique when you pray"
            </p>
        </div>

        {% if erro %}
        <div class="p-3 bg-rose-50 border-2 border-rose-300 rounded-xl text-rose-800 text-xs font-bold text-center">
            {{ erro }}
        </div>
        {% endif %}

        <!-- FORMULÁRIO DE LOGIN -->
        <form action="/login" method="POST" class="space-y-4 text-xs">
            <div>
                <label class="block font-bold text-slate-700 mb-1">Nome de Utilizador *</label>
                <input type="text" name="usuario" required placeholder="Ex: admin / pastor / tesouraria" class="w-full h-11 px-3 border-2 border-slate-200 rounded-xl bg-slate-50 focus:bg-white focus:border-indigo-600 focus:outline-none font-bold">
            </div>

            <div>
                <label class="block font-bold text-slate-700 mb-1">Palavra-passe *</label>
                <input type="password" name="senha" required placeholder="••••••••" class="w-full h-11 px-3 border-2 border-slate-200 rounded-xl bg-slate-50 focus:bg-white focus:border-indigo-600 focus:outline-none font-bold">
            </div>

            <button type="submit" class="w-full py-3.5 bg-indigo-900 hover:bg-indigo-950 text-white font-black rounded-xl shadow-lg cursor-pointer text-sm transition">
                Entrar no Sistema
            </button>
        </form>

        <div class="border-t border-slate-200 pt-3 text-[10px] text-slate-500 space-y-1">
            <span class="font-bold text-slate-700 block">Acessos Padronizados por Função:</span>
            <div class="grid grid-cols-2 gap-1 text-[9px]">
                <p>• <b>admin:</b> Acesso Geral (admin123)</p>
                <p>• <b>tesouraria:</b> Caixa Exclusivo (tesouro123)</p>
                <p>• <b>secretaria:</b> Membresia/Atos (sec123)</p>
                <p>• <b>distrital:</b> Painel do Distrito (distrito123)</p>
                <p>• <b>provincial:</b> Painel da Província (provincia123)</p>
                <p>• <b>pastor:</b> Direção Local (pastor123)</p>
            </div>
        </div>

    </div>

</body>
</html>
"""

env.parse(login_html)
with open(os.path.join('templates', 'login.html'), 'w', encoding='utf-8') as f:
    f.write(login_html)
print("✓ templates/login.html criado com o logotipo oficial!")

# =============================================================================
# 4. RECONSTRUIR TEMPLATES/DASHBOARD.HTML COM LOGO, SEM 'THAVANE' E COM 'ZONAS'
# =============================================================================
dash_completo = """<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IEAD Moçambique - {{ congregacao.nome }}</title>
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

    <!-- MENU LATERAL COM O LOGO OFICIAL -->
    <aside class="w-64 bg-slate-900 text-white flex flex-col justify-between min-h-screen shrink-0 shadow-xl">
        <div>
            <div class="p-4 border-b border-slate-800 flex items-center gap-3">
                <div class="w-12 h-12 bg-white rounded-full p-1 flex items-center justify-center shrink-0 shadow">
                    {% include 'logo_ad.html' %}
                </div>
                <div class="overflow-hidden">
                    <h1 class="font-extrabold text-xs uppercase tracking-wide leading-tight text-white truncate">
                        ASSEMBLEIA DE DEUS
                    </h1>
                    <p class="text-[10px] text-amber-400 font-semibold truncate">{{ congregacao.nome }}</p>
                    <p class="text-[9px] text-slate-400 truncate">{{ congregacao.distrito }}</p>
                </div>
            </div>

            <nav class="p-3 space-y-1 text-xs font-semibold">
                <div class="px-3 py-2 text-[10px] font-bold uppercase tracking-wider text-slate-400">Visão Geral</div>
                
                <a href="/?aba=dashboard" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'dashboard' %}bg-indigo-600 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                    <span>🔬</span><span>Raio-X Demográfico</span>
                </a>

                <div class="px-3 pt-3 pb-1 text-[10px] font-bold uppercase tracking-wider text-slate-400">Geral & Frequência</div>

                <a href="/?aba=membros" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'membros' %}bg-indigo-600 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                    <span>👥</span><span>1. Membros ({{ demografia.membros_cadastrados }})</span>
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

                <a href="/?aba=actos" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'actos' %}bg-pink-700 text-white shadow-md{% else %}text-pink-300 hover:bg-slate-800{% endif %}">
                    <span>💒</span><span>Actos (Casamentos & Óbitos)</span>
                </a>

                <!-- BLOCO FINANCEIRO RESTRITO -->
                {% if usuario_logado and usuario_logado.perfil in ['tesoureiro', 'admin'] %}
                <div class="px-3 pt-3 pb-1 text-[10px] font-bold uppercase tracking-wider text-emerald-400">Finanças & Tesouraria (Exclusivo)</div>

                <a href="/?aba=financas" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'financas' %}bg-emerald-700 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                    <span>📊</span><span>5. Dashboard Financeiro</span>
                </a>

                <a href="/?aba=tesouraria" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'tesouraria' %}bg-amber-600 text-white shadow-md{% else %}text-amber-300 hover:bg-slate-800{% endif %}">
                    <span>🔐</span><span>6. Caixa & Lançamentos</span>
                </a>
                {% endif %}

                <div class="px-3 pt-3 pb-1 text-[10px] font-bold uppercase tracking-wider text-amber-400">Ensino Bíblico</div>

                <a href="/?aba=doutrina" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'doutrina' %}bg-amber-700 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                    <span>📖</span><span>7. Doutrina & Batismo</span>
                </a>
            </nav>
        </div>

        <div class="p-4 border-t border-slate-800 text-xs text-slate-400 flex items-center justify-between">
            <div>
                <p class="font-bold text-white">{{ usuario_logado.nome if usuario_logado else 'Utilizador' }}</p>
                <p class="text-[10px] text-amber-400 uppercase font-semibold">{{ usuario_logado.perfil if usuario_logado else 'Local' }}</p>
            </div>
            <a href="/logout" class="px-2 py-1 bg-slate-800 hover:bg-rose-700 text-slate-300 hover:text-white rounded text-[10px] font-bold">Sair</a>
        </div>
    </aside>

    <!-- ÁREA PRINCIPAL -->
    <main class="flex-1 p-6 overflow-y-auto">

        <!-- ========================================================= -->
        <!-- ABA: RAIO-X ECLESIÁSTICO & DEMOGRAFIA (ZERO FINANÇAS)     -->
        <!-- ========================================================= -->
        {% if aba_ativa == 'dashboard' %}
        <div class="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white p-6 rounded-3xl shadow-xl mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div class="flex items-center gap-4">
                <div class="w-16 h-16 bg-white rounded-2xl p-1.5 shrink-0 hidden sm:block">
                    {% include 'logo_ad.html' %}
                </div>
                <div>
                    <div class="inline-flex items-center gap-2 bg-indigo-500/20 text-indigo-300 px-3 py-1 rounded-full text-[10px] font-black uppercase mb-1 border border-indigo-400/30">
                        <span>🔬</span> CENSO MINISTERIAL • DEMOGRAFIA PROFUNDA
                    </div>
                    <h2 class="text-2xl font-black">Raio-X Eclesiástico: {{ congregacao.nome }}</h2>
                    <p class="text-xs text-indigo-200 mt-0.5">Estatística de almas congregadas sem interferência financeira • {{ congregacao.distrito }}, {{ congregacao.provincia }}</p>
                </div>
            </div>
            <div class="bg-white/10 p-4 rounded-2xl border border-white/10 text-center shrink-0">
                <span class="text-[10px] uppercase font-bold text-indigo-200 block">Total de Almas no Rebanho</span>
                <span class="text-3xl font-black text-amber-300">{{ demografia.total_almas }} Vidas</span>
                <span class="text-[10px] text-slate-300 block mt-0.5">{{ demografia.membros_cadastrados }} Membros • {{ demografia.novos_convertidos }} em Discipulado</span>
            </div>
        </div>

        <!-- 4 CARDS DEMOGRÁFICOS PRINCIPAIS -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-8 text-xs">
            <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 space-y-2">
                <div class="text-slate-500 text-[10px] font-bold uppercase tracking-wider">Distribuição por Género</div>
                <div class="flex justify-between items-baseline">
                    <span class="text-2xl font-black text-slate-900">👨 {{ demografia.homens }} <span class="text-xs font-normal text-slate-400">Homens</span></span>
                    <span class="text-2xl font-black text-indigo-900">👩 {{ demografia.mulheres }} <span class="text-xs font-normal text-slate-400">Mulheres</span></span>
                </div>
                <div class="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden flex border">
                    <div class="bg-blue-600 h-full" style="width: {{ demografia.perc_homens }}%"></div>
                    <div class="bg-pink-500 h-full" style="width: {{ demografia.perc_mulheres }}%"></div>
                </div>
                <div class="flex justify-between text-[10px] text-slate-500 font-bold">
                    <span>Homens: {{ demografia.perc_homens }}%</span>
                    <span>Mulheres: {{ demografia.perc_mulheres }}%</span>
                </div>
            </div>

            <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 space-y-1.5">
                <div class="text-slate-500 text-[10px] font-bold uppercase tracking-wider">Composição Etária</div>
                <div class="flex justify-between items-center text-slate-800 font-bold pt-1">
                    <span>👶 Crianças (Boa Esperança):</span>
                    <span class="text-blue-700 font-black">{{ demografia.criancas }}</span>
                </div>
                <div class="flex justify-between items-center text-slate-800 font-bold">
                    <span>👦 Juventude Cristã:</span>
                    <span class="text-indigo-700 font-black">{{ demografia.jovens }}</span>
                </div>
                <div class="flex justify-between items-center text-slate-800 font-bold">
                    <span>👨‍👩‍👧‍👦 Adultos & Seniores:</span>
                    <span class="text-amber-800 font-black">{{ demografia.adultos }}</span>
                </div>
            </div>

            <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 space-y-1.5">
                <div class="text-slate-500 text-[10px] font-bold uppercase tracking-wider">Situação Eclesiástica</div>
                <div class="flex justify-between items-center text-emerald-800 font-bold pt-1">
                    <span>🌊 Membros Baptizados:</span>
                    <span class="font-black">{{ demografia.batizados }}</span>
                </div>
                <div class="flex justify-between items-center text-amber-800 font-bold">
                    <span>🌱 Não Baptizados / Doutrina:</span>
                    <span class="font-black">{{ demografia.nao_batizados }}</span>
                </div>
                <div class="flex justify-between items-center text-blue-800 font-bold">
                    <span>📖 Novos Convertidos:</span>
                    <span class="font-black">{{ demografia.novos_convertidos }}</span>
                </div>
            </div>

            <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 space-y-1.5">
                <div class="text-slate-500 text-[10px] font-bold uppercase tracking-wider">Actos & Planificação</div>
                <div class="flex justify-between items-center text-slate-800 font-bold pt-1">
                    <span>💒 Casamentos Registados:</span>
                    <span class="text-pink-600 font-black">{{ demografia.total_casamentos }}</span>
                </div>
                <div class="flex justify-between items-center text-slate-800 font-bold">
                    <span>🕊️ Óbitos / Falecimentos:</span>
                    <span class="text-slate-600 font-black">{{ demografia.total_obitos }}</span>
                </div>
                <div class="flex justify-between items-center text-slate-800 font-bold">
                    <span>🎯 Metas Executadas:</span>
                    <span class="text-emerald-700 font-black">{{ demografia.taxa_execucao }}%</span>
                </div>
            </div>
        </div>

        <!-- ZONAS, CÉLULAS E CARGOS -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8 text-xs">
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 space-y-4">
                <h3 class="font-extrabold text-sm text-slate-900 border-b pb-2 flex items-center gap-2">
                    <span>📍</span> Cartografia Ministerial: Zonas e Células Familiares
                </h3>
                <div class="space-y-3">
                    <div>
                        <span class="font-bold text-slate-600 text-[11px] uppercase block mb-1.5">Distribuição por Zonas:</span>
                        <div class="grid grid-cols-2 gap-2">
                            {% for z, qtd in demografia.zonas.items() %}
                            <div class="p-2.5 bg-slate-50 border rounded-xl flex justify-between items-center">
                                <span class="font-semibold text-slate-700 truncate">{{ z }}</span>
                                <span class="bg-indigo-100 text-indigo-900 px-2 py-0.5 rounded-full font-black text-[11px]">{{ qtd }}</span>
                            </div>
                            {% else %}
                            <p class="text-slate-400 italic">Nenhuma zona cadastrada.</p>
                            {% endfor %}
                        </div>
                    </div>

                    <div class="pt-2 border-t">
                        <span class="font-bold text-slate-600 text-[11px] uppercase block mb-1.5">Células Familiares:</span>
                        <div class="flex flex-wrap gap-2">
                            {% for c, qtd in demografia.celulas.items() %}
                            <span class="bg-slate-100 border text-slate-800 px-3 py-1 rounded-xl font-bold flex items-center gap-1.5">
                                <span>🏠 {{ c }}:</span>
                                <b class="text-indigo-900">{{ qtd }} membros</b>
                            </span>
                            {% else %}
                            <p class="text-slate-400 italic">Nenhuma célula registada.</p>
                            {% endfor %}
                        </div>
                    </div>
                </div>
            </div>

            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 space-y-4">
                <h3 class="font-extrabold text-sm text-slate-900 border-b pb-2 flex items-center gap-2">
                    <span>✝️</span> Estatística do Corpo Ministerial & Obreiros
                </h3>
                <div class="grid grid-cols-2 gap-3">
                    {% for cg, qtd in demografia.cargos.items() %}
                    <div class="p-3 bg-slate-50 border rounded-xl flex justify-between items-center">
                        <div>
                            <span class="font-bold text-slate-800 block">{{ cg }}</span>
                            <span class="text-[10px] text-slate-400">Serviço Ministerial</span>
                        </div>
                        <span class="text-base font-black text-indigo-950">{{ qtd }}</span>
                    </div>
                    {% else %}
                    <p class="text-slate-400 italic">Nenhum obreiro registado.</p>
                    {% endfor %}
                </div>
            </div>
        </div>
        {% endif %}

        <!-- ========================================================= -->
        <!-- ABA: ACTOS ECLESIÁSTICOS (CASAMENTOS & ÓBITOS)            -->
        <!-- ========================================================= -->
        {% if aba_ativa == 'actos' %}
        <div class="bg-gradient-to-r from-pink-950 via-slate-900 to-slate-900 text-white p-6 rounded-3xl shadow mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
                <div class="inline-flex items-center gap-2 bg-pink-500/20 text-pink-300 px-3 py-1 rounded-full text-[10px] font-black uppercase mb-1 border border-pink-400/30">
                    <span>💒</span> REGISTO DE ACTOS PASTORAIS & NOTARIAIS
                </div>
                <h2 class="text-2xl font-black">Registo de Casamentos & Registo de Óbitos</h2>
                <p class="text-xs text-pink-200 mt-0.5">{{ congregacao.nome }} • Registo solene dos matrimónios e condolências</p>
            </div>
            <div class="flex gap-3">
                <a href="/secretaria/relatorio-anual" target="_blank" class="px-4 py-2 bg-amber-500 hover:bg-amber-600 text-slate-950 font-black rounded-xl text-xs shadow flex items-center gap-1.5">
                    <span>📄</span><span>Ver no Relatório Anual Oficial</span>
                </a>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 text-xs">
            <div class="space-y-4">
                <div class="bg-white p-6 rounded-2xl shadow-sm border-2 border-pink-200 space-y-4">
                    <h3 class="font-black text-sm uppercase text-pink-950 border-b pb-2 flex items-center gap-2">
                        <span>💍</span> Registar Casamento Celebrado
                    </h3>
                    <form action="/actos/casamento/novo" method="POST" class="space-y-3">
                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <label class="block font-bold text-slate-700 mb-1">Categoria *</label>
                                <select name="tipo" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-bold">
                                    <option value="Jovens">Casamento de Jovens</option>
                                    <option value="Adultos">Casamento de Adultos</option>
                                </select>
                            </div>
                            <div>
                                <label class="block font-bold text-slate-700 mb-1">Data da Cerimónia *</label>
                                <input type="date" name="data_casamento" required class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-bold">
                            </div>
                        </div>
                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <label class="block font-bold text-slate-700 mb-1">Nome do Noivo *</label>
                                <input type="text" name="noivo" required placeholder="Nome completo" class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                            </div>
                            <div>
                                <label class="block font-bold text-slate-700 mb-1">Nome da Noiva *</label>
                                <input type="text" name="noiva" required placeholder="Nome completo" class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                            </div>
                        </div>
                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <label class="block font-bold text-slate-700 mb-1">Pastor / Ministro Oficiante</label>
                                <input type="text" name="ministro" placeholder="Pr. ..." class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                            </div>
                            <div>
                                <label class="block font-bold text-slate-700 mb-1">Regime / Certidão Civil</label>
                                <input type="text" name="certidao" placeholder="Nº de Assento / Registo" class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                            </div>
                        </div>
                        <button type="submit" class="w-full py-3 bg-pink-700 hover:bg-pink-800 text-white font-black rounded-xl shadow cursor-pointer transition">
                            💍 Gravar Registo de Casamento
                        </button>
                    </form>
                </div>

                <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200">
                    <h4 class="font-extrabold text-xs text-slate-800 mb-3 border-b pb-2 flex justify-between items-center">
                        <span>📋 Casamentos Registados</span>
                        <span class="bg-pink-100 text-pink-900 px-2.5 py-0.5 rounded-full font-black">{{ casamentos|length }}</span>
                    </h4>
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-xs">
                            <thead>
                                <tr class="border-b text-slate-500 font-bold">
                                    <th class="py-2 px-1">Data</th>
                                    <th class="py-2 px-1">Noivos</th>
                                    <th class="py-2 px-1">Tipo</th>
                                    <th class="py-2 px-1 text-right">Ação</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for cs in casamentos %}
                                <tr class="border-b hover:bg-slate-50">
                                    <td class="py-2.5 px-1 font-semibold">{{ cs.data_casamento }}</td>
                                    <td class="py-2.5 px-1">
                                        <div class="font-bold text-slate-900">{{ cs.noivo }} & {{ cs.noiva }}</div>
                                        <div class="text-[10px] text-slate-400">Oficiante: {{ cs.ministro or 'Pastor' }}</div>
                                    </td>
                                    <td class="py-2.5 px-1"><span class="bg-pink-50 text-pink-800 px-2 py-0.5 rounded font-bold text-[10px]">{{ cs.tipo }}</span></td>
                                    <td class="py-2.5 px-1 text-right"><a href="/actos/casamento/remover/{{ cs.id }}" onclick="return confirm('Excluir?')" class="text-rose-500 hover:text-rose-700 font-bold text-xs">Excluir</a></td>
                                </tr>
                                {% else %}
                                <tr><td colspan="4" class="py-6 text-center text-slate-400 italic">Nenhum casamento registado no período.</td></tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div class="space-y-4">
                <div class="bg-white p-6 rounded-2xl shadow-sm border-2 border-slate-300 space-y-4">
                    <h3 class="font-black text-sm uppercase text-slate-900 border-b pb-2 flex items-center gap-2">
                        <span>🕊️</span> Registar Óbito / Falecimento
                    </h3>
                    <form action="/actos/obito/novo" method="POST" class="space-y-3">
                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <label class="block font-bold text-slate-700 mb-1">Nome do Irmão(ã) Falecido *</label>
                                <input type="text" name="nome_falecido" required placeholder="Nome completo" class="w-full h-10 px-3 border rounded-xl bg-slate-50 font-bold">
                            </div>
                            <div>
                                <label class="block font-bold text-slate-700 mb-1">Género / Sexo *</label>
                                <select name="genero" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-bold">
                                    <option value="Masculino">Homem</option>
                                    <option value="Feminino">Mulher</option>
                                </select>
                            </div>
                        </div>
                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <label class="block font-bold text-slate-700 mb-1">Categoria Eclesiástica *</label>
                                <select name="categoria" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-bold text-indigo-950">
                                    <option value="Baptizados">Baptizado Adulto</option>
                                    <option value="Juventude">Juventude</option>
                                    <option value="Boa Esperança">Boa Esperança (Criança)</option>
                                    <option value="Novos Convertidos">Novo Convertido</option>
                                    <option value="Diáconos">Diácono / Diaconisa</option>
                                    <option value="Evangelistas">Evangelista</option>
                                    <option value="Presbíteros">Presbítero</option>
                                    <option value="Pastores">Pastor</option>
                                    <option value="Mães Pastoras">Mãe Pastora</option>
                                </select>
                            </div>
                            <div>
                                <label class="block font-bold text-slate-700 mb-1">Data do Falecimento *</label>
                                <input type="date" name="data_falecimento" required class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-bold">
                            </div>
                        </div>
                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <label class="block font-bold text-slate-700 mb-1">Local do Funeral / Cemitério</label>
                                <input type="text" name="local_funeral" placeholder="Ex: Cemitério Municipal" class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                            </div>
                            <div>
                                <label class="block font-bold text-slate-700 mb-1">Contacto da Família</label>
                                <input type="text" name="contacto_familia" placeholder="+258..." class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                            </div>
                        </div>
                        <button type="submit" class="w-full py-3 bg-slate-800 hover:bg-slate-900 text-white font-black rounded-xl shadow cursor-pointer transition">
                            🕊️ Gravar Registo de Óbito
                        </button>
                    </form>
                </div>

                <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200">
                    <h4 class="font-extrabold text-xs text-slate-800 mb-3 border-b pb-2 flex justify-between items-center">
                        <span>📋 Registo de Óbitos no Ano</span>
                        <span class="bg-slate-200 text-slate-800 px-2.5 py-0.5 rounded-full font-black">{{ obitos|length }}</span>
                    </h4>
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-xs">
                            <thead>
                                <tr class="border-b text-slate-500 font-bold">
                                    <th class="py-2 px-1">Data</th>
                                    <th class="py-2 px-1">Falecido</th>
                                    <th class="py-2 px-1">Categoria</th>
                                    <th class="py-2 px-1 text-right">Ação</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for ob in obitos %}
                                <tr class="border-b hover:bg-slate-50">
                                    <td class="py-2.5 px-1 font-semibold">{{ ob.data_falecimento }}</td>
                                    <td class="py-2.5 px-1">
                                        <div class="font-bold text-slate-900">{{ ob.nome_falecido }}</div>
                                        <div class="text-[10px] text-slate-400">Funeral: {{ ob.local_funeral or '---' }}</div>
                                    </td>
                                    <td class="py-2.5 px-1"><span class="bg-slate-100 text-slate-800 px-2 py-0.5 rounded font-bold text-[10px]">{{ ob.categoria }}</span></td>
                                    <td class="py-2.5 px-1 text-right"><a href="/actos/obito/remover/{{ ob.id }}" onclick="return confirm('Excluir?')" class="text-rose-500 hover:text-rose-700 font-bold text-xs">Excluir</a></td>
                                </tr>
                                {% else %}
                                <tr><td colspan="4" class="py-6 text-center text-slate-400 italic">Nenhum óbito registado no período.</td></tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- ========================================================= -->
        <!-- ABA 1: MEMBROS & RELATÓRIOS OFICIAIS                     -->
        <!-- ========================================================= -->
        {% if aba_ativa == 'membros' %}
        <div class="bg-indigo-900 text-white p-5 rounded-2xl shadow mb-6 flex justify-between items-center">
            <div>
                <h2 class="text-xl font-extrabold">👥 Cadastro Geral de Membresia: {{ congregacao.nome }}</h2>
                <p class="text-xs text-indigo-200 mt-1">Registo oficial com geração automática de credenciais e cartões</p>
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
                            <label class="block font-semibold text-slate-600 mb-1">Género / Sexo *</label>
                            <select name="genero" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-bold text-slate-800">
                                <option value="Masculino">Homem (Masculino)</option>
                                <option value="Feminino">Mulher (Feminino)</option>
                            </select>
                        </div>
                    </div>
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Contacto / WhatsApp</label>
                        <input type="text" name="contacto" placeholder="+258..." class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                    </div>
                    <div class="grid grid-cols-3 gap-2">
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Estado Civil *</label>
                            <select name="estado_civil" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-bold text-indigo-900">
                                {% for op in opcoes.get('estado_civil', []) %}
                                <option value="{{ op.valor }}">{{ op.valor }}</option>
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
                                    <div class="text-[10px] text-slate-400">{{ m.genero or 'Homem' }} • {{ m.estado_civil or '---' }} • {{ m.local_residencia or m.bairro or '---' }}</div>
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
        <!-- ABA 2: SECRETARIA & PLANIFICAÇÃO (COM BALANÇO ANUAL)      -->
        <!-- ========================================================= -->
        {% if aba_ativa == 'secretaria' %}
        <div class="bg-indigo-900 text-white p-5 rounded-2xl shadow mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
                <h2 class="text-xl font-extrabold">📋 Secretaria & Planificação: {{ congregacao.nome }}</h2>
                <p class="text-xs text-indigo-200 mt-0.5">Gestão de cronograma, execução de metas e prestação oficial de contas</p>
            </div>
            <div class="flex flex-wrap items-center gap-2.5">
                <a href="/secretaria/balanco" class="px-3.5 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-black rounded-xl text-xs shadow flex items-center gap-1.5 transition">
                    <span>🎯</span><span>Balanço Anual & Questionamentos</span>
                </a>
                <a href="/secretaria/relatorio-anual" target="_blank" class="px-3.5 py-2.5 bg-amber-500 hover:bg-amber-600 text-slate-950 font-black rounded-xl text-xs shadow flex items-center gap-1.5 transition">
                    <span>📄</span><span>Emitir Relatório Oficial (2026)</span>
                </a>
            </div>
        </div>

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
                            <tr><td colspan="4" class="py-8 text-center text-slate-400">Nenhum plano registado.</td></tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- ========================================================= -->
        <!-- ABA 3: CULTOS COM PRESENÇAS                               -->
        <!-- ========================================================= -->
        {% if aba_ativa == 'cultos' %}
        <div class="bg-indigo-900 text-white p-5 rounded-2xl shadow mb-6">
            <h2 class="text-xl font-extrabold">⛪ Registo de Cultos: {{ congregacao.nome }}</h2>
            <p class="text-xs text-indigo-200 mt-1">Estatística oficial discriminada de presenças</p>
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
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="font-bold text-blue-800">📊 Total de Presentes</label>
                            <input type="number" name="total_presentes" value="0" min="0" class="w-full h-9 px-2 border-2 border-blue-400 rounded bg-blue-50 font-extrabold text-center text-blue-900 text-sm">
                        </div>
                        <div>
                            <label class="font-bold text-amber-700">🔥 Vidas no Altar (Apelos)</label>
                            <input type="number" name="apelos" value="0" min="0" class="w-full h-9 px-2 border-2 border-amber-300 rounded bg-amber-50 font-bold text-center">
                        </div>
                    </div>
                    <div><label class="block font-semibold mb-1">Pregador</label><input type="text" name="pregador" placeholder="Nome do Pregador" class="w-full h-10 px-3 border rounded-xl bg-slate-50"></div>
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
                                <th class="py-2.5 px-2 text-center">Total</th>
                                <th class="py-2.5 px-2 text-center">Apelos</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for c in cultos %}
                            <tr class="border-b border-slate-100 hover:bg-slate-50">
                                <td class="py-3 px-2 font-semibold">{{ c.data_culto }}</td>
                                <td class="py-3 px-2 font-bold text-slate-800">{{ c.tipo_culto }}<div class="text-[11px] text-slate-400">{{ c.pregador or '---' }}</div></td>
                                <td class="py-3 px-2 text-center font-black text-blue-900 bg-blue-50/50 rounded-lg">{{ c.total_presentes }}</td>
                                <td class="py-3 px-2 text-center font-black text-amber-700">{{ c.apelos }}</td>
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
                    <thead><tr class="border-b-2 border-slate-200 text-slate-500"><th class="py-3 px-3">Nome</th><th class="py-3 px-3">Contacto</th><th class="py-3 px-3">Bairro</th></tr></thead>
                    <tbody>
                        {% for c in convertidos %}
                        <tr class="border-b border-slate-100 hover:bg-slate-50"><td class="py-3 px-3 font-bold">{{ c.nome }}</td><td class="py-3 px-3">{{ c.telefone or '---' }}</td><td class="py-3 px-3">{{ c.bairro or '---' }}</td></tr>
                        {% else %}
                        <tr><td colspan="3" class="py-8 text-center text-slate-400">Nenhum convertido registado.</td></tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
        {% endif %}

        <!-- ========================================================= -->
        <!-- ABA 5: DASHBOARD FINANCEIRO (EXCLUSIVO TESOURARIA)        -->
        <!-- ========================================================= -->
        {% if aba_ativa == 'financas' and usuario_logado.perfil in ['tesoureiro', 'admin'] %}
        <div class="bg-emerald-950 text-white p-6 rounded-2xl shadow mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
                <h2 class="text-2xl font-black">📊 Dashboard Financeiro: {{ congregacao.nome }}</h2>
                <p class="text-xs text-emerald-300 mt-1">Acesso exclusivo da Tesouraria e Administração</p>
            </div>
            <div class="text-right flex items-center gap-3">
                <span class="text-2xl font-black text-white">{{ "%.2f"|format(kpis.saldo_caixa) }} MT</span>
                <a href="/?aba=tesouraria" class="px-3.5 py-2 bg-amber-500 hover:bg-amber-600 text-slate-950 font-black rounded-xl text-xs shadow">Lançamentos</a>
            </div>
        </div>
        {% endif %}

        <!-- ========================================================= -->
        <!-- ABA 6: CAIXA & TESOURARIA (EXCLUSIVO TESOURARIA)          -->
        <!-- ========================================================= -->
        {% if aba_ativa == 'tesouraria' and usuario_logado.perfil in ['tesoureiro', 'admin'] %}
        <div class="bg-amber-950 text-white p-6 rounded-2xl shadow mb-6 flex justify-between items-center">
            <div>
                <div class="inline-flex items-center gap-2 bg-amber-500/20 text-amber-300 px-3 py-1 rounded-full text-[10px] font-black uppercase mb-1 border border-amber-400/30">
                    <span>🔐</span> ACESSO EXCLUSIVO • TESOURARIA
                </div>
                <h2 class="text-2xl font-black">Lançamentos de Caixa & Movimentação Financeira</h2>
            </div>
            <div class="text-2xl font-black text-white">{{ "%.2f"|format(kpis.saldo_caixa) }} MT</div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 text-xs">
            <div class="lg:col-span-5 bg-white p-6 rounded-2xl shadow-sm border-2 border-amber-300">
                <h3 class="font-extrabold text-base mb-4 border-b pb-2 text-amber-950">✍️ Lançar Entrada ou Saída</h3>
                <form action="/financas/caixa/novo" method="POST" class="space-y-4">
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block font-bold mb-1">Tipo *</label>
                            <select name="tipo" class="w-full h-11 px-2 border rounded-xl font-bold"><option value="Entrada">🟢 Entrada (+)</option><option value="Saída">🔴 Saída (-)</option></select>
                        </div>
                        <div>
                            <label class="block font-bold mb-1">Conta *</label>
                            <select name="conta" class="w-full h-11 px-2 border rounded-xl font-bold"><option value="Caixa Físico">💵 Caixa Físico</option><option value="Conta Bancária">🏦 Banco</option></select>
                        </div>
                    </div>
                    <div class="grid grid-cols-2 gap-3">
                        <div><label class="block font-bold mb-1">Data *</label><input type="date" name="data_movimento" required class="w-full h-11 px-2 border rounded-xl"></div>
                        <div><label class="block font-bold mb-1">Valor (MZN) *</label><input type="number" step="0.01" name="valor" required placeholder="Ex: 1000.00" class="w-full h-11 px-3 border rounded-xl font-bold"></div>
                    </div>
                    <div><label class="block font-bold mb-1">Categoria / Descrição *</label><input type="text" name="descricao" required placeholder="Ex: Dízimos / Credelec / Água" class="w-full h-11 px-3 border rounded-xl"></div>
                    <button type="submit" class="w-full py-3.5 bg-emerald-700 hover:bg-emerald-800 text-white font-black rounded-xl shadow cursor-pointer text-sm">
                        💾 Confirmar Movimento
                    </button>
                </form>
            </div>

            <div class="lg:col-span-7 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">📋 Últimos Movimentos ({{ caixa|length }})</h3>
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs">
                        <thead><tr class="border-b text-slate-500 font-bold"><th class="py-2">Data</th><th class="py-2">Conta</th><th class="py-2">Descrição</th><th class="py-2 text-right">Valor</th></tr></thead>
                        <tbody>
                            {% for cx in caixa[:15] %}
                            <tr class="border-b hover:bg-slate-50">
                                <td class="py-2.5 text-slate-600">{{ cx.data_movimento }}</td>
                                <td class="py-2.5 font-bold">{{ cx.conta }}</td>
                                <td class="py-2.5 font-bold">{{ cx.categoria }}<div class="text-[10px] text-slate-400 font-normal">{{ cx.descricao }}</div></td>
                                <td class="py-2.5 text-right font-black {% if cx.tipo == 'Entrada' %}text-emerald-700{% else %}text-rose-700{% endif %}">
                                    {% if cx.tipo == 'Entrada' %}+{% else %}-{% endif %} {{ "%.2f"|format(cx.valor or 0) }} MT
                                </td>
                            </tr>
                            {% else %}
                            <tr><td colspan="4" class="py-6 text-center text-slate-400">Nenhum lançamento efetuado.</td></tr>
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
                <h2 class="text-2xl font-black">📖 Dashboard de Doutrina: {{ congregacao.nome }}</h2>
                <p class="text-xs text-amber-300 mt-1">Formação bíblica de candidatos ao baptismo e novos convertidos</p>
            </div>
            <span class="text-2xl font-black text-emerald-400">✅ {{ doutrina|length }} Formandos</span>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 text-xs">
            <div class="lg:col-span-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">🎓 Inscrever Formando com Login</h3>
                <form action="/doutrina/novo" method="POST" class="space-y-3">
                    <div><label class="block font-semibold mb-1">Nome Completo *</label><input type="text" name="nome_aluno" required class="w-full h-10 px-3 border rounded-xl bg-slate-50 font-bold"></div>
                    <div><label class="block font-semibold mb-1">Classe *</label><input type="text" name="classe" value="Classe I - Primeiros Passos" class="w-full h-10 px-3 border rounded-xl bg-slate-50 font-bold"></div>
                    <div><label class="block font-semibold mb-1">Instrutor / Mentor</label><input type="text" name="professor" placeholder="Pr. / Diác." class="w-full h-10 px-3 border rounded-xl bg-slate-50"></div>
                    <div class="grid grid-cols-2 gap-2">
                        <div><label class="block font-semibold mb-1">Utilizador</label><input type="text" name="usuario" placeholder="Ex: anselmo" class="w-full h-8 px-2 border rounded font-bold"></div>
                        <div><label class="block font-semibold mb-1">Palavra-passe</label><input type="text" name="senha" value="123456" class="w-full h-8 px-2 border rounded font-bold"></div>
                    </div>
                    <button type="submit" class="w-full py-3 bg-amber-700 hover:bg-amber-800 text-white font-bold rounded-xl shadow cursor-pointer">
                        Gravar Inscrição & Credenciais
                    </button>
                </form>
            </div>

            <div class="lg:col-span-8 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">📋 Formandos Registados ({{ doutrina|length }})</h3>
                <table class="w-full text-left text-xs">
                    <thead><tr class="border-b text-slate-500 font-bold"><th class="py-2">Formando & Acesso</th><th class="py-2">Classe</th><th class="py-2">Instrutor</th></tr></thead>
                    <tbody>
                        {% for d in doutrina %}
                        <tr class="border-b hover:bg-slate-50">
                            <td class="py-2.5 font-bold">{{ d.nome_aluno }}<div class="text-[10px] text-slate-400">User: {{ d.usuario }}</div></td>
                            <td class="py-2.5">{{ d.classe }}</td>
                            <td class="py-2.5 text-slate-600">{{ d.professor or 'Pastor' }}</td>
                        </tr>
                        {% else %}
                        <tr><td colspan="3" class="py-6 text-center text-slate-400">Nenhum formando inscrito.</td></tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
        {% endif %}

    </main>

</body>
</html>
"""

env.parse(dash_completo)
with open(os.path.join('templates', 'dashboard.html'), 'w', encoding='utf-8') as f:
    f.write(dash_completo)
print("✓ templates/dashboard.html reconstruído e validado com sucesso!")

# =============================================================================
# 5. ATUALIZAR TEMPLATES/RELATORIO_ANUAL_MODELO.HTML COM O LOGO E SEM 'THAVANE'
# =============================================================================
relatorio_template_html = """<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <title>Relatório Anual Oficial - {{ congregacao.nome }}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @media print {
            .no-print { display: none !important; }
            body { background: white !important; padding: 0 !important; color: black !important; }
            @page { size: A4 portrait; margin: 12mm 15mm; }
            .page-break { page-break-before: always; }
        }
        table, th, td { border: 1px solid #1e293b !important; }
    </style>
</head>
<body class="bg-slate-100 p-6 font-sans text-slate-900 text-xs leading-normal">

    <div class="no-print max-w-4xl mx-auto mb-6 flex justify-between items-center bg-white p-4 rounded-2xl shadow border">
        <a href="/?aba=secretaria" class="px-4 py-2 bg-slate-800 text-white rounded-xl font-bold text-xs shadow hover:bg-slate-900">
            ← Voltar à Secretaria
        </a>
        <button onclick="window.print()" class="px-6 py-2.5 bg-indigo-700 hover:bg-indigo-800 text-white font-black rounded-xl shadow cursor-pointer text-xs">
            🖨️ Imprimir / Guardar em PDF
        </button>
    </div>

    <div class="max-w-4xl mx-auto bg-white p-10 rounded-2xl shadow-xl print:shadow-none print:p-0 print:border-none border border-slate-300 space-y-6">

        <!-- CABEÇALHO COM O LOGO OFICIAL -->
        <div class="flex justify-between items-start border-b-2 border-slate-900 pb-4">
            <div class="w-24 h-24 flex items-center justify-center shrink-0">
                {% include 'logo_ad.html' %}
            </div>

            <div class="text-center flex-1 px-4 space-y-0.5">
                <h1 class="font-black text-sm uppercase tracking-wide text-slate-950">
                    IGREJA EVANGÉLICA ASSEMBLEIA DE DEUS EM MOÇAMBIQUE
                </h1>
                <p class="text-[10px] italic font-semibold text-slate-600 font-serif">
                    "Quando orardes, lembrai-vos de Moçambique! Remember Mozambique when you pray"
                </p>
                <p class="text-[11px] font-bold uppercase text-slate-800">
                    PROVÍNCIA DE {{ congregacao.provincia|upper }} • DISTRITO DE {{ congregacao.distrito|upper }} • {{ congregacao.nome|upper }}
                </p>
                <div class="pt-1">
                    <span class="inline-block px-4 py-1 bg-slate-900 text-white font-black text-xs uppercase tracking-widest rounded">
                        RELATÓRIO ANUAL OFICIAL
                    </span>
                </div>
            </div>

            <div class="w-48 text-right text-[10px] space-y-2 shrink-0 pt-2">
                <p class="font-bold">Visto Do Pastor</p>
                <p class="border-b border-slate-600 pb-0.5 text-center text-slate-400">Assinatura</p>
                <p class="text-center">_____/_____/2026</p>
            </div>
        </div>

        <div class="space-y-2">
            <h2 class="font-black text-xs uppercase bg-slate-100 p-1.5 border border-slate-300">
                1. INTRODUÇÃO
            </h2>
            <p class="text-justify leading-relaxed text-slate-800">
                Graça e Paz do nosso Senhor Jesus Cristo, Amem! Saudamos o reverendíssimo Pastor Presidente Provincial, membros da Direcção Executiva Provincial, Conselho Pastoral, obreiros no geral e a todos os presentes. Com a permissão do presídio, a Secretaria da Igreja apresenta o resumo oficial das actividades desenvolvidas na <b>Assembleia de Deus ({{ congregacao.nome }})</b>.
            </p>
        </div>

        <div class="space-y-2">
            <h2 class="font-black text-xs uppercase bg-slate-100 p-1.5 border border-slate-300">
                2. RESUMO ESTATÍSTICO DE MEMBRESIA & ACTOS
            </h2>
            <div class="grid grid-cols-4 gap-2 text-center">
                <div class="p-2 border font-bold">Total Almas: {{ demografia.total_almas }}</div>
                <div class="p-2 border font-bold">Membros: {{ demografia.membros_cadastrados }}</div>
                <div class="p-2 border font-bold">Casamentos: {{ demografia.total_casamentos }}</div>
                <div class="p-2 border font-bold">Óbitos: {{ demografia.total_obitos }}</div>
            </div>
        </div>

        <div class="pt-8 flex justify-between items-end">
            <div class="text-xs">
                <p>{{ congregacao.distrito }}, aos {{ rel.data_dia if rel else '18' }} de {{ rel.data_mes if rel else 'Outubro' }} de 2026</p>
            </div>
            <div class="text-center w-64 space-y-1">
                <p class="font-extrabold text-xs">O Secretário da Igreja</p>
                <div class="border-b border-slate-700 w-48 mx-auto my-2"></div>
                <p class="text-[10px] text-slate-500 font-bold uppercase">Secretaria da Igreja • {{ congregacao.nome }}</p>
            </div>
        </div>

    </div>

</body>
</html>
"""

env.parse(relatorio_template_html)
with open(os.path.join('templates', 'relatorio_anual_modelo.html'), 'w', encoding='utf-8') as f:
    f.write(relatorio_template_html)
print("✓ templates/relatorio_anual_modelo.html atualizado com o logotipo oficial e sem Thavane!")

print("=" * 80)
print(">>> INSTALAÇÃO NACIONAL CONCLUÍDA COM SUCESSO! ZERO ERROS DE JINJA2! <<<")
print("=" * 80)