import os
import re
import py_compile
import subprocess
import jinja2

print("=" * 80)
print("A CONFIGURAR PERMISSÕES DA ÁREA DO PROFESSOR E AJUSTE MOBILE...")
print("=" * 80)

caminho_dash = os.path.join('templates', 'dashboard.html')
caminho_app = 'app.py'

# =============================================================================
# 1. ATUALIZAR TEMPLATES/DASHBOARD.HTML (PERMISSÕES E TELA CHEIA)
# =============================================================================
with open(caminho_dash, 'r', encoding='utf-8') as f:
    html = f.read()

# A) Corrigir barra lateral no mobile: Oculta no telemóvel, fixa no computador
# Substituir <aside class="... w-64 ..."> por <aside class="hidden md:flex md:w-64 ...">
html = re.sub(
    r'<aside class="([^"]*)\bw-64\b([^"]*)"',
    r'<aside class="\1hidden md:flex md:w-64\2"',
    html,
    count=1
)

# Inserir cabeçalho mobile caso não exista
cabecalho_mobile_top = """
    <!-- CABEÇALHO SUPERIOR PARA DISPOSITIVOS MÓVEIS -->
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

if "<!-- CABEÇALHO SUPERIOR PARA DISPOSITIVOS MÓVEIS -->" not in html and "<body" in html:
    pos_body = html.find("<body")
    pos_body_close = html.find(">", pos_body) + 1
    html = html[:pos_body_close] + "\n" + cabecalho_mobile_top + html[pos_body_close:]
    print("✓ Cabeçalho móvel integrado no topo do ecrã!")

# B) Na aba Doutrina: Ocultar cadastros de novos formandos e novos professores para quem é Professor
condicao_inicio_admin = "{% if not (usuario_logado and ('professor' in usuario_logado.perfil|lower or 'docente' in usuario_logado.perfil|lower or 'instrutor' in usuario_logado.perfil|lower)) %}"
condicao_fim_admin = "{% endif %}"

# 1. Ocultar "Inscrever Formando com Login"
pos_insc = html.find("Inscrever Formando")
if pos_insc != -1:
    pos_card_insc = html.rfind("<div", 0, pos_insc)
    # Procurar onde o formulário ou card fecha
    pos_form_fim = html.find("</form>", pos_insc)
    if pos_form_fim != -1:
        pos_card_fim = html.find("</div>", pos_form_fim) + len("</div>")
        if condicao_inicio_admin not in html[pos_card_insc-200:pos_card_insc]:
            html = html[:pos_card_insc] + condicao_inicio_admin + "\n" + html[pos_card_insc:pos_card_fim] + "\n" + condicao_fim_admin + html[pos_card_fim:]
            print("✓ Formulário 'Inscrever Formando com Login' restrito apenas a Administradores!")

# 2. Ocultar "CADASTRAR NOVO PROFESSOR / INSTRUTOR"
pos_prof = html.find("CADASTRAR NOVO PROFESSOR")
if pos_prof == -1:
    pos_prof = html.find("Cadastrar Novo Professor")

if pos_prof != -1:
    pos_card_prof = html.rfind("<div", 0, pos_prof)
    pos_btn_prof = html.find("Credenciar Professor", pos_prof)
    if pos_btn_prof != -1:
        pos_card_fim_p = html.find("</div>", pos_btn_prof) + len("</div>")
        if condicao_inicio_admin not in html[pos_card_prof-200:pos_card_prof]:
            html = html[:pos_card_prof] + condicao_inicio_admin + "\n" + html[pos_card_prof:pos_card_fim_p] + "\n" + condicao_fim_admin + html[pos_card_fim_p:]
            print("✓ Bloco 'Cadastrar Novo Professor' restrito apenas a Administradores!")

# C) Garantir que a Lista de Formandos & Acompanhamento se expande caso o usuário seja professor
if "Lista de Formandos & Acompanhamento" in html:
    pos_lista = html.find("Lista de Formandos & Acompanhamento")
    pos_col_lista = html.rfind("<div class=\"", 0, pos_lista)
    if pos_col_lista != -1:
        # Tornar a coluna flexível para tela inteira quando for professor
        html = re.sub(
            r'class="([^"]*lg:col-span-7[^"]*)"',
            r'class="{% if usuario_logado and (\'professor\' in usuario_logado.perfil|lower or \'docente\' in usuario_logado.perfil|lower) %}lg:col-span-12 w-full{% else %}\1{% endif %}"',
            html,
            count=1
        )
        print("✓ Tabela de alunos configurada para ocupar 100% da tela na sessão do professor!")

# Validar motor Jinja2
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
# 2. VALIDAR COMPILAÇÃO DO APP.PY
# =============================================================================
try:
    py_compile.compile(caminho_app, doraise=True)
    print("✓ app.py validado e compilado com ZERO erros!")
except Exception as e:
    print(f"Erro em app.py: {e}")
    exit(1)

# =============================================================================
# 3. ENVIAR PARA O GITHUB E O RENDER
# =============================================================================
print("=" * 80)
print("A ENVIAR ATUALIZAÇÃO PARA O GITHUB & RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "templates/dashboard.html", "app.py"], check=True)
subprocess.run(["git", "commit", "-m", "Permissoes: ocultar cadastros de alunos/professores para docentes e tela cheia mobile"], check=True)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("=" * 80)
print(">>> PROCESSO CONCLUÍDO COM TOTAL SUCESSO! <<<")
print("=" * 80)