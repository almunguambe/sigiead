import os
import re
import py_compile
import jinja2

print("=" * 80)
print("A ATUALIZAR CHICUQUE E A CRIAR RELATÓRIO ESTATÍSTICO DISTRITAL/PROVINCIAL...")
print("=" * 80)

os.makedirs('templates', exist_ok=True)
env = jinja2.Environment()

# =============================================================================
# 1. CRIAR TEMPLATES/RELATORIO_ESTATISTICO_AGREGADO.HTML (A4 / SEM FINANÇAS)
# =============================================================================
relatorio_estatistico_html = """<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SIGIEAD - Relatório Estatístico Agregado - {{ jurisdicao_titulo }}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @media print {
            body { background: white !important; font-size: 11px; }
            .no-print { display: none !important; }
            .page-container { border: none !important; box-shadow: none !important; margin: 0 !important; width: 100% !important; max-width: 100% !important; padding: 0 !important; }
        }
        table, th, td { border: 1px solid #cbd5e1 !important; }
    </style>
</head>
<body class="bg-slate-100 text-slate-900 font-sans p-4 sm:p-8">

    <div class="max-w-5xl mx-auto mb-6 flex justify-between items-center no-print">
        <a href="/?aba=estatistica_agregada" class="px-4 py-2 bg-slate-800 hover:bg-slate-900 text-white font-bold rounded-xl text-xs transition flex items-center gap-1.5 shadow">
            ← Voltar ao Painel
        </a>
        <button onclick="window.print()" class="px-5 py-2.5 bg-indigo-900 hover:bg-indigo-950 text-white font-black rounded-xl text-xs transition flex items-center gap-2 shadow-lg cursor-pointer">
            <span>🖨️</span><span>Imprimir / Baixar Mapa Estatístico A4 (PDF)</span>
        </button>
    </div>

    <div class="max-w-5xl mx-auto bg-white p-8 sm:p-12 rounded-3xl shadow-xl border border-slate-300 page-container space-y-6">

        <!-- CABEÇALHO OFICIAL COM LOGÓTIPO -->
        <div class="flex items-center gap-5 border-b-2 border-slate-800 pb-5">
            <div class="w-24 h-24 shrink-0 flex items-center justify-center p-1 border border-slate-200 rounded-2xl">
                {% include 'logo_ad.html' %}
            </div>
            <div class="flex-1">
                <span class="text-[10px] font-black uppercase text-indigo-900 tracking-wider block">
                    REPÚBLICA DE MOÇAMBIQUE • CONVENÇÃO NACIONAL
                </span>
                <h1 class="text-xl font-black uppercase text-slate-900 leading-tight">
                    IGREJA EVANGÉLICA ASSEMBLEIA DE DEUS
                </h1>
                <h2 class="text-sm font-extrabold text-indigo-900 uppercase mt-0.5">
                    DIRECÇÃO {{ nivel_nome|upper }}: {{ jurisdicao_titulo }}
                </h2>
                <p class="text-xs text-slate-600 font-medium">
                    Secretaria Executiva de Estatística e Membresia • Censo Eclesiástico Consolidado
                </p>
                <p class="text-[10px] text-slate-500 mt-1">
                    Âmbito: <b>{{ congregações_lista|length }} Congregações Registadas</b> (Sem interferência financeira)
                </p>
            </div>
            <div class="text-right text-[11px] text-slate-500 shrink-0 border-l pl-4 border-slate-200">
                <span class="block font-bold uppercase text-slate-700">SIGIEAD</span>
                <span>Estatística Geral</span>
                <span class="block font-black text-slate-900 mt-1">{{ data_emissao }}</span>
            </div>
        </div>

        <div class="text-center space-y-1">
            <h3 class="text-base font-black uppercase tracking-wider text-slate-900">
                MAPA ESTATÍSTICO GERAL CONSOLIDADO POR CONGREGAÇÃO
            </h3>
            <p class="text-xs text-slate-500 italic">
                Demonstrativo demográfico oficial de almas, frequência aos cultos e actos ministeriais
            </p>
        </div>

        <!-- QUADRO RESUMO GERAL DA JURISDIÇÃO -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center text-xs">
            <div class="p-3 bg-indigo-50 rounded-xl border border-indigo-200">
                <span class="text-[10px] uppercase font-bold text-indigo-800 block">Total de Almas</span>
                <span class="text-xl font-black text-indigo-950 mt-0.5 block">{{ totais.total_almas }}</span>
                <span class="text-[9px] text-slate-500">{{ totais.membros }} membros + {{ totais.convertidos }} novos</span>
            </div>
            <div class="p-3 bg-blue-50 rounded-xl border border-blue-200">
                <span class="text-[10px] uppercase font-bold text-blue-800 block">Homens vs Mulheres</span>
                <span class="text-lg font-black text-blue-950 mt-0.5 block">👨 {{ totais.homens }} | 👩 {{ totais.mulheres }}</span>
                <span class="text-[9px] text-slate-500">{{ totais.perc_homens }}% H • {{ totais.perc_mulheres }}% M</span>
            </div>
            <div class="p-3 bg-emerald-50 rounded-xl border border-emerald-200">
                <span class="text-[10px] uppercase font-bold text-emerald-800 block">Baptizados nas Águas</span>
                <span class="text-xl font-black text-emerald-950 mt-0.5 block">🌊 {{ totais.batizados }}</span>
                <span class="text-[9px] text-slate-500">{{ totais.nao_batizados }} em preparação</span>
            </div>
            <div class="p-3 bg-amber-50 rounded-xl border border-amber-200">
                <span class="text-[10px] uppercase font-bold text-amber-800 block">Actos Pastorais</span>
                <span class="text-lg font-black text-amber-950 mt-0.5 block">💍 {{ totais.casamentos }} | 🕊️ {{ totais.obitos }}</span>
                <span class="text-[9px] text-slate-500">Casamentos vs Óbitos</span>
            </div>
        </div>

        <!-- TABELA ANALÍTICA DISCRIMINADA POR IGREJA -->
        <div class="space-y-2">
            <div class="flex justify-between items-center">
                <h4 class="font-black text-xs uppercase tracking-wider text-slate-800">
                    Discriminação Demográfica por Cada Igreja / Congregação
                </h4>
                <span class="text-[10px] text-slate-500">Dados Actualizados em Tempo Real</span>
            </div>

            <table class="w-full text-left text-xs border-collapse">
                <thead>
                    <tr class="bg-slate-100 text-slate-800 font-extrabold uppercase text-[9px]">
                        <th class="p-2">Igreja / Congregação</th>
                        <th class="p-2">Pastor Dirigente</th>
                        <th class="p-2 text-center">Membros</th>
                        <th class="p-2 text-center">H / M</th>
                        <th class="p-2 text-center">Crianças</th>
                        <th class="p-2 text-center">Jovens</th>
                        <th class="p-2 text-center">Baptizados</th>
                        <th class="p-2 text-center">Novos Conv.</th>
                        <th class="p-2 text-center">Cultos</th>
                        <th class="p-2 text-center">Média Culto</th>
                    </tr>
                </thead>
                <tbody>
                    {% for cg in dados_igrejas %}
                    <tr class="hover:bg-slate-50">
                        <td class="p-2 font-bold text-slate-900">
                            {{ cg.nome }}
                            <span class="block text-[9px] text-slate-400 font-normal">{{ cg.bairro or cg.distrito }}</span>
                        </td>
                        <td class="p-2 text-slate-700 font-medium">{{ cg.pastor }}</td>
                        <td class="p-2 text-center font-black text-indigo-950">{{ cg.total_membros }}</td>
                        <td class="p-2 text-center text-[10px] font-bold text-slate-600">{{ cg.homens }} / {{ cg.mulheres }}</td>
                        <td class="p-2 text-center font-bold text-blue-700">{{ cg.criancas }}</td>
                        <td class="p-2 text-center font-bold text-indigo-700">{{ cg.jovens }}</td>
                        <td class="p-2 text-center font-bold text-emerald-700">🌊 {{ cg.batizados }}</td>
                        <td class="p-2 text-center font-bold text-amber-700">🌱 {{ cg.convertidos }}</td>
                        <td class="p-2 text-center text-slate-600">{{ cg.total_cultos }}</td>
                        <td class="p-2 text-center font-black bg-slate-50 text-indigo-900">{{ cg.media_culto }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
                <tfoot>
                    <tr class="bg-slate-200 font-black text-xs text-slate-950">
                        <td class="p-2 uppercase" colspan="2">TOTAL CONSOLIDADO ({{ nivel_nome|upper }}):</td>
                        <td class="p-2 text-center text-indigo-950">{{ totais.membros }}</td>
                        <td class="p-2 text-center text-[10px]">{{ totais.homens }} / {{ totais.mulheres }}</td>
                        <td class="p-2 text-center">{{ totais.criancas }}</td>
                        <td class="p-2 text-center">{{ totais.jovens }}</td>
                        <td class="p-2 text-center text-emerald-900">{{ totais.batizados }}</td>
                        <td class="p-2 text-center text-amber-900">{{ totais.convertidos }}</td>
                        <td class="p-2 text-center">{{ totais.total_cultos }}</td>
                        <td class="p-2 text-center bg-slate-300 text-indigo-950">{{ totais.media_culto_geral }}</td>
                    </tr>
                </tfoot>
            </table>
        </div>

        <!-- RADAR DE PONTUALIDADE E STATUS DE ENVIO -->
        <div class="space-y-2 pt-2">
            <h4 class="font-black text-xs uppercase tracking-wider text-slate-800">
                Estado de Regularidade & Pontualidade dos Lançamentos das Congregações
            </h4>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                {% for cg in dados_igrejas %}
                <div class="p-3 rounded-2xl border flex items-center justify-between {% if cg.dias_sem_lancamento <= 7 %}bg-emerald-50/60 border-emerald-300{% elif cg.dias_sem_lancamento <= 14 %}bg-amber-50/60 border-amber-300{% else %}bg-rose-50/60 border-rose-300{% endif %}">
                    <div>
                        <span class="font-bold text-slate-900 block truncate">{{ cg.nome }}</span>
                        <span class="text-[10px] text-slate-500">Último culto: {{ cg.ultimo_culto_data or 'Sem registo' }}</span>
                    </div>
                    <span class="px-2 py-0.5 rounded-full text-[9px] font-black {% if cg.dias_sem_lancamento <= 7 %}bg-emerald-200 text-emerald-900{% elif cg.dias_sem_lancamento <= 14 %}bg-amber-200 text-amber-900{% else %}bg-rose-200 text-rose-900{% endif %}">
                        {% if cg.dias_sem_lancamento <= 7 %}EM DIA{% elif cg.dias_sem_lancamento <= 14 %}ATENÇÃO{% else %}ATRASADA{% endif %}
                    </span>
                </div>
                {% endfor %}
            </div>
        </div>

        <!-- TERMOS DE CONFORMIDADE E ASSINATURAS -->
        <div class="pt-8 border-t-2 border-slate-800 space-y-6">
            <div class="grid grid-cols-2 gap-8 text-center text-xs pt-4">
                <div class="space-y-1">
                    <div class="border-b border-slate-400 pb-8"></div>
                    <span class="font-extrabold text-slate-900 block mt-1">Secretaria Executiva {{ nivel_nome|title }}</span>
                    <span class="text-[9px] text-slate-500 uppercase">Responsável pela Estatística e Censo</span>
                </div>
                <div class="space-y-1">
                    <div class="border-b border-slate-400 pb-8"></div>
                    <span class="font-extrabold text-slate-900 block mt-1">Pastor {{ supervisor_cargo }}</span>
                    <span class="text-[9px] text-slate-500 uppercase">Supervisão Geral / Visto Pastoral</span>
                </div>
            </div>
        </div>

    </div>

</body>
</html>
"""

env.parse(relatorio_estatistico_html)
with open('templates/relatorio_estatistico_agregado.html', 'w', encoding='utf-8') as f:
    f.write(relatorio_estatistico_html)
print("✓ templates/relatorio_estatistico_agregado.html criado com modelo oficial!")

# =============================================================================
# 2. ATUALIZAR APP.PY: RENOMEAR CHICUQUE E ADICIONAR LÓGICA ESTATÍSTICA
# =============================================================================
with open('app.py', 'r', encoding='utf-8') as f:
    app_text = f.read()

# A. Atualizar "Sede Regional de Chicuque" para "Igreja de Chicuque"
app_text = app_text.replace("Sede Regional de Chicuque", "Igreja de Chicuque")
app_text = app_text.replace("'Sede Regional de Chicuque'", "'Igreja de Chicuque'")

# B. Atualizar no banco de dados existente a congregação 1 para 'Igreja de Chicuque'
update_db_chicuque = """
    # Garantir nome correto de Chicuque como congregação com suas zonas
    executar_comando("UPDATE congregacoes SET nome = 'Igreja de Chicuque' WHERE id = 1 OR nome LIKE '%Sede Regional%'")
"""
if "UPDATE congregacoes SET nome = 'Igreja de Chicuque'" not in app_text:
    app_text = app_text.replace("inicializar_banco()\n", "inicializar_banco()\n" + update_db_chicuque + "\n")

# C. Rota para o Relatório Estatístico Agregado (Distrital / Provincial)
rota_estatistica_agregada = """
# =============================================================================
# RELATÓRIO ESTATÍSTICO AGREGADO DISTRITAL / PROVINCIAL (SEM FINANÇAS)
# =============================================================================
@app.route('/secretaria/estatistica-agregada')
def secretaria_estatistica_agregada():
    if not session.get('usuario_id'):
        return redirect('/login')

    u_id = session.get('usuario_id')
    user = consultar_um("SELECT * FROM usuarios_sistema WHERE id = ?", (u_id,))
    if not user:
        return redirect('/login')

    nivel = user.get('nivel', 'local')
    cid = session.get('congregacao_id', 1)
    cong_atual = consultar_um("SELECT * FROM congregacoes WHERE id = ?", (cid,)) or {'provincia': 'Inhambane', 'distrito': 'Maxixe (Cidade/Distrito)'}

    # Se for Provincial, busca todas as igrejas da província; se for Distrital ou Local, do distrito
    if nivel == 'provincial':
        prov = user.get('provincia') or cong_atual.get('provincia', 'Inhambane')
        igrejas = consultar_todos("SELECT * FROM congregacoes WHERE provincia = ? ORDER BY distrito, nome ASC", (prov,))
        jurisdicao_titulo = f"Província de {prov}"
        nivel_nome = "Provincial"
        supervisor_cargo = "Presidente Provincial"
    else:
        dist = user.get('distrito') or cong_atual.get('distrito', 'Maxixe (Cidade/Distrito)')
        igrejas = consultar_todos("SELECT * FROM congregacoes WHERE distrito = ? ORDER BY nome ASC", (dist,))
        jurisdicao_titulo = f"Distrito de {dist}"
        nivel_nome = "Distrital"
        supervisor_cargo = "Supervisor Distrital"

    if not igrejas:
        igrejas = [cong_atual]

    dados_igrejas = []
    tot_almas = 0
    tot_membros = 0
    tot_homens = 0
    tot_mulheres = 0
    tot_criancas = 0
    tot_jovens = 0
    tot_batizados = 0
    tot_nao_batizados = 0
    tot_convertidos = 0
    tot_casamentos = 0
    tot_obitos = 0
    tot_cultos = 0
    soma_medias = 0

    agora = datetime.now()

    for ig in igrejas:
        i_id = ig['id']
        membros_ig = consultar_todos("SELECT * FROM membros WHERE congregacao_id = ?", (i_id,))
        cultos_ig = consultar_todos("SELECT * FROM cultos WHERE congregacao_id = ? ORDER BY data_culto DESC", (i_id,))
        conv_ig = consultar_todos("SELECT * FROM novos_convertidos WHERE congregacao_id = ?", (i_id,))
        cas_ig = consultar_todos("SELECT * FROM casamentos WHERE congregacao_id = ?", (i_id,))
        ob_ig = consultar_todos("SELECT * FROM obitos WHERE congregacao_id = ?", (i_id,))

        h = len([m for m in membros_ig if str(m.get('genero') or '').lower() in ['masculino', 'homem', 'h']])
        mulh = len(membros_ig) - h
        cri = len([m for m in membros_ig if str(m.get('estado_civil') or '').lower() == 'criança' or 'esperança' in str(m.get('departamento') or '').lower()])
        jov = len([m for m in membros_ig if 'jov' in str(m.get('departamento') or '').lower() or 'jovem' in str(m.get('cargo') or '').lower()])
        bat = len([m for m in membros_ig if m.get('data_batismo')])
        
        pres_tot = sum([int(c.get('total_presentes') or 0) for c in cultos_ig])
        media_c = int(pres_tot / len(cultos_ig)) if cultos_ig else 0

        # Radar de atraso
        ultimo_culto_str = cultos_ig[0]['data_culto'] if cultos_ig and cultos_ig[0].get('data_culto') else None
        dias_sem_lancamento = 999
        if ultimo_culto_str:
            try:
                dt_c = datetime.strptime(ultimo_culto_str[:10], '%Y-%m-%d')
                dias_sem_lancamento = (agora - dt_c).days
            except:
                dias_sem_lancamento = 0

        dados_igrejas.append({
            'nome': ig['nome'],
            'pastor': ig.get('pastor_responsavel') or 'Pastor',
            'bairro': ig.get('bairro') or '',
            'distrito': ig.get('distrito') or '',
            'total_membros': len(membros_ig),
            'homens': h,
            'mulheres': mulh,
            'criancas': cri,
            'jovens': jov,
            'batizados': bat,
            'convertidos': len(conv_ig),
            'total_cultos': len(cultos_ig),
            'media_culto': media_c,
            'ultimo_culto_data': ultimo_culto_str,
            'dias_sem_lancamento': dias_sem_lancamento
        })

        tot_membros += len(membros_ig)
        tot_homens += h
        tot_mulheres += mulh
        tot_criancas += cri
        tot_jovens += jov
        tot_batizados += bat
        tot_convertidos += len(conv_ig)
        tot_casamentos += len(cas_ig)
        tot_obitos += len(ob_ig)
        tot_cultos += len(cultos_ig)
        soma_medias += media_c

    tot_almas = tot_membros + tot_convertidos
    tot_nao_batizados = tot_membros - tot_batizados
    media_culto_geral = int(soma_medias / len(dados_igrejas)) if dados_igrejas else 0

    totais = {
        'total_almas': tot_almas,
        'membros': tot_membros,
        'homens': tot_homens,
        'mulheres': tot_mulheres,
        'perc_homens': int((tot_homens / tot_membros * 100)) if tot_membros else 50,
        'perc_mulheres': int((tot_mulheres / tot_membros * 100)) if tot_membros else 50,
        'criancas': tot_criancas,
        'jovens': tot_jovens,
        'batizados': tot_batizados,
        'nao_batizados': tot_nao_batizados,
        'convertidos': tot_convertidos,
        'casamentos': tot_casamentos,
        'obitos': tot_obitos,
        'total_cultos': tot_cultos,
        'media_culto_geral': media_culto_geral
    }

    return render_template(
        'relatorio_estatistico_agregado.html',
        jurisdicao_titulo=jurisdicao_titulo,
        nivel_nome=nivel_nome,
        supervisor_cargo=supervisor_cargo,
        congregações_lista=igrejas,
        dados_igrejas=dados_igrejas,
        totais=totais,
        data_emissao=datetime.now().strftime('%d/%m/%Y às %H:%M')
    )
"""

if "/secretaria/estatistica-agregada" not in app_text:
    app_text = app_text.replace(
        "if __name__ == '__main__':",
        rota_estatistica_agregada + "\nif __name__ == '__main__':"
    )

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_text)

try:
    py_compile.compile('app.py', doraise=True)
    print("✓ app.py: Rota de estatística agregada compilada sem erros!")
except Exception as e:
    print(f"Erro em app.py: {e}")
    exit(1)

# =============================================================================
# 3. ATUALIZAR TEMPLATES/DASHBOARD.HTML (MENU LATERAL E ABA DE ESTATÍSTICA)
# =============================================================================
with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    dash_html = f.read()

# Substituir Chicuque textual
dash_html = dash_html.replace("Sede Regional de Chicuque", "Igreja de Chicuque")
dash_html = dash_html.replace("(Sede Chicuque)", "")

# Adicionar link para a Estatística Agregada no menu lateral para liderança e secretários
link_menu_agregado = """                <!-- RELATÓRIO ESTATÍSTICO AGREGADO DISTRITAL / PROVINCIAL (SEM FINANÇAS) -->
                {% if usuario_logado and (usuario_logado.perfil in ['admin', 'pastor', 'lideranca', 'secretario']) %}
                <a href="/?aba=estatistica_agregada" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'estatistica_agregada' %}bg-indigo-700 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                    <span>📊</span><span>Estatística Distrital / Prov.</span>
                </a>
                {% endif %}"""

if 'Estatística Distrital / Prov.' not in dash_html:
    dash_html = dash_html.replace(
        '<span>📋</span><span>2. Secretaria & Planos</span>\n                </a>',
        '<span>📋</span><span>2. Secretaria & Planos</span>\n                </a>\n' + link_menu_agregado
    )

# Adicionar a visualização da aba estatistica_agregada no dashboard.html
aba_conteudo_agregado = """        <!-- ========================================================= -->
        <!-- ABA: ESTATÍSTICA AGREGADA DISTRITAL / PROVINCIAL          -->
        <!-- ========================================================= -->
        {% if aba_ativa == 'estatistica_agregada' %}
        <div class="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white p-6 rounded-3xl shadow-xl mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
                <div class="inline-flex items-center gap-2 bg-indigo-500/20 text-indigo-300 px-3 py-1 rounded-full text-[10px] font-black uppercase mb-1 border border-indigo-400/30">
                    <span>📊</span> CENSO AGREGADO OFICIAL • ZERO FINANÇAS
                </div>
                <h2 class="text-2xl font-black">Estatística Eclesiástica Agregada por Congregação</h2>
                <p class="text-xs text-indigo-200 mt-0.5">Visão consolidada para Secretários Distritais e Provinciais • Monitoramento de Regularidade</p>
            </div>
            <div class="flex gap-3">
                <a href="/secretaria/estatistica-agregada" target="_blank" class="px-4 py-2.5 bg-amber-500 hover:bg-amber-600 text-slate-950 font-black rounded-xl text-xs shadow flex items-center gap-1.5 transition">
                    <span>📄</span><span>Emitir Mapa Estatístico A4 (PDF)</span>
                </a>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-5 mb-8 text-xs">
            <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 space-y-2">
                <span class="text-slate-500 text-[10px] font-bold uppercase block">Igrejas na Jurisdição</span>
                <span class="text-2xl font-black text-indigo-950 block">{{ congregacoes_todas|length }} Congregações</span>
                <p class="text-[10px] text-slate-400">Total de congregações cadastradas em acompanhamento contínuo.</p>
            </div>
            <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 space-y-2">
                <span class="text-slate-500 text-[10px] font-bold uppercase block">Frequência em Tempo Real</span>
                <span class="text-2xl font-black text-emerald-700 block">Sem Espera de Papel</span>
                <p class="text-[10px] text-slate-400">Os dados actualizam na hora em que a congregação lança o culto.</p>
            </div>
            <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 space-y-2">
                <span class="text-slate-500 text-[10px] font-bold uppercase block">Privacidade Financeira</span>
                <span class="text-2xl font-black text-slate-800 block">100% Estatístico</span>
                <p class="text-[10px] text-slate-400">As secretarias distritais e provinciais auditam unicamente o censo de almas.</p>
            </div>
        </div>

        <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 space-y-4 text-xs">
            <div class="flex justify-between items-center border-b pb-3">
                <h3 class="font-extrabold text-sm text-slate-900 uppercase">
                    Congregações em Acompanhamento & Acesso ao Relatório Detalhado
                </h3>
                <a href="/secretaria/estatistica-agregada" target="_blank" class="text-indigo-600 hover:text-indigo-800 font-bold">
                    Abrir Relatório Completo por Igreja →
                </a>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {% for cg in congregacoes_todas %}
                <div class="p-4 bg-slate-50 rounded-xl border border-slate-200 flex justify-between items-center">
                    <div>
                        <span class="font-bold text-slate-900 block">{{ cg.nome }}</span>
                        <span class="text-[10px] text-slate-500">{{ cg.distrito }} • Pr. {{ cg.pastor_responsavel }}</span>
                    </div>
                    <span class="bg-indigo-100 text-indigo-900 px-2.5 py-1 rounded-full font-black text-[10px]">Ativa</span>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}"""

if 'ABA: ESTATÍSTICA AGREGADA DISTRITAL' not in dash_html:
    dash_html = dash_html.replace(
        "{% if aba_ativa == 'dashboard' %}",
        aba_conteudo_agregado + "\n\n        {% if aba_ativa == 'dashboard' %}"
    )

env.parse(dash_html)
with open(caminho_dash, 'w', encoding='utf-8') as f:
    f.write(dash_html)
print("✓ templates/dashboard.html atualizado com aba de Estatística Agregada!")

# =============================================================================
# 4. LIMPAR TEMPLATES/PORTAL_ALUNO.HTML DE REFERÊNCIAS A "SEDE REGIONAL"
# =============================================================================
caminho_aluno = os.path.join('templates', 'portal_aluno.html')
if os.path.exists(caminho_aluno):
    with open(caminho_aluno, 'r', encoding='utf-8') as f:
        aluno_html = f.read()
    aluno_html = aluno_html.replace("Sede Regional de Chicuque", "Igreja de Chicuque")
    env.parse(aluno_html)
    with open(caminho_aluno, 'w', encoding='utf-8') as f:
        f.write(aluno_html)
    print("✓ templates/portal_aluno.html limpo de 'Sede Regional'!")

print("=" * 80)
print(">>> INSTALAÇÃO CONCLUÍDA COM TOTAL SUCESSO! EXECUTE: py app.py <<<")
print("=" * 80)