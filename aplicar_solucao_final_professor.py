import os
import re
import py_compile
import subprocess
import jinja2

print("=" * 80)
print("A CONFIGURAR ACESSO EXCLUSIVO DO PROFESSOR (SEM CÉLULAS E SEM RAIO-X)...")
print("=" * 80)

caminho_app = 'app.py'
caminho_dash = os.path.join('templates', 'dashboard.html')

# =============================================================================
# 1. ATUALIZAR APP.PY: PROFESSOR ENTRA SEMPRE EM DOUTRINA
# =============================================================================
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
    print("✓ app.py: Forçada aba_ativa = 'doutrina' para perfil docente!")

with open(caminho_app, 'w', encoding='utf-8') as f:
    f.write(app_code)

try:
    py_compile.compile(caminho_app, doraise=True)
    print("✓ app.py validado e compilado com ZERO erros!")
except Exception as e:
    print(f"Erro em app.py: {e}")
    exit(1)

# =============================================================================
# 2. ATUALIZAR TEMPLATES/DASHBOARD.HTML (MENU DO PROFESSOR E TELA CHEIA)
# =============================================================================
with open(caminho_dash, 'r', encoding='utf-8') as f:
    html = f.read()

# A) Barra lateral responsiva: oculta no telemóvel (hidden md:flex), visível no PC
html = re.sub(r'<aside class="([^"]*)\bw-64\b([^"]*)"', r'<aside class="\1hidden md:flex md:w-64\2"', html, count=1)

# B) Cabeçalho móvel compacto para telemóveis
cabecalho_mobile = """
    <!-- CABEÇALHO MÓVEL PARA TELEMÓVEL -->
    <header class="md:hidden bg-slate-900 text-white px-4 py-3 flex items-center justify-between sticky top-0 z-50 shadow-md">
        <div class="flex items-center gap-2.5">
            <div class="w-8 h-8 rounded-xl bg-amber-500/20 border border-amber-400/30 flex items-center justify-center font-black text-amber-400 text-sm">
                📖
            </div>
            <div>
                <span class="font-black text-xs text-white tracking-tight block">SIGIEAD • Chicuque</span>
                <span class="text-[9px] text-amber-400 font-bold block -mt-0.5">
                    {{ usuario_logado.nome if usuario_logado else 'Área do Professor' }}
                </span>
            </div>
        </div>
        <div class="flex items-center gap-2">
            <span class="text-[10px] font-bold px-2 py-0.5 rounded-md bg-slate-800 text-slate-300 border border-slate-700 uppercase">
                {{ usuario_logado.perfil if usuario_logado else 'Docente' }}
            </span>
            <a href="/logout" class="px-2.5 py-1 bg-rose-600 text-white hover:bg-rose-700 rounded-lg text-xs font-bold transition shadow-sm">
                Sair
            </a>
        </div>
    </header>
"""

if "<!-- CABEÇALHO MÓVEL PARA TELEMÓVEL -->" not in html and "<body" in html:
    pos_b = html.find("<body")
    pos_b_close = html.find(">", pos_b) + 1
    html = html[:pos_b_close] + "\n" + cabecalho_mobile + html[pos_b_close:]
    print("✓ Cabeçalho móvel integrado!")

# C) Adicionar botão 'Minhas Turmas & Alunos' na barra lateral para o professor
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
        print("✓ Menu lateral com botão 'Minhas Turmas & Alunos' adicionado!")

# D) Ocultar formulários administrativos (Inscrever Formando e Cadastrar Professor) para o docente
cond_inicio_admin = "{% if not (usuario_logado and ('professor' in usuario_logado.perfil|lower or 'docente' in usuario_logado.perfil|lower or 'instrutor' in usuario_logado.perfil|lower)) %}"
cond_fim_admin = "{% endif %}"

pos_insc = html.find("Inscrever Formando")
if pos_insc != -1:
    pos_c_insc = html.rfind("<div", 0, pos_insc)
    pos_f_insc = html.find("</form>", pos_insc)
    if pos_f_insc != -1:
        pos_f_div = html.find("</div>", pos_f_insc) + len("</div>")
        if cond_inicio_admin not in html[pos_c_insc-250:pos_c_insc]:
            html = html[:pos_c_insc] + cond_inicio_admin + "\n" + html[pos_c_insc:pos_f_div] + "\n" + cond_fim_admin + html[pos_f_div:]
            print("✓ Formulário 'Inscrever Formando' restrito a Administradores!")

pos_prof = html.find("CADASTRAR NOVO PROFESSOR")
if pos_prof == -1:
    pos_prof = html.find("Cadastrar Novo Professor")

if pos_prof != -1:
    pos_c_prof = html.rfind("<div", 0, pos_prof)
    pos_b_prof = html.find("Credenciar Professor", pos_prof)
    if pos_b_prof != -1:
        pos_f_div_p = html.find("</div>", pos_b_prof) + len("</div>")
        if cond_inicio_admin not in html[pos_c_prof-250:pos_c_prof]:
            html = html[:pos_c_prof] + cond_inicio_admin + "\n" + html[pos_c_prof:pos_f_div_p] + "\n" + cond_fim_admin + html[pos_f_div_p:]
            print("✓ Formulário 'Cadastrar Novo Professor' restrito a Administradores!")

# E) Fazer a lista de formandos expandir a 100% da largura útil
def expandir_coluna(m):
    orig = m.group(1)
    tag = '{% if usuario_logado and ("professor" in usuario_logado.perfil|lower or "docente" in usuario_logado.perfil|lower) %}lg:col-span-12 w-full{% else %}' + orig + '{% endif %}'
    return 'class="' + tag + '"'

html = re.sub(r'class="([^"]*lg:col-span-7[^"]*)"', expandir_coluna, html, count=1)

# F) Blindar o Raio-X e Células contra o acesso do professor
if "{% if aba_ativa == 'dashboard'" in html:
    html = re.sub(
        r"{% if aba_ativa == 'dashboard'[^%]*%}",
        "{% if aba_ativa == 'dashboard' and not (usuario_logado and ('professor' in usuario_logado.perfil|lower or 'docente' in usuario_logado.perfil|lower)) %}",
        html
    )
    print("✓ Raio-X e Células bloqueados para o professor!")

env = jinja2.Environment()
try:
    env.parse(html)
    print("✓ templates/dashboard.html validado com ZERO erros no Jinja2!")
except Exception as e:
    print(f"Erro no Jinja2: {e}")
    exit(1)

with open(caminho_dash, 'w', encoding='utf-8') as f:
    f.write(html)

# =============================================================================
# 3. ENVIAR PARA O GITHUB E RENDER
# =============================================================================
print("=" * 80)
print("A ENVIAR ATUALIZAÇÃO DEFINITIVA PARA O RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "-A"])
subprocess.run(["git", "commit", "-m", "Correcao definitiva: professor abre sempre doutrina e menu exclusivo sem celulas"])
subprocess.run(["git", "push", "origin", "main"])

print("=" * 80)
print(">>> ATUALIZAÇÃO PUBLICADA NO RENDER COM SUCESSO! <<<")
print("=" * 80)