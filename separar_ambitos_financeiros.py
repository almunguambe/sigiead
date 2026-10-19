import os
import re
import jinja2

print("=" * 80)
print("A SEPARAR IGREJA GERAL, IGREJA MÃE E DEPARTAMENTOS NA TESOURARIA...")
print("=" * 80)

# =============================================================================
# 1. ATUALIZAR APP.PY COM OS 3 ÂMBITOS E MÉTRICAS SEPARADAS NO DASHBOARD
# =============================================================================
with open('app.py', 'r', encoding='utf-8') as f:
    app_py = f.read()

# Atualizar cálculo de KPIs no context_processor
kpis_busca = """    total_entradas = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Entrada'])
    total_saidas = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Saída'])
    saldo_caixa = total_entradas - total_saidas"""

kpis_substituicao = """    total_entradas = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Entrada'])
    total_saidas = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Saída'])
    saldo_caixa = total_entradas - total_saidas

    # 1. Separação por Conta: Caixa Físico vs Banco
    entradas_caixa_fisico = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Entrada' and 'banco' not in str(c.get('conta', '')).lower()])
    saidas_caixa_fisico = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Saída' and 'banco' not in str(c.get('conta', '')).lower()])
    saldo_caixa_fisico = entradas_caixa_fisico - saidas_caixa_fisico

    entradas_banco = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Entrada' and 'banco' in str(c.get('conta', '')).lower()])
    saidas_banco = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Saída' and 'banco' in str(c.get('conta', '')).lower()])
    saldo_banco = entradas_banco - saidas_banco

    # 2. Análise Separada: Igreja Geral vs Igreja Mãe vs Departamentos
    geral_in = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Entrada' and str(c.get('destino_tipo', 'Igreja Geral')) == 'Igreja Geral'])
    geral_out = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Saída' and str(c.get('destino_tipo', 'Igreja Geral')) == 'Igreja Geral'])

    mae_in = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Entrada' and str(c.get('destino_tipo', '')) == 'Igreja Mãe'])
    mae_out = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Saída' and str(c.get('destino_tipo', '')) == 'Igreja Mãe'])

    depto_in = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Entrada' and str(c.get('destino_tipo', '')) == 'Departamento'])
    depto_out = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Saída' and str(c.get('destino_tipo', '')) == 'Departamento'])"""

if kpis_busca in app_py:
    app_py = app_py.replace(kpis_busca, kpis_substituicao)

# Injetar os novos KPIs no dicionário retornado
app_py = re.sub(
    r"'saldo_caixa': saldo_caixa,[\s\S]*?'total_dizimos': total_dizimos,",
    """'saldo_caixa': saldo_caixa, 'saldo_caixa_fisico': saldo_caixa_fisico, 'saldo_banco': saldo_banco,
            'geral_in': geral_in, 'geral_out': geral_out,
            'mae_in': mae_in, 'mae_out': mae_out,
            'depto_in': depto_in, 'depto_out': depto_out,
            'total_dizimos': total_dizimos,""",
    app_py
)

# Atualizar a rota /financas/caixa/novo para registrar com precisão os 3 âmbitos
rota_caixa_nova = '''@app.route('/financas/caixa/novo', methods=['POST'])
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
    else:  # Saída
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
    return redirect('/?aba=tesouraria')'''

app_py = re.sub(
    r'@app\.route\(\'/financas/caixa/novo\', methods=\[\'POST\'\]\)[\s\S]*?return redirect\(\'/\?aba=tesouraria\'\)',
    rota_caixa_nova,
    app_py
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_py)
print("✓ app.py: Lógica contábil dos 3 âmbitos configurada com sucesso!")

# =============================================================================
# 2. RECONSTRUIR TEMPLATES/DASHBOARD.HTML COM OS 3 ÂMBITOS SEPARADOS
# =============================================================================
with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    dash_html = f.read()

# Substituir o bloco da tesouraria
bloco_tesouraria_3ambitos = '''        <!-- ========================================================= -->
        <!-- ABA 6: CAIXA & TESOURARIA (3 ÂMBITOS SEPARADOS)           -->
        <!-- ========================================================= -->
        {% if aba_ativa == 'tesouraria' %}
        <div class="bg-amber-950 text-white p-6 rounded-2xl shadow mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
                <div class="inline-flex items-center gap-2 bg-amber-500/20 text-amber-300 px-3 py-1 rounded-full text-[10px] font-black uppercase mb-1 border border-amber-400/30">
                    <span>🔐</span> ACESSO RESTRITO • GABINETE DA TESOURARIA
                </div>
                <h2 class="text-2xl font-black">Lançamentos de Caixa & Movimentação Financeira</h2>
                <p class="text-xs text-amber-200 mt-0.5">Gestão separada: Igreja em Geral (Local), Igreja Mãe (Sede) e Departamentos</p>
            </div>
            <div class="flex items-center gap-3">
                <div class="bg-white/10 px-3.5 py-2 rounded-xl text-right border border-white/10">
                    <span class="text-[9px] uppercase font-bold text-amber-300 block">Caixa Físico</span>
                    <span class="text-sm font-black text-white">{{ "%.2f"|format(kpis.saldo_caixa_fisico or 0) }} MT</span>
                </div>
                <div class="bg-white/10 px-3.5 py-2 rounded-xl text-right border border-white/10">
                    <span class="text-[9px] uppercase font-bold text-blue-300 block">Conta Bancária</span>
                    <span class="text-sm font-black text-white">{{ "%.2f"|format(kpis.saldo_banco or 0) }} MT</span>
                </div>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            
            <!-- FORMULÁRIO DINÂMICO COM OS 3 ÂMBITOS -->
            <div class="lg:col-span-5 bg-white p-6 rounded-2xl shadow-sm border-2 border-amber-300">
                <h3 class="font-extrabold text-base mb-4 border-b pb-2 text-amber-950 flex items-center gap-2">
                    <span>✍️</span> Lançar Entrada ou Saída de Valores
                </h3>
                
                <form action="/financas/caixa/novo" method="POST" class="space-y-4 text-xs">
                    
                    <!-- LINHA 1: TIPO DE MOVIMENTO E CONTA -->
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">Tipo de Movimento *</label>
                            <select id="tipo_movimento" name="tipo" onchange="atualizarFormularioTesouraria()" class="w-full h-11 px-2 border-2 border-slate-200 rounded-xl bg-slate-50 font-black text-sm">
                                <option value="Entrada">🟢 Entrada (+)</option>
                                <option value="Saída">🔴 Saída (-)</option>
                            </select>
                        </div>
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">Conta Financeira *</label>
                            <select name="conta" required class="w-full h-11 px-2 border-2 border-slate-200 rounded-xl bg-slate-50 font-black text-xs text-indigo-900">
                                <option value="Caixa Físico">💵 Caixa Físico (Numerário)</option>
                                <option value="Conta Bancária">🏦 Conta Bancária</option>
                            </select>
                        </div>
                    </div>

                    <!-- LINHA 2: ÂMBITO RIGOROSAMENTE SEPARADO (3 OPÇÕES) -->
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">Âmbito do Movimento (Onde entra / De onde sai) *</label>
                        <select id="destino_tipo" name="destino_tipo" onchange="atualizarFormularioTesouraria()" class="w-full h-11 px-3 border-2 border-indigo-300 rounded-xl bg-indigo-50/50 font-black text-xs text-indigo-950">
                            <option value="Igreja Geral">🏛️ 1. Igreja em Geral (Local / Sede Chicuque)</option>
                            <option value="Igreja Mãe">🏢 2. Igreja Mãe (Sede / Ministério Thavane)</option>
                            <option value="Departamento">👥 3. Departamentos da Igreja</option>
                        </select>
                    </div>

                    <!-- LINHA 3: DATA E VALOR -->
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">Data da Operação *</label>
                            <input type="date" name="data_movimento" required class="w-full h-11 px-2 border-2 border-slate-200 rounded-xl bg-slate-50 font-bold">
                        </div>
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">Valor (MZN) *</label>
                            <input type="number" step="0.01" name="valor" required placeholder="Ex: 2500.00" class="w-full h-11 px-3 border-2 border-emerald-400 rounded-xl bg-emerald-50/50 font-black text-emerald-950 text-base">
                        </div>
                    </div>

                    <!-- ======================================================== -->
                    <!-- 1A. ENTRADA NA IGREJA GERAL (LOCAL)                     -->
                    <!-- ======================================================== -->
                    <div id="box_entrada_geral" class="space-y-2 p-3.5 bg-emerald-50/70 rounded-xl border border-emerald-200">
                        <div class="font-black text-emerald-900 text-[10px] uppercase">Receita da Igreja Local (Sede Chicuque)</div>
                        <label class="block font-semibold text-slate-700 mb-1">Categoria de Entrada Local *</label>
                        <select name="categoria" class="w-full h-10 px-2 border rounded-xl bg-white font-bold text-slate-800">
                            {% for op in opcoes.get('categoria_caixa', []) %}
                            <option value="{{ op.valor }}">{{ op.valor }}</option>
                            {% else %}
                            <option value="Dízimos">Dízimos</option>
                            <option value="Oferta de Culto">Oferta de Culto</option>
                            <option value="Oferta de Missões">Oferta de Missões</option>
                            <option value="Fundo de Construção">Fundo de Construção</option>
                            <option value="Ação Social">Ação Social</option>
                            {% endfor %}
                        </select>
                    </div>

                    <!-- ======================================================== -->
                    <!-- 1B. ENTRADA DA IGREJA MÃE (SEDE / THAVANE)               -->
                    <!-- ======================================================== -->
                    <div id="box_entrada_mae" class="hidden space-y-2 p-3.5 bg-blue-50/70 rounded-xl border border-blue-200">
                        <div class="font-black text-blue-900 text-[10px] uppercase">Valores Recebidos da Igreja Mãe / Sede</div>
                        <label class="block font-semibold text-slate-700 mb-1">Tipo de Entrada da Igreja Mãe *</label>
                        <select name="categoria_entrada_mae" class="w-full h-10 px-2 border-2 border-blue-300 rounded-xl bg-white font-bold text-blue-950">
                            <option value="Subsídio da Igreja Mãe">Apoio / Subsídio da Igreja Mãe</option>
                            <option value="Fundo de Missão da Sede">Fundo Missionário Enviado pela Sede</option>
                            <option value="Doação Especial da Sede">Doação Especial da Igreja Mãe</option>
                        </select>
                    </div>

                    <!-- ======================================================== -->
                    <!-- 1C. ENTRADA EM DEPARTAMENTOS                            -->
                    <!-- ======================================================== -->
                    <div id="box_entrada_depto" class="hidden space-y-3 p-3.5 bg-emerald-50/70 rounded-xl border border-emerald-200">
                        <div class="font-black text-emerald-900 text-[10px] uppercase">Entrada Destinada ao Departamento</div>
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">Qual Departamento recebe? *</label>
                            <select name="departamento" class="w-full h-10 px-2 border-2 border-emerald-300 rounded-xl bg-white font-extrabold text-indigo-900">
                                {% for op in opcoes.get('departamento', []) %}
                                <option value="{{ op.valor }}">{{ op.valor }}</option>
                                {% endfor %}
                            </select>
                            <p class="text-[10px] text-slate-400 mt-1">Gerido no menu ⚙️ Gestor de Seletores</p>
                        </div>
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">Tipo de Entrada Departamental *</label>
                            <select name="categoria_entrada_depto" class="w-full h-10 px-2 border rounded-xl bg-white font-semibold">
                                <option value="Quotas / Mensalidades do Depto">Quotas / Mensalidades do Depto</option>
                                <option value="Oferta de Culto do Depto">Oferta de Culto do Depto</option>
                                <option value="Bazar / Venda do Depto">Bazar / Arrecadação de Fundos</option>
                                <option value="Oferta Especial / Doação">Oferta Especial / Doação Direta</option>
                            </select>
                        </div>
                    </div>

                    <!-- ======================================================== -->
                    <!-- 2A. SAÍDA DA IGREJA GERAL (DESPESAS LOCAIS)              -->
                    <!-- ======================================================== -->
                    <div id="box_saida_geral" class="hidden space-y-2 p-3.5 bg-rose-50/70 rounded-xl border border-rose-200">
                        <div class="font-black text-rose-900 text-[10px] uppercase">Despesas de Funcionamento Local</div>
                        <label class="block font-bold text-slate-700 mb-1">Selecione a Despesa Local *</label>
                        <select name="categoria_saida_geral" class="w-full h-10 px-2 border-2 border-slate-300 rounded-xl bg-white font-extrabold text-slate-800">
                            <option value="Energia (Electricidade / Credelec)">💡 Energia (Electricidade / Credelec)</option>
                            <option value="Água">🚰 Água</option>
                            <option value="Vogal (Apoio Pastoral / Transporte)">🚗 Vogal (Subsídio / Apoio Pastoral)</option>
                            <option value="Santa Ceia (Pão e Vinho)">🍞 Santa Ceia (Pão / Vinho / Elementos)</option>
                            <option value="Manutenção & Reparações">🛠️ Manutenção & Reparações do Templo</option>
                            <option value="Limpeza & Consumíveis">🧹 Material de Limpeza & Higiene</option>
                            <option value="Outras Despesas Locais">📦 Outras Despesas Gerais da Igreja</option>
                        </select>
                    </div>

                    <!-- ======================================================== -->
                    <!-- 2B. SAÍDA PARA A IGREJA MÃE (REMESSAS SEDE)              -->
                    <!-- ======================================================== -->
                    <div id="box_saida_mae" class="hidden space-y-2 p-3.5 bg-amber-50/70 rounded-xl border-2 border-amber-300">
                        <div class="font-black text-amber-950 text-[10px] uppercase">Remessas Enviadas à Igreja Mãe (Sede Thavane)</div>
                        <label class="block font-bold text-amber-900 mb-1">Selecione o Tipo de Remessa / Envio *</label>
                        <select name="categoria_saida_mae" class="w-full h-10 px-2 border-2 border-amber-400 rounded-xl bg-white font-black text-amber-950 text-xs">
                            <option value="Dízimo dos Dízimos (Remessa Oficial)">📜 Dízimo dos Dízimos (Remessa Oficial à Sede)</option>
                            <option value="Quota da Sede Provincial">🏢 Quota / Taxa da Sede Provincial</option>
                            <option value="Conferências da Igreja Mãe">🎪 Contribuição para Conferências da Sede</option>
                            <option value="Oferta Especial para a Igreja Mãe">🤝 Oferta Especial / Apoio à Igreja Mãe</option>
                        </select>
                    </div>

                    <!-- ======================================================== -->
                    <!-- 2C. SAÍDA PARA DEPARTAMENTOS                            -->
                    <!-- ======================================================== -->
                    <div id="box_saida_depto" class="hidden space-y-3 p-3.5 bg-rose-50/70 rounded-xl border border-rose-200">
                        <div class="font-black text-rose-900 text-[10px] uppercase">Saída / Fundo Destinado a Departamento</div>
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">Qual Departamento recebe o valor? *</label>
                            <select name="departamento" class="w-full h-10 px-2 border-2 border-rose-300 rounded-xl bg-white font-extrabold text-indigo-900">
                                {% for op in opcoes.get('departamento', []) %}
                                <option value="{{ op.valor }}">{{ op.valor }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        <div>
                            <label class="block font-bold text-rose-900 mb-1">Propósito da Saída (Justificativa Obrigatória) *</label>
                            <textarea name="proposito" rows="2" placeholder="Ex: Compra de materiais didáticos da EBD / Lanche da vigília da Juventude..." class="w-full p-2.5 border-2 border-rose-300 rounded-xl bg-white font-medium"></textarea>
                        </div>
                    </div>

                    <!-- OBSERVAÇÕES / RECIBO GERAL -->
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">Observações Adicionais / Recibo</label>
                        <input type="text" name="descricao" placeholder="Nº do recibo, beneficiário ou detalhe complementar..." class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                    </div>

                    <button type="submit" class="w-full py-3.5 bg-emerald-700 hover:bg-emerald-800 text-white font-black rounded-xl shadow cursor-pointer text-sm transition">
                        💾 Confirmar e Lançar Movimento
                    </button>
                </form>
            </div>

            <!-- TABELA DE ÚLTIMOS LANÇAMENTOS -->
            <div class="lg:col-span-7 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2 text-slate-800 flex justify-between items-center">
                    <span>📋 Últimos Lançamentos Efetuados</span>
                    <span class="text-xs bg-slate-100 text-slate-600 px-2.5 py-1 rounded-full font-bold">Total: {{ caixa|length }}</span>
                </h3>
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs">
                        <thead>
                            <tr class="border-b-2 border-slate-200 text-slate-500">
                                <th class="py-2.5 px-2">Data</th>
                                <th class="py-2.5 px-2">Conta</th>
                                <th class="py-2.5 px-2">Âmbito & Classificação</th>
                                <th class="py-2.5 px-2 text-right">Valor</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for cx in caixa[:15] %}
                            <tr class="border-b border-slate-100 hover:bg-slate-50">
                                <td class="py-2.5 px-2 text-slate-600 font-semibold">{{ cx.data_movimento }}</td>
                                <td class="py-2.5 px-2">
                                    {% if 'banco' in (cx.conta or '')|lower %}
                                    <span class="bg-blue-100 text-blue-900 px-2 py-0.5 rounded font-black text-[10px]">🏦 Banco</span>
                                    {% else %}
                                    <span class="bg-amber-100 text-amber-900 px-2 py-0.5 rounded font-black text-[10px]">💵 Caixa</span>
                                    {% endif %}
                                </td>
                                <td class="py-2.5 px-2">
                                    <div class="flex items-center gap-1.5">
                                        {% if cx.destino_tipo == 'Igreja Mãe' %}
                                        <span class="bg-purple-100 text-purple-900 px-1.5 py-0.5 rounded text-[9px] font-black">🏢 Igreja Mãe</span>
                                        {% elif cx.destino_tipo == 'Departamento' %}
                                        <span class="bg-indigo-100 text-indigo-900 px-1.5 py-0.5 rounded text-[9px] font-black">👥 Depto</span>
                                        {% else %}
                                        <span class="bg-slate-200 text-slate-800 px-1.5 py-0.5 rounded text-[9px] font-black">🏛️ Local</span>
                                        {% endif %}
                                        <span class="font-bold {% if cx.tipo == 'Entrada' %}text-emerald-950{% else %}text-rose-950{% endif %}">
                                            {{ cx.categoria }}
                                        </span>
                                    </div>
                                    {% if cx.descricao %}
                                    <div class="text-[10px] text-slate-500 truncate max-w-xs mt-0.5">{{ cx.descricao }}</div>
                                    {% endif %}
                                </td>
                                <td class="py-2.5 px-2 text-right font-black {% if cx.tipo == 'Entrada' %}text-emerald-700{% else %}text-rose-700{% endif %}">
                                    {% if cx.tipo == 'Entrada' %}+{% else %}-{% endif %} {{ "%.2f"|format(cx.valor or 0) }} MT
                                </td>
                            </tr>
                            {% else %}
                            <tr><td colspan="4" class="py-8 text-center text-slate-400">Nenhum lançamento efetuado ainda.</td></tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- SCRIPT PARA TROCA DINÂMICA ENTRE OS 3 ÂMBITOS -->
        <script>
            function atualizarFormularioTesouraria() {
                var tipo = document.getElementById('tipo_movimento').value;
                var destinoTipo = document.getElementById('destino_tipo').value;

                var bEntGeral = document.getElementById('box_entrada_geral');
                var bEntMae = document.getElementById('box_entrada_mae');
                var bEntDepto = document.getElementById('box_entrada_depto');

                var bSaiGeral = document.getElementById('box_saida_geral');
                var bSaiMae = document.getElementById('box_saida_mae');
                var bSaiDepto = document.getElementById('box_saida_depto');

                // Esconder todos inicialmente
                bEntGeral.classList.add('hidden');
                bEntMae.classList.add('hidden');
                bEntDepto.classList.add('hidden');
                bSaiGeral.classList.add('hidden');
                bSaiMae.classList.add('hidden');
                bSaiDepto.classList.add('hidden');

                if (tipo === 'Entrada') {
                    if (destinoTipo === 'Igreja Geral') {
                        bEntGeral.classList.remove('hidden');
                    } else if (destinoTipo === 'Igreja Mãe') {
                        bEntMae.classList.remove('hidden');
                    } else if (destinoTipo === 'Departamento') {
                        bEntDepto.classList.remove('hidden');
                    }
                } else {
                    if (destinoTipo === 'Igreja Geral') {
                        bSaiGeral.classList.remove('hidden');
                    } else if (destinoTipo === 'Igreja Mãe') {
                        bSaiMae.classList.remove('hidden');
                    } else if (destinoTipo === 'Departamento') {
                        bSaiDepto.classList.remove('hidden');
                    }
                }
            }
        </script>
        {% endif %}'''

# Substituição exata do bloco da tesouraria
regex_tesouraria = r'<!-- ========================================================= -->\s*<!-- ABA 6: CAIXA & TESOURARIA[\s\S]*?{% endif %}'
dash_html = re.sub(regex_tesouraria, bloco_tesouraria_3ambitos, dash_html)

# Adicionar cards analíticos na aba 5 (Dashboard Financeiro) mostrando a divisão dos 3 âmbitos
bloco_analise_ambitos = '''        <!-- 3 CARDS ANALÍTICOS: IGREJA LOCAL, IGREJA MÃE E DEPARTAMENTOS -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-5 mb-8 text-xs">
            <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200">
                <div class="font-extrabold text-slate-800 uppercase flex items-center justify-between border-b pb-2 mb-2">
                    <span>🏛️ Igreja Geral (Local)</span>
                    <span class="text-[10px] bg-slate-100 text-slate-600 px-2 py-0.5 rounded">Sede Chicuque</span>
                </div>
                <div class="flex justify-between items-center text-emerald-700 font-bold">
                    <span>Entradas:</span>
                    <span>+ {{ "%.2f"|format(kpis.geral_in or 0) }} MT</span>
                </div>
                <div class="flex justify-between items-center text-rose-700 font-bold mt-1">
                    <span>Despesas Locais:</span>
                    <span>- {{ "%.2f"|format(kpis.geral_out or 0) }} MT</span>
                </div>
                <div class="border-t pt-2 mt-2 flex justify-between items-center font-black text-slate-900">
                    <span>Saldo Operacional:</span>
                    <span>{{ "%.2f"|format((kpis.geral_in or 0) - (kpis.geral_out or 0)) }} MT</span>
                </div>
            </div>

            <div class="bg-white p-5 rounded-2xl shadow-sm border border-amber-200 bg-amber-50/30">
                <div class="font-extrabold text-amber-950 uppercase flex items-center justify-between border-b border-amber-200 pb-2 mb-2">
                    <span>🏢 Igreja Mãe (Sede)</span>
                    <span class="text-[10px] bg-amber-200 text-amber-950 px-2 py-0.5 rounded font-black">Thavane</span>
                </div>
                <div class="flex justify-between items-center text-blue-800 font-bold">
                    <span>Apoio Recebido:</span>
                    <span>+ {{ "%.2f"|format(kpis.mae_in or 0) }} MT</span>
                </div>
                <div class="flex justify-between items-center text-rose-700 font-bold mt-1">
                    <span>Remessas / Dízimo Dízimos:</span>
                    <span>- {{ "%.2f"|format(kpis.mae_out or 0) }} MT</span>
                </div>
                <div class="border-t border-amber-200 pt-2 mt-2 flex justify-between items-center font-black text-amber-950">
                    <span>Balanço c/ a Sede:</span>
                    <span>{{ "%.2f"|format((kpis.mae_in or 0) - (kpis.mae_out or 0)) }} MT</span>
                </div>
            </div>

            <div class="bg-white p-5 rounded-2xl shadow-sm border border-indigo-200 bg-indigo-50/30">
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
        </div>'''

# Inserir os 3 cards analíticos no Dashboard Financeiro antes do gráfico de barras
if '<!-- 3 CARDS ANALÍTICOS' not in dash_html:
    dash_html = dash_html.replace(
        '<div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 mb-8">',
        bloco_analise_ambitos + '\n        <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 mb-8">'
    )

# Validação do Jinja2 em memória
env = jinja2.Environment()
env.parse(dash_html)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(dash_html)

print("=" * 80)
print(">>> SUCESSO: TEMPLATE VALIDADO COM OS 3 ÂMBITOS E ZERO ERROS DE JINJA2! <<<")
print("=" * 80)