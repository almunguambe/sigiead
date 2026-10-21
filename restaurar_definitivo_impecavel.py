import os
import subprocess
import jinja2

print("=" * 80)
print("1. A RESTAURAR TEMPLATES/DASHBOARD.HTML LIMPO DO COMMIT 61ba4ea...")
print("=" * 80)

# 1. Recuperar o arquivo original intacto do Git
subprocess.run(["git", "checkout", "61ba4ea", "--", "templates/dashboard.html"], check=True)

caminho = os.path.join('templates', 'dashboard.html')
with open(caminho, 'r', encoding='utf-8') as f:
    html = f.read()

# Validar que a base recuperada está 100% integra
env = jinja2.Environment()
env.parse(html)
print("✓ Base original recuperada e 100% íntegra!")

# 2. Definir os 4 cartões pedagógicos
cards = """
        <!-- 4 CARDS: SITUAÇÃO GERAL DE ENSINO (DASHBOARD PEDAGÓGICO) -->
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

# Inserir os 4 cartões exclusivamente dentro da aba de doutrina
target_doutrina = "{% if aba_ativa == 'doutrina' %}"
if target_doutrina in html:
    html = html.replace(target_doutrina, target_doutrina + "\n" + cards, 1)
    print("✓ 4 Cartões inseridos exclusivamente na aba Doutrina!")

# 3. Inserir o cadastro de professores exclusivamente na coluna de inscrições de Doutrina
alvo_btn = "Gravar Inscrição & Credenciais"
pos_btn = html.find(alvo_btn)
if pos_btn != -1:
    pos_end_form = html.find('</form>', pos_btn)
    if pos_end_form != -1:
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
        insert_at = pos_end_form + len('</form>')
        html = html[:insert_at] + prof_form + html[insert_at:]
        print("✓ Formulário de credenciamento docente integrado à Doutrina!")

# 4. Validar rigorosamente a integridade final com Jinja2
env.parse(html)
print("✓ Validação Jinja2: Aprovado com ZERO erros de sintaxe!")

with open(caminho, 'w', encoding='utf-8') as f:
    f.write(html)
print("✓ templates/dashboard.html gravado com sucesso!")

# 5. Enviar commit e push para o Render
print("=" * 80)
print("A ENVIAR PARA O GITHUB E ATUALIZAR O RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "templates/dashboard.html"], check=True)
subprocess.run(["git", "commit", "-m", "Restaurar layout oficial impecavel: sidebar limpa, Raio-X limpo e Doutrina com indicadores"], check=True)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("=" * 80)
print(">>> PROCESSO CONCLUÍDO COM SUCESSO ABSOLUTO! <<<")
print("=" * 80)