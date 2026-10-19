import os

print("=" * 80)
print("A APLICAR REGRA RIGOROSA: RESUMO OBRIGATÓRIO, 70% E CERTIFICADO...")
print("=" * 80)

os.makedirs('templates', exist_ok=True)

# =============================================================================
# 1. ATUALIZAR APP.PY COM CONTROLO ESTRITO DE PROGRESSO E EXAME FINAL
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

# Sincronização e tabelas de progresso curricular
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
            id {pk}, aluno_id INT, licao_id TEXT, pergunta TEXT, resposta_sistema TEXT, criado_em TEXT
        );"""
    ]
    for sql in tabelas:
        try:
            cur.execute(sql)
            if hasattr(conn, 'commit'): conn.commit()
        except: pass

    if not is_pg:
        for col, tipo in [('nome', 'TEXT'), ('contacto', 'TEXT'), ('bi', 'TEXT'), ('cargo', 'TEXT'), ('departamento', 'TEXT'), ('estado_civil', 'TEXT'), ('zona', 'TEXT'), ('celula', 'TEXT'), ('ano_conversao', 'TEXT'), ('data_batismo', 'TEXT'), ('local_residencia', 'TEXT'), ('criado_em', 'TEXT')]:
            try: cur.execute(f"ALTER TABLE membros ADD COLUMN {col} {tipo};")
            except: pass
        for col, tipo in [('usuario', 'TEXT'), ('senha', 'TEXT'), ('aproveitamento', 'REAL DEFAULT 0'), ('classe', 'TEXT'), ('situacao', 'TEXT DEFAULT "Em Formação"')]:
            try: cur.execute(f"ALTER TABLE doutrina ADD COLUMN {col} {tipo};")
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
                'id': 'c1_l1',
                'numero': 'Lição 1',
                'titulo': 'O Pecado e o Perdão',
                'texto_aureo': 'Porque o salário do pecado é a morte, mas o dom gratuito de Deus é a vida eterna. (Rm 6:23)',
                'leitura_base': 'Rm 3:23; Is 59:2; 1Jo 1:7-9; Pv 28:13',
                'conteudo': 'Pecar significa literalmente "Errar o Alvo" da Santa Vontade de Deus. Existe uma distinção teológica vital: Desobedecer é a causa (escondida no coração) e Transgredir é o efeito visível (a lei exposta). Na cruz, Cristo operou a Expiação (pagou a consequência pelo sacrifício inocente) e nos deu amor, graça, paz e gozo.',
                'questoes': [
                    {'p': 'Qual é a diferença entre desobedecer e transgredir segundo o Manual?', 'ops': ['Transgredir é no coração e desobedecer é o ato físico.', 'Desobedecer é a causa oculta no coração e transgredir é o efeito exposto.', 'Não há diferença doutrinária.', 'Transgredir só se aplica a pagãos.'], 'c': 1},
                    {'p': 'O que significa Expiação no plano da salvação?', 'ops': ['Perdão mediante o sacrifício de uma vítima inocente (Cristo).', 'Cumprir penitências humanas.', 'Esquecer o erro sem arrependimento.', 'Rito feito apenas no batismo.'], 'c': 0}
                ]
            },
            {
                'id': 'c1_l2',
                'numero': 'Lição 2',
                'titulo': 'Salvação e Senhorio de Cristo',
                'texto_aureo': 'Se alguém está em Cristo, nova criatura é; as coisas velhas já passaram. (2Co 5:17)',
                'leitura_base': 'Ef 2:8-10; Jo 1:12; 1Co 8:6',
                'conteudo': 'Somos salvos pela graça mediante a fé, e não por obras para que ninguém se glorie. As boas obras são o resultado e fruto de estarmos salvos. Cristo quer ser Salvador e dominar como Senhor sobre o trono do nosso coração, substituindo o "eu" desgovernado.',
                'questoes': [
                    {'p': 'Qual é a relação entre fé, obras e salvação em Efésios 2:8-10?', 'ops': ['As obras compram a salvação.', 'Somos salvos pela graça por meio da fé, e as obras acompanham como fruto.', 'O crente salvo não precisa de praticar boas obras.', 'A fé sem moralidade basta.'], 'c': 1},
                    {'p': 'O que significa o Senhorio de Cristo na vida prática?', 'ops': ['Cristo é apenas um protetor nominal.', 'Cristo não quer apenas salvar da condenação, mas dirigir e reinar sobre a nossa conduta.', 'O homem deve manter o ego no trono.', 'Aplica-se apenas aos líderes.'], 'c': 1}
                ]
            },
            {
                'id': 'c1_l3',
                'numero': 'Lição 3',
                'titulo': 'O Testemunho Cristão',
                'texto_aureo': 'Mas recebereis a virtude do Espírito Santo e ser-me-eis testemunhas. (At 1:8)',
                'leitura_base': 'At 1:8; At 4:20; Mt 5:16; 1Pe 3:1',
                'conteudo': 'Um dos maiores propósitos para o qual Deus nos salvou é sermos Suas testemunhas vivas. A verdadeira testemunha fala do que viu, sabe e crê, mas o mundo aprende a lição muito mais observando a nossa prática e conduta diária do que apenas palavras.',
                'questoes': [
                    {'p': 'Segundo a Lição 3, como o mundo aprende melhor a mensagem do Evangelho?', 'ops': ['Apenas por debates intelectuais.', 'Observando o que a testemunha faz e a integridade da sua conduta.', 'Por imposição formal.', 'Através de isolamento social.'], 'c': 1}
                ]
            },
            {
                'id': 'c1_l4',
                'numero': 'Lição 4',
                'titulo': 'A Pessoa de Deus Triuno',
                'texto_aureo': 'Os céus manifestam a glória de Deus e o firmamento anuncia a obra de suas mãos. (Sl 19:1)',
                'leitura_base': 'Dt 6:4; Mt 28:19; Jo 14:16; 2Co 13:13',
                'conteudo': 'Deus é Uno e ao mesmo tempo Triuno: a unidade de Deus é composta. Existe Um Só Deus subsistindo em três pessoas: Deus Pai (divindade invisível planejadora), Deus Filho (divindade manifesta redentora) e Deus Espírito Santo (divindade operando santificação no homem).',
                'questoes': [
                    {'p': 'Como o Manual define a Trindade Divina?', 'ops': ['São três deuses separados.', 'Um Só Deus verdadeiro operando e subsistindo em três Pessoas divinas.', 'Deus é apenas uma força impessoal.', 'Jesus e o Espírito Santo foram criados posteriormente.'], 'c': 1}
                ]
            },
            {
                'id': 'c1_l5',
                'numero': 'Lição 5',
                'titulo': 'A Bíblia - Manual de Fé dos Cristãos',
                'texto_aureo': 'Lâmpada para os meus pés é a tua palavra e luz para o meu caminho. (Sl 119:105)',
                'leitura_base': '2Tm 3:16; Js 1:8; Sl 1:2',
                'conteudo': 'A Bíblia contém 66 livros (39 no Antigo Testamento e 27 no Novo Testamento). Escrita por cerca de 40 homens num período de 1600 anos sob inspiração do Espírito Santo. O Autor é Deus, o Intérprete é o Espírito Santo e o Tema Central é Jesus Cristo.',
                'questoes': [
                    {'p': 'Qual é a divisão exata dos 66 livros da Bíblia?', 'ops': ['40 no AT e 26 no NT.', '39 no Antigo Testamento e 27 no Novo Testamento.', '46 no AT e 27 no NT.', '50 no AT e 16 no NT.'], 'c': 1}
                ]
            }
        ]
    },
    {
        'id_classe': 'classe_2',
        'nome_classe': 'Classe II - Vida Cristã',
        'descricao': 'Disciplina Espiritual, Oração, Jejum, Mordomia e Batalha',
        'licoes': [
            {
                'id': 'c2_l1',
                'numero': 'Lição 1',
                'titulo': 'Oração e Jejum',
                'texto_aureo': 'Servindo a Deus em jejuns e orações, de noite e de dia. (Lc 2:37)',
                'leitura_base': '1Ts 5:17; Is 58:6-7; Mt 6:16-18; Zc 7:5',
                'conteudo': 'Orar é um mandamento e uma necessidade vital. O jejum é a abstinência total ou parcial de alimento para nos humilharmos diante de Deus, tornando o espírito mais sensível. O jejum não deve ser para ostentação, mas acompanhado de obras de amor e reconciliação.',
                'questoes': [
                    {'p': 'Qual é o verdadeiro espírito do jejum segundo Isaías 58?', 'ops': ['Fazer greve de fome para obrigar Deus a atender desejos.', 'Humilhar a carne para que o espírito fique sensível, acompanhado de amor ao próximo.', 'Apenas emagrecer.', 'Exibir piedade diante dos outros irmãos.'], 'c': 1}
                ]
            },
            {
                'id': 'c2_l2',
                'numero': 'Lição 2',
                'titulo': 'A Tentação e Como Vencê-la',
                'texto_aureo': 'Sujeitai-vos a Deus, resisti ao diabo, e ele fugirá de vós. (Tg 4:7)',
                'leitura_base': '1Co 10:13; 2Pe 2:9; Ef 6:13; Tg 1:12-14',
                'conteudo': 'Ser tentado não é pecado; o pecado ocorre ao ceder à tentação. Deus não permite tentações maiores que as nossas forças e com a tentação dá o escape para suportar. A vitória exige sujeição a Deus, exame das amizades e uso da Espada do Espírito (a Palavra).',
                'questoes': [
                    {'p': 'A tentação em si mesma já é pecado?', 'ops': ['Sim, qualquer pensamento tentador já é condenação.', 'Não. Ser tentado não é pecado; o pecado consuma-se quando cedemos e desobedecemos.', 'Só é pecado se for em público.', 'A tentação só atinge quem não ora.'], 'c': 1}
                ]
            },
            {
                'id': 'c2_l3',
                'numero': 'Lição 3',
                'titulo': 'Dízimos e Ofertas Alçadas',
                'texto_aureo': 'Cada um contribua de coração, porque Deus ama ao que dá com alegria. (2Co 9:7)',
                'leitura_base': 'Ml 3:8-11; Lv 27:30; 1Co 16:2; Mt 23:23',
                'conteudo': 'O dízimo (a décima parte) pertence ao Senhor. Não é favor, mas obediência e fidelidade espiritual. As ofertas alçadas são doações voluntárias de gratidão e voto de fé para sustento e avanço da obra de Deus.',
                'questoes': [
                    {'p': 'O que representa o dízimo na visão bíblica da IEADAO?', 'ops': ['Uma taxa humana cobrada pela igreja.', 'A devolução obediente da décima parte que pertence ao Senhor.', 'Uma doação opcional para ricos.', 'Um costume que foi cancelado.'], 'c': 1}
                ]
            }
        ]
    },
    {
        'id_classe': 'classe_3',
        'nome_classe': 'Classe III - Maturidade Cristã',
        'descricao': 'Santificação, Discernimento de Heresias e Firmeza na Fé',
        'licoes': [
            {
                'id': 'c3_l1',
                'numero': 'Lição 1',
                'titulo': 'Santificação da Vida',
                'texto_aureo': 'Sede santos, porque Eu Sou Santo. (1Pe 1:16)',
                'leitura_base': 'Hb 12:14; 1Ts 4:3; 1Co 6:11; Jo 17:17',
                'conteudo': 'Santificação possui duplo aspecto: Negativo (afastados do pecado e do espírito mundano) e Positivo (consagrados a Deus). Opera-se em 3 tempos: Instantânea (no espírito na salvação), Progressiva (na alma no caminhar diário) e Final (no corpo no arrebatamento).',
                'questoes': [
                    {'p': 'Em que dimensões ocorre a santificação progressiva?', 'ops': ['Apenas após a morte física.', 'Na alma (mente, emoções e vontade) à medida que conhecemos o Senhor.', 'Apenas nas vestes exteriores.', 'Não existe processo progressivo.'], 'c': 1}
                ]
            },
            {
                'id': 'c3_l2',
                'numero': 'Lição 5',
                'titulo': 'Fé: Factos, Não Sentimentos',
                'texto_aureo': 'A fé é o firme fundamento das coisas que se esperam. (Hb 11:1)',
                'leitura_base': '2Co 5:7; 2Tm 3:14-16; Jr 17:9',
                'conteudo': 'O crente vive por fé na Palavra e não por sentimentos oscilantes. Na ilustração do comboio da fé: 1) A LOCOMOTIVA é o FACTO (a Palavra de Deus); 2) O CARRO DE LIGAÇÃO é a FÉ (nossa confiança); 3) O VAGÃO são os SENTIMENTOS. O comboio anda pela locomotiva, nunca pelo vagão das emoções.',
                'questoes': [
                    {'p': 'Na analogia do comboio, o que deve conduzir a vida do cristão?', 'ops': ['O vagão das emoções passageiras.', 'A locomotiva dos Factos inabaláveis da Palavra de Deus.', 'Os sentimentos de medo ou incerteza.', 'A aprovação dos homens.'], 'c': 1}
                ]
            }
        ]
    },
    {
        'id_classe': 'classe_4',
        'nome_classe': 'Classe IV - Candidatos ao Baptismo',
        'descricao': 'Ordenanças Sagradas, Membrasia, Disciplina e Escatologia',
        'licoes': [
            {
                'id': 'c4_l1',
                'numero': 'Lição 1',
                'titulo': 'Baptismo nas Águas e Ceia do Senhor',
                'texto_aureo': 'De sorte que foram baptizados os que de bom grado receberam a sua palavra. (At 2:41)',
                'leitura_base': 'Rm 6:4; 1Co 11:23-29; Mt 28:19',
                'conteudo': 'O Baptismo nas águas por imersão é um mandamento e símbolo exterior de que morremos para o pecado e ressuscitámos para Deus. A Ceia do Senhor possui 3 lembranças solenes: Passado Comemorativo (a cruz), Presente Instrutivo (o autoexame) e Futuro Inspirador (a Vinda de Cristo).',
                'questoes': [
                    {'p': 'O que simboliza o acto de descer e sair das águas no baptismo?', 'ops': ['Um mero banho ritualístico de purificação.', 'Sepultamento da velha vida de pecado e ressurreição para uma nova vida com Deus.', 'Uma exigência da lei de Moisés.', 'Apenas a inscrição no livro de membros.'], 'c': 1},
                    {'p': 'Quais são as três dimensões temporais da Ceia do Senhor?', 'ops': ['Infância, mocidade e velhice.', 'Passado (Comemorativo), Presente (Instrutivo) e Futuro (Inspirador da Vinda de Jesus).', 'Terça, quinta e domingo.', 'Criação, dilúvio e juízo.'], 'c': 1}
                ]
            },
            {
                'id': 'c4_l2',
                'numero': 'Lição 6',
                'titulo': 'A Vinda do Senhor e Sinais dos Tempos',
                'texto_aureo': 'Certamente cedo venho. Ámen. (Ap 22:20)',
                'leitura_base': '1Ts 4:16-17; Mt 24:7-14; Ap 22:20',
                'conteudo': 'A esperança gloriosa da Igreja é o Arrebatamento dos salvos, que ocorrerá de forma súbita e inesperada. Os sinais dos tempos comprovam o cumprimento profético: guerras, terramotos, fomes, declínio moral e o ressurgimento da nação de Israel.',
                'questoes': [
                    {'p': 'Como será o Arrebatamento dos salvos segundo 1 Tessalonicenses 4:16-17?', 'ops': ['Um evento lento que durará muitos anos.', 'Súbito e transformador, onde os mortos em Cristo ressuscitarão primeiro e os vivos serão trasladados.', 'Apenas uma alegoria poética.', 'Ocorrerá somente para sacerdotes.'], 'c': 1}
                ]
            }
        ]
    }
]

TODAS_LICOES_ORDENADAS = []
for cl in CURRICULO_CLASSES:
    for lic in cl['licoes']:
        TODAS_LICOES_ORDENADAS.append({**lic, 'id_classe': cl['id_classe'], 'nome_classe': cl['nome_classe']})

MAPA_LICOES = {l['id']: l for l in TODAS_LICOES_ORDENADAS}

# -------------------------------------------------------------
# ROTAS PEDAGÓGICAS DO PORTAL DO ALUNO COM BLOQUEIO RIGOROSO
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

    # Bloqueio sequencial estrito
    licoes_status = {}
    todas_concluidas = True
    bloqueado_a_partir_daqui = False

    for idx, lic in enumerate(TODAS_LICOES_ORDENADAS):
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
        for lic in TODAS_LICOES_ORDENADAS:
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

# 1. Submeter Resumo da Lição (Destrava o Teste)
@app.route('/ensino/submeter_resumo', methods=['POST'])
def aluno_submeter_resumo():
    aluno_id = session.get('aluno_id')
    if not aluno_id: return redirect('/ensino/login')

    licao_id = request.form.get('licao_id')
    resumo = request.form.get('resumo', '').strip()

    if not resumo or len(resumo) < 20:
        return "<script>alert('Por favor, escreva um resumo completo com o que realmente aprendeu (mínimo de 20 caracteres).'); window.history.back();</script>"

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

# 2. Submeter Teste da Lição (Avalia e, se >= 70%, destrava a lição seguinte)
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
        for i, l in enumerate(TODAS_LICOES_ORDENADAS):
            if l['id'] == licao_id and (i + 1) < len(TODAS_LICOES_ORDENADAS):
                proxima_id = TODAS_LICOES_ORDENADAS[i + 1]['id']
                break
        if proxima_id:
            return redirect(f"/ensino/aulas?licao={proxima_id}&sucesso_aprovado=1")
    
    return redirect(f"/ensino/aulas?licao={licao_id}&nota_resultado={nota}")

# 3. Espaço Tira-Dúvidas com o Pastor e Sistema
@app.route('/ensino/duvida', methods=['POST'])
def aluno_duvida():
    aluno_id = session.get('aluno_id')
    if not aluno_id: return redirect('/ensino/login')

    licao_id = request.form.get('licao_id')
    pergunta = request.form.get('pergunta', '').strip()
    if not pergunta: return redirect(f"/ensino/aulas?licao={licao_id}")

    p_lower = pergunta.lower()
    resp_sistema = "A sua questão foi anotada e encaminhada ao Gabinete de Educação Cristã da IEAD Chicuque."
    if 'expiação' in p_lower or 'expiar' in p_lower:
        resp_sistema = "Conforme o Manual da IEADAO (Lição 1): Expiação é o perdão dos pecados daqueles que se arrependem e os confessam, com reconciliação operada pelo sacrifício de Cristo Jesus (Hb 9:19-28)."
    elif 'desobediência' in p_lower or 'transgressão' in p_lower:
        resp_sistema = "Segundo o Manual: Desobedecer é a causa oculta no coração, enquanto Transgredir é o efeito manifesto contra a Lei Moral de Deus."
    elif 'comboio' in p_lower or 'sentimento' in p_lower:
        resp_sistema = "O crente anda pela Fé nas Promessas (A Locomotiva do Facto). Os sentimentos são apenas o vagão traseiro que segue a locomotiva (2Co 5:7)."
    elif 'ceia' in p_lower or 'baptismo' in p_lower:
        resp_sistema = "O Baptismo nas águas por imersão é a morte e sepultamento para o pecado e ressurreição para Deus (Rm 6:4). A Ceia tem três dimensões: Passado (Cruz), Presente (Autoexame) e Futuro (A Vinda do Senhor)."

    m = "%s" if DATABASE_URL else "?"
    sql = f"""INSERT INTO duvidas_alunos (aluno_id, licao_id, pergunta, resposta_sistema, criado_em)
              VALUES ({m}, {m}, {m}, {m}, {m})"""
    executar_comando(sql, (aluno_id, licao_id, pergunta, resp_sistema, datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect(f"/ensino/aulas?licao={licao_id}#duvidas")

# 4. Exame Final de Conclusão do Curso
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
            flash(f"Obteve {nota_final}%. É necessário no mínimo 70% no Exame Final. Reveja as lições e tente novamente.")

    return render_template('aluno_exame_final.html', aluno=aluno, questoes=questoes_finais)

# 5. Certificado Oficial de Conclusão com Logotipo da Igreja
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
# RESTANTE DO SISTEMA (CADASTRO, SECRETARIA, CULTOS, FINANÇAS)
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
    classe = fd.get('classe', 'Classe I - Primeiros Passos').strip()
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
print("✓ app.py: Lógica curricular, bloqueio sequencial e emissão de certificado prontas!")

# =============================================================================
# 2. NOVO PORTAL DO ALUNO COM SIDEBAR POR CLASSES E FLUXO DAS 3 ETAPAS
# =============================================================================
portal_html = '''<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portal do Aluno - IEAD Chicuque</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .card-bg { background: linear-gradient(135deg, #090d16 0%, #1e1b4b 60%, #312e81 100%); }
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

        <!-- BOAS-VINDAS & APROVEITAMENTO GLOBAL -->
        <div class="card-bg text-white p-6 sm:p-8 rounded-3xl shadow-xl flex flex-col lg:flex-row lg:items-center justify-between gap-6">
            <div class="space-y-2">
                <span class="bg-amber-400 text-slate-950 text-[10px] font-black uppercase px-3 py-1 rounded-full shadow">
                    Plataforma de Discipulado Contínuo
                </span>
                <h2 class="text-2xl sm:text-3xl font-black">
                    A Paz do Senhor, {{ aluno.nome_aluno }}!
                </h2>
                <p class="text-xs sm:text-sm text-indigo-200 max-w-2xl leading-relaxed">
                    As lições seguem a ordem do <b>Manual de Candidatos e Integração da IEADAO</b>. Para avançar, leia a lição, <b>submeta o seu resumo</b> e atinja pelo menos <b>70% no teste</b>.
                </p>
            </div>

            <div class="bg-white/10 backdrop-blur-md border border-white/20 p-5 rounded-3xl text-center shrink-0 w-full lg:w-64">
                <span class="text-[10px] uppercase font-bold text-indigo-200 block">Aproveitamento Médio</span>
                <div class="text-4xl font-black mt-1 text-amber-300">
                    {{ "%.1f"|format(aluno.aproveitamento or 0) }}%
                </div>
                <div class="w-full bg-slate-900/60 h-2.5 rounded-full overflow-hidden my-2.5 border border-white/10">
                    <div class="bg-emerald-400 h-full rounded-full transition-all duration-700" style="width: {{ [aluno.aproveitamento or 0, 100]|min }}%"></div>
                </div>

                {% if todas_concluidas %}
                <span class="text-[11px] font-bold text-emerald-300 block mb-2">🎉 Todas as Lições Concluídas!</span>
                <a href="/ensino/exame_final" class="block w-full py-2 bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-black rounded-xl text-xs shadow transition">
                    🏆 Fazer Exame Final & Obter Certificado
                </a>
                {% else %}
                <span class="text-[10px] text-indigo-200 block">Nota mínima de desbloqueio: <b>70%</b></span>
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

            <!-- COLUNA DA ESQUERDA: AS 4 CLASSES E SUAS LIÇÕES COM STATUS -->
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

            <!-- COLUNA DA DIREITA: A LIÇÃO ATIVA COM O FLUXO DE 3 ETAPAS -->
            <div class="lg:col-span-8 space-y-6">

                <!-- ETAPA 1: ESTUDO DA LIÇÃO -->
                <div class="bg-white p-6 sm:p-8 rounded-3xl shadow-sm border border-slate-200 space-y-6">
                    <div class="border-b border-slate-100 pb-4">
                        <span class="text-xs font-black uppercase text-indigo-600 tracking-wider">
                            ETAPA 1: LEITURA & FUNDAMENTO BÍBLICO
                        </span>
                        <h2 class="text-2xl font-black text-slate-900 mt-1">{{ licao.numero }}: {{ licao.titulo }}</h2>
                        <p class="text-xs text-slate-500 mt-0.5">Leitura Bíblica: <b>{{ licao.leitura_base }}</b></p>
                    </div>

                    <div class="bg-amber-50 border-l-4 border-amber-500 p-4 rounded-r-2xl">
                        <span class="text-[10px] font-black uppercase text-amber-900 block mb-1">🔥 Texto Áureo da Lição</span>
                        <p class="text-xs italic text-amber-950 font-serif leading-relaxed">"{{ licao.texto_aureo }}"</p>
                    </div>

                    <div class="p-5 bg-slate-50 rounded-2xl border border-slate-200 text-xs text-slate-700 leading-relaxed text-justify space-y-3">
                        <p class="font-bold text-sm text-slate-800">Doutrina e Conteúdo da Lição:</p>
                        <p>{{ licao.conteudo }}</p>
                    </div>

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
                                <p class="text-xs text-slate-500">Escreva com as suas próprias palavras. O teste de fixação só será destravado após submeter o resumo.</p>
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
                            <textarea name="resumo" required rows="4" placeholder="Escreva aqui pelo menos 2 ou 3 frases explicando o que compreendeu do texto áureo e do conteúdo desta lição..." class="w-full p-4 border-2 border-slate-200 rounded-2xl bg-slate-50 focus:bg-white focus:border-indigo-600 focus:outline-none font-medium leading-relaxed"></textarea>
                            <button type="submit" class="w-full py-3.5 bg-amber-600 hover:bg-amber-700 text-white font-black rounded-xl shadow cursor-pointer text-xs transition">
                                ✍️ Submeter Resumo & Desbloquear o Teste de Fixação
                            </button>
                        </form>
                        {% endif %}
                    </div>

                    <!-- ETAPA 3: TESTE DE FIXAÇÃO (SÓ ABRE APÓS ENTREGAR O RESUMO) -->
                    <div id="teste" class="pt-6 border-t-2 border-slate-100 space-y-4">
                        <span class="text-xs font-black uppercase text-indigo-600 tracking-wider block">
                            ETAPA 3: TESTE DE FIXAÇÃO TEOLÓGICA (MÍNIMO 70%)
                        </span>

                        {% if not progresso_atual.resumo %}
                        <div class="bg-slate-100 border-2 border-dashed border-slate-300 p-8 rounded-2xl text-center space-y-2">
                            <span class="text-3xl">🔒</span>
                            <h4 class="font-bold text-sm text-slate-700">Teste Bloqueado</h4>
                            <p class="text-xs text-slate-500 max-w-md mx-auto">
                                Para ter acesso a este teste, complete o estudo da lição acima e <b>submeta o seu resumo na Etapa 2</b>.
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

                    <!-- ESPAÇO TIRA-DÚVIDAS -->
                    <div id="duvidas" class="pt-6 border-t-2 border-slate-100 space-y-4">
                        <h4 class="font-extrabold text-sm text-slate-900 flex items-center gap-2">
                            <span>💬</span> Espaço Tira-Dúvidas da Lição
                        </h4>
                        <form action="/ensino/duvida" method="POST" class="space-y-2 text-xs">
                            <input type="hidden" name="licao_id" value="{{ licao.id }}">
                            <div class="flex gap-2">
                                <input type="text" name="pergunta" required placeholder="Tem alguma dúvida bíblica? Pergunte aqui..." class="flex-1 h-11 px-3 border rounded-xl bg-slate-50">
                                <button type="submit" class="px-5 h-11 bg-slate-800 text-white font-bold rounded-xl shadow cursor-pointer">Perguntar</button>
                            </div>
                        </form>
                        <div class="space-y-2">
                            {% for d in duvidas %}
                            <div class="p-3 bg-slate-50 rounded-xl text-xs space-y-1">
                                <div class="font-bold text-slate-800">Pergunta: "{{ d.pergunta }}"</div>
                                <div class="p-2.5 bg-white border border-indigo-100 rounded-lg text-indigo-950 text-[11px] leading-relaxed">
                                    <b>Resposta:</b> {{ d.resposta_sistema }}
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>

                </div>
            </div>

        </div>

    </main>
</body>
</html>
'''

with open(os.path.join('templates', 'portal_aluno.html'), 'w', encoding='utf-8') as f:
    f.write(portal_html)
print("✓ templates/portal_aluno.html atualizado!")

# =============================================================================
# 3. TELA DE EXAME FINAL DO CURSO
# =============================================================================
exame_html = '''<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <title>Exame Final de Conclusão - IEAD Chicuque</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 min-h-screen text-slate-800 p-6 font-sans flex items-center justify-center">
    <div class="max-w-2xl w-full bg-white rounded-3xl shadow-2xl p-8 space-y-6">
        <div class="text-center border-b pb-4">
            <div class="w-16 h-16 mx-auto rounded-full bg-indigo-950 text-white flex items-center justify-center font-black text-2xl shadow mb-2">AD</div>
            <h1 class="text-2xl font-black uppercase text-slate-900">EXAME FINAL DE DOUTRINA</h1>
            <p class="text-xs text-amber-700 font-bold uppercase tracking-wider">Avaliação Geral de Graduação e Batismo</p>
            <p class="text-xs text-slate-500 mt-1">Aluno: <b>{{ aluno.nome_aluno }}</b> • Requisito: Mínimo 70% de Acertos</p>
        </div>

        <form action="/ensino/exame_final" method="POST" class="space-y-4 text-xs">
            {% for q in questoes %}
            <div class="p-4 bg-slate-50 rounded-2xl border border-slate-200 space-y-2">
                <p class="font-extrabold text-sm text-slate-800">{{ loop.index }}. {{ q.p }}</p>
                <div class="space-y-1.5">
                    {% for op in q.ops %}
                    <label class="flex items-center gap-3 p-2.5 bg-white rounded-xl border border-slate-200 cursor-pointer hover:bg-indigo-50">
                        <input type="radio" name="q_{{ loop.parent.loop.index0 }}" value="{{ loop.index0 }}" required class="w-4 h-4 text-indigo-600">
                        <span class="text-slate-700 font-medium">{{ op }}</span>
                    </label>
                    {% endfor %}
                </div>
            </div>
            {% endfor %}

            <button type="submit" class="w-full py-4 bg-emerald-700 hover:bg-emerald-800 text-white font-black rounded-2xl shadow-xl cursor-pointer text-sm">
                🎓 Submeter Exame Final e Gerar Certificado Oficial
            </button>
        </form>
    </div>
</body>
</html>
'''

with open(os.path.join('templates', 'aluno_exame_final.html'), 'w', encoding='utf-8') as f:
    f.write(exame_html)

# =============================================================================
# 4. CERTIFICADO OFICIAL DE CONCLUSÃO COM LOGO DA IGREJA
# =============================================================================
certificado_html = '''<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <title>Certificado de Conclusão - {{ aluno.nome_aluno }}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @media print {
            .no-print { display: none !important; }
            body { background: white !important; padding: 0 !important; }
            @page { size: A4 landscape; margin: 10mm; }
        }
    </style>
</head>
<body class="bg-slate-200 min-h-screen p-8 font-serif flex flex-col items-center justify-center">

    <div class="no-print mb-6 flex gap-4 font-sans text-xs">
        <a href="/ensino/aulas" class="px-4 py-2 bg-slate-800 text-white rounded-xl font-bold shadow">← Voltar às Aulas</a>
        <button onclick="window.print()" class="px-6 py-2 bg-indigo-700 hover:bg-indigo-800 text-white font-extrabold rounded-xl shadow cursor-pointer">
            🖨️ Imprimir Certificado Oficial / Guardar PDF
        </button>
    </div>

    <div class="w-full max-w-4xl bg-white p-12 rounded-3xl shadow-2xl border-8 border-double border-amber-600/70 relative print:shadow-none print:border-amber-700">
        
        <div class="text-center border-b-2 border-amber-600/40 pb-6 mb-8 font-sans">
            <div class="w-16 h-16 mx-auto rounded-full bg-indigo-950 text-white flex items-center justify-center font-black text-2xl shadow mb-2 border-2 border-amber-400">
                AD
            </div>
            <h1 class="text-2xl font-black uppercase tracking-widest text-slate-950">ASSEMBLEIA DE DEUS EM MOÇAMBIQUE</h1>
            <h2 class="text-xs font-bold uppercase tracking-wider text-amber-800 mt-0.5">MINISTÉRIO THAVANE • SEDE REGIONAL DE CHICUQUE - MAXIXE</h2>
            <p class="text-[10px] uppercase tracking-widest text-slate-400 mt-1">Departamento de Educação Cristã & Escola de Integração Bíblica</p>
        </div>

        <div class="text-center my-6 font-sans">
            <h3 class="text-3xl font-black uppercase tracking-widest text-indigo-950 underline decoration-amber-500 underline-offset-8">
                CERTIFICADO DE FORMAÇÃO DOUTRINÁRIA
            </h3>
        </div>

        <div class="text-center max-w-2xl mx-auto space-y-4 my-8 text-base leading-relaxed text-slate-800">
            <p>
                Certificamos solenemente que o(a) irmão(ã)
            </p>
            <p class="text-3xl font-extrabold text-indigo-950 uppercase border-b-2 border-slate-300 pb-1 mx-8 font-sans">
                {{ aluno.nome_aluno }}
            </p>
            <p class="text-sm">
                Concluiu com êxito todas as lições curriculares, resumos e testes teológicos do Manual Oficial da Igreja, obtendo o aproveitamento de <b class="text-indigo-950 font-sans text-lg">{{ "%.1f"|format(aluno.aproveitamento or 0) }}%</b>, sendo declarado(a) apto(a) e promovido(a) na fé cristã.
            </p>
            <p class="text-xs italic text-slate-600 pt-2 font-sans">
                "Procura apresentar-te a Deus aprovado, como obreiro que não tem de que se envergonhar, que maneja bem a palavra da verdade." — <b>2 Timóteo 2:15</b>
            </p>
        </div>

        <div class="grid grid-cols-2 gap-12 mt-12 pt-8 border-t border-slate-200 text-center font-sans text-xs">
            <div>
                <div class="w-56 mx-auto border-b border-slate-600 mb-1.5"></div>
                <p class="font-extrabold text-slate-900">Pastor Presidente Regional</p>
                <p class="text-[10px] text-slate-500">IEAD Sede Chicuque</p>
            </div>
            <div>
                <div class="w-56 mx-auto border-b border-slate-600 mb-1.5"></div>
                <p class="font-extrabold text-slate-900">Diretor de Educação Cristã</p>
                <p class="text-[10px] text-slate-500">Ministério Thavane</p>
            </div>
        </div>

        <div class="text-center font-sans text-[10px] text-slate-400 mt-6">
            Emitido e homologado pela Secretaria-Geral em Chicuque, aos {{ data_extenso }}.
        </div>
    </div>
</body>
</html>
'''

with open(os.path.join('templates', 'certificado_ensino.html'), 'w', encoding='utf-8') as f:
    f.write(certificado_html)
print("✓ templates/certificado_ensino.html gerado com sucesso!")

print("=" * 80)
print("SISTEMA TOTALMENTE ATUALIZADO COM AS NOVAS DIRETRIZES!")
print("=" * 80)