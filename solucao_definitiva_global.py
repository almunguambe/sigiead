import os
import re
import py_compile
import subprocess
import jinja2

print("=" * 80)
print("A APLICAR SOLUÇÃO DEFINITIVA: EXTINÇÃO DA BARRA PRETA & RESPONSIVIDADE PROFESSOR...")
print("=" * 80)

caminho_app = 'app.py'
caminho_dash = os.path.join('templates', 'dashboard.html')

# =============================================================================
# 1. BLINDAGEM NO APP.PY (ACESSO DO PROFESSOR DIRETO À DOUTRINA)
# =============================================================================
with open(caminho_app, 'r', encoding='utf-8') as f:
    app_code = f.read()

# Assegurar que 'g' e 'has_request_context' estão presentes
if "from flask import" in app_code:
    m_imp = re.search(r"from flask import ([^\n]+)", app_code)
    if m_imp:
        itens = [i.strip() for i in m_imp.group(1).split(",")]
        for item in ["g", "has_request_context"]:
            if item not in itens:
                itens.append(item)
        app_code = app_code[:m_imp.start()] + "from flask import " + ", ".join(itens) + app_code[m_imp.end():]

# Na rota index(), forçar redirecionamento do professor para aba=doutrina
redirecionamento_docente = '''
    # Trava exclusiva para professores: acesso direto à Doutrina
    perfil_usuario = str(usuario.get('perfil', '')).lower()
    if ('professor' in perfil_usuario or 'docente' in perfil_usuario or 'instrutor' in perfil_usuario):
        if aba_ativa != 'doutrina':
            return redirect(url_for('index', aba='doutrina'))
'''

if "perfil_usuario = str(usuario.get('perfil'" not in app_code:
    pos_aba = app_code.find("aba_ativa = request.args.get('aba'")
    if pos_aba != -1:
        fim_linha_aba = app_code.find("\n", pos_aba) + 1
        app_code = app_code[:fim_linha_aba] + redirecionamento_docente + app_code[fim_linha_aba:]
        print("✓ Trava e redirecionamento de professores garantidos em app.py!")

with open(caminho_app, 'w', encoding='utf-8') as f:
    f.write(app_code)

try:
    py_compile.compile(caminho_app, doraise=True)
    print("✓ app.py validado e compilado com ZERO erros!")
except Exception as e:
    print(f"Erro em app.py: {e}")
    exit(1)

# =============================================================================
# 2. ELIMINAÇÃO TOTAL DA BARRA PRETA EM TEMPLATES/DASHBOARD.HTML
# =============================================================================
with open(caminho_dash, 'r', encoding='utf-8') as f:
    dash_html = f.read()

# A) Injetar CSS Universal anti-barra preta no <head>
css_anti_barra_preta = """
    <!-- CSS GLOBAL ANTI-BARRA PRETA: PROÍBE SCROLLBAR EM SELECTS NO CHROME -->
    <style>
        select, select::-webkit-scrollbar {
            overflow: hidden !important;
            overflow-x: hidden !important;
            scrollbar-width: none !important;
            -ms-overflow-style: none !important;
        }
        select::-webkit-scrollbar {
            display: none !important;
            width: 0 !important;
            height: 0 !important;
        }
        .no-scrollbar::-webkit-scrollbar {
            display: none !important;
        }
        .no-scrollbar {
            -ms-overflow-style: none;
            scrollbar-width: none;
        }
    </style>
</head>
"""

if "CSS GLOBAL ANTI-BARRA PRETA" not in dash_html and "</head>" in dash_html:
    dash_html = dash_html.replace("</head>", css_anti_barra_preta, 1)
    print("✓ CSS global anti-barra preta inserido no cabeçalho!")

# B) Remover qualquer classe de overflow-x de todas as tags <select> do documento
def limpar_classes_select(html):
    def substituir(m):
        tag = m.group(0)
        tag_limpa = re.sub(r'\boverflow(-x)?-(auto|scroll)\b', '', tag)
        tag_limpa = re.sub(r'class="([^"]*)"', lambda x: f'class="{" ".join(x.group(1).split())}"', tag_limpa)
        return tag_limpa
    return re.sub(r'<select[^>]*>', substituir, html)

dash_html = limpar_classes_select(dash_html)
print("✓ Varredura concluída: todas as classes overflow removidas de tags <select>!")

# C) Na Tesouraria: remover o bloco duplicado antigo "Categoria de Entrada Local"
pos_old_cat = dash_html.find("Categoria de Entrada Local")
if pos_old_cat != -1:
    pos_div_start = dash_html.rfind("<div", 0, pos_old_cat)
    # Procurar o fecho da div
    pos_div_end = dash_html.find("</div>", pos_old_cat)
    if pos_div_end != -1:
        pos_div_end += len("</div>")
        dash_html = dash_html[:pos_div_start] + dash_html[pos_div_end:]
        print("✓ Campo duplicado antigo 'Categoria de Entrada Local' removido da Tesouraria!")

# =============================================================================
# 3. RESPONSIVIDADE MOBILE DEFINITIVA (ELIMINA ESMAGAMENTO DO PROFESSOR)
# =============================================================================

# A) Ajustar tag <body> para suportar fluxo coluna no mobile e linha no desktop
dash_html = re.sub(
    r'<body class="([^"]*)"',
    lambda m: '<body class="bg-slate-100 flex flex-col md:flex-row min-h-screen text-slate-800 antialiased font-sans">',
    dash_html,
    count=1
)

# B) Ajustar tag <aside> para ser oculta no mobile e fixa apenas em desktop (md:)
dash_html = re.sub(
    r'<aside class="([^"]*)"',
    lambda m: '<aside class="hidden md:flex md:w-64 bg-slate-900 text-white min-h-screen p-4 flex-col justify-between shrink-0 shadow-2xl">',
    dash_html,
    count=1
)

# C) Ajustar tag <main> para ocupar 100% de largura no mobile
dash_html = re.sub(
    r'<main class="([^"]*)"',
    lambda m: '<main class="flex-1 w-full min-w-0 p-4 md:p-6 overflow-x-hidden">',
    dash_html,
    count=1
)

# D) Inserir Cabeçalho e Navegação Móvel Fluida logo no início de <body>
cabecalho_mobile = """
    <!-- CABEÇALHO MÓVEL (EXIBIDO APENAS EM TELEMÓVEIS / ECRÃS PEQUENOS) -->
    <header class="md:hidden bg-slate-900 text-white px-4 py-3 flex items-center justify-between sticky top-0 z-50 shadow-md">
        <div class="flex items-center gap-2.5">
            <div class="w-8 h-8 rounded-xl bg-amber-500/20 border border-amber-400/30 flex items-center justify-center font-black text-amber-400 text-sm">
                ✝
            </div>
            <div>
                <span class="font-black text-xs text-white tracking-tight block">SIGIEAD • Chicuque</span>
                <span class="text-[9px] text-slate-400 block -mt-0.5">
                    {{ usuario_logado.nome if usuario_logado else 'Utilizador' }}
                </span>
            </div>
        </div>
        <div class="flex items-center gap-2">
            <span class="text-[10px] font-bold px-2 py-0.5 rounded-md bg-slate-800 text-slate-300 border border-slate-700 uppercase">
                {{ usuario_logado.perfil if usuario_logado else 'Membro' }}
            </span>
            <a href="/logout" class="px-2.5 py-1 bg-rose-600/20 text-rose-300 hover:bg-rose-600 hover:text-white rounded-lg text-xs font-bold transition border border-rose-500/30">
                Sair
            </a>
        </div>
    </header>

    <!-- BARRA DE ABAS MÓVEL SUPERIOR -->
    <nav class="md:hidden bg-slate-950 px-3 py-2 border-b border-slate-800 flex items-center gap-1.5 overflow-x-auto no-scrollbar shrink-0 text-xs">
        {% if usuario_logado and ('professor' in usuario_logado.perfil|lower or 'docente' in usuario_logado.perfil|lower) %}
            <a href="/?aba=doutrina" class="px-3 py-1.5 rounded-lg font-bold whitespace-nowrap bg-amber-600 text-white shadow">
                📖 Minhas Aulas & Alunos
            </a>
            <a href="/ensino/aulas" target="_blank" class="px-3 py-1.5 rounded-lg font-bold whitespace-nowrap bg-slate-900 text-slate-300">
                🎓 Sala Virtual ↗
            </a>
        {% else %}
            <a href="/?aba=dashboard" class="px-3 py-1.5 rounded-lg font-bold whitespace-nowrap {% if aba_ativa == 'dashboard' %}bg-indigo-600 text-white{% else %}bg-slate-900 text-slate-300{% endif %}">
                Raio-X
            </a>
            <a href="/?aba=membros" class="px-3 py-1.5 rounded-lg font-bold whitespace-nowrap {% if aba_ativa == 'membros' %}bg-indigo-600 text-white{% else %}bg-slate-900 text-slate-300{% endif %}">
                Membros
            </a>
            <a href="/?aba=secretaria" class="px-3 py-1.5 rounded-lg font-bold whitespace-nowrap {% if aba_ativa == 'secretaria' %}bg-indigo-600 text-white{% else %}bg-slate-900 text-slate-300{% endif %}">
                Secretaria
            </a>
            <a href="/?aba=financas" class="px-3 py-1.5 rounded-lg font-bold whitespace-nowrap {% if aba_ativa == 'financas' %}bg-indigo-600 text-white{% else %}bg-slate-900 text-slate-300{% endif %}">
                Finanças
            </a>
            <a href="/?aba=tesouraria" class="px-3 py-1.5 rounded-lg font-bold whitespace-nowrap {% if aba_ativa == 'tesouraria' %}bg-indigo-600 text-white{% else %}bg-slate-900 text-slate-300{% endif %}">
                Caixa
            </a>
            <a href="/?aba=doutrina" class="px-3 py-1.5 rounded-lg font-bold whitespace-nowrap {% if aba_ativa == 'doutrina' %}bg-indigo-600 text-white{% else %}bg-slate-900 text-slate-300{% endif %}">
                Doutrina
            </a>
        {% endif %}
    </nav>
"""

if "<!-- CABEÇALHO MÓVEL" not in dash_html:
    pos_body = dash_html.find("<body")
    pos_body_close = dash_html.find(">", pos_body) + 1
    dash_html = dash_html[:pos_body_close] + "\n" + cabecalho_mobile + dash_html[pos_body_close:]
    print("✓ Cabeçalho e barra móvel nativa integrados no topo do ecrã!")

# 4. VALIDAÇÃO RIGOROSA NO MOTOR JINJA2
env = jinja2.Environment()
try:
    env.parse(dash_html)
    print("✓ templates/dashboard.html validado com ZERO erros no Jinja2!")
except Exception as e:
    print(f"Erro no Jinja2: {e}")
    exit(1)

with open(caminho_dash, 'w', encoding='utf-8') as f:
    f.write(dash_html)

# =============================================================================
# 5. SINCRONIZAR COM O GITHUB E O RENDER
# =============================================================================
print("=" * 80)
print("A ENVIAR ATUALIZAÇÃO DEFINITIVA PARA O GITHUB & RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "app.py", "templates/dashboard.html"], check=True)
subprocess.run(["git", "commit", "-m", "Solucao definitiva: extincao da barra preta nos selects e layout full-width mobile para professores"], check=True)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("=" * 80)
print(">>> TUDO CONCLUÍDO COM SUCESSO DEFINITIVO! <<<")
print("=" * 80)