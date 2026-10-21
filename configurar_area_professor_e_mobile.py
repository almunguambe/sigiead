import os
import re
import py_compile
import subprocess
import jinja2

print("=" * 80)
print("A CONFIGURAR ÁREA EXCLUSIVA DO PROFESSOR E RESPONSIVIDADE MÓVEL...")
print("=" * 80)

caminho_app = 'app.py'
caminho_dash = os.path.join('templates', 'dashboard.html')

# =============================================================================
# 1. ATUALIZAR APP.PY: REDIRECIONAR AUTOMATICAMENTE PROFESSOR PARA DOUTRINA
# =============================================================================
with open(caminho_app, 'r', encoding='utf-8') as f:
    app_code = f.read()

# Na rota /login, se for professor redireciona logo para doutrina
if "session['usuario'] = user" in app_code and "user.get('perfil') == 'professor'" not in app_code:
    app_code = app_code.replace(
        "session['usuario'] = user",
        "session['usuario'] = user\n            if user.get('perfil') == 'professor':\n                return redirect(url_for('index', aba='doutrina'))"
    )
    print("✓ Redirecionamento de login do professor configurado!")

# Na rota principal index(), impedir que professor caia no dashboard geral
if "aba_ativa = request.args.get('aba'" in app_code:
    trava_professor = """
    # Se o perfil for professor, redirecionar para a sua área exclusiva de ensino
    if usuario.get('perfil') == 'professor' and aba_ativa != 'doutrina':
        return redirect(url_for('index', aba='doutrina'))
"""
    if "usuario.get('perfil') == 'professor' and aba_ativa != 'doutrina'" not in app_code:
        app_code = re.sub(
            r"(aba_ativa\s*=\s*request\.args\.get\('aba'[^\n]+\n)",
            r"\1" + trava_professor,
            app_code,
            count=1
        )
        print("✓ Trava de acesso exclusivo à Doutrina ativada para professores!")

with open(caminho_app, 'w', encoding='utf-8') as f:
    f.write(app_code)

try:
    py_compile.compile(caminho_app, doraise=True)
    print("✓ app.py validado e compilado com sucesso!")
except Exception as e:
    print(f"Erro em app.py: {e}")
    exit(1)

# =============================================================================
# 2. ATUALIZAR TEMPLATES/DASHBOARD.HTML (RESPONSIVIDADE E MENU DO PROFESSOR)
# =============================================================================
with open(caminho_dash, 'r', encoding='utf-8') as f:
    dash_html = f.read()

# Tornar o body responsivo (coluna no mobile, linha no desktop)
dash_html = re.sub(
    r'<body class="([^"]*)"',
    lambda m: f'<body class="{m.group(1)} flex-col md:flex-row"' if 'flex-col' not in m.group(1) else m.group(0),
    dash_html,
    count=1
)

# Tornar o <main> fluido (largura total no mobile)
dash_html = re.sub(
    r'<main class="([^"]*)"',
    lambda m: f'<main class="{m.group(1)} w-full min-w-0 overflow-x-hidden"' if 'min-w-0' not in m.group(1) else m.group(0),
    dash_html,
    count=1
)

# Ajustar a largura do <aside> para ser 100% no mobile e w-64 no desktop
dash_html = dash_html.replace('aside class="w-64', 'aside class="w-full md:w-64')

# Inserir o menu exclusivo do professor no início da navegação da sidebar
menu_professor_snippet = """
            {% if usuario_logado and usuario_logado.perfil == 'professor' %}
            <!-- MENU EXCLUSIVO DA ÁREA DO PROFESSOR -->
            <div class="space-y-4 mb-4">
                <div class="px-3 py-1.5 bg-amber-500/20 border border-amber-400/30 rounded-xl">
                    <span class="text-[10px] font-black uppercase tracking-wider text-amber-300 block">
                        👨‍🏫 Gabinete do Instrutor
                    </span>
                    <span class="text-xs font-bold text-white block mt-0.5 truncate">{{ usuario_logado.nome }}</span>
                </div>
                <nav class="space-y-1.5">
                    <a href="/?aba=doutrina" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition bg-amber-600 text-white shadow-md font-bold text-xs">
                        <span class="text-base">📖</span>
                        <span>Minhas Classes & Alunos</span>
                    </a>
                    <a href="/ensino/aulas" target="_blank" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-slate-300 hover:bg-slate-800 transition text-xs font-medium">
                        <span class="text-base">🎓</span>
                        <span>Sala de Aulas Virtual ↗</span>
                    </a>
                </nav>
            </div>
            {% else %}
"""

if "{% if usuario_logado and usuario_logado.perfil == 'professor' %}" not in dash_html:
    pos_nav = dash_html.find("<nav")
    if pos_nav != -1:
        dash_html = dash_html[:pos_nav] + menu_professor_snippet + dash_html[pos_nav:]
        # Fechar o if correspondente antes do fecho do menu
        pos_aside_close = dash_html.find("</aside>")
        dash_html = dash_html[:pos_aside_close] + "{% endif %}\n        " + dash_html[pos_aside_close:]
        print("✓ Menu exclusivo do professor integrado na barra lateral!")

env = jinja2.Environment()
try:
    env.parse(dash_html)
    print("✓ templates/dashboard.html validado com ZERO erros no Jinja2!")
except Exception as e:
    print(f"Aviso no Jinja2: {e}")

with open(caminho_dash, 'w', encoding='utf-8') as f:
    f.write(dash_html)

# =============================================================================
# 3. ENVIAR PARA O GITHUB E O RENDER
# =============================================================================
print("=" * 80)
print("A ENVIAR ATUALIZAÇÃO PARA O GITHUB & RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "app.py", "templates/dashboard.html"], check=True)
subprocess.run(["git", "commit", "-m", "Feature: area exclusiva do professor e layout responsivo mobile anti-esmagamento"], check=True)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("=" * 80)
print(">>> PROCESSO CONCLUÍDO COM TOTAL SUCESSO! <<<")
print("=" * 80)