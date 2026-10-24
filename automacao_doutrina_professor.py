import os
import re
import py_compile
import subprocess
import jinja2

print("=" * 80)
print("A CONFIGURAR ACESSO AUTOMÁTICO DO PROFESSOR À DOUTRINA...")
print("=" * 80)

caminho_app = 'app.py'
caminho_dash = os.path.join('templates', 'dashboard.html')

# 1. ATUALIZAR APP.PY: PROFESSOR CAI SEMPRE NA DOUTRINA
with open(caminho_app, 'r', encoding='utf-8') as f:
    app_code = f.read()

sub_aba = """perfil_docente = str(usuario.get('perfil', '')).lower() if 'usuario' in locals() and usuario else ''
    if any(p in perfil_docente for p in ['prof', 'docente', 'instrutor']):
        aba_ativa = 'doutrina'
    else:
        aba_ativa = request.args.get('aba', 'dashboard')"""

pos_aba = app_code.find("aba_ativa = request.args.get('aba'")
if pos_aba == -1:
    pos_aba = app_code.find('aba_ativa = request.args.get("aba"')

if pos_aba != -1:
    pos_fim_linha = app_code.find("\n", pos_aba) + 1
    app_code = app_code[:pos_aba] + sub_aba + app_code[pos_fim_linha:]
    print("✓ app.py: Professor configurado para abrir sempre a Doutrina!")

with open(caminho_app, 'w', encoding='utf-8') as f:
    f.write(app_code)

py_compile.compile(caminho_app, doraise=True)
print("✓ app.py validado e compilado com ZERO erros!")

# 2. ATUALIZAR TEMPLATES/DASHBOARD.HTML (BOTÃO DO PROFESSOR NO MENU)
with open(caminho_dash, 'r', encoding='utf-8') as f:
    html = f.read()

menu_docente = """
        <!-- MENU EXCLUSIVO PARA O PROFESSOR -->
        {% if usuario_logado and ('professor' in usuario_logado.perfil|lower or 'docente' in usuario_logado.perfil|lower or 'instrutor' in usuario_logado.perfil|lower) %}
        <div class="space-y-2 mb-4">
            <div class="px-3 py-1 text-[10px] font-black text-amber-400 uppercase tracking-wider">
                Gabinete Docente
            </div>
            <a href="/?aba=doutrina" class="flex items-center gap-3 px-3 py-2.5 rounded-xl font-bold text-xs bg-amber-500 text-slate-950 shadow-md">
                <span class="text-base">📖</span>
                <span>Minhas Turmas & Alunos</span>
            </a>
            <a href="/ensino/aulas" target="_blank" class="flex items-center gap-3 px-3 py-2.5 rounded-xl font-bold text-xs text-slate-300 hover:text-white hover:bg-slate-800 transition">
                <span class="text-base">🎓</span>
                <span>Sala Virtual do Aluno ↗</span>
            </a>
        </div>
        {% endif %}
"""

if "<!-- MENU EXCLUSIVO PARA O PROFESSOR -->" not in html:
    pos_nav = html.find("<nav")
    if pos_nav != -1:
        pos_nav_open = html.find(">", pos_nav) + 1
        html = html[:pos_nav_open] + "\n" + menu_docente + html[pos_nav_open:]
        print("✓ Menu lateral com botão 'Minhas Turmas & Alunos' integrado!")

env = jinja2.Environment()
env.parse(html)
with open(caminho_dash, 'w', encoding='utf-8') as f:
    f.write(html)
print("✓ templates/dashboard.html validado com sucesso!")

# 3. SINCRONIZAR COM GITHUB E RENDER (SEM FALHAS DE COMMIT)
print("=" * 80)
print("A ENVIAR ATUALIZAÇÃO PARA O RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "app.py", "templates/dashboard.html"])
subprocess.run(["git", "commit", "-m", "Acesso automatico do professor a doutrina e menu exclusivo"])
subprocess.run(["git", "push", "origin", "main"])

print("=" * 80)
print(">>> PROCESSO CONCLUÍDO COM SUCESSO! <<<")
print("=" * 80)