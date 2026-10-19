import os
import sys
import jinja2

print("=" * 80)
print("A INSTALAR PORTA DE ENTRADA ESPECTACULAR E REDIRECIONAMENTOS POR PERFIL...")
print("=" * 80)

os.makedirs('templates', exist_ok=True)
env = jinja2.Environment()

# =============================================================================
# 1. ATUALIZAR O APP.PY COM REDIRECIONAMENTO E BLINDAGEM DE PERFIS
# =============================================================================
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

    m = "%s" if is_pg else "?"
    if not consultar_um("SELECT id FROM congregacoes WHERE id = 1"):
        sql_c = f"""INSERT INTO congregacoes (id, nome, provincia, distrito, bairro, pastor_responsavel, criado_em)
                    VALUES (1, 'Sede Regional de Chicuque', 'Inhambane', 'Maxixe (Cidade/Distrito)', 'Chicuque', 'Pastor Dirigente', {m})"""
        executar_comando(sql_c, (datetime.now().strftime('%Y-%m-%d %H:%M'),))

    # GARANTIR UTILIZADORES INSTITUCIONAIS COM PERFIS BEM DELIMITADOS
    perfis_padrao = [
        ('Administrador Geral', 'admin', 'admin123', 'geral', 'admin', 1, 'Inhambane', 'Maxixe (Cidade/Distrito)'),
        ('Pastor Presidente / Liderança', 'pastor', 'pastor123', 'lideranca', 'lideranca', 1, 'Inhambane', 'Maxixe (Cidade/Distrito)'),
        ('Secretaria Executiva', 'secretaria', 'sec123', 'secretaria', 'secretario', 1, 'Inhambane', 'Maxixe (Cidade/Distrito)'),
        ('Tesouraria da Igreja', 'tesouraria', 'tesouro123', 'tesouraria', 'tesoureiro', 1, 'Inhambane', 'Maxixe (Cidade/Distrito)')
    ]
    for n, u, s, niv, perf, cid, prov, dist in perfis_padrao:
        existente = consultar_um(f"SELECT id FROM usuarios_sistema WHERE usuario = {m}", (u,))
        if not existente:
            sql_u = f"""INSERT INTO usuarios_sistema (nome, usuario, senha, nivel, perfil, congregacao_id, provincia, distrito, criado_em)
                        VALUES ({m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m})"""
            executar_comando(sql_u, (n, u, s, niv, perf, cid, prov, dist, datetime.now().strftime('%Y-%m-%d %H:%M')))
        else:
            # Atualizar perfil se necessário
            sql_up = f"UPDATE usuarios_sistema SET perfil = {m}, nivel = {m} WHERE id = {m}"
            executar_comando(sql_up, (perf, niv, existente['id']))

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
                'id': 'c1_l1',
                'numero': 'Lição 1',
                'titulo': 'O Pecado e o Perdão',
                'texto_aureo': 'Porque o salário do pecado é a morte, mas o dom gratuito de Deus é a vida eterna, por Cristo Jesus nosso Senhor. (Rm 6:23)',
                'leitura_base': 'Rm 3:23; Is 59:2; 1Jo 1:7-9; Pv 28:13; Hb 9:22',
                'conteudo_completo': {
                    'introducao': 'Se o pecado não fosse uma triste realidade, seria desnecessária a Salvação consumada por Jesus no Calvário. A doutrina bíblica do pecado e da redenção é o alicerce fundamental para a caminhada cristã.',
                    'pontos_doutrinarios': [
                        {
                            'titulo': '1. O Significado de Pecar: Errar o Alvo',
                            'detalhes': 'Pecar significa literalmente "Errar o Alvo", isto é, errar o alvo de fazer a Vontade de Deus e assim ferirmos a Sua santidade e os Seus propósitos para as nossas vidas.'
                        },
                        {
                            'titulo': '2. Transgressão e Desobediência à Lei Moral de Deus',
                            'detalhes': 'Pecar significa Transgredir a Lei de Deus. Uma pessoa que transgride a Lei Moral de Deus está em desobediência ao Criador (Ex 20:3-17; 1Jo 3:4; Rm 5:14,19; Rm 8:7).\\n\\n• A DIFERENÇA BÍBLICA: Desobedecer é a causa e Transgredir o efeito.\\n• A desobediência está escondida no coração e a transgressão sempre está exposta e manifesta nas ações.'
                        },
                        {
                            'titulo': '3. Lista de Pecados Condenados pelas Escrituras',
                            'detalhes': 'A Bíblia apresenta com clareza as obras da carne que afastam o homem da presença de Deus: Marcos 7:21-22; Romanos 1:29-31; Gálatas 5:19-21; Efésios 5:3; Colossenses 3:5-9. O crente em Cristo abandona a mentira, a imoralidade, a feitiçaria, o ódio e as murmurações.'
                        },
                        {
                            'titulo': '4. A Situação do Homem Perante o Pecado',
                            'tabela': [
                                {'situacao': 'Imoralidade', 'descricao': 'Desfiguração total da imagem divina.', 'versiculos': 'Rm 3:9-12'},
                                {'situacao': 'Inimigo', 'descricao': 'Separação espiritual da presença de Deus.', 'versiculos': 'Is 59:2; Gl 5:4'},
                                {'situacao': 'Morte', 'descricao': 'Separação definitiva e eterna do Criador.', 'versiculos': 'Rm 3:23; Rm 6:23a'}
                            ]
                        },
                        {
                            'titulo': '5. Posição do Homem para se Libertar do Pecado',
                            'detalhes': 'a) Reconhecer que é pecador perante o Deus Santo (Sl 51:3; Rm 3:23);\\nb) Saber que Deus ama o pecador e enviou Seu Filho (Jo 3:16; Rm 5:8);\\nc) Arrepender-se dos seus pecados com genuína dor na alma (Sl 51:1; At 2:37-38);\\nd) Crer e aceitar a Cristo como seu único Salvador e Senhor (Jo 1:12; Jo 3:3,18; At 16:30-31; 1Jo 5:12-13).'
                        },
                        {
                            'titulo': '6. O Perdão de Deus: Expiação e Substituição',
                            'detalhes': 'Deus nos perdoou em Cristo (Mc 2:5; Lc 7:48; 1Jo 1:9). Cristo ofereceu Expiação e Propiciação — pagou com a Sua própria vida inocente o preço justo da ira santa de Deus. "Sem derramamento de sangue não há remissão" (Hb 9:22).\\n\\n• O perdão divino é manifestação viva da Graça:\\n  - Bondade de Deus (Sl 86:5);\\n  - Justiça de Deus pela Justificação: Cristo assumiu a nossa culpa e declarou-nos sem culpa (Rm 3:25);\\n  - Fidelidade de Deus (1Jo 1:9);\\n  - Compaixão de Deus (Mq 7:18-19).\\n\\n• A REGRA DE OURO DA GRAÇA: Quando Cristo perdoa, Ele não só retira o pecado (o mal), mas coloca algo santo que o substitui: Amor, Graça, Paz e Gozo no Espírito Santo!'
                        }
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
                'id': 'c1_l2',
                'numero': 'Lição 2',
                'titulo': 'Salvação e Senhorio de Cristo',
                'texto_aureo': 'Assim que, se alguém está em Cristo, nova criatura é; as coisas velhas já passaram; eis que tudo se fez novo. (2Co 5:17)',
                'leitura_base': 'Ef 2:8-10; Jo 1:12; 1Co 8:6; Cl 1:21-22',
                'conteudo_completo': {
                    'introducao': 'A salvação é um dom gratuito de Deus por meio da fé e não por obras, para que ninguém se glorie (Ef 2:8-9). As boas obras são o resultado natural e inseparável da salvação operada no coração regenerado.',
                    'pontos_doutrinarios': [
                        {'titulo': '1. Passos para a Filiação Divina', 'detalhes': 'Ouvir a Palavra (Rm 10:17), Crer no que Deus revelou (Jo 3:16), Arrepender-se e Confessar (Rm 10:9; 1Jo 1:9) e Receber a Cristo no trono da vida (Jo 1:12; Ap 3:20).'},
                        {'titulo': '2. Cristo Salvador e Senhor', 'detalhes': 'Cristo não quer apenas livrar-nos da condenação eterna, mas dominar e reger o trono do nosso coração, trazendo equilíbrio e paz interior.'}
                    ],
                    'proverbio_chave': 'Cristo não só pode e quer salvar, mas deseja dominar como Senhor da nossa vida.'
                },
                'questoes': [
                    {'p': 'Qual é a relação entre fé, obras e salvação em Efésios 2:8-10?', 'ops': ['As obras compram o perdão.', 'Somos salvos pela graça por meio da fé, e as obras acompanham como fruto.', 'O crente salvo não precisa de praticar boas obras.', 'A fé sem moralidade basta.'], 'c': 1}
                ]
            },
            {
                'id': 'c1_l5',
                'numero': 'Lição 5',
                'titulo': 'A Bíblia - Manual de Fé dos Cristãos',
                'texto_aureo': 'Lâmpada para os meus pés é a tua palavra e luz para o meu caminho. (Sl 119:105)',
                'leitura_base': '2Tm 3:16; Js 1:8; Sl 1:2; 2Pe 1:21',
                'conteudo_completo': {
                    'introducao': 'Não se pode conhecer e obedecer a Deus e à Sua santa Vontade sem conhecermos a Sua Palavra revelada. A Bíblia é infalível e a nossa regra soberana de conduta.',
                    'pontos_doutrinarios': [
                        {'titulo': '1. Inspiração e Origem Divina', 'detalhes': 'Cerca de 40 homens escreveram as Escrituras num período de 1600 anos. O Autor é Deus, o Intérprete é o Espírito Santo e o Tema Central é Cristo Jesus.'},
                        {'titulo': '2. Estrutura Canónica', 'detalhes': 'A Bíblia contém 66 livros (39 no Antigo Testamento e 27 no Novo Testamento).'}
                    ],
                    'proverbio_chave': 'Toda a Escritura é divinamente inspirada e proveitosa para ensinar e redarguir. (2Tm 3:16)'
                },
                'questoes': [
                    {'p': 'Quantos livros compõem o cânon bíblico?', 'ops': ['39 no Antigo Testamento e 27 no Novo Testamento (Total: 66 livros).', '46 no AT e 27 no NT.', '30 no AT e 36 no NT.', '50 no AT e 16 no NT.'], 'c': 0}
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
                'id': 'c2_l1',
                'numero': 'Lição 1',
                'titulo': 'Oração e Jejum',
                'texto_aureo': 'Servindo a Deus em jejuns e orações, de noite e de dia. (Lc 2:37)',
                'leitura_base': '1Ts 5:17; Is 58:6-7; Mt 6:16-18; Zc 7:5',
                'conteudo_completo': {
                    'introducao': 'A oração é a respiração da alma e o jejum é o aprimoramento da sensibilidade espiritual através da subjugação do corpo.',
                    'pontos_doutrinarios': [
                        {'titulo': '1. Oração Contínua', 'detalhes': 'Orar é um mandamento vital (1Ts 5:17). O Espírito Santo ajuda nas nossas fraquezas e intercede por nós.'},
                        {'titulo': '2. O Espírito do Jejum Bíblico', 'detalhes': 'O jejum bíblico não serve para ostentação, mas para quebrantamento e aproximação de Deus acompanhado de amor ao próximo (Is 58:6-7).'}
                    ],
                    'proverbio_chave': 'O importante a guardar no jejum é para quem o estamos fazendo.'
                },
                'questoes': [
                    {'p': 'Qual é o verdadeiro espírito do jejum segundo Isaías 58?', 'ops': ['Exibição de piedade aos homens.', 'Quebrantamento para sensibilidade espiritual acompanhado de amor ao próximo.', 'Greve de fome para forçar Deus.', 'Apenas dieta corporal.'], 'c': 1}
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
                'id': 'c3_l2',
                'numero': 'Lição 5',
                'titulo': 'Fé: Factos, Não Sentimentos',
                'texto_aureo': 'A fé é o firme fundamento das coisas que se esperam e a prova das coisas que não se vêem. (Hb 11:1)',
                'leitura_base': '2Co 5:7; 2Tm 3:14-16; Jr 17:9',
                'conteudo_completo': {
                    'introducao': 'O crente vive por fé na Palavra eterna de Deus e não guiado pelas emoções instáveis da alma.',
                    'pontos_doutrinarios': [
                        {'titulo': '1. A Ilustração do Comboio', 'detalhes': 'A Locomotiva é o FACTO (a Palavra de Deus), o Carro de Ligação é a FÉ e o Vagão Traseiro são os SENTIMENTOS. O comboio anda pela locomotiva, nunca pelo vagão das emoções.'},
                        {'titulo': '2. A Firmeza na Promessa', 'detalhes': 'Mesmo quando não sentimos nada, continuamos firmes porque a Palavra de Deus nunca falha.'}
                    ],
                    'proverbio_chave': 'Porque andamos por fé e não por vista. (2 Coríntios 5:7)'
                },
                'questoes': [
                    {'p': 'Na analogia do comboio da fé, o que representa a Locomotiva?', 'ops': ['Os sentimentos de alegria.', 'O Facto soberano de Deus e as promessas da Sua Palavra.', 'A aprovação dos homens.', 'Os nossos jejuns.'], 'c': 1}
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
                'id': 'c4_l1',
                'numero': 'Lição 1',
                'titulo': 'Baptismo nas Águas e Ceia do Senhor',
                'texto_aureo': 'De sorte que foram baptizados os que de bom grado receberam a sua palavra. (At 2:41)',
                'leitura_base': 'Rm 6:4; 1Co 11:23-29; Mt 28:19',
                'conteudo_completo': {
                    'introducao': 'As duas ordenanças deixadas por Jesus Cristo para a Sua Igreja são o Baptismo nas Águas e a Santa Ceia.',
                    'pontos_doutrinarios': [
                        {'titulo': '1. Baptismo nas Águas', 'detalhes': 'Símbolo da nossa morte e sepultamento para o pecado e ressurreição para Deus ao emergir das águas (Rm 6:4).'},
                        {'titulo': '2. As Três Dimensões da Ceia', 'detalhes': 'Passado Comemorativo (a cruz), Presente Instrutivo (o autoexame de comunhão) e Futuro Inspirador (a Vinda do Senhor).'}
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
# CONTEXT PROCESSOR: DADOS TOTAIS E COMPLETOS
# =============================================================================
@app.context_processor
def injetar_dados():
    u_id = session.get('usuario_id')
    user = consultar_um("SELECT * FROM usuarios_sistema WHERE id = %s" % u_id) if u_id else None
    
    membros = consultar_todos("SELECT * FROM membros ORDER BY id DESC")
    planos = consultar_todos("SELECT * FROM planificacao ORDER BY id DESC")
    cultos = consultar_todos("SELECT * FROM cultos ORDER BY id DESC")
    convertidos = consultar_todos("SELECT * FROM novos_convertidos ORDER BY id DESC")
    caixa = consultar_todos("SELECT * FROM caixa ORDER BY id DESC")
    doutrina = consultar_todos("SELECT * FROM doutrina ORDER BY id DESC")
    casamentos = consultar_todos("SELECT * FROM casamentos ORDER BY id DESC")
    obitos = consultar_todos("SELECT * FROM obitos ORDER BY id DESC")
    duvidas_pendentes = consultar_todos("SELECT * FROM duvidas_alunos WHERE resposta_professor IS NULL OR resposta_professor = '' ORDER BY id DESC")
    opcoes_lista = consultar_todos("SELECT * FROM opcoes_sistema ORDER BY categoria, valor ASC")

    opcoes_map = {}
    for op in opcoes_lista:
        opcoes_map.setdefault(op['categoria'], []).append(op)

    # 1. DEMOGRAFIA COMPLETA COM ZONAS, CÉLULAS E CARGOS
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
        if ec == 'criança' or 'esperança' in dep or 'crian' in dep:
            total_criancas += 1
        elif 'jov' in dep or 'juventude' in dep:
            total_jovens += 1
        else:
            total_adultos += 1

        if m.get('data_batismo'): total_batizados += 1
        else: total_nao_batizados += 1

        z = m.get('zona') or 'Zona Central'
        zonas_contagem[z] = zonas_contagem.get(z, 0) + 1

        cel = m.get('celula') or 'Geral'
        celulas_contagem[cel] = celulas_contagem.get(cel, 0) + 1

        cg = m.get('cargo') or 'Membro em Comunhão'
        cargos_contagem[cg] = cargos_contagem.get(cg, 0) + 1

    total_pres = sum([int(c.get('total_presentes') or 0) for c in cultos])
    media_culto = int(total_pres / len(cultos)) if cultos else 0

    # 2. FINANÇAS COMPLETAS (SALDOS, CARDS E LIVRO RAZÃO)
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
# CONTROLO DE AUTENTICAÇÃO E AUTORIZAÇÃO (RBAC)
# =============================================================================
def login_obrigatorio(f):
    @wraps(f)
    def decorado(*args, **kwargs):
        if not session.get('usuario_id') and not session.get('aluno_id'):
            return redirect('/login')
        return f(*args, **kwargs)
    return decorado

# =============================================================================
# ROTAS DE AUTENTICAÇÃO E NAVEGAÇÃO POR PERFIL
# =============================================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        usuario = request.form.get('usuario', '').strip().lower()
        senha = request.form.get('senha', '').strip()
        m = "%s" if DATABASE_URL else "?"

        # 1. Verificar se é Aluno de Doutrina
        aluno = consultar_um(f"SELECT * FROM doutrina WHERE LOWER(usuario) = {m} AND senha = {m}", (usuario, senha))
        if aluno:
            session.clear()
            session['aluno_id'] = aluno['id']
            session['aluno_nome'] = aluno['nome_aluno']
            session['usuario_perfil'] = 'aluno'
            return redirect('/ensino/aulas')

        # 2. Verificar se é Utilizador do Sistema (Liderança, Tesouraria, Secretaria, Admin)
        u = consultar_um(f"SELECT * FROM usuarios_sistema WHERE LOWER(usuario) = {m} AND senha = {m}", (usuario, senha))
        if u:
            session.clear()
            session['usuario_id'] = u['id']
            session['usuario_nome'] = u['nome']
            session['usuario_perfil'] = u['perfil']
            session['usuario_nivel'] = u['nivel']
            session['congregacao_id'] = u.get('congregacao_id', 1)

            # REDIRECIONAMENTOS AUTOMÁTICOS BASEADOS NO PERFIL
            if u['perfil'] == 'tesoureiro':
                return redirect('/?aba=tesouraria')
            elif u['perfil'] == 'secretario':
                return redirect('/?aba=membros')
            elif u['perfil'] in ['lideranca', 'pastor']:
                return redirect('/?aba=dashboard')
            else: # admin
                return redirect('/?aba=dashboard')
        else:
            erro = "Credenciais inválidas! Verifique o utilizador e a palavra-passe."

    return render_template('login.html', erro=erro)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# =============================================================================
# PAINEL DA CONGREGAÇÃO LOCAL COM BLINDAGEM POR PERFIL
# =============================================================================
@app.route('/')
@login_obrigatorio
def index():
    # Se for aluno, nunca entra na administração! Vai logo para a sala de aula!
    if session.get('usuario_perfil') == 'aluno':
        return redirect('/ensino/aulas')

    aba = request.args.get('aba', 'dashboard')
    perfil = session.get('usuario_perfil', '')

    # BLINDAGENS DE ACESSO POR PERFIL
    if perfil == 'secretario' and aba in ['financas', 'tesouraria']:
        return redirect('/?aba=membros')
    if perfil in ['lideranca', 'pastor'] and aba == 'tesouraria':
        return redirect('/?aba=financas') # Liderança vê Dashboard Financeiro mas não lança caixa!

    id_relatar = request.args.get('relatar_id')
    plano_para_relatar = None
    if id_relatar:
        m = "%s" if DATABASE_URL else "?"
        plano_para_relatar = consultar_um(f"SELECT * FROM planificacao WHERE id = {m}", (id_relatar,))
    return render_template('dashboard.html', aba_ativa=aba, plano_relatar=plano_para_relatar)

# -------------------------------------------------------------
# CADASTROS LOCAIS E TESOURARIA EXCLUSIVA
# -------------------------------------------------------------
@app.route('/membros/novo', methods=['POST'])
@login_obrigatorio
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
@login_obrigatorio
def membros_relatorio_geral():
    membros = consultar_todos("SELECT * FROM membros ORDER BY nome ASC")
    cong = {'nome': 'Sede Regional de Chicuque', 'distrito': 'Maxixe (Cidade/Distrito)', 'provincia': 'Inhambane'}
    return render_template('relatorio_membros.html', membros=membros, congregacao=cong, agora=datetime.now().strftime('%d/%m/%Y às %H:%M'))

@app.route('/membros/<int:id>/cartao')
@login_obrigatorio
def membros_cartao(id):
    m = "%s" if DATABASE_URL else "?"
    membro = consultar_um(f"SELECT * FROM membros WHERE id = {m}", (id,))
    if not membro: return redirect('/?aba=membros')
    cong = {'nome': 'Sede Regional de Chicuque', 'distrito': 'Maxixe (Cidade/Distrito)', 'provincia': 'Inhambane'}
    return render_template('cartao_membro.html', m=membro, congregacao=cong, agora_ano=datetime.now().year)

@app.route('/membros/<int:id>/batismo')
@login_obrigatorio
def membros_batismo(id):
    m = "%s" if DATABASE_URL else "?"
    membro = consultar_um(f"SELECT * FROM membros WHERE id = {m}", (id,))
    if not membro or not membro.get('data_batismo'):
        return "<script>alert('Membro sem data de baptismo registada!'); window.location.href='/?aba=membros';</script>"
    cong = {'nome': 'Sede Regional de Chicuque', 'distrito': 'Maxixe (Cidade/Distrito)', 'provincia': 'Inhambane'}
    return render_template('cartao_batismo.html', m=membro, congregacao=cong, data_extenso=datetime.now().strftime('%d de %B de %Y'))

@app.route('/membros/<int:id>/recomendacao')
@login_obrigatorio
def membros_recomendacao(id):
    m = "%s" if DATABASE_URL else "?"
    membro = consultar_um(f"SELECT * FROM membros WHERE id = {m}", (id,))
    if not membro: return redirect('/?aba=membros')
    cong = {'nome': 'Sede Regional de Chicuque', 'distrito': 'Maxixe (Cidade/Distrito)', 'provincia': 'Inhambane'}
    return render_template('carta_recomendacao.html', m=membro, congregacao=cong, data_extenso=datetime.now().strftime('%d de %B de %Y'), agora_ano=datetime.now().year)

# CULTOS COMPLETOS COM TODOS OS CAMPOS DE ASSISTÊNCIA DISCRIMINADA
@app.route('/cultos/novo', methods=['POST'])
@login_obrigatorio
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

# CAIXA E TESOURARIA EXCLUSIVA (BLOQUEADA PARA SECRETARIA E LIDERANÇA)
@app.route('/financas/caixa/novo', methods=['POST'])
@login_obrigatorio
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

    m = "%s" if DATABASE_URL else "?"
    sql = f"""INSERT INTO caixa 
              (tipo, categoria, valor, descricao, data_movimento, conta, destino_tipo, departamento, proposito, criado_em)
              VALUES ({m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m})"""
    executar_comando(sql, (tipo, categoria, val, desc, dt, conta, destino_tipo, depto, proposito, datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=tesouraria')

@app.route('/actos/casamento/novo', methods=['POST'])
@login_obrigatorio
def actos_casamento():
    fd = request.form
    m = "%s" if DATABASE_URL else "?"
    sql = f"INSERT INTO casamentos (tipo, noivo, noiva, data_casamento, ministro, regime, certidao, criado_em) VALUES ({m}, {m}, {m}, {m}, {m}, {m}, {m}, {m})"
    executar_comando(sql, (fd.get('tipo'), fd.get('noivo'), fd.get('noiva'), fd.get('data_casamento'), fd.get('ministro'), fd.get('regime'), fd.get('certidao'), datetime.now().strftime('%Y-%m-%d %H:%M')))
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
    m = "%s" if DATABASE_URL else "?"
    sql = f"INSERT INTO obitos (nome_falecido, genero, categoria, data_falecimento, local_funeral, causa, contacto_familia, criado_em) VALUES ({m}, {m}, {m}, {m}, {m}, {m}, {m}, {m})"
    executar_comando(sql, (fd.get('nome_falecido'), fd.get('genero'), fd.get('categoria'), fd.get('data_falecimento'), fd.get('local_funeral'), fd.get('causa'), fd.get('contacto_familia'), datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=actos')

@app.route('/actos/obito/remover/<int:id>')
@login_obrigatorio
def actos_obito_remover(id):
    m = "%s" if DATABASE_URL else "?"
    executar_comando(f"DELETE FROM obitos WHERE id = {m}", (id,))
    return redirect('/?aba=actos')

@app.route('/convertidos/novo', methods=['POST'])
@login_obrigatorio
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

@app.route('/secretaria/planificacao/nova', methods=['POST'])
@login_obrigatorio
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
@login_obrigatorio
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
@login_obrigatorio
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
@login_obrigatorio
def secretaria_relatorio_anual():
    membros = consultar_todos("SELECT * FROM membros")
    planos = consultar_todos("SELECT * FROM planificacao")
    casamentos = consultar_todos("SELECT * FROM casamentos")
    obitos = consultar_todos("SELECT * FROM obitos")

    agora = datetime.now()
    ano_atual = agora.year
    ano_anterior = ano_atual - 1

    meses_pt = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
    data_mes_pt = meses_pt.get(agora.month, 'Outubro')
    data_dia = agora.strftime('%d')

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
@login_obrigatorio
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

@app.route('/doutrina/responder_duvida', methods=['POST'])
@login_obrigatorio
def doutrina_responder_duvida():
    duvida_id = request.form.get('duvida_id')
    resp_prof = request.form.get('resposta_professor', '').strip()
    prof_nome = request.form.get('professor_nome', 'Pastor / Instrutor').strip()
    if duvida_id and resp_prof:
        m = "%s" if DATABASE_URL else "?"
        sql = f"UPDATE duvidas_alunos SET resposta_professor = {m}, professor_nome = {m} WHERE id = {m}"
        executar_comando(sql, (resp_prof, prof_nome, duvida_id))
    return redirect('/?aba=doutrina')

@app.route('/ensino/aulas')
def aluno_aulas():
    aluno_id = session.get('aluno_id')
    if not aluno_id: return redirect('/login')

    m = "%s" if DATABASE_URL else "?"
    aluno = consultar_um(f"SELECT * FROM doutrina WHERE id = {m}", (aluno_id,))
    if not aluno: return redirect('/logout')

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
    if not aluno_id: return redirect('/login')

    licao_id = request.form.get('licao_id')
    resumo = request.form.get('resumo', '').strip()

    if not resumo or len(resumo) < 20:
        return "<script>alert('Por favor, escreva um resumo reflexivo.'); window.history.back();</script>"

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

    m = "%s" if DATABASE_URL else "?"
    sql = f"""INSERT INTO duvidas_alunos (aluno_id, licao_id, pergunta, resposta_sistema, criado_em)
              VALUES ({m}, {m}, {m}, {m}, {m})"""
    executar_comando(sql, (aluno_id, licao_id, pergunta, resp_sistema, datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect(f"/ensino/aulas?licao={licao_id}#duvidas")

@app.route('/ensino/exame_final', methods=['GET', 'POST'])
def aluno_exame_final():
    aluno_id = session.get('aluno_id')
    if not aluno_id: return redirect('/login')
    m = "%s" if DATABASE_URL else "?"
    aluno = consultar_um(f"SELECT * FROM doutrina WHERE id = {m}", (aluno_id,))
    return render_template('aluno_exame_final.html', aluno=aluno)

@app.route('/ensino/certificado/<int:aluno_id>')
def aluno_certificado(aluno_id):
    m = "%s" if DATABASE_URL else "?"
    aluno = consultar_um(f"SELECT * FROM doutrina WHERE id = {m}", (aluno_id,))
    if not aluno: return redirect('/login')
    return render_template('certificado_ensino.html', aluno=aluno, data_extenso=datetime.now().strftime('%d de %B de %Y'))

@app.route('/config/opcoes/adicionar', methods=['POST'])
@login_obrigatorio
def opcoes_adicionar():
    cat = request.form.get('categoria', '').strip()
    val = request.form.get('valor', '').strip()
    if cat and val:
        m = "%s" if DATABASE_URL else "?"
        executar_comando(f"INSERT INTO opcoes_sistema (categoria, valor) VALUES ({m}, {m})", (cat, val))
    return redirect('/?aba=configuracoes')

@app.route('/config/opcoes/editar', methods=['POST'])
@login_obrigatorio
def opcoes_editar():
    id_op = request.form.get('id')
    novo_val = request.form.get('valor', '').strip()
    if id_op and novo_val:
        m = "%s" if DATABASE_URL else "?"
        executar_comando(f"UPDATE opcoes_sistema SET valor = {m} WHERE id = {m}", (novo_val, id_op))
    return redirect('/?aba=configuracoes')

@app.route('/config/opcoes/remover/<int:id>')
@login_obrigatorio
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
print("✓ app.py: Restaurado e configurado com RBAC e redirecionamentos!")

# =============================================================================
# 3. INTERFACE DE ENTRADA ESPECTACULAR (TEMPLATES/LOGIN.HTML)
# =============================================================================
login_html_espectacular = """<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portal Oficial - Assembleia de Deus em Moçambique</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .celestial-bg {
            background: radial-gradient(circle at 50% 0%, #1e1b4b 0%, #0f172a 50%, #020617 100%);
        }
        .glow-gold {
            box-shadow: 0 0 40px -5px rgba(245, 158, 11, 0.3);
        }
    </style>
</head>
<body class="celestial-bg min-h-screen flex items-center justify-center p-4 font-sans text-slate-800">

    <div class="max-w-4xl w-full grid grid-cols-1 md:grid-cols-12 bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl overflow-hidden border border-amber-500/20 glow-gold">

        <!-- LADO ESQUERDO: APRESENTAÇÃO INSTITUCIONAL & NOTA DE BOAS-VINDAS -->
        <div class="md:col-span-5 bg-gradient-to-br from-indigo-950 via-slate-900 to-slate-950 p-8 text-white flex flex-col justify-between relative overflow-hidden border-r border-indigo-900/40">
            <div class="space-y-4 relative z-10 text-center sm:text-left">
                <!-- LOGO OFICIAL VETORIAL -->
                <div class="w-28 h-28 mx-auto sm:mx-0 bg-white rounded-3xl p-2 shadow-2xl flex items-center justify-center border-2 border-amber-400">
                    {% include 'logo_ad.html' %}
                </div>

                <div>
                    <span class="bg-amber-400/20 text-amber-300 border border-amber-400/40 text-[9px] font-black uppercase px-2.5 py-0.5 rounded-full inline-block mb-1">
                        Plataforma Oficial
                    </span>
                    <h1 class="text-xl font-black uppercase tracking-wide leading-tight">
                        ASSEMBLEIA DE DEUS
                    </h1>
                    <p class="text-[11px] text-blue-300 font-bold mt-0.5">República de Moçambique</p>
                </div>

                <!-- NOTA DE BOAS-VINDAS CALOROSA E INTERATIVA -->
                <div class="bg-white/5 border border-white/10 p-4 rounded-2xl text-xs space-y-2 text-indigo-100 backdrop-blur-sm">
                    <p class="font-extrabold text-amber-300 flex items-center gap-1.5 text-[11px]">
                        <span>🕊️</span> Bem-vindo à Casa do Senhor!
                    </p>
                    <p class="leading-relaxed text-[11px] text-justify text-slate-200">
                        Um ambiente eclesiástico integrado, seguro e transparente para a expansão do Reino de Deus. Cada servo e formando acessa a sua área de vocação e serviço.
                    </p>
                </div>
            </div>

            <!-- VERSÍCULO LITÚRGICO -->
            <div class="pt-6 relative z-10 border-t border-white/10 text-[10px] italic text-indigo-200 text-center font-serif">
                "Alegrei-me quando me disseram: Vamos à casa do Senhor!" (Salmo 122:1)
            </div>
        </div>

        <!-- LADO DIREITO: FORMULÁRIO DE LOGIN & ATALHOS DE PERFIL -->
        <div class="md:col-span-7 p-8 sm:p-10 flex flex-col justify-between space-y-6">

            <div class="space-y-1">
                <h2 class="text-2xl font-black text-slate-900">Acesso ao Sistema</h2>
                <p class="text-xs text-slate-500">Introduza as suas credenciais para entrar na sua área eclesiástica.</p>
            </div>

            {% if erro %}
            <div class="p-3 bg-rose-50 border-2 border-rose-300 rounded-xl text-rose-800 text-xs font-bold text-center">
                {{ erro }}
            </div>
            {% endif %}

            <!-- FORMULÁRIO -->
            <form action="/login" method="POST" class="space-y-4 text-xs">
                <div>
                    <label class="block font-bold text-slate-700 mb-1">Nome de Utilizador *</label>
                    <div class="relative">
                        <span class="absolute left-3.5 top-3 text-slate-400">👤</span>
                        <input type="text" id="campo_usuario" name="usuario" required placeholder="Digite o seu utilizador" class="w-full h-11 pl-10 pr-3 border-2 border-slate-200 rounded-xl bg-slate-50 focus:bg-white focus:border-indigo-600 focus:outline-none font-bold">
                    </div>
                </div>

                <div>
                    <label class="block font-bold text-slate-700 mb-1">Palavra-passe *</label>
                    <div class="relative">
                        <span class="absolute left-3.5 top-3 text-slate-400">🔒</span>
                        <input type="password" id="campo_senha" name="senha" required placeholder="••••••••" class="w-full h-11 pl-10 pr-3 border-2 border-slate-200 rounded-xl bg-slate-50 focus:bg-white focus:border-indigo-600 focus:outline-none font-bold">
                    </div>
                </div>

                <button type="submit" class="w-full py-3.5 bg-gradient-to-r from-indigo-900 to-blue-900 hover:from-indigo-950 hover:to-blue-950 text-white font-black rounded-xl shadow-xl cursor-pointer text-sm transition transform hover:-translate-y-0.5">
                    Entrar com o Meu Perfil →
                </button>
            </form>

            <!-- CARDS INTERATIVOS DE SELEÇÃO RÁPIDA (TESTE E ORIENTAÇÃO) -->
            <div class="space-y-2 pt-2 border-t border-slate-200">
                <span class="text-[10px] uppercase font-bold text-slate-400 block tracking-wider">Perfis & Destinos Automáticos:</span>
                <div class="grid grid-cols-2 gap-2 text-[10px]">
                    <button type="button" onclick="preencherLogin('pastor', 'pastor123')" class="p-2 bg-slate-50 hover:bg-indigo-50 border rounded-xl text-left transition">
                        <span class="font-black text-indigo-950 block">⛪ Pastor / Liderança</span>
                        <span class="text-[9px] text-slate-500">Vê tudo (menos lançamentos)</span>
                    </button>
                    <button type="button" onclick="preencherLogin('tesouraria', 'tesouro123')" class="p-2 bg-amber-50/60 hover:bg-amber-100 border border-amber-200 rounded-xl text-left transition">
                        <span class="font-black text-amber-950 block">🔐 Tesoureira</span>
                        <span class="text-[9px] text-amber-700">Acesso exclusivo ao caixa</span>
                    </button>
                    <button type="button" onclick="preencherLogin('secretaria', 'sec123')" class="p-2 bg-blue-50/60 hover:bg-blue-100 border border-blue-200 rounded-xl text-left transition">
                        <span class="font-black text-blue-950 block">📋 Secretaria</span>
                        <span class="text-[9px] text-blue-700">Membros, Actos e Actas</span>
                    </button>
                    <button type="button" onclick="preencherLogin('admin', 'admin123')" class="p-2 bg-purple-50/60 hover:bg-purple-100 border border-purple-200 rounded-xl text-left transition">
                        <span class="font-black text-purple-950 block">⚙️ Administrador</span>
                        <span class="text-[9px] text-purple-700">Supervisão total</span>
                    </button>
                </div>
            </div>

        </div>

    </div>

    <script>
        function preencherLogin(u, s) {
            document.getElementById('campo_usuario').value = u;
            document.getElementById('campo_senha').value = s;
        }
    </script>

</body>
</html>
"""

env.parse(login_html_espectacular)
with open(os.path.join('templates', 'login.html'), 'w', encoding='utf-8') as f:
    f.write(login_html_espectacular)
print("✓ templates/login.html: Porta de entrada espetacular criada com sucesso!")

# =============================================================================
# 4. RESTAURAR TEMPLATES/DASHBOARD.HTML COMPLETO COM TODAS AS ABAS E SEGURANÇA
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
                {% if usuario_logado and usuario_logado.perfil != 'secretario' %}
                <div class="px-3 pt-3 pb-1 text-[10px] font-bold uppercase tracking-wider text-emerald-400">Finanças & Tesouraria</div>

                <!-- Dashboard Financeiro (Consulta para Liderança, Tesouraria e Admin) -->
                <a href="/?aba=financas" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'financas' %}bg-emerald-700 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                    <span>📊</span><span>5. Dashboard Financeiro</span>
                </a>

                <!-- Caixa & Lançamentos: EXCLUSIVO PARA QUEM LANÇA (TESOURARIA E ADMIN) -->
                {% if usuario_logado.perfil in ['tesoureiro', 'admin'] %}
                <a href="/?aba=tesouraria" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'tesouraria' %}bg-amber-600 text-white shadow-md{% else %}text-amber-300 hover:bg-slate-800{% endif %}">
                    <span>🔐</span><span>6. Caixa & Lançamentos</span>
                </a>
                {% endif %}
                {% endif %}

                <div class="px-3 pt-3 pb-1 text-[10px] font-bold uppercase tracking-wider text-amber-400">Ensino & Parâmetros</div>

                <a href="/?aba=doutrina" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'doutrina' %}bg-amber-700 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                    <span>📖</span><span>7. Doutrina & Batismo</span>
                </a>

                {% if usuario_logado and usuario_logado.perfil == 'admin' %}
                <a href="/?aba=configuracoes" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'configuracoes' %}bg-purple-700 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                    <span>⚙️</span><span>Gestor de Seletores</span>
                </a>
                {% endif %}
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
                    <p class="text-xs text-indigo-200 mt-0.5">Estatística de almas congregadas sem interferência financeira • {{ congregacao.distrito }}</p>
                </div>
            </div>
            <div class="bg-white/10 p-4 rounded-2xl border border-white/10 text-center shrink-0">
                <span class="text-[10px] uppercase font-bold text-indigo-200 block">Total de Almas no Rebanho</span>
                <span class="text-3xl font-black text-amber-300">{{ demografia.total_almas }} Vidas</span>
                <span class="text-[10px] text-slate-300 block mt-0.5">{{ demografia.membros_cadastrados }} Membros • {{ demografia.novos_convertidos }} em Discipulado</span>
            </div>
        </div>

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
                <p class="text-xs text-pink-200 mt-0.5">Gestão solene dos matrimónios e registo de condolências da membresia</p>
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
                                <input type="text" name="certidao" placeholder="Nº Registo Civil / Assento" class="w-full h-10 px-3 border rounded-xl bg-slate-50">
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
                                <input type="text" name="local_funeral" placeholder="Ex: Chicuque / Maxixe" class="w-full h-10 px-3 border rounded-xl bg-slate-50">
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
                                <tr><td colspan="4" class="py-6 text-center text-slate-400 italic">Nenhum óbito registado no período. Graças a Deus!</td></tr>
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
                <h2 class="text-xl font-extrabold">📋 Secretaria & Planificação de Actividades</h2>
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
                            <tr><td colspan="4" class="py-8 text-center text-slate-400">Nenhum plano registado.</td></tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- ========================================================= -->
        <!-- ABA 3: CULTOS COM CRIANÇAS POR GÉNERO (RESTAURADA 100%)    -->
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

                    <div class="p-3 bg-slate-50 rounded-xl border border-slate-200 space-y-2">
                        <div class="font-bold text-slate-700 text-[11px] uppercase tracking-wider">Assistência Discriminada por Género</div>
                        
                        <div class="grid grid-cols-2 gap-2">
                            <div><label class="text-slate-500 font-semibold">👨 Homens Adultos</label><input type="number" name="homens_adultos" value="0" min="0" oninput="somarCulto()" class="campo-soma w-full h-8 px-2 border rounded bg-white font-bold"></div>
                            <div><label class="text-slate-500 font-semibold">👩 Mulheres Adultas</label><input type="number" name="mulheres_adultas" value="0" min="0" oninput="somarCulto()" class="campo-soma w-full h-8 px-2 border rounded bg-white font-bold"></div>
                            <div><label class="text-slate-500 font-semibold">👦 Jovens (Rapazes)</label><input type="number" name="jovens_rapazes" value="0" min="0" oninput="somarCulto()" class="campo-soma w-full h-8 px-2 border rounded bg-white font-bold"></div>
                            <div><label class="text-slate-500 font-semibold">👧 Jovens (Moças)</label><input type="number" name="jovens_mocas" value="0" min="0" oninput="somarCulto()" class="campo-soma w-full h-8 px-2 border rounded bg-white font-bold"></div>
                            
                            <div class="bg-blue-50/60 p-1.5 rounded-lg border border-blue-200">
                                <label class="text-blue-900 font-bold text-[11px] block">👶 Crianças (Meninos)</label>
                                <input type="number" name="criancas_meninos" value="0" min="0" oninput="somarCulto()" class="campo-soma w-full h-8 px-2 border border-blue-300 rounded bg-white font-bold text-blue-900">
                            </div>
                            <div class="bg-pink-50/60 p-1.5 rounded-lg border border-pink-200">
                                <label class="text-pink-900 font-bold text-[11px] block">👧 Crianças (Meninas)</label>
                                <input type="number" name="criancas_meninas" value="0" min="0" oninput="somarCulto()" class="campo-soma w-full h-8 px-2 border border-pink-300 rounded bg-white font-bold text-pink-900">
                            </div>

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
                    <thead><tr class="border-b-2 border-slate-200 text-slate-500"><th class="py-3 px-3">Nome</th><th class="py-3 px-3">Contacto</th><th class="py-3 px-3">Bairro</th></tr></thead>
                    <tbody>
                        {% for c in convertidos %}
                        <tr class="border-b border-slate-100 hover:bg-slate-50"><td class="py-3 px-3 font-bold">{{ c.nome }}</td><td class="py-3 px-3">{{ c.telefone or '---' }}</td><td class="py-3 px-3">{{ c.bairro or '---' }}</td></tr>
                        {% else %}
                        <tr><td colspan="4" class="py-8 text-center text-slate-400">Nenhum convertido registado.</td></tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
        {% endif %}

        <!-- ========================================================= -->
        <!-- ABA 5: DASHBOARD FINANCEIRO COMPLETO (RESTAURADA 100%)    -->
        <!-- ========================================================= -->
        {% if aba_ativa == 'financas' and (usuario_logado.perfil != 'secretario') %}
        <div class="bg-emerald-950 text-white p-6 rounded-2xl shadow mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
                <h2 class="text-2xl font-black">📊 Dashboard Financeiro & Transparência</h2>
                <p class="text-xs text-emerald-300 mt-1">Visão analítica completa das finanças da congregação (Sede Chicuque)</p>
            </div>
            <div class="text-right flex flex-wrap items-center gap-3">
                <div class="bg-white/10 px-3 py-1.5 rounded-xl border border-white/10 text-right">
                    <span class="text-[9px] uppercase font-bold text-amber-300 block">💵 Caixa Físico</span>
                    <span class="text-sm font-black text-white">{{ "%.2f"|format(kpis.saldo_caixa_fisico or 0) }} MT</span>
                </div>
                <div class="bg-white/10 px-3 py-1.5 rounded-xl border border-white/10 text-right">
                    <span class="text-[9px] uppercase font-bold text-blue-300 block">🏦 Conta Bancária</span>
                    <span class="text-sm font-black text-white">{{ "%.2f"|format(kpis.saldo_banco or 0) }} MT</span>
                </div>
                <div>
                    <span class="text-[10px] uppercase font-bold text-emerald-300 block">Saldo Geral Total</span>
                    <span class="text-2xl font-black text-white">{{ "%.2f"|format(kpis.saldo_caixa) }} MT</span>
                </div>
                {% if usuario_logado.perfil in ['tesoureiro', 'admin'] %}
                <a href="/?aba=tesouraria" class="px-3.5 py-2 bg-amber-500 hover:bg-amber-600 text-slate-950 font-black rounded-xl text-xs shadow flex items-center gap-1.5">
                    <span>🔐</span><span>Lançamentos</span>
                </a>
                {% endif %}
            </div>
        </div>

        <!-- 3 CARDS ANALÍTICOS SEPARADOS: IGREJA LOCAL, IGREJA MÃE E DEPARTAMENTOS -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-5 mb-8 text-xs">
            <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200">
                <div class="font-extrabold text-slate-800 uppercase flex items-center justify-between border-b pb-2 mb-2">
                    <span>🏛️ Igreja Geral (Local)</span>
                    <span class="text-[10px] bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-bold">Chicuque</span>
                </div>
                <div class="flex justify-between items-center text-emerald-700 font-bold">
                    <span>Entradas Locais:</span>
                    <span>+ {{ "%.2f"|format(kpis.geral_in or 0) }} MT</span>
                </div>
                <div class="flex justify-between items-center text-rose-700 font-bold mt-1">
                    <span>Despesas Locais:</span>
                    <span>- {{ "%.2f"|format(kpis.geral_out or 0) }} MT</span>
                </div>
                <div class="border-t pt-2 mt-2 flex justify-between items-center font-black text-slate-900">
                    <span>Saldo Operacional:</span>
                    <span>{{ "%.2f"|format((kpis.geral_in or 0) - (kpis.geral_out or 0)) }} MT</span>
                </div>
            </div>

            <div class="bg-white p-5 rounded-2xl shadow-sm border border-amber-200 bg-amber-50/30">
                <div class="font-extrabold text-amber-950 uppercase flex items-center justify-between border-b border-amber-200 pb-2 mb-2">
                    <span>🏢 Igreja Mãe (Sede)</span>
                    <span class="text-[10px] bg-amber-200 text-amber-950 px-2 py-0.5 rounded font-black">Remessas</span>
                </div>
                <div class="flex justify-between items-center text-blue-800 font-bold">
                    <span>Apoio Recebido:</span>
                    <span>+ {{ "%.2f"|format(kpis.mae_in or 0) }} MT</span>
                </div>
                <div class="flex justify-between items-center text-rose-700 font-bold mt-1">
                    <span>Remessas / Dízimo Dízimos:</span>
                    <span>- {{ "%.2f"|format(kpis.mae_out or 0) }} MT</span>
                </div>
                <div class="border-t border-amber-200 pt-2 mt-2 flex justify-between items-center font-black text-amber-950">
                    <span>Balanço c/ a Sede:</span>
                    <span>{{ "%.2f"|format((kpis.mae_in or 0) - (kpis.mae_out or 0)) }} MT</span>
                </div>
            </div>

            <div class="bg-white p-5 rounded-2xl shadow-sm border border-indigo-200 bg-indigo-50/30">
                <div class="font-extrabold text-indigo-950 uppercase flex items-center justify-between border-b border-indigo-200 pb-2 mb-2">
                    <span>👥 Departamentos</span>
                    <span class="text-[10px] bg-indigo-200 text-indigo-950 px-2 py-0.5 rounded font-black">Fundos</span>
                </div>
                <div class="flex justify-between items-center text-emerald-700 font-bold">
                    <span>Arrecadação Deptos:</span>
                    <span>+ {{ "%.2f"|format(kpis.depto_in or 0) }} MT</span>
                </div>
                <div class="flex justify-between items-center text-rose-700 font-bold mt-1">
                    <span>Gastos Deptos:</span>
                    <span>- {{ "%.2f"|format(kpis.depto_out or 0) }} MT</span>
                </div>
                <div class="border-t border-indigo-200 pt-2 mt-2 flex justify-between items-center font-black text-indigo-950">
                    <span>Fundo Departamental:</span>
                    <span>{{ "%.2f"|format((kpis.depto_in or 0) - (kpis.depto_out or 0)) }} MT</span>
                </div>
            </div>
        </div>

        <!-- 4 CARDS DE RESUMO GERAL -->
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

        <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
            <h3 class="font-bold text-base mb-4 border-b pb-2">📋 Livro Razão de Movimentos ({{ caixa|length }} registos)</h3>
            <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse text-xs">
                    <thead>
                        <tr class="border-b-2 border-slate-200 text-slate-500">
                            <th class="py-2.5 px-2">Data</th>
                            <th class="py-2.5 px-2">Conta</th>
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
                                {% if 'banco' in (cx.conta or '')|lower %}
                                <span class="bg-blue-100 text-blue-900 px-2 py-0.5 rounded font-black text-[10px]">🏦 Banco</span>
                                {% else %}
                                <span class="bg-amber-100 text-amber-900 px-2 py-0.5 rounded font-black text-[10px]">💵 Caixa</span>
                                {% endif %}
                            </td>
                            <td class="py-3 px-2">
                                <span class="{% if cx.tipo == 'Entrada' %}bg-emerald-100 text-emerald-800{% else %}bg-rose-100 text-rose-800{% endif %} px-2.5 py-1 rounded-full font-bold text-[11px]">{{ cx.tipo }}</span>
                            </td>
                            <td class="py-3 px-2 font-bold">{{ cx.categoria }}<div class="text-[11px] text-slate-400 font-normal">{{ cx.descricao }}</div></td>
                            <td class="py-3 px-2 text-right font-extrabold {% if cx.tipo == 'Entrada' %}text-emerald-700{% else %}text-rose-700{% endif %}">
                                {{ "%.2f"|format(cx.valor or 0) }} MT
                            </td>
                        </tr>
                        {% else %}
                        <tr><td colspan="5" class="py-8 text-center text-slate-400">Nenhum movimento gravado.</td></tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
        {% endif %}

        <!-- ========================================================= -->
        <!-- ABA 6: CAIXA & TESOURARIA (EXCLUSIVO TESOURARIA E ADMIN)  -->
        <!-- ========================================================= -->
        {% if aba_ativa == 'tesouraria' and usuario_logado.perfil in ['tesoureiro', 'admin'] %}
        <div class="bg-amber-950 text-white p-6 rounded-2xl shadow mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
                <div class="inline-flex items-center gap-2 bg-amber-500/20 text-amber-300 px-3 py-1 rounded-full text-[10px] font-black uppercase mb-1 border border-amber-400/30">
                    <span>🔐</span> ACESSO RESTRITO • GABINETE DA TESOURARIA
                </div>
                <h2 class="text-2xl font-black">Lançamentos de Caixa & Movimentação Financeira</h2>
                <p class="text-xs text-amber-200 mt-0.5">Gestão separada: Igreja em Geral (Local), Igreja Mãe (Sede) e Departamentos</p>
            </div>
            <div class="flex items-center gap-3">
                <div class="bg-white/10 px-3.5 py-2 rounded-xl text-right border border-white/10">
                    <span class="text-[9px] uppercase font-bold text-amber-300 block">Caixa Físico</span>
                    <span class="text-sm font-black text-white">{{ "%.2f"|format(kpis.saldo_caixa_fisico or 0) }} MT</span>
                </div>
                <div class="bg-white/10 px-3.5 py-2 rounded-xl text-right border border-white/10">
                    <span class="text-[9px] uppercase font-bold text-blue-300 block">Conta Bancária</span>
                    <span class="text-sm font-black text-white">{{ "%.2f"|format(kpis.saldo_banco or 0) }} MT</span>
                </div>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div class="lg:col-span-5 bg-white p-6 rounded-2xl shadow-sm border-2 border-amber-300">
                <h3 class="font-extrabold text-base mb-4 border-b pb-2 text-amber-950 flex items-center gap-2">
                    <span>✍️</span> Lançar Entrada ou Saída de Valores
                </h3>
                
                <form action="/financas/caixa/novo" method="POST" class="space-y-4 text-xs">
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">Tipo de Movimento *</label>
                            <select id="tipo_movimento" name="tipo" onchange="atualizarFormularioTesouraria()" class="w-full h-11 px-2 border-2 border-slate-200 rounded-xl bg-slate-50 font-black text-sm">
                                <option value="Entrada">🟢 Entrada (+)</option>
                                <option value="Saída">🔴 Saída (-)</option>
                            </select>
                        </div>
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">Conta Financeira *</label>
                            <select name="conta" required class="w-full h-11 px-2 border-2 border-slate-200 rounded-xl bg-slate-50 font-black text-xs text-indigo-900">
                                <option value="Caixa Físico">💵 Caixa Físico (Numerário)</option>
                                <option value="Conta Bancária">🏦 Conta Bancária</option>
                            </select>
                        </div>
                    </div>

                    <div>
                        <label class="block font-bold text-slate-700 mb-1">Âmbito do Movimento (Onde entra / De onde sai) *</label>
                        <select id="destino_tipo" name="destino_tipo" onchange="atualizarFormularioTesouraria()" class="w-full h-11 px-3 border-2 border-indigo-300 rounded-xl bg-indigo-50/50 font-black text-xs text-indigo-950">
                            <option value="Igreja Geral">🏛️ 1. Igreja em Geral (Local / Sede Chicuque)</option>
                            <option value="Igreja Mãe">🏢 2. Igreja Mãe (Sede / Remessas)</option>
                            <option value="Departamento">👥 3. Departamentos da Igreja</option>
                        </select>
                    </div>

                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">Data da Operação *</label>
                            <input type="date" name="data_movimento" required class="w-full h-11 px-2 border-2 border-slate-200 rounded-xl bg-slate-50 font-bold">
                        </div>
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">Valor (MZN) *</label>
                            <input type="number" step="0.01" name="valor" required placeholder="Ex: 2500.00" class="w-full h-11 px-3 border-2 border-emerald-400 rounded-xl bg-emerald-50/50 font-black text-emerald-950 text-base">
                        </div>
                    </div>

                    <!-- ENTRADA NA IGREJA GERAL -->
                    <div id="box_entrada_geral" class="space-y-2 p-3.5 bg-emerald-50/70 rounded-xl border border-emerald-200">
                        <div class="font-black text-emerald-900 text-[10px] uppercase">Receita da Igreja Local (Sede Chicuque)</div>
                        <label class="block font-semibold text-slate-700 mb-1">Categoria de Entrada Local *</label>
                        <select name="categoria" class="w-full h-10 px-2 border rounded-xl bg-white font-bold text-slate-800">
                            {% for op in opcoes.get('categoria_caixa', []) %}
                            <option value="{{ op.valor }}">{{ op.valor }}</option>
                            {% endfor %}
                        </select>
                    </div>

                    <!-- ENTRADA DA IGREJA MÃE -->
                    <div id="box_entrada_mae" class="hidden space-y-2 p-3.5 bg-blue-50/70 rounded-xl border border-blue-200">
                        <div class="font-black text-blue-900 text-[10px] uppercase">Valores Recebidos da Igreja Mãe / Sede</div>
                        <label class="block font-semibold text-slate-700 mb-1">Tipo de Entrada da Igreja Mãe *</label>
                        <select name="categoria_entrada_mae" class="w-full h-10 px-2 border-2 border-blue-300 rounded-xl bg-white font-bold text-blue-950">
                            {% for op in opcoes.get('categoria_entrada_mae', []) %}
                            <option value="{{ op.valor }}">{{ op.valor }}</option>
                            {% else %}
                            <option value="Apoio / Subsídio da Igreja Mãe">Apoio / Subsídio da Igreja Mãe</option>
                            <option value="Fundo Missionário da Sede">Fundo Missionário da Sede</option>
                            {% endfor %}
                        </select>
                    </div>

                    <!-- ENTRADA EM DEPARTAMENTOS -->
                    <div id="box_entrada_depto" class="hidden space-y-3 p-3.5 bg-emerald-50/70 rounded-xl border border-emerald-200">
                        <div class="font-black text-emerald-900 text-[10px] uppercase">Entrada Destinada ao Departamento</div>
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">Qual Departamento recebe? *</label>
                            <select name="departamento" class="w-full h-10 px-2 border-2 border-emerald-300 rounded-xl bg-white font-extrabold text-indigo-900">
                                {% for op in opcoes.get('departamento', []) %}
                                <option value="{{ op.valor }}">{{ op.valor }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">Tipo de Entrada Departamental *</label>
                            <select name="categoria_entrada_depto" class="w-full h-10 px-2 border rounded-xl bg-white font-semibold">
                                {% for op in opcoes.get('categoria_entrada_depto', []) %}
                                <option value="{{ op.valor }}">{{ op.valor }}</option>
                                {% else %}
                                <option value="Quotas / Mensalidades do Depto">Quotas / Mensalidades do Depto</option>
                                <option value="Oferta de Culto do Depto">Oferta de Culto do Depto</option>
                                <option value="Bazar / Venda do Depto">Bazar / Arrecadação de Fundos</option>
                                {% endfor %}
                            </select>
                        </div>
                    </div>

                    <!-- SAÍDA DA IGREJA GERAL -->
                    <div id="box_saida_geral" class="hidden space-y-2 p-3.5 bg-rose-50/70 rounded-xl border border-rose-200">
                        <div class="font-black text-rose-900 text-[10px] uppercase">Despesas de Funcionamento Local</div>
                        <label class="block font-bold text-slate-700 mb-1">Selecione a Despesa Local *</label>
                        <select name="categoria_saida_geral" class="w-full h-10 px-2 border-2 border-slate-300 rounded-xl bg-white font-extrabold text-slate-800">
                            {% for op in opcoes.get('categoria_saida_geral', []) %}
                            <option value="{{ op.valor }}">{{ op.valor }}</option>
                            {% else %}
                            <option value="Energia (Electricidade / Credelec)">💡 Energia (Electricidade / Credelec)</option>
                            <option value="Água">🚰 Água</option>
                            <option value="Vogal (Apoio Pastoral / Transporte)">🚗 Vogal (Subsídio / Apoio Pastoral)</option>
                            <option value="Santa Ceia (Pão e Vinho)">🍞 Santa Ceia (Pão / Vinho / Elementos)</option>
                            {% endfor %}
                        </select>
                    </div>

                    <!-- SAÍDA PARA A IGREJA MÃE -->
                    <div id="box_saida_mae" class="hidden space-y-2 p-3.5 bg-amber-50/70 rounded-xl border-2 border-amber-300">
                        <div class="font-black text-amber-950 text-[10px] uppercase">Remessas Enviadas à Igreja Mãe (Sede)</div>
                        <label class="block font-bold text-amber-900 mb-1">Selecione o Tipo de Remessa / Envio *</label>
                        <select name="categoria_saida_mae" class="w-full h-10 px-2 border-2 border-amber-400 rounded-xl bg-white font-black text-amber-950 text-xs">
                            {% for op in opcoes.get('categoria_saida_mae', []) %}
                            <option value="{{ op.valor }}">{{ op.valor }}</option>
                            {% else %}
                            <option value="Dízimo dos Dízimos (Remessa Oficial)">📜 Dízimo dos Dízimos (Remessa Oficial)</option>
                            <option value="Quota da Sede Provincial">🏢 Quota da Sede Provincial</option>
                            {% endfor %}
                        </select>
                    </div>

                    <!-- SAÍDA PARA DEPARTAMENTOS -->
                    <div id="box_saida_depto" class="hidden space-y-3 p-3.5 bg-rose-50/70 rounded-xl border border-rose-200">
                        <div class="font-black text-rose-900 text-[10px] uppercase">Saída / Fundo Destinado a Departamento</div>
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">Qual Departamento recebe o valor? *</label>
                            <select name="departamento" class="w-full h-10 px-2 border-2 border-rose-300 rounded-xl bg-white font-extrabold text-indigo-900">
                                {% for op in opcoes.get('departamento', []) %}
                                <option value="{{ op.valor }}">{{ op.valor }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        <div>
                            <label class="block font-bold text-rose-900 mb-1">Propósito da Saída (Justificativa Obrigatória) *</label>
                            <textarea name="proposito" rows="2" placeholder="Ex: Compra de materiais didáticos da EBD / Lanche da vigília..." class="w-full p-2.5 border-2 border-rose-300 rounded-xl bg-white font-medium"></textarea>
                        </div>
                    </div>

                    <div>
                        <label class="block font-bold text-slate-700 mb-1">Observações Adicionais / Recibo</label>
                        <input type="text" name="descricao" placeholder="Nº do recibo, beneficiário ou detalhe complementar..." class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                    </div>

                    <button type="submit" class="w-full py-3.5 bg-emerald-700 hover:bg-emerald-800 text-white font-black rounded-xl shadow cursor-pointer text-sm transition">
                        💾 Confirmar e Lançar Movimento
                    </button>
                </form>
            </div>

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
                                <th class="py-2.5 px-2">Conta</th>
                                <th class="py-2.5 px-2">Âmbito & Classificação</th>
                                <th class="py-2.5 px-2 text-right">Valor</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for cx in caixa[:15] %}
                            <tr class="border-b border-slate-100 hover:bg-slate-50">
                                <td class="py-2.5 px-2 text-slate-600 font-semibold">{{ cx.data_movimento }}</td>
                                <td class="py-2.5 px-2">
                                    {% if 'banco' in (cx.conta or '')|lower %}
                                    <span class="bg-blue-100 text-blue-900 px-2 py-0.5 rounded font-black text-[10px]">🏦 Banco</span>
                                    {% else %}
                                    <span class="bg-amber-100 text-amber-900 px-2 py-0.5 rounded font-black text-[10px]">💵 Caixa</span>
                                    {% endif %}
                                </td>
                                <td class="py-2.5 px-2">
                                    <div class="flex items-center gap-1.5">
                                        {% if cx.destino_tipo == 'Igreja Mãe' %}
                                        <span class="bg-purple-100 text-purple-900 px-1.5 py-0.5 rounded text-[9px] font-black">🏢 Igreja Mãe</span>
                                        {% elif cx.destino_tipo == 'Departamento' %}
                                        <span class="bg-indigo-100 text-indigo-900 px-1.5 py-0.5 rounded text-[9px] font-black">👥 Depto</span>
                                        {% else %}
                                        <span class="bg-slate-200 text-slate-800 px-1.5 py-0.5 rounded text-[9px] font-black">🏛️ Local</span>
                                        {% endif %}
                                        <span class="font-bold {% if cx.tipo == 'Entrada' %}text-emerald-950{% else %}text-rose-950{% endif %}">
                                            {{ cx.categoria }}
                                        </span>
                                    </div>
                                    {% if cx.descricao %}
                                    <div class="text-[10px] text-slate-500 truncate max-w-xs mt-0.5">{{ cx.descricao }}</div>
                                    {% endif %}
                                </td>
                                <td class="py-2.5 px-2 text-right font-black {% if cx.tipo == 'Entrada' %}text-emerald-700{% else %}text-rose-700{% endif %}">
                                    {% if cx.tipo == 'Entrada' %}+{% else %}-{% endif %} {{ "%.2f"|format(cx.valor or 0) }} MT
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

        <script>
            function atualizarFormularioTesouraria() {
                var tipo = document.getElementById('tipo_movimento').value;
                var destinoTipo = document.getElementById('destino_tipo').value;

                var bEntGeral = document.getElementById('box_entrada_geral');
                var bEntMae = document.getElementById('box_entrada_mae');
                var bEntDepto = document.getElementById('box_entrada_depto');

                var bSaiGeral = document.getElementById('box_saida_geral');
                var bSaiMae = document.getElementById('box_saida_mae');
                var bSaiDepto = document.getElementById('box_saida_depto');

                bEntGeral.classList.add('hidden');
                bEntMae.classList.add('hidden');
                bEntDepto.classList.add('hidden');
                bSaiGeral.classList.add('hidden');
                bSaiMae.classList.add('hidden');
                bSaiDepto.classList.add('hidden');

                if (tipo === 'Entrada') {
                    if (destinoTipo === 'Igreja Geral') {
                        bEntGeral.classList.remove('hidden');
                    } else if (destinoTipo === 'Igreja Mãe') {
                        bEntMae.classList.remove('hidden');
                    } else if (destinoTipo === 'Departamento') {
                        bEntDepto.classList.remove('hidden');
                    }
                } else {
                    if (destinoTipo === 'Igreja Geral') {
                        bSaiGeral.classList.remove('hidden');
                    } else if (destinoTipo === 'Igreja Mãe') {
                        bSaiMae.classList.remove('hidden');
                    } else if (destinoTipo === 'Departamento') {
                        bSaiDepto.classList.remove('hidden');
                    }
                }
            }
        </script>
        {% endif %}

        <!-- ========================================================= -->
        <!-- ABA 7: DOUTRINA & BATISMO (COM GABINETE DO PROFESSOR)     -->
        <!-- ========================================================= -->
        {% if aba_ativa == 'doutrina' %}
        <div class="bg-amber-950 text-white p-6 rounded-2xl shadow mb-6 flex justify-between items-center">
            <div>
                <h2 class="text-2xl font-black">📖 Dashboard de Doutrina & Preparação Batismal</h2>
                <p class="text-xs text-amber-300 mt-1">Acompanhamento e aprovação de formandos para o Batismo nas Águas</p>
            </div>
            <div class="text-right">
                <span class="text-xs uppercase font-bold text-amber-300">Total Formandos</span>
                <div class="text-2xl font-black text-emerald-400">✅ {{ kpis.total_doutrina }} Inscritos</div>
            </div>
        </div>

        <!-- PAINEL DO PROFESSOR: ACOMPANHAMENTO E RESPOSTA A DÚVIDAS -->
        <div class="bg-white p-6 rounded-2xl shadow-sm border-2 border-indigo-200 space-y-4 mb-6 text-xs">
            <div class="border-b pb-2 flex justify-between items-center">
                <div>
                    <h3 class="font-extrabold text-base text-indigo-950 flex items-center gap-2">
                        <span>👨‍🏫</span> Gabinete do Instrutor / Professor de Doutrina & Discipulado
                    </h3>
                    <p class="text-[11px] text-slate-500">Responda diretamente às dúvidas bíblicas enviadas pelos seus formandos.</p>
                </div>
                <span class="bg-amber-100 text-amber-900 px-3 py-1 rounded-full text-xs font-black">
                    {{ duvidas_pendentes|length }} Dúvidas Pendentes
                </span>
            </div>

            <div class="space-y-3">
                {% for d in duvidas_pendentes %}
                <div class="p-4 bg-slate-50 rounded-2xl border border-slate-200 space-y-2">
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
                <p class="text-xs text-slate-400 py-2 italic text-center">Nenhuma dúvida bíblica pendente no momento.</p>
                {% endfor %}
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div class="lg:col-span-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">🎓 Inscrever Formando com Login</h3>
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
                            <label class="block font-semibold mb-1">Instrutor / Mentor</label>
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