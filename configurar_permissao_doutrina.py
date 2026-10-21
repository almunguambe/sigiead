import os
import re
import py_compile
import subprocess
import jinja2

print("=" * 80)
print("A CONFIGURAR ACESSO EXCLUSIVO E ACOMPANHAMENTO DO PROFESSOR...")
print("=" * 80)

caminho_app = 'app.py'
caminho_dash = os.path.join('templates', 'dashboard.html')

# =============================================================================
# 1. ATUALIZAR APP.PY: PROFESSOR ENTRA SEMPRE NA DOUTRINA
# =============================================================================
with open(caminho_app, 'r', encoding='utf-8') as f:
    app_code = f.read()

# Roteamento no Login: se for professor, vai para ?aba=doutrina
if "def login():" in app_code:
    pos_login = app_code.find("def login():")
    pos_sess = app_code.find("session['usuario'] = user", pos_login)
    if pos_sess != -1:
        fim_s = app_code.find("\n", pos_sess) + 1
        pos_redir = app_code.find("return redirect", fim_s)
        pos_redir_fim = app_code.find("\n", pos_redir) + 1
        
        redirecionamento_correto = (
            "            perfil_u = str(user.get('perfil', '')).lower()\n"
            "            if any(p in perfil_u for p in ['prof', 'docente', 'instrutor']):\n"
            "                return redirect('/?aba=doutrina')\n"
            "            return redirect('/?aba=dashboard')\n"
        )
        app_code = app_code[:fim_s] + redirecionamento_correto + app_code[pos_redir_fim:]
        print("✓ Login configurado: professor vai diretamente para Doutrina!")

# Roteamento no Index (/): professor NUNCA vê Raio-X
pos_idx = app_code.find("def index():")
if pos_idx != -1:
    pos_u = app_code.find("usuario = session", pos_idx)
    if pos_u != -1:
        fim_u = app_code.find("\n", pos_u) + 1
        trava_doutrina = (
            "\n    # RESTRINGIR PROFESSOR: APENAS ACESSO A DOUTRINA\n"
            "    perfil_atual = str(usuario.get('perfil', '')).lower() if 'usuario' in locals() and usuario else ''\n"
            "    if any(p in perfil_atual for p in ['prof', 'docente', 'instrutor']):\n"
            "        aba_ativa = 'doutrina'\n"
        )
        if "RESTRINGIR PROFESSOR: APENAS ACESSO A DOUTRINA" not in app_code:
            app_code = app_code[:fim_u] + trava_doutrina + app_code[fim_u:]
            print("✓ Index configurado: professor recebe sempre Doutrina!")

with open(caminho_app, 'w', encoding='utf-8') as f:
    f.write(app_code)

py_compile.compile(caminho_app, doraise=True)
print("✓ app.py validado e compilado com ZERO erros!")

# =============================================================================
# 2. ATUALIZAR TEMPLATES/DASHBOARD.HTML (OCULTAR CADASTROS E RESPONSIVIDADE)
# =============================================================================
with open(caminho_dash, 'r', encoding='utf-8') as f:
    html = f.read()

# A) No telemóvel, esconder a barra lateral (hidden md:flex) para não esmagar
html = re.sub(
    r'<aside class="([^"]*)\bw-64\b([^"]*)"',
    r'<aside class="\1hidden md:flex md:w-64\2"',
    html,
    count=1
)

# B) Adicionar cabeçalho móvel compacto caso ainda não exista
cabecalho_mobile = """
    <!-- CABEÇALHO COMPACTO PARA DISPOSITIVOS MÓVEIS -->
    <header class="md:hidden bg-slate-900 text-white px-4 py-3 flex items-center justify-between sticky top-0 z-50 shadow-md">
        <div class="flex items-center gap-2.5">
            <div class="w-8 h-8 rounded-xl bg-amber-500/20 border border-amber-400/30 flex items-center justify-center font-black text-amber-400 text-sm">
                📖
            </div>
            <div>
                <span class="font-black text-xs text-white tracking-tight block">SIGIEAD • Chicuque</span>
                <span class="text-[9px] text-amber-400 font-bold block -mt-0.5">
                    {{ usuario_logado.nome if usuario_logado else 'Utilizador' }}
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

if "<!-- CABEÇALHO COMPACTO PARA DISPOSITIVOS MÓVEIS -->" not in html and "<body" in html:
    pos_b = html.find("<body")
    pos_b_close = html.find(">", pos_b) + 1
    html = html[:pos_b_close] + "\n" + cabecalho_mobile + html[pos_b_close:]
    print("✓ Cabeçalho móvel integrado!")

# C) Ocultar formulários de cadastro para professores
cond_inicio_admin = "{% if not (usuario_logado and ('professor' in usuario_logado.perfil|lower or 'docente' in usuario_logado.perfil|lower or 'instrutor' in usuario_logado.perfil|lower)) %}"
cond_fim_admin = "{% endif %}"

# 1. Formulário "Inscrever Formando com Login"
pos_insc = html.find("Inscrever Formando")
if pos_insc != -1:
    pos_c_insc = html.rfind("<div", 0, pos_insc)
    pos_f_insc = html.find("</form>", pos_insc)
    if pos_f_insc != -1:
        pos_f_div = html.find("</div>", pos_f_insc) + len("</div>")
        if cond_inicio_admin not in html[pos_c_insc-250:pos_c_insc]:
            html = html[:pos_c_insc] + cond_inicio_admin + "\n" + html[pos_c_insc:pos_f_div] + "\n" + cond_fim_admin + html[pos_f_div:]
            print("✓ Formulário 'Inscrever Formando' restrito apenas a Administradores!")

# 2. Formulário "Cadastrar Novo Professor"
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
            print("✓ Formulário 'Cadastrar Novo Professor' restrito apenas a Administradores!")

# D) Fazer a Lista de Formandos expandir em largura completa (w-full) para o professor
def expandir_coluna(m):
    orig = m.group(1)
    return f'class="{{% if usuario_logado and (\'professor\' in usuario_logado.perfil|lower or \'docente\' in usuario_logado.perfil|lower) %}}lg:col-span-12 w-full{{% else %}}{orig}{{% endif %}}"'

html = re.sub(r'class="([^"]*lg:col-span-7[^"]*)"', expandir_coluna, html, count=1)
print("✓ Tabela de alunos configurada para ocupar largura total na sessão do professor!")

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
# 3. ENVIAR PARA O GITHUB E O RENDER
# =============================================================================
subprocess.run(["git", "add", "app.py", "templates/dashboard.html"], check=True)
subprocess.run(["git", "commit", "-m", "Ajuste definitivo: acompanhamento de formandos pelo professor sem raio-x e sem cadastros"], check=True)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("=" * 80)
print(">>> ATUALIZAÇÃO CONCLUÍDA E PUBLICADA COM SUCESSO! <<<")
print("=" * 80)