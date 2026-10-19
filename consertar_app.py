import os
import py_compile

print("=" * 80)
print("A RECONSTRUIR APP.PY DE FORMA LIMPA E LINEAR...")
print("=" * 80)

app_code = '''import os
import sqlite3
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'iead_mz_portal_nacional_2026')

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db():
    if DATABASE_URL:
        import psycopg2
        import psycopg2.extras
        url = DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return psycopg2.connect(url, sslmode='require')
    else:
        conn = sqlite3.connect('igreja.db')
        conn.row_factory = sqlite3.Row
        return conn

def executar_comando(sql, params=()):
    conn = get_db()
    cur = conn.cursor()
    try:
        if DATABASE_URL:
            sql = sql.replace('?', '%s')
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
        if DATABASE_URL:
            sql = sql.replace('?', '%s')
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

    if not consultar_um("SELECT id FROM congregacoes WHERE id = 1"):
        sql_c = """INSERT INTO congregacoes (id, nome, provincia, distrito, bairro, pastor_responsavel, criado_em)
                    VALUES (1, 'Sede Regional de Chicuque', 'Inhambane', 'Maxixe (Cidade/Distrito)', 'Chicuque', 'Pastor Dirigente', ?)"""
        executar_comando(sql_c, (datetime.now().strftime('%Y-%m-%d %H:%M'),))

    perfis_padrao = [
        ('Administrador Geral', 'admin', 'admin123', 'geral', 'admin', 1, 'Inhambane', 'Maxixe (Cidade/Distrito)'),
        ('Pastor Presidente', 'pastor', 'pastor123', 'lideranca', 'lideranca', 1, 'Inhambane', 'Maxixe (Cidade/Distrito)'),
        ('Secretaria Executiva', 'secretaria', 'sec123', 'secretaria', 'secretario', 1, 'Inhambane', 'Maxixe (Cidade/Distrito)'),
        ('Tesouraria da Igreja', 'tesouraria', 'tesouro123', 'tesouraria', 'tesoureiro', 1, 'Inhambane', 'Maxixe (Cidade/Distrito)')
    ]
    for n, u, s, niv, perf, cid, prov, dist in perfis_padrao:
        existente = consultar_um("SELECT id FROM usuarios_sistema WHERE usuario = ?", (u,))
        if not existente:
            sql_u = """INSERT INTO usuarios_sistema (nome, usuario, senha, nivel, perfil, congregacao_id, provincia, distrito, criado_em)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
            executar_comando(sql_u, (n, u, s, niv, perf, cid, prov, dist, datetime.now().strftime('%Y-%m-%d %H:%M')))
        else:
            executar_comando("UPDATE usuarios_sistema SET perfil = ?, nivel = ? WHERE id = ?", (perf, niv, existente['id']))

    if not consultar_um("SELECT id FROM doutrina WHERE LOWER(usuario) = ?", ('anselmo',)):
        sql_al = """INSERT INTO doutrina 
                    (nome_aluno, classe, professor, licao_atual, data_inicio, presencas, situacao, usuario, senha, aproveitamento, criado_em)
                    VALUES (?, 'Classe I - Primeiros Passos', 'Pastor Dirigente', 'Lição 1 - O Pecado e o Perdão', '2026-01-01', 1, 'Em Formação', ?, ?, 0.0, ?)"""
        executar_comando(sql_al, ('Anselmo Munguambe', 'anselmo', '123456', datetime.now().strftime('%Y-%m-%d %H:%M')))

inicializar_banco()

# =============================================================================
# CURRÍCULO DE ENSINO: CONTEÚDO INTEGRAL E PROFUNDO (MANUAL DA IEADAO)
# =============================================================================
CURRICULO_CLASSES = [
    {
        'id_classe': 'classe_1',
        'nome_classe': 'Classe I - Primeiros Passos',
        'descricao': 'Rudimentos da Fé Cristã e Fundamentos da Salvação',
        'licoes': [
            {
                'id': 'c1_l1', 'numero': 'Lição 1', 'titulo': 'O Pecado e o Perdão',
                'texto_aureo': 'Porque o salário do pecado é a morte, mas o dom gratuito de Deus é a vida eterna, por Cristo Jesus nosso Senhor. (Rm 6:23)',
                'leitura_base': 'Rm 3:23; Is 59:2; 1Jo 1:7-9; Pv 28:13; Hb 9:22',
                'conteudo': 'Pecar significa literalmente "Errar o Alvo" da Santa Vontade de Deus. Desobedecer é a causa no coração e Transgredir é o efeito visível contra a Lei moral. Na cruz, Cristo operou a Expiação e deu-nos reconciliação.',
                'conteudo_completo': {
                    'introducao': 'Se o pecado não fosse uma triste realidade, seria desnecessária a Salvação consumada por Jesus no Calvário. A doutrina bíblica do pecado e da redenção é o alicerce fundamental para a caminhada cristã.',
                    'pontos_doutrinarios': [
                        {'titulo': '1. O Significado de Pecar: Errar o Alvo', 'detalhes': 'Pecar significa literalmente "Errar o Alvo", isto é, errar o alvo de fazer a Vontade de Deus e assim ferirmos a Sua santidade e os Seus propósitos para as nossas vidas.'},
                        {'titulo': '2. Transgressão e Desobediência à Lei Moral de Deus', 'detalhes': 'Pecar significa Transgredir a Lei de Deus. Desobedecer é a causa oculta no coração e Transgredir o efeito manifesto nas ações.'},
                        {'titulo': '3. Lista de Pecados Condenados pelas Escrituras', 'detalhes': 'A Bíblia condena as obras da carne que afastam o homem de Deus: Marcos 7:21-22; Romanos 1:29-31; Gálatas 5:19-21.'},
                        {'titulo': '4. A Situação do Homem Perante o Pecado', 'tabela': [
                            {'situacao': 'Imoralidade', 'descricao': 'Desfiguração total da imagem divina.', 'versiculos': 'Rm 3:9-12'},
                            {'situacao': 'Inimigo', 'descricao': 'Separação espiritual da presença de Deus.', 'versiculos': 'Is 59:2; Gl 5:4'},
                            {'situacao': 'Morte', 'descricao': 'Separação definitiva e eterna do Criador.', 'versiculos': 'Rm 3:23; Rm 6:23a'}
                        ]},
                        {'titulo': '5. Posição do Homem para se Libertar do Pecado', 'detalhes': 'Reconhecer, Saber do amor de Deus, Arrepender-se sinceramente e Crer/Aceitar a Cristo como Salvador e Senhor.'},
                        {'titulo': '6. O Perdão de Deus: Expiação e Substituição', 'detalhes': 'Cristo pagou com a Sua própria vida inocente o preço justo da ira santa de Deus. Quando Cristo perdoa, retira o pecado e coloca Amor, Graça, Paz e Gozo.'}
                    ],
                    'proverbio_chave': 'O que encobre as suas transgressões, nunca prosperará; mas o que as confessa e deixa, alcançará misericórdia. (Provérbios 28:13)'
                },
                'questoes': [
                    {'p': 'Qual é a diferença entre desobedecer e transgredir ensinada no Manual?', 'ops': ['Transgredir é no coração e desobedecer é o ato físico.', 'Desobedecer é a causa oculta no coração e transgredir é o efeito exposto.', 'Não há qualquer diferença bíblica.', 'Desobedecer aplica-se só a crianças.'], 'c': 1},
                    {'p': 'O que acontece espiritualmente quando Cristo perdoa o crente segundo a Lição 1?', 'ops': ['Apenas adia o castigo temporal.', 'Não só tira o pecado (o mal), mas coloca algo santo que o substitui (Amor, Graça, Paz e Gozo).', 'Exige pagamento monetário à congregação.', 'Dispensa a necessidade de oração.'], 'c': 1},
                    {'p': 'Conforme a tabela da Situação do Homem perante o Pecado, o que descreve a Imoralidade?', 'ops': ['Desfiguração da imagem divina (Rm 3:9-12).', 'Apenas a perda de bens materiais.', 'Sentimento passageiro de desânimo.', 'Infração de regras civis de trânsito.'], 'c': 0}
                ]
            },
            {
                'id': 'c1_l2', 'numero': 'Lição 2', 'titulo': 'Salvação e Senhorio de Cristo',
                'texto_aureo': 'Assim que, se alguém está em Cristo, nova criatura é; as coisas velhas já passaram; eis que tudo se fez novo. (2Co 5:17)',
                'leitura_base': 'Ef 2:8-10; Jo 1:12; 1Co 8:6; Cl 1:21-22',
                'conteudo': 'Somos salvos pela graça por meio da fé, e as obras acompanham como fruto. Cristo quer ser Salvador e dominar como Senhor sobre o trono do nosso coração.',
                'conteudo_completo': {
                    'introducao': 'Somos salvos pela graça mediante a fé. As boas obras são o resultado e fruto inseparável da salvação operada no coração regenerado.',
                    'pontos_doutrinarios': [
                        {'titulo': '1. Passos para a Filiação Divina', 'detalhes': 'Ouvir, Crer, Arrepender-se, Confessar e Receber a Cristo no trono do coração.'},
                        {'titulo': '2. Cristo Salvador e Senhor', 'detalhes': 'Cristo não quer só salvar da condenação, mas reinar sobre a conduta do cristão.'}
                    ],
                    'proverbio_chave': 'Cristo quer governar como Senhor em todas as áreas da nossa vida.'
                },
                'questoes': [
                    {'p': 'Qual é a relação entre fé, obras e salvação em Efésios 2:8-10?', 'ops': ['As obras compram o perdão.', 'Somos salvos pela graça por meio da fé, e as obras acompanham como fruto.', 'O crente salvo não precisa de praticar boas obras.', 'A fé sem moralidade basta.'], 'c': 1}
                ]
            },
            {
                'id': 'c1_l5', 'numero': 'Lição 5', 'titulo': 'A Bíblia - Manual de Fé dos Cristãos',
                'texto_aureo': 'Lâmpada para os meus pés é a tua palavra e luz para o meu caminho. (Sl 119:105)',
                'leitura_base': '2Tm 3:16; Js 1:8; Sl 1:2; 2Pe 1:21',
                'conteudo': 'A Bíblia contém 66 livros (39 no AT e 27 no NT). O Autor é Deus, o Intérprete é o Espírito Santo e o Tema Central é Jesus Cristo.',
                'conteudo_completo': {
                    'introducao': 'A Bíblia é infalível, inerrante e a nossa suprema regra de fé e prática.',
                    'pontos_doutrinarios': [
                        {'titulo': '1. Inspiração Divina', 'detalhes': 'Escrita por cerca de 40 homens num período de 1600 anos sob a inspiração do Espírito Santo.'},
                        {'titulo': '2. Estrutura Canónica', 'detalhes': '39 livros no Antigo Testamento e 27 no Novo Testamento (Total: 66 livros).'}
                    ],
                    'proverbio_chave': 'Toda a Escritura é divinamente inspirada e proveitosa. (2Tm 3:16)'
                },
                'questoes': [
                    {'p': 'Quantos livros compõem o cânon bíblico?', 'ops': ['39 no Antigo Testamento e 27 no Novo Testamento (Total: 66 livros).', '46 no AT e 27 no NT.', '30 no AT e 36 no NT.', '50 no AT e 16 no NT.'], 'c': 0}
                ]
            }
        ]
    },
    {
        'id_classe': 'classe_2', 'nome_classe': 'Classe II - Vida Cristã', 'descricao': 'Disciplina Espiritual, Oração e Jejum',
        'licoes': [
            {
                'id': 'c2_l1', 'numero': 'Lição 1', 'titulo': 'Oração e Jejum',
                'texto_aureo': 'Servindo a Deus em jejuns e orações, de noite e de dia. (Lc 2:37)',
                'leitura_base': '1Ts 5:17; Is 58:6-7; Mt 6:16-18; Zc 7:5',
                'conteudo': 'Orar é um mandamento vital. O jejum quebranta a carne e aguça a sensibilidade espiritual.',
                'conteudo_completo': {
                    'introducao': 'A oração é a respiração da alma e o jejum é o domínio do corpo para sensibilidade espiritual.',
                    'pontos_doutrinarios': [
                        {'titulo': '1. Oração Contínua', 'detalhes': 'Orar sem cessar (1Ts 5:17).'},
                        {'titulo': '2. Jejum Bíblico', 'detalhes': 'Acompanhado de arrependimento e atos de misericórdia (Is 58).'}
                    ],
                    'proverbio_chave': 'O importante no jejum é para quem o fazemos.'
                },
                'questoes': [
                    {'p': 'Qual é o verdadeiro espírito do jejum segundo Isaías 58?', 'ops': ['Exibição de piedade.', 'Quebrantamento para sensibilidade espiritual acompanhado de amor ao próximo.', 'Greve de fome.', 'Apenas dieta corporal.'], 'c': 1}
                ]
            }
        ]
    },
    {
        'id_classe': 'classe_3', 'nome_classe': 'Classe III - Maturidade Cristã', 'descricao': 'Santificação e Firmeza da Fé',
        'licoes': [
            {
                'id': 'c3_l2', 'numero': 'Lição 5', 'titulo': 'Fé: Factos, Não Sentimentos',
                'texto_aureo': 'A fé é o firme fundamento das coisas que se esperam. (Hb 11:1)',
                'leitura_base': '2Co 5:7; 2Tm 3:14-16; Jr 17:9',
                'conteudo': 'A Locomotiva é o FACTO (a Palavra de Deus), o Carro de Ligação é a FÉ e o Vagão são os SENTIMENTOS.',
                'conteudo_completo': {
                    'introducao': 'O crente vive por fé na Palavra infalível de Deus e não pelas emoções passageiras.',
                    'pontos_doutrinarios': [
                        {'titulo': '1. A Ilustração do Comboio', 'detalhes': 'O comboio anda pela locomotiva dos Factos da Palavra, nunca pelo vagão dos sentimentos.'}
                    ],
                    'proverbio_chave': 'Andamos por fé e não por vista. (2Co 5:7)'
                },
                'questoes': [
                    {'p': 'Na analogia do comboio da fé, o que representa a Locomotiva?', 'ops': ['Os sentimentos de alegria.', 'O Facto soberano de Deus e as promessas da Sua Palavra.', 'A aprovação dos homens.', 'Os nossos jejuns.'], 'c': 1}
                ]
            }
        ]
    },
    {
        'id_classe': 'classe_4', 'nome_classe': 'Classe IV - Candidatos ao Baptismo', 'descricao': 'Ordenanças Sagradas',
        'licoes': [
            {
                'id': 'c4_l1', 'numero': 'Lição 1', 'titulo': 'Baptismo nas Águas e Ceia do Senhor',
                'texto_aureo': 'De sorte que foram baptizados os que de bom grado receberam a sua palavra. (At 2:41)',
                'leitura_base': 'Rm 6:4; 1Co 11:23-29; Mt 28:19',
                'conteudo': 'O Baptismo simboliza morte e ressurreição com Cristo. A Santa Ceia contempla Passado, Presente e Futuro.',
                'conteudo_completo': {
                    'introducao': 'As duas ordenanças da Igreja: Baptismo por imersão e a Santa Ceia.',
                    'pontos_doutrinarios': [
                        {'titulo': '1. Baptismo nas Águas', 'detalhes': 'Testemunho público de morte para o pecado e ressurreição para Deus.'},
                        {'titulo': '2. As 3 Dimensões da Ceia', 'detalhes': 'Passado Comemorativo, Presente Instrutivo e Futuro Inspirador.'}
                    ],
                    'proverbio_chave': 'Fazei isto em memória de mim até que Ele venha.'
                },
                'questoes': [
                    {'p': 'Quais são as três dimensões da Ceia do Senhor segundo o Manual?', 'ops': ['Passado Comemorativo, Presente Instrutivo e Futuro Inspirador.', 'Ontem, hoje e amanhã.', 'Nenhum olhar específico.', 'Apenas recordar os discípulos.'], 'c': 0}
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

# =============================================================================
# CONTEXT PROCESSOR COMPLETO
# =============================================================================
@app.context_processor
def injetar_dados():
    u_id = session.get('usuario_id')
    user = consultar_um("SELECT * FROM usuarios_sistema WHERE id = ?", (u_id,)) if u_id else None
    
    membros = consultar_todos("SELECT * FROM membros ORDER BY id DESC")
    planos = consultar_todos("SELECT * FROM planificacao ORDER BY id DESC")
    cultos = consultar_todos("SELECT * FROM cultos ORDER BY id DESC")
    convertidos = consultar_todos("SELECT * FROM novos_convertidos ORDER BY id DESC")
    caixa = consultar_todos("SELECT * FROM caixa ORDER BY id DESC")
    doutrina = consultar_todos("SELECT * FROM doutrina ORDER BY id DESC")
    casamentos = consultar_todos("SELECT * FROM casamentos ORDER BY id DESC")
    obitos = consultar_todos("SELECT * FROM obitos ORDER BY id DESC")
    usuarios_todos = consultar_todos("SELECT id, nome, usuario, perfil, nivel, criado_em FROM usuarios_sistema ORDER BY id ASC")
    duvidas_pendentes = consultar_todos("SELECT * FROM duvidas_alunos WHERE resposta_professor IS NULL OR resposta_professor = '' ORDER BY id DESC")
    opcoes_lista = consultar_todos("SELECT * FROM opcoes_sistema ORDER BY categoria, valor ASC")

    opcoes_map = {}
    for op in opcoes_lista:
        opcoes_map.setdefault(op['categoria'], []).append(op)

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

    for m in membros:
        gen = str(m.get('genero') or '').lower()
        if gen in ['f', 'feminino', 'mulher']: total_mulheres += 1
        else: total_homens += 1

        ec = str(m.get('estado_civil') or '').lower()
        dep = str(m.get('departamento') or '').lower()
        if ec == 'criança' or 'esperança' in dep or 'crian' in dep: total_criancas += 1
        elif 'jov' in dep or 'juventude' in dep: total_jovens += 1
        else: total_adultos += 1

        if m.get('data_batismo'): total_batizados += 1
        else: total_nao_batizados += 1

        z = m.get('zona') or 'Zona 1 - Central'
        zonas_contagem[z] = zonas_contagem.get(z, 0) + 1

        cel = m.get('celula') or 'Célula Betel'
        celulas_contagem[cel] = celulas_contagem.get(cel, 0) + 1

        cg = m.get('cargo') or 'Membro em Comunhão'
        cargos_contagem[cg] = cargos_contagem.get(cg, 0) + 1

    total_pres = sum([int(c.get('total_presentes') or 0) for c in cultos])
    media_culto = int(total_pres / len(cultos)) if cultos else 0

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

    planos_executados = len([p for p in planos if p.get('status') == 'Executado'])
    taxa_execucao = int((planos_executados / len(planos) * 100)) if planos else 0

    return {
        'usuario_logado': user,
        'usuarios_todos': usuarios_todos,
        'congregacao': {'nome': 'Sede Regional de Chicuque', 'distrito': 'Maxixe (Cidade/Distrito)', 'provincia': 'Inhambane'},
        'membros': membros, 'planificacoes': planos, 'cronograma': planos,
        'cultos': cultos, 'convertidos': convertidos, 'caixa': caixa,
        'doutrina': doutrina, 'casamentos': casamentos, 'obitos': obitos,
        'duvidas_pendentes': duvidas_pendentes, 'opcoes': opcoes_map,
        'demografia': {
            'total_almas': len(membros) + len(convertidos),
            'membros_cadastrados': len(membros),
            'homens': total_homens,
            'mulheres': total_mulheres,
            'perc_mulheres': int((total_mulheres / len(membros) * 100)) if membros else 50,
            'perc_homens': int((total_homens / len(membros) * 100)) if membros else 50,
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
            'planos_executados': planos_executados,
            'taxa_execucao': taxa_execucao
        },
        'kpis': {
            'total_membros': len(membros),
            'total_planos': len(planos),
            'planos_executados': planos_executados,
            'taxa_execucao': taxa_execucao,
            'total_cultos': len(cultos),
            'media_assistencia': media_culto,
            'total_convertidos': len(convertidos),
            'total_entradas': total_entradas,
            'total_saidas': total_saidas,
            'saldo_caixa': saldo_caixa,
            'saldo_caixa_fisico': saldo_caixa_fisico,
            'saldo_banco': saldo_banco,
            'geral_in': geral_in, 'geral_out': geral_out,
            'mae_in': mae_in, 'mae_out': mae_out,
            'depto_in': depto_in, 'depto_out': depto_out,
            'total_dizimos': total_dizimos, 'total_ofertas': total_ofertas,
            'total_missoes': total_missoes, 'taxa_gasto': taxa_gasto,
            'categorias_caixa': categorias_caixa_valores,
            'total_doutrina': len(doutrina)
        }
    }

# =============================================================================
# ROTAS DE AUTENTICAÇÃO, LOGOUT E NAVEGAÇÃO SEGURA POR PERFIS
# =============================================================================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/ensino/logout')
def aluno_logout():
    session.clear()
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        usuario = request.form.get('usuario', '').strip().lower()
        senha = request.form.get('senha', '').strip()

        # 1. Aluno / Estudante
        aluno = consultar_um("SELECT * FROM doutrina WHERE LOWER(usuario) = ? AND senha = ?", (usuario, senha))
        if aluno:
            session.clear()
            session['aluno_id'] = aluno['id']
            session['aluno_nome'] = aluno['nome_aluno']
            session['usuario_perfil'] = 'aluno'
            return redirect('/ensino/aulas')

        # 2. Utilizadores Administrativos
        u = consultar_um("SELECT * FROM usuarios_sistema WHERE LOWER(usuario) = ? AND senha = ?", (usuario, senha))
        if u:
            session.clear()
            session['usuario_id'] = u['id']
            session['usuario_nome'] = u['nome']
            session['usuario_perfil'] = u['perfil']
            session['usuario_nivel'] = u.get('nivel', 'local')
            session['congregacao_id'] = u.get('congregacao_id', 1)

            if u['perfil'] == 'tesoureiro':
                return redirect('/?aba=tesouraria')
            elif u['perfil'] == 'secretario':
                return redirect('/?aba=membros')
            elif u['perfil'] in ['lideranca', 'pastor']:
                return redirect('/?aba=dashboard')
            else:
                return redirect('/?aba=dashboard')
        else:
            erro = "Credenciais inválidas! Verifique o utilizador e a palavra-passe."

    return render_template('login.html', erro=erro)

@app.route('/')
def index():
    if not session.get('usuario_id') and not session.get('aluno_id'):
        return redirect('/login')

    if session.get('usuario_perfil') == 'aluno':
        return redirect('/ensino/aulas')

    perfil = session.get('usuario_perfil', '')
    aba = request.args.get('aba')

    if not aba:
        if perfil == 'secretario': aba = 'membros'
        elif perfil == 'tesoureiro': aba = 'tesouraria'
        else: aba = 'dashboard'

    if perfil == 'secretario':
        if aba in ['financas', 'tesouraria', 'doutrina']:
            return redirect('/?aba=membros')
    elif perfil == 'tesoureiro':
        if aba not in ['financas', 'tesouraria']:
            return redirect('/?aba=tesouraria')
    elif perfil in ['pastor', 'lideranca']:
        if aba in ['tesouraria', 'configuracoes']:
            return redirect('/?aba=financas')

    id_relatar = request.args.get('relatar_id')
    plano_para_relatar = None
    if id_relatar:
        plano_para_relatar = consultar_um("SELECT * FROM planificacao WHERE id = ?", (id_relatar,))
    return render_template('dashboard.html', aba_ativa=aba, plano_relatar=plano_para_relatar)

# =============================================================================
# GESTÃO DE UTILIZADORES E RECUPERAÇÃO DE SENHAS (ADMIN)
# =============================================================================
@app.route('/admin/usuarios/novo', methods=['POST'])
def admin_usuario_novo():
    if session.get('usuario_perfil') != 'admin':
        return redirect('/login')
    fd = request.form
    nome, usuario, senha, perfil = fd.get('nome', '').strip(), fd.get('usuario', '').strip().lower(), fd.get('senha', '123456').strip(), fd.get('perfil', 'secretario').strip()
    if nome and usuario and senha:
        existente = consultar_um("SELECT id FROM usuarios_sistema WHERE LOWER(usuario) = ?", (usuario,))
        if existente:
            return "<script>alert('Este utilizador já existe!'); window.history.back();</script>"
        executar_comando("INSERT INTO usuarios_sistema (nome, usuario, senha, nivel, perfil, criado_em) VALUES (?, ?, ?, ?, ?, ?)",
                         (nome, usuario, senha, perfil, perfil, datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=configuracoes')

@app.route('/admin/usuarios/redefinir_senha', methods=['POST'])
def admin_usuario_redefinir_senha():
    if session.get('usuario_perfil') != 'admin':
        return redirect('/login')
    uid, nova = request.form.get('usuario_id'), request.form.get('nova_senha', '').strip()
    if uid and nova:
        executar_comando("UPDATE usuarios_sistema SET senha = ? WHERE id = ?", (nova, uid))
    return redirect('/?aba=configuracoes')

@app.route('/admin/usuarios/excluir/<int:id>')
def admin_usuario_excluir(id):
    if session.get('usuario_perfil') != 'admin':
        return redirect('/login')
    u = consultar_um("SELECT usuario FROM usuarios_sistema WHERE id = ?", (id,))
    if u and u.get('usuario') == 'admin':
        return "<script>alert('Não é permitido apagar o Administrador!'); window.history.back();</script>"
    executar_comando("DELETE FROM usuarios_sistema WHERE id = ?", (id,))
    return redirect('/?aba=configuracoes')

@app.route('/admin/alunos/redefinir_senha', methods=['POST'])
def admin_aluno_redefinir_senha():
    aid, nova = request.form.get('aluno_id'), request.form.get('nova_senha', '').strip()
    if aid and nova:
        executar_comando("UPDATE doutrina SET senha = ? WHERE id = ?", (nova, aid))
    return redirect('/?aba=doutrina')

# =============================================================================
# CADASTROS E MÓDULOS LOCAIS
# =============================================================================
@app.route('/membros/novo', methods=['POST'])
def membros_gravar():
    fd = request.form
    local = (fd.get('local_residencia') or fd.get('bairro') or '').strip()
    genero = fd.get('genero', 'Masculino').strip()
    sql = """INSERT INTO membros 
              (nome, contacto, bi, cargo, departamento, estado_civil, zona, celula, ano_conversao, data_batismo, local_residencia, bairro, genero, criado_em)
              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
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
    cong = {'nome': 'Sede Regional de Chicuque', 'distrito': 'Maxixe (Cidade/Distrito)', 'provincia': 'Inhambane'}
    return render_template('relatorio_membros.html', membros=membros, congregacao=cong, agora=datetime.now().strftime('%d/%m/%Y às %H:%M'))

@app.route('/membros/<int:id>/cartao')
def membros_cartao(id):
    membro = consultar_um("SELECT * FROM membros WHERE id = ?", (id,))
    if not membro: return redirect('/?aba=membros')
    cong = {'nome': 'Sede Regional de Chicuque', 'distrito': 'Maxixe (Cidade/Distrito)', 'provincia': 'Inhambane'}
    return render_template('cartao_membro.html', m=membro, congregacao=cong, agora_ano=datetime.now().year)

@app.route('/membros/<int:id>/batismo')
def membros_batismo(id):
    membro = consultar_um("SELECT * FROM membros WHERE id = ?", (id,))
    if not membro or not membro.get('data_batismo'):
        return "<script>alert('Membro sem data de baptismo registada!'); window.location.href='/?aba=membros';</script>"
    cong = {'nome': 'Sede Regional de Chicuque', 'distrito': 'Maxixe (Cidade/Distrito)', 'provincia': 'Inhambane'}
    return render_template('cartao_batismo.html', m=membro, congregacao=cong, data_extenso=datetime.now().strftime('%d de %B de %Y'))

@app.route('/membros/<int:id>/recomendacao')
def membros_recomendacao(id):
    membro = consultar_um("SELECT * FROM membros WHERE id = ?", (id,))
    if not membro: return redirect('/?aba=membros')
    cong = {'nome': 'Sede Regional de Chicuque', 'distrito': 'Maxixe (Cidade/Distrito)', 'provincia': 'Inhambane'}
    return render_template('carta_recomendacao.html', m=membro, congregacao=cong, data_extenso=datetime.now().strftime('%d de %B de %Y'), agora_ano=datetime.now().year)

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

    sql = """INSERT INTO cultos 
              (data_culto, tipo_culto, homens_adultos, mulheres_adultas, jovens_rapazes, jovens_mocas,
               criancas_meninos, criancas_meninas, visitantes_homens, visitantes_mulheres, apelos, total_presentes, pregador, tema_mensagem, criado_em)
              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    executar_comando(sql, (dt, tipo, ha, ma, jr, jm, cm, cf, vh, vm, apelos, tot, preg, tema, datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=cultos')

@app.route('/financas/caixa/novo', methods=['POST'])
def caixa_gravar():
    perfil = session.get('usuario_perfil', '')
    if perfil not in ['tesoureiro', 'admin']:
        return "<script>alert('Acesso negado! O lançamento de caixa é exclusivo da Tesouraria.'); window.location.href='/?aba=dashboard';</script>"

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

    sql = """INSERT INTO caixa 
              (tipo, categoria, valor, descricao, data_movimento, conta, destino_tipo, departamento, proposito, criado_em)
              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    executar_comando(sql, (tipo, categoria, val, desc, dt, conta, destino_tipo, depto, proposito, datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=tesouraria')

@app.route('/actos/casamento/novo', methods=['POST'])
def actos_casamento():
    fd = request.form
    sql = "INSERT INTO casamentos (tipo, noivo, noiva, data_casamento, ministro, regime, certidao, criado_em) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
    executar_comando(sql, (fd.get('tipo'), fd.get('noivo'), fd.get('noiva'), fd.get('data_casamento'), fd.get('ministro'), fd.get('regime'), fd.get('certidao'), datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=actos')

@app.route('/actos/casamento/remover/<int:id>')
def actos_casamento_remover(id):
    executar_comando("DELETE FROM casamentos WHERE id = ?", (id,))
    return redirect('/?aba=actos')

@app.route('/actos/obito/novo', methods=['POST'])
def actos_obito():
    fd = request.form
    sql = "INSERT INTO obitos (nome_falecido, genero, categoria, data_falecimento, local_funeral, causa, contacto_familia, criado_em) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
    executar_comando(sql, (fd.get('nome_falecido'), fd.get('genero'), fd.get('categoria'), fd.get('data_falecimento'), fd.get('local_funeral'), fd.get('causa'), fd.get('contacto_familia'), datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=actos')

@app.route('/actos/obito/remover/<int:id>')
def actos_obito_remover(id):
    executar_comando("DELETE FROM obitos WHERE id = ?", (id,))
    return redirect('/?aba=actos')

@app.route('/convertidos/novo', methods=['POST'])
def convertidos_gravar():
    fd = request.form
    nome = fd.get('nome', 'Sem Nome').strip()
    tel = fd.get('telefone', '').strip()
    bairro = fd.get('bairro', '').strip()
    dt = fd.get('data_decisao', datetime.now().strftime('%Y-%m-%d')).strip()
    conv = fd.get('quem_convidou', '').strip()
    orig = fd.get('culto_origem', 'Culto de Domingo').strip()
    sql = """INSERT INTO novos_convertidos 
              (nome, telefone, bairro, data_decisao, quem_convidou, culto_origem, status_discipulado, criado_em)
              VALUES (?, ?, ?, ?, ?, ?, 'Acompanhamento', ?)"""
    executar_comando(sql, (nome, tel, bairro, dt, conv, orig, datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=convertidos')

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
    sql = """INSERT INTO planificacao 
              (actividade, titulo, nome_actividade, departamento, tipo_evento, data_prevista, data_inicio, frequencia, responsavel, contacto, status, criado_em)
              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Planeado', ?)"""
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

    sql = """UPDATE planificacao SET 
              status = 'Executado', feedback = ?, data_execucao = ?,
              participantes_homens = ?, participantes_mulheres = ?,
              participantes_jovens = ?, participantes_criancas = ?,
              total_participantes = ? WHERE id = ?"""
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

                sql_up = """UPDATE planificacao SET 
                             status = ?, feedback = ?, dificuldades = ?, 
                             perspectivas = ?, participantes_homens = ?, 
                             participantes_mulheres = ?, participantes_jovens = ?, 
                             participantes_criancas = ?, total_participantes = ? 
                             WHERE id = ?"""
                executar_comando(sql_up, (st, fb, dif, persp, h, mulh, j, c, tot, pid))

        c1 = fd.get('constrangimento_1', '').strip()
        c2 = fd.get('constrangimento_2', '').strip()
        c3 = fd.get('constrangimento_3', '').strip()
        p1 = fd.get('perspectiva_1', '').strip()
        p2 = fd.get('perspectiva_2', '').strip()
        p3 = fd.get('perspectiva_3', '').strip()

        existente = consultar_um("SELECT id FROM balanco_anual WHERE ano = ?", (ano_form,))
        if existente:
            sql_bal = """UPDATE balanco_anual SET 
                          constrangimento_1 = ?, constrangimento_2 = ?, constrangimento_3 = ?,
                          perspectiva_1 = ?, perspectiva_2 = ?, perspectiva_3 = ?,
                          atualizado_em = ? WHERE ano = ?"""
            executar_comando(sql_bal, (c1, c2, c3, p1, p2, p3, datetime.now().strftime('%Y-%m-%d %H:%M'), ano_form))
        else:
            sql_bal = """INSERT INTO balanco_anual 
                          (ano, constrangimento_1, constrangimento_2, constrangimento_3, perspectiva_1, perspectiva_2, perspectiva_3, atualizado_em)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
            executar_comando(sql_bal, (ano_form, c1, c2, c3, p1, p2, p3, datetime.now().strftime('%Y-%m-%d %H:%M')))

        return redirect("/secretaria/relatorio-anual?sucesso_balanco=1")

    planos = consultar_todos("SELECT * FROM planificacao ORDER BY id ASC")
    balanco = consultar_um("SELECT * FROM balanco_anual WHERE ano = ?", (ano_sel,))
    return render_template('balanco_anual.html', ano_sel=ano_sel, planos=planos, balanco=balanco)

@app.route('/secretaria/relatorio-anual')
def secretaria_relatorio_anual():
    casamentos = consultar_todos("SELECT * FROM casamentos")
    obitos = consultar_todos("SELECT * FROM obitos")

    agora = datetime.now()
    ano_atual = agora.year
    ano_anterior = ano_atual - 1

    meses_pt = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
    data_mes_pt = meses_pt.get(agora.month, 'Outubro')
    data_dia = agora.strftime('%d')

    balanco = consultar_um("SELECT * FROM balanco_anual WHERE ano = ?", (ano_atual,))
    constrangimentos_lista = []
    perspectivas_lista = []

    if balanco:
        for k in ['constrangimento_1', 'constrangimento_2', 'constrangimento_3']:
            txt = str(balanco.get(k) or '').strip()
            if txt: constrangimentos_lista.append(txt)
        for k in ['perspectiva_1', 'perspectiva_2', 'perspectiva_3']:
            txt = str(balanco.get(k) or '').strip()
            if txt: perspectivas_lista.append(txt)

    rel = {
        'ano_atual': ano_atual,
        'ano_anterior': ano_anterior,
        'data_dia': data_dia,
        'data_mes': data_mes_pt,
        'casamentos': {'jovens': len([c for c in casamentos if 'jov' in str(c.get('tipo', '')).lower()]), 'adultos': len([c for c in casamentos if 'jov' not in str(c.get('tipo', '')).lower()]), 'total': len(casamentos)},
        'constrangimentos': constrangimentos_lista,
        'perspectivas': perspectivas_lista
    }

    return render_template('relatorio_anual_modelo.html', rel=rel)

# DOUTRINA, PROFESSOR E PORTAL DO ALUNO
@app.route('/doutrina/novo', methods=['POST'])
def doutrina_gravar():
    fd = request.form
    aluno = fd.get('nome_aluno', 'Aluno').strip()
    classe = fd.get('classe', 'Classe I - Primeiros Passos').strip()
    prof = fd.get('professor', 'Pastor Dirigente').strip()
    usuario = fd.get('usuario', '').strip().lower() or aluno.split()[0].lower() + str(datetime.now().second)
    senha = fd.get('senha', '123456').strip()
    dt = fd.get('data_inicio', datetime.now().strftime('%Y-%m-%d')).strip()
    sql = """INSERT INTO doutrina 
              (nome_aluno, classe, professor, licao_atual, data_inicio, presencas, situacao, usuario, senha, aproveitamento, criado_em)
              VALUES (?, ?, ?, 'Lição 1 - O Pecado e o Perdão', ?, 1, 'Em Formação', ?, ?, 0.0, ?)"""
    executar_comando(sql, (aluno, classe, prof, dt, usuario, senha, datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=doutrina')

@app.route('/doutrina/responder_duvida', methods=['POST'])
def doutrina_responder_duvida():
    duvida_id = request.form.get('duvida_id')
    resp_prof = request.form.get('resposta_professor', '').strip()
    prof_nome = request.form.get('professor_nome', 'Pastor / Instrutor').strip()
    if duvida_id and resp_prof:
        sql = "UPDATE duvidas_alunos SET resposta_professor = ?, professor_nome = ? WHERE id = ?"
        executar_comando(sql, (resp_prof, prof_nome, duvida_id))
    return redirect('/?aba=doutrina')

@app.route('/doutrina/avaliar', methods=['POST'])
def doutrina_avaliar():
    aluno_id = request.form.get('aluno_id')
    try: nota = float(request.form.get('aproveitamento') or 0)
    except: nota = 0.0
    nova_situacao = 'Apto para o Batismo / Avanço' if nota >= 70.0 else 'Em Formação'
    sql = "UPDATE doutrina SET aproveitamento = ?, situacao = ? WHERE id = ?"
    executar_comando(sql, (nota, nova_situacao, aluno_id))
    return redirect('/?aba=doutrina')

@app.route('/ensino/aulas')
def aluno_aulas():
    aluno_id = session.get('aluno_id')
    if not aluno_id: return redirect('/login')

    aluno = consultar_um("SELECT * FROM doutrina WHERE id = ?", (aluno_id,))
    if not aluno: return redirect('/logout')

    registos_prog = consultar_todos("SELECT * FROM progresso_licoes WHERE aluno_id = ?", (aluno_id,))
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
    
    executar_comando("UPDATE doutrina SET aproveitamento = ? WHERE id = ?", (media_global, aluno_id))
    aluno['aproveitamento'] = media_global

    duvidas = consultar_todos("SELECT * FROM duvidas_alunos WHERE aluno_id = ? AND licao_id = ? ORDER BY id DESC", (aluno_id, licao_atual_id))

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
    if not aluno_id: return redirect('/login')

    licao_id = request.form.get('licao_id')
    resumo = request.form.get('resumo', '').strip()

    if not resumo or len(resumo) < 20:
        return "<script>alert('Por favor, escreva um resumo reflexivo.'); window.history.back();</script>"

    existente = consultar_um("SELECT id FROM progresso_licoes WHERE aluno_id = ? AND licao_id = ?", (aluno_id, licao_id))

    if existente:
        sql = "UPDATE progresso_licoes SET resumo_aluno = ? WHERE id = ?"
        executar_comando(sql, (resumo, existente['id']))
    else:
        sql = """INSERT INTO progresso_licoes (aluno_id, licao_id, resumo_aluno, nota_teste, status, criado_em)
                  VALUES (?, ?, ?, 0.0, 'Resumo Entregue', ?)"""
        executar_comando(sql, (aluno_id, licao_id, resumo, datetime.now().strftime('%Y-%m-%d %H:%M')))

    return redirect(f"/ensino/aulas?licao={licao_id}#teste")

@app.route('/ensino/submeter_teste', methods=['POST'])
def aluno_submeter_teste():
    aluno_id = session.get('aluno_id')
    if not aluno_id: return redirect('/login')

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

    sql = "UPDATE progresso_licoes SET nota_teste = ?, status = ? WHERE aluno_id = ? AND licao_id = ?"
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
    if not aluno_id: return redirect('/login')

    licao_id = request.form.get('licao_id')
    pergunta = request.form.get('pergunta', '').strip()
    if not pergunta: return redirect(f"/ensino/aulas?licao={licao_id}")

    p_lower = pergunta.lower()
    resp_sistema = "A sua dúvida foi registada e encaminhada ao seu Professor/Mentor na Assembleia de Deus para resposta pastoral."
    if 'expiação' in p_lower:
        resp_sistema = "Manual IEADAO: Expiação é o perdão dos pecados através do sacrifício de Cristo (Hb 9:22)."
    elif 'desobediência' in p_lower or 'transgressão' in p_lower:
        resp_sistema = "Manual IEADAO: Desobedecer é a causa oculta no coração; Transgredir é o efeito manifesto contra a Lei de Deus."

    sql = """INSERT INTO duvidas_alunos (aluno_id, licao_id, pergunta, resposta_sistema, criado_em)
              VALUES (?, ?, ?, ?, ?)"""
    executar_comando(sql, (aluno_id, licao_id, pergunta, resp_sistema, datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect(f"/ensino/aulas?licao={licao_id}#duvidas")

@app.route('/ensino/exame_final', methods=['GET', 'POST'])
def aluno_exame_final():
    aluno_id = session.get('aluno_id')
    if not aluno_id: return redirect('/login')
    aluno = consultar_um("SELECT * FROM doutrina WHERE id = ?", (aluno_id,))
    return render_template('aluno_exame_final.html', aluno=aluno)

@app.route('/ensino/certificado/<int:aluno_id>')
def aluno_certificado(aluno_id):
    aluno = consultar_um("SELECT * FROM doutrina WHERE id = ?", (aluno_id,))
    if not aluno: return redirect('/login')
    return render_template('certificado_ensino.html', aluno=aluno, data_extenso=datetime.now().strftime('%d de %B de %Y'))

@app.route('/config/opcoes/adicionar', methods=['POST'])
def opcoes_adicionar():
    cat = request.form.get('categoria', '').strip()
    val = request.form.get('valor', '').strip()
    if cat and val:
        executar_comando("INSERT INTO opcoes_sistema (categoria, valor) VALUES (?, ?)", (cat, val))
    return redirect('/?aba=configuracoes')

@app.route('/config/opcoes/editar', methods=['POST'])
def opcoes_editar():
    id_op = request.form.get('id')
    novo_val = request.form.get('valor', '').strip()
    if id_op and novo_val:
        executar_comando("UPDATE opcoes_sistema SET valor = ? WHERE id = ?", (novo_val, id_op))
    return redirect('/?aba=configuracoes')

@app.route('/config/opcoes/remover/<int:id>')
def opcoes_remover(id):
    executar_comando("DELETE FROM opcoes_sistema WHERE id = ?", (id,))
    return redirect('/?aba=configuracoes')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
'''

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_code)

try:
    py_compile.compile('app.py', doraise=True)
    print("✓ Validação de sintaxe: app.py compilado sem nenhum erro!")
except Exception as e:
    print(f"Erro ao compilar app.py: {e}")

print("=" * 80)
print(">>> CORREÇÃO CONCLUÍDA! PODE EXECUTAR: py app.py <<<")
print("=" * 80)