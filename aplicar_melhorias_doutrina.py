import os
import re
import jinja2

print("=" * 80)
print("A APLICAR INDICADORES, SELETORES E FORMULÁRIO DE PROFESSORES...")
print("=" * 80)

caminho = os.path.join('templates', 'dashboard.html')

with open(caminho, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Validar sintaxe inicial
env = jinja2.Environment()
env.parse(html)
print("✓ Template base carregado e 100% válido no Jinja2!")

# 2. Inserir os 4 cartões de estatísticas pedagógicas logo acima do Gabinete do Instrutor
alvo_gabinete = "Gabinete do Instrutor / Professor de Doutrina & Discipulado"
pos_gabinete = html.find(alvo_gabinete)
if pos_gabinete != -1 and "<!-- 4 CARDS: SITUAÇÃO GERAL DE ENSINO" not in html:
    pos_div_card = html.rfind('<div', 0, pos_gabinete)
    cards_html = """
        <!-- 4 CARDS: SITUAÇÃO GERAL DE ENSINO (DASHBOARD PEDAGÓGICO) -->
        <div class="w-full grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6 text-xs">
            <div class="bg-white p-4.5 rounded-2xl shadow-sm border-l-4 border-indigo-600 border-slate-200">
                <span class="text-slate-500 text-[10px] font-bold uppercase block">Total de Formandos</span>
                <span class="text-2xl font-black text-indigo-950 mt-1 block">{{ doutrina|length }} Alunos</span>
                <span class="text-[10px] text-slate-400">Inscritos no currículo</span>
            </div>
            <div class="bg-white p-4.5 rounded-2xl shadow-sm border-l-4 border-emerald-500 border-slate-200">
                <span class="text-slate-500 text-[10px] font-bold uppercase block">Aptos / Batismo</span>
                <span class="text-2xl font-black text-emerald-700 mt-1 block">🌊 {{ doutrina|selectattr('situacao', 'equalto', 'Apto / Aprovado')|list|length }} Prontos</span>
                <span class="text-[10px] text-emerald-600 font-bold">Aproveitamento >= 70%</span>
            </div>
            <div class="bg-white p-4.5 rounded-2xl shadow-sm border-l-4 border-amber-500 border-slate-200">
                <span class="text-slate-500 text-[10px] font-bold uppercase block">Em Formação Ativa</span>
                <span class="text-2xl font-black text-amber-700 mt-1 block">📖 {{ doutrina|rejectattr('situacao', 'equalto', 'Apto / Aprovado')|list|length }} Alunos</span>
                <span class="text-[10px] text-slate-400">Em estudo nas classes</span>
            </div>
            <div class="bg-white p-4.5 rounded-2xl shadow-sm border-l-4 border-blue-500 border-slate-200">
                <span class="text-slate-500 text-[10px] font-bold uppercase block">Corpo Docente</span>
                <span class="text-2xl font-black text-blue-900 mt-1 block">👨‍🏫 {{ professores_cadastrados|length if professores_cadastrados is defined and professores_cadastrados else 1 }} Instrutor(es)</span>
                <span class="text-[10px] text-slate-400">Credenciados</span>
            </div>
        </div>
"""
    html = html[:pos_div_card] + cards_html + html[pos_div_card:]
    print("✓ 4 Cartões de Indicadores inseridos com sucesso!")

# 3. Inserir o formulário de cadastro de Professor logo abaixo do formulário de alunos
alvo_btn = "Gravar Inscrição & Credenciais"
pos_btn = html.find(alvo_btn)
if pos_btn != -1 and "Cadastrar Novo Professor / Instrutor" not in html:
    pos_end_form = html.find('</form>', pos_btn)
    if pos_end_form != -1:
        prof_form = """
                <!-- FORMULÁRIO: CADASTRAR PROFESSOR / INSTRUTOR -->
                <div class="mt-6 pt-5 border-t border-slate-200 space-y-3">
                    <div class="flex items-center gap-2">
                        <span class="text-base">👨‍🏫</span>
                        <div>
                            <h4 class="font-black text-xs text-slate-900 uppercase">Cadastrar Novo Professor / Instrutor</h4>
                            <p class="text-[10px] text-slate-500">Credencie um instrutor com acesso restrito ao ensino</p>
                        </div>
                    </div>
                    <form action="/doutrina/gravar_professor" method="POST" class="space-y-2 text-xs">
                        <input type="text" name="nome_professor" required placeholder="Nome Completo do Instrutor" class="w-full h-10 px-3 border border-slate-300 rounded-xl focus:border-indigo-600 focus:outline-none">
                        <div class="grid grid-cols-2 gap-2">
                            <input type="text" name="usuario_professor" required placeholder="Usuário (ex: prof.mateus)" class="w-full h-9 px-2 border border-slate-300 rounded-lg bg-white font-bold text-xs">
                            <input type="text" name="senha_professor" required value="prof123" class="w-full h-9 px-2 border border-slate-300 rounded-lg bg-white font-bold text-xs">
                        </div>
                        <button type="submit" class="w-full py-2.5 bg-indigo-900 hover:bg-indigo-950 text-white font-bold rounded-xl shadow cursor-pointer text-xs transition">
                            + Credenciar Professor
                        </button>
                    </form>
                </div>
"""
        insert_at = pos_end_form + len('</form>')
        html = html[:insert_at] + prof_form + html[insert_at:]
        print("✓ Formulário de credenciamento de professores inserido!")

# 4. Ajustar seletores de Classe e Mentor para layout fluido (sem barras de rolagem)
padrao_seletores = r'<div class="grid grid-cols-2 gap-2">[\s\S]*?name="professor"[\s\S]*?<\/div>\s*<\/div>'
seletores_fluidos = """<div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
                        <div>
                            <label class="block font-bold text-slate-700 mb-1 text-xs">Classe *</label>
                            <select name="classe" required class="w-full h-11 px-3 border border-slate-300 rounded-xl bg-white font-bold text-xs text-slate-800 focus:border-indigo-600 focus:outline-none shadow-sm cursor-pointer">
                                <option value="Preparação para Batismo nas Águas">Preparação para Batismo nas Águas</option>
                                <option value="Discipulado de Novos Convertidos">Discipulado de Novos Convertidos</option>
                                <option value="Classe I - Primeiros Passos">Classe I - Primeiros Passos</option>
                                <option value="Classe II - Vida Cristã">Classe II - Vida Cristã</option>
                                <option value="Classe III - Maturidade Cristã">Classe III - Maturidade Cristã</option>
                            </select>
                        </div>
                        <div>
                            <label class="block font-bold text-slate-700 mb-1 text-xs">Instrutor / Mentor *</label>
                            <select name="professor" required class="w-full h-11 px-3 border border-slate-300 rounded-xl bg-white font-bold text-xs text-slate-800 focus:border-indigo-600 focus:outline-none shadow-sm cursor-pointer">
                                <option value="Anselmo Leonardo Munguambe">Anselmo Leonardo Munguambe</option>
                                <option value="Pastor Dirigente">Pastor Dirigente</option>
                                {% if professores_cadastrados is defined and professores_cadastrados %}
                                    {% for p in professores_cadastrados %}
                                    <option value="{{ p.nome }}">{{ p.nome }}</option>
                                    {% endfor %}
                                {% endif %}
                            </select>
                        </div>
                    </div>"""

if re.search(padrao_seletores, html):
    html = re.sub(padrao_seletores, seletores_fluidos, html, count=1)
    print("✓ Seletores ajustados para formato fluido!")

# 5. Validar novamente no Jinja2
env.parse(html)
print("✓ Validação Jinja2: Aprovada com ZERO erros de sintaxe!")

with open(caminho, 'w', encoding='utf-8') as f:
    f.write(html)
print("✓ templates/dashboard.html atualizado e pronto para produção!")

print("=" * 80)
print(">>> TUDO PRONTO! EXECUTE OS COMANDOS GIT PARA ATUALIZAR O RENDER! <<<")
print("=" * 80)