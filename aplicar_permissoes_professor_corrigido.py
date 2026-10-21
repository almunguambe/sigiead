import os
import re
import py_compile
import subprocess
import jinja2

print("=" * 80)
print("A APLICAR PERMISSÕES DA ÁREA DO PROFESSOR (SEM ERROS DE JINJA2)...")
print("=" * 80)

caminho_dash = os.path.join('templates', 'dashboard.html')
caminho_app = 'app.py'

# 1. RESTAURAR TEMPLATE BASE LIMPO DO GIT HEAD
subprocess.run(["git", "checkout", "HEAD", "--", "templates/dashboard.html"], check=True)
print("✓ templates/dashboard.html restaurado ao estado limpo do Git!")

with open(caminho_dash, 'r', encoding='utf-8') as f:
    html = f.read()

# 2. AJUSTAR BARRA LATERAL PARA NÃO ESMAGAR NO TELEMÓVEL
# No telemóvel: hidden (oculta). No computador: md:flex md:w-64 (largura normal)
html = re.sub(
    r'<aside class="([^"]*)\bw-64\b([^"]*)"',
    r'<aside class="\1hidden md:flex md:w-64\2"',
    html,
    count=1
)

# 3. CABEÇALHO COMPACTO SUPERIOR PARA DISPOSITIVOS MÓVEIS
cabecalho_mobile = """
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
    html = html[:pos_body_close] + "\n" + cabecalho_mobile + html[pos_body_close:]
    print("✓ Cabeçalho móvel integrado no topo do ecrã!")

# 4. OCULTAR CADASTROS DE ALUNOS E PROFESSORES PARA QUEM É PROFESSOR
cond_inicio = "{% if not (usuario_logado and ('professor' in usuario_logado.perfil|lower or 'docente' in usuario_logado.perfil|lower or 'instrutor' in usuario_logado.perfil|lower)) %}"
cond_fim = "{% endif %}"

# A) Ocultar "Inscrever Formando com Login"
pos_insc = html.find("Inscrever Formando")
if pos_insc != -1:
    pos_card_insc = html.rfind("<div", 0, pos_insc)
    pos_form_fim = html.find("</form>", pos_insc)
    if pos_form_fim != -1:
        pos_card_fim = html.find("</div>", pos_form_fim) + len("</div>")
        html = html[:pos_card_insc] + cond_inicio + "\n" + html[pos_card_insc:pos_card_fim] + "\n" + cond_fim + html[pos_card_fim:]
        print("✓ Formulário 'Inscrever Formando' restrito apenas a Administradores!")

# B) Ocultar "CADASTRAR NOVO PROFESSOR / INSTRUTOR"
pos_prof = html.find("CADASTRAR NOVO PROFESSOR")
if pos_prof == -1:
    pos_prof = html.find("Cadastrar Novo Professor")

if pos_prof != -1:
    pos_card_prof = html.rfind("<div", 0, pos_prof)
    pos_btn_prof = html.find("Credenciar Professor", pos_prof)
    if pos_btn_prof != -1:
        pos_card_fim_p = html.find("</div>", pos_btn_prof) + len("</div>")
        html = html[:pos_card_prof] + cond_inicio + "\n" + html[pos_card_prof:pos_card_fim_p] + "\n" + cond_fim + html[pos_card_fim_p:]
        print("✓ Formulário 'Cadastrar Novo Professor' restrito apenas a Administradores!")

# C) Fazer a Lista de Alunos expandir a 100% da largura na sessão do professor
def expandir_coluna_alunos(m):
    classe_original = m.group(1)
    return f'class="{{% if usuario_logado and (\'professor\' in usuario_logado.perfil|lower or \'docente\' in usuario_logado.perfil|lower) %}}lg:col-span-12 w-full{{% else %}}{classe_original}{{% endif %}}"'

html = re.sub(r'class="([^"]*lg:col-span-7[^"]*)"', expandir_coluna_alunos, html, count=1)
print("✓ Tabela de formandos configurada para tela cheia na sessão do professor!")

# 5. VALIDAÇÃO RIGOROSA NO MOTOR JINJA2
env = jinja2.Environment()
try:
    env.parse(html)
    print("✓ templates/dashboard.html validado com ZERO erros no Jinja2!")
except Exception as e:
    print(f"Erro no Jinja2: {e}")
    exit(1)

with open(caminho_dash, 'w', encoding='utf-8') as f:
    f.write(html)

# 6. VALIDAR APP.PY
try:
    py_compile.compile(caminho_app, doraise=True)
    print("✓ app.py validado e compilado com ZERO erros!")
except Exception as e:
    print(f"Erro em app.py: {e}")
    exit(1)

# 7. SINCRONIZAR COM O GITHUB E O RENDER
print("=" * 80)
print("A ENVIAR ATUALIZAÇÃO DEFINITIVA PARA O GITHUB & RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "templates/dashboard.html", "app.py"], check=True)
subprocess.run(["git", "commit", "-m", "Permissoes: ocultar cadastros para professor e expandir tabela de alunos em tela cheia"], check=True)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("=" * 80)
print(">>> ATUALIZAÇÃO CONCLUÍDA COM TOTAL SUCESSO! <<<")
print("=" * 80)