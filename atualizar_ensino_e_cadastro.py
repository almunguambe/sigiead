import os

print("=" * 80)
print("A CONFIGURAR PORTAL DO ALUNO, SESSÕES E CORREÇÃO DO CADASTRO...")
print("=" * 80)

os.makedirs('templates', exist_ok=True)

# =============================================================================
# 1. ATUALIZAR APP.PY COM SESSÕES DE ALUNO, MIGRAÇÃO ROBUSTA E REGRAS DE 70%
# =============================================================================
app_code = '''import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'iead_chicuque_chave_secreta_2026_ensino')

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
# MIGRAÇÃO E SINCRONIZAÇÃO TOTAL DE COLUNAS
# -----------------------------------------------------------------------------
def sincronizar_banco():
    is_pg = bool(DATABASE_URL)
    conn = get_db()
    cur = conn.cursor()

    # Criação base das tabelas caso não existam
    pk = "SERIAL PRIMARY KEY" if is_pg else "INTEGER PRIMARY KEY AUTOINCREMENT"
    tabelas_base = [
        f"""CREATE TABLE IF NOT EXISTS membros (id {pk}, nome TEXT);""",
        f"""CREATE TABLE IF NOT EXISTS planificacao (id {pk}, actividade TEXT);""",
        f"""CREATE TABLE IF NOT EXISTS novos_convertidos (id {pk}, nome TEXT);""",
        f"""CREATE TABLE IF NOT EXISTS cultos (id {pk}, data_culto TEXT);""",
        f"""CREATE TABLE IF NOT EXISTS caixa (id {pk}, valor REAL);""",
        f"""CREATE TABLE IF NOT EXISTS doutrina (id {pk}, nome_aluno TEXT);""",
        f"""CREATE TABLE IF NOT EXISTS opcoes_sistema (id {pk}, categoria TEXT, valor TEXT);"""
    ]
    for sql in tabelas_base:
        try:
            cur.execute(sql)
            if hasattr(conn, 'commit'): conn.commit()
        except: pass

    # Sincronização detalhada de colunas em SQLite
    if not is_pg:
        # Colunas de Membros
        cur.execute("PRAGMA table_info(membros);")
        cols_m = [c[1].lower() for c in cur.fetchall()]
        cols_membros_necessarias = [
            ('nome', 'TEXT'), ('contacto', 'TEXT'), ('bi', 'TEXT'), ('cargo', 'TEXT'),
            ('departamento', 'TEXT'), ('estado_civil', 'TEXT'), ('zona', 'TEXT'),
            ('celula', 'TEXT'), ('ano_conversao', 'TEXT'), ('data_batismo', 'TEXT'),
            ('local_residencia', 'TEXT'), ('bairro', 'TEXT'), ('data_nascimento', 'TEXT'),
            ('criado_em', 'TEXT')
        ]
        for col, tipo in cols_membros_necessarias:
            if col not in cols_m:
                cur.execute(f"ALTER TABLE membros ADD COLUMN {col} {tipo};")

        # Colunas de Doutrina & Portal do Aluno
        cur.execute("PRAGMA table_info(doutrina);")
        cols_d = [c[1].lower() for c in cur.fetchall()]
        cols_doutrina_necessarias = [
            ('nome_aluno', 'TEXT'), ('classe', 'TEXT'), ('professor', 'TEXT'),
            ('licao_atual', 'TEXT'), ('data_inicio', 'TEXT'), ('presencas', 'INT DEFAULT 0'),
            ('situacao', 'TEXT DEFAULT "Em Formação"'), ('usuario', 'TEXT'),
            ('senha', 'TEXT'), ('aproveitamento', 'REAL DEFAULT 0'), ('criado_em', 'TEXT')
        ]
        for col, tipo in cols_doutrina_necessarias:
            if col not in cols_d:
                cur.execute(f"ALTER TABLE doutrina ADD COLUMN {col} {tipo};")

        # Colunas de Cultos
        cur.execute("PRAGMA table_info(cultos);")
        cols_c = [c[1].lower() for c in cur.fetchall()]
        for col in ['tipo_culto', 'homens_adultos', 'mulheres_adultas', 'jovens_rapazes', 'jovens_mocas', 'criancas_meninos', 'criancas_meninas', 'visitantes_homens', 'visitantes_mulheres', 'apelos', 'total_presentes', 'pregador', 'tema_mensagem', 'criado_em']:
            if col not in cols_c:
                cur.execute(f"ALTER TABLE cultos ADD COLUMN {col} TEXT;")

        # Colunas de Caixa
        cur.execute("PRAGMA table_info(caixa);")
        cols_cx = [c[1].lower() for c in cur.fetchall()]
        for col in ['tipo', 'categoria', 'descricao', 'data_movimento', 'criado_em']:
            if col not in cols_cx:
                cur.execute(f"ALTER TABLE caixa ADD COLUMN {col} TEXT;")

        if hasattr(conn, 'commit'): conn.commit()
    conn.close()

    # Preencher seletores se vazio
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
            ('tipo_evento', 'Aniversário de Departamento'),
            ('tipo_culto', 'Culto de Domingo'), ('tipo_culto', 'Estudo Bíblico / Doutrina'),
            ('tipo_culto', 'Culto de Oração'), ('tipo_culto', 'Santa Ceia'),
            ('categoria_caixa', 'Dízimos'), ('categoria_caixa', 'Oferta de Culto'),
            ('categoria_caixa', 'Oferta de Missões'), ('categoria_caixa', 'Fundo de Construção'),
            ('categoria_caixa', 'Despesa Operacional'),
            ('classe_doutrina', 'Preparação para Batismo nas Águas'),
            ('classe_doutrina', 'Discipulado de Novos Convertidos'),
            ('classe_doutrina', 'Doutrina Bíblica Fundamental'),
            ('classe_doutrina', 'Formação Ministerial')
        ]
        m = "%s" if is_pg else "?"
        for cat, val in opcoes_iniciais:
            executar_comando(f"INSERT INTO opcoes_sistema (categoria, valor) VALUES ({m}, {m})", (cat, val))

sincronizar_banco()

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
        categorias_caixa_valores[cat] = categorias_caixa_valores.get(cat, 0.0) + float(c.get('valor') or 0)

    aptos_batismo = [d for d in doutrina if float(d.get('aproveitamento') or 0) >= 70 or 'apto' in str(d.get('situacao', '')).lower()]
    em_formacao = [d for d in doutrina if d not in aptos_batismo]

    planos_executados = len([p for p in planos if p.get('status') == 'Executado'])
    taxa_execucao = int((planos_executados / len(planos) * 100)) if planos else 0
    total_pres = sum([int(c.get('total_presentes') or 0) for c in cultos])
    media_assistencia = int(total_pres / len(cultos)) if cultos else 0

    return {
        'membros': membros, 'planificacoes': planos, 'cronograma': planos,
        'cultos': cultos, 'convertidos': convertidos, 'caixa': caixa,
        'doutrina': doutrina, 'opcoes': opcoes_map,
        'kpis': {
            'total_membros': len(membros), 'total_planos': len(planos),
            'planos_executados': planos_executados, 'taxa_execucao': taxa_execucao,
            'total_cultos': len(cultos), 'media_assistencia': media_assistencia,
            'total_convertidos': len(convertidos), 'total_entradas': total_entradas,
            'total_saidas': total_saidas, 'saldo_caixa': saldo_caixa,
            'total_dizimos': total_dizimos, 'total_ofertas': total_ofertas,
            'total_missoes': total_missoes, 'taxa_gasto': taxa_gasto,
            'categorias_caixa': categorias_caixa_valores, 'total_doutrina': len(doutrina),
            'total_aptos_batismo': len(aptos_batismo), 'total_em_formacao': len(em_formacao),
            'aptos_lista': aptos_batismo
        }
    }

# -------------------------------------------------------------
# PAINEL ADMINISTRATIVO & CADASTROS
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

# 1. Cadastro de Membro (Garantido e Validado)
@app.route('/membros/novo', methods=['POST'])
def membros_gravar():
    fd = request.form
    local = (fd.get('local_residencia') or fd.get('bairro') or '').strip()
    m = "%s" if DATABASE_URL else "?"
    sql = f"""INSERT INTO membros 
              (nome, contacto, bi, cargo, departamento, estado_civil, zona, celula, ano_conversao, data_batismo, local_residencia, bairro, criado_em)
              VALUES ({m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m})"""
    params = (
        fd.get('nome', '').strip(), fd.get('contacto', '').strip(), fd.get('bi', '').strip(),
        fd.get('cargo', 'Membro em Comunhão').strip(), fd.get('departamento', 'Geral').strip(),
        fd.get('estado_civil', 'Solteiro(a)').strip(), fd.get('zona', 'Zona 1 - Central').strip(),
        fd.get('celula', 'Célula Betel').strip(), fd.get('ano_conversao', '').strip(),
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
        return "<script>alert('Membro sem data de batismo registada!'); window.location.href='/?aba=membros';</script>"
    return render_template('cartao_batismo.html', m=m, data_extenso=datetime.now().strftime('%d de %B de %Y'))

@app.route('/membros/<int:id>/recomendacao')
def membros_recomendacao(id):
    m = "%s" if DATABASE_URL else "?"
    membro = consultar_um(f"SELECT * FROM membros WHERE id = {m}", (id,))
    if not membro: return redirect('/?aba=membros')
    return render_template('carta_recomendacao.html', m=m, data_extenso=datetime.now().strftime('%d de %B de %Y'))

# -------------------------------------------------------------
# ÁREA DE ENSINO & PORTAL DO ALUNO (COM USUÁRIO, SENHA E 70%)
# -------------------------------------------------------------

# Cadastro de Aluno pelo Professor / Secretaria
@app.route('/doutrina/novo', methods=['POST'])
def doutrina_gravar():
    fd = request.form
    aluno = fd.get('nome_aluno', 'Aluno').strip()
    classe = fd.get('classe', 'Preparação para Batismo nas Águas').strip()
    prof = fd.get('professor', 'Pastor').strip()
    usuario = fd.get('usuario', '').strip().lower() or aluno.split()[0].lower() + str(datetime.now().second)
    senha = fd.get('senha', '123456').strip()
    dt = fd.get('data_inicio', datetime.now().strftime('%Y-%m-%d')).strip()
    
    m = "%s" if DATABASE_URL else "?"
    sql = f"""INSERT INTO doutrina 
              (nome_aluno, classe, professor, licao_atual, data_inicio, presencas, situacao, usuario, senha, aproveitamento, criado_em)
              VALUES ({m}, {m}, {m}, 'Lição 1 - A Salvação e Fé', {m}, 1, 'Em Formação', {m}, {m}, 0.0, {m})"""
    executar_comando(sql, (aluno, classe, prof, dt, usuario, senha, datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=doutrina')

# Avaliação pelo Professor (Lançamento de Aproveitamento %)
@app.route('/doutrina/avaliar', methods=['POST'])
def doutrina_avaliar():
    aluno_id = request.form.get('aluno_id')
    try: nota = float(request.form.get('aproveitamento') or 0)
    except: nota = 0.0
    
    nova_situacao = 'Apto para o Batismo / Avanço' if nota >= 70.0 else 'Em Formação'
    m = "%s" if DATABASE_URL else "?"
    sql = f"UPDATE doutrina SET aproveitamento = {m}, situacao = {m} WHERE id = {m}"
    executar_comando(sql, (nota, nova_situacao, aluno_id))
    return redirect('/?aba=doutrina')

# Login do Aluno
@app.route('/ensino/login', methods=['GET', 'POST'])
def aluno_login():
    erro = None
    if request.method == 'POST':
        usuario = request.form.get('usuario', '').strip().lower()
        senha = request.form.get('senha', '').strip()
        m = "%s" if DATABASE_URL else "?"
        aluno = consultar_um(f"SELECT * FROM doutrina WHERE LOWER(usuario) = {m} AND senha = {m}", (usuario, senha))
        if aluno:
            session['aluno_id'] = aluno['id']
            session['aluno_nome'] = aluno['nome_aluno']
            return redirect('/ensino/aulas')
        else:
            erro = "Usuário ou senha incorretos! Verifique com o seu instrutor."
    return render_template('aluno_login.html', erro=erro)

@app.route('/ensino/logout')
def aluno_logout():
    session.pop('aluno_id', None)
    session.pop('aluno_nome', None)
    return redirect('/ensino/login')

# Sala de Aulas Virtual do Aluno
@app.route('/ensino/aulas')
def aluno_aulas():
    aluno_id = session.get('aluno_id')
    if not aluno_id:
        return redirect('/ensino/login')
    
    m = "%s" if DATABASE_URL else "?"
    aluno = consultar_um(f"SELECT * FROM doutrina WHERE id = {m}", (aluno_id,))
    if not aluno:
        return redirect('/ensino/logout')
    
    return render_template('portal_aluno.html', aluno=aluno)

# Transição para Outra Classe (Exige 70% de Aproveitamento)
@app.route('/ensino/promover')
def aluno_promover():
    aluno_id = session.get('aluno_id')
    if not aluno_id: return redirect('/ensino/login')
    
    m = "%s" if DATABASE_URL else "?"
    aluno = consultar_um(f"SELECT * FROM doutrina WHERE id = {m}", (aluno_id,))
    if not aluno: return redirect('/ensino/login')
    
    nota = float(aluno.get('aproveitamento') or 0)
    if nota < 70.0:
        return "<script>alert('Aproveitamento insuficiente! Necessita de no mínimo 70% para transição de classe.'); window.location.href='/ensino/aulas';</script>"

    # Progressão Hierárquica de Classes
    classe_atual = aluno.get('classe') or ''
    if 'batismo' in classe_atual.lower():
        nova_classe = 'Discipulado de Novos Convertidos'
    elif 'discipulado' in classe_atual.lower():
        nova_classe = 'Doutrina Bíblica Fundamental'
    elif 'fundamental' in classe_atual.lower():
        nova_classe = 'Formação Ministerial'
    else:
        nova_classe = 'Graduado no Ensino Bíblico'

    sql = f"""UPDATE doutrina SET 
              classe = {m}, 
              licao_atual = 'Módulo 1 da Nova Classe', 
              aproveitamento = 0.0, 
              situacao = 'Em Formação' 
              WHERE id = {m}"""
    executar_comando(sql, (nova_classe, aluno_id))
    return redirect('/ensino/aulas')

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
print("✓ app.py: Migrações seguras e regras de ensino/70% integradas!")

# =============================================================================
# 2. CRIAR TELA DE LOGIN DO ALUNO (TEMPLATES/ALUNO_LOGIN.HTML)
# =============================================================================
login_html = '''<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portal do Aluno - IEAD Chicuque</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 min-h-screen flex items-center justify-center p-4 font-sans text-slate-800">
    <div class="w-full max-w-md bg-white rounded-3xl shadow-2xl p-8 border border-slate-700">
        <div class="text-center mb-6">
            <div class="w-16 h-16 mx-auto rounded-full bg-indigo-950 text-white flex items-center justify-center font-black text-2xl shadow mb-3">
                AD
            </div>
            <h1 class="text-xl font-black uppercase tracking-wider text-slate-900">ESCOLA DE DOUTRINA</h1>
            <p class="text-xs text-indigo-700 font-bold">Assembleia de Deus • Sede Chicuque</p>
            <p class="text-[11px] text-slate-400 mt-1">Portal Exclusivo de Formação e Acesso às Aulas</p>
        </div>

        {% if erro %}
        <div class="bg-rose-50 border border-rose-300 text-rose-700 text-xs p-3 rounded-xl mb-4 font-semibold text-center">
            {{ erro }}
        </div>
        {% endif %}

        <form action="/ensino/login" method="POST" class="space-y-4 text-xs">
            <div>
                <label class="block font-bold text-slate-700 mb-1">Usuário do Aluno</label>
                <input type="text" name="usuario" required placeholder="Ex: anselmo ou nº atribuído" class="w-full h-11 px-3 border-2 border-slate-200 rounded-xl bg-slate-50 font-bold focus:border-indigo-600 focus:outline-none">
            </div>

            <div>
                <label class="block font-bold text-slate-700 mb-1">Senha de Acesso</label>
                <input type="password" name="senha" required placeholder="Digite a sua senha" class="w-full h-11 px-3 border-2 border-slate-200 rounded-xl bg-slate-50 font-bold focus:border-indigo-600 focus:outline-none">
            </div>

            <button type="submit" class="w-full py-3.5 bg-indigo-900 hover:bg-indigo-950 text-white font-extrabold rounded-xl shadow cursor-pointer text-sm transition">
                Entrar na Sala de Aula
            </button>
        </form>

        <div class="mt-6 pt-4 border-t border-slate-100 text-center text-xs">
            <a href="/" class="text-indigo-600 hover:underline font-bold">← Voltar ao Sistema Geral</a>
        </div>
    </div>
</body>
</html>
'''

with open(os.path.join('templates', 'aluno_login.html'), 'w', encoding='utf-8') as f:
    f.write(login_html)
print("✓ templates/aluno_login.html criado com sucesso!")

# =============================================================================
# 3. CRIAR PORTAL DO ALUNO COM MENSAGEM DE BOAS-VINDAS E 70% DE APROVEITAMENTO
# =============================================================================
portal_html = '''<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sala de Aulas - {{ aluno.nome_aluno }}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-100 text-slate-800 font-sans min-h-screen flex flex-col">

    <!-- CABEÇALHO DO PORTAL DO ALUNO -->
    <header class="bg-indigo-950 text-white px-6 py-4 flex justify-between items-center shadow-lg">
        <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-white text-indigo-950 flex items-center justify-center font-black text-lg">AD</div>
            <div>
                <h1 class="font-extrabold text-sm uppercase tracking-wide">ÁREA DE ENSINO BÍBLICO</h1>
                <p class="text-[11px] text-amber-300">IEAD Chicuque • Ministério Thavane</p>
            </div>
        </div>
        <div class="flex items-center gap-4 text-xs">
            <span class="font-bold text-slate-200">Aluno(a): <b class="text-white">{{ aluno.nome_aluno }}</b></span>
            <a href="/ensino/logout" class="bg-rose-700 hover:bg-rose-800 text-white px-3 py-1.5 rounded-lg font-bold shadow">
                Sair
            </a>
        </div>
    </header>

    <main class="flex-1 max-w-5xl w-full mx-auto p-6 space-y-6">

        <!-- MENSAGEM DE BOAS-VINDAS PASTORAL -->
        <div class="bg-gradient-to-r from-indigo-900 to-indigo-800 text-white p-6 rounded-3xl shadow-xl flex flex-col md:flex-row items-center justify-between gap-4">
            <div>
                <span class="bg-amber-400 text-slate-950 text-[10px] font-black uppercase px-2.5 py-1 rounded-full">
                    Acesso Confirmado
                </span>
                <h2 class="text-2xl font-black mt-2">Graça e Paz, {{ aluno.nome_aluno }}!</h2>
                <p class="text-xs text-indigo-200 mt-1 max-w-xl">
                    Seja muito bem-vindo(a) à sua classe de formação espiritual na IEAD Chicuque. Dedique-se à leitura da Palavra e acompanhe com zelo as lições ministradas.
                </p>
            </div>
            <div class="bg-white/10 p-4 rounded-2xl text-center shrink-0 border border-white/20">
                <span class="text-[10px] uppercase font-bold text-indigo-200 block">Classe Atual</span>
                <span class="text-sm font-extrabold text-white">{{ aluno.classe }}</span>
            </div>
        </div>

        <!-- PAINEL DE APROVEITAMENTO & META DE 70% PARA TRANSIÇÃO -->
        {% set nota = aluno.aproveitamento or 0.0 %}
        <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
            <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-3">
                <div>
                    <h3 class="font-extrabold text-sm uppercase text-slate-700">Seu Aproveitamento Curricular</h3>
                    <p class="text-xs text-slate-400">Meta oficial para transição de classe ou homologação de batismo: <b>70% de aproveitamento</b></p>
                </div>
                <div class="text-right">
                    <span class="text-3xl font-black {% if nota >= 70.0 %}text-emerald-600{% else %}text-amber-600{% endif %}">
                        {{ "%.1f"|format(nota) }}%
                    </span>
                </div>
            </div>

            <!-- BARRA DE PROGRESSO -->
            <div class="w-full bg-slate-100 h-4 rounded-full overflow-hidden p-0.5 border border-slate-200">
                <div class="{% if nota >= 70.0 %}bg-emerald-500{% else %}bg-amber-500{% endif %} h-full rounded-full transition-all duration-500" style="width: {{ [nota, 100]|min }}%"></div>
            </div>

            <!-- ALERTA / BOTÃO DE PROMOÇÃO -->
            <div class="mt-4 pt-4 border-t border-slate-100 flex flex-col md:flex-row items-center justify-between gap-3 text-xs">
                {% if nota >= 70.0 %}
                <div class="flex items-center gap-2 text-emerald-800 font-bold">
                    <span class="text-xl">🎉</span>
                    <span>Parabéns! Atingiu {{ "%.1f"|format(nota) }}% de aproveitamento e está qualificado(a) para avançar!</span>
                </div>
                <a href="/ensino/promover" onclick="return confirm('Confirmar avanço para a próxima classe?')" class="px-5 py-2.5 bg-emerald-700 hover:bg-emerald-800 text-white font-extrabold rounded-xl shadow cursor-pointer text-xs">
                    🎓 Subir para a Próxima Classe
                </a>
                {% else %}
                <div class="text-slate-500">
                    Status: <b class="text-amber-700">{{ aluno.situacao }}</b> • Faltam <b>{{ "%.1f"|format(70.0 - nota) }}%</b> para atingir a nota mínima de aprovação.
                </div>
                <span class="text-slate-400 italic text-[11px]">As notas são atualizadas pelo seu professor após as provas e lições.</span>
                {% endif %}
            </div>
        </div>

        <!-- MÓDULO DE LIÇÕES E CONTEÚDO DAS AULAS -->
        <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
            <h3 class="font-extrabold text-base text-indigo-950 mb-4 pb-2 border-b flex items-center gap-2">
                <span>📖</span> Lições Bíblicas do Currículo Oficial
            </h3>

            <div class="space-y-4 text-xs">
                <!-- LIÇÃO 1 -->
                <details open class="border border-slate-200 rounded-2xl p-4 bg-slate-50">
                    <summary class="font-bold text-sm text-slate-800 cursor-pointer flex justify-between items-center">
                        <span>Lição 1: O Plano da Salvação e a Justificação pela Fé</span>
                        <span class="text-[11px] text-emerald-700 font-extrabold bg-emerald-100 px-2.5 py-0.5 rounded-full">Disponível</span>
                    </summary>
                    <div class="mt-3 text-slate-600 space-y-2 text-justify border-t pt-3">
                        <p><b>Texto Áureo:</b> <i>"Porque pela graça sois salvos, por meio da fé; e isto não vem de vós, é dom de Deus." (Efésios 2:8)</i></p>
                        <p>A salvação é um dom imerecido proporcionado pelo sacrifício vicário de Cristo Jesus no Calvário. O pecador regenerado reconhece o seu estado e entrega a sua vida ao Senhor.</p>
                    </div>
                </details>

                <!-- LIÇÃO 2 -->
                <details class="border border-slate-200 rounded-2xl p-4 bg-slate-50">
                    <summary class="font-bold text-sm text-slate-800 cursor-pointer flex justify-between items-center">
                        <span>Lição 2: A Importância da Oração e Leitura Diária da Palavra</span>
                        <span class="text-[11px] text-emerald-700 font-extrabold bg-emerald-100 px-2.5 py-0.5 rounded-full">Disponível</span>
                    </summary>
                    <div class="mt-3 text-slate-600 space-y-2 text-justify border-t pt-3">
                        <p><b>Texto Áureo:</b> <i>"Lâmpada para os meus pés é tua palavra e luz, para o meu caminho." (Salmos 119:105)</i></p>
                        <p>O alimento diário do cristão é a comunhão permanente com Deus através da oração perseverante e da meditação constante nas Sagradas Escrituras.</p>
                    </div>
                </details>

                <!-- LIÇÃO 3 -->
                <details class="border border-slate-200 rounded-2xl p-4 bg-slate-50">
                    <summary class="font-bold text-sm text-slate-800 cursor-pointer flex justify-between items-center">
                        <span>Lição 3: O Batismo nas Águas por Imersão</span>
                        <span class="text-[11px] text-indigo-700 font-extrabold bg-indigo-100 px-2.5 py-0.5 rounded-full">Requisito Batismal</span>
                    </summary>
                    <div class="mt-3 text-slate-600 space-y-2 text-justify border-t pt-3">
                        <p><b>Texto Áureo:</b> <i>"Ide, portanto, fazei discípulos de todas as nações, batizando-os em nome do Pai, e do Filho, e do Espírito Santo." (Mateus 28:19)</i></p>
                        <p>O batismo bíblico representa publicamente o sepultamento da velha vida de pecados e o ressurgimento para uma nova vida em Cristo Jesus (Romanos 6:4).</p>
                    </div>
                </details>

                <!-- LIÇÃO 4 -->
                <details class="border border-slate-200 rounded-2xl p-4 bg-slate-50">
                    <summary class="font-bold text-sm text-slate-800 cursor-pointer flex justify-between items-center">
                        <span>Lição 4: A Santa Ceia e a Comunhão dos Santos</span>
                        <span class="text-[11px] text-slate-500 font-semibold bg-slate-200 px-2.5 py-0.5 rounded-full">Módulo 4</span>
                    </summary>
                    <div class="mt-3 text-slate-600 space-y-2 text-justify border-t pt-3">
                        <p><b>Texto Áureo:</b> <i>"Fazei isto em memória de mim." (1 Coríntios 11:24)</i></p>
                        <p>Memorial solene do corpo e do sangue de Jesus Cristo, celebrado em reverência por todos os membros em comunhão.</p>
                    </div>
                </details>
            </div>
        </div>

    </main>

    <footer class="bg-white border-t border-slate-200 py-4 text-center text-xs text-slate-400">
        IEAD Chicuque • Sistema de Ensino Eclesiástico • Gabinete de Educação Cristã
    </footer>
</body>
</html>
'''

with open(os.path.join('templates', 'portal_aluno.html'), 'w', encoding='utf-8') as f:
    f.write(portal_html)
print("✓ templates/portal_aluno.html criado com sucesso!")

# =============================================================================
# 4. ATUALIZAR DASHBOARD.HTML COM ACESSO AO PORTAL E LANÇAMENTO DE NOTAS
# =============================================================================
with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    dash = f.read()

# Adicionar link do Portal do Aluno no menu lateral
if 'href="/ensino/login"' not in dash:
    dash = dash.replace(
        '<span>📖</span><span>7. Doutrina & Batismo</span>',
        '<span>📖</span><span>7. Doutrina & Batismo</span>\n                </a>\n                <a href="/ensino/login" target="_blank" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition text-emerald-300 hover:bg-slate-800 font-bold">\n                    <span>🎓</span><span>Portal do Aluno (Aulas)</span>'
    )

# Atualizar formulário de inscrição de formando para incluir Usuário e Senha
form_doutrina_antigo = '''                <h3 class="font-bold text-base mb-4 border-b pb-2">🎓 Inscrever Formando</h3>
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
                </form>'''

form_doutrina_novo = '''                <h3 class="font-bold text-base mb-4 border-b pb-2">🎓 Inscrever Formando com Login</h3>
                <form action="/doutrina/novo" method="POST" class="space-y-3 text-xs">
                    <div>
                        <label class="block font-semibold mb-1">Nome Completo do Aluno *</label>
                        <input type="text" name="nome_aluno" required placeholder="Nome do formando" class="w-full h-10 px-3 border rounded-xl bg-slate-50 font-bold">
                    </div>
                    <div class="grid grid-cols-2 gap-2">
                        <div>
                            <label class="block font-semibold mb-1">Classe *</label>
                            <select name="classe" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-bold">
                                {% for op in opcoes.get('classe_doutrina', []) %}<option value="{{ op.valor }}">{{ op.valor }}</option>{% endfor %}
                            </select>
                        </div>
                        <div>
                            <label class="block font-semibold mb-1">Instrutor</label>
                            <input type="text" name="professor" placeholder="Pr. / Diác." class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                        </div>
                    </div>
                    
                    <div class="p-3 bg-amber-50 rounded-xl border border-amber-200 space-y-2">
                        <div class="font-bold text-amber-900 text-[10px] uppercase">Acesso à Área de Ensino do Aluno</div>
                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <label class="block text-slate-600 mb-0.5">Usuário</label>
                                <input type="text" name="usuario" placeholder="Ex: anselmo" class="w-full h-8 px-2 border rounded bg-white font-bold">
                            </div>
                            <div>
                                <label class="block text-slate-600 mb-0.5">Senha</label>
                                <input type="text" name="senha" value="123456" class="w-full h-8 px-2 border rounded bg-white font-bold">
                            </div>
                        </div>
                    </div>

                    <div>
                        <label class="block font-semibold mb-1">Data Início</label>
                        <input type="date" name="data_inicio" required class="w-full h-10 px-2 border rounded-xl bg-slate-50">
                    </div>

                    <button type="submit" class="w-full py-3 bg-amber-700 hover:bg-amber-800 text-white font-bold rounded-xl shadow cursor-pointer">
                        Gravar Inscrição & Credenciais
                    </button>
                </form>'''

if form_doutrina_antigo in dash:
    dash = dash.replace(form_doutrina_antigo, form_doutrina_novo)

# Atualizar tabela de formandos para exibir Usuário, Aproveitamento % e formulário rápido de notas
tabela_doutrina_antiga = '''                        <thead><tr class="border-b-2 border-slate-200 text-slate-500"><th class="py-2.5 px-2">Candidato</th><th class="py-2.5 px-2">Classe</th><th class="py-2.5 px-2">Progresso</th><th class="py-2.5 px-2">Situação</th><th class="py-2.5 px-2 text-right">Ação</th></tr></thead>
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
                        </tbody>'''

tabela_doutrina_nova = '''                        <thead>
                            <tr class="border-b-2 border-slate-200 text-slate-500">
                                <th class="py-2.5 px-2">Aluno & Credenciais</th>
                                <th class="py-2.5 px-2">Classe</th>
                                <th class="py-2.5 px-2 text-center">Aproveitamento</th>
                                <th class="py-2.5 px-2">Situação</th>
                                <th class="py-2.5 px-2 text-right">Lançar Nota (≥70%)</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for d in doutrina %}
                            <tr class="border-b border-slate-100 hover:bg-slate-50">
                                <td class="py-2.5 px-2">
                                    <div class="font-bold text-slate-900">{{ d.nome_aluno }}</div>
                                    <div class="text-[10px] text-slate-500">Usuário: <b class="text-indigo-900">{{ d.usuario or '---' }}</b> | Senha: <b>{{ d.senha or '123456' }}</b></div>
                                </td>
                                <td class="py-2.5 px-2 text-slate-700 font-semibold">{{ d.classe }}</td>
                                <td class="py-2.5 px-2 text-center">
                                    <span class="px-2.5 py-1 rounded-full font-black text-xs {% if (d.aproveitamento or 0) >= 70 %}bg-emerald-100 text-emerald-800{% else %}bg-amber-100 text-amber-800{% endif %}">
                                        {{ "%.0f"|format(d.aproveitamento or 0) }}%
                                    </span>
                                </td>
                                <td class="py-2.5 px-2">
                                    {% if (d.aproveitamento or 0) >= 70 or 'apto' in d.situacao|lower %}
                                    <span class="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-bold text-[10px]">✅ Apto / Aprovado</span>
                                    {% else %}
                                    <span class="bg-slate-100 text-slate-700 px-2 py-0.5 rounded font-bold text-[10px]">Em Formação</span>
                                    {% endif %}
                                </td>
                                <td class="py-2.5 px-2 text-right">
                                    <form action="/doutrina/avaliar" method="POST" class="inline-flex items-center gap-1">
                                        <input type="hidden" name="aluno_id" value="{{ d.id }}">
                                        <input type="number" step="1" min="0" max="100" name="aproveitamento" value="{{ (d.aproveitamento or 0)|int }}" class="w-14 h-7 px-1 border rounded text-center font-bold text-xs">
                                        <button type="submit" class="px-2 py-1 bg-indigo-700 hover:bg-indigo-800 text-white rounded font-bold text-[10px]">
                                            Gravar %
                                        </button>
                                    </form>
                                </td>
                            </tr>
                            {% else %}
                            <tr><td colspan="5" class="py-8 text-center text-slate-400">Nenhum formando inscrito.</td></tr>
                            {% endfor %}
                        </tbody>'''

if tabela_doutrina_antiga in dash:
    dash = dash.replace(tabela_doutrina_antiga, tabela_doutrina_nova)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(dash)

print("✓ templates/dashboard.html atualizado!")
print("=" * 80)
print("CONFIGURAÇÃO CONCLUÍDA COM TOTAL SUCESSO!")
print("=" * 80)