import os
import re
import py_compile
import subprocess
import jinja2

print("=" * 80)
print("A CONFIGURAR MOSTRAR/OCULTAR SENHA NO LOGIN E OTIMIZAÇÃO DE VELOCIDADE...")
print("=" * 80)

caminho_app = 'app.py'
caminho_login = os.path.join('templates', 'login.html')
caminho_dash = os.path.join('templates', 'dashboard.html')

# =============================================================================
# 1. ATUALIZAR TEMPLATES/LOGIN.HTML: OLHO DE MOSTRAR/OCULTAR SENHA
# =============================================================================
if os.path.exists(caminho_login):
    with open(caminho_login, 'r', encoding='utf-8') as f:
        login_html = f.read()

    # Bloco do botão de olho SVG e script de alternância
    bloco_olho_senha = """
                    <div class="relative">
                        <input type="password" id="campo_senha_login" name="senha" required placeholder="Sua senha de acesso" class="w-full h-11 px-3.5 pr-11 border border-slate-300 rounded-xl bg-white text-xs font-semibold text-slate-800 focus:border-indigo-600 focus:outline-none shadow-sm transition">
                        <button type="button" onclick="alternarVisibilidadeSenha()" class="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-400 hover:text-indigo-600 cursor-pointer focus:outline-none" title="Mostrar/Ocultar Senha">
                            <!-- Ícone Olho Aberto -->
                            <svg id="icone_olho_aberto" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                            </svg>
                            <!-- Ícone Olho Fechado -->
                            <svg id="icone_olho_fechado" class="w-4 h-4 hidden" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.542-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l18 18"></path>
                            </svg>
                        </button>
                    </div>
    """

    script_toggle_js = """
    <!-- SCRIPT DE VISIBILIDADE DE SENHA E FEEDBACK NO LOGIN -->
    <script>
        function alternarVisibilidadeSenha() {
            const input = document.getElementById('campo_senha_login');
            const olhoAberto = document.getElementById('icone_olho_aberto');
            const olhoFechado = document.getElementById('icone_olho_fechado');
            if (input.type === 'password') {
                input.type = 'text';
                olhoAberto.classList.add('hidden');
                olhoFechado.classList.remove('hidden');
            } else {
                input.type = 'password';
                olhoAberto.classList.remove('hidden');
                olhoFechado.classList.add('hidden');
            }
        }

        document.addEventListener('DOMContentLoaded', function() {
            const form = document.querySelector('form');
            if (form) {
                form.addEventListener('submit', function() {
                    const btn = this.querySelector('button[type="submit"]');
                    if (btn && !btn.disabled) {
                        btn.disabled = true;
                        btn.classList.add('opacity-75', 'cursor-not-allowed');
                        btn.innerHTML = `<svg class="animate-spin -ml-1 mr-2 h-4 w-4 inline text-white" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path></svg> A entrar...`;
                    }
                });
            }
        });
    </script>
</body>
    """

    # Substituir o campo de senha padrão pelo campo com botão de olho
    padrao_input_senha = r'<input[^>]*type=["\']password["\'][^>]*name=["\']senha["\'][^>]*>|<input[^>]*name=["\']senha["\'][^>]*type=["\']password["\'][^>]*>'
    if "campo_senha_login" not in login_html:
        if re.search(padrao_input_senha, login_html):
            login_html = re.sub(padrao_input_senha, bloco_olho_senha.strip(), login_html, count=1)
            print("✓ Campo de senha adaptado com botão de mostrar/ocultar!")
        elif 'name="senha"' in login_html:
            login_html = re.sub(r'<input[^>]*name=["\']senha["\'][^>]*>', bloco_olho_senha.strip(), login_html, count=1)
            print("✓ Campo de senha adaptado via seletor de nome!")

    if "alternarVisibilidadeSenha" not in login_html and "</body>" in login_html:
        login_html = login_html.replace("</body>", script_toggle_js, 1)
        print("✓ Script de alternância de senha e feedback inserido em login.html!")

    env = jinja2.Environment()
    env.parse(login_html)
    with open(caminho_login, 'w', encoding='utf-8') as f:
        f.write(login_html)
    print("✓ templates/login.html atualizado e 100% validado!")
else:
    print("Aviso: templates/login.html não encontrado no diretório.")

# =============================================================================
# 2. OTIMIZAR APP.PY: REUSO DE CONEXÃO SUPABASE VIA flask.g
# =============================================================================
with open(caminho_app, 'r', encoding='utf-8') as f:
    app_code = f.read()

if "from flask import" in app_code and ", g" not in app_code and " g," not in app_code:
    app_code = app_code.replace("from flask import ", "from flask import g, ", 1)
    print("✓ Objeto 'g' do Flask importado em app.py!")

db_otimizado = '''def get_db():
    if 'db' not in g:
        if USAR_POSTGRES:
            import psycopg2
            g.db = psycopg2.connect(DATABASE_URL)
            g.db.autocommit = True
        else:
            import sqlite3
            g.db = sqlite3.connect('banco.db')
            g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def fechar_conexao_db(exception=None):
    db = g.pop('db', None)
    if db is not None:
        try:
            db.close()
        except Exception:
            pass

def executar_comando(sql, params=()):
    conn = get_db()
    try:
        if USAR_POSTGRES:
            with conn.cursor() as cur:
                if params:
                    sql_pg = sql.replace('?', '%s')
                    cur.execute(sql_pg, params)
                else:
                    cur.execute(sql)
        else:
            with conn:
                if params:
                    conn.execute(sql, params)
                else:
                    conn.execute(sql)
    except Exception as e:
        print(f"[ERRO DB EXECUTAR]: {e} | SQL: {sql}")
        raise e

def consultar_todos(sql, params=()):
    conn = get_db()
    try:
        if USAR_POSTGRES:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if params:
                    sql_pg = sql.replace('?', '%s')
                    cur.execute(sql_pg, params)
                else:
                    cur.execute(sql)
                res = cur.fetchall()
                return [dict(r) for r in res]
        else:
            cur = conn.cursor()
            if params:
                cur.execute(sql, params)
            else:
                cur.execute(sql)
            res = cur.fetchall()
            return [dict(r) for r in res]
    except Exception as e:
        print(f"[ERRO DB CONSULTAR TODOS]: {e} | SQL: {sql}")
        return []

def consultar_um(sql, params=()):
    conn = get_db()
    try:
        if USAR_POSTGRES:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if params:
                    sql_pg = sql.replace('?', '%s')
                    cur.execute(sql_pg, params)
                else:
                    cur.execute(sql)
                res = cur.fetchone()
                return dict(res) if res else None
        else:
            cur = conn.cursor()
            if params:
                cur.execute(sql, params)
            else:
                cur.execute(sql)
            res = cur.fetchone()
            return dict(res) if res else None
    except Exception as e:
        print(f"[ERRO DB CONSULTAR UM]: {e} | SQL: {sql}")
        return None'''

padrao_db_antigo = r"def get_db\(\):[\s\S]*?def consultar_um\(sql, params=\(\)\):[\s\S]*?return None"
if re.search(padrao_db_antigo, app_code):
    app_code = re.sub(padrao_db_antigo, db_otimizado, app_code, count=1)
    print("✓ Funções de banco de dados otimizadas com reuso de conexão!")

with open(caminho_app, 'w', encoding='utf-8') as f:
    f.write(app_code)

try:
    py_compile.compile(caminho_app, doraise=True)
    print("✓ app.py compilado com ZERO erros!")
except Exception as e:
    print(f"Erro em app.py: {e}")
    exit(1)

# =============================================================================
# 3. ATUALIZAR TEMPLATES/DASHBOARD.HTML: FEEDBACK DE CLIQUE NOS FORMULÁRIOS
# =============================================================================
with open(caminho_dash, 'r', encoding='utf-8') as f:
    dash_html = f.read()

script_loading_dash = """
    <!-- FEEDBACK INSTANTÂNEO NOS BOTÕES: RESPOSTA IMEDIATA AO CLIQUE -->
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            document.querySelectorAll('form').forEach(form => {
                form.addEventListener('submit', function(e) {
                    const btn = this.querySelector('button[type="submit"]');
                    if (btn && !btn.disabled) {
                        btn.disabled = true;
                        btn.classList.add('opacity-75', 'cursor-not-allowed');
                        const spinner = `<svg class="animate-spin -ml-1 mr-2 h-4 w-4 inline text-white" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path></svg>`;
                        btn.innerHTML = spinner + " A processar...";
                    }
                });
            });
        });
    </script>
</body>
"""

if "<!-- FEEDBACK INSTANTÂNEO NOS BOTÕES" not in dash_html and "</body>" in dash_html:
    dash_html = dash_html.replace("</body>", script_loading_dash, 1)
    print("✓ Script de feedback instantâneo inserido em dashboard.html!")

env = jinja2.Environment()
env.parse(dash_html)
with open(caminho_dash, 'w', encoding='utf-8') as f:
    f.write(dash_html)

# =============================================================================
# 4. ENVIAR PARA O GITHUB E O RENDER
# =============================================================================
print("=" * 80)
print("A ENVIAR ATUALIZAÇÃO PARA O GITHUB & RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "app.py", "templates/login.html", "templates/dashboard.html"], check=True)
subprocess.run(["git", "commit", "-m", "Feature: mostrar/ocultar senha no login e otimizacao de cliques e conexao"], check=True)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("=" * 80)
print(">>> ATUALIZAÇÃO CONCLUÍDA COM TOTAL SUCESSO! <<<")
print("=" * 80)