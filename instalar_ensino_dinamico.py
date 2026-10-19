import os

print("=" * 80)
print("A INSTALAR O NOVO PORTAL DINÂMICO DE ENSINO (MANUAL IEADAO)...")
print("=" * 80)

os.makedirs('templates', exist_ok=True)

# =============================================================================
# 1. ATUALIZAR APP.PY COM MOTOR PEDAGÓGICO, QUIZZES E TIRA-DÚVIDAS INTELIGENTE
# =============================================================================
app_code = '''import os
import sqlite3
import json
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

# -------------------------------------------------------------
# MIGRAÇÕES E ESTRUTURA DO BANCO
# -------------------------------------------------------------
def sincronizar_banco():
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
        f"""CREATE TABLE IF NOT EXISTS testes_realizados (
            id {pk}, aluno_id INT, licao_id TEXT, nota_percentual REAL, criado_em TEXT
        );""",
        f"""CREATE TABLE IF NOT EXISTS duvidas_alunos (
            id {pk}, aluno_id INT, licao_id TEXT, pergunta TEXT, resposta_sistema TEXT, resposta_pastor TEXT, criado_em TEXT
        );"""
    ]
    for sql in tabelas:
        try:
            cur.execute(sql)
            if hasattr(conn, 'commit'): conn.commit()
        except: pass

    if not is_pg:
        # Sincronizar membros
        cur.execute("PRAGMA table_info(membros);")
        cols_m = [c[1].lower() for c in cur.fetchall()]
        cols_membros = [
            ('nome', 'TEXT'), ('contacto', 'TEXT'), ('bi', 'TEXT'), ('cargo', 'TEXT'),
            ('departamento', 'TEXT'), ('estado_civil', 'TEXT'), ('zona', 'TEXT'),
            ('celula', 'TEXT'), ('ano_conversao', 'TEXT'), ('data_batismo', 'TEXT'),
            ('local_residencia', 'TEXT'), ('bairro', 'TEXT'), ('criado_em', 'TEXT')
        ]
        for col, tipo in cols_membros:
            if col not in cols_m:
                cur.execute(f"ALTER TABLE membros ADD COLUMN {col} {tipo};")

        # Sincronizar doutrina
        cur.execute("PRAGMA table_info(doutrina);")
        cols_d = [c[1].lower() for c in cur.fetchall()]
        cols_doutrina = [
            ('nome_aluno', 'TEXT'), ('classe', 'TEXT'), ('professor', 'TEXT'),
            ('licao_atual', 'TEXT'), ('data_inicio', 'TEXT'), ('presencas', 'INT DEFAULT 0'),
            ('situacao', 'TEXT DEFAULT "Em Formação"'), ('usuario', 'TEXT'),
            ('senha', 'TEXT'), ('aproveitamento', 'REAL DEFAULT 0'), ('criado_em', 'TEXT')
        ]
        for col, tipo in cols_doutrina:
            if col not in cols_d:
                cur.execute(f"ALTER TABLE doutrina ADD COLUMN {col} {tipo};")

        # Sincronizar cultos
        cur.execute("PRAGMA table_info(cultos);")
        cols_c = [c[1].lower() for c in cur.fetchall()]
        for col in ['tipo_culto', 'homens_adultos', 'mulheres_adultas', 'jovens_rapazes', 'jovens_mocas', 'criancas_meninos', 'criancas_meninas', 'visitantes_homens', 'visitantes_mulheres', 'apelos', 'total_presentes', 'pregador', 'tema_mensagem', 'criado_em']:
            if col not in cols_c:
                cur.execute(f"ALTER TABLE cultos ADD COLUMN {col} TEXT;")

        # Sincronizar caixa
        cur.execute("PRAGMA table_info(caixa);")
        cols_cx = [c[1].lower() for c in cur.fetchall()]
        for col in ['tipo', 'categoria', 'descricao', 'data_movimento', 'criado_em']:
            if col not in cols_cx:
                cur.execute(f"ALTER TABLE caixa ADD COLUMN {col} TEXT;")

        if hasattr(conn, 'commit'): conn.commit()
    conn.close()

sincronizar_banco()

# -------------------------------------------------------------
# BASE DE DADOS DOUTRINÁRIA (CONFORME O MANUAL DA IEADAO)
# -------------------------------------------------------------
LICOES_MANUAL = {
    'licao_1': {
        'id': 'licao_1',
        'numero': 'Lição 1',
        'titulo': 'O Pecado e o Perdão',
        'classe': 'Classe I - Primeiros Passos',
        'texto_aureo': 'Porque o salário do pecado é a morte, mas o dom gratuito de Deus é a vida eterna, por Cristo Jesus nosso Senhor. (Rm 6:23)',
        'leitura_base': 'Rm 3:23; Is 59:2; 1Jo 1:7-9; Pv 28:13',
        'conteudo_didatico': [
            {
                'subtitulo': '1. A Natureza do Pecado: Errar o Alvo',
                'texto': 'Pecar significa literalmente "Errar o Alvo", ou seja, errar o alvo de fazer a Santa Vontade de Deus e transgredir a Sua Lei Moral. A Bíblia ensina uma distinção essencial: a Desobediência é a causa oculta no coração, enquanto a Transgressão é o efeito manifesto e exposto nas atitudes exteriores.',
                'destaque': 'Desobedecer é a causa invisível; Transgredir é o efeito visível.'
            },
            {
                'subtitulo': '2. A Condição Humana Diante do Pecado',
                'texto': 'O pecado afeta o homem em três dimensões graves: 1) Imoralidade (desfiguração da imagem divina, Rm 3:9-12); 2) Inimizade (separação espiritual de Deus, Is 59:2); 3) Morte (separação definitiva e condenação eterna, Rm 6:23a).'
            },
            {
                'subtitulo': '3. O Perdão Divino: Expiação e Propiciação',
                'texto': 'Não há perdão sem derramamento de sangue (Hb 9:22). Na cruz, Cristo expiou as consequências do pecado e ofereceu propiciação, aplacando o preço justo da ira divina. O perdão de Deus opera uma substituição soberana: Cristo não apenas retira o mal (a condenação), mas deposita em nós o bem (Amor, Graça, Paz e Gozo).'
            }
        ],
        'questoes_teste': [
            {
                'id': 1,
                'pergunta': 'De acordo com o Manual da IEADAO, qual é a diferença entre desobedecer e transgredir?',
                'opcoes': [
                    'Transgredir é a causa no coração e desobedecer é a consequência física.',
                    'Desobedecer é a causa oculta no coração e transgredir é o efeito exposto.',
                    'São sinónimos exatos e não possuem qualquer diferença doutrinária.',
                    'Desobedecer só se aplica a crianças e transgredir a membros batizados.'
                ],
                'correta': 1,
                'explicacao': 'Conforme o Manual da IEADAO (Lição 1): "Desobedecer é a causa e Transgredir o efeito. A desobediência está escondida no coração e a transgressão sempre está exposta."'
            },
            {
                'id': 2,
                'pergunta': 'O que significa biblicamente o conceito teológico de "Expiação"?',
                'opcoes': [
                    'O ato de esquecer os próprios erros sem necessidade de arrependimento.',
                    'O pagamento do preço dos pecados através do sacrifício de uma vítima inocente (Cristo).',
                    'A obrigação do crente de pagar penitências e fazer votos para ser salvo.',
                    'Uma cerimónia litúrgica reservada apenas para o dia do batismo nas águas.'
                ],
                'correta': 1,
                'explicacao': 'Expiação é o perdão dos pecados acompanhado da reconciliação com Deus mediante o sacrifício de uma vítima inocente (Lv 1-7; Hb 9:19-28).'
            },
            {
                'id': 3,
                'pergunta': 'Segundo Provérbios 28:13 citado na lição, quem alcançará misericórdia?',
                'opcoes': [
                    'Aquele que oculta suas faltas para manter um bom testemunho social.',
                    'Aquele que confessa as suas transgressões e as abandona.',
                    'Apenas quem nunca cometeu falhas após a conversão.',
                    'Aquele que cumpre os rituais tradicionais da congregação.'
                ],
                'correta': 1,
                'explicacao': 'Provérbios 28:13: "O que encobre as suas transgressões nunca prosperará; mas o que as confessa e deixa, alcançará misericórdia."'
            }
        ]
    },
    'licao_2': {
        'id': 'licao_2',
        'numero': 'Lição 2',
        'titulo': 'Salvação e Senhorio de Cristo',
        'classe': 'Classe I - Primeiros Passos',
        'texto_aureo': 'Assim que, se alguém está em Cristo, nova criatura é; as coisas velhas já passaram; eis que tudo se fez novo. (2Co 5:17)',
        'leitura_base': 'Ef 2:8-10; Jo 1:12; Cl 1:21-22; Jo 13:13',
        'conteudo_didatico': [
            {
                'subtitulo': '1. Salvação Pela Graça e Fé, Não Por Obras',
                'texto': 'A salvação é um dom soberano e gracioso de Deus (Ef 2:8-9). As boas obras não são a raiz ou a causa da salvação, mas sim o seu fruto inseparável e consequência viva (Ef 2:10).',
                'destaque': 'As obras não geram a salvação; a salvação gera as boas obras!'
            },
            {
                'subtitulo': '2. Os Dois Tronos do Coração Humano',
                'texto': 'O manual ilustra a vida do crente através de dois centros de comando: 1) O "EU" Entronizado: o ego domina, resultando em discórdias, instabilidade e carnalidade; 2) CRISTO Entronizado: Jesus assume o comando como Senhor, resultando em equilíbrio, paz e santidade (1Co 8:6).'
            }
        ],
        'questoes_teste': [
            {
                'id': 1,
                'pergunta': 'Segundo Efésios 2:8-10, qual é o papel exato das obras na salvação cristã?',
                'opcoes': [
                    'As obras são necessárias para comprar a salvação perante a justiça de Deus.',
                    'As obras não salvam, mas acompanham a salvação como seu fruto natural.',
                    'O crente não necessita de praticar obras depois que aceita a fé.',
                    'Apenas as ofertas e dízimos contam como obras de salvação.'
                ],
                'correta': 1,
                'explicacao': 'Somos salvos pela graça por meio da fé, e as boas obras são o resultado preparado por Deus para andarmos nelas (Ef 2:8-10).'
            },
            {
                'id': 2,
                'pergunta': 'O que ensina a doutrina do "Senhorio de Cristo"?',
                'opcoes': [
                    'Cristo é apenas um protetor que não interfere nas nossas decisões.',
                    'Cristo não quer apenas salvar a alma da condenação, mas dominar e reger toda a vida do salvo.',
                    'Ser Senhor aplica-se apenas quando estivermos no Reino Milenar.',
                    'O crente deve colocar o seu "eu" no trono e Cristo ao seu redor.'
                ],
                'correta': 1,
                'explicacao': 'Cristo quer ser Salvador e Senhor. Ele é Senhor (Jo 13:13) e deve dominar as nossas vidas (1Co 8:6).'
            }
        ]
    },
    'licao_5': {
        'id': 'licao_5',
        'numero': 'Lição 5',
        'titulo': 'A Bíblia - O Livro e Manual de Fé dos Cristãos',
        'classe': 'Classe I - Primeiros Passos',
        'texto_aureo': 'Lâmpada para os meus pés é a tua palavra e luz para o meu caminho. (Sl 119:105)',
        'leitura_base': '2Tm 3:16; Sl 1:2; Josué 1:8; 2Pe 1:21',
        'conteudo_didatico': [
            {
                'subtitulo': '1. Origem e Autoria Divina',
                'texto': 'A Bíblia Sagrada foi escrita num período de aproximadamente 1600 anos por cerca de 40 homens inspirados por Deus. O seu Autor soberano é Deus, o seu Intérprete infalível é o Espírito Santo, e o seu Tema Central é a Pessoa de Jesus Cristo.',
                'destaque': 'Autor: Deus | Intérprete: Espírito Santo | Tema Central: Jesus Cristo.'
            },
            {
                'subtitulo': '2. Estrutura Canónica: 66 Livros',
                'texto': 'O cânon bíblico está dividido em duas partes interligadas: Antigo Testamento com 39 livros (Pentateuco, Históricos, Poéticos, Profetas Maiores e Menores) e Novo Testamento com 27 livros (Evangelhos, Histórico, Epístolas Paulinas, Epístolas Gerais e Revelação/Apocalipse).'
            }
        ],
        'questoes_teste': [
            {
                'id': 1,
                'pergunta': 'Quantos livros compõem o Antigo e o Novo Testamento no cânon das Escrituras?',
                'opcoes': [
                    '30 no Antigo e 36 no Novo (total de 66).',
                    '39 no Antigo e 27 no Novo (total de 66 livros).',
                    '46 no Antigo e 27 no Novo (total de 73 livros).',
                    '27 no Antigo e 39 no Novo (total de 66 livros).'
                ],
                'correta': 1,
                'explicacao': 'A Bíblia contém 66 livros: 39 no Antigo Testamento e 27 no Novo Testamento (Manual da IEADAO, pág. 16).'
            },
            {
                'id': 2,
                'pergunta': 'Qual é o Tema Principal de toda a Bíblia Sagrada?',
                'opcoes': [
                    'A história política e social do povo de Israel.',
                    'A pessoa e obra salvífica do Senhor Jesus Cristo.',
                    'Os rituais de sacerdócio descritos no livro de Levítico.',
                    'As normas da moralidade civil da antiguidade.'
                ],
                'correta': 1,
                'explicacao': 'O Autor da Bíblia é Deus, o Intérprete é o Espírito Santo e o Tema Central é Jesus Cristo.'
            }
        ]
    },
    'licao_comboio': {
        'id': 'licao_comboio',
        'numero': 'Lição 5 (Classe III)',
        'titulo': 'Fé: Factos, Não Sentimentos',
        'classe': 'Classe III - Maturidade Cristã',
        'texto_aureo': 'Ora, a fé é o firme fundamento das coisas que se esperam e a prova das coisas que não se vêem. (Hb 11:1)',
        'leitura_base': '2Co 5:7; Hb 11:1; 2Tm 3:14-16; Jr 17:9',
        'conteudo_didatico': [
            {
                'subtitulo': '1. A Ilustração Pastoral do Comboio',
                'texto': 'O crente vive por fé e não pela vista. O manual apresenta uma das ilustrações clássicas: 1) A LOCOMOTIVA é o FACTO (Deus e as Promessas infalíveis da Sua Palavra); 2) O CARRO DE LIGAÇÃO é a FÉ (nossa confiança absoluta no que Deus disse); 3) O VAGÃO TRASEIRO são os SENTIMENTOS (as emoções decorrentes).',
                'destaque': 'O comboio anda com ou sem o vagão. Nunca tente puxar o comboio pelo vagão das emoções!'
            },
            {
                'subtitulo': '2. Emoções São Oscilantes, a Palavra é Eterna',
                'texto': 'O nosso coração humano é por vezes enganoso (Jr 17:9). O crente maduro não avalia a presença de Deus ou o perdão dos seus pecados pelo que "sente", mas pela fidelidade do que "Deus prometeu" (Js 23:14).'
            }
        ],
        'questoes_teste': [
            {
                'id': 1,
                'pergunta': 'Na clássica ilustração do comboio da fé, o que representa a Locomotiva?',
                'opcoes': [
                    'Os sentimentos de alegria do crente.',
                    'O Facto soberano de Deus e as promessas da Sua Palavra.',
                    'A nossa capacidade humana de orar muito.',
                    'A opinião pública das pessoas ao redor.'
                ],
                'correta': 1,
                'explicacao': 'A Locomotiva representa o FACTO (Deus e a Sua Palavra), que traciona a fé independentemente das emoções passageiras.'
            }
        ]
    },
    'licao_ceia': {
        'id': 'licao_ceia',
        'numero': 'Lição 1 (Classe IV)',
        'titulo': 'Baptismo nas Águas e Ceia do Senhor',
        'classe': 'Classe IV - Candidatos ao Baptismo',
        'texto_aureo': 'De sorte que foram baptizados os que de bom grado receberam a sua palavra. (At 2:41)',
        'leitura_base': 'Rm 6:4-11; 1Co 11:23-29; Mt 28:19; Tt 3:5',
        'conteudo_didatico': [
            {
                'subtitulo': '1. O Significado Espiritual do Baptismo nas Águas',
                'texto': 'O baptismo nas águas por imersão é um mandamento de Jesus para todo o regenerado. Simboliza a morte e sepultamento para o pecado e a ressurreição triunfal para uma nova vida com Cristo (Rm 6:4).'
            },
            {
                'subtitulo': '2. As Três Dimensões Temporais da Ceia do Senhor',
                'texto': 'A Ceia é um memorial solene com 3 olhares obrigatórios: 1) PASSADO (Comemorativa): "Fazei isto em memória de mim", relembrando o sacrifício na cruz (1Co 11:24); 2) PRESENTE (Instrutiva): "Examine-se o homem a si mesmo", tempo de reconciliação, discernimento e santificação (1Co 11:28); 3) FUTURO (Inspiradora): "Até que Ele venha", consolando-nos com a certeza do Arrebatamento (1Co 11:26).',
                'destaque': 'Passado: Comemora a Morte | Presente: Examina a Conduta | Futuro: Anuncia a Volta!'
            }
        ],
        'questoes_teste': [
            {
                'id': 1,
                'pergunta': 'Quais são as três lembranças sagradas da Ceia do Senhor segundo o Manual?',
                'opcoes': [
                    'Lembrança da infância, da igreja e dos antepassados.',
                    'Passado (Comemorativa), Presente (Instrutiva) e Futuro (Inspiradora).',
                    'Dízimos, ofertas alçadas e campanhas missionárias.',
                    'A criação do mundo, a arca de Noé e o templo de Salomão.'
                ],
                'correta': 1,
                'explicacao': 'Conforme o Manual da IEADAO (pág. 42), a Ceia recorda o Passado (Cruz), o Presente (Autoexame) e o Futuro (A Vinda do Senhor).'
            }
        ]
    }
}

# -------------------------------------------------------------
# ROTAS DO PORTAL DO ALUNO, TESTES E TIRA-DÚVIDAS INTELIGENTE
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
            erro = "Credenciais inválidas! Solicite o seu usuário e senha ao professor ou à secretaria."
    return render_template('aluno_login.html', erro=erro)

@app.route('/ensino/logout')
def aluno_logout():
    session.pop('aluno_id', None)
    session.pop('aluno_nome', None)
    return redirect('/ensino/login')

@app.route('/ensino/aulas')
def aluno_aulas():
    aluno_id = session.get('aluno_id')
    if not aluno_id: return redirect('/ensino/login')

    m = "%s" if DATABASE_URL else "?"
    aluno = consultar_um(f"SELECT * FROM doutrina WHERE id = {m}", (aluno_id,))
    if not aluno: return redirect('/ensino/logout')

    licao_selecionada_id = request.args.get('licao', 'licao_1')
    if licao_selecionada_id not in LICOES_MANUAL:
        licao_selecionada_id = 'licao_1'
    
    licao_ativa = LICOES_MANUAL[licao_selecionada_id]

    # Consultar histórico de dúvidas deste aluno na lição
    duvidas = consultar_todos(f"SELECT * FROM duvidas_alunos WHERE aluno_id = {m} AND licao_id = {m} ORDER BY id DESC", (aluno_id, licao_selecionada_id))

    # Consultar último teste desta lição
    teste_recente = consultar_um(f"SELECT * FROM testes_realizados WHERE aluno_id = {m} AND licao_id = {m} ORDER BY id DESC", (aluno_id, licao_selecionada_id))

    return render_template('portal_aluno.html', aluno=aluno, licao=licao_ativa, todas_licoes=LICOES_MANUAL, duvidas=duvidas, teste_recente=teste_recente)

# Submeter Teste da Lição e Recalcular Aproveitamento
@app.route('/ensino/submeter_teste', methods=['POST'])
def aluno_submeter_teste():
    aluno_id = session.get('aluno_id')
    if not aluno_id: return redirect('/ensino/login')

    licao_id = request.form.get('licao_id')
    if licao_id not in LICOES_MANUAL:
        return redirect('/ensino/aulas')

    licao = LICOES_MANUAL[licao_id]
    questoes = licao['questoes_teste']
    total_q = len(questoes)
    acertos = 0

    for q in questoes:
        resposta_usuario = request.form.get(f"q_{q['id']}")
        if resposta_usuario is not None and int(resposta_usuario) == q['correta']:
            acertos += 1

    nota_percentual = round((acertos / total_q) * 100.0, 1) if total_q > 0 else 0.0

    m = "%s" if DATABASE_URL else "?"
    # Gravar tentativa de teste
    sql_teste = f"""INSERT INTO testes_realizados (aluno_id, licao_id, nota_percentual, criado_em)
                    VALUES ({m}, {m}, {m}, {m})"""
    executar_comando(sql_teste, (aluno_id, licao_id, nota_percentual, datetime.now().strftime('%Y-%m-%d %H:%M')))

    # Recalcular média global do aluno a partir de todos os testes efetuados
    todos_testes = consultar_todos(f"SELECT nota_percentual FROM testes_realizados WHERE aluno_id = {m}", (aluno_id,))
    if todos_testes:
        media_geral = round(sum([float(t['nota_percentual']) for t in todos_testes]) / len(todos_testes), 1)
    else:
        media_geral = nota_percentual

    situacao = 'Apto para o Batismo / Avanço' if media_geral >= 70.0 else 'Em Formação'

    sql_up = f"UPDATE doutrina SET aproveitamento = {m}, situacao = {m} WHERE id = {m}"
    executar_comando(sql_up, (media_geral, situacao, aluno_id))

    return redirect(f"/ensino/aulas?licao={licao_id}&msg_teste=1")

# Espaço de Dúvidas: Resposta Automática Inteligente Teológica + Registo Pastoral
@app.route('/ensino/duvida', methods=['POST'])
def aluno_enviar_duvida():
    aluno_id = session.get('aluno_id')
    if not aluno_id: return redirect('/ensino/login')

    licao_id = request.form.get('licao_id', 'licao_1')
    pergunta = request.form.get('pergunta', '').strip()

    if not pergunta:
        return redirect(f"/ensino/aulas?licao={licao_id}")

    # Motor de Resposta Teológica do Sistema Baseado no Manual da IEADAO
    p_lower = pergunta.lower()
    resposta_sistema = "Paz do Senhor! A sua dúvida foi registada com sucesso na secretaria da IEAD Chicuque. O seu pastor ou instrutor também receberá esta notificação para orientação personalizada."

    if 'expiação' in p_lower or 'expiar' in p_lower:
        resposta_sistema = "Conforme o Manual da IEADAO (Lição 1): Expiação é o perdão dos pecados daqueles que se arrependem e os confessam, acompanhado de reconciliação com Deus através do sacrifício de uma vítima inocente (Cristo Jesus, conforme Hb 9:19-28)."
    elif 'diferença' in p_lower and ('desobediência' in p_lower or 'transgressão' in p_lower):
        resposta_sistema = "Segundo o Manual: Desobedecer é a causa (está escondida no coração) e Transgredir é o efeito manifesto (que está exposto aos olhos dos homens)."
    elif 'sentimento' in p_lower or 'sentir' in p_lower or 'emoção' in p_lower:
        resposta_sistema = "Na doutrina de 'Factos, não Sentimentos' (Classe III), o crente vive pela fé nas Promessas de Deus (A Locomotiva/Facto). Os sentimentos são apenas o vagão traseiro. O comboio anda pela Palavra de Deus, mesmo quando as nossas emoções oscilam."
    elif 'ceia' in p_lower:
        resposta_sistema = "A Ceia do Senhor contempla 3 lembranças solenes: 1) Passado Comemorativo (a cruz); 2) Presente Instrutivo (o autoexame de comunhão e perdão); 3) Futuro Inspirador (a promessa do Arrebatamento até que Ele venha)."
    elif 'dízimo' in p_lower or 'oferta' in p_lower:
        resposta_sistema = "De acordo com o Manual (Lição 5): O dízimo (a décima parte) representa a devolução voluntária e obediente do que pertence ao Senhor. Não é um favor, mas fidelidade espiritual com base em Ml 3:10 e Mt 23:23."
    elif 'batismo' in p_lower:
        resposta_sistema = "O batismo nas águas por imersão é a manifestação pública do novo nascimento. Simboliza a nossa morte e sepultamento para o mundo do pecado e o ressurgimento para uma nova vida espiritual em Deus (Rm 6:4)."

    m = "%s" if DATABASE_URL else "?"
    sql = f"""INSERT INTO duvidas_alunos (aluno_id, licao_id, pergunta, resposta_sistema, criado_em)
              VALUES ({m}, {m}, {m}, {m}, {m})"""
    executar_comando(sql, (aluno_id, licao_id, pergunta, resposta_sistema, datetime.now().strftime('%Y-%m-%d %H:%M')))

    return redirect(f"/ensino/aulas?licao={licao_id}#duvidas")

# -------------------------------------------------------------
# RESTANTE DO SISTEMA (MEMBROS, SECRETARIA, CULTOS, FINANÇAS)
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
              VALUES ({m}, {m}, {m}, 'Lição 1 - O Pecado e o Perdão', {m}, 1, 'Em Formação', {m}, {m}, 0.0, {m})"""
    executar_comando(sql, (aluno, classe, prof, dt, usuario, senha, datetime.now().strftime('%Y-%m-%d %H:%M')))
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

@app.route('/ensino/promover')
def aluno_promover():
    aluno_id = session.get('aluno_id')
    if not aluno_id: return redirect('/ensino/login')
    m = "%s" if DATABASE_URL else "?"
    aluno = consultar_um(f"SELECT * FROM doutrina WHERE id = {m}", (aluno_id,))
    if not aluno: return redirect('/ensino/login')
    
    nota = float(aluno.get('aproveitamento') or 0)
    if nota < 70.0:
        return "<script>alert('Aproveitamento insuficiente! Necessita de no mínimo 70% para avançar de classe.'); window.location.href='/ensino/aulas';</script>"

    classe_atual = aluno.get('classe') or ''
    if 'batismo' in classe_atual.lower():
        nova_classe = 'Discipulado de Novos Convertidos'
    elif 'discipulado' in classe_atual.lower():
        nova_classe = 'Doutrina Bíblica Fundamental'
    elif 'fundamental' in classe_atual.lower():
        nova_classe = 'Formação Ministerial'
    else:
        nova_classe = 'Graduado no Ensino Bíblico'

    sql = f"""UPDATE doutrina SET classe = {m}, licao_atual = 'Módulo 1 da Nova Classe', aproveitamento = 0.0, situacao = 'Em Formação' WHERE id = {m}"""
    executar_comando(sql, (nova_classe, aluno_id))
    return redirect('/ensino/aulas')

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
print("✓ app.py: Motor de testes, tira-dúvidas e lições do manual integrados!")

# =============================================================================
# 2. NOVO PORTAL DO ALUNO DINÂMICO, INTERATIVO E ATRAENTE
# =============================================================================
portal_html = '''<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sala de Aulas - {{ aluno.nome_aluno }}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .gradient-card { background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #312e81 100%); }
    </style>
</head>
<body class="bg-slate-100 text-slate-800 font-sans min-h-screen flex flex-col">

    <!-- CABEÇALHO DO PORTAL DO ALUNO -->
    <header class="bg-slate-900 text-white px-6 py-4 flex justify-between items-center shadow-lg border-b border-indigo-900 sticky top-0 z-50">
        <div class="flex items-center gap-3">
            <div class="w-11 h-11 rounded-2xl bg-gradient-to-tr from-indigo-600 to-amber-500 text-white flex items-center justify-center font-black text-xl shadow-md">
                AD
            </div>
            <div>
                <h1 class="font-extrabold text-sm uppercase tracking-wide">ESCOLA DE DOUTRINA & INTEGRAÇÃO</h1>
                <p class="text-[11px] text-amber-300 font-semibold">IEAD Chicuque • Ministério Thavane</p>
            </div>
        </div>

        <div class="flex items-center gap-4 text-xs">
            <div class="hidden sm:block text-right">
                <span class="text-slate-400 block text-[10px] uppercase font-bold">Formando em Comunhão</span>
                <span class="font-black text-white text-sm">{{ aluno.nome_aluno }}</span>
            </div>
            <a href="/ensino/logout" class="bg-rose-600 hover:bg-rose-700 text-white px-4 py-2 rounded-xl font-bold shadow transition">
                Sair
            </a>
        </div>
    </header>

    <main class="flex-1 max-w-6xl w-full mx-auto p-6 space-y-6">

        <!-- BOAS-VINDAS & PAINEL DE METAS 70% -->
        <div class="gradient-card text-white p-6 sm:p-8 rounded-3xl shadow-2xl relative overflow-hidden">
            <div class="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
                <div class="space-y-2">
                    <div class="inline-flex items-center gap-2 bg-amber-400/20 text-amber-300 border border-amber-300/30 px-3 py-1 rounded-full text-[11px] font-black uppercase">
                        <span>✨</span> {{ aluno.classe }}
                    </div>
                    <h2 class="text-2xl sm:text-3xl font-black tracking-tight">
                        A Paz do Senhor, {{ aluno.nome_aluno }}!
                    </h2>
                    <p class="text-xs sm:text-sm text-indigo-200 max-w-2xl leading-relaxed">
                        Bem-vindo(a) à sua sala virtual de estudos. Todas as lições e testes são baseados no <b>Manual Oficial de Candidatos e Integração da IEADAO</b>. Estude cada módulo, faça o teste de fixação e submeta as suas dúvidas bíblicas.
                    </p>
                </div>

                <!-- CARD DE APROVEITAMENTO CIRCULAR / KPI -->
                {% set nota = aluno.aproveitamento or 0.0 %}
                <div class="bg-white/10 backdrop-blur-md border border-white/20 p-5 rounded-3xl text-center shrink-0 w-full lg:w-64">
                    <span class="text-[10px] uppercase tracking-wider font-extrabold text-indigo-200 block">Seu Aproveitamento</span>
                    <div class="text-4xl font-black mt-1 {% if nota >= 70.0 %}text-emerald-400{% else %}text-amber-400{% endif %}">
                        {{ "%.1f"|format(nota) }}%
                    </div>
                    
                    <div class="w-full bg-slate-900/60 h-2.5 rounded-full overflow-hidden my-3 border border-white/10">
                        <div class="{% if nota >= 70.0 %}bg-emerald-400{% else %}bg-amber-400{% endif %} h-full rounded-full transition-all duration-700" style="width: {{ [nota, 100]|min }}%"></div>
                    </div>

                    {% if nota >= 70.0 %}
                    <span class="text-[11px] font-bold text-emerald-300 block">✅ Meta Atingida (≥70%)</span>
                    <a href="/ensino/promover" onclick="return confirm('Promover para a próxima classe curricular?')" class="mt-2 block w-full py-2 bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-black rounded-xl text-xs shadow transition">
                        🎓 Subir de Classe
                    </a>
                    {% else %}
                    <span class="text-[10px] text-amber-200 block">Meta: 70% • Faltam {{ "%.1f"|format(70.0 - nota) }}%</span>
                    {% endif %}
                </div>
            </div>
        </div>

        <!-- SELETOR DINÂMICO DE LIÇÕES DO MANUAL -->
        <div class="bg-white p-4 rounded-2xl shadow-sm border border-slate-200 flex flex-wrap gap-2 items-center justify-between">
            <span class="text-xs font-bold uppercase text-slate-500 px-2">Lições do Manual:</span>
            <div class="flex flex-wrap gap-2">
                {% for k, lic in todas_licoes.items() %}
                <a href="/ensino/aulas?licao={{ k }}" class="px-3.5 py-2 rounded-xl text-xs font-bold transition flex items-center gap-2 {% if licao.id == k %}bg-indigo-600 text-white shadow-md{% else %}bg-slate-100 text-slate-700 hover:bg-slate-200{% endif %}">
                    <span>📖</span>
                    <span>{{ lic.numero }}: {{ lic.titulo }}</span>
                </a>
                {% endfor %}
            </div>
        </div>

        <!-- CORPO DA LIÇÃO ATIVA -->
        <div class="bg-white rounded-3xl shadow-sm border border-slate-200 p-6 sm:p-8 space-y-6">
            
            <!-- TOPO DA LIÇÃO -->
            <div class="border-b border-slate-100 pb-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <span class="text-[11px] font-extrabold uppercase text-indigo-600 tracking-wider">{{ licao.classe }} • {{ licao.numero }}</span>
                    <h3 class="text-2xl font-black text-slate-900 mt-1">{{ licao.titulo }}</h3>
                    <p class="text-xs text-slate-500 mt-0.5">Leitura Bíblica de Apoio: <b>{{ licao.leitura_base }}</b></p>
                </div>
                <div class="bg-indigo-50 border border-indigo-200 p-4 rounded-2xl max-w-md">
                    <span class="text-[10px] font-black uppercase text-indigo-900 block mb-1">🔥 Texto Áureo da Lição</span>
                    <p class="text-xs italic text-indigo-950 font-serif leading-relaxed">"{{ licao.texto_aureo }}"</p>
                </div>
            </div>

            <!-- BLOCOS PEDAGÓGICOS EXPLICATIVOS -->
            <div class="space-y-5">
                {% for bloco in licao.conteudo_didatico %}
                <div class="bg-slate-50 border border-slate-200 p-5 rounded-2xl space-y-2">
                    <h4 class="text-base font-extrabold text-slate-800">{{ bloco.subtitulo }}</h4>
                    <p class="text-xs text-slate-600 leading-relaxed text-justify">{{ bloco.texto }}</p>
                    {% if bloco.destaque %}
                    <div class="p-3 bg-white border-l-4 border-amber-500 rounded-r-xl text-xs font-bold text-slate-800 shadow-sm mt-2">
                        💡 Princípio Fundamental: {{ bloco.destaque }}
                    </div>
                    {% endif %}
                </div>
                {% endfor %}
            </div>

            <!-- ILUSTRAÇÕES DOUTRINÁRIAS DO MANUAL EM HTML/CSS -->
            {% if licao.id == 'licao_1' %}
            <div class="bg-gradient-to-r from-slate-900 to-indigo-950 text-white p-6 rounded-2xl shadow-inner border border-slate-700">
                <div class="text-center font-bold text-xs uppercase tracking-wider text-amber-300 mb-4">Esquema Bíblico: O Homem Condenado vs Homem Perdoado (1Jo 1:7)</div>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-center items-center">
                    <div class="bg-white/10 p-4 rounded-xl border border-white/10">
                        <span class="text-2xl">⛓️</span>
                        <div class="font-extrabold text-sm mt-1 text-rose-300">HOMEM CONDENADO</div>
                        <p class="text-[11px] text-slate-300 mt-1">Incredulidade • Murmuração • Mentira • Culpa</p>
                    </div>
                    <div class="text-amber-400 font-black text-xl flex flex-col items-center">
                        <span class="text-3xl">✝️</span>
                        <span class="text-xs uppercase tracking-widest mt-1">O Sangue de Jesus</span>
                        <span class="text-[10px] text-slate-300">Apaga o pecado</span>
                    </div>
                    <div class="bg-white/10 p-4 rounded-xl border border-white/10">
                        <span class="text-2xl">🕊️</span>
                        <div class="font-extrabold text-sm mt-1 text-emerald-300">HOMEM PERDOADO</div>
                        <p class="text-[11px] text-slate-300 mt-1">Amor • Graça • Paz • Gozo no Espírito</p>
                    </div>
                </div>
            </div>
            {% endif %}

            {% if licao.id == 'licao_comboio' %}
            <div class="bg-amber-50 border-2 border-amber-300 p-6 rounded-2xl shadow-sm text-slate-800">
                <div class="text-center font-extrabold text-xs uppercase tracking-wider text-amber-900 mb-3">O Comboio da Fé (Factos, Não Sentimentos - 2Co 5:7)</div>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-3 text-center">
                    <div class="bg-white p-3 rounded-xl border border-amber-200 shadow-sm">
                        <span class="text-2xl">🚂</span>
                        <div class="font-black text-sm text-indigo-950">1. FACTO (Locomotiva)</div>
                        <p class="text-[11px] text-slate-600 mt-0.5">Deus e a fidelidade da Sua Palavra que nunca falha.</p>
                    </div>
                    <div class="bg-white p-3 rounded-xl border border-amber-200 shadow-sm">
                        <span class="text-2xl">🔗</span>
                        <div class="font-black text-sm text-amber-800">2. FÉ (Ligação)</div>
                        <p class="text-[11px] text-slate-600 mt-0.5">Nossa confiança e obediência incondicional ao Facto.</p>
                    </div>
                    <div class="bg-white p-3 rounded-xl border border-amber-200 shadow-sm">
                        <span class="text-2xl">🚃</span>
                        <div class="font-black text-sm text-slate-600">3. SENTIMENTOS (Vagão)</div>
                        <p class="text-[11px] text-slate-600 mt-0.5">Consequência natural. O comboio anda mesmo sem o vagão.</p>
                    </div>
                </div>
            </div>
            {% endif %}

            <!-- ========================================================= -->
            <!-- TESTE OFICIAL DA LIÇÃO (AVALIAÇÃO INTERATIVA AUTOMÁTICA)   -->
            <!-- ========================================================= -->
            <div id="teste" class="pt-6 border-t-2 border-slate-100">
                <div class="flex items-center justify-between mb-4">
                    <div>
                        <h4 class="text-lg font-black text-slate-900 flex items-center gap-2">
                            <span>📝</span> Teste de Fixação Teológica: {{ licao.titulo }}
                        </h4>
                        <p class="text-xs text-slate-500">Responda a todas as questões para gravar a sua nota curricular no sistema.</p>
                    </div>
                    {% if teste_recente %}
                    <span class="bg-indigo-100 text-indigo-900 px-3 py-1 rounded-full text-xs font-black">
                        Último Resultado: {{ teste_recente.nota_percentual }}%
                    </span>
                    {% endif %}
                </div>

                <form action="/ensino/submeter_teste" method="POST" class="space-y-4 text-xs">
                    <input type="hidden" name="licao_id" value="{{ licao.id }}">

                    {% for q in licao.questoes_teste %}
                    <div class="bg-slate-50 p-5 rounded-2xl border border-slate-200 space-y-3">
                        <p class="font-extrabold text-sm text-slate-800">
                            {{ loop.index }}. {{ q.pergunta }}
                        </p>
                        <div class="space-y-2">
                            {% for op in q.opcoes %}
                            <label class="flex items-center gap-3 p-3 bg-white rounded-xl border border-slate-200 cursor-pointer hover:bg-indigo-50/50 transition">
                                <input type="radio" name="q_{{ q.id }}" value="{{ loop.index0 }}" required class="w-4 h-4 text-indigo-600">
                                <span class="text-slate-700 font-medium">{{ op }}</span>
                            </label>
                            {% endfor %}
                        </div>
                    </div>
                    {% endfor %}

                    <button type="submit" class="w-full py-4 bg-indigo-900 hover:bg-indigo-950 text-white font-black rounded-2xl shadow-lg cursor-pointer text-sm transition">
                        🎯 Submeter Respostas do Teste e Gravar Aproveitamento
                    </button>
                </form>
            </div>

            <!-- ========================================================= -->
            <!-- ESPAÇO DE DÚVIDAS E RESPOSTAS (TIRA-DÚVIDAS INTELIGENTE)  -->
            <!-- ========================================================= -->
            <div id="duvidas" class="pt-8 border-t-2 border-slate-100 space-y-5">
                <div>
                    <h4 class="text-lg font-black text-slate-900 flex items-center gap-2">
                        <span>💬</span> Espaço Tira-Dúvidas com o Pastor & Sistema Bíblico
                    </h4>
                    <p class="text-xs text-slate-500">Tem alguma dúvida sobre esta lição? Escreva abaixo para receber orientação imediata do manual e acompanhamento pastoral.</p>
                </div>

                <!-- FORMULÁRIO DE ENVIO DE DÚVIDA -->
                <form action="/ensino/duvida" method="POST" class="space-y-3 text-xs">
                    <input type="hidden" name="licao_id" value="{{ licao.id }}">
                    <div class="flex gap-3">
                        <input type="text" name="pergunta" required placeholder="Ex: O que significa expiação na prática? / Posso jejuar só meio dia?" class="flex-1 h-12 px-4 border-2 border-slate-200 rounded-2xl bg-slate-50 focus:bg-white focus:border-indigo-600 focus:outline-none font-medium">
                        <button type="submit" class="px-6 h-12 bg-amber-600 hover:bg-amber-700 text-white font-extrabold rounded-2xl shadow transition cursor-pointer shrink-0">
                            Perguntar
                        </button>
                    </div>
                </form>

                <!-- HISTÓRICO DE PERGUNTAS E RESPOSTAS DO FORMANDO -->
                <div class="space-y-3">
                    {% for d in duvidas %}
                    <div class="p-4 bg-slate-50 rounded-2xl border border-slate-200 text-xs space-y-2">
                        <div class="flex items-center justify-between">
                            <span class="font-bold text-slate-800">❓ Sua Pergunta: "{{ d.pergunta }}"</span>
                            <span class="text-[10px] text-slate-400">{{ d.criado_em }}</span>
                        </div>
                        <div class="p-3 bg-white rounded-xl border border-indigo-100 text-indigo-950 leading-relaxed">
                            <b class="text-indigo-800 block mb-0.5">📖 Orientação Bíblica do Manual:</b>
                            {{ d.resposta_sistema }}
                        </div>
                    </div>
                    {% else %}
                    <p class="text-xs text-slate-400 text-center py-4 italic">Nenhuma dúvida enviada sobre esta lição ainda. Faça uma pergunta acima!</p>
                    {% endfor %}
                </div>
            </div>

        </div>

    </main>

    <footer class="bg-white border-t border-slate-200 py-4 text-center text-xs text-slate-400">
        IEAD Chicuque • Sistema de Ensino e Formação Eclesiástica • Baseado no Manual Oficial da IEADAO
    </footer>
</body>
</html>
'''

with open(os.path.join('templates', 'portal_aluno.html'), 'w', encoding='utf-8') as f:
    f.write(portal_html)

print("✓ templates/portal_aluno.html gerado com sucesso!")
print("=" * 80)
print("INSTALAÇÃO CONCLUÍDA COM TOTAL SUCESSO!")
print("=" * 80)