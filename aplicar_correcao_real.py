import os
import re
import py_compile
import subprocess
import jinja2

print("=" * 80)
print("A CONFIGURAR ABA PADRÃO DO PROFESSOR E REMOÇÃO TOTAL DE BARRAS PRETAS...")
print("=" * 80)

caminho_app = 'app.py'
caminho_dash = os.path.join('templates', 'dashboard.html')

# =============================================================================
# 1. APP.PY: SE FOR PROFESSOR E A URL NÃO TIVER ?aba=, ABRIR DOUTRINA POR PADRÃO
# =============================================================================
with open(caminho_app, 'r', encoding='utf-8') as f:
    app_code = f.read()

# Substituir de forma limpa a definição de aba_ativa na rota principal
# Se o utilizador na sessão for professor, default_aba = 'doutrina'
padrao_aba = r"aba_ativa\s*=\s*request\.args\.get\(['\"]aba['\"],\s*['\"]dashboard['\"]\)"

codigo_novo_aba = """sess_user = session.get('usuario') or {}
    perfil_doc = str(sess_user.get('perfil', '')).lower()
    aba_padrao = 'doutrina' if any(c in perfil_doc for c in ['professor', 'docente', 'instrutor']) else 'dashboard'
    aba_ativa = request.args.get('aba', aba_padrao)"""

if re.search(padrao_aba, app_code):
    app_code = re.sub(padrao_aba, codigo_novo_aba, app_code, count=1)
    print("✓ Aba padrão do Professor ajustada nativamente para 'doutrina'!")
else:
    print("Aviso: Padrão exato de aba_ativa não localizado, mantido original.")

with open(caminho_app, 'w', encoding='utf-8') as f:
    f.write(app_code)

try:
    py_compile.compile(caminho_app, doraise=True)
    print("✓ app.py validado e compilado com ZERO erros!")
except Exception as e:
    print(f"Erro em app.py: {e}")
    exit(1)

# =============================================================================
# 2. DASHBOARD.HTML: EXTINÇÃO TOTAL DAS BARRAS PRETAS EM SELECTS
# =============================================================================
with open(caminho_dash, 'r', encoding='utf-8') as f:
    html = f.read()

# Remover resíduo de '>' solto antes de main se existir
html = re.sub(r'>\s*<main', '<main', html)

# Remover qualquer classe de overflow-x de TODAS as tags <select> do sistema
def remover_overflow_selects(texto):
    def limpa_tag(m):
        tag = m.group(0)
        tag = re.sub(r'\boverflow(-x)?-(auto|scroll)\b', '', tag)
        tag = re.sub(r'class="([^"]*)"', lambda c: f'class="{" ".join(c.group(1).split())}"', tag)
        return tag
    return re.sub(r'<select[^>]*>', limpa_tag, texto)

html = remover_overflow_selects(html)
print("✓ Classes 'overflow-x-auto' removidas de todas as tags <select>!")

# Na Tesouraria: se ainda existir o campo Categoria de Entrada Local, remover
if "Categoria de Entrada Local" in html:
    idx = html.find("Categoria de Entrada Local")
    start_d = html.rfind("<div", 0, idx)
    end_d = html.find("</div>", idx)
    if start_d != -1 and end_d != -1:
        end_d += len("</div>")
        html = html[:start_d] + html[end_d:]
        print("✓ Campo residual antigo 'Categoria de Entrada Local' eliminado!")

# CSS no cabeçalho para forçar o Chrome a nunca desenhar scrollbar nos selects
css_limpo = """
    <style>
        select {
            scrollbar-width: none !important;
            -ms-overflow-style: none !important;
        }
        select::-webkit-scrollbar {
            display: none !important;
            width: 0 !important;
            height: 0 !important;
        }
    </style>
</head>
"""
if "select::-webkit-scrollbar" not in html and "</head>" in html:
    html = html.replace("</head>", css_limpo, 1)

# Validar com o Jinja2
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
# 3. PUBLICAR NO GITHUB E RENDER
# =============================================================================
print("=" * 80)
print("A ENVIAR ATUALIZAÇÃO SEGURA PARA O GITHUB & RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "app.py", "templates/dashboard.html"], check=True)
subprocess.run(["git", "commit", "-m", "Ajuste seguro: aba padrao doutrina para professores e remocao de overflow em selects"], check=True)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("=" * 80)
print(">>> ATUALIZAÇÃO CONCLUÍDA COM TOTAL SUCESSO! <<<")
print("=" * 80)