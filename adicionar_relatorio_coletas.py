import os
import re
import py_compile
import subprocess
import jinja2

print("=" * 80)
print("A INTEGRAR PAINEL E RELATÓRIO DE COLETAS NO DASHBOARD FINANCEIRO...")
print("=" * 80)

caminho_app = 'app.py'
caminho_dash = os.path.join('templates', 'dashboard.html')

# =============================================================================
# 1. ATUALIZAR APP.PY: FILTRAR E PASSAR AS COLETAS PARA O DASHBOARD
# =============================================================================
with open(caminho_app, 'r', encoding='utf-8') as f:
    app_code = f.read()

# Consulta específica para coletas dos cultos e ofertas
query_coletas = '''
    # Consulta de Coletas e Ofertas Eclesiásticas para o Relatório Financeiro
    coletas_relatorio = consultar_todos("""
        SELECT * FROM caixa 
        WHERE tipo = 'Entrada' 
          AND (categoria LIKE '%Oferta%' OR categoria LIKE '%Dízimo%' OR categoria LIKE '%Coleta%' OR categoria LIKE '%Contribui%')
        ORDER BY data_operacao DESC, id DESC
    """)
    total_coletado = sum(float(c.get('valor', 0) or 0) for c in coletas_relatorio)
'''

if "coletas_relatorio" not in app_code:
    # Insere antes da renderização da página principal
    pos_render = app_code.find("return render_template('dashboard.html'")
    if pos_render != -1:
        app_code = app_code[:pos_render] + query_coletas + "\n    " + app_code[pos_render:]
        # Adicionar as variáveis no render_template
        app_code = app_code.replace(
            "return render_template('dashboard.html',",
            "return render_template('dashboard.html',\n                           coletas_relatorio=coletas_relatorio,\n                           total_coletado=total_coletado,",
            1
        )
        print("✓ Consulta e variáveis de Coletas integradas em app.py!")

with open(caminho_app, 'w', encoding='utf-8') as f:
    f.write(app_code)

try:
    py_compile.compile(caminho_app, doraise=True)
    print("✓ app.py validado e compilado com sucesso!")
except Exception as e:
    print(f"Erro em app.py: {e}")
    exit(1)

# =============================================================================
# 2. ATUALIZAR TEMPLATES/DASHBOARD.HTML (DENTRO DA ABA FINANCAS)
# =============================================================================
with open(caminho_dash, 'r', encoding='utf-8') as f:
    dash_html = f.read()

bloco_relatorio_coletas = """
        <!-- RELATÓRIO EXECUTIVO DE COLETAS E OFERTAS ECLESIÁSTICAS -->
        <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 mt-6 space-y-4">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-100 pb-4 gap-3">
                <div class="flex items-center gap-3">
                    <div class="p-2.5 bg-amber-50 text-amber-700 rounded-xl">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                    </div>
                    <div>
                        <h3 class="font-black text-sm text-slate-900 uppercase">Relatório Oficial de Coletas & Ofertas</h3>
                        <p class="text-xs text-slate-500">Discriminação das receitas recolhidas nos cultos, reuniões e zonas</p>
                    </div>
                </div>
                <div class="flex items-center gap-2">
                    <button onclick="window.print()" class="px-3.5 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-xl text-xs transition flex items-center gap-1.5 cursor-pointer">
                        <span>🖨️</span><span>Imprimir Boletim de Coleta</span>
                    </button>
                </div>
            </div>

            <!-- CARDS DE RESUMO DE ARRECADAÇÃO -->
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                <div class="p-4 bg-emerald-50/60 rounded-xl border border-emerald-200">
                    <span class="text-[10px] font-bold text-emerald-800 uppercase block">Total Arrecadado em Coletas</span>
                    <span class="text-2xl font-black text-emerald-900 mt-1 block">
                        {{ "%.2f"|format(total_coletado|default(0)|float) }} MZN
                    </span>
                    <span class="text-[10px] text-emerald-700">Ofertas, dízimos e coletas de culto</span>
                </div>
                <div class="p-4 bg-blue-50/60 rounded-xl border border-blue-200">
                    <span class="text-[10px] font-bold text-blue-800 uppercase block">Total de Atos de Coleta</span>
                    <span class="text-2xl font-black text-blue-900 mt-1 block">
                        {{ coletas_relatorio|length if coletas_relatorio is defined else 0 }} Lançamentos
                    </span>
                    <span class="text-[10px] text-blue-700">Registos efetuados pela tesouraria</span>
                </div>
                <div class="p-4 bg-amber-50/60 rounded-xl border border-amber-200">
                    <span class="text-[10px] font-bold text-amber-800 uppercase block">Última Coleta Registada</span>
                    <span class="text-lg font-black text-amber-900 mt-1 block truncate">
                        {% if coletas_relatorio and coletas_relatorio|length > 0 %}
                            {{ coletas_relatorio[0].data_operacao or 'Hoje' }} • {{ "%.2f"|format(coletas_relatorio[0].valor|float) }} MZN
                        {% else %}
                            Nenhum registo
                        {% endif %}
                    </span>
                    <span class="text-[10px] text-amber-700">Entrada mais recente</span>
                </div>
            </div>

            <!-- TABELA DETALHADA DAS COLETAS -->
            <div class="overflow-x-auto pt-2">
                <table class="w-full text-left text-xs border-collapse">
                    <thead>
                        <tr class="bg-slate-100 text-slate-700 font-bold uppercase text-[10px]">
                            <th class="p-2.5">Data da Operação</th>
                            <th class="p-2.5">Origem / Âmbito</th>
                            <th class="p-2.5">Classificação / Categoria</th>
                            <th class="p-2.5">Conta Receptora</th>
                            <th class="p-2.5 text-right">Valor Coletado</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% if coletas_relatorio and coletas_relatorio|length > 0 %}
                            {% for c in coletas_relatorio %}
                            <tr class="border-b hover:bg-slate-50 transition">
                                <td class="p-2.5 font-bold text-slate-800">{{ c.data_operacao or '—' }}</td>
                                <td class="p-2.5 text-slate-700">
                                    <span class="font-bold text-indigo-900 block">{{ c.ambito or 'Igreja Geral' }}</span>
                                    <span class="text-[10px] text-slate-400">{{ c.descricao or 'Culto Congregacional' }}</span>
                                </td>
                                <td class="p-2.5">
                                    <span class="px-2.5 py-1 rounded-full text-[10px] font-black bg-emerald-100 text-emerald-800">
                                        {{ c.categoria or 'Coleta' }}
                                    </span>
                                </td>
                                <td class="p-2.5 text-slate-600 font-medium text-[11px]">{{ c.conta or 'Caixa Físico' }}</td>
                                <td class="p-2.5 text-right font-black text-emerald-700 text-sm">
                                    + {{ "%.2f"|format(c.valor|float) }} MZN
                                </td>
                            </tr>
                            {% endfor %}
                        {% else %}
                            <tr>
                                <td colspan="5" class="p-6 text-center text-slate-400 italic">
                                    Nenhuma coleta ou oferta registada no período.
                                </td>
                            </tr>
                        {% endif %}
                    </tbody>
                </table>
            </div>
        </div>
"""

# Localizar o fim do conteúdo da aba de finanças para anexar o relatório
pos_aside_end = dash_html.find('</aside>')
pos_financas = dash_html.find("{% if aba_ativa == 'financas' %}", pos_aside_end)

if pos_financas != -1:
    # Achar o {% endif %} correspondente à aba financas
    pos_endif_financas = dash_html.find("{% endif %}", pos_financas)
    if "RELATÓRIO OFICIAL DE COLETAS" not in dash_html:
        dash_html = dash_html[:pos_endif_financas] + bloco_relatorio_coletas + "\n        " + dash_html[pos_endif_financas:]
        print("✓ Bloco do Relatório de Coletas inserido na aba Finanças com isolamento total!")
else:
    print("Aviso: Bloco aba_ativa == 'financas' não localizado em dashboard.html.")

env = jinja2.Environment()
env.parse(dash_html)
print("✓ templates/dashboard.html validado com ZERO erros no Jinja2!")

with open(caminho_dash, 'w', encoding='utf-8') as f:
    f.write(dash_html)

# =============================================================================
# 3. ENVIAR ATUALIZAÇÃO PARA O GITHUB & RENDER
# =============================================================================
print("=" * 80)
print("A ENVIAR ATUALIZAÇÃO PARA O GITHUB & RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "app.py", "templates/dashboard.html"], check=True)
subprocess.run(["git", "commit", "-m", "Feature: relatorio de coletas e ofertas com totalizadores e impressao no dashboard financeiro"], check=True)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("=" * 80)
print(">>> ATUALIZAÇÃO CONCLUÍDA COM TOTAL SUCESSO! <<<")
print("=" * 80)