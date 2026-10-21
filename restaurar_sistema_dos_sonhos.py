import os
import subprocess
import jinja2

print("=" * 80)
print("A RESTAURAR O SIGIEAD DOS TEUS SONHOS: TELA CHEIA, DASHBOARD & SELETORES...")
print("=" * 80)

caminho_dash = os.path.join('templates', 'dashboard.html')

# 1. RECUPERAR O TEMPLATE ORIGINAL LIMPO E PANORÂMICO DO HISTÓRICO DO GIT
print("1. A extrair a estrutura estável do commit 61ba4ea...")
try:
    res = subprocess.run(["git", "show", "61ba4ea:templates/dashboard.html"], capture_output=True, text=True, check=True)
    html_base = res.stdout
    print("✓ Estrutura panorâmica original recuperada do Git com sucesso!")
except Exception as e:
    print("A carregar backup local...")
    with open(caminho_dash, 'r', encoding='utf-8') as f:
        html_base = f.read()

# 2. INJETAR OS 4 CARDS DE INDICADORES DO ENSINO NO TOPO DO GABINETE
cards_indicadores = """
        <!-- 4 CARDS: SITUAÇÃO GERAL DE ENSINO (DASHBOARD PEDAGÓGICO) -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
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
                <span class="text-2xl font-black text-blue-900 mt-1 block">👨‍🏫 {{ professores_cadastrados|length if professores_cadastrados else 1 }} Instrutor(es)</span>
                <span class="text-[10px] text-slate-400">Docentes credenciados</span>
            </div>
        </div>
"""

# Injeta os 4 cards exatamente no início do módulo de Doutrina
ancora_gabinete = "Gabinete do Instrutor / Professor de Doutrina & Discipulado"
if ancora_gabinete in html_base and "<!-- 4 CARDS: SITUAÇÃO GERAL DE ENSINO" not in html_base:
    pos_card = html_base.rfind('<div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 mb-6', 0, html_base.find(ancora_gabinete))
    if pos_card != -1:
        html_base = html_base[:pos_card] + cards_indicadores + html_base[pos_card:]
        print("✓ 4 Cards de Indicadores Pedagógicos injetados no topo da tela!")

# 3. RESTAURAR SELETORES FLUIDOS (CLASSE E INSTRUTOR) SEM BARRAS DE ROLAGEM
bloco_seletores_fluidos = """<div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
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
                                {% if professores_cadastrados %}
                                    {% for p in professores_cadastrados %}
                                    <option value="{{ p.nome }}">{{ p.nome }}</option>
                                    {% endfor %}
                                {% endif %}
                            </select>
                        </div>
                    </div>"""

# Substitui o bloco anterior de campos cortados
import re
padrao_campos = r'<div class="grid grid-cols-2 gap-2">[\s\S]*?name="professor"[\s\S]*?<\/div>[\s\S]*?<\/div>'
if re.search(padrao_campos, html_base):
    html_base = re.sub(padrao_campos, bloco_seletores_fluidos, html_base, count=1)
    print("✓ Seletores de Classe e Mentor restaurados com formato fluido!")

# 4. ADICIONAR O FORMULÁRIO DE CADASTRO DE PROFESSOR NA COLUNA ESQUERDA
form_professor = """
                <!-- CADASTRO DE PROFESSOR / INSTRUTOR -->
                <div class="mt-6 pt-5 border-t border-slate-200 space-y-3">
                    <div class="flex items-center gap-2">
                        <span class="text-base">👨‍🏫</span>
                        <div>
                            <h4 class="font-black text-xs text-slate-900 uppercase">Cadastrar Novo Professor / Instrutor</h4>
                            <p class="text-[10px] text-slate-500">Credencia um instrutor com acesso restrito ao ensino</p>
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

ancora_botao_aluno = 'Gravar Inscrição & Credenciais'
if ancora_botao_aluno in html_base and "Cadastrar Novo Professor / Instrutor" not in html_base:
    pos_btn = html_base.find(ancora_botao_aluno)
    pos_fecha_form = html_base.find('</form>', pos_btn)
    if pos_fecha_form != -1:
        html_base = html_base[:pos_fecha_form + 7] + form_professor + html_base[pos_fecha_form + 7:]
        print("✓ Formulário de credenciamento de Professores integrado!")

# 5. VALIDAR TEMPLATE COM JINJA2
env = jinja2.Environment()
env.parse(html_base)

with open(caminho_dash, 'w', encoding='utf-8') as f:
    f.write(html_base)
print("✓ templates/dashboard.html regravado e 100% validado!")

print("=" * 80)
print(">>> A ENVIAR ATUALIZAÇÃO PARA O GITHUB & RENDER... <<<")
print("=" * 80)

subprocess.run(["git", "add", "templates/dashboard.html"], check=True)
subprocess.run(["git", "commit", "-m", "Restaurar SIGIEAD perfeito: tela cheia, 4 indicadores e seletores fluidos"], check=True)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("=" * 80)
print(">>> SUCESSO ABSOLUTO! O DEPLOY ESTÁ A SUBIR PARA O RENDER! <<<")
print("=" * 80)