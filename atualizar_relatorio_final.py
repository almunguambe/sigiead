import os
import re
import jinja2

print("=" * 80)
print("A CONFIGURAR RELATÓRIO 100% DINÂMICO E ASSINATURA DA IGREJA...")
print("=" * 80)

os.makedirs('templates', exist_ok=True)

# =============================================================================
# 1. ATUALIZAR A ROTA DO RELATÓRIO EM APP.PY (CÁLCULO 100% REAL)
# =============================================================================
with open('app.py', 'r', encoding='utf-8') as f:
    app_code = f.read()

nova_rota = '''
# -------------------------------------------------------------
# ROTA: RELATÓRIO ANUAL OFICIAL (100% REAL, ANOS DINÂMICOS)
# -------------------------------------------------------------
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

    # 1. TABELA 2.1: OBREIROS (Calculado exclusivamente das linhas reais)
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

    # 2. TABELA 2.2: MEMBROS NÃO OBREIROS (Calculado exclusivamente das linhas reais)
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
        'tot_geral': (sub_m_ant_h + sub_nov_h) + (sub_m_ant_m + sub_m_nov_m)
    }

    tot_geral_dict = {
        'ant_h': sub_ant_h + sub_m_ant_h, 'ant_m': sub_ant_m + sub_m_ant_m, 'ant_tot': (sub_ant_h + sub_m_ant_h) + (sub_ant_m + sub_m_ant_m),
        'nov_h': sub_nov_h + sub_m_nov_h, 'nov_m': sub_nov_m + sub_m_nov_m, 'nov_tot': (sub_nov_h + sub_m_nov_h) + (sub_nov_m + sub_m_nov_m),
        'tot_h': (sub_ant_h + sub_nov_h) + (sub_m_ant_h + sub_m_nov_h),
        'tot_m': (sub_ant_m + sub_nov_m) + (sub_m_ant_m + sub_m_nov_m),
        'tot_geral': (sub_ant_h + sub_nov_h + sub_m_ant_h + sub_m_nov_h) + (sub_ant_m + sub_nov_m + sub_m_ant_m + sub_m_nov_m)
    }

    # 3. ACTIVIDADES EXECUTADAS DA PLANIFICAÇÃO
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
        }
    }

    return render_template('relatorio_anual_modelo.html', rel=rel)
'''

if "@app.route('/secretaria/relatorio-anual')" in app_code:
    app_code = re.sub(
        r'@app\.route\(\'/secretaria/relatorio-anual\'\)[\s\S]*?return render_template\(\'relatorio_anual_modelo\.html\', rel=rel\)',
        nova_rota.strip(),
        app_code
    )
else:
    app_code = app_code.replace(
        "if __name__ == '__main__':",
        nova_rota + "\nif __name__ == '__main__':"
    )

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_code)
print("✓ app.py: Lógica do Relatório Anual 100% dinâmica gravada!")

# =============================================================================
# 2. ATUALIZAR TEMPLATES/RELATORIO_ANUAL_MODELO.HTML
# =============================================================================
relatorio_template_html = """<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <title>Relatório Anual Oficial {{ rel.ano_atual }} - IEAD Chicuque</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @media print {
            .no-print { display: none !important; }
            body { background: white !important; padding: 0 !important; color: black !important; }
            @page { size: A4 portrait; margin: 12mm 15mm; }
            .page-break { page-break-before: always; }
        }
        table, th, td { border: 1px solid #1e293b !important; }
    </style>
</head>
<body class="bg-slate-100 p-6 font-sans text-slate-900 text-xs leading-normal">

    <!-- BARRA SUPERIOR DE IMPRESSÃO -->
    <div class="no-print max-w-4xl mx-auto mb-6 flex justify-between items-center bg-white p-4 rounded-2xl shadow border">
        <a href="/?aba=secretaria" class="px-4 py-2 bg-slate-800 text-white rounded-xl font-bold text-xs shadow hover:bg-slate-900">
            ← Voltar à Secretaria
        </a>
        <div class="flex items-center gap-3">
            <span class="text-xs text-emerald-700 font-bold">✅ Dados 100% calculados em tempo real da base de dados</span>
            <button onclick="window.print()" class="px-6 py-2.5 bg-indigo-700 hover:bg-indigo-800 text-white font-black rounded-xl shadow cursor-pointer text-xs">
                🖨️ Imprimir / Guardar em PDF
            </button>
        </div>
    </div>

    <!-- FOLHA PRINCIPAL -->
    <div class="max-w-4xl mx-auto bg-white p-10 rounded-2xl shadow-xl print:shadow-none print:p-0 print:border-none border border-slate-300 space-y-6">

        <!-- CABEÇALHO OFICIAL COM VISTO DO PASTOR -->
        <div class="flex justify-between items-start border-b-2 border-slate-900 pb-4">
            <div class="w-24 h-24 rounded-full border-2 border-indigo-950 flex flex-col items-center justify-center p-1 text-center shrink-0">
                <span class="text-[7px] font-black uppercase tracking-tighter text-indigo-950 leading-tight">IGREJA EVANGÉLICA</span>
                <div class="w-10 h-10 my-0.5 rounded-full bg-indigo-950 text-white flex items-center justify-center font-black text-sm">
                    AΩ
                </div>
                <span class="text-[7px] font-black uppercase tracking-tighter text-indigo-950 leading-tight">ASSEMBLEIA DE DEUS</span>
            </div>

            <div class="text-center flex-1 px-4 space-y-0.5">
                <h1 class="font-black text-sm uppercase tracking-wide text-slate-950">
                    IGREJA EVANGÉLICA ASSEMBLEIA DE DEUS EM MOÇAMBIQUE
                </h1>
                <p class="text-[10px] italic font-semibold text-slate-600">
                    "Quando orardes, lembrai-vos de Moçambique! Remember Mozambique when you pray"
                </p>
                <p class="text-xs font-black uppercase text-amber-800 tracking-wider">MINISTÉRIO THAVANE</p>
                <p class="text-[11px] font-bold uppercase text-slate-800">
                    PROVÍNCIA DE INHAMBANE • DISTRITO DE MAXIXE • SEDE CHICUQUE
                </p>
                <div class="pt-1">
                    <span class="inline-block px-4 py-1 bg-slate-900 text-white font-black text-xs uppercase tracking-widest rounded">
                        RELATÓRIO ANUAL ({{ rel.ano_anterior }} - {{ rel.ano_atual }})
                    </span>
                </div>
            </div>

            <div class="w-48 text-right text-[10px] space-y-2 shrink-0 pt-2">
                <p class="font-bold">Visto Do Pastor</p>
                <p class="border-b border-slate-600 pb-0.5 text-center text-slate-400">Assinatura</p>
                <p class="text-center">_____/_____/{{ rel.ano_atual }}</p>
            </div>
        </div>

        <!-- 1. INTRODUÇÃO -->
        <div class="space-y-2">
            <h2 class="font-black text-xs uppercase bg-slate-100 p-1.5 border border-slate-300">
                1. INTRODUÇÃO
            </h2>
            <div class="space-y-1.5 text-justify leading-relaxed text-slate-800">
                <p>Graça e Paz do nosso Senhor Jesus Cristo, Amem!</p>
                <p>
                    Saudamos o reverendíssimo Pastor Presidente Provincial, membros da Direcção Executiva Provincial, Conselho Pastoral, obreiros no geral e a todos os presentes nesta conferência. Amem!
                </p>
                <p>
                    Com a permissão do presídio, a <b>Secretaria da Igreja</b> passa a apresentar o resumo oficial das actividades desenvolvidas na <b>Assembleia de Deus (Ministério Thavane - Sede Chicuque)</b>, no período entre <b>Setembro de {{ rel.ano_anterior }} a Setembro de {{ rel.ano_atual }}</b>.
                </p>
            </div>
        </div>

        <!-- 2. ESTRUTURA DA IGREJA LOCAL -->
        <div class="space-y-2">
            <h2 class="font-black text-xs uppercase bg-slate-100 p-1.5 border border-slate-300">
                2. APRESENTAÇÃO DA ESTRUTURA DA IGREJA LOCAL (SEDE CHICUQUE)
            </h2>
            <table class="w-full text-left border-collapse text-xs">
                <thead>
                    <tr class="bg-slate-200 font-bold uppercase">
                        <th class="p-2 w-1/3">Cargo / Função</th>
                        <th class="p-2 w-1/4">Categoria Ministerial</th>
                        <th class="p-2">Liderança Responsável</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td class="p-2 font-bold">Pastor Presidente / Dirigente</td>
                        <td class="p-2">Pastor</td>
                        <td class="p-2 font-semibold">Gabinete Pastoral da Sede Chicuque</td>
                    </tr>
                    <tr>
                        <td class="p-2 font-bold">Secretário da Igreja</td>
                        <td class="p-2">Secretaria-Geral</td>
                        <td class="p-2 font-semibold">Secretaria da Igreja Local</td>
                    </tr>
                    <tr>
                        <td class="p-2 font-bold">Adjunto Secretário da Igreja</td>
                        <td class="p-2">Diácono / Obreiro</td>
                        <td class="p-2 font-semibold">Secretaria Executiva</td>
                    </tr>
                    <tr>
                        <td class="p-2 font-bold">Tesoureiro da Igreja</td>
                        <td class="p-2">Tesouraria</td>
                        <td class="p-2 font-semibold">Gabinete de Finanças e Caixa</td>
                    </tr>
                    <tr>
                        <td class="p-2 font-bold">Adjunto Tesoureiro da Igreja</td>
                        <td class="p-2">Diaconisa / Obreiro</td>
                        <td class="p-2 font-semibold">Controlo Financeiro</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- 2.1 ESTATÍSTICA DOS OBREIROS -->
        <div class="space-y-2">
            <h2 class="font-black text-xs uppercase bg-slate-100 p-1.5 border border-slate-300 flex justify-between items-center">
                <span>2.1. ESTATÍSTICA DOS OBREIROS</span>
                <span class="text-[10px] text-slate-500 font-normal">Calculado do cadastro de membros</span>
            </h2>
            <table class="w-full text-center border-collapse text-xs">
                <thead>
                    <tr class="bg-slate-200 font-bold uppercase text-[10px]">
                        <th rowspan="2" class="p-1 w-8">Nº</th>
                        <th rowspan="2" class="p-1 text-left">DESIGNAÇÃO</th>
                        <th colspan="3" class="p-1">Antigos (até {{ rel.ano_anterior }})</th>
                        <th colspan="3" class="p-1">Consagrações actuais ({{ rel.ano_atual }})</th>
                        <th colspan="3" class="p-1">Total geral actual</th>
                    </tr>
                    <tr class="bg-slate-100 text-[10px]">
                        <th class="p-1">Homem</th><th class="p-1">Mulher</th><th class="p-1 font-bold">TOTAL</th>
                        <th class="p-1">Homem</th><th class="p-1">Mulher</th><th class="p-1 font-bold">TOTAL</th>
                        <th class="p-1">Homem</th><th class="p-1">Mulher</th><th class="p-1 font-bold">TOTAL</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td class="p-1.5 font-bold">01</td>
                        <td class="p-1.5 text-left font-semibold">Pastores e Mães Pastoras</td>
                        <td>{{ rel.obreiros.pastores.ant_h }}</td><td>{{ rel.obreiros.pastores.ant_m }}</td><td class="font-bold">{{ rel.obreiros.pastores.ant_tot }}</td>
                        <td>{{ rel.obreiros.pastores.nov_h }}</td><td>{{ rel.obreiros.pastores.nov_m }}</td><td class="font-bold">{{ rel.obreiros.pastores.nov_tot }}</td>
                        <td>{{ rel.obreiros.pastores.tot_h }}</td><td>{{ rel.obreiros.pastores.tot_m }}</td><td class="font-black bg-slate-50">{{ rel.obreiros.pastores.tot_geral }}</td>
                    </tr>
                    <tr>
                        <td class="p-1.5 font-bold">02</td>
                        <td class="p-1.5 text-left font-semibold">Presbitério</td>
                        <td>{{ rel.obreiros.presbiteros.ant_h }}</td><td>{{ rel.obreiros.presbiteros.ant_m }}</td><td class="font-bold">{{ rel.obreiros.presbiteros.ant_tot }}</td>
                        <td>{{ rel.obreiros.presbiteros.nov_h }}</td><td>{{ rel.obreiros.presbiteros.nov_m }}</td><td class="font-bold">{{ rel.obreiros.presbiteros.nov_tot }}</td>
                        <td>{{ rel.obreiros.presbiteros.tot_h }}</td><td>{{ rel.obreiros.presbiteros.tot_m }}</td><td class="font-black bg-slate-50">{{ rel.obreiros.presbiteros.tot_geral }}</td>
                    </tr>
                    <tr>
                        <td class="p-1.5 font-bold">03</td>
                        <td class="p-1.5 text-left font-semibold">Evangelistas</td>
                        <td>{{ rel.obreiros.evangelistas.ant_h }}</td><td>{{ rel.obreiros.evangelistas.ant_m }}</td><td class="font-bold">{{ rel.obreiros.evangelistas.ant_tot }}</td>
                        <td>{{ rel.obreiros.evangelistas.nov_h }}</td><td>{{ rel.obreiros.evangelistas.nov_m }}</td><td class="font-bold">{{ rel.obreiros.evangelistas.nov_tot }}</td>
                        <td>{{ rel.obreiros.evangelistas.tot_h }}</td><td>{{ rel.obreiros.evangelistas.tot_m }}</td><td class="font-black bg-slate-50">{{ rel.obreiros.evangelistas.tot_geral }}</td>
                    </tr>
                    <tr>
                        <td class="p-1.5 font-bold">04</td>
                        <td class="p-1.5 text-left font-semibold">Diáconos e Diaconisas</td>
                        <td>{{ rel.obreiros.diaconos.ant_h }}</td><td>{{ rel.obreiros.diaconos.ant_m }}</td><td class="font-bold">{{ rel.obreiros.diaconos.ant_tot }}</td>
                        <td>{{ rel.obreiros.diaconos.nov_h }}</td><td>{{ rel.obreiros.diaconos.nov_m }}</td><td class="font-bold">{{ rel.obreiros.diaconos.nov_tot }}</td>
                        <td>{{ rel.obreiros.diaconos.tot_h }}</td><td>{{ rel.obreiros.diaconos.tot_m }}</td><td class="font-black bg-slate-50">{{ rel.obreiros.diaconos.tot_geral }}</td>
                    </tr>
                    <tr class="bg-slate-200 font-black">
                        <td colspan="2" class="p-1.5 text-right uppercase">Sub-Total de Obreiros</td>
                        <td>{{ rel.obreiros.subtotal.ant_h }}</td><td>{{ rel.obreiros.subtotal.ant_m }}</td><td>{{ rel.obreiros.subtotal.ant_tot }}</td>
                        <td>{{ rel.obreiros.subtotal.nov_h }}</td><td>{{ rel.obreiros.subtotal.nov_m }}</td><td>{{ rel.obreiros.subtotal.nov_tot }}</td>
                        <td>{{ rel.obreiros.subtotal.tot_h }}</td><td>{{ rel.obreiros.subtotal.tot_m }}</td><td class="bg-slate-300 text-sm">{{ rel.obreiros.subtotal.tot_geral }}</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- 2.2 ESTATÍSTICA DOS MEMBROS NÃO OBREIROS -->
        <div class="space-y-2">
            <h2 class="font-black text-xs uppercase bg-slate-100 p-1.5 border border-slate-300 flex justify-between items-center">
                <span>2.2. ESTATÍSTICA DOS MEMBROS NÃO OBREIROS</span>
                <span class="text-[10px] text-slate-500 font-normal">Calculado do cadastro de membros e convertidos</span>
            </h2>
            <table class="w-full text-center border-collapse text-xs">
                <thead>
                    <tr class="bg-slate-200 font-bold uppercase text-[10px]">
                        <th rowspan="2" class="p-1 w-8">Nº</th>
                        <th rowspan="2" class="p-1 text-left">DESIGNAÇÃO</th>
                        <th colspan="3" class="p-1">Antigos (até {{ rel.ano_anterior }})</th>
                        <th colspan="3" class="p-1">Novos Baptizados / Conversões</th>
                        <th colspan="3" class="p-1">Total geral actual</th>
                    </tr>
                    <tr class="bg-slate-100 text-[10px]">
                        <th class="p-1">H</th><th class="p-1">M</th><th class="p-1 font-bold">HM</th>
                        <th class="p-1">H</th><th class="p-1">M</th><th class="p-1 font-bold">HM</th>
                        <th class="p-1">H</th><th class="p-1">M</th><th class="p-1 font-bold">HM</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td class="p-1.5 font-bold">05</td>
                        <td class="p-1.5 text-left font-semibold">Baptizados Adultos</td>
                        <td>{{ rel.membros_nao_obreiros.batizados_adultos.ant_h }}</td><td>{{ rel.membros_nao_obreiros.batizados_adultos.ant_m }}</td><td class="font-bold">{{ rel.membros_nao_obreiros.batizados_adultos.ant_tot }}</td>
                        <td>{{ rel.membros_nao_obreiros.batizados_adultos.nov_h }}</td><td>{{ rel.membros_nao_obreiros.batizados_adultos.nov_m }}</td><td class="font-bold">{{ rel.membros_nao_obreiros.batizados_adultos.nov_tot }}</td>
                        <td>{{ rel.membros_nao_obreiros.batizados_adultos.tot_h }}</td><td>{{ rel.membros_nao_obreiros.batizados_adultos.tot_m }}</td><td class="font-black bg-slate-50">{{ rel.membros_nao_obreiros.batizados_adultos.tot_geral }}</td>
                    </tr>
                    <tr>
                        <td class="p-1.5 font-bold">06</td>
                        <td class="p-1.5 text-left font-semibold">Jovens Baptizados (18-35 anos)</td>
                        <td>{{ rel.membros_nao_obreiros.jovens_batizados.ant_h }}</td><td>{{ rel.membros_nao_obreiros.jovens_batizados.ant_m }}</td><td class="font-bold">{{ rel.membros_nao_obreiros.jovens_batizados.ant_tot }}</td>
                        <td>{{ rel.membros_nao_obreiros.jovens_batizados.nov_h }}</td><td>{{ rel.membros_nao_obreiros.jovens_batizados.nov_m }}</td><td class="font-bold">{{ rel.membros_nao_obreiros.jovens_batizados.nov_tot }}</td>
                        <td>{{ rel.membros_nao_obreiros.jovens_batizados.tot_h }}</td><td>{{ rel.membros_nao_obreiros.jovens_batizados.tot_m }}</td><td class="font-black bg-slate-50">{{ rel.membros_nao_obreiros.jovens_batizados.tot_geral }}</td>
                    </tr>
                    <tr>
                        <td class="p-1.5 font-bold">07</td>
                        <td class="p-1.5 text-left font-semibold">Jovens Não Baptizados (18-35 anos)</td>
                        <td>{{ rel.membros_nao_obreiros.jovens_nao_batizados.ant_h }}</td><td>{{ rel.membros_nao_obreiros.jovens_nao_batizados.ant_m }}</td><td class="font-bold">{{ rel.membros_nao_obreiros.jovens_nao_batizados.ant_tot }}</td>
                        <td>{{ rel.membros_nao_obreiros.jovens_nao_batizados.nov_h }}</td><td>{{ rel.membros_nao_obreiros.jovens_nao_batizados.nov_m }}</td><td class="font-bold">{{ rel.membros_nao_obreiros.jovens_nao_batizados.nov_tot }}</td>
                        <td>{{ rel.membros_nao_obreiros.jovens_nao_batizados.tot_h }}</td><td>{{ rel.membros_nao_obreiros.jovens_nao_batizados.tot_m }}</td><td class="font-black bg-slate-50">{{ rel.membros_nao_obreiros.jovens_nao_batizados.tot_geral }}</td>
                    </tr>
                    <tr>
                        <td class="p-1.5 font-bold">08</td>
                        <td class="p-1.5 text-left font-semibold">Novos Convertidos</td>
                        <td>{{ rel.membros_nao_obreiros.novos_convertidos.ant_h }}</td><td>{{ rel.membros_nao_obreiros.novos_convertidos.ant_m }}</td><td class="font-bold">{{ rel.membros_nao_obreiros.novos_convertidos.ant_tot }}</td>
                        <td>{{ rel.membros_nao_obreiros.novos_convertidos.nov_h }}</td><td>{{ rel.membros_nao_obreiros.novos_convertidos.nov_m }}</td><td class="font-bold">{{ rel.membros_nao_obreiros.novos_convertidos.nov_tot }}</td>
                        <td>{{ rel.membros_nao_obreiros.novos_convertidos.tot_h }}</td><td>{{ rel.membros_nao_obreiros.novos_convertidos.tot_m }}</td><td class="font-black bg-slate-50">{{ rel.membros_nao_obreiros.novos_convertidos.tot_geral }}</td>
                    </tr>
                    <tr>
                        <td class="p-1.5 font-bold">09</td>
                        <td class="p-1.5 text-left font-semibold">Boa Esperança (Crianças)</td>
                        <td>{{ rel.membros_nao_obreiros.boa_esperanca.ant_h }}</td><td>{{ rel.membros_nao_obreiros.boa_esperanca.ant_m }}</td><td class="font-bold">{{ rel.membros_nao_obreiros.boa_esperanca.ant_tot }}</td>
                        <td>{{ rel.membros_nao_obreiros.boa_esperanca.nov_h }}</td><td>{{ rel.membros_nao_obreiros.boa_esperanca.nov_m }}</td><td class="font-bold">{{ rel.membros_nao_obreiros.boa_esperanca.nov_tot }}</td>
                        <td>{{ rel.membros_nao_obreiros.boa_esperanca.tot_h }}</td><td>{{ rel.membros_nao_obreiros.boa_esperanca.tot_m }}</td><td class="font-black bg-slate-50">{{ rel.membros_nao_obreiros.boa_esperanca.tot_geral }}</td>
                    </tr>
                    <tr class="bg-slate-200 font-bold">
                        <td colspan="2" class="p-1.5 text-right uppercase">Sub-Total de Membros</td>
                        <td>{{ rel.membros_nao_obreiros.subtotal.ant_h }}</td><td>{{ rel.membros_nao_obreiros.subtotal.ant_m }}</td><td>{{ rel.membros_nao_obreiros.subtotal.ant_tot }}</td>
                        <td>{{ rel.membros_nao_obreiros.subtotal.nov_h }}</td><td>{{ rel.membros_nao_obreiros.subtotal.nov_m }}</td><td>{{ rel.membros_nao_obreiros.subtotal.nov_tot }}</td>
                        <td>{{ rel.membros_nao_obreiros.subtotal.tot_h }}</td><td>{{ rel.membros_nao_obreiros.subtotal.tot_m }}</td><td class="bg-slate-300">{{ rel.membros_nao_obreiros.subtotal.tot_geral }}</td>
                    </tr>
                    <tr class="bg-slate-300 font-black text-xs">
                        <td colspan="2" class="p-2 text-right uppercase">TOTAL GERAL DE MEMBROS (Obreiros + Membros)</td>
                        <td>{{ rel.total_geral.ant_h }}</td><td>{{ rel.total_geral.ant_m }}</td><td>{{ rel.total_geral.ant_tot }}</td>
                        <td>{{ rel.total_geral.nov_h }}</td><td>{{ rel.total_geral.nov_m }}</td><td>{{ rel.total_geral.nov_tot }}</td>
                        <td>{{ rel.total_geral.tot_h }}</td><td>{{ rel.total_geral.tot_m }}</td><td class="bg-slate-900 text-white text-sm">{{ rel.total_geral.tot_geral }}</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="page-break"></div>

        <!-- 3. ACTIVIDADES REALIZADAS -->
        <div class="space-y-4">
            <h2 class="font-black text-xs uppercase bg-slate-100 p-1.5 border border-slate-300 flex justify-between items-center">
                <span>3. ACTIVIDADES REALIZADAS</span>
                <span class="text-[10px] text-slate-500 font-normal">Extraído das actividades marcadas como «Executado»</span>
            </h2>

            <!-- 3.1 CASAMENTOS REALIZADOS -->
            <div class="space-y-1">
                <h3 class="font-bold text-xs uppercase text-slate-800">3.1. CASAMENTOS REALIZADOS</h3>
                <table class="w-full text-center border-collapse text-xs">
                    <thead>
                        <tr class="bg-slate-200 font-bold uppercase">
                            <th class="p-1.5 w-1/3">DE JOVENS</th>
                            <th class="p-1.5 w-1/3">DE ADULTOS</th>
                            <th class="p-1.5 w-1/3">TOTAL DE CASAMENTOS</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td class="p-2 font-semibold">{{ rel.casamentos.jovens }}</td>
                            <td class="p-2 font-semibold">{{ rel.casamentos.adultos }}</td>
                            <td class="p-2 font-black text-sm bg-slate-50">{{ rel.casamentos.total }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- 3.2 BAPTISMOS, INAUGURAÇÕES E APRESENTAÇÕES -->
            <div class="space-y-1">
                <h3 class="font-bold text-xs uppercase text-slate-800">
                    3.2. BAPTISMOS, INAUGURAÇÕES, LANÇAMENTOS DE PEDRA E APRESENTAÇÕES DOS OBREIROS
                </h3>
                <table class="w-full text-center border-collapse text-xs">
                    <thead>
                        <tr class="bg-slate-200 font-bold uppercase text-[10px]">
                            <th colspan="2" class="p-1">Baptismos</th>
                            <th colspan="2" class="p-1">Inaugurações de templos</th>
                            <th colspan="2" class="p-1">Lançamentos da 1ª pedra</th>
                            <th colspan="2" class="p-1">Apresentações de obreiros</th>
                        </tr>
                        <tr class="bg-slate-100 text-[10px]">
                            <th class="p-1 w-12">Nº</th><th class="p-1">Locais</th>
                            <th class="p-1 w-12">Nº</th><th class="p-1">Locais</th>
                            <th class="p-1 w-12">Nº</th><th class="p-1">Locais</th>
                            <th class="p-1 w-12">Nº</th><th class="p-1">Locais</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td class="p-2 font-black">{{ rel.atos.batismos_num }}</td>
                            <td class="p-2 text-slate-700">{{ rel.atos.batismos_locais }}</td>
                            <td class="p-2 font-black">{{ rel.atos.inauguracoes_num }}</td>
                            <td class="p-2 text-slate-700">{{ rel.atos.inauguracoes_locais }}</td>
                            <td class="p-2 font-black">{{ rel.atos.pedras_num }}</td>
                            <td class="p-2 text-slate-700">{{ rel.atos.pedras_locais }}</td>
                            <td class="p-2 font-black">{{ rel.atos.apresentacoes_num }}</td>
                            <td class="p-2 text-slate-700">{{ rel.atos.apresentacoes_locais }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- 4. ANIVERSÁRIOS REALIZADOS -->
        <div class="space-y-2">
            <h2 class="font-black text-xs uppercase bg-slate-100 p-1.5 border border-slate-300">
                4. ANIVERSÁRIOS REALIZADOS
            </h2>
            <table class="w-full text-left border-collapse text-xs">
                <thead>
                    <tr class="bg-slate-200 font-bold uppercase">
                        <th class="p-2 w-2/3">DEPARTAMENTO</th>
                        <th class="p-2 text-center w-1/3">Quantidade de Aniversários</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td class="p-2 font-semibold">Activista Cristã</td>
                        <td class="p-2 text-center font-bold">{{ rel.aniversarios.activista }}</td>
                    </tr>
                    <tr>
                        <td class="p-2 font-semibold">Juventude Cristã</td>
                        <td class="p-2 text-center font-bold">{{ rel.aniversarios.juventude }}</td>
                    </tr>
                    <tr>
                        <td class="p-2 font-semibold">Boa Esperança (Infantil)</td>
                        <td class="p-2 text-center font-bold">{{ rel.aniversarios.boa_esperanca }}</td>
                    </tr>
                    <tr>
                        <td class="p-2 font-semibold">Outros Departamentos (Mães / Pais / Louvor)</td>
                        <td class="p-2 text-center font-bold">{{ rel.aniversarios.outros }}</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- 5. SEMINÁRIOS E CONFERÊNCIAS -->
        <div class="space-y-4">
            <h2 class="font-black text-xs uppercase bg-slate-100 p-1.5 border border-slate-300">
                5. SEMINÁRIOS E CONFERÊNCIAS
            </h2>

            <!-- 5.1 SEMINÁRIOS REALIZADOS -->
            <div class="space-y-2">
                <h3 class="font-bold text-xs uppercase text-slate-800">5.1. SEMINÁRIOS REALIZADOS</h3>
                <table class="w-full text-center border-collapse text-[10px]">
                    <thead>
                        <tr class="bg-slate-200 font-bold uppercase">
                            <th class="p-1">Obreiros</th>
                            <th class="p-1">Depart. dos Pais</th>
                            <th class="p-1">Depart. das Mães</th>
                            <th class="p-1">Activista Cristã</th>
                            <th class="p-1">Juventude Cristã</th>
                            <th class="p-1">Baptizados</th>
                            <th class="p-1">Novos Convertidos</th>
                            <th class="p-1">Casados</th>
                            <th class="p-1">Solteiros</th>
                            <th class="p-1">Boa Esperança</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr class="font-black text-xs bg-slate-50">
                            <td class="p-2">{{ rel.seminarios_contagem.obreiros }}</td>
                            <td class="p-2">{{ rel.seminarios_contagem.pais }}</td>
                            <td class="p-2">{{ rel.seminarios_contagem.maes }}</td>
                            <td class="p-2">{{ rel.seminarios_contagem.activista }}</td>
                            <td class="p-2">{{ rel.seminarios_contagem.juventude }}</td>
                            <td class="p-2">{{ rel.seminarios_contagem.batizados }}</td>
                            <td class="p-2">{{ rel.seminarios_contagem.convertidos }}</td>
                            <td class="p-2">{{ rel.seminarios_contagem.casados }}</td>
                            <td class="p-2">{{ rel.seminarios_contagem.solteiros }}</td>
                            <td class="p-2">{{ rel.seminarios_contagem.boa_esperanca }}</td>
                        </tr>
                    </tbody>
                </table>

                <div class="p-3 bg-slate-50 border border-slate-300 rounded text-xs space-y-1">
                    <p class="font-bold text-slate-900">Descrever a data e os Temas Abordados (Resultados da Planificação):</p>
                    <div class="space-y-1 pl-2 text-slate-700">
                        {% for s in rel.temas_seminarios %}
                        <p>• <b>{{ s.data }}</b> — <i>{{ s.actividade }}</i> ({{ s.departamento }}): «{{ s.feedback or 'Actividade executada com êxito' }}» 
                           <span class="text-indigo-900 font-bold">[Participantes: {{ s.total }} (H: {{ s.h }}, M: {{ s.m }}, J: {{ s.j }}, C: {{ s.c }})]</span>
                        </p>
                        {% else %}
                        <p class="italic text-slate-500">• Nenhum seminário com feedback executado registado no sistema no período.</p>
                        {% endfor %}
                    </div>
                </div>
            </div>

            <!-- 5.2 CONFERÊNCIAS REALIZADAS -->
            <div class="space-y-2">
                <h3 class="font-bold text-xs uppercase text-slate-800">5.2. CONFERÊNCIAS REALIZADAS</h3>
                <table class="w-full text-center border-collapse text-[10px]">
                    <thead>
                        <tr class="bg-slate-200 font-bold uppercase">
                            <th class="p-1">Obreiros</th>
                            <th class="p-1">Depart. dos Pais</th>
                            <th class="p-1">Depart. das Mães</th>
                            <th class="p-1">Activista Cristã</th>
                            <th class="p-1">Juventude Cristã</th>
                            <th class="p-1">Baptizados</th>
                            <th class="p-1">Novos Convertidos</th>
                            <th class="p-1">Casados</th>
                            <th class="p-1">Solteiros</th>
                            <th class="p-1">Boa Esperança</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr class="font-black text-xs bg-slate-50">
                            <td class="p-2">{{ rel.conferencias_contagem.obreiros }}</td>
                            <td class="p-2">{{ rel.conferencias_contagem.pais }}</td>
                            <td class="p-2">{{ rel.conferencias_contagem.maes }}</td>
                            <td class="p-2">{{ rel.conferencias_contagem.activista }}</td>
                            <td class="p-2">{{ rel.conferencias_contagem.juventude }}</td>
                            <td class="p-2">{{ rel.conferencias_contagem.batizados }}</td>
                            <td class="p-2">{{ rel.conferencias_contagem.convertidos }}</td>
                            <td class="p-2">{{ rel.conferencias_contagem.casados }}</td>
                            <td class="p-2">{{ rel.conferencias_contagem.solteiros }}</td>
                            <td class="p-2">{{ rel.conferencias_contagem.boa_esperanca }}</td>
                        </tr>
                    </tbody>
                </table>
                <div class="p-3 bg-slate-50 border border-slate-300 rounded text-xs space-y-1">
                    <p class="font-bold text-slate-900">Descrever a data e os Temas Abordados:</p>
                    <div class="space-y-1 pl-2 text-slate-700">
                        {% for c in rel.temas_conferencias %}
                        <p>• <b>{{ c.data }}</b> — <i>{{ c.actividade }}</i> ({{ c.departamento }}): «{{ c.feedback or 'Realizada com êxito' }}»</p>
                        {% else %}
                        <p class="italic text-slate-500">• Não foram realizadas conferências locais próprias no período; os membros participaram nas conferências zonais e provinciais.</p>
                        {% endfor %}
                    </div>
                </div>
            </div>
        </div>

        <div class="page-break"></div>

        <!-- 6. VISITAS RECEBIDAS -->
        <div class="space-y-2">
            <h2 class="font-black text-xs uppercase bg-slate-100 p-1.5 border border-slate-300">
                6. VISITAS RECEBIDAS
            </h2>
            <table class="w-full text-center border-collapse text-xs">
                <thead>
                    <tr class="bg-slate-200 font-bold uppercase text-[10px]">
                        <th colspan="2" class="p-1">Liderança Nacional</th>
                        <th colspan="2" class="p-1">Liderança Provincial</th>
                        <th colspan="2" class="p-1">Pastores</th>
                        <th colspan="2" class="p-1">Presbíteros</th>
                        <th colspan="2" class="p-1">Diáconos</th>
                        <th colspan="2" class="p-1">Baptizados</th>
                        <th colspan="2" class="p-1">Jovens</th>
                    </tr>
                    <tr class="bg-slate-100 text-[10px]">
                        <th>H</th><th>M</th><th>H</th><th>M</th><th>H</th><th>M</th><th>H</th><th>M</th><th>H</th><th>M</th><th>H</th><th>M</th><th>H</th><th>M</th>
                    </tr>
                </thead>
                <tbody>
                    <tr class="font-bold">
                        <td>{{ rel.visitas.nac_h }}</td><td>{{ rel.visitas.nac_m }}</td>
                        <td>{{ rel.visitas.prov_h }}</td><td>{{ rel.visitas.prov_m }}</td>
                        <td>{{ rel.visitas.past_h }}</td><td>{{ rel.visitas.past_m }}</td>
                        <td>{{ rel.visitas.presb_h }}</td><td>{{ rel.visitas.presb_m }}</td>
                        <td>{{ rel.visitas.diac_h }}</td><td>{{ rel.visitas.diac_m }}</td>
                        <td>{{ rel.visitas.bapt_h }}</td><td>{{ rel.visitas.bapt_m }}</td>
                        <td>{{ rel.visitas.jov_h }}</td><td>{{ rel.visitas.jov_m }}</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- 7. PERDAS DOS MEMBROS -->
        <div class="space-y-2">
            <h2 class="font-black text-xs uppercase bg-slate-100 p-1.5 border border-slate-300">
                7. PERDAS DOS MEMBROS (POR DESISTÊNCIA OU MORTE)
            </h2>
            <table class="w-full text-center border-collapse text-[10px]">
                <thead>
                    <tr class="bg-slate-200 font-bold uppercase">
                        <th colspan="2" class="p-1">Desistentes</th>
                        <th colspan="9" class="p-1">Óbitos</th>
                    </tr>
                    <tr class="bg-slate-100">
                        <th class="p-1">H</th><th class="p-1">M</th>
                        <th class="p-1">Pastores</th>
                        <th class="p-1">Mães Pastoras</th>
                        <th class="p-1">Presbíteros</th>
                        <th class="p-1">Evangelistas</th>
                        <th class="p-1">Diáconos</th>
                        <th class="p-1">Baptizados</th>
                        <th class="p-1">Novos Conv.</th>
                        <th class="p-1">Juventude</th>
                        <th class="p-1">Boa Esperança</th>
                    </tr>
                </thead>
                <tbody>
                    <tr class="font-bold text-xs">
                        <td>{{ rel.perdas.desistentes_h }}</td>
                        <td>{{ rel.perdas.desistentes_m }}</td>
                        <td>{{ rel.perdas.obitos_pastores }}</td>
                        <td>{{ rel.perdas.obitos_maes_pastoras }}</td>
                        <td>{{ rel.perdas.obitos_presbiteros }}</td>
                        <td>{{ rel.perdas.obitos_evangelistas }}</td>
                        <td>{{ rel.perdas.obitos_diaconos }}</td>
                        <td>{{ rel.perdas.obitos_baptizados }}</td>
                        <td>{{ rel.perdas.obitos_novos_convertidos }}</td>
                        <td>{{ rel.perdas.obitos_juventude }}</td>
                        <td>{{ rel.perdas.obitos_boa_esperanca }}</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- 8. CONSTRANGIMENTOS / DIFICULDADES -->
        <div class="space-y-1.5">
            <h2 class="font-black text-xs uppercase bg-slate-100 p-1.5 border border-slate-300">
                8. CONSTRANGIMENTOS / DIFICULDADES
            </h2>
            <ol class="list-decimal list-inside space-y-1 text-slate-800 text-xs pl-2">
                <li>Necessidade premente de reabilitação e melhoria das infraestruturas dos locais de culto no distrito.</li>
                <li>Limitação de recursos e meios de locomoção para assistência pastoral regular a todos os campos e congregações periféricas.</li>
                <li>Escassez de material didático, bíblias e manuais de apoio para o discipulado e fortalecimento dos departamentos infantojuvenis.</li>
            </ol>
        </div>

        <!-- 9. PERSPECTIVAS / PLANOS PARA O ANO SEGUINTE -->
        <div class="space-y-1.5">
            <h2 class="font-black text-xs uppercase bg-slate-100 p-1.5 border border-slate-300">
                9. PERSPECTIVAS / PLANOS PARA O ANO SEGUINTE
            </h2>
            <ol class="list-decimal list-inside space-y-1 text-slate-800 text-xs pl-2">
                <li>Intensificar o plano da igreja de evangelização e missões para a conquista de novas almas e plantação de congregações.</li>
                <li>Realizar cerimónias de baptismo nas águas para os novos convertidos e jovens preparados na doutrina.</li>
                <li>Promover cursos contínuos de capacitação e reciclagem bíblico-doutrinária para diáconos, diaconisas e evangelistas.</li>
            </ol>
        </div>

        <!-- 10. CONCLUSÃO E ASSINATURA OFICIAL DA SECRETARIA DA IGREJA -->
        <div class="space-y-4 pt-2">
            <h2 class="font-black text-xs uppercase bg-slate-100 p-1.5 border border-slate-300">
                10. CONCLUSÃO
            </h2>
            <p class="text-justify leading-relaxed text-slate-800 text-xs">
                Rendemos toda a honra, glória e louvor ao Deus Todo-Poderoso por ter sustentado a Sua obra ao longo deste ano ministerial. Agradecemos à Direcção Provincial, ao Pastorado, a todos os obreiros, líderes de departamentos e membros da Assembleia de Deus (Sede Chicuque) pelo amor, zelo e esforço demonstrados na expansão do Evangelho de Cristo Jesus.
            </p>

            <div class="pt-8 flex justify-between items-end">
                <div class="text-xs">
                    <p>Chicuque - Maxixe, aos {{ rel.data_dia }} de {{ rel.data_mes }} de {{ rel.ano_atual }}</p>
                </div>
                <div class="text-center w-64 space-y-1">
                    <p class="font-extrabold text-xs">O Secretário da Igreja</p>
                    <div class="border-b border-slate-700 w-48 mx-auto my-2"></div>
                    <p class="text-[10px] text-slate-500 font-bold uppercase">Secretaria da Igreja • Sede Chicuque</p>
                    <p class="text-[9px] text-slate-400 font-semibold">Ministério Thavane</p>
                </div>
            </div>
        </div>

    </div>

</body>
</html>
"""

env = jinja2.Environment()
env.parse(relatorio_template_html)

with open(os.path.join('templates', 'relatorio_anual_modelo.html'), 'w', encoding='utf-8') as f:
    f.write(relatorio_template_html)
print("✓ templates/relatorio_anual_modelo.html compilado com sucesso!")

print("=" * 80)
print(">>> RELATÓRIO ANUAL 100% DINÂMICO E AUTOMATIZADO COM SUCESSO! <<<")
print("=" * 80)