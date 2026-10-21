import os
import re
import subprocess
import jinja2

print("=" * 80)
print("A RESTAURAR A ESTRUTURA OFICIAL (COMMIT 61ba4ea) E APLICAR AS MELHORIAS...")
print("=" * 80)

caminho_dash = os.path.join('templates', 'dashboard.html')

# 1. RECUPERAR A ESTRUTURA ORIGINAL LIMPA DO COMMIT 61ba4ea
print("1. A extrair o template intacto do commit 61ba4ea...")
try:
    res = subprocess.run(["git", "show", "61ba4ea:templates/dashboard.html"], capture_output=True, text=True, check=True)
    html_base = res.stdout
    print("✓ Template limpo do commit 61ba4ea recuperado com sucesso!")
except Exception as e:
    print(f"Erro ao ler git show: {e}")
    exit(1)

# 2. INSERIR OS 4 CARDS NO TOPO DO GABINETE DO INSTRUTOR
pos_gab = html_base.find("Gabinete do Instrutor / Professor de Doutrina & Discipulado")
if pos_gab != -1:
    pos_card_div = html_base.rfind("<div", 0, pos_gab)
    cards = """<!-- 4 CARDS: SITUAÇÃO GERAL DE ENSINO (DASHBOARD PEDAGÓGICO) -->
        <div class="w-full grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6 text-xs">
            <div class="bg-white p-5 rounded-2xl shadow-sm border-l-4 border-indigo-600 border-slate-200">
                <span class="text-slate-500 text-[10px] font-bold uppercase block">Total de Formandos</span>
                <span class="text-2xl font-black text-indigo-950 mt-1 block">{{ doutrina|length }} Alunos</span>
                <span class="text-[10px] text-slate-400">Inscritos no currículo oficial</span>
            </div>
            <div class="bg-white p-5 rounded-2xl shadow-sm border-l-4 border-emerald-500 border-slate-200">
                <span class="text-slate-500 text-[10px] font-bold uppercase block">Aptos / Batismo</span>
                <span class="text-2xl font-black text-emerald-700 mt-1 block">🌊 {{ doutrina|selectattr('situacao', 'equalto', 'Apto / Aprovado')|list|length }} Prontos</span>
                <span class="text-[10px] text-emerald-600 font-bold">Aproveitamento >= 70%</span>
            </div>
            <div class="bg-white p-5 rounded-2xl shadow-sm border-l-4 border-amber-500 border-slate-200">
                <span class="text-slate-500 text-[10px] font-bold uppercase block">Em Formação Ativa</span>
                <span class="text-2xl font-black text-amber-700 mt-1 block">📖 {{ doutrina|rejectattr('situacao', 'equalto', 'Apto / Aprovado')|list|length }} Alunos</span>
                <span class="text-[10px] text-slate-400">Em estudo nas classes</span>
            </div>
            <div class="bg-white p-5 rounded-2xl shadow-sm border-l-4 border-blue-500 border-slate-200">
                <span class="text-slate-500 text-[10px] font-bold uppercase block">Corpo Docente</span>
                <span class="text-2xl font-black text-blue-900 mt-1 block">👨‍🏫 {{ professores_cadastrados|length if professores_cadastrados is defined and professores_cadastrados else 1 }} Instrutor(es)</span>
                <span class="text-[10px] text-slate-400">Docentes credenciados</span>
            </div>
        </div>

        """
    html_base = html_base[:pos_card_div] + cards + html_base[pos_card_div:]
    print("✓ 4 Cards pedagógicos inseridos no topo da área principal!")

# 3. INSERIR O FORMULÁRIO DE CADASTRO DE PROFESSOR
pos_btn = html_base.find("Gravar Inscrição & Credenciais")
if pos_btn != -1:
    pos_form_end = html_base.find("</form>", pos_btn) + len("</form>")
    prof_form = """

                <!-- CADASTRO DE PROFESSOR / INSTRUTOR -->
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
                </div>"""
    html_base = html_base[:pos_form_end] + prof_form + html_base[pos_form_end:]
    print("✓ Formulário de credenciamento docente integrado!")

# 4. ATUALIZAR SELETORES PARA EVITAR BARRAS DE ROLAGEM E CORTES
pat_selector = r'<div class="grid grid-cols-2 gap-2">[\s\S]*?name="professor"[\s\S]*?<\/div>\s*<\/div>'
replacement_selector = """<div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
                        <div class="min-w-0">
                            <label class="block font-bold text-slate-700 mb-1 text-xs">Classe *</label>
                            <select name="classe" required class="w-full h-11 px-3 border border-slate-300 rounded-xl bg-white font-bold text-xs text-slate-800 focus:border-indigo-600 focus:outline-none shadow-sm cursor-pointer truncate">
                                <option value="Preparação para Batismo nas Águas">Preparação para Batismo nas Águas</option>
                                <option value="Discipulado de Novos Convertidos">Discipulado de Novos Convertidos</option>
                                <option value="Classe I - Primeiros Passos">Classe I - Primeiros Passos</option>
                                <option value="Classe II - Vida Cristã">Classe II - Vida Cristã</option>
                                <option value="Classe III - Maturidade Cristã">Classe III - Maturidade Cristã</option>
                            </select>
                        </div>
                        <div class="min-w-0">
                            <label class="block font-bold text-slate-700 mb-1 text-xs">Instrutor / Mentor *</label>
                            <select name="professor" required class="w-full h-11 px-3 border border-slate-300 rounded-xl bg-white font-bold text-xs text-slate-800 focus:border-indigo-600 focus:outline-none shadow-sm cursor-pointer truncate">
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

html_base = re.sub(pat_selector, replacement_selector, html_base)
print("✓ Seletores de Classe e Mentor ajustados com largura proporcional!")

# 5. TESTAR E VALIDAR A SINTAXE JINJA2
env = jinja2.Environment()
env.parse(html_base)
print("✓ Validação Jinja2: Aprovado com ZERO erros de sintaxe!")

with open(caminho_dash, 'w', encoding='utf-8') as f:
    f.write(html_base)

print("✓ templates/dashboard.html regravado com layout panorâmico perfeito!")
print("=" * 80)
print(">>> PROCESSO CONCLUÍDO! ENVIE PARA O GIT ABAIXO! <<<")
print("=" * 80)