import os
import jinja2

print("=" * 80)
print("A INSTALAR CONTEÚDO INTEGRAL DE ENSINO, RAIO-X DEMOGRÁFICO E ACTOS (CASAMENTOS/ÓBITOS)...")
print("=" * 80)

os.makedirs('templates', exist_ok=True)

# =============================================================================
# 1. ATUALIZAR APP.PY COM TABELAS DE CASAMENTOS/ÓBITOS E DEMOGRAFIA PROFUNDA
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
        f"""CREATE TABLE IF NOT EXISTS casamentos (
            id {pk}, tipo TEXT, noivo TEXT, noiva TEXT, data_casamento TEXT, 
            ministro TEXT, regime TEXT, certidao TEXT, criado_em TEXT
        );""",
        f"""CREATE TABLE IF NOT EXISTS obitos (
            id {pk}, nome_falecido TEXT, genero TEXT, categoria TEXT, 
            data_falecimento TEXT, local_funeral TEXT, causa TEXT, contacto_familia TEXT, criado_em TEXT
        );""",
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
            ('destino_tipo', 'TEXT'), ('departamento', 'TEXT'),
            ('proposito', 'TEXT'), ('criado_em', 'TEXT')
        ]:
            try: cur.execute(f"ALTER TABLE caixa ADD COLUMN {col} {tipo};")
            except: pass

        for col, tipo in [
            ('usuario', 'TEXT'), ('senha', 'TEXT'), ('aproveitamento', 'REAL DEFAULT 0'),
            ('classe', 'TEXT'), ('situacao', 'TEXT DEFAULT "Em Formação"')
        ]:
            try: cur.execute(f"ALTER TABLE doutrina ADD COLUMN {col} {tipo};")
            except: pass

        try: cur.execute("ALTER TABLE duvidas_alunos ADD COLUMN resposta_professor TEXT;")
        except: pass
        try: cur.execute("ALTER TABLE duvidas_alunos ADD COLUMN professor_nome TEXT;")
        except: pass

        if hasattr(conn, 'commit'): conn.commit()
    conn.close()

inicializar_banco()

# =============================================================================
# CURRÍCULO DE ENSINO: CONTEÚDO INTEGRAL E PROFUNDO (MANUAL OFICIAL IEADAO)
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
                    'introducao': 'Se o pecado não fosse uma triste realidade, seria desnecessária a Salvação consumada por Jesus no Calvário. A doutrina do pecado e da justificação é o alicerce fundamental para a compreensão da obra redentora.',
                    'pontos_doutrinarios': [
                        {
                            'titulo': '1. O Significado de Pecar: Errar o Alvo',
                            'detalhes': 'Pecar significa literalmente "Errar o Alvo", ou seja, errar o alvo soberano de fazer a Vontade de Deus, ferindo a Sua santidade e os Seus propósitos eternos para as nossas vidas.'
                        },
                        {
                            'titulo': '2. Transgressão e Desobediência à Lei Moral de Deus',
                            'detalhes': 'Pecar significa Transgredir a Lei de Deus. Quem transgride a Lei Moral de Deus está em rebelião aberta contra o Criador (Ex 20:3-17; 1Jo 3:4; Rm 5:14,19; Rm 8:7).\\n\\n• A DIFERENÇA CRUCIAL: Desobedecer é a causa; Transgredir é o efeito.\\n• A desobediência está escondida e oculta no coração humano; a transgressão está sempre exposta e visível nas atitudes exteriores.'
                        },
                        {
                            'titulo': '3. Lista de Pecados Condenados pelas Sagradas Escrituras',
                            'detalhes': 'A Palavra de Deus lista expressamente as obras da carne que separam o homem de Deus: Marcos 7:21-22; Romanos 1:29-31; Gálatas 5:19-21; Efésios 5:3; Colossenses 3:5-9. O crente em comunhão renuncia a toda a impureza, idolatria, feitiçaria, ódio, murmuração, mentira e imoralidade.'
                        },
                        {
                            'titulo': '4. A Situação Real do Homem Perante o Pecado',
                            'tabela': [
                                {'situacao': 'Imoralidade', 'descricao': 'Desfiguração total da imagem e semelhança divina no homem.', 'versiculos': 'Rm 3:9-12'},
                                {'situacao': 'Inimigo de Deus', 'descricao': 'Separação espiritual da presença, comunhão e favor de Deus.', 'versiculos': 'Is 59:2; Gl 5:4'},
                                {'situacao': 'Morte Espiritual', 'descricao': 'Separação definitiva e condenação eterna do Criador.', 'versiculos': 'Rm 3:23; Rm 6:23a'}
                            ]
                        },
                        {
                            'titulo': '5. A Posição Bíblica do Homem para se Libertar do Pecado',
                            'detalhes': 'a) Reconhecer sinceramente que é pecador perante Deus (Sl 51:3; Rm 3:23);\\nb) Saber com certeza que Deus ama o pecador e quer salvá-lo (Jo 3:16; Rm 5:8);\\nc) Arrepender-se verdadeiramente dos seus pecados com tristeza segundo Deus (Sl 51:1; At 2:37-38; 2Co 7:10);\\nd) Crer e aceitar a Cristo Jesus como único Salvador e Senhor absoluto da sua vida (Jo 1:12; Jo 3:3,18; At 16:30-31; 1Jo 5:12-13).'
                        },
                        {
                            'titulo': '6. O Perdão Divino: Expiação e Substituição',
                            'detalhes': 'Deus nos perdoou em Cristo (Mc 2:5; Lc 7:48; 1Jo 1:9). Cristo ofereceu Expiação e Propiciação — pagou com a Sua própria vida inocente o preço justo da ira santa de Deus. "Sem derramamento de sangue não há remissão" (Hb 9:22).\\n\\n• O perdão de Deus é manifestação viva da Sua Graça:\\n  - Bondade de Deus (Sl 86:5);\\n  - Justiça de Deus pela Justificação — Cristo assumiu nossa culpa e declarou-nos justos (Rm 3:25);\\n  - Fidelidade de Deus (1Jo 1:9);\\n  - Compaixão de Deus, lançando os pecados nas profundezas do mar (Mq 7:18-19).\\n\\n• A REGRA DE OURO DA GRAÇA: Quando Cristo perdoa, Ele não só retira o mal (o pecado e a culpa), mas coloca algo santo que o substitui: Amor, Graça, Paz e Gozo no Espírito Santo!'
                        }
                    ],
                    'proverbio_chave': 'O que encobre as suas transgressões, nunca prosperará; mas o que as confessa e deixa, alcançará misericórdia. (Provérbios 28:13)'
                },
                'questoes': [
                    {'p': 'Qual é a diferença exata entre desobedecer e transgredir apresentada no Manual?', 'ops': ['Transgredir é apenas mental e desobedecer é um crime público.', 'Desobedecer é a causa oculta no coração; transgredir é o efeito manifesto e exposto.', 'Não existe nenhuma diferença entre ambos.', 'Desobedecer aplica-se só a crianças e transgredir a membros batizados.'], 'c': 1},
                    {'p': 'Segundo o Manual, o que acontece espiritualmente quando Cristo perdoa o homem?', 'ops': ['Apenas suspende o castigo temporariamente.', 'Não apenas retira o mal e a culpa, mas coloca o bem que o substitui (Amor, Graça, Paz e Gozo).', 'Exige sacrifícios materiais em dinheiro para validar o perdão.', 'Torna desnecessária a santificação diária.'], 'c': 1},
                    {'p': 'Conforme a tabela da Situação do Homem perante o Pecado, o que significa a Imoralidade?', 'ops': ['Desfiguração da imagem divina no homem (Rm 3:9-12).', 'Um sentimento passageiro de tristeza.', 'A perda temporária de bens materiais.', 'Apenas desobediência civil às leis.'], 'c': 0}
                ]
            },
            {
                'id': 'c1_l2',
                'numero': 'Lição 2',
                'titulo': 'Salvação e Senhorio de Cristo',
                'texto_aureo': 'Assim que, se alguém está em Cristo, nova criatura é; as coisas velhas já passaram; eis que tudo se fez novo. (2Co 5:17)',
                'leitura_base': 'Ef 2:8-10; Jo 1:12; 1Co 8:6; Cl 1:21-22',
                'conteudo_completo': {
                    'introducao': 'A separação entre Deus e os homens é resultado direto do pecado (Rm 3:23; Is 59:2). Somos salvos unicamente pela graça por meio da fé e não por obras, para que ninguém se glorie (Ef 2:8-9). As boas obras são o resultado indispensável da salvação operada no coração regenerado.',
                    'pontos_doutrinarios': [
                        {'titulo': '1. Os Passos para a Filiação Divina', 'detalhes': 'Ouvir a Palavra (Rm 10:17), Crer no testemunho divino (Jo 3:16), Arrepender-se e Confessar (Rm 10:9; 1Jo 1:9) e Receber a Cristo no trono da vida (Jo 1:12; Ap 3:20).'},
                        {'titulo': '2. Os Dois Tronos do Coração', 'detalhes': 'O coração humano possui um trono. Se o "EU" estiver entronizado, os interesses e atividades são governados pelo ego, gerando frustração e discórdia. Quando CRISTO é entronizado como Senhor (1Co 8:6; 2Co 5:15), a vida experimenta harmonia, fruto e direção divina.'}
                    ],
                    'proverbio_chave': 'Cristo não só pode e quer salvar a alma, mas deseja dominar e reinar sobre toda a vida do cristão.'
                },
                'questoes': [
                    {'p': 'Qual é o papel das obras na doutrina bíblica da salvação?', 'ops': ['As obras são o preço pago para comprar o perdão.', 'Somos salvos pela graça mediante a fé, e as boas obras são o fruto e resultado de estarmos em Cristo.', 'O salvo não tem qualquer compromisso com boas obras.', 'Apenas as obras dos pastores são aceitas por Deus.'], 'c': 1}
                ]
            },
            {
                'id': 'c1_l5',
                'numero': 'Lição 5',
                'titulo': 'A Bíblia - Manual de Fé dos Cristãos',
                'texto_aureo': 'Lâmpada para os meus pés é a tua palavra e luz para o meu caminho. (Sl 119:105)',
                'leitura_base': '2Tm 3:16; Js 1:8; Sl 1:2; 2Pe 1:21',
                'conteudo_completo': {
                    'introducao': 'Não se pode conhecer e obedecer a Deus e à Sua santa Vontade sem conhecermos a Sua Palavra revelada. A Bíblia é infalível, inerrante e o nosso único manual supremo de fé e conduta.',
                    'pontos_doutrinarios': [
                        {'titulo': '1. Inspiração e Origem Divina', 'detalhes': 'Cerca de 40 homens santos escreveram as Escrituras num período de aproximadamente 1600 anos sob inspiração do Espírito Santo. O Autor é Deus, o Intérprete é o Espírito Santo e o Tema Central é Jesus Cristo.'},
                        {'titulo': '2. Os 66 Livros Canónicos', 'detalhes': 'O Antigo Testamento possui 39 livros (Pentateuco, Históricos, Poéticos, Profetas Maiores e Menores). O Novo Testamento possui 27 livros (Evangelhos, Histórico, Epístolas Paulinas, Gerais e Apocalipse).'}
                    ],
                    'proverbio_chave': 'Toda a Escritura é divinamente inspirada e proveitosa para ensinar, redarguir, corrigir e instruir em justiça. (2Tm 3:16)'
                },
                'questoes': [
                    {'p': 'Qual é a estrutura canónica da Bíblia Sagrada?', 'ops': ['39 livros no Antigo Testamento e 27 no Novo Testamento (Total: 66 livros).', '46 no AT e 27 no NT.', '30 no AT e 36 no NT.', '50 no AT e 16 no NT.'], 'c': 0}
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
                    'introducao': 'A oração é a respiração da alma e o jejum é o aprimoramento da sensibilidade espiritual através da subjugação da carne.',
                    'pontos_doutrinarios': [
                        {'titulo': '1. A Oração Perseverante', 'detalhes': 'Orar é um mandamento (1Ts 5:17). As orações sobem como incenso agradável ao altar do Senhor (Ap 5:8; Sl 141:2). O Espírito Santo intercede em nós com gemidos inexprimíveis (Rm 8:26).'},
                        {'titulo': '2. O Verdadeiro Sentido do Jejum Bíblico', 'detalhes': 'O jejum é a abstinência total ou parcial de alimento para o domínio do corpo e da alma (Sl 69:10). Torna o crente sensível à voz do Espírito Santo. O jejum agradável a Deus deve ser acompanhado de confissão e obras de amor ao próximo (Is 58:6-7).'}
                    ],
                    'proverbio_chave': 'O importante a guardar no jejum é: para quem o estamos fazendo e não somente porque o fazemos.'
                },
                'questoes': [
                    {'p': 'Qual é o espírito correto do jejum ensinado em Isaías 58?', 'ops': ['Exibição de piedade.', 'Humilhação do corpo para sensibilidade espiritual acompanhada de amor e justiça ao próximo.', 'Greve de fome.', 'Apenas desintoxicação física.'], 'c': 1}
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
                    'introducao': 'O crente vive por fé na Palavra eterna de Deus e não guiado pelas emoções instáveis da alma humana.',
                    'pontos_doutrinarios': [
                        {'titulo': '1. A Ilustração Pastoral do Comboio', 'detalhes': '1) A LOCOMOTIVA é o FACTO (A Palavra infalível de Deus);\\n2) O CARRO DE LIGAÇÃO é a FÉ (A nossa confiança absoluta no Facto);\\n3) O VAGÃO TRASEIRO são os SENTIMENTOS (As emoções passageiras).\\n\\nO comboio anda com ou sem o vagão. Nunca tente puxar o comboio pelo vagão das emoções!'},
                        {'titulo': '2. A Inconstância do Coração', 'detalhes': 'O coração humano é por vezes enganoso (Jr 17:9). Quando não sentimos nada, continuamos a crer porque Deus prometeu e Ele é fiel (Js 23:14).'}
                    ],
                    'proverbio_chave': 'Porque andamos por fé e não por vista. (2 Coríntios 5:7)'
                },
                'questoes': [
                    {'p': 'Na analogia do comboio da fé, o que representa a Locomotiva?', 'ops': ['Os sentimentos de alegria.', 'O Facto soberano de Deus e as promessas da Sua Palavra.', 'A opinião dos homens.', 'Os nossos jejuns.'], 'c': 1}
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
                    'introducao': 'As duas ordenanças instituídas por Jesus para a Sua Igreja são o Baptismo nas Águas por imersão e a Santa Ceia.',
                    'pontos_doutrinarios': [
                        {'titulo': '1. O Significado do Baptismo nas Águas', 'detalhes': 'É o testemunho público da lavagem interior da salvação (Tt 3:5). Simboliza a morte e sepultamento para o pecado ao descer às águas e o ressurgimento vitorioso para uma nova vida ao sair delas (Rm 6:4).'},
                        {'titulo': '2. As Três Dimensões da Santa Ceia', 'detalhes': '• PASSADO (Comemorativa): Relembra a morte expiatória de Cristo na cruz ("Fazei isto em memória de mim");\\n• PRESENTE (Instrutiva): Autoexame pessoal, comunhão e reconciliação ("Examine-se o homem a si mesmo");\\n• FUTURO (Inspiradora): A gloriosa esperança do Arrebatamento da Noiva ("Até que Ele venha").'}
                    ],
                    'proverbio_chave': 'Fazei isto em memória de mim. Porque todas as vezes que comerdes este pão e beberdes este cálice anunciais a morte do Senhor, até que venha. (1Co 11:24,26)'
                },
                'questoes': [
                    {'p': 'Quais são os três olhares temporais sagrados da Santa Ceia?', 'ops': ['Passado Comemorativo, Presente Instrutivo e Futuro Inspirador.', 'Ontem, hoje e amanhã.', 'Nenhum olhar específico.', 'Apenas lembrar os apóstolos.'], 'c': 0}
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
# CONTEXT PROCESSOR: DEMOGRAFIA PURA (ZERO FINANÇAS NO RAIO-X)
# =============================================================================
@app.context_processor
def injetar_dados():
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

    # 1. DEMOGRAFIA E PESSOAS (RAIO-X 100% DEMOGRÁFICO)
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

    # Frequência Média aos Cultos
    total_pres = sum([int(c.get('total_presentes') or 0) for c in cultos])
    media_culto = int(total_pres / len(cultos)) if cultos else 0

    # 2. FINANÇAS (APENAS PARA DASHBOARD FINANCEIRO E TESOURARIA)
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
# ROTAS GERAIS & MÓDULO DE ACTOS (CASAMENTOS E ÓBITOS)
# =============================================================================
@app.route('/')
def index():
    aba = request.args.get('aba', 'dashboard')
    id_relatar = request.args.get('relatar_id')
    plano_para_relatar = None
    if id_relatar:
        m = "%s" if DATABASE_URL else "?"
        plano_para_relatar = consultar_um(f"SELECT * FROM planificacao WHERE id = {m}", (id_relatar,))
    return render_template('dashboard.html', aba_ativa=aba, plano_relatar=plano_para_relatar)

# 1. Registo de Casamentos
@app.route('/actos/casamento/novo', methods=['POST'])
def actos_casamento_novo():
    fd = request.form
    tipo = fd.get('tipo', 'Adultos').strip()
    noivo = fd.get('noivo', '').strip()
    noiva = fd.get('noiva', '').strip()
    dt = fd.get('data_casamento', datetime.now().strftime('%Y-%m-%d')).strip()
    ministro = fd.get('ministro', 'Pastor').strip()
    regime = fd.get('regime', 'Comunhão de Bens').strip()
    certidao = fd.get('certidao', '').strip()
    m = "%s" if DATABASE_URL else "?"
    sql = f"""INSERT INTO casamentos (tipo, noivo, noiva, data_casamento, ministro, regime, certidao, criado_em)
              VALUES ({m}, {m}, {m}, {m}, {m}, {m}, {m}, {m})"""
    executar_comando(sql, (tipo, noivo, noiva, dt, ministro, regime, certidao, datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=actos')

@app.route('/actos/casamento/remover/<int:id>')
def actos_casamento_remover(id):
    m = "%s" if DATABASE_URL else "?"
    executar_comando(f"DELETE FROM casamentos WHERE id = {m}", (id,))
    return redirect('/?aba=actos')

# 2. Registo de Óbitos
@app.route('/actos/obito/novo', methods=['POST'])
def actos_obito_novo():
    fd = request.form
    nome = fd.get('nome_falecido', '').strip()
    genero = fd.get('genero', 'Masculino').strip()
    cat = fd.get('categoria', 'Baptizados').strip()
    dt_falec = fd.get('data_falecimento', datetime.now().strftime('%Y-%m-%d')).strip()
    local_fun = fd.get('local_funeral', 'Chicuque').strip()
    causa = fd.get('causa', '').strip()
    contacto = fd.get('contacto_familia', '').strip()
    m = "%s" if DATABASE_URL else "?"
    sql = f"""INSERT INTO obitos (nome_falecido, genero, categoria, data_falecimento, local_funeral, causa, contacto_familia, criado_em)
              VALUES ({m}, {m}, {m}, {m}, {m}, {m}, {m}, {m})"""
    executar_comando(sql, (nome, genero, cat, dt_falec, local_fun, causa, contacto, datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=actos')

@app.route('/actos/obito/remover/<int:id>')
def actos_obito_remover(id):
    m = "%s" if DATABASE_URL else "?"
    executar_comando(f"DELETE FROM obitos WHERE id = {m}", (id,))
    return redirect('/?aba=actos')

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

# =============================================================================
# PORTAL DO ALUNO (/ensino/login, /ensino/aulas)
# =============================================================================
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

# =============================================================================
# SECRETARIA, BALANÇO ANUAL E RELATÓRIO OFICIAL DINÂMICO
# =============================================================================
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
    casamentos = consultar_todos("SELECT * FROM casamentos")
    obitos = consultar_todos("SELECT * FROM obitos")

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
        'tot_geral': (sub_m_ant_h + sub_m_nov_h) + (sub_m_ant_m + sub_m_nov_m)
    }

    tot_geral_dict = {
        'ant_h': sub_ant_h + sub_m_ant_h, 'ant_m': sub_ant_m + sub_m_ant_m, 'ant_tot': (sub_ant_h + sub_m_ant_h) + (sub_ant_m + sub_m_ant_m),
        'nov_h': sub_nov_h + sub_m_nov_h, 'nov_m': sub_nov_m + sub_m_nov_m, 'nov_tot': (sub_nov_h + sub_m_nov_h) + (sub_nov_m + sub_m_nov_m),
        'tot_h': (sub_ant_h + sub_nov_h) + (sub_m_ant_h + sub_m_nov_h),
        'tot_m': (sub_ant_m + sub_nov_m) + (sub_m_ant_m + sub_m_nov_m),
        'tot_geral': (sub_ant_h + sub_nov_h + sub_m_ant_h + sub_m_nov_h) + (sub_ant_m + sub_nov_m + sub_m_ant_m + sub_m_nov_m)
    }

    # 3. ACTIVIDADES E CASAMENTOS REAIS
    planos_exec = [p for p in planos if str(p.get('status') or '').strip().lower() == 'executado']

    cj = len([c for c in casamentos if 'jov' in str(c.get('tipo', '')).lower()])
    ca = len([c for c in casamentos if 'jov' not in str(c.get('tipo', '')).lower()])

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

    # Óbitos Reais por Categoria
    def contar_obitos_cat(termo):
        return len([o for o in obitos if termo in str(o.get('categoria', '')).lower()])

    perdas_obitos = {
        'desistentes_h': 0, 'desistentes_m': 0,
        'obitos_pastores': contar_obitos_cat('pastor'),
        'obitos_maes_pastoras': contar_obitos_cat('mãe pastora'),
        'obitos_presbiteros': contar_obitos_cat('presb'),
        'obitos_evangelistas': contar_obitos_cat('evang'),
        'obitos_diaconos': contar_obitos_cat('diác') + contar_obitos_cat('diac'),
        'obitos_baptizados': contar_obitos_cat('baptiz') + contar_obitos_cat('batiz'),
        'obitos_novos_convertidos': contar_obitos_cat('novo conv') + contar_obitos_cat('convert'),
        'obitos_juventude': contar_obitos_cat('jov') + contar_obitos_cat('juvent'),
        'obitos_boa_esperanca': contar_obitos_cat('esperan') + contar_obitos_cat('crian')
    }

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
        'casamentos': {'jovens': cj, 'adultos': ca, 'total': cj + ca},
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
        'perdas': perdas_obitos,
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
print("✓ app.py: Actualizado com tabelas de Casamentos, Óbitos, Demografia e Ensino sem cortes!")

# =============================================================================
# 2. RECONSTRUIR DASHBOARD.HTML: RAIO-X PURAMENTE DEMOGRÁFICO E ABA DE ACTOS
# =============================================================================
with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    dash_html = f.read()

# Substituir o Raio-X Geral (Dashboard) para Demografia Pura sem Finanças
novo_raiox_demografico = """        <!-- ========================================================= -->
        <!-- ABA: RAIO-X ECLESIÁSTICO & DEMOGRAFIA (ZERO FINANÇAS)     -->
        <!-- ========================================================= -->
        {% if aba_ativa == 'dashboard' %}
        <div class="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white p-6 rounded-3xl shadow-xl mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
                <div class="inline-flex items-center gap-2 bg-indigo-500/20 text-indigo-300 px-3 py-1 rounded-full text-[10px] font-black uppercase mb-1 border border-indigo-400/30">
                    <span>🔬</span> CENSO MINISTERIAL • ANÁLISE DEMOGRÁFICA PROFUNDA
                </div>
                <h2 class="text-2xl sm:text-3xl font-black">Raio-X Eclesiástico & Estatística de Almas</h2>
                <p class="text-xs text-indigo-200 mt-1">Visão demográfica consolidada da congregação (Sede Chicuque) sem interferência financeira</p>
            </div>
            <div class="bg-white/10 p-4 rounded-2xl border border-white/10 text-center shrink-0">
                <span class="text-[10px] uppercase font-bold text-indigo-200 block">Total de Almas no Rebanho</span>
                <span class="text-3xl font-black text-amber-300">{{ demografia.total_almas }} Vidas</span>
                <span class="text-[10px] text-slate-300 block mt-0.5">{{ demografia.membros_cadastrados }} Membros • {{ demografia.novos_convertidos }} em Discipulado</span>
            </div>
        </div>

        <!-- 4 CARDS DEMOGRÁFICOS PRINCIPAIS -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-8 text-xs">
            <!-- GÉNERO -->
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

            <!-- FAIXAS ETÁRIAS / DEPARTAMENTOS -->
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

            <!-- BATISMO E DISCIPULADO -->
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

            <!-- ACTIVIDADES SOCIAIS E ACTOS -->
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

        <!-- DISTRIBUIÇÃO GEOGRÁFICA (ZONAS E CÉLULAS) & CORPO MINISTERIAL -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8 text-xs">
            <!-- ZONAS E CÉLULAS -->
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 space-y-4">
                <h3 class="font-extrabold text-sm text-slate-900 border-b pb-2 flex items-center gap-2">
                    <span>📍</span> Cartografia Ministerial: Zonas e Células Familiares
                </h3>
                <div class="space-y-3">
                    <div>
                        <span class="font-bold text-slate-600 text-[11px] uppercase block mb-1.5">Distribuição por Zonas da Cidade:</span>
                        <div class="grid grid-cols-2 gap-2">
                            {% for z, qtd in demografia.zonas.items() %}
                            <div class="p-2.5 bg-slate-50 border rounded-xl flex justify-between items-center">
                                <span class="font-semibold text-slate-700 truncate">{{ z }}</span>
                                <span class="bg-indigo-100 text-indigo-900 px-2 py-0.5 rounded-full font-black text-[11px]">{{ qtd }}</span>
                            </div>
                            {% endfor %}
                        </div>
                    </div>

                    <div class="pt-2 border-t">
                        <span class="font-bold text-slate-600 text-[11px] uppercase block mb-1.5">Células Familiares Activas:</span>
                        <div class="flex flex-wrap gap-2">
                            {% for c, qtd in demografia.celulas.items() %}
                            <span class="bg-slate-100 border text-slate-800 px-3 py-1 rounded-xl font-bold flex items-center gap-1.5">
                                <span>🏠 {{ c }}:</span>
                                <b class="text-indigo-900">{{ qtd }} membros</b>
                            </span>
                            {% endfor %}
                        </div>
                    </div>
                </div>
            </div>

            <!-- CORPO MINISTERIAL E OBREIROS -->
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
                    {% endfor %}
                </div>
            </div>
        </div>
        {% endif %}"""

# Substituição do bloco dashboard no dashboard.html
regex_dash = r'<!-- ========================================================= -->\s*<!-- ABA: PAINEL GERAL & METAS[\s\S]*?{% endif %}'
dash_html = re.sub(regex_dash, novo_raiox_demografico, dash_html)

# Adicionar link de navegação para a aba "Actos: Casamentos & Óbitos" no menu lateral
if 'href="/?aba=actos"' not in dash_html:
    dash_html = dash_html.replace(
        '<span>🌱</span><span>4. Novos Convertidos</span>\n                </a>',
        '<span>🌱</span><span>4. Novos Convertidos</span>\n                </a>\n\n                <a href="/?aba=actos" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == \'actos\' %}bg-pink-700 text-white shadow-md{% else %}text-pink-300 hover:bg-slate-800{% endif %}">\n                    <span>💒</span><span>Actos (Casamentos & Óbitos)</span>\n                </a>'
    )

# Adicionar a secção da aba "Actos" no corpo do dashboard.html
secao_actos_html = """        <!-- ========================================================= -->
        <!-- ABA: ACTOS ECLESIÁSTICOS (CASAMENTOS & ÓBITOS)            -->
        <!-- ========================================================= -->
        {% if aba_ativa == 'actos' %}
        <div class="bg-gradient-to-r from-pink-950 via-slate-900 to-slate-900 text-white p-6 rounded-3xl shadow mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
                <div class="inline-flex items-center gap-2 bg-pink-500/20 text-pink-300 px-3 py-1 rounded-full text-[10px] font-black uppercase mb-1 border border-pink-400/30">
                    <span>💒</span> REGISTO DE ACTOS PASTORAIS & NOTARIAIS
                </div>
                <h2 class="text-2xl font-black">Registo de Casamentos & Registo de Óbitos</h2>
                <p class="text-xs text-pink-200 mt-0.5">Gestão solene dos casamentos celebrados e registo de condolências e óbitos da membresia</p>
            </div>
            <div class="flex gap-3">
                <a href="/secretaria/relatorio-anual" target="_blank" class="px-4 py-2 bg-amber-500 hover:bg-amber-600 text-slate-950 font-black rounded-xl text-xs shadow flex items-center gap-1.5">
                    <span>📄</span><span>Ver no Relatório Anual Oficial</span>
                </a>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 text-xs">
            
            <!-- 1. CASAMENTOS -->
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

                <!-- TABELA DE CASAMENTOS -->
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
                                    <td class="py-2.5 px-1">
                                        <span class="bg-pink-50 text-pink-800 px-2 py-0.5 rounded font-bold text-[10px]">{{ cs.tipo }}</span>
                                    </td>
                                    <td class="py-2.5 px-1 text-right">
                                        <a href="/actos/casamento/remover/{{ cs.id }}" onclick="return confirm('Excluir registo?')" class="text-rose-500 hover:text-rose-700 font-bold text-xs">Excluir</a>
                                    </td>
                                </tr>
                                {% else %}
                                <tr><td colspan="4" class="py-6 text-center text-slate-400 italic">Nenhum casamento registado no período.</td></tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- 2. ÓBITOS -->
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
                                <label class="block font-bold text-slate-700 mb-1">Contacto da Família Enlutada</label>
                                <input type="text" name="contacto_familia" placeholder="+258..." class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                            </div>
                        </div>

                        <button type="submit" class="w-full py-3 bg-slate-800 hover:bg-slate-900 text-white font-black rounded-xl shadow cursor-pointer transition">
                            🕊️ Gravar Registo de Óbito
                        </button>
                    </form>
                </div>

                <!-- TABELA DE ÓBITOS -->
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
                                    <td class="py-2.5 px-1">
                                        <span class="bg-slate-100 text-slate-800 px-2 py-0.5 rounded font-bold text-[10px]">{{ ob.categoria }}</span>
                                    </td>
                                    <td class="py-2.5 px-1 text-right">
                                        <a href="/actos/obito/remover/{{ ob.id }}" onclick="return confirm('Excluir registo?')" class="text-rose-500 hover:text-rose-700 font-bold text-xs">Excluir</a>
                                    </td>
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
        {% endif %}"""

if '<!-- ABA: ACTOS ECLESIÁSTICOS' not in dash_html:
    dash_html = dash_html.replace(
        '<!-- ========================================================= -->\n        <!-- ABA 1: MEMBROS & RELATÓRIOS OFICIAIS',
        secao_actos_html + '\n\n        <!-- ========================================================= -->\n        <!-- ABA 1: MEMBROS & RELATÓRIOS OFICIAIS'
    )

env = jinja2.Environment()
env.parse(dash_html)
with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(dash_html)
print("✓ templates/dashboard.html: Raio-X Demográfico e Aba de Actos integrados com validação Jinja2!")

# =============================================================================
# 3. ATUALIZAR TEMPLATES/PORTAL_ALUNO.HTML COM O CONTEÚDO INTEGRAL DE ENSINO
# =============================================================================
portal_html_integral = """<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portal do Aluno - IEAD Chicuque</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .card-bg { background: linear-gradient(135deg, #090d16 0%, #1e1b4b 60%, #312e81 100%); }
        table, th, td { border: 1px solid #cbd5e1 !important; }
    </style>
</head>
<body class="bg-slate-100 text-slate-800 font-sans min-h-screen flex flex-col">

    <!-- BARRA SUPERIOR -->
    <header class="bg-slate-900 text-white px-6 py-4 flex justify-between items-center shadow-lg border-b border-indigo-900 sticky top-0 z-50">
        <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-2xl bg-gradient-to-tr from-indigo-500 to-amber-400 flex items-center justify-center font-black text-xl shadow">
                AD
            </div>
            <div>
                <h1 class="font-black text-sm uppercase tracking-wider">ESCOLA DE INTEGRAÇÃO & DOUTRINA</h1>
                <p class="text-[11px] text-amber-300 font-bold">Assembleia de Deus • Sede Regional de Chicuque</p>
            </div>
        </div>

        <div class="flex items-center gap-4 text-xs">
            <div class="text-right">
                <span class="text-[10px] text-slate-400 block uppercase font-bold">Aluno Conectado</span>
                <span class="font-extrabold text-white">{{ aluno.nome_aluno }}</span>
            </div>
            <a href="/ensino/logout" class="bg-rose-600 hover:bg-rose-700 text-white px-3.5 py-1.5 rounded-xl font-bold shadow text-xs transition">
                Sair
            </a>
        </div>
    </header>

    <main class="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">

        <!-- BOAS-VINDAS E CARD DO PROFESSOR -->
        <div class="card-bg text-white p-6 sm:p-8 rounded-3xl shadow-xl flex flex-col lg:flex-row lg:items-center justify-between gap-6">
            <div class="space-y-2">
                <span class="bg-amber-400 text-slate-950 text-[10px] font-black uppercase px-3 py-1 rounded-full shadow">
                    Plataforma Oficial de Formação Ministerial
                </span>
                <h2 class="text-2xl sm:text-3xl font-black">
                    Graça e Paz, {{ aluno.nome_aluno }}!
                </h2>
                <p class="text-xs sm:text-sm text-indigo-200 max-w-2xl leading-relaxed">
                    Você está estudando o <b>Manual Oficial de Candidatos e Integração da IEADAO</b> na íntegra. Leia cada fundamento bíblico com reverência, faça o seu resumo reflexivo e realize o teste de fixação.
                </p>
            </div>

            <!-- CARD DE PROGRESSO & INSTRUTOR -->
            <div class="bg-white/10 backdrop-blur-md border border-white/20 p-5 rounded-3xl text-center shrink-0 w-full lg:w-72 space-y-3">
                <div>
                    <span class="text-[10px] uppercase font-bold text-indigo-200 block">Aproveitamento Curricular</span>
                    <div class="text-3xl font-black mt-0.5 text-amber-300">
                        {{ "%.1f"|format(aluno.aproveitamento or 0) }}%
                    </div>
                    <div class="w-full bg-slate-900/60 h-2 rounded-full overflow-hidden my-2 border border-white/10">
                        <div class="bg-emerald-400 h-full rounded-full transition-all duration-700" style="width: {{ [aluno.aproveitamento or 0, 100]|min }}%"></div>
                    </div>
                </div>

                <div class="border-t border-white/10 pt-2 text-left bg-white/5 p-2.5 rounded-xl">
                    <span class="text-[9px] uppercase font-bold text-amber-300 block">👨‍🏫 Instrutor / Pai na Fé</span>
                    <span class="text-xs font-black text-white block truncate">{{ aluno.professor or "Pastor Dirigente" }}</span>
                    <span class="text-[10px] text-indigo-200 block mt-0.5">{{ aluno.classe }}</span>
                </div>

                {% if todas_concluidas %}
                <a href="/ensino/exame_final" class="block w-full py-2 bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-black rounded-xl text-xs shadow transition">
                    🏆 Fazer Exame Final & Obter Certificado
                </a>
                {% endif %}
            </div>
        </div>

        {% if request.args.get('sucesso_aprovado') %}
        <div class="bg-emerald-50 border-2 border-emerald-400 p-4 rounded-2xl flex items-center justify-between text-emerald-900 text-xs font-bold shadow">
            <span>🎉 Glória a Deus! Concluiu a lição anterior com aproveitamento $\ge$ 70%! A lição seguinte foi destravada para o seu estudo!</span>
        </div>
        {% endif %}

        {% if request.args.get('nota_resultado') %}
        <div class="bg-amber-50 border-2 border-amber-400 p-4 rounded-2xl flex items-center justify-between text-amber-900 text-xs font-bold shadow">
            <span>⚠️ Atingiu {{ request.args.get('nota_resultado') }}%. É necessário no mínimo 70% para destrancar a próxima lição. Reveja os tópicos e repita o teste abaixo.</span>
        </div>
        {% endif %}

        <!-- CURRÍCULO AGRUPADO POR CLASSES (SIDEBAR + CONTEÚDO) -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">

            <!-- COLUNA DA ESQUERDA: AS 4 CLASSES -->
            <div class="lg:col-span-4 space-y-4">
                <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200">
                    <h3 class="font-extrabold text-sm uppercase text-slate-900 mb-3 border-b pb-2 flex items-center gap-2">
                        <span>📚</span> Currículo Oficial por Classes
                    </h3>

                    <div class="space-y-4">
                        {% for classe in curriculo %}
                        <div class="border border-slate-200 rounded-xl p-3 bg-slate-50">
                            <div class="font-black text-xs text-indigo-950 uppercase mb-1">
                                {{ classe.nome_classe }}
                            </div>
                            <p class="text-[10px] text-slate-500 mb-2.5">{{ classe.descricao }}</p>

                            <div class="space-y-1.5">
                                {% for l in classe.licoes %}
                                {% set st = licoes_status[l.id] %}
                                
                                {% if st.status == 'concluida' %}
                                <a href="/ensino/aulas?licao={{ l.id }}" class="flex items-center justify-between p-2 rounded-lg text-xs font-bold transition {% if licao.id == l.id %}bg-indigo-600 text-white{% else %}bg-emerald-50 text-emerald-900 hover:bg-emerald-100{% endif %}">
                                    <span class="truncate">✅ {{ l.numero }}: {{ l.titulo }}</span>
                                    <span class="text-[10px] bg-emerald-200 text-emerald-950 px-2 py-0.5 rounded-full font-black ml-1">{{ st.nota }}%</span>
                                </a>
                                {% elif st.status == 'em_estudo' %}
                                <a href="/ensino/aulas?licao={{ l.id }}" class="flex items-center justify-between p-2 rounded-lg text-xs font-bold transition {% if licao.id == l.id %}bg-indigo-600 text-white shadow-md{% else %}bg-blue-100 text-blue-900 border border-blue-300 hover:bg-blue-200{% endif %}">
                                    <span class="truncate">📖 {{ l.numero }}: {{ l.titulo }}</span>
                                    <span class="text-[10px] bg-amber-400 text-slate-950 px-2 py-0.5 rounded-full font-black ml-1">EM ESTUDO</span>
                                </a>
                                {% else %}
                                <div class="flex items-center justify-between p-2 rounded-lg text-xs text-slate-400 bg-slate-100 cursor-not-allowed">
                                    <span class="truncate">🔒 {{ l.numero }}: {{ l.titulo }}</span>
                                    <span class="text-[10px] text-slate-400">Trancada</span>
                                </div>
                                {% endif %}
                                {% endfor %}
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>

            <!-- COLUNA DA DIREITA: CONTEÚDO INTEGRAL PROFUNDO -->
            <div class="lg:col-span-8 space-y-6">

                <!-- ETAPA 1: ESTUDO INTEGRAL DA LIÇÃO -->
                <div class="bg-white p-6 sm:p-8 rounded-3xl shadow-sm border border-slate-200 space-y-6">
                    <div class="border-b border-slate-100 pb-4">
                        <span class="text-xs font-black uppercase text-indigo-600 tracking-wider">
                            ETAPA 1: ESTUDO DOUTRINÁRIO PROFUNDO (MANUAL DA IEADAO)
                        </span>
                        <h2 class="text-2xl sm:text-3xl font-black text-slate-900 mt-1">{{ licao.numero }}: {{ licao.titulo }}</h2>
                        <p class="text-xs text-slate-500 mt-0.5">Leitura Bíblica de Apoio: <b>{{ licao.leitura_base }}</b></p>
                    </div>

                    <!-- TEXTO ÁUREO -->
                    <div class="bg-amber-50 border-l-4 border-amber-500 p-4 rounded-r-2xl">
                        <span class="text-[10px] font-black uppercase text-amber-900 block mb-1">🔥 Texto Áureo da Lição</span>
                        <p class="text-sm italic text-amber-950 font-serif leading-relaxed">"{{ licao.texto_aureo }}"</p>
                    </div>

                    <!-- INTRODUÇÃO DA LIÇÃO -->
                    <div class="text-xs text-slate-700 leading-relaxed text-justify bg-slate-50 p-4 rounded-2xl border border-slate-200">
                        <p class="font-bold text-slate-900 mb-1">Prefácio Temático:</p>
                        <p>{{ licao.conteudo_completo.introducao }}</p>
                    </div>

                    <!-- PONTOS DOUTRINÁRIOS DETALHADOS -->
                    <div class="space-y-4 text-xs">
                        {% for pt in licao.conteudo_completo.pontos_doutrinarios %}
                        <div class="p-5 rounded-2xl border border-slate-200 bg-white shadow-sm space-y-2.5">
                            <h4 class="font-black text-sm text-indigo-950 flex items-center gap-1.5">
                                <span class="w-2 h-2 rounded-full bg-indigo-600"></span> {{ pt.titulo }}
                            </h4>

                            {% if pt.detalhes %}
                            <p class="text-slate-700 leading-relaxed text-justify whitespace-pre-line">{{ pt.detalhes }}</p>
                            {% endif %}

                            <!-- TABELA DE SITUAÇÃO DO HOMEM PERANTE O PECADO -->
                            {% if pt.tabela %}
                            <div class="overflow-x-auto pt-2">
                                <table class="w-full text-left border-collapse text-xs">
                                    <thead>
                                        <tr class="bg-slate-100 font-bold uppercase text-[10px]">
                                            <th class="p-2 w-1/4">Situação</th>
                                            <th class="p-2">Descrição Espiritual</th>
                                            <th class="p-2 w-1/4">Versículos</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for l in pt.tabela %}
                                        <tr class="hover:bg-slate-50">
                                            <td class="p-2 font-bold text-rose-900">{{ l.situacao }}</td>
                                            <td class="p-2 text-slate-700">{{ l.descricao }}</td>
                                            <td class="p-2 font-semibold text-indigo-900">{{ l.versiculos }}</td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                            {% endif %}
                        </div>
                        {% endfor %}
                    </div>

                    <!-- PROVÉRBIO CHAVE / CONCLUSÃO -->
                    {% if licao.conteudo_completo.proverbio_chave %}
                    <div class="bg-gradient-to-r from-indigo-900 to-indigo-950 text-white p-4 rounded-2xl border border-indigo-800 text-xs text-center font-bold">
                        📖 {{ licao.conteudo_completo.proverbio_chave }}
                    </div>
                    {% endif %}

                    <!-- ETAPA 2: RESUMO OBRIGATÓRIO DO ALUNO -->
                    <div class="pt-6 border-t-2 border-slate-100 space-y-4">
                        <div class="flex items-center justify-between">
                            <div>
                                <span class="text-xs font-black uppercase text-amber-600 tracking-wider">
                                    ETAPA 2: RESUMO REFLEXIVO DO ALUNO
                                </span>
                                <h3 class="text-base font-extrabold text-slate-900 mt-0.5">
                                    O Que Você Aprendeu Nesta Lição?
                                </h3>
                                <p class="text-xs text-slate-500">Escreva com as suas próprias palavras. O teste só será destravado após submeter o resumo.</p>
                            </div>
                            {% if progresso_atual.resumo %}
                            <span class="bg-emerald-100 text-emerald-800 px-3 py-1 rounded-full text-xs font-black">
                                ✅ Resumo Entregue
                            </span>
                            {% endif %}
                        </div>

                        {% if progresso_atual.resumo %}
                        <div class="p-4 bg-emerald-50/70 border border-emerald-200 rounded-2xl text-xs text-emerald-950 space-y-1">
                            <span class="font-extrabold block text-emerald-800">Seu Resumo Gravado:</span>
                            <p class="italic">"{{ progresso_atual.resumo }}"</p>
                        </div>
                        {% else %}
                        <form action="/ensino/submeter_resumo" method="POST" class="space-y-3 text-xs">
                            <input type="hidden" name="licao_id" value="{{ licao.id }}">
                            <textarea name="resumo" required rows="4" placeholder="Escreva aqui detalhadamente o que compreendeu dos pontos doutrinários acima..." class="w-full p-4 border-2 border-slate-200 rounded-2xl bg-slate-50 focus:bg-white focus:border-indigo-600 focus:outline-none font-medium leading-relaxed"></textarea>
                            <button type="submit" class="w-full py-3.5 bg-amber-600 hover:bg-amber-700 text-white font-black rounded-xl shadow cursor-pointer text-xs transition">
                                ✍️ Submeter Resumo & Desbloquear o Teste de Fixação
                            </button>
                        </form>
                        {% endif %}
                    </div>

                    <!-- ETAPA 3: TESTE DE FIXAÇÃO -->
                    <div id="teste" class="pt-6 border-t-2 border-slate-100 space-y-4">
                        <span class="text-xs font-black uppercase text-indigo-600 tracking-wider block">
                            ETAPA 3: TESTE DE FIXAÇÃO TEOLÓGICA (MÍNIMO 70%)
                        </span>

                        {% if not progresso_atual.resumo %}
                        <div class="bg-slate-100 border-2 border-dashed border-slate-300 p-8 rounded-2xl text-center space-y-2">
                            <span class="text-3xl">🔒</span>
                            <h4 class="font-bold text-sm text-slate-700">Teste Bloqueado</h4>
                            <p class="text-xs text-slate-500 max-w-md mx-auto">
                                Para ter acesso a este teste, complete o estudo aprofundado da lição acima e <b>submeta o seu resumo na Etapa 2</b>.
                            </p>
                        </div>
                        {% else %}
                        <form action="/ensino/submeter_teste" method="POST" class="space-y-4 text-xs">
                            <input type="hidden" name="licao_id" value="{{ licao.id }}">

                            {% for q in licao.questoes %}
                            <div class="bg-slate-50 p-5 rounded-2xl border border-slate-200 space-y-3">
                                <p class="font-extrabold text-sm text-slate-800">
                                    {{ loop.index }}. {{ q.p }}
                                </p>
                                <div class="space-y-2">
                                    {% for op in q.ops %}
                                    <label class="flex items-center gap-3 p-3 bg-white rounded-xl border border-slate-200 cursor-pointer hover:bg-indigo-50/50 transition">
                                        <input type="radio" name="q_{{ loop.parent.loop.index0 }}" value="{{ loop.index0 }}" required class="w-4 h-4 text-indigo-600">
                                        <span class="text-slate-700 font-medium">{{ op }}</span>
                                    </label>
                                    {% endfor %}
                                </div>
                            </div>
                            {% endfor %}

                            <button type="submit" class="w-full py-4 bg-indigo-900 hover:bg-indigo-950 text-white font-black rounded-2xl shadow-lg cursor-pointer text-sm transition">
                                🎯 Submeter Teste de Fixação
                            </button>
                        </form>
                        {% endif %}
                    </div>

                    <!-- ESPAÇO TIRA-DÚVIDAS INTEGRADO COM O PROFESSOR -->
                    <div id="duvidas" class="pt-6 border-t-2 border-slate-100 space-y-4">
                        <div class="flex items-center justify-between">
                            <h4 class="font-extrabold text-sm text-slate-900 flex items-center gap-2">
                                <span>💬</span> Espaço Tira-Dúvidas com o Professor ({{ aluno.professor or "Pastor" }})
                            </h4>
                            <span class="text-[10px] text-slate-400">Resposta bíblica imediata e acompanhamento pastoral</span>
                        </div>

                        <form action="/ensino/duvida" method="POST" class="space-y-2 text-xs">
                            <input type="hidden" name="licao_id" value="{{ licao.id }}">
                            <div class="flex gap-2">
                                <input type="text" name="pergunta" required placeholder="Tem alguma dúvida bíblica sobre os pontos desta lição? Pergunte aqui..." class="flex-1 h-11 px-3 border-2 border-slate-200 rounded-xl bg-slate-50 focus:bg-white focus:border-indigo-600 focus:outline-none">
                                <button type="submit" class="px-5 h-11 bg-slate-800 hover:bg-slate-900 text-white font-bold rounded-xl shadow cursor-pointer">
                                    Perguntar
                                </button>
                            </div>
                        </form>

                        <div class="space-y-2.5">
                            {% for d in duvidas %}
                            <div class="p-3.5 bg-slate-50 rounded-xl text-xs space-y-1.5 border border-slate-200">
                                <div class="font-bold text-slate-800 flex justify-between">
                                    <span>❓ Sua Pergunta: "{{ d.pergunta }}"</span>
                                    <span class="text-[10px] text-slate-400">{{ d.criado_em }}</span>
                                </div>
                                {% if d.resposta_professor %}
                                <div class="p-2.5 bg-emerald-50 border border-emerald-300 rounded-lg text-emerald-950 text-[11px] leading-relaxed">
                                    <b class="text-emerald-800 block">👨‍🏫 Resposta do seu Professor ({{ d.professor_nome or aluno.professor or 'Pastor' }}):</b>
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
                            {% else %}
                            <p class="text-[11px] text-slate-400 italic text-center py-2">Nenhuma dúvida enviada sobre esta lição ainda.</p>
                            {% endfor %}
                        </div>
                    </div>

                </div>
            </div>

        </div>

    </main>
</body>
</html>
"""

env.parse(portal_html_integral)
with open(os.path.join('templates', 'portal_aluno.html'), 'w', encoding='utf-8') as f:
    f.write(portal_html_integral)
print("✓ templates/portal_aluno.html: Conteúdo integral e profundo do manual instalado!")

print("=" * 80)
print(">>> INSTALAÇÃO CONCLUÍDA COM TOTAL SUCESSO! <<<")
print("=" * 80)