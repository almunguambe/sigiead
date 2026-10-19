import os
import re

print("=" * 80)
print("A CONFIGURAR SELETORES DE CONTA (CAIXA/BANCO), DESPESAS E DEPARTAMENTOS...")
print("=" * 80)

# =============================================================================
# 1. ATUALIZAR APP.PY COM OS NOVOS CAMPOS FINANCEIROS E SALDOS SEPARADOS
# =============================================================================
with open('app.py', 'r', encoding='utf-8') as f:
    app_py = f.read()

# Migração das novas colunas na tabela caixa
migracao_caixa_code = '''
        # Sincronizar colunas da tabela caixa
        cur.execute("PRAGMA table_info(caixa);")
        cols_cx = [c[1].lower() for c in cur.fetchall()]
        novas_cols_cx = [
            ('tipo', 'TEXT'), ('categoria', 'TEXT'), ('valor', 'REAL'),
            ('descricao', 'TEXT'), ('data_movimento', 'TEXT'), ('conta', 'TEXT'),
            ('destino_tipo', 'TEXT'), ('departamento', 'TEXT'),
            ('categoria_saida', 'TEXT'), ('proposito', 'TEXT'), ('criado_em', 'TEXT')
        ]
        for col, tipo in novas_cols_cx:
            if col not in cols_cx:
                try: cur.execute(f"ALTER TABLE caixa ADD COLUMN {col} {tipo};")
                except: pass
'''

if 'cols_cx = [c[1].lower() for c in cur.fetchall()]' in app_py:
    # Substituir bloco simples de caixa pelo bloco completo
    app_py = re.sub(
        r'# Sincronizar caixa[\s\S]*?cur\.execute\(f"ALTER TABLE caixa ADD COLUMN \{col\} \{tipo\};"\)',
        migracao_caixa_code.strip(),
        app_py
    )

# Atualizar o cálculo de KPIs financeiros no context_processor para separar Caixa e Banco
kpis_antigo = """    total_entradas = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Entrada'])
    total_saidas = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Saída'])
    saldo_caixa = total_entradas - total_saidas"""

kpis_novo = """    total_entradas = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Entrada'])
    total_saidas = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Saída'])
    saldo_caixa = total_entradas - total_saidas

    # Separação por Conta Financeira: Caixa Físico vs Conta Bancária
    entradas_caixa_fisico = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Entrada' and 'banco' not in str(c.get('conta', '')).lower()])
    saidas_caixa_fisico = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Saída' and 'banco' not in str(c.get('conta', '')).lower()])
    saldo_caixa_fisico = entradas_caixa_fisico - saidas_caixa_fisico

    entradas_banco = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Entrada' and 'banco' in str(c.get('conta', '')).lower()])
    saidas_banco = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Saída' and 'banco' in str(c.get('conta', '')).lower()])
    saldo_banco = entradas_banco - saidas_banco"""

if kpis_antigo in app_py:
    app_py = app_py.replace(kpis_antigo, kpis_novo)

# Injetar os novos saldos no dicionário kpis do context_processor
app_py = app_py.replace(
    "'saldo_caixa': saldo_caixa,",
    "'saldo_caixa': saldo_caixa, 'saldo_caixa_fisico': saldo_caixa_fisico, 'saldo_banco': saldo_banco,"
)

# Atualizar a rota /financas/caixa/novo para receber todas as novas variáveis
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
    cat_saida = fd.get('categoria_saida', '').strip()
    proposito = fd.get('proposito', '').strip()

    if tipo == 'Entrada':
        categoria = fd.get('categoria', 'Dízimos').strip()
    else:
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

app_py = re.sub(
    r'@app\.route\(\'/financas/caixa/novo\', methods=\[\'POST\'\]\)[\s\S]*?return redirect\(\'/\?aba=tesouraria\'\)',
    rota_caixa_nova,
    app_py
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_py)
print("✓ app.py: Migrações de Caixa/Banco, Despesas Gerais e Departamentos integradas!")

# =============================================================================
# 2. ATUALIZAR TEMPLATES/DASHBOARD.HTML COM O FORMULÁRIO DINÂMICO DA TESOURARIA
# =============================================================================
with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    dash = f.read()

# Substituir todo o bloco da aba tesouraria pelo novo formulário dinâmico
secao_tesouraria_nova = '''        <!-- ========================================================= -->
        <!-- ABA 6: CAIXA & TESOURARIA (COM SELEÇÃO CAIXA/BANCO & SAÍDAS) -->
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
                    <span class="text-sm font-black text-white">{{ "%.2f"|format(kpis.saldo_caixa_fisico) }} MT</span>
                </div>
                <div class="bg-white/10 px-3.5 py-2 rounded-xl text-right border border-white/10">
                    <span class="text-[9px] uppercase font-bold text-blue-300 block">Conta Bancária</span>
                    <span class="text-sm font-black text-white">{{ "%.2f"|format(kpis.saldo_banco) }} MT</span>
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
                    
                    <!-- 1. TIPO DE MOVIMENTO E CONTA (CAIXA OU BANCO) -->
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

                    <!-- 2. CAMPOS EXCLUSIVOS PARA ENTRADA -->
                    <div id="secao_entrada" class="space-y-3 p-3.5 bg-emerald-50/60 rounded-xl border border-emerald-200">
                        <div class="font-black text-emerald-900 text-[10px] uppercase">Classificação da Entrada</div>
                        <div>
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
                    </div>

                    <!-- 3. CAMPOS EXCLUSIVOS PARA SAÍDA (IGREJA GERAL OU DEPARTAMENTO) -->
                    <div id="secao_saida" class="hidden space-y-3 p-3.5 bg-rose-50/60 rounded-xl border border-rose-200">
                        <div class="font-black text-rose-900 text-[10px] uppercase">Origem / Destino da Saída</div>
                        
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">Local / Destino do Gasto *</label>
                            <select id="destino_tipo" name="destino_tipo" onchange="atualizarFormularioTesouraria()" class="w-full h-10 px-2 border-2 border-rose-300 rounded-xl bg-white font-black text-xs text-rose-950">
                                <option value="Igreja Geral">🏛️ Igreja em Geral / Igreja Mãe</option>
                                <option value="Departamento">👥 Departamentos da Igreja</option>
                            </select>
                        </div>

                        <!-- 3A. SE FOR IGREJA GERAL / IGREJA MÃE -->
                        <div id="saida_igreja_geral" class="space-y-2">
                            <label class="block font-bold text-slate-700 mb-1">Despesa Institucional da Igreja *</label>
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

                        <!-- 3B. SE FOR DEPARTAMENTO DA IGREJA -->
                        <div id="saida_departamento" class="hidden space-y-3">
                            <div>
                                <label class="block font-bold text-slate-700 mb-1">Selecione o Departamento *</label>
                                <select name="departamento" class="w-full h-10 px-2 border-2 border-slate-300 rounded-xl bg-white font-extrabold text-indigo-900">
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
                            </div>

                            <div>
                                <label class="block font-bold text-rose-900 mb-1">Propósito da Saída (Justificativa Obrigatória) *</label>
                                <textarea name="proposito" rows="2" placeholder="Ex: Compra de materiais didáticos para as crianças da EBD / Lanche da vigília..." class="w-full p-2.5 border-2 border-rose-300 rounded-xl bg-white font-medium"></textarea>
                            </div>
                        </div>
                    </div>

                    <!-- DESCRIÇÃO GERAL / COMPROVATIVO -->
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
                                <th class="py-2.5 px-2">Classificação / Destino</th>
                                <th class="py-2.5 px-2 text-right">Valor</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for cx in caixa[:15] %}
                            <tr class="border-b border-slate-100 hover:bg-slate-50">
                                <td class="py-2.5 px-2 text-slate-600 font-semibold">{{ cx.data_movimento }}</td>
                                <td class="py-2.5 px-2">
                                    {% if 'banco' in cx.conta|lower %}
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
                                    <div class="text-[10px] text-slate-400 truncate max-w-xs">{{ cx.descricao }}</div>
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

        <!-- SCRIPT PARA TROCA DINÂMICA DE CAMPOS -->
        <script>
            function atualizarFormularioTesouraria() {
                var tipo = document.getElementById('tipo_movimento').value;
                var secEntrada = document.getElementById('secao_entrada');
                var secSaida = document.getElementById('secao_saida');
                var destinoTipo = document.getElementById('destino_tipo').value;
                var saidaGeral = document.getElementById('saida_igreja_geral');
                var saidaDepto = document.getElementById('saida_departamento');

                if (tipo === 'Entrada') {
                    secEntrada.classList.remove('hidden');
                    secSaida.classList.add('hidden');
                } else {
                    secEntrada.classList.add('hidden');
                    secSaida.classList.remove('hidden');

                    if (destinoTipo === 'Departamento') {
                        saidaGeral.classList.add('hidden');
                        saidaDepto.classList.remove('hidden');
                    } else {
                        saidaGeral.classList.remove('hidden');
                        saidaDepto.classList.add('hidden');
                    }
                }
            }
        </script>
        {% endif %}'''

# Substituir na íntegra a aba tesouraria antiga
regex_aba_tesouraria = r'<!-- ========================================================= -->\s*<!-- ABA 6: CAIXA & TESOURARIA[\s\S]*?{% endif %}'
dash = re.sub(regex_aba_tesouraria, secao_tesouraria_nova, dash)

# Atualizar também o cabeçalho da aba financas para mostrar os saldos separados de Caixa Físico e Banco
cabecalho_financas_antigo = '''            <div class="text-right flex items-center gap-4">
                <div>
                    <span class="text-[10px] uppercase font-bold text-emerald-300 block">Saldo em Caixa</span>
                    <span class="text-2xl font-black text-white">{{ "%.2f"|format(kpis.saldo_caixa) }} MT</span>
                </div>
                <a href="/?aba=tesouraria" class="px-3.5 py-2 bg-amber-500 hover:bg-amber-600 text-slate-950 font-black rounded-xl text-xs shadow flex items-center gap-1.5">
                    <span>🔐</span><span>Ir para Lançamentos da Tesoureira</span>
                </a>
            </div>'''

cabecalho_financas_novo = '''            <div class="text-right flex items-center gap-4">
                <div class="bg-white/10 px-3 py-1.5 rounded-xl border border-white/10 text-right">
                    <span class="text-[9px] uppercase font-bold text-amber-300 block">💵 Caixa Físico</span>
                    <span class="text-sm font-black text-white">{{ "%.2f"|format(kpis.saldo_caixa_fisico) }} MT</span>
                </div>
                <div class="bg-white/10 px-3 py-1.5 rounded-xl border border-white/10 text-right">
                    <span class="text-[9px] uppercase font-bold text-blue-300 block">🏦 Conta Bancária</span>
                    <span class="text-sm font-black text-white">{{ "%.2f"|format(kpis.saldo_banco) }} MT</span>
                </div>
                <div>
                    <span class="text-[10px] uppercase font-bold text-emerald-300 block">Saldo Geral Total</span>
                    <span class="text-2xl font-black text-white">{{ "%.2f"|format(kpis.saldo_caixa) }} MT</span>
                </div>
                <a href="/?aba=tesouraria" class="px-3.5 py-2 bg-amber-500 hover:bg-amber-600 text-slate-950 font-black rounded-xl text-xs shadow flex items-center gap-1.5">
                    <span>🔐</span><span>Lançamentos</span>
                </a>
            </div>'''

if cabecalho_financas_antigo in dash:
    dash = dash.replace(cabecalho_financas_antigo, cabecalho_financas_novo)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(dash)

print("✓ templates/dashboard.html: Formulário dinâmico da Tesouraria e saldos separados integrados!")
print("=" * 80)
print("CONFIGURAÇÃO CONCLUÍDA COM TOTAL SUCESSO!")
print("=" * 80)