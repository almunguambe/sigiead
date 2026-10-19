import os
import re
import jinja2

print("=" * 80)
print("A INSTALAR O MÓDULO DE BALANÇO ANUAL E QUESTIONAMENTOS AUTOMÁTICOS...")
print("=" * 80)

os.makedirs('templates', exist_ok=True)

# =============================================================================
# 1. ATUALIZAR O APP.PY COM TABELA E ROTAS DE BALANÇO ANUAL
# =============================================================================
with open('app.py', 'r', encoding='utf-8') as f:
    app_code = f.read()

# Adicionar tabela balanco_anual e novas colunas na planificacao
codigo_tabelas = '''
        # Tabela de Balanço Anual
        cur.execute("""CREATE TABLE IF NOT EXISTS balanco_anual (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ano INT UNIQUE,
            constrangimento_1 TEXT,
            constrangimento_2 TEXT,
            constrangimento_3 TEXT,
            perspectiva_1 TEXT,
            perspectiva_2 TEXT,
            perspectiva_3 TEXT,
            atualizado_em TEXT
        );""")

        # Colunas de questionamento em planificacao
        cur.execute("PRAGMA table_info(planificacao);")
        cols_pl = [c[1].lower() for c in cur.fetchall()]
        for c_nome in ['dificuldades', 'perspectivas']:
            if c_nome not in cols_pl:
                try: cur.execute(f"ALTER TABLE planificacao ADD COLUMN {c_nome} TEXT;")
                except: pass
'''

if "balanco_anual" not in app_code:
    app_code = app_code.replace(
        "if hasattr(conn, 'commit'): conn.commit()\n    conn.close()",
        codigo_tabelas + "\n        if hasattr(conn, 'commit'): conn.commit()\n    conn.close()"
    )

# Rotas do Balanço Anual e Relatório Dinâmico
rotas_balanco = '''
# -------------------------------------------------------------
# ROTAS: BALANÇO ANUAL DE ACTIVIDADES & QUESTIONAMENTOS
# -------------------------------------------------------------
@app.route('/secretaria/balanco', methods=['GET', 'POST'])
def secretaria_balanco():
    agora = datetime.now()
    ano_sel = request.args.get('ano', agora.year, type=int)

    if request.method == 'POST':
        fd = request.form
        ano_form = int(fd.get('ano_exercicio', ano_sel))

        # 1. Atualizar questionamentos individuais de cada atividade planificada
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

        # 2. Gravar os Constrangimentos Gerais e Perspectivas para o Relatório Oficial
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

    # Modo GET: carregar atividades e dados do balanço
    m = "%s" if DATABASE_URL else "?"
    planos = consultar_todos("SELECT * FROM planificacao ORDER BY id ASC")
    balanco = consultar_um(f"SELECT * FROM balanco_anual WHERE ano = {m}", (ano_sel,))
    
    return render_template('balanco_anual.html', ano_sel=ano_sel, planos=planos, balanco=balanco)
'''

if "def secretaria_balanco():" not in app_code:
    app_code = app_code.replace(
        "if __name__ == '__main__':",
        rotas_balanco + "\nif __name__ == '__main__':"
    )

# Atualizar a rota secretaria_relatorio_anual para puxar os dados reais do balanço
rota_relatorio_atualizada = '''@app.route('/secretaria/relatorio-anual')
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
        'tot_geral': (sub_m_ant_h + sub_m_nov_h) + (sub_m_ant_m + sub_m_nov_m)
    }

    tot_geral_dict = {
        'ant_h': sub_ant_h + sub_m_ant_h, 'ant_m': sub_ant_m + sub_m_ant_m, 'ant_tot': (sub_ant_h + sub_m_ant_h) + (sub_ant_m + sub_m_ant_m),
        'nov_h': sub_nov_h + sub_m_nov_h, 'nov_m': sub_nov_m + sub_m_nov_m, 'nov_tot': (sub_nov_h + sub_m_nov_h) + (sub_nov_m + sub_m_nov_m),
        'tot_h': (sub_ant_h + sub_nov_h) + (sub_m_ant_h + sub_m_nov_h),
        'tot_m': (sub_ant_m + sub_nov_m) + (sub_m_ant_m + sub_m_nov_m),
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

    # =========================================================================
    # LEITURA DOS CONSTRANGIMENTOS E PERSPECTIVAS DO BALANÇO ANUAL
    # =========================================================================
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

    # Se houver constrangimentos anotados diretamente nas atividades, juntar
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

    return render_template('relatorio_anual_modelo.html', rel=rel)'''

app_code = re.sub(
    r'@app\.route\(\'/secretaria/relatorio-anual\'\)[\s\S]*?return render_template\(\'relatorio_anual_modelo\.html\', rel=rel\)',
    rota_relatorio_atualizada,
    app_code
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_code)
print("✓ app.py: Rotas de Balanço Anual e integração de Constrangimentos/Perspectivas configuradas!")

# =============================================================================
# 2. CRIAR A TELA DO BALANÇO ANUAL E QUESTIONAMENTOS AUTOMÁTICOS
# =============================================================================
balanco_html = """<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Balanço Anual & Questionamentos - IEAD Chicuque</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-100 text-slate-800 font-sans min-h-screen p-6">

    <div class="max-w-5xl mx-auto space-y-6">

        <!-- CABEÇALHO -->
        <div class="bg-slate-900 text-white p-6 rounded-3xl shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
                <div class="inline-flex items-center gap-2 bg-indigo-500/20 text-indigo-300 px-3 py-1 rounded-full text-[10px] font-black uppercase mb-1 border border-indigo-400/30">
                    <span>🎯</span> GABINETE DA SECRETARIA • BALANÇO DE ENCERRAMENTO MINISTERIAL
                </div>
                <h1 class="text-2xl font-black">Balanço Anual & Questionamento de Metas ({{ ano_sel }})</h1>
                <p class="text-xs text-slate-400 mt-1">
                    Avalie o que foi realizado em cada actividade planificada e consolide os constrangimentos e perspectivas para o Relatório Oficial.
                </p>
            </div>
            <div class="flex gap-2">
                <a href="/?aba=secretaria" class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-xl text-xs font-bold shadow">
                    ← Voltar à Secretaria
                </a>
                <a href="/secretaria/relatorio-anual" target="_blank" class="px-4 py-2 bg-amber-500 hover:bg-amber-600 text-slate-950 font-black rounded-xl text-xs shadow flex items-center gap-1.5">
                    <span>📄</span><span>Ver Relatório Oficial</span>
                </a>
            </div>
        </div>

        <form action="/secretaria/balanco" method="POST" class="space-y-6 text-xs">
            <input type="hidden" name="ano_exercicio" value="{{ ano_sel }}">

            <!-- 1. MATRIZ DE QUESTIONAMENTOS AUTOMÁTICOS POR ACTIVIDADE -->
            <div class="bg-white p-6 rounded-3xl shadow-sm border border-slate-200 space-y-4">
                <div class="border-b pb-3 flex justify-between items-center">
                    <div>
                        <h2 class="text-base font-extrabold text-slate-900 flex items-center gap-2">
                            <span>📋</span> 1. Questionamento Automático por Actividade Planificada
                        </h2>
                        <p class="text-[11px] text-slate-500">O sistema gerou automaticamente este formulário para cada actividade registada na planificação.</p>
                    </div>
                    <span class="bg-indigo-100 text-indigo-900 px-3 py-1 rounded-full font-black text-xs">Total: {{ planos|length }} Actividades</span>
                </div>

                <div class="space-y-4">
                    {% for p in planos %}
                    <div class="p-4 rounded-2xl border border-slate-200 bg-slate-50/70 space-y-3">
                        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-200 pb-2">
                            <div>
                                <span class="text-[10px] bg-indigo-50 text-indigo-700 border border-indigo-200 px-2 py-0.5 rounded font-bold uppercase">{{ p.departamento }}</span>
                                <span class="font-extrabold text-slate-900 text-sm ml-2">{{ p.actividade }}</span>
                                <span class="text-[11px] text-slate-400 block sm:inline sm:ml-2">Data: {{ p.data_prevista }}</span>
                            </div>
                            <div class="flex items-center gap-2">
                                <label class="font-bold text-slate-600 text-[11px]">Situação:</label>
                                <select name="status_{{ p.id }}" class="h-8 px-2 border rounded-lg bg-white font-bold text-xs">
                                    <option value="Executado" {% if p.status == 'Executado' %}selected{% endif %}>✅ Executado</option>
                                    <option value="Parcial" {% if p.status == 'Parcial' %}selected{% endif %}>⚠️ Parcialmente Executado</option>
                                    <option value="Não Realizado" {% if p.status == 'Não Realizado' %}selected{% endif %}>❌ Não Realizado</option>
                                    <option value="Planeado" {% if p.status == 'Planeado' %}selected{% endif %}>⏳ Planeado</option>
                                </select>
                            </div>
                        </div>

                        <!-- PERGUNTAS ESPECÍFICAS DA ACTIVIDADE -->
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                            <div>
                                <label class="block font-bold text-rose-900 mb-1">
                                    ❓ Quais foram os constrangimentos e dificuldades nesta actividade?
                                </label>
                                <textarea name="dificuldades_{{ p.id }}" rows="2" placeholder="Ex: Falta de meios de transporte, chuva torrencial, falta de material didáctico..." class="w-full p-2.5 border rounded-xl bg-white font-medium">{{ p.dificuldades or '' }}</textarea>
                            </div>

                            <div>
                                <label class="block font-bold text-emerald-900 mb-1">
                                    🚀 Quais são as perspectivas e lições para o ano seguinte?
                                </label>
                                <textarea name="perspectivas_{{ p.id }}" rows="2" placeholder="Ex: Antecipar a recolha de fundos, realizar em dois turnos, adquirir equipamento próprio..." class="w-full p-2.5 border rounded-xl bg-white font-medium">{{ p.perspectivas or '' }}</textarea>
                            </div>
                        </div>

                        <!-- FEEDBACK E PARTICIPAÇÃO REAL POR GÉNERO -->
                        <div class="bg-white p-3 rounded-xl border border-slate-200 grid grid-cols-1 sm:grid-cols-5 gap-2 items-center">
                            <div class="sm:col-span-2">
                                <label class="block text-[10px] text-slate-500 font-bold mb-0.5">Resumo / Feedback do que foi feito:</label>
                                <input type="text" name="feedback_{{ p.id }}" value="{{ p.feedback or '' }}" placeholder="Breve nota de realização..." class="w-full h-8 px-2 border rounded-lg bg-slate-50">
                            </div>
                            <div>
                                <label class="block text-[10px] text-slate-500 font-bold">Homens</label>
                                <input type="number" name="part_h_{{ p.id }}" value="{{ p.participantes_homens or 0 }}" min="0" class="w-full h-8 px-2 border rounded text-center font-bold">
                            </div>
                            <div>
                                <label class="block text-[10px] text-slate-500 font-bold">Mulheres</label>
                                <input type="number" name="part_m_{{ p.id }}" value="{{ p.participantes_mulheres or 0 }}" min="0" class="w-full h-8 px-2 border rounded text-center font-bold">
                            </div>
                            <div>
                                <label class="block text-[10px] text-slate-500 font-bold">Jovens / Crianças</label>
                                <input type="number" name="part_j_{{ p.id }}" value="{{ (p.participantes_jovens or 0) + (p.participantes_criancas or 0) }}" min="0" class="w-full h-8 px-2 border rounded text-center font-bold">
                            </div>
                        </div>
                    </div>
                    {% else %}
                    <p class="text-center text-slate-400 py-6 italic">Nenhuma actividade registada no cronograma de planificação.</p>
                    {% endfor %}
                </div>
            </div>

            <!-- 2. CONSTRANGIMENTOS GERAIS DA IGREJA (ALIMENTA A SEÇÃO 8 DO RELATÓRIO) -->
            <div class="bg-white p-6 rounded-3xl shadow-sm border border-slate-200 space-y-4">
                <div class="border-b pb-2">
                    <h2 class="text-base font-extrabold text-slate-900 flex items-center gap-2">
                        <span>⚠️</span> 2. Constrangimentos / Dificuldades Gerais da Igreja (Seção 8 do Relatório Oficial)
                    </h2>
                    <p class="text-[11px] text-slate-500">Defina os principais constrangimentos institucionais para saírem impressos no relatório final:</p>
                </div>

                <div class="space-y-3">
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">Constrangimento 1:</label>
                        <input type="text" name="constrangimento_1" value="{{ balanco.constrangimento_1 if balanco else 'Necessidade premente de reabilitação e melhoria das infraestruturas dos locais de culto.' }}" class="w-full h-10 px-3 border-2 border-slate-200 rounded-xl bg-slate-50 focus:bg-white font-medium">
                    </div>
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">Constrangimento 2:</label>
                        <input type="text" name="constrangimento_2" value="{{ balanco.constrangimento_2 if balanco else 'Limitação de recursos e meios de locomoção para assistência pastoral regular a congregações periféricas.' }}" class="w-full h-10 px-3 border-2 border-slate-200 rounded-xl bg-slate-50 focus:bg-white font-medium">
                    </div>
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">Constrangimento 3:</label>
                        <input type="text" name="constrangimento_3" value="{{ balanco.constrangimento_3 if balanco else 'Escassez de material didáctico, bíblias e manuais de apoio para o discipulado e departamentos infantojuvenis.' }}" class="w-full h-10 px-3 border-2 border-slate-200 rounded-xl bg-slate-50 focus:bg-white font-medium">
                    </div>
                </div>
            </div>

            <!-- 3. PERSPECTIVAS E PLANOS PARA O ANO SEGUINTE (ALIMENTA A SEÇÃO 9 DO RELATÓRIO) -->
            <div class="bg-white p-6 rounded-3xl shadow-sm border border-slate-200 space-y-4">
                <div class="border-b pb-2">
                    <h2 class="text-base font-extrabold text-slate-900 flex items-center gap-2">
                        <span>🚀</span> 3. Perspectivas / Planos para o Ano Seguinte (Seção 9 do Relatório Oficial)
                    </h2>
                    <p class="text-[11px] text-slate-500">Defina as grandes metas e prioridades ministeriais para o ano subsequente:</p>
                </div>

                <div class="space-y-3">
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">Perspectiva / Meta 1:</label>
                        <input type="text" name="perspectiva_1" value="{{ balanco.perspectiva_1 if balanco else 'Intensificar o plano de evangelização e missões para a conquista de novas almas e plantação de congregações.' }}" class="w-full h-10 px-3 border-2 border-slate-200 rounded-xl bg-slate-50 focus:bg-white font-medium">
                    </div>
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">Perspectiva / Meta 2:</label>
                        <input type="text" name="perspectiva_2" value="{{ balanco.perspectiva_2 if balanco else 'Realizar cerimónias solenes de baptismo nas águas para os novos convertidos e jovens preparados na doutrina.' }}" class="w-full h-10 px-3 border-2 border-slate-200 rounded-xl bg-slate-50 focus:bg-white font-medium">
                    </div>
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">Perspectiva / Meta 3:</label>
                        <input type="text" name="perspectiva_3" value="{{ balanco.perspectiva_3 if balanco else 'Promover cursos contínuos de capacitação bíblico-doutrinária para diáconos, diaconisas e obreiros.' }}" class="w-full h-10 px-3 border-2 border-slate-200 rounded-xl bg-slate-50 focus:bg-white font-medium">
                    </div>
                </div>
            </div>

            <!-- BOTÃO DE GRAVAÇÃO -->
            <button type="submit" class="w-full py-4 bg-emerald-700 hover:bg-emerald-800 text-white font-black rounded-2xl shadow-xl cursor-pointer text-sm transition flex items-center justify-center gap-2">
                <span>💾</span><span>Gravar Balanço Anual & Actualizar Relatório Oficial 2026</span>
            </button>
        </form>

    </div>
</body>
</html>
"""

env = jinja2.Environment()
env.parse(balanco_html)

with open(os.path.join('templates', 'balanco_anual.html'), 'w', encoding='utf-8') as f:
    f.write(balanco_html)
print("✓ templates/balanco_anual.html compilado com sucesso!")

# =============================================================================
# 3. ATUALIZAR TEMPLATES/RELATORIO_ANUAL_MODELO.HTML (SEÇÕES 8 E 9 DINÂMICAS)
# =============================================================================
with open('templates/relatorio_anual_modelo.html', 'r', encoding='utf-8') as f:
    rel_html = f.read()

secao_8_e_9_nova = """        <!-- 8. CONSTRANGIMENTOS / DIFICULDADES (100% DINÂMICO DO BALANÇO ANUAL) -->
        <div class="space-y-1.5">
            <h2 class="font-black text-xs uppercase bg-slate-100 p-1.5 border border-slate-300 flex justify-between items-center">
                <span>8. CONSTRANGIMENTOS / DIFICULDADES</span>
                <span class="text-[9px] text-slate-500 font-normal">Alimentado pelo Balanço Anual</span>
            </h2>
            <ol class="list-decimal list-inside space-y-1 text-slate-800 text-xs pl-2">
                {% for c in rel.constrangimentos %}
                <li>{{ c }}</li>
                {% else %}
                <li class="italic text-slate-400">Nenhum constrangimento registado. Aceda ao módulo de Balanço Anual na Secretaria para preencher.</li>
                {% endfor %}
            </ol>
        </div>

        <!-- 9. PERSPECTIVAS / PLANOS PARA O ANO SEGUINTE (100% DINÂMICO DO BALANÇO ANUAL) -->
        <div class="space-y-1.5">
            <h2 class="font-black text-xs uppercase bg-slate-100 p-1.5 border border-slate-300 flex justify-between items-center">
                <span>9. PERSPECTIVAS / PLANOS PARA O ANO SEGUINTE</span>
                <span class="text-[9px] text-slate-500 font-normal">Alimentado pelo Balanço Anual</span>
            </h2>
            <ol class="list-decimal list-inside space-y-1 text-slate-800 text-xs pl-2">
                {% for p in rel.perspectivas %}
                <li>{{ p }}</li>
                {% else %}
                <li class="italic text-slate-400">Nenhuma perspectiva registada. Aceda ao módulo de Balanço Anual na Secretaria para definir as metas do próximo ano.</li>
                {% endfor %}
            </ol>
        </div>"""

# Substituir o bloco estático das seções 8 e 9
regex_8_9 = r'<!-- 8\. CONSTRANGIMENTOS / DIFICULDADES[\s\S]*?<!-- 10\. CONCLUSÃO'
rel_html = re.sub(regex_8_9, secao_8_e_9_nova + '\n\n        <!-- 10. CONCLUSÃO', rel_html)

env.parse(rel_html)
with open('templates/relatorio_anual_modelo.html', 'w', encoding='utf-8') as f:
    f.write(rel_html)
print("✓ templates/relatorio_anual_modelo.html: Seções 8 e 9 ligadas ao Balanço Anual!")

# =============================================================================
# 4. ADICIONAR BOTÃO DE BALANÇO ANUAL NA ABA SECRETARIA EM DASHBOARD.HTML
# =============================================================================
with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    dash_html = f.read()

bloco_botoes_secretaria = '''        <!-- ========================================================= -->
        <!-- ABA 2: SECRETARIA & PLANIFICAÇÃO                          -->
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
        </div>'''

regex_topo_sec = r'<!-- ========================================================= -->\s*<!-- ABA 2: SECRETARIA & PLANIFICAÇÃO[\s\S]*?<\/div>\s*<\/div>'
dash_html = re.sub(regex_topo_sec, bloco_botoes_secretaria, dash_html)

env.parse(dash_html)
with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(dash_html)
print("✓ templates/dashboard.html: Botão de Balanço Anual adicionado ao topo da Secretaria!")

print("=" * 80)
print(">>> INSTALAÇÃO CONCLUÍDA: MÓDULO DE BALANÇO ANUAL OPERACIONAL! <<<")
print("=" * 80)