import os
import re
import jinja2

print("=" * 80)
print("A CONFIGURAR ENTRADAS E SAÍDAS (IGREJA GERAL, IGREJA MÃE E DEPARTAMENTOS)...")
print("=" * 80)

# =============================================================================
# 1. ATUALIZAR A ROTA DE GRAVAÇÃO DO CAIXA NO APP.PY
# =============================================================================
with open('app.py', 'r', encoding='utf-8') as f:
    app_code = f.read()

nova_rota_caixa = '''@app.route('/financas/caixa/novo', methods=['POST'])
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
    cat_entrada = fd.get('categoria', 'Dízimos').strip()
    cat_entrada_depto = fd.get('categoria_entrada_depto', 'Oferta do Departamento').strip()
    cat_saida = fd.get('categoria_saida', 'Despesa Geral').strip()
    proposito = fd.get('proposito', '').strip()

    if tipo == 'Entrada':
        if destino_tipo == 'Departamento':
            categoria = f"Entrada: {depto}"
            detalhe = f"{cat_entrada_depto}"
            desc = f"{detalhe} | {desc}".strip(' |')
        else:
            categoria = cat_entrada
    else:  # Saída
        if destino_tipo == 'Departamento':
            categoria = f"Saída: {depto}"
            if proposito:
                desc = f"Propósito: {proposito} | {desc}".strip(' |')
        else:
            categoria = cat_saida or 'Despesa Geral'

    m = "%s" if DATABASE_URL else "?"
    sql = f"""INSERT INTO caixa 
              (tipo, categoria, valor, descricao, data_movimento, conta, destino_tipo, departamento, categoria_saida, proposito, criado_em)
              VALUES ({m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m}, {m})"""
    executar_comando(sql, (tipo, categoria, val, desc, dt, conta, destino_tipo, depto, cat_saida, proposito, datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=tesouraria')'''

app_code = re.sub(
    r'@app\.route\(\'/financas/caixa/novo\', methods=\[\'POST\'\]\)[\s\S]*?return redirect\(\'/\?aba=tesouraria\'\)',
    nova_rota_caixa,
    app_code
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_code)
print("✓ app.py: Lógica de Entrada/Saída por Departamentos atualizada!")

# =============================================================================
# 2. ATUALIZAR TEMPLATES/DASHBOARD.HTML (ABA TESOURARIA TOTALMENTE DINÂMICA)
# =============================================================================
with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    dash_html = f.read()

bloco_tesouraria_novo = '''        <!-- ========================================================= -->
        <!-- ABA 6: CAIXA & TESOURARIA (ENTRADAS E SAÍDAS DINÂMICAS)    -->
        <!-- ========================================================= -->
        {% if aba_ativa == 'tesouraria' %}
        <div class="bg-amber-950 text-white p-6 rounded-2xl shadow mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
                <div class="inline-flex items-center gap-2 bg-amber-500/20 text-amber-300 px-3 py-1 rounded-full text-[10px] font-black uppercase mb-1 border border-amber-400/30">
                    <span>🔐</span> ACESSO RESTRITO • GABINETE DA TESOURARIA
                </div>
                <h2 class="text-2xl font-black">Lançamentos de Caixa & Movimentação Financeira</h2>
                <p class="text-xs text-amber-200 mt-0.5">Controlo de entradas e saídas por conta financeira, igreja mãe e departamentos</p>
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
            
            <!-- FORMULÁRIO DINÂMICO DE LANÇAMENTO -->
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

                    <!-- LINHA 2: ÂMBITO / DESTINO (IGREJA GERAL OU DEPARTAMENTO) -->
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">Âmbito do Movimento (Onde entra / de onde sai) *</label>
                        <select id="destino_tipo" name="destino_tipo" onchange="atualizarFormularioTesouraria()" class="w-full h-11 px-3 border-2 border-slate-300 rounded-xl bg-white font-black text-xs text-indigo-950">
                            <option value="Igreja Geral">🏛️ Igreja em Geral / Igreja Mãe</option>
                            <option value="Departamento">👥 Departamentos da Igreja</option>
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
                    <!-- CASO 1: ENTRADA NA IGREJA GERAL / IGREJA MÃE            -->
                    <!-- ======================================================== -->
                    <div id="box_entrada_geral" class="space-y-2 p-3.5 bg-emerald-50/60 rounded-xl border border-emerald-200">
                        <div class="font-black text-emerald-900 text-[10px] uppercase">Classificação da Entrada Geral</div>
                        <label class="block font-semibold text-slate-700 mb-1">Categoria de Receita *</label>
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
                    <!-- CASO 2: ENTRADA EM DEPARTAMENTO                         -->
                    <!-- ======================================================== -->
                    <div id="box_entrada_depto" class="hidden space-y-3 p-3.5 bg-emerald-50/60 rounded-xl border border-emerald-200">
                        <div class="font-black text-emerald-900 text-[10px] uppercase">Departamento Beneficiário da Entrada</div>
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">Qual Departamento recebe? *</label>
                            <select name="departamento" class="w-full h-10 px-2 border-2 border-emerald-300 rounded-xl bg-white font-extrabold text-indigo-900">
                                {% for op in opcoes.get('departamento', []) %}
                                <option value="{{ op.valor }}">{{ op.valor }}</option>
                                {% else %}
                                <option value="Juventude Cristã">Juventude Cristã</option>
                                <option value="Círculo de Oração">Círculo de Oração</option>
                                <option value="Escola Dominical">Escola Dominical</option>
                                <option value="Evangelismo & Missões">Evangelismo & Missões</option>
                                <option value="Louvor & Adoração">Louvor & Adoração</option>
                                {% endfor %}
                            </select>
                            <p class="text-[10px] text-slate-400 mt-1">Gerido no menu ⚙️ Gestor de Seletores</p>
                        </div>
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">Tipo de Entrada no Departamento *</label>
                            <select name="categoria_entrada_depto" class="w-full h-10 px-2 border rounded-xl bg-white font-semibold">
                                <option value="Quotas / Mensalidades do Depto">Quotas / Mensalidades do Depto</option>
                                <option value="Oferta de Culto do Depto">Oferta de Culto do Depto</option>
                                <option value="Bazar / Venda do Depto">Bazar / Arrecadação de Fundos</option>
                                <option value="Oferta Especial / Doação">Oferta Especial / Doação Direta</option>
                            </select>
                        </div>
                    </div>

                    <!-- ======================================================== -->
                    <!-- CASO 3: SAÍDA DA IGREJA GERAL / IGREJA MÃE              -->
                    <!-- ======================================================== -->
                    <div id="box_saida_geral" class="hidden space-y-2 p-3.5 bg-rose-50/60 rounded-xl border border-rose-200">
                        <div class="font-black text-rose-900 text-[10px] uppercase">Despesa Institucional Central</div>
                        <label class="block font-bold text-slate-700 mb-1">Selecione a Despesa *</label>
                        <select name="categoria_saida" class="w-full h-10 px-2 border-2 border-slate-300 rounded-xl bg-white font-extrabold text-slate-800">
                            <option value="Energia (Electricidade)">💡 Energia (Electricidade / Credelec)</option>
                            <option value="Água">🚰 Água</option>
                            <option value="Vogal (Apoio Pastoral / Transporte)">🚗 Vogal (Subsídio / Apoio Pastoral)</option>
                            <option value="Santa Ceia (Elementos)">🍞 Santa Ceia (Pão / Vinho / Elementos)</option>
                            <option value="Dízimo dos Dízimos (Igreja Mãe)">📜 Dízimo dos Dízimos (Igreja Mãe / Sede)</option>
                            <option value="Conferências & Eventos">🎪 Conferências & Eventos Oficiais</option>
                            <option value="Manutenção & Conservação">🛠️ Manutenção & Reparações do Templo</option>
                            <option value="Outras Despesas Gerais">📦 Outras Despesas Gerais</option>
                        </select>
                    </div>

                    <!-- ======================================================== -->
                    <!-- CASO 4: SAÍDA PARA DEPARTAMENTO                         -->
                    <!-- ======================================================== -->
                    <div id="box_saida_depto" class="hidden space-y-3 p-3.5 bg-rose-50/60 rounded-xl border border-rose-200">
                        <div class="font-black text-rose-900 text-[10px] uppercase">Saída / Fundo Destinado a Departamento</div>
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">Para qual Departamento sai o valor? *</label>
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
                                <th class="py-2.5 px-2">Classificação / Origem-Destino</th>
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
                                    <div class="font-bold {% if cx.tipo == 'Entrada' %}text-emerald-950{% else %}text-rose-950{% endif %}">
                                        {{ cx.categoria }}
                                    </div>
                                    {% if cx.descricao %}
                                    <div class="text-[10px] text-slate-500 truncate max-w-xs">{{ cx.descricao }}</div>
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

        <!-- SCRIPT PARA TROCA DINÂMICA DE BLOCOS -->
        <script>
            function atualizarFormularioTesouraria() {
                var tipo = document.getElementById('tipo_movimento').value;
                var destinoTipo = document.getElementById('destino_tipo').value;

                var bEntradaGeral = document.getElementById('box_entrada_geral');
                var bEntradaDepto = document.getElementById('box_entrada_depto');
                var bSaidaGeral = document.getElementById('box_saida_geral');
                var bSaidaDepto = document.getElementById('box_saida_depto');

                // Esconder todos inicialmente
                bEntradaGeral.classList.add('hidden');
                bEntradaDepto.classList.add('hidden');
                bSaidaGeral.classList.add('hidden');
                bSaidaDepto.classList.add('hidden');

                if (tipo === 'Entrada') {
                    if (destinoTipo === 'Departamento') {
                        bEntradaDepto.classList.remove('hidden');
                    } else {
                        bEntradaGeral.classList.remove('hidden');
                    }
                } else {
                    if (destinoTipo === 'Departamento') {
                        bSaidaDepto.classList.remove('hidden');
                    } else {
                        bSaidaGeral.classList.remove('hidden');
                    }
                }
            }
        </script>
        {% endif %}'''

# Substituição cirúrgica do bloco da tesouraria
regex_tesouraria = r'<!-- ========================================================= -->\s*<!-- ABA 6: CAIXA & TESOURARIA[\s\S]*?{% endif %}'
dash_html = re.sub(regex_tesouraria, bloco_tesouraria_novo, dash_html)

# Validação prévia com o compilador do Jinja2
env = jinja2.Environment()
env.parse(dash_html)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(dash_html)

print("=" * 80)
print(">>> SUCESSO: TEMPLATE VALIDADO COM ZERO ERROS DE JINJA2! <<<")
print("=" * 80)