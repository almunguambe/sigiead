import os
import re
import py_compile
import jinja2

print("=" * 80)
print("A CONFIGURAR MAPA FINANCEIRO (ENTROU, USOU, SOBROU) E RELATÓRIO A4...")
print("=" * 80)

os.makedirs('templates', exist_ok=True)
env = jinja2.Environment()

# =============================================================================
# 1. CRIAR TEMPLATES/RELATORIO_FINANCEIRO.HTML (DOCUMENTO OFICIAL A4 / PDF)
# =============================================================================
relatorio_html = """<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SIGIEAD - Balancete Financeiro Oficial - {{ congregacao.nome }}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @media print {
            body { background: white !important; font-size: 11px; }
            .no-print { display: none !important; }
            .print-break { page-break-before: always; }
            .page-container { border: none !important; box-shadow: none !important; margin: 0 !important; width: 100% !important; max-width: 100% !important; padding: 0 !important; }
        }
        table, th, td { border: 1px solid #cbd5e1 !important; }
    </style>
</head>
<body class="bg-slate-100 text-slate-900 font-sans p-4 sm:p-8">

    <!-- BOTÕES DE AÇÃO (OCULTOS NA IMPRESSÃO) -->
    <div class="max-w-4xl mx-auto mb-6 flex justify-between items-center no-print">
        <a href="/?aba=financas" class="px-4 py-2 bg-slate-800 hover:bg-slate-900 text-white font-bold rounded-xl text-xs transition flex items-center gap-1.5 shadow">
            ← Voltar ao Painel Financeiro
        </a>
        <button onclick="window.print()" class="px-5 py-2.5 bg-emerald-700 hover:bg-emerald-800 text-white font-black rounded-xl text-xs transition flex items-center gap-2 shadow-lg">
            <span>🖨️</span><span>Imprimir / Baixar Relatório em PDF (A4)</span>
        </button>
    </div>

    <!-- FOLHA A4 TIMBRADA -->
    <div class="max-w-4xl mx-auto bg-white p-8 sm:p-12 rounded-3xl shadow-xl border border-slate-300 page-container space-y-6">

        <!-- CABEÇALHO OFICIAL COM LOGO E DADOS DA IGREJA -->
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
                <h2 class="text-sm font-extrabold text-amber-800 uppercase mt-0.5">
                    {{ congregacao.nome }}
                </h2>
                <p class="text-xs text-slate-600 font-medium">
                    Jurisdição: Distrito de {{ congregacao.distrito }} • Província de {{ congregacao.provincia }}
                </p>
                <p class="text-[10px] text-slate-500 mt-1">
                    Pastor Dirigente: <b>{{ congregacao.pastor_responsavel or 'Pastor Responsável' }}</b>
                </p>
            </div>
            <div class="text-right text-[11px] text-slate-500 shrink-0 border-l pl-4 border-slate-200">
                <span class="block font-bold uppercase text-slate-700">SIGIEAD</span>
                <span>Balancete Oficial</span>
                <span class="block font-black text-slate-900 mt-1">{{ data_emissao }}</span>
            </div>
        </div>

        <div class="text-center space-y-1">
            <h3 class="text-base font-black uppercase tracking-wider text-slate-900">
                DEMONSTRAÇÃO DE PRESTAÇÃO DE CONTAS & BALANÇO POR RUBRICA
            </h3>
            <p class="text-xs text-slate-500 italic">
                Demonstrativo de Arrecadação, Aplicação de Recursos e Saldos Remanescentes
            </p>
        </div>

        <!-- 3 CARDS SÍNTESE DO DOCUMENTO -->
        <div class="grid grid-cols-3 gap-3 text-center text-xs">
            <div class="p-3 bg-emerald-50 rounded-xl border border-emerald-200">
                <span class="text-[10px] uppercase font-bold text-emerald-800 block">Total Arrecadado (Entradas)</span>
                <span class="text-lg font-black text-emerald-900 mt-0.5 block">+ {{ "%.2f"|format(total_entradas) }} MT</span>
            </div>
            <div class="p-3 bg-rose-50 rounded-xl border border-rose-200">
                <span class="text-[10px] uppercase font-bold text-rose-800 block">Total Aplicado (Saídas / Despesas)</span>
                <span class="text-lg font-black text-rose-900 mt-0.5 block">- {{ "%.2f"|format(total_saidas) }} MT</span>
            </div>
            <div class="p-3 bg-indigo-50 rounded-xl border border-indigo-200">
                <span class="text-[10px] uppercase font-bold text-indigo-800 block">Saldo Líquido Remanescente</span>
                <span class="text-lg font-black text-indigo-950 mt-0.5 block">{{ "%.2f"|format(saldo_geral) }} MT</span>
            </div>
        </div>

        <!-- TABELA PRINCIPAL: O QUE ENTROU, O QUE FOI USADO E O QUE SOBROU -->
        <div class="space-y-2">
            <div class="flex justify-between items-center">
                <h4 class="font-black text-xs uppercase tracking-wider text-slate-800">
                    1. Mapa Analítico por Linha de Entrada & Fundos Específicos
                </h4>
                <span class="text-[10px] text-slate-500">Valores em Meticais (MZN)</span>
            </div>

            <table class="w-full text-left text-xs border-collapse">
                <thead>
                    <tr class="bg-slate-100 text-slate-800 font-extrabold uppercase text-[10px]">
                        <th class="p-2.5">Linha de Entrada / Fundo da Igreja</th>
                        <th class="p-2.5 text-right">O que Entrou (+)</th>
                        <th class="p-2.5 text-right">O que foi Usado (-)</th>
                        <th class="p-2.5 text-right font-black">O que Sobrou (=)</th>
                        <th class="p-2.5 text-center w-24">Execução</th>
                    </tr>
                </thead>
                <tbody>
                    {% for linha in balancete_linhas %}
                    <tr class="hover:bg-slate-50">
                        <td class="p-2.5 font-bold text-slate-900">
                            {{ linha.nome }}
                            <span class="block text-[10px] text-slate-400 font-normal">{{ linha.descricao }}</span>
                        </td>
                        <td class="p-2.5 text-right font-extrabold text-emerald-700">
                            {{ "%.2f"|format(linha.entradas) }} MT
                        </td>
                        <td class="p-2.5 text-right font-extrabold text-rose-700">
                            {{ "%.2f"|format(linha.saidas) }} MT
                        </td>
                        <td class="p-2.5 text-right font-black {% if linha.saldo >= 0 %}text-indigo-950 bg-indigo-50/50{% else %}text-rose-800 bg-rose-50/50{% endif %}">
                            {{ "%.2f"|format(linha.saldo) }} MT
                        </td>
                        <td class="p-2.5 text-center font-bold text-slate-600 text-[10px]">
                            {{ linha.perc_uso }}%
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
                <tfoot>
                    <tr class="bg-slate-200 font-black text-xs text-slate-950">
                        <td class="p-2.5 uppercase">TOTALIZAÇÃO GERAL DOS RECURSOS:</td>
                        <td class="p-2.5 text-right text-emerald-800">+ {{ "%.2f"|format(total_entradas) }} MT</td>
                        <td class="p-2.5 text-right text-rose-800">- {{ "%.2f"|format(total_saidas) }} MT</td>
                        <td class="p-2.5 text-right text-indigo-950 text-sm">{{ "%.2f"|format(saldo_geral) }} MT</td>
                        <td class="p-2.5 text-center text-[11px]">{{ taxa_global }}%</td>
                    </tr>
                </tfoot>
            </table>
        </div>

        <!-- RECONCILIAÇÃO FÍSICA E BANCÁRIA -->
        <div class="space-y-2 pt-2">
            <h4 class="font-black text-xs uppercase tracking-wider text-slate-800">
                2. Onde Está o Dinheiro que Sobrou? (Reconciliação por Conta)
            </h4>
            <div class="grid grid-cols-2 gap-4 text-xs">
                <div class="p-4 bg-slate-50 rounded-2xl border border-slate-200 space-y-1.5">
                    <div class="flex justify-between items-center">
                        <span class="font-bold text-slate-700">💵 Caixa Físico (Numerário em Cofre):</span>
                        <b class="text-sm text-slate-950">{{ "%.2f"|format(saldo_caixa_fisico) }} MT</b>
                    </div>
                    <div class="flex justify-between text-[10px] text-slate-500">
                        <span>Total Entrado: + {{ "%.2f"|format(in_fisico) }} MT</span>
                        <span>Total Pago: - {{ "%.2f"|format(out_fisico) }} MT</span>
                    </div>
                </div>

                <div class="p-4 bg-slate-50 rounded-2xl border border-slate-200 space-y-1.5">
                    <div class="flex justify-between items-center">
                        <span class="font-bold text-slate-700">🏦 Conta Bancária / Conta Móvel:</span>
                        <b class="text-sm text-blue-900">{{ "%.2f"|format(saldo_banco) }} MT</b>
                    </div>
                    <div class="flex justify-between text-[10px] text-slate-500">
                        <span>Total Depositado: + {{ "%.2f"|format(in_banco) }} MT</span>
                        <span>Total Levantado/Gasto: - {{ "%.2f"|format(out_banco) }} MT</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- DISCRIMINATIVO RECENTE DAS ENTRADAS E SAÍDAS -->
        <div class="space-y-2 pt-2">
            <h4 class="font-black text-xs uppercase tracking-wider text-slate-800">
                3. Resumo por Categoria de Operação
            </h4>
            <div class="grid grid-cols-2 gap-4 text-xs">
                <div class="border rounded-2xl p-3 bg-emerald-50/30">
                    <span class="font-bold text-emerald-950 uppercase text-[10px] block mb-2 border-b pb-1">
                        Fontes de Receita Registadas:
                    </span>
                    <ul class="space-y-1">
                        {% for cat, val in categorias_entradas.items() %}
                        <li class="flex justify-between py-0.5">
                            <span class="text-slate-600">{{ cat }}:</span>
                            <b class="text-emerald-800">+ {{ "%.2f"|format(val) }} MT</b>
                        </li>
                        {% else %}
                        <li class="text-slate-400 italic">Sem entradas no período.</li>
                        {% endfor %}
                    </ul>
                </div>

                <div class="border rounded-2xl p-3 bg-rose-50/30">
                    <span class="font-bold text-rose-950 uppercase text-[10px] block mb-2 border-b pb-1">
                        Aplicações e Despesas Pagas:
                    </span>
                    <ul class="space-y-1">
                        {% for cat, val in categorias_saidas.items() %}
                        <li class="flex justify-between py-0.5">
                            <span class="text-slate-600">{{ cat }}:</span>
                            <b class="text-rose-800">- {{ "%.2f"|format(val) }} MT</b>
                        </li>
                        {% else %}
                        <li class="text-slate-400 italic">Sem despesas registadas.</li>
                        {% endfor %}
                    </ul>
                </div>
            </div>
        </div>

        <!-- TERMOS DE CONFORMIDADE E ASSINATURAS OFICIAIS -->
        <div class="pt-8 border-t-2 border-slate-800 space-y-6">
            <p class="text-[10px] text-slate-500 text-justify leading-relaxed">
                Certificamos que as demonstrações acima refletem com fidelidade e transparência todos os valores arrecadados, despesas e remessas efetuadas pela congregação, sob observância dos estatutos da Igreja Evangélica Assembleia de Deus e das normas de gestão financeira eclesiástica.
            </p>

            <div class="grid grid-cols-3 gap-6 text-center text-xs pt-4">
                <div class="space-y-1">
                    <div class="border-b border-slate-400 pb-8"></div>
                    <span class="font-extrabold text-slate-900 block mt-1">Tesouraria da Igreja</span>
                    <span class="text-[9px] text-slate-500 uppercase">Responsável pelo Caixa</span>
                </div>
                <div class="space-y-1">
                    <div class="border-b border-slate-400 pb-8"></div>
                    <span class="font-extrabold text-slate-900 block mt-1">Comissão de Contas</span>
                    <span class="text-[9px] text-slate-500 uppercase">Conselho Fiscal / Auditoria</span>
                </div>
                <div class="space-y-1">
                    <div class="border-b border-slate-400 pb-8"></div>
                    <span class="font-extrabold text-slate-900 block mt-1">{{ congregacao.pastor_responsavel or 'Pastor Dirigente' }}</span>
                    <span class="text-[9px] text-slate-500 uppercase">Pastor Dirigente / Visto</span>
                </div>
            </div>
        </div>

    </div>

</body>
</html>
"""

env.parse(relatorio_html)
with open('templates/relatorio_financeiro.html', 'w', encoding='utf-8') as f:
    f.write(relatorio_html)
print("✓ templates/relatorio_financeiro.html criado com modelo A4 e termos oficiais!")

# =============================================================================
# 2. ATUALIZAR APP.PY COM A ROTA /financas/relatorio-geral E CÁLCULO ANALÍTICO
# =============================================================================
with open('app.py', 'r', encoding='utf-8') as f:
    app_text = f.read()

rota_relatorio_analitico = """
# =============================================================================
# RELATÓRIO FINANCEIRO OFICIAL (A4 / IMPRESSÃO / PDF)
# =============================================================================
@app.route('/financas/relatorio-geral')
def financas_relatorio_geral():
    if not session.get('usuario_id') and not session.get('aluno_id'):
        return redirect('/login')

    perfil = session.get('usuario_perfil', '')
    if perfil == 'secretario':
        return redirect('/?aba=membros')

    cid = session.get('congregacao_id', 1)
    cong = consultar_um("SELECT * FROM congregacoes WHERE id = ?", (cid,)) or {
        'id': 1, 'nome': 'Assembleia de Deus', 'distrito': 'Maxixe (Cidade/Distrito)', 'provincia': 'Inhambane', 'pastor_responsavel': 'Pastor Dirigente'
    }

    movimentos = consultar_todos("SELECT * FROM caixa WHERE congregacao_id = ? ORDER BY data_movimento ASC, id ASC", (cid,))

    # Classificação analítica por fundos/linhas de entrada
    def calcular_linha(nome, desc, filtro_in, filtro_out):
        e = sum([float(m.get('valor') or 0) for m in movimentos if m.get('tipo') == 'Entrada' and filtro_in(m)])
        s = sum([float(m.get('valor') or 0) for m in movimentos if m.get('tipo') == 'Saída' and filtro_out(m)])
        sobra = e - s
        perc = int((s / e * 100)) if e > 0 else 0
        return {'nome': nome, 'descricao': desc, 'entradas': e, 'saidas': s, 'saldo': sobra, 'perc_uso': perc}

    linhas = [
        calcular_linha(
            '1. Dízimos Ministeriais',
            'Fidelidade dos membros e obreiros (receita nuclear)',
            lambda m: 'dízimo' in str(m.get('categoria', '')).lower() or 'dizimo' in str(m.get('categoria', '')).lower(),
            lambda m: 'vogal' in str(m.get('categoria', '')).lower() or 'pastoral' in str(m.get('descricao', '')).lower()
        ),
        calcular_linha(
            '2. Ofertas de Culto & Gerais',
            'Ofertas ordinárias de cultos (manutenção, energia, água)',
            lambda m: 'oferta' in str(m.get('categoria', '')).lower() and 'miss' not in str(m.get('categoria', '')).lower() and 'depto' not in str(m.get('categoria', '')).lower(),
            lambda m: any(k in str(m.get('categoria', '')).lower() or k in str(m.get('descricao', '')).lower() for k in ['energia', 'credelec', 'água', 'agua', 'ceia', 'limpeza', 'geral'])
        ),
        calcular_linha(
            '3. Fundo de Missões & Evangelismo',
            'Ofertas voluntárias para expansão e obreiros do campo',
            lambda m: 'miss' in str(m.get('categoria', '')).lower() or 'evangel' in str(m.get('categoria', '')).lower(),
            lambda m: 'miss' in str(m.get('categoria', '')).lower() or 'evangel' in str(m.get('categoria', '')).lower() or 'campo' in str(m.get('descricao', '')).lower()
        ),
        calcular_linha(
            '4. Campanha de Construção & Obras',
            'Arrecadação de cimento, tijolos e expansão física',
            lambda m: any(k in str(m.get('categoria', '')).lower() for k in ['constru', 'obra', 'cimento', 'tijolo']),
            lambda m: any(k in str(m.get('categoria', '')).lower() or k in str(m.get('descricao', '')).lower() for k in ['constru', 'obra', 'cimento', 'pedreiro', 'material'])
        ),
        calcular_linha(
            '5. Departamentos da Igreja',
            'Fundos próprios: Juventude, Mães, EBD, Crianças',
            lambda m: m.get('destino_tipo') == 'Departamento' or 'depto' in str(m.get('categoria', '')).lower(),
            lambda m: m.get('destino_tipo') == 'Departamento' or 'depto' in str(m.get('categoria', '')).lower()
        ),
        calcular_linha(
            '6. Relações com a Igreja Mãe (Sede)',
            'Subsídios recebidos da Sede vs. Dízimo dos dízimos remetido',
            lambda m: m.get('destino_tipo') == 'Igreja Mãe' or 'mãe' in str(m.get('categoria', '')).lower(),
            lambda m: m.get('destino_tipo') == 'Igreja Mãe' or 'mãe' in str(m.get('categoria', '')).lower() or 'remessa' in str(m.get('categoria', '')).lower()
        )
    ]

    tot_in = sum([float(m.get('valor') or 0) for m in movimentos if m.get('tipo') == 'Entrada'])
    tot_out = sum([float(m.get('valor') or 0) for m in movimentos if m.get('tipo') == 'Saída'])
    saldo_tot = tot_in - tot_out
    taxa_global = int((tot_out / tot_in * 100)) if tot_in > 0 else 0

    in_f = sum([float(m.get('valor') or 0) for m in movimentos if m.get('tipo') == 'Entrada' and 'banco' not in str(m.get('conta', '')).lower()])
    out_f = sum([float(m.get('valor') or 0) for m in movimentos if m.get('tipo') == 'Saída' and 'banco' not in str(m.get('conta', '')).lower()])
    in_b = sum([float(m.get('valor') or 0) for m in movimentos if m.get('tipo') == 'Entrada' and 'banco' in str(m.get('conta', '')).lower()])
    out_b = sum([float(m.get('valor') or 0) for m in movimentos if m.get('tipo') == 'Saída' and 'banco' in str(m.get('conta', '')).lower()])

    cat_in = {}
    cat_out = {}
    for m in movimentos:
        cat = m.get('categoria') or 'Geral'
        v = float(m.get('valor') or 0)
        if m.get('tipo') == 'Entrada':
            cat_in[cat] = cat_in.get(cat, 0.0) + v
        else:
            cat_out[cat] = cat_out.get(cat, 0.0) + v

    return render_template(
        'relatorio_financeiro.html',
        congregacao=cong,
        balancete_linhas=linhas,
        total_entradas=tot_in,
        total_saidas=tot_out,
        saldo_geral=saldo_tot,
        taxa_global=taxa_global,
        saldo_caixa_fisico=in_f - out_f,
        saldo_banco=in_b - out_b,
        in_fisico=in_f, out_fisico=out_f,
        in_banco=in_b, out_banco=out_b,
        categorias_entradas=cat_in,
        categorias_saidas=cat_out,
        data_emissao=datetime.now().strftime('%d/%m/%Y às %H:%M')
    )
"""

if "/financas/relatorio-geral" not in app_text:
    app_text += "\n" + rota_relatorio_analitico

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_text)

try:
    py_compile.compile('app.py', doraise=True)
    print("✓ app.py: Rota /financas/relatorio-geral compilada com sucesso!")
except Exception as e:
    print(f"Erro em app.py: {e}")
    exit(1)

# =============================================================================
# 3. ATUALIZAR TEMPLATES/DASHBOARD.HTML (INCLUIR BOTÃO DE BAIXAR E MAPA ANALÍTICO)
# =============================================================================
with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    dash_html = f.read()

# 1. Adicionar o botão de baixar relatório A4 no cabeçalho financeiro
botao_relatorio_header = """                <a href="/financas/relatorio-geral" target="_blank" class="px-3.5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-black rounded-xl text-xs shadow flex items-center gap-1.5 transition">
                    <span>📄</span><span>Baixar Balancete A4 (PDF)</span>
                </a>"""

if "Baixar Balancete A4" not in dash_html:
    dash_html = dash_html.replace(
        '<span>🔐</span><span>Lançamentos</span>\n                </a>',
        '<span>🔐</span><span>Lançamentos</span>\n                </a>\n' + botao_relatorio_header
    )

# 2. Adicionar o Mapa Analítico de Linhas (Entrou, Usou, Sobrou) antes da Distribuição de Categorias
bloco_tabela_analitica_dash = """        <!-- MAPA ANALÍTICO: O QUE ENTROU, O QUE FOI USADO E O QUE SOBROU -->
        <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 mb-8 space-y-3">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b pb-3">
                <div>
                    <h3 class="font-extrabold text-sm text-slate-900 uppercase tracking-wider flex items-center gap-2">
                        <span>⚖️</span> Mapa de Reconciliação: Entrou, Usado e Sobrou por Rubrica
                    </h3>
                    <p class="text-xs text-slate-500">Transparência detalhada por fonte de arrecadação e aplicação dos fundos</p>
                </div>
                <a href="/financas/relatorio-geral" target="_blank" class="text-xs font-bold text-emerald-700 hover:text-emerald-900 flex items-center gap-1">
                    <span>🖨️</span> Ver Balancete Oficial Completo →
                </a>
            </div>

            <div class="overflow-x-auto">
                <table class="w-full text-left text-xs border-collapse">
                    <thead>
                        <tr class="bg-slate-100 text-slate-700 font-bold uppercase text-[10px]">
                            <th class="py-2.5 px-3">Fonte / Fundo</th>
                            <th class="py-2.5 px-3 text-right">Entrou (+)</th>
                            <th class="py-2.5 px-3 text-right">Foi Usado (-)</th>
                            <th class="py-2.5 px-3 text-right font-black">Sobrou (=)</th>
                            <th class="py-2.5 px-3 text-center">Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        <!-- DÍZIMOS -->
                        <tr class="border-b hover:bg-slate-50">
                            <td class="py-2.5 px-3 font-bold text-slate-900">
                                📜 Dízimos Ministeriais
                                <span class="block text-[10px] text-slate-400 font-normal">Fidelidade e sustento pastoral</span>
                            </td>
                            <td class="py-2.5 px-3 text-right font-bold text-emerald-700">+ {{ "%.2f"|format(kpis.total_dizimos or 0) }} MT</td>
                            <td class="py-2.5 px-3 text-right font-bold text-rose-700">- 0.00 MT</td>
                            <td class="py-2.5 px-3 text-right font-black text-indigo-950">{{ "%.2f"|format(kpis.total_dizimos or 0) }} MT</td>
                            <td class="py-2.5 px-3 text-center"><span class="px-2 py-0.5 rounded-full text-[9px] font-black bg-emerald-100 text-emerald-800">POSITIVO</span></td>
                        </tr>
                        <!-- OFERTAS GERAIS -->
                        <tr class="border-b hover:bg-slate-50">
                            <td class="py-2.5 px-3 font-bold text-slate-900">
                                🏛️ Ofertas de Culto & Despesas Gerais
                                <span class="block text-[10px] text-slate-400 font-normal">Energia, água, ceia e manutenção local</span>
                            </td>
                            <td class="py-2.5 px-3 text-right font-bold text-emerald-700">+ {{ "%.2f"|format(kpis.geral_in or 0) }} MT</td>
                            <td class="py-2.5 px-3 text-right font-bold text-rose-700">- {{ "%.2f"|format(kpis.geral_out or 0) }} MT</td>
                            <td class="py-2.5 px-3 text-right font-black text-indigo-950">{{ "%.2f"|format((kpis.geral_in or 0) - (kpis.geral_out or 0)) }} MT</td>
                            <td class="py-2.5 px-3 text-center">
                                {% if (kpis.geral_in or 0) >= (kpis.geral_out or 0) %}
                                <span class="px-2 py-0.5 rounded-full text-[9px] font-black bg-emerald-100 text-emerald-800">EQUILIBRADO</span>
                                {% else %}
                                <span class="px-2 py-0.5 rounded-full text-[9px] font-black bg-rose-100 text-rose-800">DÉFICE</span>
                                {% endif %}
                            </td>
                        </tr>
                        <!-- MISSÕES -->
                        <tr class="border-b hover:bg-slate-50">
                            <td class="py-2.5 px-3 font-bold text-slate-900">
                                🌍 Fundo de Missões & Evangelismo
                                <span class="block text-[10px] text-slate-400 font-normal">Ofertas missionárias e obreiros do campo</span>
                            </td>
                            <td class="py-2.5 px-3 text-right font-bold text-emerald-700">+ {{ "%.2f"|format(kpis.total_missoes or 0) }} MT</td>
                            <td class="py-2.5 px-3 text-right font-bold text-rose-700">- 0.00 MT</td>
                            <td class="py-2.5 px-3 text-right font-black text-indigo-950">{{ "%.2f"|format(kpis.total_missoes or 0) }} MT</td>
                            <td class="py-2.5 px-3 text-center"><span class="px-2 py-0.5 rounded-full text-[9px] font-black bg-amber-100 text-amber-800">RESERVADO</span></td>
                        </tr>
                        <!-- CONSTRUÇÃO -->
                        <tr class="border-b hover:bg-slate-50">
                            <td class="py-2.5 px-3 font-bold text-slate-900">
                                🏗️ Campanha de Construção & Obras
                                <span class="block text-[10px] text-slate-400 font-normal">Infraestrutura, cimento e tijolos</span>
                            </td>
                            <td class="py-2.5 px-3 text-right font-bold text-emerald-700">+ {{ "%.2f"|format(kpis.total_construcao or 0) }} MT</td>
                            <td class="py-2.5 px-3 text-right font-bold text-rose-700">- 0.00 MT</td>
                            <td class="py-2.5 px-3 text-right font-black text-indigo-950">{{ "%.2f"|format(kpis.total_construcao or 0) }} MT</td>
                            <td class="py-2.5 px-3 text-center"><span class="px-2 py-0.5 rounded-full text-[9px] font-black bg-cyan-100 text-cyan-800">RESERVADO</span></td>
                        </tr>
                        <!-- DEPARTAMENTOS -->
                        <tr class="border-b hover:bg-slate-50">
                            <td class="py-2.5 px-3 font-bold text-slate-900">
                                👥 Departamentos (Juventude, EBD, Mães)
                                <span class="block text-[10px] text-slate-400 font-normal">Arrecadações setoriais</span>
                            </td>
                            <td class="py-2.5 px-3 text-right font-bold text-emerald-700">+ {{ "%.2f"|format(kpis.depto_in or 0) }} MT</td>
                            <td class="py-2.5 px-3 text-right font-bold text-rose-700">- {{ "%.2f"|format(kpis.depto_out or 0) }} MT</td>
                            <td class="py-2.5 px-3 text-right font-black text-indigo-950">{{ "%.2f"|format((kpis.depto_in or 0) - (kpis.depto_out or 0)) }} MT</td>
                            <td class="py-2.5 px-3 text-center"><span class="px-2 py-0.5 rounded-full text-[9px] font-black bg-indigo-100 text-indigo-800">DEPARTAMENTAL</span></td>
                        </tr>
                        <!-- SEDE / IGREJA MÃE -->
                        <tr class="border-b hover:bg-slate-50">
                            <td class="py-2.5 px-3 font-bold text-slate-900">
                                🏢 Igreja Mãe (Sede Provincial / Nacional)
                                <span class="block text-[10px] text-slate-400 font-normal">Apoios recebidos vs. Remessas enviadas</span>
                            </td>
                            <td class="py-2.5 px-3 text-right font-bold text-emerald-700">+ {{ "%.2f"|format(kpis.mae_in or 0) }} MT</td>
                            <td class="py-2.5 px-3 text-right font-bold text-rose-700">- {{ "%.2f"|format(kpis.mae_out or 0) }} MT</td>
                            <td class="py-2.5 px-3 text-right font-black text-indigo-950">{{ "%.2f"|format((kpis.mae_in or 0) - (kpis.mae_out or 0)) }} MT</td>
                            <td class="py-2.5 px-3 text-center"><span class="px-2 py-0.5 rounded-full text-[9px] font-black bg-purple-100 text-purple-800">CONVENÇÃO</span></td>
                        </tr>
                    </tbody>
                    <tfoot>
                        <tr class="bg-slate-100 font-black text-xs text-slate-900">
                            <td class="py-2.5 px-3 uppercase">SALDO TOTAL REMANESCENTE:</td>
                            <td class="py-2.5 px-3 text-right text-emerald-700">+ {{ "%.2f"|format(kpis.total_entradas) }} MT</td>
                            <td class="py-2.5 px-3 text-right text-rose-700">- {{ "%.2f"|format(kpis.total_saidas) }} MT</td>
                            <td class="py-2.5 px-3 text-right text-indigo-950 text-sm">{{ "%.2f"|format(kpis.saldo_caixa) }} MT</td>
                            <td class="py-2.5 px-3 text-center text-slate-500 font-normal">Consumo: {{ kpis.taxa_gasto }}%</td>
                        </tr>
                    </tfoot>
                </table>
            </div>
        </div>"""

if "Mapa de Reconciliação: Entrou, Usado e Sobrou" not in dash_html:
    dash_html = dash_html.replace(
        '<div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 mb-8">\n            <h3 class="font-bold text-sm text-slate-800 uppercase tracking-wider mb-4">📊 Distribuição por Categoria Financeira</h3>',
        bloco_tabela_analitica_dash + '\n\n        <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 mb-8">\n            <h3 class="font-bold text-sm text-slate-800 uppercase tracking-wider mb-4">📊 Distribuição por Categoria Financeira</h3>'
    )

env.parse(dash_html)
with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(dash_html)
print("✓ templates/dashboard.html: Tabela analítica e botão de download integrados!")

print("=" * 80)
print(">>> INSTALAÇÃO CONCLUÍDA COM TOTAL SUCESSO! EXECUTE: py app.py <<<")
print("=" * 80)