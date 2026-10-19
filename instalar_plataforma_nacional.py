import os
import sys
import jinja2

print("=" * 80)
print("A CONFIGURAR PLATAFORMA NACIONAL MULTI-CONGREGAÇÃO DA ASSEMBLEIA DE DEUS...")
print("=" * 80)

os.makedirs('templates', exist_ok=True)
env = jinja2.Environment()

# =============================================================================
# 1. ATUALIZAR O APP.PY COM MULTI-CONGREGAÇÃO, 36 DISTRITOS E PERFIS RESTRITOS
# =============================================================================
app_py_code = '''import os
import sqlite3
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'iead_mz_plataforma_nacional_2026')

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

# ESTRUTURA TERRITORIAL OFICIAL
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
        f"""CREATE TABLE IF NOT EXISTS provincias (id {pk}, nome TEXT UNIQUE);""",
        f"""CREATE TABLE IF NOT EXISTS distritos (id {pk}, provincia_id INT, nome TEXT);""",
        f"""CREATE TABLE IF NOT EXISTS congregacoes (
            id {pk}, nome TEXT, provincia TEXT, distrito TEXT, bairro TEXT, pastor_responsavel TEXT, criado_em TEXT
        );""",
        f"""CREATE TABLE IF NOT EXISTS usuarios_sistema (
            id {pk}, nome TEXT, usuario TEXT UNIQUE, senha TEXT, 
            nivel TEXT, perfil TEXT, congregacao_id INT, provincia TEXT, distrito TEXT, criado_em TEXT
        );""",
        f"""CREATE TABLE IF NOT EXISTS membros (id {pk}, congregacao_id INT, nome TEXT);""",
        f"""CREATE TABLE IF NOT EXISTS planificacao (id {pk}, congregacao_id INT, actividade TEXT);""",
        f"""CREATE TABLE IF NOT EXISTS novos_convertidos (id {pk}, congregacao_id INT, nome TEXT);""",
        f"""CREATE TABLE IF NOT EXISTS cultos (id {pk}, congregacao_id INT, data_culto TEXT);""",
        f"""CREATE TABLE IF NOT EXISTS caixa (id {pk}, congregacao_id INT, valor REAL);""",
        f"""CREATE TABLE IF NOT EXISTS doutrina (id {pk}, congregacao_id INT, nome_aluno TEXT);""",
        f"""CREATE TABLE IF NOT EXISTS casamentos (id {pk}, congregacao_id INT, noivo TEXT);""",
        f"""CREATE TABLE IF NOT EXISTS obitos (id {pk}, congregacao_id INT, nome_falecido TEXT);""",
        f"""CREATE TABLE IF NOT EXISTS opcoes_sistema (id {pk}, categoria TEXT, valor TEXT);""",
        f"""CREATE TABLE IF NOT EXISTS progresso_licoes (
            id {pk}, aluno_id INT, licao_id TEXT, resumo_aluno TEXT, nota_teste REAL DEFAULT 0, status TEXT, criado_em TEXT
        );""",
        f"""CREATE TABLE IF NOT EXISTS duvidas_alunos (
            id {pk}, aluno_id INT, licao_id TEXT, pergunta TEXT, resposta_sistema TEXT, resposta_professor TEXT, professor_nome TEXT, criado_em TEXT
        );""",
        f"""CREATE TABLE IF NOT EXISTS balanco_anual (
            id {pk}, congregacao_id INT, ano INT, constrangimento_1 TEXT, constrangimento_2 TEXT, constrangimento_3 TEXT,
            perspectiva_1 TEXT, perspectiva_2 TEXT, perspectiva_3 TEXT, atualizado_em TEXT
        );"""
    ]
    for sql in tabelas:
        try:
            cur.execute(sql)
            if hasattr(conn, 'commit'): conn.commit()
        except: pass

    # Garantir colunas essenciais
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

        if hasattr(conn, 'commit'): conn.commit()
    conn.close()

    # Preencher dados geográficos e congregação inicial
    m = "%s" if is_pg else "?"
    c_padrao = consultar_um("SELECT id FROM congregacoes WHERE id = 1")
    if not c_padrao:
        sql_c = f"""INSERT INTO congregacoes (id, nome, provincia, distrito, bairro, pastor_responsavel, criado_em)
                    VALUES (1, 'Sede Regional de Chicuque', 'Inhambane', 'Maxixe (Cidade/Distrito)', 'Chicuque', 'Pastor Presidente', {m})"""
        executar_comando(sql_c, (datetime.now().strftime('%Y-%m-%d %H:%M'),))

    # Criar perfis institucionais padrão
    usuarios_padrao = [
        ('Administrador Geral', 'admin', 'admin123', 'geral', 'admin', 1, 'Inhambane', 'Maxixe (Cidade/Distrito)'),
        ('Pastor Presidente', 'pastor', 'pastor123', 'geral', 'pastor', 1, 'Inhambane', 'Maxixe (Cidade/Distrito)'),
        ('Secretaria Geral', 'secretaria', 'sec123', 'secretaria', 'secretario', 1, 'Inhambane', 'Maxixe (Cidade/Distrito)'),
        ('Tesouraria da Igreja', 'tesouraria', 'tesouro123', 'tesouraria', 'tesoureiro', 1, 'Inhambane', 'Maxixe (Cidade/Distrito)'),
        ('Direcção Distrital Maxixe', 'distrital', 'distrito123', 'distrital', 'distrital', 1, 'Inhambane', 'Maxixe (Cidade/Distrito)'),
        ('Superintendência Provincial', 'provincial', 'provincia123', 'provincial', 'provincial', 1, 'Inhambane', 'Todos')
    ]
    for n, u, s, niv, perf, cid, prov, dist in usuarios_padrao:
        if not consultar_um(f"SELECT id FROM usuarios_sistema WHERE usuario = {m}", (u,)):
            sql_u = f"""INSERT INTO usuarios_sistema (nome, usuario, senha, nivel, perfil, congregacao_id, provincia, distrito, criado_em)
                        VALUES ({m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m})"""
            executar_comando(sql_u, (n, u, s, niv, perf, cid, prov, dist, datetime.now().strftime('%Y-%m-%d %H:%M')))

inicializar_banco()

# CONTROLO DE SESSÃO E DECORADORES DE ACESSO
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
        perfil = session.get('usuario_perfil', '')
        if perfil not in ['tesoureiro', 'admin']:
            flash("Acesso restrito! O módulo financeiro é exclusivo da Tesouraria.")
            return redirect('/?aba=dashboard')
        return f(*args, **kwargs)
    return decorado

# CONTEXTO GLOBAL INJETADO NOS TEMPLATES
@app.context_processor
def injetar_global():
    u_id = session.get('usuario_id')
    user = consultar_um("SELECT * FROM usuarios_sistema WHERE id = %s" % u_id) if u_id else None
    cid = user.get('congregacao_id', 1) if user else 1
    congregacao_atual = consultar_um("SELECT * FROM congregacoes WHERE id = %s" % cid) or {'nome': 'Assembleia de Deus', 'distrito': 'Maxixe', 'provincia': 'Inhambane'}

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

    # Demografia
    h = len([x for x in membros if str(x.get('genero') or '').lower() in ['masculino', 'homem', 'h']])
    mulh = len(membros) - h
    cri = len([x for x in membros if str(x.get('estado_civil') or '').lower() == 'criança' or 'esperança' in str(x.get('departamento') or '').lower()])
    jov = len([x for x in membros if 'jov' in str(x.get('departamento') or '').lower() or 'jovem' in str(x.get('cargo') or '').lower()])
    adult = max(0, len(membros) - cri - jov)
    bat = len([x for x in membros if x.get('data_batismo')])
    nao_bat = len(membros) - bat

    # Finanças
    tin = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Entrada'])
    tout = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Saída'])

    return {
        'usuario_logado': user,
        'congregacao': congregacao_atual,
        'divisao_territorial': DIVISAO_TERRITORIAL,
        'membros': membros, 'planificacoes': planos, 'cultos': cultos,
        'convertidos': convertidos, 'caixa': caixa, 'doutrina': doutrina,
        'casamentos': casamentos, 'obitos': obitos, 'duvidas_pendentes': duvidas_pendentes,
        'opcoes': opcoes_map,
        'demografia': {
            'total_almas': len(membros) + len(convertidos),
            'membros_cadastrados': len(membros),
            'homens': h, 'mulheres': mulh,
            'criancas': cri, 'jovens': jov, 'adultos': adult,
            'batizados': bat, 'nao_batizados': nao_bat,
            'novos_convertidos': len(convertidos),
            'total_casamentos': len(casamentos), 'total_obitos': len(obitos)
        },
        'kpis': {
            'saldo_caixa': tin - tout,
            'total_entradas': tin,
            'total_saidas': tout
        }
    }

# =============================================================================
# ROTAS DE AUTENTICAÇÃO E PERFIS
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
# ÁREA DE CONSOLIDAÇÃO DISTRITAL E PROVINCIAL (AGREGAÇÃO ESTATÍSTICA)
# =============================================================================
@app.route('/distrital/dashboard')
@login_obrigatorio
def distrital_dashboard():
    user = session.get('usuario_id')
    u = consultar_um("SELECT * FROM usuarios_sistema WHERE id = %s" % user)
    distrito = u.get('distrito', 'Maxixe (Cidade/Distrito)')

    # Agregar todas as congregações pertencentes a este distrito
    m = "%s" if DATABASE_URL else "?"
    congs = consultar_todos(f"SELECT * FROM congregacoes WHERE distrito = {m}", (distrito,))
    c_ids = [str(c['id']) for c in congs] or ['0']
    in_clause = ",".join(c_ids)

    total_membros = consultar_um(f"SELECT COUNT(*) as t FROM membros WHERE congregacao_id IN ({in_clause})")['t']
    total_convertidos = consultar_um(f"SELECT COUNT(*) as t FROM novos_convertidos WHERE congregacao_id IN ({in_clause})")['t']
    total_casamentos = consultar_um(f"SELECT COUNT(*) as t FROM casamentos WHERE congregacao_id IN ({in_clause})")['t']
    total_obitos = consultar_um(f"SELECT COUNT(*) as t FROM obitos WHERE congregacao_id IN ({in_clause})")['t']
    total_cultos = consultar_um(f"SELECT COUNT(*) as t FROM cultos WHERE congregacao_id IN ({in_clause})")['t']

    return render_template(
        'distrital_dashboard.html',
        distrito=distrito,
        congregações=congs,
        totais={'membros': total_membros, 'convertidos': total_convertidos, 'casamentos': total_casamentos, 'obitos': total_obitos, 'cultos': total_cultos}
    )

@app.route('/provincial/dashboard')
@login_obrigatorio
def provincial_dashboard():
    user = session.get('usuario_id')
    u = consultar_um("SELECT * FROM usuarios_sistema WHERE id = %s" % user)
    provincia = u.get('provincia', 'Inhambane')

    m = "%s" if DATABASE_URL else "?"
    congs = consultar_todos(f"SELECT * FROM congregacoes WHERE provincia = {m}", (provincia,))
    c_ids = [str(c['id']) for c in congs] or ['0']
    in_clause = ",".join(c_ids)

    total_membros = consultar_um(f"SELECT COUNT(*) as t FROM membros WHERE congregacao_id IN ({in_clause})")['t']
    total_convertidos = consultar_um(f"SELECT COUNT(*) as t FROM novos_convertidos WHERE congregacao_id IN ({in_clause})")['t']
    total_casamentos = consultar_um(f"SELECT COUNT(*) as t FROM casamentos WHERE congregacao_id IN ({in_clause})")['t']
    total_obitos = consultar_um(f"SELECT COUNT(*) as t FROM obitos WHERE congregacao_id IN ({in_clause})")['t']

    return render_template(
        'provincial_dashboard.html',
        provincia=provincia,
        congregações=congs,
        totais={'membros': total_membros, 'convertidos': total_convertidos, 'casamentos': total_casamentos, 'obitos': total_obitos}
    )

# -------------------------------------------------------------
# DEMAIS ROTAS DA CONGREGAÇÃO LOCAL PROTEGIDAS POR LOGIN
# -------------------------------------------------------------
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

# Bloqueio estrito da tesouraria
@app.route('/financas/caixa/novo', methods=['POST'])
@login_obrigatorio
@apenas_tesouraria
def caixa_gravar():
    fd = request.form
    tipo = fd.get('tipo', 'Entrada').strip()
    conta = fd.get('conta', 'Caixa Físico').strip()
    try: val = float(fd.get('valor') or 0)
    except: val = 0.0
    dt = fd.get('data_movimento', datetime.now().strftime('%Y-%m-%d')).strip()
    desc = fd.get('descricao', '').strip()
    destino_tipo = fd.get('destino_tipo', 'Igreja Geral').strip()
    depto = fd.get('departamento', 'Geral').strip()
    proposito = fd.get('proposito', '').strip()
    cid = session.get('congregacao_id', 1)

    if tipo == 'Entrada':
        categoria = fd.get('categoria', 'Dízimos') if destino_tipo == 'Igreja Geral' else f"Entrada: {depto}"
    else:
        categoria = fd.get('categoria_saida_geral', 'Despesa') if destino_tipo == 'Igreja Geral' else f"Saída: {depto}"

    m = "%s" if DATABASE_URL else "?"
    sql = f"""INSERT INTO caixa (congregacao_id, tipo, categoria, valor, descricao, data_movimento, conta, destino_tipo, departamento, proposito, criado_em)
              VALUES ({m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m})"""
    executar_comando(sql, (cid, tipo, categoria, val, desc, dt, conta, destino_tipo, depto, proposito, datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=tesouraria')

# Inscrição de Congregação
@app.route('/congregacao/nova', methods=['POST'])
@login_obrigatorio
def congregacao_nova():
    fd = request.form
    nome = fd.get('nome', '').strip()
    prov = fd.get('provincia', 'Inhambane').strip()
    dist = fd.get('distrito', 'Maxixe (Cidade/Distrito)').strip()
    bairro = fd.get('bairro', '').strip()
    past = fd.get('pastor', '').strip()
    m = "%s" if DATABASE_URL else "?"
    sql = f"INSERT INTO congregacoes (nome, provincia, distrito, bairro, pastor_responsavel, criado_em) VALUES ({m}, {m}, {m}, {m}, {m}, {m})"
    executar_comando(sql, (nome, prov, dist, bairro, past, datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=configuracoes')

# Registo de Membros com isolamento por congregação
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

@app.route('/secretaria/planificacao/nova', methods=['POST'])
@login_obrigatorio
def secretaria_gravar():
    fd = request.form
    cid = session.get('congregacao_id', 1)
    m = "%s" if DATABASE_URL else "?"
    sql = f"INSERT INTO planificacao (congregacao_id, actividade, titulo, departamento, tipo_evento, data_prevista, status, criado_em) VALUES ({m}, {m}, {m}, {m}, {m}, {m}, 'Planeado', {m})"
    executar_comando(sql, (cid, fd.get('actividade'), fd.get('actividade'), fd.get('departamento'), fd.get('tipo_evento'), fd.get('data_prevista'), datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=secretaria')

@app.route('/actos/casamento/novo', methods=['POST'])
@login_obrigatorio
def actos_casamento():
    fd = request.form
    cid = session.get('congregacao_id', 1)
    m = "%s" if DATABASE_URL else "?"
    sql = f"INSERT INTO casamentos (congregacao_id, tipo, noivo, noiva, data_casamento, ministro, regime, criado_em) VALUES ({m}, {m}, {m}, {m}, {m}, {m}, {m}, {m})"
    executar_comando(sql, (cid, fd.get('tipo'), fd.get('noivo'), fd.get('noiva'), fd.get('data_casamento'), fd.get('ministro'), fd.get('regime'), datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=actos')

@app.route('/actos/obito/novo', methods=['POST'])
@login_obrigatorio
def actos_obito():
    fd = request.form
    cid = session.get('congregacao_id', 1)
    m = "%s" if DATABASE_URL else "?"
    sql = f"INSERT INTO obitos (congregacao_id, nome_falecido, genero, categoria, data_falecimento, local_funeral, criado_em) VALUES ({m}, {m}, {m}, {m}, {m}, {m}, {m})"
    executar_comando(sql, (cid, fd.get('nome_falecido'), fd.get('genero'), fd.get('categoria'), fd.get('data_falecimento'), fd.get('local_funeral'), datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=actos')

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

# Portal do Aluno
@app.route('/ensino/login')
def portal_login():
    return redirect('/login')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
'''

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_py_code)
print("✓ app.py: Arquitetura multi-congregação, RBAC e 36 distritos configurados!")

# =============================================================================
# 2. CRIAR A NOVA TELA DE LOGIN INSTITUCIONAL
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
        
        <!-- BRASÃO E CABEÇALHO NACIONAL -->
        <div class="text-center space-y-2">
            <div class="w-20 h-20 mx-auto rounded-full bg-slate-900 text-amber-400 border-2 border-amber-400 flex flex-col items-center justify-center p-1 shadow-lg">
                <span class="text-[6px] font-black uppercase tracking-tighter">ASSEMBLEIA DE DEUS</span>
                <span class="text-2xl font-black">AΩ</span>
                <span class="text-[6px] font-bold">MOÇAMBIQUE</span>
            </div>
            <h1 class="text-lg font-black uppercase text-slate-900 tracking-wide">
                ASSEMBLEIA DE DEUS
            </h1>
            <p class="text-[11px] font-bold text-amber-700 uppercase">
                Sistema Integrado de Gestão Eclesiástica
            </p>
            <p class="text-[10px] italic text-slate-400">
                "Quando orardes, lembrai-vos de Moçambique!"
            </p>
        </div>

        {% if erro %}
        <div class="p-3 bg-rose-50 border-2 border-rose-300 rounded-xl text-rose-800 text-xs font-bold text-center">
            {{ erro }}
        </div>
        {% endif %}

        <!-- FORMULÁRIO DE ACESSO -->
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

        <!-- GUIA RÁPIDO DE PERFIS INSTITUCIONAIS -->
        <div class="border-t border-slate-200 pt-3 text-[10px] text-slate-500 space-y-1">
            <span class="font-bold text-slate-700 block">Acessos Configuráveis por Função:</span>
            <div class="grid grid-cols-2 gap-1 text-[9px]">
                <p>• <b>admin:</b> Acesso total</p>
                <p>• <b>tesouraria:</b> Caixa exclusivo</p>
                <p>• <b>secretaria:</b> Fichas e atas</p>
                <p>• <b>distrital:</b> Dados distritais</p>
                <p>• <b>provincial:</b> Consolidação</p>
                <p>• <b>pastor:</b> Direção local</p>
            </div>
        </div>

    </div>

</body>
</html>
"""

env.parse(login_html)
with open(os.path.join('templates', 'login.html'), 'w', encoding='utf-8') as f:
    f.write(login_html)
print("✓ templates/login.html criado com sucesso!")

# =============================================================================
# 3. CRIAR DASHBOARD DISTRITAL (COMPILADOR ESTATÍSTICO DO DISTRITO)
# =============================================================================
distrital_html = """<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <title>Gabinete Distrital - Assembleia de Deus</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-100 p-6 font-sans text-slate-800 text-xs">
    <div class="max-w-6xl mx-auto space-y-6">
        
        <div class="bg-slate-900 text-white p-6 rounded-3xl shadow flex justify-between items-center">
            <div>
                <span class="bg-amber-400 text-slate-950 px-3 py-1 rounded-full text-[10px] font-black uppercase">
                    Direcção Distrital
                </span>
                <h1 class="text-2xl font-black mt-1">Distrito de {{ distrito }}</h1>
                <p class="text-xs text-slate-300">Relatório Compilado de todas as congregações da Assembleia de Deus neste distrito</p>
            </div>
            <a href="/logout" class="px-4 py-2 bg-rose-600 text-white font-bold rounded-xl shadow">Sair</a>
        </div>

        <!-- TOTAIS AGREGADOS DO DISTRITO -->
        <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div class="bg-white p-4 rounded-2xl shadow border text-center">
                <span class="text-slate-400 font-bold block text-[10px]">MEMBROS NO DISTRITO</span>
                <span class="text-2xl font-black text-indigo-950">{{ totais.membros }}</span>
            </div>
            <div class="bg-white p-4 rounded-2xl shadow border text-center">
                <span class="text-slate-400 font-bold block text-[10px]">NOVOS CONVERTIDOS</span>
                <span class="text-2xl font-black text-emerald-700">{{ totais.convertidos }}</span>
            </div>
            <div class="bg-white p-4 rounded-2xl shadow border text-center">
                <span class="text-slate-400 font-bold block text-[10px]">CASAMENTOS NO ANO</span>
                <span class="text-2xl font-black text-pink-700">{{ totais.casamentos }}</span>
            </div>
            <div class="bg-white p-4 rounded-2xl shadow border text-center">
                <span class="text-slate-400 font-bold block text-[10px]">ÓBITOS NO ANO</span>
                <span class="text-2xl font-black text-slate-600">{{ totais.obitos }}</span>
            </div>
            <div class="bg-white p-4 rounded-2xl shadow border text-center">
                <span class="text-slate-400 font-bold block text-[10px]">CULTOS REALIZADOS</span>
                <span class="text-2xl font-black text-blue-700">{{ totais.cultos }}</span>
            </div>
        </div>

        <!-- LISTA DAS CONGREGAÇÕES SUBORDINADAS -->
        <div class="bg-white p-6 rounded-3xl shadow border space-y-3">
            <h2 class="font-extrabold text-sm uppercase text-slate-900 border-b pb-2">Congregações Jurisdicionadas ({{ congregações|length }})</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                {% for c in congregações %}
                <div class="p-3 bg-slate-50 border rounded-xl flex justify-between items-center">
                    <div>
                        <span class="font-bold text-slate-900 block">{{ c.nome }}</span>
                        <span class="text-[10px] text-slate-500">Bairro: {{ c.bairro }} • Pastor: {{ c.pastor_responsavel }}</span>
                    </div>
                    <span class="bg-indigo-100 text-indigo-900 px-2 py-1 rounded-lg font-black text-[10px]">Ativa</span>
                </div>
                {% endfor %}
            </div>
        </div>

    </div>
</body>
</html>
"""

env.parse(distrital_html)
with open(os.path.join('templates', 'distrital_dashboard.html'), 'w', encoding='utf-8') as f:
    f.write(distrital_html)
print("✓ templates/distrital_dashboard.html criado com sucesso!")

# =============================================================================
# 4. CRIAR DASHBOARD PROVINCIAL (COMPILADOR ESTATÍSTICO DA PROVÍNCIA)
# =============================================================================
provincial_html = """<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <title>Gabinete Provincial - Assembleia de Deus</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-100 p-6 font-sans text-slate-800 text-xs">
    <div class="max-w-6xl mx-auto space-y-6">
        
        <div class="bg-indigo-950 text-white p-6 rounded-3xl shadow flex justify-between items-center">
            <div>
                <span class="bg-amber-400 text-slate-950 px-3 py-1 rounded-full text-[10px] font-black uppercase">
                    Superintendência Provincial
                </span>
                <h1 class="text-2xl font-black mt-1">Província de {{ provincia }}</h1>
                <p class="text-xs text-indigo-200">Consolidação Estatística de Todos os Distritos</p>
            </div>
            <a href="/logout" class="px-4 py-2 bg-rose-600 text-white font-bold rounded-xl shadow">Sair</a>
        </div>

        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="bg-white p-5 rounded-2xl shadow border text-center">
                <span class="text-slate-400 font-bold block text-[10px]">TOTAL DE MEMBROS</span>
                <span class="text-3xl font-black text-indigo-950">{{ totais.membros }}</span>
            </div>
            <div class="bg-white p-5 rounded-2xl shadow border text-center">
                <span class="text-slate-400 font-bold block text-[10px]">NOVAS CONVERSÕES</span>
                <span class="text-3xl font-black text-emerald-700">{{ totais.convertidos }}</span>
            </div>
            <div class="bg-white p-5 rounded-2xl shadow border text-center">
                <span class="text-slate-400 font-bold block text-[10px]">CASAMENTOS NO ANO</span>
                <span class="text-3xl font-black text-pink-700">{{ totais.casamentos }}</span>
            </div>
            <div class="bg-white p-5 rounded-2xl shadow border text-center">
                <span class="text-slate-400 font-bold block text-[10px]">ÓBITOS NO ANO</span>
                <span class="text-3xl font-black text-slate-600">{{ totais.obitos }}</span>
            </div>
        </div>

    </div>
</body>
</html>
"""

env.parse(provincial_html)
with open(os.path.join('templates', 'provincial_dashboard.html'), 'w', encoding='utf-8') as f:
    f.write(provincial_html)
print("✓ templates/provincial_dashboard.html criado com sucesso!")

print("=" * 80)
print(">>> INSTALAÇÃO NACIONAL CONCLUÍDA COM TOTAL SUCESSO! <<<")
print("=" * 80)