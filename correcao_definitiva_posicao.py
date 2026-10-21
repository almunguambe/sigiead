import os
import subprocess
import jinja2

print("=" * 80)
print("A RESTAURAR BASE LIMPA E A POSICIONAR OS CARDS NA ÁREA PRINCIPAL...")
print("=" * 80)

caminho = os.path.join('templates', 'dashboard.html')

# 1. RECUPERAR TEMPLATE ORIGINAL LIMPO DO COMMIT 61ba4ea
subprocess.run(["git", "checkout", "61ba4ea", "--", "templates/dashboard.html"], check=True)

with open(caminho, 'r', encoding='utf-8') as f:
    html = f.read()

# Validar base inicial
env = jinja2.Environment()
env.parse(html)
print("✓ Base original restaurada com sucesso e 100% íntegra!")

# 2. LOCALIZAR O BLOCO DE DOUTRINA ESTRITAMENTE DEPOIS DO FECHO DA SIDEBAR (</aside>)
pos_aside_end = html.find('</aside>')
if pos_aside_end == -1:
    print("Erro: tag </aside> não encontrada.")
    exit(1)

# Encontra a tag de Doutrina que está dentro de <main>, NUNCA a que está dentro do menu lateral
pos_doutrina_main = html.find("{% if aba_ativa == 'doutrina' %}", pos_aside_end)
if pos_doutrina_main == -1:
    print("Erro: Bloco de Doutrina não encontrado dentro de <main>.")
    exit(1)

# 3. DEFINIR OS 4 CARDS PARA A ÁREA PRINCIPAL
cards_html = """
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

tag_doutrina = "{% if aba_ativa == 'doutrina' %}"
html = html[:pos_doutrina_main + len(tag_doutrina)] + "\n" + cards_html + html[pos_doutrina_main + len(tag_doutrina):]
print("✓ 4 Cards inseridos corretamente no início da área principal (fora da barra lateral)!")

# 4. INSERIR O FORMULÁRIO DE PROFESSOR NA COLUNA ESQUERDA DA DOUTRINA
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
        print("✓ Formulário de credenciamento docente inserido na Doutrina!")

# 5. VALIDAR SINTAXE JINJA2
env.parse(html)
print("✓ Validação Jinja2: APROVADO! Zero erros de sintaxe.")

with open(caminho, 'w', encoding='utf-8') as f:
    f.write(html)

print("✓ templates/dashboard.html atualizado e pronto para produção!")

# 6. ENVIAR DIRETAMENTE PARA O GITHUB E O RENDER
print("=" * 80)
print("A ENVIAR ATUALIZAÇÃO PARA O GITHUB & RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "templates/dashboard.html"], check=True)
subprocess.run(["git", "commit", "-m", "Fix: isolar barra lateral e posicionar cards de ensino estritamente em main"], check=True)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("=" * 80)
print(">>> ATUALIZAÇÃO CONCLUÍDA COM SUCESSO! <<<")
print("=" * 80)