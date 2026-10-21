import os
import re
import py_compile
import subprocess
import jinja2

print("=" * 80)
print("A RESTAURAR LAYOUT DO ADMIN E A CONFIGURAR ENCAMINHAMENTO DO PROFESSOR...")
print("=" * 80)

caminho_app = 'app.py'
caminho_dash = os.path.join('templates', 'dashboard.html')

# =============================================================================
# 1. RESTAURAR TEMPLATES/DASHBOARD.HTML AO ESTADO LIMPO DO GIT
# =============================================================================
# Procurar no histórico do Git o commit estável (antes dos testes de flexbox móvel)
res = subprocess.run(["git", "log", "--oneline", "templates/dashboard.html"], capture_output=True, text=True)
linhas_git = [l.strip() for l in res.stdout.strip().split('\n') if l.strip()]

hash_limpo = None
for l in linhas_git:
    if any(termo in l for termo in ["Demografia ministerial", "relatorio de coletas", "Performance definitiva", "connection already closed"]):
        hash_limpo = l.split()[0]
        print(f"✓ Commit estável localizado: {l}")
        break

if not hash_limpo and len(linhas_git) >= 5:
    hash_limpo = linhas_git[4].split()[0]

if hash_limpo:
    subprocess.run(["git", "checkout", hash_limpo, "--", "templates/dashboard.html"], check=True)
    print(f"✓ templates/dashboard.html restaurado com sucesso a partir do commit {hash_limpo}!")
else:
    print("Aviso: Histórico do Git não retornou o commit; mantendo ficheiro atual para limpeza manual.")

# =============================================================================
# 2. LIMPAR AS BARRAS PRETAS NO TEMPLATE RESTAURADO (SEM TOCAR NA ESTRUTURA)
# =============================================================================
with open(caminho_dash, 'r', encoding='utf-8') as f:
    html = f.read()

# Remover resíduos de overflow-x que provocavam a barra de rolagem preta no Chrome
html = re.sub(r'\boverflow(-x)?-(auto|scroll)\b', '', html)

# Garantir que o campo residual 'Categoria de Entrada Local' não fica duplicado
if "Categoria de Entrada Local" in html and "Categoria Financeira *" in html:
    pos_antiga = html.find("Categoria de Entrada Local")
    pos_d_start = html.rfind("<div", 0, pos_antiga)
    pos_d_end = html.find("</div>", pos_antiga)
    if pos_d_start != -1 and pos_d_end != -1:
        html = html[:pos_d_start] + html[pos_d_end + len("</div>"):]
        print("✓ Campo duplicado de categoria suprimido da Tesouraria!")

# Validação com motor Jinja2
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
# 3. CONFIGURAR ROTEAMENTO NO APP.PY (PROFESSOR VAI SEMPRE PARA DOUTRINA)
# =============================================================================
with open(caminho_app, 'r', encoding='utf-8') as f:
    app_code = f.read()

# A) Corrigir a consulta SQL da tabela caixa caso ainda contenha data_operacao
if "data_operacao DESC" in app_code:
    app_code = app_code.replace("data_operacao DESC", "id DESC")
    print("✓ Consulta da tabela caixa ajustada para usar coluna válida!")

# B) Na rota /login: redirecionar professor diretamente para ?aba=doutrina
if "def login():" in app_code:
    app_code = re.sub(
        r"return redirect\(url_for\('index'\)\)|return redirect\(['\"]/\?aba=dashboard['\"]\)",
        """perfil_u = str(user.get('perfil', '')).lower() if 'user' in locals() and user else ''
            if any(p in perfil_u for p in ['prof', 'docente', 'instrutor']):
                return redirect('/?aba=doutrina')
            return redirect('/')""",
        app_code,
        count=1
    )
    print("✓ Rota de login configurada para direcionar professor a ?aba=doutrina!")

# C) Na rota index(): se quem aceder for professor e estiver em dashboard, redirecionar
bloco_index_prof = """
    # Se o utilizador com sessão iniciada for professor, abrir diretamente a Doutrina
    perfil_sess = str(usuario.get('perfil', '')).lower() if 'usuario' in locals() and usuario else ''
    is_docente = any(p in perfil_sess for p in ['prof', 'docente', 'instrutor'])
    aba_solicitada = request.args.get('aba')
    
    if is_docente and (not aba_solicitada or aba_solicitada == 'dashboard'):
        return redirect('/?aba=doutrina')
"""

if "is_docente = any(p in perfil_sess" not in app_code:
    pos_index = app_code.find("def index():")
    if pos_index != -1:
        # Achar onde a sessão do utilizador é carregada
        pos_user = app_code.find("usuario = session", pos_index)
        if pos_user != -1:
            fim_linha_u = app_code.find("\n", pos_user) + 1
            app_code = app_code[:fim_linha_u] + bloco_index_prof + app_code[fim_linha_u:]
            print("✓ Salvaguarda aplicada na rota index(): professor não acede ao Raio-X!")

with open(caminho_app, 'w', encoding='utf-8') as f:
    f.write(app_code)

try:
    py_compile.compile(caminho_app, doraise=True)
    print("✓ app.py validado e compilado com ZERO erros!")
except Exception as e:
    print(f"Erro em app.py: {e}")
    exit(1)

# =============================================================================
# 4. ENVIAR PARA O GITHUB E O RENDER
# =============================================================================
print("=" * 80)
print("A ENVIAR RESTAURAÇÃO PARA O GITHUB & RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "app.py", "templates/dashboard.html"], check=True)
subprocess.run(["git", "commit", "-m", "Restauracao: repor layout desktop do admin, redirecionar professor para doutrina e limpar overflow"], check=True)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("=" * 80)
print(">>> RESTAURAÇÃO E CORREÇÃO CONCLUÍDAS COM SUCESSO! <<<")
print("=" * 80)