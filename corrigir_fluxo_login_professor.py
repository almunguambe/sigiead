import os
import re
import py_compile
import subprocess
import jinja2

print("=" * 80)
print("A CORRIGIR O FLUXO DE LOGIN E A ADICIONAR ATALHO NA BARRA DO ADMIN...")
print("=" * 80)

caminho_app = 'app.py'
caminho_dash = os.path.join('templates', 'dashboard.html')

# =============================================================================
# 1. ATUALIZAR APP.PY: LOGIN RESPEITA A ROTA DO PROFESSOR E PARÂMETRO 'NEXT'
# =============================================================================
with open(caminho_app, 'r', encoding='utf-8') as f:
    app_code = f.read()

# Rota /professor guarda o parâmetro next=/professor se não estiver logado
app_code = re.sub(
    r"@app\.route\('/professor'\)[\s\S]*?def area_professor\(\):[\s\S]*?if not session\.get\('usuario'\):[^\n]*\n",
    """@app.route('/professor')
def area_professor():
    if not session.get('usuario'):
        return redirect(url_for('login', next='/professor'))\n""",
    app_code,
    count=1
)

# No login, se for professor ou se o parâmetro 'next' existir, redirecionar corretamente
pos_login = app_code.find("def login():")
if pos_login != -1:
    pos_sess = app_code.find("session['usuario'] = user", pos_login)
    if pos_sess != -1:
        fim_sess = app_code.find("\n", pos_sess) + 1
        pos_ret = app_code.find("return redirect", fim_sess)
        pos_ret_fim = app_code.find("\n", pos_ret) + 1
        
        fluxo_login_correto = """            perfil_u = str(user.get('perfil', '')).lower()
            proxima = request.args.get('next')
            if proxima:
                return redirect(proxima)
            if any(p in perfil_u for p in ['prof', 'docente', 'instrutor']):
                return redirect('/professor')
            return redirect('/?aba=dashboard')\n"""
            
        app_code = app_code[:fim_sess] + fluxo_login_correto + app_code[pos_ret_fim:]
        print("✓ Fluxo de login corrigido para enviar professores diretamente a /professor!")

# Na rota index (/): qualquer acesso de professor é desviado para /professor
pos_idx = app_code.find("def index():")
if pos_idx != -1:
    fim_idx = app_code.find("\n", pos_idx) + 1
    guarda_index = """    u_sess = session.get('usuario') or {}
    if any(p in str(u_sess.get('perfil', '')).lower() for p in ['prof', 'docente', 'instrutor']):
        return redirect('/professor')\n"""
    if "u_sess = session.get('usuario')" not in app_code:
        app_code = app_code[:fim_idx] + guarda_index + app_code[fim_idx:]
        print("✓ Guarda ativada na rota principal para evitar desvios ao Raio-X!")

with open(caminho_app, 'w', encoding='utf-8') as f:
    f.write(app_code)

py_compile.compile(caminho_app, doraise=True)
print("✓ app.py validado e compilado com ZERO erros!")

# =============================================================================
# 2. ADICIONAR BOTÃO DE ATALHO DIRETO NO MENU LATERAL DO ADMINISTRADOR
# =============================================================================
if os.path.exists(caminho_dash):
    with open(caminho_dash, 'r', encoding='utf-8') as f:
        dash_html = f.read()
    
    # Inserir atalho sob "ENSINO & FORMAÇÃO"
    botao_atalho_prof = """
                <a href="/professor" class="flex items-center gap-3 px-3 py-2 rounded-xl text-amber-300 bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 transition text-xs font-bold my-1">
                    <span class="text-base">👨‍🏫</span>
                    <span>Área do Professor (Direto)</span>
                </a>
    """
    if "Área do Professor (Direto)" not in dash_html:
        pos_ensino = dash_html.find("ENSINO & FORMAÇÃO")
        if pos_ensino != -1:
            pos_nav_item = dash_html.find("<a", pos_ensino)
            dash_html = dash_html[:pos_nav_item] + botao_atalho_prof + "\n" + dash_html[pos_nav_item:]
            print("✓ Atalho 'Área do Professor' inserido no menu lateral do Administrador!")

    env = jinja2.Environment()
    env.parse(dash_html)
    with open(caminho_dash, 'w', encoding='utf-8') as f:
        f.write(dash_html)

# =============================================================================
# 3. ENVIAR PARA O GITHUB E RENDER
# =============================================================================
subprocess.run(["git", "add", "app.py", "templates/dashboard.html"], check=True)
subprocess.run(["git", "commit", "-m", "Fluxo final: login redireciona professor para /professor e atalho no menu admin"], check=True)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("=" * 80)
print(">>> TUDO ATUALIZADO E PUBLICADO COM SUCESSO! <<<")
print("=" * 80)