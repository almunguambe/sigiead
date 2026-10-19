import os
import jinja2

print("=" * 80)
print("A RESTAURAR PORTAL DO ALUNO (/ensino/login) E ATIVAR CONEXÃO ALUNO-PROFESSOR...")
print("=" * 80)

os.makedirs('templates', exist_ok=True)

# =============================================================================
# 1. ATUALIZAR APP.PY COM TODAS AS ROTAS UNIFICADAS E SISTEMA DE PROFESSOR
# =============================================================================
app_code = '''import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'iead_chicuque_chave_ensino_2026')

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

def inicializar_banco():
    is_pg = bool(DATABASE_URL)
    conn = get_db()
    cur = conn.cursor()
    pk = "SERIAL PRIMARY KEY" if is_pg else "INTEGER PRIMARY KEY AUTOINCREMENT"

    tabelas = [
        f"""CREATE TABLE IF NOT EXISTS membros (id {pk}, nome TEXT);""",
        f"""CREATE TABLE IF NOT EXISTS planificacao (id {pk}, actividade TEXT);""",
        f"""CREATE TABLE IF NOT EXISTS novos_convertidos (id {pk}, nome TEXT);""",
        f"""CREATE TABLE IF NOT EXISTS cultos (id {pk}, data_culto TEXT);""",
        f"""CREATE TABLE IF NOT EXISTS caixa (id {pk}, valor REAL);""",
        f"""CREATE TABLE IF NOT EXISTS doutrina (id {pk}, nome_aluno TEXT);""",
        f"""CREATE TABLE IF NOT EXISTS opcoes_sistema (id {pk}, categoria TEXT, valor TEXT);""",
        f"""CREATE TABLE IF NOT EXISTS progresso_licoes (
            id {pk}, aluno_id INT, licao_id TEXT, resumo_aluno TEXT,
            nota_teste REAL DEFAULT 0, status TEXT DEFAULT 'Em Estudo', criado_em TEXT
        );""",
        f"""CREATE TABLE IF NOT EXISTS duvidas_alunos (
            id {pk}, aluno_id INT, licao_id TEXT, pergunta TEXT, 
            resposta_sistema TEXT, resposta_professor TEXT, professor_nome TEXT, criado_em TEXT
        );""",
        f"""CREATE TABLE IF NOT EXISTS balanco_anual (
            id {pk}, ano INT UNIQUE,
            constrangimento_1 TEXT, constrangimento_2 TEXT, constrangimento_3 TEXT,
            perspectiva_1 TEXT, perspectiva_2 TEXT, perspectiva_3 TEXT, atualizado_em TEXT
        );"""
    ]
    for sql in tabelas:
        try:
            cur.execute(sql)
            if hasattr(conn, 'commit'): conn.commit()
        except: pass

    if not is_pg:
        # Colunas de membros
        for col, tipo in [
            ('nome', 'TEXT'), ('contacto', 'TEXT'), ('bi', 'TEXT'), ('cargo', 'TEXT'),
            ('departamento', 'TEXT'), ('estado_civil', 'TEXT'), ('zona', 'TEXT'),
            ('celula', 'TEXT'), ('ano_conversao', 'TEXT'), ('data_batismo', 'TEXT'),
            ('local_residencia', 'TEXT'), ('bairro', 'TEXT'), ('genero', 'TEXT DEFAULT "Masculino"'), ('criado_em', 'TEXT')
        ]:
            try: cur.execute(f"ALTER TABLE membros ADD COLUMN {col} {tipo};")
            except: pass

        # Colunas de caixa
        for col, tipo in [
            ('tipo', 'TEXT'), ('categoria', 'TEXT'), ('valor', 'REAL'),
            ('descricao', 'TEXT'), ('data_movimento', 'TEXT'), ('conta', 'TEXT'),
            ('destino_tipo', 'TEXT'), ('departamento', 'TEXT'),
            ('proposito', 'TEXT'), ('criado_em', 'TEXT')
        ]:
            try: cur.execute(f"ALTER TABLE caixa ADD COLUMN {col} {tipo};")
            except: pass

        # Colunas de doutrina
        for col, tipo in [
            ('nome_aluno', 'TEXT'), ('classe', 'TEXT'), ('professor', 'TEXT'),
            ('licao_atual', 'TEXT'), ('data_inicio', 'TEXT'), ('presencas', 'INT DEFAULT 0'),
            ('situacao', 'TEXT DEFAULT "Em Formação"'), ('usuario', 'TEXT'),
            ('senha', 'TEXT'), ('aproveitamento', 'REAL DEFAULT 0'), ('criado_em', 'TEXT')
        ]:
            try: cur.execute(f"ALTER TABLE doutrina ADD COLUMN {col} {tipo};")
            except: pass

        # Colunas de planificação
        for col, tipo in [
            ('dificuldades', 'TEXT'), ('perspectivas', 'TEXT'),
            ('participantes_homens', 'INT DEFAULT 0'), ('participantes_mulheres', 'INT DEFAULT 0'),
            ('participantes_jovens', 'INT DEFAULT 0'), ('participantes_criancas', 'INT DEFAULT 0'),
            ('total_participantes', 'INT DEFAULT 0'), ('data_execucao', 'TEXT'), ('feedback', 'TEXT')
        ]:
            try: cur.execute(f"ALTER TABLE planificacao ADD COLUMN {col} {tipo};")
            except: pass

        # Coluna resposta_professor em duvidas_alunos
        try: cur.execute("ALTER TABLE duvidas_alunos ADD COLUMN resposta_professor TEXT;")
        except: pass
        try: cur.execute("ALTER TABLE duvidas_alunos ADD COLUMN professor_nome TEXT;")
        except: pass

        if hasattr(conn, 'commit'): conn.commit()
    conn.close()

inicializar_banco()

# -------------------------------------------------------------
# CURRÍCULO ESTRUTURADO POR CLASSES (MANUAL DA IEADAO)
# -------------------------------------------------------------
CURRICULO_CLASSES = [
    {
        'id_classe': 'classe_1',
        'nome_classe': 'Classe I - Primeiros Passos',
        'descricao': 'Rudimentos da Fé Cristã e Fundamentos da Salvação',
        'licoes': [
            {
                'id': 'c1_l1', 'numero': 'Lição 1', 'titulo': 'O Pecado e o Perdão',
                'texto_aureo': 'Porque o salário do pecado é a morte, mas o dom gratuito de Deus é a vida eterna. (Rm 6:23)',
                'leitura_base': 'Rm 3:23; Is 59:2; 1Jo 1:7-9; Pv 28:13',
                'conteudo': 'Pecar significa literalmente "Errar o Alvo" da Santa Vontade de Deus. Desobedecer é a causa no coração e Transgredir é o efeito visível contra a Lei. Na cruz, Cristo operou a Expiação (pagou as consequências pelo sacrifício inocente) e nos deu paz e reconciliação.',
                'questoes': [
                    {'p': 'Qual é a diferença entre desobedecer e transgredir?', 'ops': ['Transgredir é no coração e desobedecer é o ato físico.', 'Desobedecer é a causa oculta no coração e transgredir é o efeito exposto.', 'Não há diferença doutrinária.', 'Transgredir só se aplica a pagãos.'], 'c': 1},
                    {'p': 'O que significa Expiação no plano da salvação?', 'ops': ['Perdão mediante o sacrifício de uma vítima inocente (Cristo).', 'Cumprir penitências humanas.', 'Esquecer o erro sem arrependimento.', 'Rito feito apenas no batismo.'], 'c': 0}
                ]
            },
            {
                'id': 'c1_l2', 'numero': 'Lição 2', 'titulo': 'Salvação e Senhorio de Cristo',
                'texto_aureo': 'Se alguém está em Cristo, nova criatura é; as coisas velhas já passaram. (2Co 5:17)',
                'leitura_base': 'Ef 2:8-10; Jo 1:12; 1Co 8:6',
                'conteudo': 'Somos salvos pela graça por meio da fé, e as obras acompanham como fruto. Cristo quer ser Salvador e dominar como Senhor sobre o trono do nosso coração, governando a nossa conduta.',
                'questoes': [
                    {'p': 'Qual é a relação entre fé, obras e salvação em Efésios 2:8-10?', 'ops': ['As obras compram a salvação.', 'Somos salvos pela graça por meio da fé, e as obras acompanham como fruto.', 'O crente salvo não precisa de praticar boas obras.', 'A fé sem moralidade basta.'], 'c': 1}
                ]
            },
            {
                'id': 'c1_l5', 'numero': 'Lição 5', 'titulo': 'A Bíblia - Manual de Fé dos Cristãos',
                'texto_aureo': 'Lâmpada para os meus pés é a tua palavra e luz para o meu caminho. (Sl 119:105)',
                'leitura_base': '2Tm 3:16; Js 1:8; Sl 1:2',
                'conteudo': 'A Bíblia contém 66 livros (39 no Antigo Testamento e 27 no Novo Testamento). O Autor é Deus, o Intérprete é o Espírito Santo e o Tema Central é Jesus Cristo.',
                'questoes': [
                    {'p': 'Qual é a divisão exata dos 66 livros da Bíblia?', 'ops': ['40 no AT e 26 no NT.', '39 no Antigo Testamento e 27 no Novo Testamento.', '46 no AT e 27 no NT.', '50 no AT e 16 no NT.'], 'c': 1}
                ]
            }
        ]
    },
    {
        'id_classe': 'classe_2',
        'nome_classe': 'Classe II - Vida Cristã',
        'descricao': 'Disciplina Espiritual, Oração, Jejum e Mordomia',
        'licoes': [
            {
                'id': 'c2_l1', 'numero': 'Lição 1', 'titulo': 'Oração e Jejum',
                'texto_aureo': 'Servindo a Deus em jejuns e orações, de noite e de dia. (Lc 2:37)',
                'leitura_base': '1Ts 5:17; Is 58:6-7; Mt 6:16-18; Zc 7:5',
                'conteudo': 'Orar é um mandamento. O jejum é a abstinência para consagrar a vida a Deus, tornando o espírito sensível e acompanhado de obras de amor e reconciliação.',
                'questoes': [
                    {'p': 'Qual é o verdadeiro espírito do jejum segundo Isaías 58?', 'ops': ['Greve de fome egoísta.', 'Humilhar a carne para sensibilidade espiritual e amor ao próximo.', 'Apenas emagrecer.', 'Exibir santidade aos homens.'], 'c': 1}
                ]
            },
            {
                'id': 'c2_l3', 'numero': 'Lição 3', 'titulo': 'Dízimos e Ofertas Alçadas',
                'texto_aureo': 'Cada um contribua de coração, porque Deus ama ao que dá com alegria. (2Co 9:7)',
                'leitura_base': 'Ml 3:8-11; Lv 27:30; 1Co 16:2',
                'conteudo': 'O dízimo (décima parte) pertence ao Senhor. Não é favor, mas ato de obediência e fidelidade espiritual para sustento da Sua Obra.',
                'questoes': [
                    {'p': 'O que representa o dízimo na visão bíblica da IEADAO?', 'ops': ['Uma taxa civil opcional.', 'A devolução obediente da décima parte que pertence ao Senhor.', 'Uma exigência dispensável.', 'Um costume que foi cancelado.'], 'c': 1}
                ]
            }
        ]
    },
    {
        'id_classe': 'classe_3',
        'nome_classe': 'Classe III - Maturidade Cristã',
        'descricao': 'Santificação, Consciência do Corpo e Firmeza da Fé',
        'licoes': [
            {
                'id': 'c3_l2', 'numero': 'Lição 5', 'titulo': 'Fé: Factos, Não Sentimentos',
                'texto_aureo': 'A fé é o firme fundamento das coisas que se esperam. (Hb 11:1)',
                'leitura_base': '2Co 5:7; 2Tm 3:14-16; Jr 17:9',
                'conteudo': 'O crente vive por fé na Palavra e não por emoções. Na analogia do comboio: 1) A LOCOMOTIVA é o FACTO (a Palavra de Deus); 2) O CARRO DE LIGAÇÃO é a FÉ; 3) O VAGÃO são os SENTIMENTOS. O comboio anda pela locomotiva, nunca pelo vagão.',
                'questoes': [
                    {'p': 'Na analogia do comboio, o que deve conduzir a vida do cristão?', 'ops': ['O vagão das emoções passageiras.', 'A locomotiva dos Factos inabaláveis da Palavra de Deus.', 'Sentimentos de medo ou incerteza.', 'A aprovação dos homens.'], 'c': 1}
                ]
            }
        ]
    },
    {
        'id_classe': 'classe_4',
        'nome_classe': 'Classe IV - Candidatos ao Baptismo',
        'descricao': 'Ordenanças Sagradas e Preparação Batismal',
        'licoes': [
            {
                'id': 'c4_l1', 'numero': 'Lição 1', 'titulo': 'Baptismo nas Águas e Ceia do Senhor',
                'texto_aureo': 'De sorte que foram baptizados os que de bom grado receberam a sua palavra. (At 2:41)',
                'leitura_base': 'Rm 6:4; 1Co 11:23-29; Mt 28:19',
                'conteudo': 'O Baptismo nas águas por imersão simboliza a morte para o pecado e a ressurreição para Deus. A Ceia contempla Passado (a cruz), Presente (autoexame e comunhão) e Futuro (a volta de Cristo).',
                'questoes': [
                    {'p': 'O que simboliza descer e sair das águas no baptismo?', 'ops': ['Um banho ritualístico simples.', 'Sepultamento da velha vida de pecado e ressurreição para uma nova vida com Deus.', 'Uma exigência da lei de Moisés.', 'Apenas um rito de passagem.'], 'c': 1}
                ]
            }
        ]
    }
]

TODAS_LICOES = []
for cl in CURRICULO_CLASSES:
    for lic in cl['licoes']:
        TODAS_LICOES.append({**lic, 'id_classe': cl['id_classe'], 'nome_classe': cl['nome_classe']})
MAPA_LICOES = {l['id']: l for l in TODAS_LICOES}

@app.context_processor
def injetar_dados():
    membros = consultar_todos("SELECT * FROM membros ORDER BY id DESC")
    planos = consultar_todos("SELECT * FROM planificacao ORDER BY id DESC")
    cultos = consultar_todos("SELECT * FROM cultos ORDER BY id DESC")
    convertidos = consultar_todos("SELECT * FROM novos_convertidos ORDER BY id DESC")
    caixa = consultar_todos("SELECT * FROM caixa ORDER BY id DESC")
    doutrina = consultar_todos("SELECT * FROM doutrina ORDER BY id DESC")
    duvidas_pendentes = consultar_todos("SELECT * FROM duvidas_alunos WHERE resposta_professor IS NULL OR resposta_professor = '' ORDER BY id DESC")
    opcoes_lista = consultar_todos("SELECT * FROM opcoes_sistema ORDER BY categoria, valor ASC")

    opcoes_map = {}
    for op in opcoes_lista:
        opcoes_map.setdefault(op['categoria'], []).append(op)

    total_entradas = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Entrada'])
    total_saidas = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Saída'])
    saldo_caixa = total_entradas - total_saidas

    entradas_caixa_fisico = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Entrada' and 'banco' not in str(c.get('conta', '')).lower()])
    saidas_caixa_fisico = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Saída' and 'banco' not in str(c.get('conta', '')).lower()])
    saldo_caixa_fisico = entradas_caixa_fisico - saidas_caixa_fisico

    entradas_banco = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Entrada' and 'banco' in str(c.get('conta', '')).lower()])
    saidas_banco = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Saída' and 'banco' in str(c.get('conta', '')).lower()])
    saldo_banco = entradas_banco - saidas_banco

    geral_in = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Entrada' and str(c.get('destino_tipo', 'Igreja Geral')) == 'Igreja Geral'])
    geral_out = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Saída' and str(c.get('destino_tipo', 'Igreja Geral')) == 'Igreja Geral'])

    mae_in = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Entrada' and str(c.get('destino_tipo', '')) == 'Igreja Mãe'])
    mae_out = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Saída' and str(c.get('destino_tipo', '')) == 'Igreja Mãe'])

    depto_in = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Entrada' and str(c.get('destino_tipo', '')) == 'Departamento'])
    depto_out = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Saída' and str(c.get('destino_tipo', '')) == 'Departamento'])

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
        'doutrina': doutrina, 'duvidas_pendentes': duvidas_pendentes, 'opcoes': opcoes_map,
        'kpis': {
            'total_membros': len(membros), 'total_planos': len(planos),
            'planos_executados': planos_executados, 'taxa_execucao': taxa_execucao,
            'total_cultos': len(cultos), 'media_assistencia': media_assistencia,
            'total_convertidos': len(convertidos), 'total_entradas': total_entradas,
            'total_saidas': total_saidas, 'saldo_caixa': saldo_caixa,
            'saldo_caixa_fisico': saldo_caixa_fisico, 'saldo_banco': saldo_banco,
            'geral_in': geral_in, 'geral_out': geral_out,
            'mae_in': mae_in, 'mae_out': mae_out,
            'depto_in': depto_in, 'depto_out': depto_out,
            'total_dizimos': total_dizimos, 'total_ofertas': total_ofertas,
            'total_missoes': total_missoes, 'taxa_gasto': taxa_gasto,
            'categorias_caixa': categorias_caixa_valores, 'total_doutrina': len(doutrina),
            'total_aptos_batismo': len(aptos_batismo), 'total_em_formacao': len(em_formacao),
            'aptos_lista': aptos_batismo
        }
    }

# -------------------------------------------------------------
# ROTAS PRINCIPAIS DO SISTEMA GERAL
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

@app.route('/membros/novo', methods=['POST'])
def membros_gravar():
    fd = request.form
    local = (fd.get('local_residencia') or fd.get('bairro') or '').strip()
    genero = fd.get('genero', 'Masculino').strip()
    m = "%s" if DATABASE_URL else "?"
    sql = f"""INSERT INTO membros 
              (nome, contacto, bi, cargo, departamento, estado_civil, zona, celula, ano_conversao, data_batismo, local_residencia, bairro, genero, criado_em)
              VALUES ({m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m})"""
    params = (
        fd.get('nome', '').strip(), fd.get('contacto', '').strip(), fd.get('bi', '').strip(),
        fd.get('cargo', 'Membro em Comunhão').strip(), fd.get('departamento', 'Geral').strip(),
        fd.get('estado_civil', 'Solteiro(a)').strip(), fd.get('zona', 'Zona 1 - Central').strip(),
        fd.get('celula', 'Célula Betel').strip(), fd.get('ano_conversao', '').strip(),
        fd.get('data_batismo', '').strip(), local, local, genero, datetime.now().strftime('%Y-%m-%d %H:%M')
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

# CADASTRO DE ALUNOS COM ATRIBUIÇÃO DE PROFESSOR
@app.route('/doutrina/novo', methods=['POST'])
def doutrina_gravar():
    fd = request.form
    aluno = fd.get('nome_aluno', 'Aluno').strip()
    classe = fd.get('classe', 'Classe I - Primeiros Passos').strip()
    prof = fd.get('professor', 'Pastor Dirigente').strip()
    usuario = fd.get('usuario', '').strip().lower() or aluno.split()[0].lower() + str(datetime.now().second)
    senha = fd.get('senha', '123456').strip()
    dt = fd.get('data_inicio', datetime.now().strftime('%Y-%m-%d')).strip()
    m = "%s" if DATABASE_URL else "?"
    sql = f"""INSERT INTO doutrina 
              (nome_aluno, classe, professor, licao_atual, data_inicio, presencas, situacao, usuario, senha, aproveitamento, criado_em)
              VALUES ({m}, {m}, {m}, 'Lição 1 - O Pecado e o Perdão', {m}, 1, 'Em Formação', {m}, {m}, 0.0, {m})"""
    executar_comando(sql, (aluno, classe, prof, dt, usuario, senha, datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=doutrina')

# PROFESSOR RESPONDE DÚVIDA DO ALUNO
@app.route('/doutrina/responder_duvida', methods=['POST'])
def doutrina_responder_duvida():
    duvida_id = request.form.get('duvida_id')
    resp_prof = request.form.get('resposta_professor', '').strip()
    prof_nome = request.form.get('professor_nome', 'Pastor / Instrutor').strip()
    if duvida_id and resp_prof:
        m = "%s" if DATABASE_URL else "?"
        sql = f"UPDATE duvidas_alunos SET resposta_professor = {m}, professor_nome = {m} WHERE id = {m}"
        executar_comando(sql, (resp_prof, prof_nome, duvida_id))
    return redirect('/?aba=doutrina')

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

# -------------------------------------------------------------
# ROTAS DO PORTAL DO ALUNO (/ensino/login, /ensino/aulas, etc.)
# -------------------------------------------------------------
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
            erro = "Usuário ou senha incorretos! Verifique na secretaria da igreja."
    return render_template('aluno_login.html', erro=erro)

@app.route('/ensino/logout')
def aluno_logout():
    session.clear()
    return redirect('/ensino/login')

@app.route('/ensino/aulas')
def aluno_aulas():
    aluno_id = session.get('aluno_id')
    if not aluno_id: return redirect('/ensino/login')

    m = "%s" if DATABASE_URL else "?"
    aluno = consultar_um(f"SELECT * FROM doutrina WHERE id = {m}", (aluno_id,))
    if not aluno: return redirect('/ensino/logout')

    registos_prog = consultar_todos(f"SELECT * FROM progresso_licoes WHERE aluno_id = {m}", (aluno_id,))
    mapa_prog = {r['licao_id']: r for r in registos_prog}

    licoes_status = {}
    todas_concluidas = True
    bloqueado_a_partir_daqui = False

    for idx, lic in enumerate(TODAS_LICOES):
        lid = lic['id']
        prog = mapa_prog.get(lid)

        if bloqueado_a_partir_daqui:
            licoes_status[lid] = {'status': 'bloqueada', 'nota': 0, 'resumo': None}
            todas_concluidas = False
            continue

        if prog and prog.get('nota_teste', 0) >= 70.0:
            licoes_status[lid] = {'status': 'concluida', 'nota': prog['nota_teste'], 'resumo': prog.get('resumo_aluno')}
        else:
            licoes_status[lid] = {'status': 'em_estudo', 'nota': prog['nota_teste'] if prog else 0, 'resumo': prog.get('resumo_aluno') if prog else None}
            bloqueado_a_partir_daqui = True
            todas_concluidas = False

    licao_pedida = request.args.get('licao')
    if not licao_pedida or licao_pedida not in MAPA_LICOES or licoes_status.get(licao_pedida, {}).get('status') == 'bloqueada':
        licao_atual_id = 'c1_l1'
        for lic in TODAS_LICOES:
            if licoes_status[lic['id']]['status'] == 'em_estudo':
                licao_atual_id = lic['id']
                break
    else:
        licao_atual_id = licao_pedida

    licao_ativa = MAPA_LICOES[licao_atual_id]
    info_prog_atual = licoes_status.get(licao_atual_id, {})

    notas_obtidas = [p['nota_teste'] for p in registos_prog if p.get('nota_teste', 0) > 0]
    media_global = round(sum(notas_obtidas) / len(notas_obtidas), 1) if notas_obtidas else 0.0
    
    executar_comando(f"UPDATE doutrina SET aproveitamento = {m} WHERE id = {m}", (media_global, aluno_id))
    aluno['aproveitamento'] = media_global

    duvidas = consultar_todos(f"SELECT * FROM duvidas_alunos WHERE aluno_id = {m} AND licao_id = {m} ORDER BY id DESC", (aluno_id, licao_atual_id))

    return render_template(
        'portal_aluno.html',
        aluno=aluno,
        curriculo=CURRICULO_CLASSES,
        licao=licao_ativa,
        progresso_atual=info_prog_atual,
        licoes_status=licoes_status,
        todas_concluidas=todas_concluidas,
        duvidas=duvidas
    )

@app.route('/ensino/submeter_resumo', methods=['POST'])
def aluno_submeter_resumo():
    aluno_id = session.get('aluno_id')
    if not aluno_id: return redirect('/ensino/login')

    licao_id = request.form.get('licao_id')
    resumo = request.form.get('resumo', '').strip()

    if not resumo or len(resumo) < 20:
        return "<script>alert('Por favor, escreva um resumo com o que aprendeu (mínimo de 20 caracteres).'); window.history.back();</script>"

    m = "%s" if DATABASE_URL else "?"
    existente = consultar_um(f"SELECT id FROM progresso_licoes WHERE aluno_id = {m} AND licao_id = {m}", (aluno_id, licao_id))

    if existente:
        sql = f"UPDATE progresso_licoes SET resumo_aluno = {m} WHERE id = {m}"
        executar_comando(sql, (resumo, existente['id']))
    else:
        sql = f"""INSERT INTO progresso_licoes (aluno_id, licao_id, resumo_aluno, nota_teste, status, criado_em)
                  VALUES ({m}, {m}, {m}, 0.0, 'Resumo Entregue', {m})"""
        executar_comando(sql, (aluno_id, licao_id, resumo, datetime.now().strftime('%Y-%m-%d %H:%M')))

    return redirect(f"/ensino/aulas?licao={licao_id}#teste")

@app.route('/ensino/submeter_teste', methods=['POST'])
def aluno_submeter_teste():
    aluno_id = session.get('aluno_id')
    if not aluno_id: return redirect('/ensino/login')

    licao_id = request.form.get('licao_id')
    if licao_id not in MAPA_LICOES: return redirect('/ensino/aulas')

    licao = MAPA_LICOES[licao_id]
    questoes = licao['questoes']
    total_q = len(questoes)
    acertos = 0

    for idx, q in enumerate(questoes):
        resp = request.form.get(f"q_{idx}")
        if resp is not None and int(resp) == q['c']:
            acertos += 1

    nota = round((acertos / total_q) * 100.0, 1) if total_q > 0 else 0.0

    m = "%s" if DATABASE_URL else "?"
    sql = f"UPDATE progresso_licoes SET nota_teste = {m}, status = {m} WHERE aluno_id = {m} AND licao_id = {m}"
    status_str = 'Concluída' if nota >= 70.0 else 'Repetir Teste'
    executar_comando(sql, (nota, status_str, aluno_id, licao_id))

    if nota >= 70.0:
        proxima_id = None
        for i, l in enumerate(TODAS_LICOES):
            if l['id'] == licao_id and (i + 1) < len(TODAS_LICOES):
                proxima_id = TODAS_LICOES[i + 1]['id']
                break
        if proxima_id:
            return redirect(f"/ensino/aulas?licao={proxima_id}&sucesso_aprovado=1")
    
    return redirect(f"/ensino/aulas?licao={licao_id}&nota_resultado={nota}")

@app.route('/ensino/duvida', methods=['POST'])
def aluno_duvida():
    aluno_id = session.get('aluno_id')
    if not aluno_id: return redirect('/ensino/login')

    licao_id = request.form.get('licao_id')
    pergunta = request.form.get('pergunta', '').strip()
    if not pergunta: return redirect(f"/ensino/aulas?licao={licao_id}")

    p_lower = pergunta.lower()
    resp_sistema = "A sua dúvida foi registada e encaminhada ao seu Professor/Mentor na IEAD Chicuque para orientação pastoral."
    if 'expiação' in p_lower:
        resp_sistema = "Manual IEADAO: Expiação é o perdão dos pecados com reconciliação divina através do sacrifício vicário de Cristo (Hb 9:19-28)."
    elif 'desobediência' in p_lower or 'transgressão' in p_lower:
        resp_sistema = "Manual IEADAO: Desobedecer é a causa oculta no coração; Transgredir é o efeito manifesto contra a Lei de Deus."
    elif 'comboio' in p_lower or 'sentimento' in p_lower:
        resp_sistema = "Manual IEADAO: O crente anda pela Fé nas Promessas (A Locomotiva do Facto). Os sentimentos são apenas o vagão que segue."

    m = "%s" if DATABASE_URL else "?"
    sql = f"""INSERT INTO duvidas_alunos (aluno_id, licao_id, pergunta, resposta_sistema, criado_em)
              VALUES ({m}, {m}, {m}, {m}, {m})"""
    executar_comando(sql, (aluno_id, licao_id, pergunta, resp_sistema, datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect(f"/ensino/aulas?licao={licao_id}#duvidas")

@app.route('/ensino/exame_final', methods=['GET', 'POST'])
def aluno_exame_final():
    aluno_id = session.get('aluno_id')
    if not aluno_id: return redirect('/ensino/login')
    m = "%s" if DATABASE_URL else "?"
    aluno = consultar_um(f"SELECT * FROM doutrina WHERE id = {m}", (aluno_id,))

    questoes_finais = [
        {'p': 'O que significa pecar conforme ensinado na Classe I?', 'ops': ['Apenas cometer crimes civis.', 'Errar o alvo de fazer a Vontade de Deus e ferir a Sua santidade.', 'Um acidente biológico.', 'Cometer enganos sem culpa.'], 'c': 1},
        {'p': 'Qual é a atitude correta sobre dízimos e ofertas (Classe II)?', 'ops': ['São opcionais e dispensáveis.', 'Uma devolução voluntária e obediente do que pertence ao Senhor.', 'Uma taxa governamental.', 'Apenas ofertas de campanhas têm valor.'], 'c': 1},
        {'p': 'Qual a definição de Fé em relação aos Sentimentos (Classe III)?', 'ops': ['A fé depende de nos sentirmos bem e alegres.', 'O crente vive pelo Facto da Palavra e a fé na promessa divina, independentemente das emoções.', 'Se não houver arrepio, não há fé.', 'A fé é ilusória.'], 'c': 1},
        {'p': 'Quem pode participar da Ceia do Senhor (Classe IV)?', 'ops': ['Qualquer pessoa que estiver no templo.', 'Todo o salvo, batizado e em plena comunhão, consciente do corpo de Cristo.', 'Apenas pastores e presbíteros.', 'Crianças não batizadas.'], 'c': 1}
    ]

    if request.method == 'POST':
        acertos = 0
        total_q = len(questoes_finais)
        for idx, q in enumerate(questoes_finais):
            if request.form.get(f"q_{idx}") == str(q['c']):
                acertos += 1
        nota_final = round((acertos / total_q) * 100.0, 1)

        if nota_final >= 70.0:
            executar_comando(f"UPDATE doutrina SET situacao = 'Graduado / Apto', aproveitamento = {m} WHERE id = {m}", (nota_final, aluno_id))
            return redirect(f"/ensino/certificado/{aluno_id}")
        else:
            flash(f"Obteve {nota_final}%. É necessário no mínimo 70% no Exame Final.")

    return render_template('aluno_exame_final.html', aluno=aluno, questoes=questoes_finais)

@app.route('/ensino/certificado/<int:aluno_id>')
def aluno_certificado(aluno_id):
    m = "%s" if DATABASE_URL else "?"
    aluno = consultar_um(f"SELECT * FROM doutrina WHERE id = {m}", (aluno_id,))
    if not aluno: return redirect('/ensino/login')
    
    return render_template(
        'certificado_ensino.html',
        aluno=aluno,
        data_extenso=datetime.now().strftime('%d de %B de %Y')
    )

# -------------------------------------------------------------
# DEMAIS ROTAS DA SECRETARIA, CULTOS, FINANÇAS E CONFIGURAÇÕES
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

@app.route('/secretaria/balanco', methods=['GET', 'POST'])
def secretaria_balanco():
    agora = datetime.now()
    ano_sel = request.args.get('ano', agora.year, type=int)

    if request.method == 'POST':
        fd = request.form
        ano_form = int(fd.get('ano_exercicio', ano_sel))
        planos_todos = consultar_todos("SELECT * FROM planificacao")
        m = "%s" if DATABASE_URL else "?"
        for p in planos_todos:
            pid = str(p['id'])
            if f"status_{pid}" in fd:
                st = fd.get(f"status_{pid}", p.get('status', 'Planeado')).strip()
                fb = fd.get(f"feedback_{pid}", p.get('feedback', '')).strip()
                dif = fd.get(f"dificuldades_{pid}", '').strip()
                persp = fd.get(f"perspectivas_{pid}", '').strip()
                
                def to_i(k):
                    v = fd.get(k)
                    return int(v) if v and v.isdigit() else 0
                h = to_i(f"part_h_{pid}")
                mulh = to_i(f"part_m_{pid}")
                j = to_i(f"part_j_{pid}")
                c = to_i(f"part_c_{pid}")
                tot = h + mulh + j + c

                sql_up = f"""UPDATE planificacao SET 
                             status = {m}, feedback = {m}, dificuldades = {m}, 
                             perspectivas = {m}, participantes_homens = {m}, 
                             participantes_mulheres = {m}, participantes_jovens = {m}, 
                             participantes_criancas = {m}, total_participantes = {m} 
                             WHERE id = {m}"""
                executar_comando(sql_up, (st, fb, dif, persp, h, mulh, j, c, tot, pid))

        c1 = fd.get('constrangimento_1', '').strip()
        c2 = fd.get('constrangimento_2', '').strip()
        c3 = fd.get('constrangimento_3', '').strip()
        p1 = fd.get('perspectiva_1', '').strip()
        p2 = fd.get('perspectiva_2', '').strip()
        p3 = fd.get('perspectiva_3', '').strip()

        existente = consultar_um(f"SELECT id FROM balanco_anual WHERE ano = {m}", (ano_form,))
        if existente:
            sql_bal = f"""UPDATE balanco_anual SET 
                          constrangimento_1 = {m}, constrangimento_2 = {m}, constrangimento_3 = {m},
                          perspectiva_1 = {m}, perspectiva_2 = {m}, perspectiva_3 = {m},
                          atualizado_em = {m} WHERE ano = {m}"""
            executar_comando(sql_bal, (c1, c2, c3, p1, p2, p3, datetime.now().strftime('%Y-%m-%d %H:%M'), ano_form))
        else:
            sql_bal = f"""INSERT INTO balanco_anual 
                          (ano, constrangimento_1, constrangimento_2, constrangimento_3, perspectiva_1, perspectiva_2, perspectiva_3, atualizado_em)
                          VALUES ({m}, {m}, {m}, {m}, {m}, {m}, {m}, {m})"""
            executar_comando(sql_bal, (ano_form, c1, c2, c3, p1, p2, p3, datetime.now().strftime('%Y-%m-%d %H:%M')))

        return redirect(f"/secretaria/relatorio-anual?sucesso_balanco=1")

    m = "%s" if DATABASE_URL else "?"
    planos = consultar_todos("SELECT * FROM planificacao ORDER BY id ASC")
    balanco = consultar_um(f"SELECT * FROM balanco_anual WHERE ano = {m}", (ano_sel,))
    return render_template('balanco_anual.html', ano_sel=ano_sel, planos=planos, balanco=balanco)

@app.route('/secretaria/relatorio-anual')
def secretaria_relatorio_anual():
    membros = consultar_todos("SELECT * FROM membros")
    planos = consultar_todos("SELECT * FROM planificacao")
    cultos = consultar_todos("SELECT * FROM cultos")
    convertidos = consultar_todos("SELECT * FROM novos_convertidos")

    agora = datetime.now()
    ano_atual = agora.year
    ano_anterior = ano_atual - 1

    meses_pt = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
        5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
        9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }
    data_mes_pt = meses_pt.get(agora.month, 'Outubro')
    data_dia = agora.strftime('%d')

    def extrair_genero(m):
        g = str(m.get('genero') or '').strip().lower()
        if g in ['f', 'feminino', 'mulher']: return 'F'
        if g in ['m', 'masculino', 'homem', 'h']: return 'H'
        c = str(m.get('cargo') or '').lower()
        d = str(m.get('departamento') or '').lower()
        nome = str(m.get('nome') or '').lower()
        if any(term in c for term in ['diaconisa', 'pastora', 'mãe']): return 'F'
        if any(term in d for term in ['senhora', 'círculo', 'mães']): return 'F'
        primeiro = nome.split()[0] if nome.split() else ''
        if primeiro.endswith('a') and primeiro not in ['costa', 'silva', 'munguambe', 'sousa', 'baptista', 'garcia']:
            return 'F'
        return 'H'

    def eh_atual(m):
        ano_str = str(ano_atual)
        ano_conv = str(m.get('ano_conversao') or '')
        data_bat = str(m.get('data_batismo') or '')
        criado = str(m.get('criado_em') or '')
        if ano_str in ano_conv or ano_str in data_bat or criado.startswith(ano_str):
            return True
        return False

    def calc_obreiros(termos):
        ant_h, ant_m, nov_h, nov_m = 0, 0, 0, 0
        for mb in membros:
            c = str(mb.get('cargo') or '').lower()
            if any(t in c for t in termos):
                gen = extrair_genero(mb)
                if eh_atual(mb):
                    if gen == 'F': nov_m += 1
                    else: nov_h += 1
                else:
                    if gen == 'F': ant_m += 1
                    else: ant_h += 1
        return {
            'ant_h': ant_h, 'ant_m': ant_m, 'ant_tot': ant_h + ant_m,
            'nov_h': nov_h, 'nov_m': nov_m, 'nov_tot': nov_h + nov_m,
            'tot_h': ant_h + nov_h, 'tot_m': ant_m + nov_m,
            'tot_geral': (ant_h + nov_h) + (ant_m + nov_m)
        }

    obreiros_dict = {
        'pastores': calc_obreiros(['pastor', 'pastora']),
        'presbiteros': calc_obreiros(['presb']),
        'evangelistas': calc_obreiros(['evang']),
        'diaconos': calc_obreiros(['diác', 'diac'])
    }
    sub_ant_h = sum([obreiros_dict[k]['ant_h'] for k in obreiros_dict])
    sub_ant_m = sum([obreiros_dict[k]['ant_m'] for k in obreiros_dict])
    sub_nov_h = sum([obreiros_dict[k]['nov_h'] for k in obreiros_dict])
    sub_nov_m = sum([obreiros_dict[k]['nov_m'] for k in obreiros_dict])
    obreiros_dict['subtotal'] = {
        'ant_h': sub_ant_h, 'ant_m': sub_ant_m, 'ant_tot': sub_ant_h + sub_ant_m,
        'nov_h': sub_nov_h, 'nov_m': sub_nov_m, 'nov_tot': sub_nov_h + sub_nov_m,
        'tot_h': sub_ant_h + sub_nov_h, 'tot_m': sub_ant_m + sub_nov_m,
        'tot_geral': (sub_ant_h + sub_nov_h) + (sub_ant_m + sub_nov_m)
    }

    cargos_obreiros = ['pastor', 'pastora', 'presb', 'evang', 'diác', 'diac']
    membros_comuns = [m for m in membros if not any(co in str(m.get('cargo') or '').lower() for co in cargos_obreiros)]

    def calc_comuns(condicao_fn):
        ant_h, ant_m, nov_h, nov_m = 0, 0, 0, 0
        for mb in membros_comuns:
            if condicao_fn(mb):
                gen = extrair_genero(mb)
                if eh_atual(mb):
                    if gen == 'F': nov_m += 1
                    else: nov_h += 1
                else:
                    if gen == 'F': ant_m += 1
                    else: ant_h += 1
        return {
            'ant_h': ant_h, 'ant_m': ant_m, 'ant_tot': ant_h + ant_m,
            'nov_h': nov_h, 'nov_m': nov_m, 'nov_tot': nov_h + nov_m,
            'tot_h': ant_h + nov_h, 'tot_m': ant_m + nov_m,
            'tot_geral': (ant_h + nov_h) + (ant_m + nov_m)
        }

    batizados_adultos = calc_comuns(lambda m: bool(m.get('data_batismo')) and str(m.get('estado_civil', '')).lower() != 'criança' and 'juventude' not in str(m.get('departamento', '')).lower())
    jovens_batizados = calc_comuns(lambda m: bool(m.get('data_batismo')) and ('juventude' in str(m.get('departamento', '')).lower() or 'jovem' in str(m.get('cargo', '')).lower()))
    jovens_nao_batizados = calc_comuns(lambda m: not bool(m.get('data_batismo')) and ('juventude' in str(m.get('departamento', '')).lower() or 'jovem' in str(m.get('cargo', '')).lower()) and str(m.get('estado_civil', '')).lower() != 'criança')
    boa_esperanca = calc_comuns(lambda m: str(m.get('estado_civil', '')).lower() == 'criança' or 'esperança' in str(m.get('departamento', '')).lower() or 'crian' in str(m.get('departamento', '')).lower())

    conv_ant_h, conv_ant_m, conv_nov_h, conv_nov_m = 0, 0, 0, 0
    for c in convertidos:
        dt = str(c.get('data_decisao') or c.get('criado_em') or '')
        atual = len(dt) >= 4 and dt[:4].isdigit() and int(dt[:4]) >= ano_atual
        nome = str(c.get('nome') or '').lower()
        primeiro = nome.split()[0] if nome.split() else ''
        gen = 'F' if primeiro.endswith('a') else 'H'
        if atual:
            if gen == 'F': conv_nov_m += 1
            else: conv_nov_h += 1
        else:
            if gen == 'F': conv_ant_m += 1
            else: conv_ant_h += 1

    novos_convertidos_dict = {
        'ant_h': conv_ant_h, 'ant_m': conv_ant_m, 'ant_tot': conv_ant_h + conv_ant_m,
        'nov_h': conv_nov_h, 'nov_m': conv_nov_m, 'nov_tot': conv_nov_h + conv_nov_m,
        'tot_h': conv_ant_h + conv_nov_h, 'tot_m': conv_ant_m + conv_nov_m,
        'tot_geral': (conv_ant_h + conv_nov_h) + (conv_ant_m + conv_nov_m)
    }

    membros_nao_dict = {
        'batizados_adultos': batizados_adultos,
        'jovens_batizados': jovens_batizados,
        'jovens_nao_batizados': jovens_nao_batizados,
        'novos_convertidos': novos_convertidos_dict,
        'boa_esperanca': boa_esperanca
    }

    sub_m_ant_h = sum([membros_nao_dict[k]['ant_h'] for k in membros_nao_dict])
    sub_m_ant_m = sum([membros_nao_dict[k]['ant_m'] for k in membros_nao_dict])
    sub_m_nov_h = sum([membros_nao_dict[k]['nov_h'] for k in membros_nao_dict])
    sub_m_nov_m = sum([membros_nao_dict[k]['nov_m'] for k in membros_nao_dict])
    membros_nao_dict['subtotal'] = {
        'ant_h': sub_m_ant_h, 'ant_m': sub_m_ant_m, 'ant_tot': sub_m_ant_h + sub_m_ant_m,
        'nov_h': sub_m_nov_h, 'nov_m': sub_m_nov_m, 'nov_tot': sub_m_nov_h + sub_m_nov_m,
        'tot_h': sub_m_ant_h + sub_m_nov_h, 'tot_m': sub_m_ant_m + sub_m_nov_m,
        'tot_geral': (sub_m_ant_h + sub_nov_h) + (sub_m_ant_m + sub_nov_m)
    }

    tot_geral_dict = {
        'ant_h': sub_ant_h + sub_m_ant_h, 'ant_m': sub_ant_m + sub_m_ant_m, 'ant_tot': (sub_ant_h + sub_m_ant_h) + (sub_ant_m + sub_m_ant_m),
        'nov_h': sub_nov_h + sub_m_nov_h, 'nov_m': sub_nov_m + sub_m_nov_m, 'nov_tot': (sub_nov_h + sub_m_nov_h) + (sub_nov_m + sub_m_nov_m),
        'tot_h': (sub_ant_h + sub_nov_h) + (sub_m_ant_h + sub_nov_h),
        'tot_m': (sub_ant_m + sub_nov_m) + (sub_m_ant_m + sub_nov_m),
        'tot_geral': (sub_ant_h + sub_nov_h + sub_m_ant_h + sub_m_nov_h) + (sub_ant_m + sub_nov_m + sub_m_ant_m + sub_m_nov_m)
    }

    planos_exec = [p for p in planos if str(p.get('status') or '').strip().lower() == 'executado']

    casamentos_jovens = len([p for p in planos_exec if ('casamento' in str(p.get('actividade', '')).lower() or 'matrim' in str(p.get('actividade', '')).lower()) and 'jov' in str(p.get('departamento', '')).lower()])
    casamentos_adultos = len([p for p in planos_exec if ('casamento' in str(p.get('actividade', '')).lower() or 'matrim' in str(p.get('actividade', '')).lower()) and 'jov' not in str(p.get('departamento', '')).lower()])

    batismos_exec = [p for p in planos_exec if any(b in str(p.get('actividade', '')).lower() or b in str(p.get('tipo_evento', '')).lower() for b in ['batismo', 'baptismo'])]
    batismos_locais = ', '.join(set([p.get('responsavel') or p.get('feedback') or 'Sede Chicuque' for p in batismos_exec])) if batismos_exec else '---'

    aniversarios = {'activista': 0, 'juventude': 0, 'boa_esperanca': 0, 'outros': 0}
    for p in planos_exec:
        act = (p.get('actividade') or p.get('tipo_evento') or '').lower()
        if 'anivers' in act:
            dep = str(p.get('departamento', '')).lower()
            if 'activ' in dep: aniversarios['activista'] += 1
            elif 'jov' in dep: aniversarios['juventude'] += 1
            elif 'crian' in dep or 'esperança' in dep: aniversarios['boa_esperanca'] += 1
            else: aniversarios['outros'] += 1

    seminarios_contagem = {'obreiros': 0, 'pais': 0, 'maes': 0, 'activista': 0, 'juventude': 0, 'batizados': 0, 'convertidos': 0, 'casados': 0, 'solteiros': 0, 'boa_esperanca': 0}
    temas_seminarios = []
    conferencias_contagem = {'obreiros': 0, 'pais': 0, 'maes': 0, 'activista': 0, 'juventude': 0, 'batizados': 0, 'convertidos': 0, 'casados': 0, 'solteiros': 0, 'boa_esperanca': 0}
    temas_conferencias = []

    for p in planos_exec:
        act = (p.get('actividade') or '').lower()
        tipo_ev = str(p.get('tipo_evento', '')).lower()
        dep = str(p.get('departamento', '')).lower()

        if 'semin' in act or 'semin' in tipo_ev:
            temas_seminarios.append({
                'data': p.get('data_execucao') or p.get('data_prevista'),
                'actividade': p.get('actividade') or p.get('titulo'),
                'departamento': p.get('departamento'),
                'feedback': p.get('feedback'),
                'total': p.get('total_participantes', 0),
                'h': p.get('participantes_homens', 0),
                'm': p.get('participantes_mulheres', 0),
                'j': p.get('participantes_jovens', 0),
                'c': p.get('participantes_criancas', 0)
            })
            if 'obreir' in dep or 'obreir' in act: seminarios_contagem['obreiros'] += 1
            elif 'pais' in dep or 'homens' in dep: seminarios_contagem['pais'] += 1
            elif 'mães' in dep or 'senhoras' in dep or 'círculo' in dep: seminarios_contagem['maes'] += 1
            elif 'activ' in dep: seminarios_contagem['activista'] += 1
            elif 'jov' in dep: seminarios_contagem['juventude'] += 1
            elif 'crian' in dep or 'esperança' in dep: seminarios_contagem['boa_esperanca'] += 1
            else: seminarios_contagem['obreiros'] += 1

        elif 'conferên' in act or 'conferen' in act or 'conferên' in tipo_ev:
            temas_conferencias.append({
                'data': p.get('data_execucao') or p.get('data_prevista'),
                'actividade': p.get('actividade') or p.get('titulo'),
                'departamento': p.get('departamento'),
                'feedback': p.get('feedback')
            })
            if 'obreir' in dep: conferencias_contagem['obreiros'] += 1
            elif 'jov' in dep: conferencias_contagem['juventude'] += 1
            elif 'mães' in dep: conferencias_contagem['maes'] += 1
            else: conferencias_contagem['obreiros'] += 1

    m = "%s" if DATABASE_URL else "?"
    balanco = consultar_um(f"SELECT * FROM balanco_anual WHERE ano = {m}", (ano_atual,))

    constrangimentos_lista = []
    perspectivas_lista = []

    if balanco:
        for k in ['constrangimento_1', 'constrangimento_2', 'constrangimento_3']:
            txt = str(balanco.get(k) or '').strip()
            if txt: constrangimentos_lista.append(txt)

        for k in ['perspectiva_1', 'perspectiva_2', 'perspectiva_3']:
            txt = str(balanco.get(k) or '').strip()
            if txt: perspectivas_lista.append(txt)

    for p in planos:
        dif = str(p.get('dificuldades') or '').strip()
        if dif and dif not in constrangimentos_lista:
            constrangimentos_lista.append(f"Actividade «{p.get('actividade')}» ({p.get('departamento')}): {dif}")
        psp = str(p.get('perspectivas') or '').strip()
        if psp and psp not in perspectivas_lista:
            perspectivas_lista.append(f"Actividade «{p.get('actividade')}» ({p.get('departamento')}): {psp}")

    rel = {
        'ano_atual': ano_atual,
        'ano_anterior': ano_anterior,
        'data_dia': data_dia,
        'data_mes': data_mes_pt,
        'obreiros': obreiros_dict,
        'membros_nao_obreiros': membros_nao_dict,
        'total_geral': tot_geral_dict,
        'casamentos': {'jovens': casamentos_jovens, 'adultos': casamentos_adultos, 'total': casamentos_jovens + casamentos_adultos},
        'atos': {
            'batismos_num': len(batismos_exec),
            'batismos_locais': batismos_locais,
            'inauguracoes_num': len([p for p in planos_exec if 'inaugura' in str(p.get('actividade', '')).lower()]),
            'inauguracoes_locais': '---',
            'pedras_num': len([p for p in planos_exec if 'pedra' in str(p.get('actividade', '')).lower()]),
            'pedras_locais': '---',
            'apresentacoes_num': len([p for p in planos_exec if 'apresenta' in str(p.get('actividade', '')).lower()]),
            'apresentacoes_locais': '---'
        },
        'aniversarios': aniversarios,
        'seminarios_contagem': seminarios_contagem,
        'temas_seminarios': temas_seminarios,
        'conferencias_contagem': conferencias_contagem,
        'temas_conferencias': temas_conferencias,
        'visitas': {'nac_h': 0, 'nac_m': 0, 'prov_h': 0, 'prov_m': 0, 'past_h': 0, 'past_m': 0, 'presb_h': 0, 'presb_m': 0, 'diac_h': 0, 'diac_m': 0, 'bapt_h': 0, 'bapt_m': 0, 'jov_h': 0, 'jov_m': 0},
        'perdas': {
            'desistentes_h': 0, 'desistentes_m': 0,
            'obitos_pastores': 0, 'obitos_maes_pastoras': 0, 'obitos_presbiteros': 0,
            'obitos_evangelistas': 0, 'obitos_diaconos': 0, 'obitos_baptizados': 0,
            'obitos_novos_convertidos': 0, 'obitos_juventude': 0, 'obitos_boa_esperanca': 0
        },
        'constrangimentos': constrangimentos_lista,
        'perspectivas': perspectivas_lista
    }

    return render_template('relatorio_anual_modelo.html', rel=rel)

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
    conta = fd.get('conta', 'Caixa Físico').strip()
    try: val = float(fd.get('valor') or 0)
    except: val = 0.0
    dt = fd.get('data_movimento', datetime.now().strftime('%Y-%m-%d')).strip()
    desc = fd.get('descricao', '').strip()
    
    destino_tipo = fd.get('destino_tipo', 'Igreja Geral').strip()
    depto = fd.get('departamento', 'Geral').strip()
    proposito = fd.get('proposito', '').strip()

    if tipo == 'Entrada':
        if destino_tipo == 'Igreja Mãe':
            categoria = "Igreja Mãe: " + fd.get('categoria_entrada_mae', 'Apoio da Sede').strip()
        elif destino_tipo == 'Departamento':
            categoria = f"Entrada: {depto}"
            tipo_dep = fd.get('categoria_entrada_depto', 'Oferta do Depto').strip()
            desc = f"{tipo_dep} | {desc}".strip(' |')
        else:
            categoria = fd.get('categoria', 'Dízimos').strip()
    else:
        if destino_tipo == 'Igreja Mãe':
            categoria = "Igreja Mãe: " + fd.get('categoria_saida_mae', 'Dízimo dos Dízimos').strip()
        elif destino_tipo == 'Departamento':
            categoria = f"Saída: {depto}"
            if proposito:
                desc = f"Propósito: {proposito} | {desc}".strip(' |')
        else:
            categoria = fd.get('categoria_saida_geral', 'Despesa Geral').strip()

    m = "%s" if DATABASE_URL else "?"
    sql = f"""INSERT INTO caixa 
              (tipo, categoria, valor, descricao, data_movimento, conta, destino_tipo, departamento, proposito, criado_em)
              VALUES ({m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m})"""
    executar_comando(sql, (tipo, categoria, val, desc, dt, conta, destino_tipo, depto, proposito, datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=tesouraria')

@app.route('/config/opcoes/adicionar', methods=['POST'])
def opcoes_adicionar():
    cat = request.form.get('categoria', '').strip()
    val = request.form.get('valor', '').strip()
    if cat and val:
        m = "%s" if DATABASE_URL else "?"
        executar_comando(f"INSERT INTO opcoes_sistema (categoria, valor) VALUES ({m}, {m})", (cat, val))
    return redirect('/?aba=configuracoes')

@app.route('/config/opcoes/editar', methods=['POST'])
def opcoes_editar():
    id_op = request.form.get('id')
    novo_val = request.form.get('valor', '').strip()
    if id_op and novo_val:
        m = "%s" if DATABASE_URL else "?"
        executar_comando(f"UPDATE opcoes_sistema SET valor = {m} WHERE id = {m}", (novo_val, id_op))
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
print("✓ app.py: Todas as rotas (incluindo /ensino/login, /secretaria/balanco e professor) unificadas com sucesso!")

# =============================================================================
# 2. VALIDAR E RECONSTRUIR DASHBOARD.HTML COM PAINEL DO PROFESSOR EM DOUTRINA
# =============================================================================
with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    dash_html = f.read()

# Bloco interativo do Professor em Doutrina para responder dúvidas e ver alunos
bloco_professor_doutrina = '''            <!-- PAINEL DO PROFESSOR: ACOMPANHAMENTO E RESPOSTA A DÚVIDAS -->
            <div class="lg:col-span-12 bg-white p-6 rounded-2xl shadow-sm border-2 border-indigo-200 space-y-4">
                <div class="border-b pb-2 flex justify-between items-center">
                    <div>
                        <h3 class="font-extrabold text-base text-indigo-950 flex items-center gap-2">
                            <span>👨‍🏫</span> Gabinete do Instrutor / Professor de Doutrina & Discipulado
                        </h3>
                        <p class="text-[11px] text-slate-500">Acompanhamento pastoral direto: responda às dúvidas bíblicas enviadas pelos seus formandos.</p>
                    </div>
                    <span class="bg-amber-100 text-amber-900 px-3 py-1 rounded-full text-xs font-black">
                        {{ duvidas_pendentes|length }} Dúvidas Pendentes
                    </span>
                </div>

                <!-- LISTA DE DÚVIDAS ENVIADAS PELOS ALUNOS PARA O PROFESSOR RESPONDER -->
                <div class="space-y-3">
                    {% for d in duvidas_pendentes %}
                    <div class="p-4 bg-slate-50 rounded-2xl border border-slate-200 text-xs space-y-2">
                        <div class="flex justify-between items-center font-bold text-slate-800">
                            <span>❓ Pergunta do Aluno: "{{ d.pergunta }}"</span>
                            <span class="text-[10px] text-slate-400">{{ d.criado_em }}</span>
                        </div>
                        <form action="/doutrina/responder_duvida" method="POST" class="space-y-2">
                            <input type="hidden" name="duvida_id" value="{{ d.id }}">
                            <div class="grid grid-cols-1 sm:grid-cols-4 gap-2">
                                <input type="text" name="professor_nome" value="Pastor / Instrutor" placeholder="Seu Nome / Cargo" class="h-9 px-2.5 border rounded-xl bg-white font-bold">
                                <input type="text" name="resposta_professor" required placeholder="Escreva a resposta pastoral para o aluno..." class="sm:col-span-2 h-9 px-3 border-2 border-indigo-300 rounded-xl bg-white font-medium focus:outline-none">
                                <button type="submit" class="h-9 bg-indigo-700 hover:bg-indigo-800 text-white font-black rounded-xl shadow">
                                    Enviar Resposta ao Aluno
                                </button>
                            </div>
                        </form>
                    </div>
                    {% else %}
                    <p class="text-xs text-slate-400 py-2 italic text-center">Nenhuma dúvida bíblica pendente de resposta no momento.</p>
                    {% endfor %}
                </div>
            </div>'''

if 'Gabinete do Instrutor / Professor' not in dash_html:
    dash_html = dash_html.replace(
        '<div class="lg:col-span-8 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">\n                <h3 class="font-bold text-base mb-4 border-b pb-2">📋 Lista de Formandos & Acompanhamento</h3>',
        bloco_professor_doutrina + '\n\n            <div class="lg:col-span-8 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">\n                <h3 class="font-bold text-base mb-4 border-b pb-2">📋 Lista de Formandos & Acompanhamento</h3>'
    )

env = jinja2.Environment()
env.parse(dash_html)
with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(dash_html)
print("✓ templates/dashboard.html: Painel do Professor integrado com validação Jinja2!")

# =============================================================================
# 3. ATUALIZAR TEMPLATES/PORTAL_ALUNO.HTML COM DESTAQUE DO PROFESSOR E RESPOSTA
# =============================================================================
with open('templates/portal_aluno.html', 'r', encoding='utf-8') as f:
    portal_html = f.read()

# Exibir respostas do professor de forma destacada no Espaço Tira-Dúvidas
bloco_duvidas_aluno_novo = '''                        <div class="space-y-2">
                            {% for d in duvidas %}
                            <div class="p-3 bg-slate-50 rounded-xl text-xs space-y-1.5 border border-slate-200">
                                <div class="font-bold text-slate-800 flex justify-between">
                                    <span>❓ Sua Pergunta: "{{ d.pergunta }}"</span>
                                    <span class="text-[10px] text-slate-400">{{ d.criado_em }}</span>
                                </div>
                                {% if d.resposta_professor %}
                                <div class="p-2.5 bg-emerald-50 border border-emerald-300 rounded-lg text-emerald-950 text-[11px] leading-relaxed">
                                    <b class="text-emerald-800 block">👨‍🏫 Resposta do seu Professor ({{ d.professor_nome or 'Pastor' }}):</b>
                                    {{ d.resposta_professor }}
                                </div>
                                {% else %}
                                <div class="p-2.5 bg-white border border-indigo-100 rounded-lg text-indigo-950 text-[11px] leading-relaxed">
                                    <b class="text-indigo-800 block">📖 Orientação do Manual:</b>
                                    {{ d.resposta_sistema }}
                                    <span class="text-[10px] text-slate-400 block mt-1 italic">⏳ Aguardando comentário adicional do seu professor...</span>
                                </div>
                                {% endif %}
                            </div>
                            {% endfor %}
                        </div>'''

if 'Resposta do seu Professor' not in portal_html:
    portal_html = re.sub(
        r'<div class="space-y-2">\s*{% for d in duvidas %}[\s\S]*?{% endfor %}\s*<\/div>',
        bloco_duvidas_aluno_novo,
        portal_html
    )

# Adicionar no topo do portal o card do Professor / Pai na Fé
if 'Instrutor Responsável' not in portal_html:
    portal_html = portal_html.replace(
        '<span class="text-sm font-extrabold text-white">{{ aluno.classe }}</span>',
        '<span class="text-sm font-extrabold text-white">{{ aluno.classe }}</span>\n                <span class="text-[10px] uppercase font-bold text-amber-300 block mt-2">Instrutor / Pai na Fé</span>\n                <span class="text-xs font-bold text-white">{{ aluno.professor or "Pastor Dirigente" }}</span>'
    )

env.parse(portal_html)
with open('templates/portal_aluno.html', 'w', encoding='utf-8') as f:
    f.write(portal_html)
print("✓ templates/portal_aluno.html: Conexão com o Professor configurada!")

print("=" * 80)
print(">>> INSTALAÇÃO CONCLUÍDA COM SUCESSO ABSOLUTO! <<<")
print("=" * 80)