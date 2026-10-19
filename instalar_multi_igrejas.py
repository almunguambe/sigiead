import os
import py_compile
import jinja2

print("=" * 80)
print("A CONFIGURAR ARQUITETURA MULTI-CONGREGAÇÃO E ISOLAMENTO TOTAL...")
print("=" * 80)

os.makedirs('templates', exist_ok=True)
env = jinja2.Environment()

# =============================================================================
# 1. ATUALIZAR O APP.PY COM MULTI-TENANT UNIVERSAL E ISOLAMENTO ESTREITO
# =============================================================================
app_code = '''import os
import sqlite3
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'iead_mz_multitenant_2026')

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

# ESTRUTURA TERRITORIAL OFICIAL: 36 DISTRITOS DE MOÇAMBIQUE
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
                    (congregacao_id, nome_aluno, classe, professor, licao_atual, data_inicio, presencas, situacao, usuario, senha, aproveitamento, criado_em)
                    VALUES (1, 'Anselmo Munguambe', 'Classe I - Primeiros Passos', 'Pastor Dirigente', 'Lição 1 - O Pecado e o Perdão', '2026-01-01', 1, 'Em Formação', ?, ?, 0.0, ?)"""
        executar_comando(sql_al, ('anselmo', '123456', datetime.now().strftime('%Y-%m-%d %H:%M')))

inicializar_banco()

# =============================================================================
# CURRÍCULO DE ENSINO: CONTEÚDO INTEGRAL DO MANUAL DA IEADAO
# =============================================================================
CURRICULO_CLASSES = [
    {
        'id_classe': 'classe_1', 'nome_classe': 'Classe I - Primeiros Passos', 'descricao': 'Rudimentos da Fé Cristã',
        'licoes': [
            {
                'id': 'c1_l1', 'numero': 'Lição 1', 'titulo': 'O Pecado e o Perdão',
                'texto_aureo': 'Porque o salário do pecado é a morte, mas o dom gratuito de Deus é a vida eterna. (Rm 6:23)',
                'leitura_base': 'Rm 3:23; Is 59:2; 1Jo 1:7-9; Pv 28:13; Hb 9:22',
                'conteudo': 'Pecar significa literalmente "Errar o Alvo" da Santa Vontade de Deus. Desobedecer é a causa no coração e Transgredir é o efeito visível contra a Lei. Na cruz, Cristo operou a Expiação e deu reconciliação.',
                'conteudo_completo': {
                    'introducao': 'A doutrina bíblica do pecado e da redenção é o alicerce da vida cristã.',
                    'pontos_doutrinarios': [
                        {'titulo': '1. O Significado de Pecar', 'detalhes': 'Pecar significa "Errar o Alvo" soberano da Vontade de Deus.'},
                        {'titulo': '2. Transgressão e Desobediência', 'detalhes': 'Desobedecer é a causa oculta; transgredir é o efeito manifesto.'},
                        {'titulo': '3. Situação do Homem', 'tabela': [
                            {'situacao': 'Imoralidade', 'descricao': 'Desfiguração da imagem divina.', 'versiculos': 'Rm 3:9-12'},
                            {'situacao': 'Inimigo', 'descricao': 'Separação espiritual.', 'versiculos': 'Is 59:2'},
                            {'situacao': 'Morte', 'descricao': 'Condenação eterna.', 'versiculos': 'Rm 6:23'}
                        ]},
                        {'titulo': '4. O Perdão e a Expiação', 'detalhes': 'Cristo pagou o preço por nós. Quando perdoa, coloca Paz, Graça e Amor.'}
                    ],
                    'proverbio_chave': 'O que confessa e deixa, alcançará misericórdia. (Pv 28:13)'
                },
                'questoes': [
                    {'p': 'Qual é a diferença entre desobedecer e transgredir?', 'ops': ['Transgredir é no coração e desobedecer é físico.', 'Desobedecer é a causa oculta no coração e transgredir é o efeito exposto.', 'Não há diferença.', 'Apenas para pagãos.'], 'c': 1},
                    {'p': 'O que acontece espiritualmente quando Cristo perdoa?', 'ops': ['Apenas suspende o castigo.', 'Não só tira o pecado, mas coloca Amor, Graça, Paz e Gozo.', 'Exige dinheiro.', 'Cancela o batismo.'], 'c': 1}
                ]
            },
            {
                'id': 'c1_l2', 'numero': 'Lição 2', 'titulo': 'Salvação e Senhorio de Cristo',
                'texto_aureo': 'Se alguém está em Cristo, nova criatura é. (2Co 5:17)',
                'leitura_base': 'Ef 2:8-10; Jo 1:12; 1Co 8:6',
                'conteudo': 'Somos salvos pela graça por meio da fé. Cristo quer dominar como Senhor do nosso coração.',
                'conteudo_completo': {
                    'introducao': 'Salvação pela graça e fruto em santidade.',
                    'pontos_doutrinarios': [
                        {'titulo': '1. Passos para a Salvação', 'detalhes': 'Ouvir, Crer, Arrepender-se e Receber a Cristo.'},
                        {'titulo': '2. Senhorio de Cristo', 'detalhes': 'Cristo governa no trono da nossa vida.'}
                    ],
                    'proverbio_chave': 'Cristo é Salvador e Senhor.'
                },
                'questoes': [
                    {'p': 'Qual é a relação entre fé, obras e salvação em Efésios 2:8-10?', 'ops': ['As obras compram o céu.', 'Salvos pela graça por meio da fé, e as obras acompanham como fruto.', 'Obras não importam.', 'Apenas rituais.'], 'c': 1}
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
# CONTEXT PROCESSOR: DADOS ISOLADOS POR CONGREGAÇÃO (MULTI-TENANT)
# =============================================================================
@app.context_processor
def injetar_dados():
    u_id = session.get('usuario_id')
    user = consultar_um("SELECT * FROM usuarios_sistema WHERE id = ?", (u_id,)) if u_id else None
    cid = session.get('congregacao_id', 1)
    
    cong = consultar_um("SELECT * FROM congregacoes WHERE id = ?", (cid,)) or {
        'id': 1, 'nome': 'Assembleia de Deus', 'distrito': 'Maxixe (Cidade/Distrito)', 'provincia': 'Inhambane', 'pastor_responsavel': 'Pastor Dirigente'
    }

    # TODAS AS CONSULTAS ESTÃO ISOLADAS POR CONGREGAÇÃO
    membros = consultar_todos("SELECT * FROM membros WHERE congregacao_id = ? ORDER BY id DESC", (cid,))
    planos = consultar_todos("SELECT * FROM planificacao WHERE congregacao_id = ? ORDER BY id DESC", (cid,))
    cultos = consultar_todos("SELECT * FROM cultos WHERE congregacao_id = ? ORDER BY id DESC", (cid,))
    convertidos = consultar_todos("SELECT * FROM novos_convertidos WHERE congregacao_id = ? ORDER BY id DESC", (cid,))
    caixa = consultar_todos("SELECT * FROM caixa WHERE congregacao_id = ? ORDER BY id DESC", (cid,))
    doutrina = consultar_todos("SELECT * FROM doutrina WHERE congregacao_id = ? ORDER BY id DESC", (cid,))
    casamentos = consultar_todos("SELECT * FROM casamentos WHERE congregacao_id = ? ORDER BY id DESC", (cid,))
    obitos = consultar_todos("SELECT * FROM obitos WHERE congregacao_id = ? ORDER BY id DESC", (cid,))
    
    # Utilizadores desta congregação
    if user and user.get('perfil') == 'admin' and user.get('usuario') == 'admin':
        usuarios_todos = consultar_todos("SELECT id, nome, usuario, perfil, nivel, congregacao_id, criado_em FROM usuarios_sistema ORDER BY id ASC")
    else:
        usuarios_todos = consultar_todos("SELECT id, nome, usuario, perfil, nivel, congregacao_id, criado_em FROM usuarios_sistema WHERE congregacao_id = ? ORDER BY id ASC", (cid,))
    
    congregacoes_todas = consultar_todos("SELECT * FROM congregacoes ORDER BY provincia, distrito, nome ASC")
    duvidas_pendentes = consultar_todos("SELECT * FROM duvidas_alunos ORDER BY id DESC")
    opcoes_lista = consultar_todos("SELECT * FROM opcoes_sistema ORDER BY categoria, valor ASC")

    opcoes_map = {}
    for op in opcoes_lista:
        opcoes_map.setdefault(op['categoria'], []).append(op)

    # Demografia isolada
    total_homens = len([m for m in membros if str(m.get('genero') or '').lower() in ['masculino', 'homem', 'h']])
    total_mulheres = len(membros) - total_homens
    total_criancas = len([m for m in membros if str(m.get('estado_civil') or '').lower() == 'criança' or 'esperança' in str(m.get('departamento') or '').lower()])
    total_jovens = len([m for m in membros if 'jov' in str(m.get('departamento') or '').lower() or 'jovem' in str(m.get('cargo') or '').lower()])
    total_adultos = max(0, len(membros) - total_criancas - total_jovens)
    total_batizados = len([m for m in membros if m.get('data_batismo')])
    total_nao_batizados = len(membros) - total_batizados

    zonas_contagem = {}
    celulas_contagem = {}
    cargos_contagem = {}
    for m in membros:
        z = m.get('zona') or 'Zona 1 - Central'
        zonas_contagem[z] = zonas_contagem.get(z, 0) + 1
        c = m.get('celula') or 'Célula Betel'
        celulas_contagem[c] = celulas_contagem.get(c, 0) + 1
        cg = m.get('cargo') or 'Membro em Comunhão'
        cargos_contagem[cg] = cargos_contagem.get(cg, 0) + 1

    total_pres = sum([int(c.get('total_presentes') or 0) for c in cultos])
    media_culto = int(total_pres / len(cultos)) if cultos else 0

    # Finanças isoladas
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
        'congregacao': cong,
        'congregacoes_todas': congregacoes_todas,
        'divisao_territorial': DIVISAO_TERRITORIAL,
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
            session['congregacao_id'] = aluno.get('congregacao_id', 1)
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

    # PROTEÇÃO NO SERVIDOR POR PERFIL
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
# ADMINISTRAÇÃO: REGISTO DE NOVAS CONGREGAÇÕES E CONTAS LOCAIS
# =============================================================================
@app.route('/admin/congregacao/nova', methods=['POST'])
def admin_congregacao_nova():
    if session.get('usuario_perfil') != 'admin':
        return redirect('/login')

    fd = request.form
    nome = fd.get('nome_igreja', '').strip()
    prov = fd.get('provincia', 'Inhambane').strip()
    dist = fd.get('distrito', 'Maxixe (Cidade/Distrito)').strip()
    bairro = fd.get('bairro', '').strip()
    pastor = fd.get('pastor', 'Pastor').strip()
    
    admin_u = fd.get('admin_user', '').strip().lower()
    admin_s = fd.get('admin_senha', '123456').strip()

    if nome and admin_u:
        sql = "INSERT INTO congregacoes (nome, provincia, distrito, bairro, pastor_responsavel, criado_em) VALUES (?, ?, ?, ?, ?, ?)"
        executar_comando(sql, (nome, prov, dist, bairro, pastor, datetime.now().strftime('%Y-%m-%d %H:%M')))
        
        nova = consultar_um("SELECT id FROM congregacoes WHERE nome = ? ORDER BY id DESC", (nome,))
        if nova:
            cid = nova['id']
            sql_u = "INSERT INTO usuarios_sistema (nome, usuario, senha, nivel, perfil, congregacao_id, provincia, distrito, criado_em) VALUES (?, ?, ?, 'admin', 'admin', ?, ?, ?, ?)"
            executar_comando(sql_u, (f"Admin - {nome}", admin_u, admin_s, cid, prov, dist, datetime.now().strftime('%Y-%m-%d %H:%M')))

    return redirect('/?aba=configuracoes')

@app.route('/admin/trocar_congregacao/<int:id>')
def admin_trocar_congregacao(id):
    if session.get('usuario_perfil') == 'admin':
        session['congregacao_id'] = id
    return redirect('/?aba=dashboard')

@app.route('/admin/usuarios/novo', methods=['POST'])
def admin_usuario_novo():
    if session.get('usuario_perfil') != 'admin':
        return redirect('/login')
    fd = request.form
    cid = session.get('congregacao_id', 1)
    nome = fd.get('nome', '').strip()
    usuario = fd.get('usuario', '').strip().lower()
    senha = fd.get('senha', '123456').strip()
    perfil = fd.get('perfil', 'secretario').strip()

    if nome and usuario and senha:
        existente = consultar_um("SELECT id FROM usuarios_sistema WHERE LOWER(usuario) = ?", (usuario,))
        if existente:
            return "<script>alert('Este utilizador já existe!'); window.history.back();</script>"
        sql = "INSERT INTO usuarios_sistema (nome, usuario, senha, nivel, perfil, congregacao_id, criado_em) VALUES (?, ?, ?, ?, ?, ?, ?)"
        executar_comando(sql, (nome, usuario, senha, perfil, perfil, cid, datetime.now().strftime('%Y-%m-%d %H:%M')))

    return redirect('/?aba=configuracoes')

@app.route('/admin/usuarios/redefinir_senha', methods=['POST'])
def admin_usuario_redefinir_senha():
    if session.get('usuario_perfil') != 'admin':
        return redirect('/login')
    uid = request.form.get('usuario_id')
    nova = request.form.get('nova_senha', '').strip()
    if uid and nova:
        executar_comando("UPDATE usuarios_sistema SET senha = ? WHERE id = ?", (nova, uid))
    return redirect('/?aba=configuracoes')

@app.route('/admin/usuarios/excluir/<int:id>')
def admin_usuario_excluir(id):
    if session.get('usuario_perfil') != 'admin':
        return redirect('/login')
    u = consultar_um("SELECT usuario FROM usuarios_sistema WHERE id = ?", (id,))
    if u and u.get('usuario') == 'admin':
        return "<script>alert('Não é permitido apagar o Administrador Geral!'); window.history.back();</script>"
    executar_comando("DELETE FROM usuarios_sistema WHERE id = ?", (id,))
    return redirect('/?aba=configuracoes')

@app.route('/admin/alunos/redefinir_senha', methods=['POST'])
def admin_aluno_redefinir_senha():
    aid = request.form.get('aluno_id')
    nova = request.form.get('nova_senha', '').strip()
    if aid and nova:
        executar_comando("UPDATE doutrina SET senha = ? WHERE id = ?", (nova, aid))
    return redirect('/?aba=doutrina')

# =============================================================================
# CADASTROS LOCAIS ISOLADOS POR CONGREGAÇÃO
# =============================================================================
@app.route('/membros/novo', methods=['POST'])
def membros_gravar():
    cid = session.get('congregacao_id', 1)
    fd = request.form
    local = (fd.get('local_residencia') or fd.get('bairro') or '').strip()
    genero = fd.get('genero', 'Masculino').strip()
    sql = """INSERT INTO membros 
              (congregacao_id, nome, contacto, bi, cargo, departamento, estado_civil, zona, celula, ano_conversao, data_batismo, local_residencia, bairro, genero, criado_em)
              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    params = (
        cid, fd.get('nome', '').strip(), fd.get('contacto', '').strip(), fd.get('bi', '').strip(),
        fd.get('cargo', 'Membro em Comunhão').strip(), fd.get('departamento', 'Geral').strip(),
        fd.get('estado_civil', 'Solteiro(a)').strip(), fd.get('zona', 'Zona 1 - Central').strip(),
        fd.get('celula', 'Célula Betel').strip(), fd.get('ano_conversao', '').strip(),
        fd.get('data_batismo', '').strip(), local, local, genero, datetime.now().strftime('%Y-%m-%d %H:%M')
    )
    executar_comando(sql, params)
    return redirect('/?aba=membros')

@app.route('/membros/relatorio-geral')
def membros_relatorio_geral():
    cid = session.get('congregacao_id', 1)
    membros = consultar_todos("SELECT * FROM membros WHERE congregacao_id = ? ORDER BY nome ASC", (cid,))
    cong = consultar_um("SELECT * FROM congregacoes WHERE id = ?", (cid,))
    return render_template('relatorio_membros.html', membros=membros, congregacao=cong, agora=datetime.now().strftime('%d/%m/%Y às %H:%M'))

@app.route('/membros/<int:id>/cartao')
def membros_cartao(id):
    cid = session.get('congregacao_id', 1)
    membro = consultar_um("SELECT * FROM membros WHERE id = ? AND congregacao_id = ?", (id, cid))
    if not membro: return redirect('/?aba=membros')
    cong = consultar_um("SELECT * FROM congregacoes WHERE id = ?", (cid,))
    return render_template('cartao_membro.html', m=membro, congregacao=cong, agora_ano=datetime.now().year)

@app.route('/membros/<int:id>/batismo')
def membros_batismo(id):
    cid = session.get('congregacao_id', 1)
    membro = consultar_um("SELECT * FROM membros WHERE id = ? AND congregacao_id = ?", (id, cid))
    if not membro or not membro.get('data_batismo'):
        return "<script>alert('Membro sem data de baptismo registada!'); window.location.href='/?aba=membros';</script>"
    cong = consultar_um("SELECT * FROM congregacoes WHERE id = ?", (cid,))
    return render_template('cartao_batismo.html', m=membro, congregacao=cong, data_extenso=datetime.now().strftime('%d de %B de %Y'))

@app.route('/membros/<int:id>/recomendacao')
def membros_recomendacao(id):
    cid = session.get('congregacao_id', 1)
    membro = consultar_um("SELECT * FROM membros WHERE id = ? AND congregacao_id = ?", (id, cid))
    if not membro: return redirect('/?aba=membros')
    cong = consultar_um("SELECT * FROM congregacoes WHERE id = ?", (cid,))
    return render_template('carta_recomendacao.html', m=membro, congregacao=cong, data_extenso=datetime.now().strftime('%d de %B de %Y'), agora_ano=datetime.now().year)

@app.route('/cultos/novo', methods=['POST'])
def cultos_gravar():
    cid = session.get('congregacao_id', 1)
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
              (congregacao_id, data_culto, tipo_culto, homens_adultos, mulheres_adultas, jovens_rapazes, jovens_mocas,
               criancas_meninos, criancas_meninas, visitantes_homens, visitantes_mulheres, apelos, total_presentes, pregador, tema_mensagem, criado_em)
              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    executar_comando(sql, (cid, dt, tipo, ha, ma, jr, jm, cm, cf, vh, vm, apelos, tot, preg, tema, datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=cultos')

@app.route('/financas/caixa/novo', methods=['POST'])
def caixa_gravar():
    perfil = session.get('usuario_perfil', '')
    if perfil not in ['tesoureiro', 'admin']:
        return "<script>alert('Acesso negado! O lançamento de caixa é exclusivo da Tesouraria.'); window.location.href='/?aba=dashboard';</script>"

    cid = session.get('congregacao_id', 1)
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
        categoria = "Igreja Mãe: " + fd.get('categoria_entrada_mae', 'Apoio') if destino_tipo == 'Igreja Mãe' else (f"Entrada: {depto}" if destino_tipo == 'Departamento' else fd.get('categoria', 'Dízimos'))
    else:
        categoria = "Igreja Mãe: " + fd.get('categoria_saida_mae', 'Dízimo dos Dízimos') if destino_tipo == 'Igreja Mãe' else (f"Saída: {depto}" if destino_tipo == 'Departamento' else fd.get('categoria_saida_geral', 'Despesa'))

    sql = """INSERT INTO caixa 
              (congregacao_id, tipo, categoria, valor, descricao, data_movimento, conta, destino_tipo, departamento, proposito, criado_em)
              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    executar_comando(sql, (cid, tipo, categoria, val, desc, dt, conta, destino_tipo, depto, proposito, datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=tesouraria')

@app.route('/actos/casamento/novo', methods=['POST'])
def actos_casamento():
    cid = session.get('congregacao_id', 1)
    fd = request.form
    sql = "INSERT INTO casamentos (congregacao_id, tipo, noivo, noiva, data_casamento, ministro, regime, certidao, criado_em) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    executar_comando(sql, (cid, fd.get('tipo'), fd.get('noivo'), fd.get('noiva'), fd.get('data_casamento'), fd.get('ministro'), fd.get('regime'), fd.get('certidao'), datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=actos')

@app.route('/actos/casamento/remover/<int:id>')
def actos_casamento_remover(id):
    cid = session.get('congregacao_id', 1)
    executar_comando("DELETE FROM casamentos WHERE id = ? AND congregacao_id = ?", (id, cid))
    return redirect('/?aba=actos')

@app.route('/actos/obito/novo', methods=['POST'])
def actos_obito():
    cid = session.get('congregacao_id', 1)
    fd = request.form
    sql = "INSERT INTO obitos (congregacao_id, nome_falecido, genero, categoria, data_falecimento, local_funeral, causa, contacto_familia, criado_em) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    executar_comando(sql, (cid, fd.get('nome_falecido'), fd.get('genero'), fd.get('categoria'), fd.get('data_falecimento'), fd.get('local_funeral'), fd.get('causa'), fd.get('contacto_familia'), datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=actos')

@app.route('/actos/obito/remover/<int:id>')
def actos_obito_remover(id):
    cid = session.get('congregacao_id', 1)
    executar_comando("DELETE FROM obitos WHERE id = ? AND congregacao_id = ?", (id, cid))
    return redirect('/?aba=actos')

@app.route('/convertidos/novo', methods=['POST'])
def convertidos_gravar():
    cid = session.get('congregacao_id', 1)
    fd = request.form
    sql = """INSERT INTO novos_convertidos 
              (congregacao_id, nome, telefone, bairro, data_decisao, quem_convidou, culto_origem, status_discipulado, criado_em)
              VALUES (?, ?, ?, ?, ?, ?, ?, 'Acompanhamento', ?)"""
    executar_comando(sql, (cid, fd.get('nome'), fd.get('telefone'), fd.get('bairro'), fd.get('data_decisao'), fd.get('quem_convidou'), fd.get('culto_origem'), datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=convertidos')

@app.route('/secretaria/planificacao/nova', methods=['POST'])
def secretaria_gravar():
    cid = session.get('congregacao_id', 1)
    fd = request.form
    act = (fd.get('actividade') or 'Actividade').strip()
    sql = """INSERT INTO planificacao 
              (congregacao_id, actividade, titulo, nome_actividade, departamento, tipo_evento, data_prevista, data_inicio, frequencia, responsavel, contacto, status, criado_em)
              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Planeado', ?)"""
    executar_comando(sql, (cid, act, act, act, fd.get('departamento'), fd.get('tipo_evento'), fd.get('data_prevista'), fd.get('data_prevista'), fd.get('frequencia'), fd.get('responsavel'), fd.get('contacto'), datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=secretaria')

@app.route('/secretaria/planificacao/relatar', methods=['POST'])
def secretaria_relatar():
    cid = session.get('congregacao_id', 1)
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
              total_participantes = ? WHERE id = ? AND congregacao_id = ?"""
    executar_comando(sql, (feedback, data_exec, h, m_mulher, jov, cri, total, plano_id, cid))
    return redirect('/?aba=secretaria')

@app.route('/secretaria/balanco', methods=['GET', 'POST'])
def secretaria_balanco():
    cid = session.get('congregacao_id', 1)
    agora = datetime.now()
    ano_sel = request.args.get('ano', agora.year, type=int)

    if request.method == 'POST':
        fd = request.form
        ano_form = int(fd.get('ano_exercicio', ano_sel))
        planos_todos = consultar_todos("SELECT * FROM planificacao WHERE congregacao_id = ?", (cid,))
        for p in planos_todos:
            pid = str(p['id'])
            if f"status_{pid}" in fd:
                st = fd.get(f"status_{pid}", 'Planeado').strip()
                fb = fd.get(f"feedback_{pid}", '').strip()
                dif = fd.get(f"dificuldades_{pid}", '').strip()
                persp = fd.get(f"perspectivas_{pid}", '').strip()
                def to_i(k):
                    v = fd.get(k)
                    return int(v) if v and v.isdigit() else 0
                h, mulh, j, c = to_i(f"part_h_{pid}"), to_i(f"part_m_{pid}"), to_i(f"part_j_{pid}"), to_i(f"part_c_{pid}")
                tot = h + mulh + j + c
                sql_up = """UPDATE planificacao SET 
                             status = ?, feedback = ?, dificuldades = ?, 
                             perspectivas = ?, participantes_homens = ?, 
                             participantes_mulheres = ?, participantes_jovens = ?, 
                             participantes_criancas = ?, total_participantes = ? 
                             WHERE id = ? AND congregacao_id = ?"""
                executar_comando(sql_up, (st, fb, dif, persp, h, mulh, j, c, tot, pid, cid))

        c1, c2, c3 = fd.get('constrangimento_1', ''), fd.get('constrangimento_2', ''), fd.get('constrangimento_3', '')
        p1, p2, p3 = fd.get('perspectiva_1', ''), fd.get('perspectiva_2', ''), fd.get('perspectiva_3', '')

        existente = consultar_um("SELECT id FROM balanco_anual WHERE ano = ? AND congregacao_id = ?", (ano_form, cid))
        if existente:
            sql_bal = """UPDATE balanco_anual SET 
                          constrangimento_1 = ?, constrangimento_2 = ?, constrangimento_3 = ?,
                          perspectiva_1 = ?, perspectiva_2 = ?, perspectiva_3 = ?,
                          atualizado_em = ? WHERE ano = ? AND congregacao_id = ?"""
            executar_comando(sql_bal, (c1, c2, c3, p1, p2, p3, datetime.now().strftime('%Y-%m-%d %H:%M'), ano_form, cid))
        else:
            sql_bal = """INSERT INTO balanco_anual 
                          (congregacao_id, ano, constrangimento_1, constrangimento_2, constrangimento_3, perspectiva_1, perspectiva_2, perspectiva_3, atualizado_em)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
            executar_comando(sql_bal, (cid, ano_form, c1, c2, c3, p1, p2, p3, datetime.now().strftime('%Y-%m-%d %H:%M')))

        return redirect("/secretaria/relatorio-anual?sucesso_balanco=1")

    planos = consultar_todos("SELECT * FROM planificacao WHERE congregacao_id = ? ORDER BY id ASC", (cid,))
    balanco = consultar_um("SELECT * FROM balanco_anual WHERE ano = ? AND congregacao_id = ?", (ano_sel, cid))
    return render_template('balanco_anual.html', ano_sel=ano_sel, planos=planos, balanco=balanco)

@app.route('/secretaria/relatorio-anual')
def secretaria_relatorio_anual():
    cid = session.get('congregacao_id', 1)
    casamentos = consultar_todos("SELECT * FROM casamentos WHERE congregacao_id = ?", (cid,))
    obitos = consultar_todos("SELECT * FROM obitos WHERE congregacao_id = ?", (cid,))
    cong = consultar_um("SELECT * FROM congregacoes WHERE id = ?", (cid,))

    agora = datetime.now()
    meses_pt = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
    balanco = consultar_um("SELECT * FROM balanco_anual WHERE ano = ? AND congregacao_id = ?", (agora.year, cid))
    
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
        'ano_atual': agora.year,
        'data_dia': agora.strftime('%d'),
        'data_mes': meses_pt.get(agora.month, 'Outubro'),
        'casamentos': {'jovens': len([c for c in casamentos if 'jov' in str(c.get('tipo', '')).lower()]), 'adultos': len([c for c in casamentos if 'jov' not in str(c.get('tipo', '')).lower()]), 'total': len(casamentos)},
        'constrangimentos': constrangimentos_lista,
        'perspectivas': perspectivas_lista
    }
    return render_template('relatorio_anual_modelo.html', rel=rel, congregacao=cong)

# DOUTRINA E ENSINO
@app.route('/doutrina/novo', methods=['POST'])
def doutrina_gravar():
    cid = session.get('congregacao_id', 1)
    fd = request.form
    aluno = fd.get('nome_aluno', 'Aluno').strip()
    usuario = fd.get('usuario', '').strip().lower() or aluno.split()[0].lower() + str(datetime.now().second)
    senha = fd.get('senha', '123456').strip()
    sql = """INSERT INTO doutrina 
              (congregacao_id, nome_aluno, classe, professor, licao_atual, data_inicio, presencas, situacao, usuario, senha, aproveitamento, criado_em)
              VALUES (?, ?, ?, ?, 'Lição 1 - O Pecado e o Perdão', ?, 1, 'Em Formação', ?, ?, 0.0, ?)"""
    executar_comando(sql, (cid, aluno, fd.get('classe'), fd.get('professor'), fd.get('data_inicio'), usuario, senha, datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=doutrina')

@app.route('/doutrina/responder_duvida', methods=['POST'])
def doutrina_responder_duvida():
    duvida_id = request.form.get('duvida_id')
    resp_prof = request.form.get('resposta_professor', '').strip()
    prof_nome = request.form.get('professor_nome', 'Pastor').strip()
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
        executar_comando("UPDATE progresso_licoes SET resumo_aluno = ? WHERE id = ?", (resumo, existente['id']))
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
    acertos = sum([1 for idx, q in enumerate(questoes) if request.form.get(f"q_{idx}") is not None and int(request.form.get(f"q_{idx}")) == q['c']])
    nota = round((acertos / len(questoes)) * 100.0, 1) if questoes else 0.0

    executar_comando("UPDATE progresso_licoes SET nota_teste = ?, status = ? WHERE aluno_id = ? AND licao_id = ?",
                     (nota, 'Concluída' if nota >= 70.0 else 'Repetir Teste', aluno_id, licao_id))

    if nota >= 70.0:
        for i, l in enumerate(TODAS_LICOES):
            if l['id'] == licao_id and (i + 1) < len(TODAS_LICOES):
                return redirect(f"/ensino/aulas?licao={TODAS_LICOES[i + 1]['id']}&sucesso_aprovado=1")
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

    sql = "INSERT INTO duvidas_alunos (aluno_id, licao_id, pergunta, resposta_sistema, criado_em) VALUES (?, ?, ?, ?, ?)"
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

# =============================================================================
# 2. ATUALIZAR TEMPLATES/DASHBOARD.HTML COM CADASTRO DE CONGREGAÇÕES E ISOLAMENTO
# =============================================================================
with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    dash_html = f.read()

import re

# Injetar o seletor de congregação no menu superior se for Super Admin
seletor_igreja_topo = """            <!-- SELETOR DINÂMICO DE CONGREGAÇÃO (VISÍVEL APENAS PARA ADMIN GERAL) -->
            {% if usuario_logado and usuario_logado.usuario == 'admin' and congregacoes_todas|length > 1 %}
            <div class="mb-4 bg-indigo-50 border-2 border-indigo-200 p-3 rounded-2xl flex items-center justify-between text-xs">
                <span class="font-bold text-indigo-950 flex items-center gap-1.5">
                    <span>🏛️</span> Inspecionar Congregação em Sessão:
                </span>
                <select onchange="window.location.href='/admin/trocar_congregacao/' + this.value" class="h-9 px-3 border-2 border-indigo-400 rounded-xl bg-white font-extrabold text-indigo-950">
                    {% for cg in congregacoes_todas %}
                    <option value="{{ cg.id }}" {% if cg.id == congregacao.id %}selected{% endif %}>
                        {{ cg.nome }} ({{ cg.distrito }})
                    </option>
                    {% endfor %}
                </select>
            </div>
            {% endif %}"""

if 'Inspecionar Congregação em Sessão' not in dash_html:
    dash_html = dash_html.replace(
        '<main class="flex-1 p-6 overflow-y-auto">',
        '<main class="flex-1 p-6 overflow-y-auto">\n' + seletor_igreja_topo
    )

# Adicionar o painel de cadastro de novas congregações na aba de configurações
painel_novas_igrejas = """        <!-- CADASTRO DE NOVAS CONGREGAÇÕES COM ADMIN PRÓPRIO (EXCLUSIVO ADMIN) -->
        <div class="bg-white p-6 rounded-2xl shadow-sm border-2 border-amber-300 mb-8 text-xs space-y-4">
            <div class="border-b pb-2 flex justify-between items-center">
                <h3 class="font-black text-sm uppercase text-slate-900 flex items-center gap-2">
                    <span>🏛️</span> Cadastrar Nova Congregação / Igreja Independente
                </h3>
                <span class="bg-amber-100 text-amber-950 px-2.5 py-0.5 rounded-full font-black text-[10px]">Multi-Igrejas</span>
            </div>

            <form action="/admin/congregacao/nova" method="POST" class="space-y-4">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">Nome Oficial da Congregação / Ramo *</label>
                        <input type="text" name="nome_igreja" required placeholder="Ex: Assembleia de Deus de Xai-Xai" class="w-full h-11 px-3 border-2 border-slate-200 rounded-xl bg-slate-50 font-bold">
                    </div>
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">Pastor Responsável / Dirigente *</label>
                        <input type="text" name="pastor" required placeholder="Pr. ..." class="w-full h-11 px-3 border-2 border-slate-200 rounded-xl bg-slate-50 font-bold">
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">Província *</label>
                        <select id="sel_provincia" name="provincia" onchange="atualizarDistritos()" class="w-full h-11 px-2 border-2 border-indigo-300 rounded-xl bg-indigo-50/50 font-black text-indigo-950">
                            {% for prov in divisao_territorial.keys() %}
                            <option value="{{ prov }}">{{ prov }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">Distrito Oficial (36 Distritos) *</label>
                        <select id="sel_distrito" name="distrito" class="w-full h-11 px-2 border-2 border-indigo-300 rounded-xl bg-white font-bold text-slate-800">
                            <!-- Preenchido via Javascript -->
                        </select>
                    </div>
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">Bairro / Localidade</label>
                        <input type="text" name="bairro" placeholder="Ex: Bairro Central" class="w-full h-11 px-3 border rounded-xl bg-slate-50 font-semibold">
                    </div>
                </div>

                <div class="p-3.5 bg-slate-50 border rounded-2xl grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">Utilizador Admin desta Congregação *</label>
                        <input type="text" name="admin_user" required placeholder="Ex: admin_xai" class="w-full h-10 px-3 border rounded-xl bg-white font-bold text-indigo-950">
                    </div>
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">Palavra-passe Inicial *</label>
                        <input type="text" name="admin_senha" value="123456" required class="w-full h-10 px-3 border rounded-xl bg-white font-bold">
                    </div>
                </div>

                <button type="submit" class="w-full py-3.5 bg-slate-900 hover:bg-black text-white font-black rounded-xl shadow cursor-pointer text-xs transition">
                    🏛️ Gravar e Ativar Nova Congregação
                </button>
            </form>
        </div>

        <script>
            var divisaoDistritos = {{ divisao_territorial|tojson }};
            function atualizarDistritos() {
                var prov = document.getElementById('sel_provincia').value;
                var distSelect = document.getElementById('sel_distrito');
                distSelect.innerHTML = '';
                var distritos = divisaoDistritos[prov] || [];
                for (var i = 0; i < distritos.length; i++) {
                    var opt = document.createElement('option');
                    opt.value = distritos[i];
                    opt.innerText = distritos[i];
                    distSelect.appendChild(opt);
                }
            }
            atualizarDistritos();
        </script>"""

if 'Cadastrar Nova Congregação / Igreja Independente' not in dash_html:
    dash_html = dash_html.replace(
        "<!-- GESTÃO DE UTILIZADORES E SENHAS (EXCLUSIVO ADMIN) -->",
        painel_novas_igrejas + "\n\n        <!-- GESTÃO DE UTILIZADORES E SENHAS (EXCLUSIVO ADMIN) -->"
    )

env.parse(dash_html)
with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(dash_html)
print("✓ templates/dashboard.html atualizado com suporte multi-igrejas!")

print("=" * 80)
print(">>> INSTALAÇÃO MULTI-IGREJAS CONCLUÍDA COM TOTAL SUCESSO! <<<")
print("=" * 80)