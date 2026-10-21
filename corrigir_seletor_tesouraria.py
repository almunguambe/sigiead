import os
import re
import subprocess
import jinja2

print("=" * 80)
print("A ELIMINAR A BARRA PRETA E A POVOAR CATEGORIAS NA TESOURARIA...")
print("=" * 80)

caminho_dash = os.path.join('templates', 'dashboard.html')

with open(caminho_dash, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. LOCALIZAR O FORMULÁRIO DE LANÇAMENTO DA TESOURARIA
pos_titulo = html.find("Lançar Entrada ou Saída de Valores")
if pos_titulo == -1:
    pos_titulo = html.find("Confirmar e Lançar Movimento")

if pos_titulo == -1:
    print("Erro: Formulário de lançamento não localizado em templates/dashboard.html.")
    exit(1)

pos_form_inicio = html.rfind("<form", 0, pos_titulo)
if pos_form_inicio == -1:
    pos_form_inicio = html.find("<form", pos_titulo)

pos_btn = html.find("Confirmar e Lançar Movimento", pos_form_inicio)
pos_form_fim = html.find("</form>", pos_btn) + len("</form>")

form_antigo = html[pos_form_inicio:pos_form_fim]

# Preservar o endpoint de action exato já configurado no backend
m_action = re.search(r'action=["\']([^"\']+)["\']', form_antigo)
action_url = m_action.group(1) if m_action else '/caixa/lancar'
print(f"✓ Rota de submissão preservada: {action_url}")

# 2. CONSTRUIR FORMULÁRIO FLUIDO SEM OVERFLOW E COM CATEGORIAS PREDEFINIDAS
novo_formulario = f"""<form action="{action_url}" method="POST" class="space-y-4 text-xs">
                        
                        <!-- LINHA 1: TIPO DE MOVIMENTO E CONTA FINANCEIRA -->
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                            <div class="min-w-0">
                                <label class="block font-bold text-slate-700 mb-1">Tipo de Movimento *</label>
                                <select id="tipo_movimento" name="tipo" required onchange="alternarCategoriasTesouraria()" class="w-full h-11 px-3 bg-white border border-slate-300 rounded-xl font-bold text-xs text-slate-800 focus:border-indigo-600 focus:outline-none shadow-sm cursor-pointer">
                                    <option value="Entrada" selected>🟢 Entrada (+)</option>
                                    <option value="Saída">🔴 Saída (-)</option>
                                </select>
                            </div>
                            <div class="min-w-0">
                                <label class="block font-bold text-slate-700 mb-1">Conta Financeira *</label>
                                <select name="conta" required class="w-full h-11 px-3 bg-white border border-slate-300 rounded-xl font-bold text-xs text-slate-800 focus:border-indigo-600 focus:outline-none shadow-sm cursor-pointer truncate">
                                    <option value="Caixa Físico (Numerário)" selected>💵 Caixa Físico (Numerário)</option>
                                    <option value="Conta Móvel / M-Pesa">📱 Conta Móvel (M-Pesa / E-Mola)</option>
                                    <option value="Conta Bancária (Banco)">🏦 Conta Bancária Institucional</option>
                                </select>
                            </div>
                        </div>

                        <!-- LINHA 2: ÂMBITO DO MOVIMENTO -->
                        <div class="min-w-0">
                            <label class="block font-bold text-slate-700 mb-1">Âmbito do Movimento (Onde entra / De onde sai) *</label>
                            <select id="ambito_movimento" name="ambito" required class="w-full h-11 px-3 bg-white border border-slate-300 rounded-xl font-bold text-xs text-slate-800 focus:border-indigo-600 focus:outline-none shadow-sm cursor-pointer truncate">
                                <option value="1. Igreja Geral" selected>🏛️ 1. Igreja Geral (Inclui Contribuições das Zonas)</option>
                                <option value="2. Escola Bíblica / Doutrina">📖 2. Escola Bíblica / Doutrina & Batismo</option>
                                <option value="3. Departamento de Senhoras">👩 3. Departamento de Senhoras</option>
                                <option value="4. Juventude Cristã">🧑 4. Juventude Cristã</option>
                                <option value="5. Construção & Obras">🏗️ 5. Fundo de Construção & Obras</option>
                            </select>
                        </div>

                        <!-- LINHA 3: DATA E VALOR -->
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                            <div class="min-w-0">
                                <label class="block font-bold text-slate-700 mb-1">Data da Operação *</label>
                                <input type="date" name="data_operacao" required id="data_operacao_caixa" class="w-full h-11 px-3 border border-slate-300 rounded-xl bg-white text-xs font-semibold text-slate-800 focus:border-indigo-600 focus:outline-none shadow-sm">
                            </div>
                            <div class="min-w-0">
                                <label class="block font-bold text-slate-700 mb-1">Valor (MZN) *</label>
                                <input type="number" step="0.01" min="0" name="valor" required placeholder="Ex: 2500.00" class="w-full h-11 px-3 border-2 border-emerald-400 rounded-xl bg-white text-sm font-black text-slate-900 focus:border-emerald-600 focus:outline-none shadow-sm">
                            </div>
                        </div>

                        <!-- LINHA 4: CAIXA DE CATEGORIA LIMPA (SEM BARRA PRETA) -->
                        <div id="box_categoria_tesouraria" class="p-4 bg-emerald-50/60 border border-emerald-300 rounded-2xl space-y-2 transition-all duration-200">
                            <span id="badge_categoria_titulo" class="font-black text-[10px] uppercase text-emerald-900 block tracking-wider">
                                🟢 RECEITA DA IGREJA GERAL (ENVOLVE ZONAS E TODA A CONGREGAÇÃO)
                            </span>
                            <div class="min-w-0">
                                <label id="label_categoria_tesouraria" class="block font-bold text-slate-700 mb-1 text-xs">Categoria de Entrada Local *</label>
                                <select id="seletor_categoria_tesouraria" name="categoria" required class="w-full h-11 px-3 bg-white border border-slate-300 rounded-xl font-bold text-xs text-slate-800 focus:border-emerald-600 focus:outline-none shadow-sm cursor-pointer">
                                    <option value="Dízimos dos Membros">Dízimos dos Membros</option>
                                    <option value="Ofertas Gerais de Culto">Ofertas Gerais de Culto</option>
                                    <option value="Ofertas de Construção / Obras">Ofertas de Construção / Obras</option>
                                    <option value="Contribuições das Zonas / Bairros">Contribuições das Zonas / Bairros</option>
                                    <option value="Primícias">Primícias</option>
                                    <option value="Votos e Campanhas">Votos e Campanhas</option>
                                    <option value="Doações Especiais">Doações Especiais</option>
                                    <option value="Vendas e Eventos">Vendas e Eventos</option>
                                    <option value="Outras Entradas">Outras Entradas</option>
                                </select>
                            </div>
                        </div>

                        <!-- LINHA 5: OBSERVAÇÕES / RECIBO -->
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">Observações Adicionais / Recibo</label>
                            <input type="text" name="descricao" placeholder="Nº do recibo, beneficiário ou detalhe complementar..." class="w-full h-11 px-3 border border-slate-300 rounded-xl bg-white text-xs font-medium text-slate-800 focus:border-indigo-600 focus:outline-none shadow-sm">
                        </div>

                        <!-- BOTÃO DE SUBMISSÃO -->
                        <button type="submit" class="w-full py-3.5 bg-emerald-700 hover:bg-emerald-800 text-white font-black rounded-xl shadow cursor-pointer text-xs transition flex items-center justify-center gap-2">
                            <span>💾</span> Confirmar e Lançar Movimento
                        </button>
                    </form>"""

html_atualizado = html[:pos_form_inicio] + novo_formulario + html[pos_form_fim:]

# 3. ADICIONAR O SCRIPT DE ALTERNÂNCIA ENTRADA/SAÍDA ANTES DE </body>
script_dinamico = """
    <!-- SCRIPT DE ALTERNÂNCIA DE CATEGORIAS DA TESOURARIA -->
    <script>
        function alternarCategoriasTesouraria() {
            const tipo = document.getElementById('tipo_movimento')?.value || 'Entrada';
            const box = document.getElementById('box_categoria_tesouraria');
            const badge = document.getElementById('badge_categoria_titulo');
            const label = document.getElementById('label_categoria_tesouraria');
            const seletor = document.getElementById('seletor_categoria_tesouraria');
            if (!seletor) return;

            const categoriasEntrada = [
                "Dízimos dos Membros",
                "Ofertas Gerais de Culto",
                "Ofertas de Construção / Obras",
                "Contribuições das Zonas / Bairros",
                "Primícias",
                "Votos e Campanhas",
                "Doações Especiais",
                "Vendas e Eventos",
                "Outras Entradas"
            ];

            const categoriasSaida = [
                "Manutenção e Obras do Templo",
                "Energia Elétrica e Água",
                "Ação Social e Beneficência",
                "Sustento Pastoral e Obreiros",
                "Material de Escritório e Secretaria",
                "Comunicação, Som e Internet",
                "Eventos, Missões e Conferências",
                "Ajuda de Custo e Transporte",
                "Outras Saídas"
            ];

            const lista = (tipo === 'Saída' || tipo === 'Saida') ? categoriasSaida : categoriasEntrada;

            if (tipo === 'Saída' || tipo === 'Saida') {
                if (box) box.className = "p-4 bg-rose-50/60 border border-rose-300 rounded-2xl space-y-2 transition-all duration-200";
                if (badge) {
                    badge.className = "font-black text-[10px] uppercase text-rose-900 block tracking-wider";
                    badge.innerText = "🔴 DESPESA / SAÍDA LOCAL DA CONGREGAÇÃO";
                }
                if (label) label.innerText = "Categoria de Saída Local *";
            } else {
                if (box) box.className = "p-4 bg-emerald-50/60 border border-emerald-300 rounded-2xl space-y-2 transition-all duration-200";
                if (badge) {
                    badge.className = "font-black text-[10px] uppercase text-emerald-900 block tracking-wider";
                    badge.innerText = "🟢 RECEITA DA IGREJA GERAL (ENVOLVE ZONAS E TODA A CONGREGAÇÃO)";
                }
                if (label) label.innerText = "Categoria de Entrada Local *";
            }

            seletor.innerHTML = lista.map(c => `<option value="${c}">${c}</option>`).join('');
        }

        document.addEventListener('DOMContentLoaded', function() {
            const dataInput = document.getElementById('data_operacao_caixa');
            if (dataInput && !dataInput.value) {
                dataInput.value = new Date().toISOString().split('T')[0];
            }
            alternarCategoriasTesouraria();
        });
    </script>
</body>
"""

if "alternarCategoriasTesouraria" not in html_atualizado and "</body>" in html_atualizado:
    html_atualizado = html_atualizado.replace("</body>", script_dinamico, 1)
    print("✓ Script dinâmico de categorias inserido!")

# 4. VALIDAÇÃO RIGOROSA NO MOTOR JINJA2
env = jinja2.Environment()
try:
    env.parse(html_atualizado)
    print("✓ Validação Jinja2: APROVADO COM ZERO ERROS!")
except Exception as e:
    print(f"Erro no Jinja2: {e}")
    exit(1)

with open(caminho_dash, 'w', encoding='utf-8') as f:
    f.write(html_atualizado)
print("✓ templates/dashboard.html regravado com sucesso!")

# 5. SINCRONIZAR COM O GITHUB E O RENDER
print("=" * 80)
print("A ENVIAR ATUALIZAÇÃO PARA O GITHUB & RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "templates/dashboard.html"], check=True)
subprocess.run(["git", "commit", "-m", "Fix: remover barra preta da tesouraria e preencher categorias de entrada e saida"], check=True)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("=" * 80)
print(">>> ATUALIZAÇÃO CONCLUÍDA COM TOTAL SUCESSO! <<<")
print("=" * 80)