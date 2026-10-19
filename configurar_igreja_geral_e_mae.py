import os
import re
import py_compile
import jinja2

print("=" * 80)
print("A CONFIGURAR SEPARAÇÃO: IGREJA GERAL (COM ZONAS) E IGREJA MÃE (SEM ZONAS)...")
print("=" * 80)

# =============================================================================
# 1. ATUALIZAR TEMPLATES/DASHBOARD.HTML
# =============================================================================
caminho_dash = os.path.join('templates', 'dashboard.html')
with open(caminho_dash, 'r', encoding='utf-8') as f:
    dash_html = f.read()

# A. Atualizar os 3 Cards no Topo de Finanças
cards_antigos = r'<div class="grid grid-cols-1 md:grid-cols-3 gap-5 mb-8 text-xs">[\s\S]*?<!-- 5 CARDS DE RESUMO GERAL'

cards_novos = """<div class="grid grid-cols-1 md:grid-cols-3 gap-5 mb-8 text-xs">
            <!-- CARD 1: IGREJA GERAL (COM AS ZONAS) -->
            <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200">
                <div class="font-extrabold text-slate-800 uppercase flex items-center justify-between border-b pb-2 mb-2">
                    <span>🏛️ Igreja Geral</span>
                    <span class="text-[10px] bg-indigo-100 text-indigo-900 px-2 py-0.5 rounded font-black">Inclui Zonas</span>
                </div>
                <div class="flex justify-between items-center text-emerald-700 font-bold">
                    <span>Entradas Gerais (c/ Zonas):</span>
                    <span>+ {{ "%.2f"|format(kpis.geral_in or 0) }} MT</span>
                </div>
                <div class="flex justify-between items-center text-rose-700 font-bold mt-1">
                    <span>Despesas Gerais:</span>
                    <span>- {{ "%.2f"|format(kpis.geral_out or 0) }} MT</span>
                </div>
                <div class="border-t pt-2 mt-2 flex justify-between items-center font-black text-slate-900">
                    <span>Saldo da Igreja Geral:</span>
                    <span>{{ "%.2f"|format((kpis.geral_in or 0) - (kpis.geral_out or 0)) }} MT</span>
                </div>
            </div>

            <!-- CARD 2: IGREJA MÃE (EXCLUSIVO TEMPLO SEDE - SEM AS ZONAS) -->
            <div class="bg-white p-5 rounded-2xl shadow-sm border border-amber-200 bg-amber-50/20">
                <div class="font-extrabold text-amber-950 uppercase flex items-center justify-between border-b border-amber-200 pb-2 mb-2">
                    <span>🏢 Igreja Mãe</span>
                    <span class="text-[10px] bg-amber-200 text-amber-950 px-2 py-0.5 rounded font-black">Sem as Zonas</span>
                </div>
                <div class="flex justify-between items-center text-emerald-700 font-bold">
                    <span>Entradas da Igreja Mãe:</span>
                    <span>+ {{ "%.2f"|format(kpis.mae_in or 0) }} MT</span>
                </div>
                <div class="flex justify-between items-center text-rose-700 font-bold mt-1">
                    <span>Despesas da Igreja Mãe:</span>
                    <span>- {{ "%.2f"|format(kpis.mae_out or 0) }} MT</span>
                </div>
                <div class="border-t border-amber-200 pt-2 mt-2 flex justify-between items-center font-black text-amber-950">
                    <span>Saldo da Igreja Mãe:</span>
                    <span>{{ "%.2f"|format((kpis.mae_in or 0) - (kpis.mae_out or 0)) }} MT</span>
                </div>
            </div>

            <!-- CARD 3: DEPARTAMENTOS -->
            <div class="bg-white p-5 rounded-2xl shadow-sm border border-indigo-200 bg-indigo-50/20">
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

        <!-- 5 CARDS DE RESUMO GERAL"""

dash_html = re.sub(cards_antigos, cards_novos, dash_html)

# B. Atualizar o Seletor e os Blocos de Lançamento em Tesouraria
seletor_antigo = r'<select id="destino_tipo" name="destino_tipo"[\s\S]*?<\/select>'
seletor_novo = """<select id="destino_tipo" name="destino_tipo" onchange="atualizarFormularioTesouraria()" class="w-full h-11 px-3 border-2 border-indigo-300 rounded-xl bg-indigo-50/50 font-black text-xs text-indigo-950">
                            <option value="Igreja Geral">🏛️ 1. Igreja Geral (Inclui Contribuições das Zonas)</option>
                            <option value="Igreja Mãe">🏢 2. Igreja Mãe (Exclusivo Templo Sede - Sem Zonas)</option>
                            <option value="Departamento">👥 3. Departamentos da Igreja</option>
                        </select>"""
dash_html = re.sub(seletor_antigo, seletor_novo, dash_html)

# C. Atualizar o Título das Caixas de Entrada e Saída
dash_html = dash_html.replace(
    'Receita da Igreja Local (Sede Chicuque)',
    'Receita da Igreja Geral (Envolve Zonas e Toda a Congregação)'
)
dash_html = dash_html.replace(
    'Valores Recebidos da Igreja Mãe / Sede',
    'Receita Exclusiva da Igreja Mãe (Templo Sede - Sem Zonas)'
)
dash_html = dash_html.replace(
    'Remessas Enviadas à Igreja Mãe (Sede)',
    'Despesas Próprias da Igreja Mãe (Templo Sede - Sem Zonas)'
)
dash_html = dash_html.replace(
    'Selecione o Tipo de Remessa / Envio *',
    'Classificação da Despesa da Igreja Mãe *'
)

# D. Atualizar a Tabela do Mapa de Reconciliação em Finanças
mapa_antigo_sede = r'<!-- SEDE \/ IGREJA MÃE -->[\s\S]*?<\/tr>'
mapa_novo_mae = """<!-- IGREJA MÃE (SEM AS ZONAS) -->
                        <tr class="border-b hover:bg-slate-50">
                            <td class="py-2.5 px-3 font-bold text-slate-900">
                                🏢 Igreja Mãe (Templo Sede)
                                <span class="block text-[10px] text-amber-700 font-normal">Exclusivo do templo central (sem incluir as Zonas)</span>
                            </td>
                            <td class="py-2.5 px-3 text-right font-bold text-emerald-700">+ {{ "%.2f"|format(kpis.mae_in or 0) }} MT</td>
                            <td class="py-2.5 px-3 text-right font-bold text-rose-700">- {{ "%.2f"|format(kpis.mae_out or 0) }} MT</td>
                            <td class="py-2.5 px-3 text-right font-black text-indigo-950">{{ "%.2f"|format((kpis.mae_in or 0) - (kpis.mae_out or 0)) }} MT</td>
                            <td class="py-2.5 px-3 text-center"><span class="px-2 py-0.5 rounded-full text-[9px] font-black bg-amber-100 text-amber-900">TEMPLO SEDE</span></td>
                        </tr>"""

dash_html = re.sub(mapa_antigo_sede, mapa_novo_mae, dash_html)

# Atualizar a linha de Ofertas Gerais para clarificar que é Igreja Geral (com Zonas)
dash_html = dash_html.replace(
    '🏛️ Ofertas de Culto & Despesas Gerais\n                                <span class="block text-[10px] text-slate-400 font-normal">Energia, água, ceia e manutenção local</span>',
    '🏛️ Igreja Geral (Envolve Zonas)\n                                <span class="block text-[10px] text-indigo-700 font-normal">Contribuições gerais e coletas que envolvem as Zonas</span>'
)

# Validar sintaxe Jinja2 do dashboard
env = jinja2.Environment()
env.parse(dash_html)
with open(caminho_dash, 'w', encoding='utf-8') as f:
    f.write(dash_html)
print("✓ templates/dashboard.html atualizado com sucesso!")

# =============================================================================
# 2. ATUALIZAR TEMPLATES/RELATORIO_FINANCEIRO.HTML
# =============================================================================
caminho_rel = os.path.join('templates', 'relatorio_financeiro.html')
with open(caminho_rel, 'r', encoding='utf-8') as f:
    rel_html = f.read()

# Substituir a linha de "Relações com a Igreja Mãe (Sede)" pelo novo formato
rel_html = rel_html.replace(
    '6. Relações com a Igreja Mãe (Sede)',
    '6. Igreja Mãe (Templo Sede - Sem Zonas)'
)
rel_html = rel_html.replace(
    'Subsídios recebidos da Sede vs. Dízimo dos dízimos remetido',
    'Movimentos financeiros exclusivos do templo sede (sem incluir as Zonas)'
)
rel_html = rel_html.replace(
    '2. Ofertas de Culto & Gerais\n',
    '2. Igreja Geral (Ofertas & Contribuições com as Zonas)\n'
)

env.parse(rel_html)
with open(caminho_rel, 'w', encoding='utf-8') as f:
    f.write(rel_html)
print("✓ templates/relatorio_financeiro.html atualizado com sucesso!")

# =============================================================================
# 3. ATUALIZAR APP.PY: GRAVAÇÃO E CLASSIFICAÇÃO SEM AMBIGUIDADES
# =============================================================================
caminho_app = 'app.py'
with open(caminho_app, 'r', encoding='utf-8') as f:
    app_text = f.read()

# Ajustar rotulagem na rota /financas/caixa/novo
bloco_antigo_caixa = """    if tipo == 'Entrada':
        categoria = "Igreja Mãe: " + fd.get('categoria_entrada_mae', 'Apoio') if destino_tipo == 'Igreja Mãe' else (f"Entrada: {depto}" if destino_tipo == 'Departamento' else fd.get('categoria', 'Dízimos'))
    else:
        categoria = "Igreja Mãe: " + fd.get('categoria_saida_mae', 'Dízimo dos Dízimos') if destino_tipo == 'Igreja Mãe' else (f"Saída: {depto}" if destino_tipo == 'Departamento' else fd.get('categoria_saida_geral', 'Despesa'))"""

bloco_novo_caixa = """    if tipo == 'Entrada':
        if destino_tipo == 'Igreja Mãe':
            categoria = "Igreja Mãe: " + fd.get('categoria_entrada_mae', 'Oferta Templo Sede').strip()
        elif destino_tipo == 'Departamento':
            categoria = f"Entrada: {depto}"
        else:
            categoria = "Igreja Geral: " + fd.get('categoria', 'Dízimos / Contribuições').strip()
    else:
        if destino_tipo == 'Igreja Mãe':
            categoria = "Igreja Mãe: " + fd.get('categoria_saida_mae', 'Despesa Templo Sede').strip()
        elif destino_tipo == 'Departamento':
            categoria = f"Saída: {depto}"
        else:
            categoria = "Igreja Geral: " + fd.get('categoria_saida_geral', 'Despesa Geral').strip()"""

if "categoria = \"Igreja Mãe: \"" in app_text:
    app_text = re.sub(
        r"if tipo == 'Entrada':[\s\S]*?else:\s*categoria = [^\n]*\n",
        bloco_novo_caixa + "\n",
        app_text
    )

# Atualizar linha 6 da função financas_relatorio_geral em app.py
app_text = app_text.replace(
    "'6. Relações com a Igreja Mãe (Sede)',\n            'Subsídios recebidos da Sede vs. Dízimo dos dízimos remetido'",
    "'6. Igreja Mãe (Templo Sede)',\n            'Movimentações exclusivas do templo central (sem incluir as Zonas)'"
)
app_text = app_text.replace(
    "'2. Ofertas de Culto & Gerais',\n            'Ofertas ordinárias de cultos (manutenção, energia, água)'",
    "'2. Igreja Geral (Com as Zonas)',\n            'Contribuições ordinárias e coletas que envolvem as Zonas'"
)

with open(caminho_app, 'w', encoding='utf-8') as f:
    f.write(app_text)

try:
    py_compile.compile(caminho_app, doraise=True)
    print("✓ app.py compilado sem nenhum erro!")
except Exception as e:
    print(f"Erro em app.py: {e}")
    exit(1)

print("=" * 80)
print(">>> ATUALIZAÇÃO CONCLUÍDA COM TOTAL SUCESSO! EXECUTE: py app.py <<<")
print("=" * 80)