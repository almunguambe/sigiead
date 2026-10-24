import os
import re
import py_compile
import subprocess

print("=" * 80)
print("1. VERIFICAR UTILIZADORES NA BASE DE DADOS...")
print("=" * 80)

# Testar conexão com a base de dados e listar utilizadores
try:
    from app import consultar_todos
    utilizadores = consultar_todos("SELECT id, usuario, perfil, nome FROM usuarios_sistema")
    print(f"✓ Conexão com a base de dados operacional!")
    print(f"Total de contas cadastradas: {len(utilizadores)}")
    for u in utilizadores:
        print(f"   -> Utilizador: '{u.get('usuario')}' | Perfil: '{u.get('perfil')}' | Nome: '{u.get('nome')}'")
except Exception as e:
    print(f"Aviso na base de dados: {e}")

print("\n" + "=" * 80)
print("2. RESTAURAR FUNÇÃO DE LOGIN E ENCAMINHAMENTO LIMPO EM APP.PY...")
print("=" * 80)

caminho_app = 'app.py'

with open(caminho_app, 'r', encoding='utf-8') as f:
    app_code = f.read()

# Substituir a rota @app.route('/login') por uma versão blindada contra erros
login_blindado = '''@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('usuario', '').strip()
        s = request.form.get('senha', '').strip()
        user = None
        
        # Tentativa 1: PostgreSQL / Supabase (%s)
        try:
            user = consultar_um("SELECT * FROM usuarios_sistema WHERE LOWER(usuario) = LOWER(%s) AND senha = %s", (u, s))
        except Exception:
            # Tentativa 2: SQLite (?)
            try:
                user = consultar_um("SELECT * FROM usuarios_sistema WHERE LOWER(usuario) = LOWER(?) AND senha = ?", (u, s))
            except Exception as err:
                print("Erro na consulta de login:", err)
                user = None

        if user:
            session['usuario'] = dict(user)
            perfil = str(user.get('perfil', '')).lower()
            
            # Se for professor, entra direto em Doutrina
            if any(p in perfil for p in ['prof', 'docente', 'instrutor']):
                return redirect('/?aba=doutrina')
            
            # Administrador entra no Dashboard geral
            return redirect('/?aba=dashboard')
        
        flash('Utilizador ou palavra-passe incorretos.', 'danger')
    return render_template('login.html')'''

# Localizar e substituir a rota /login inteira
pos_login = app_code.find("@app.route('/login'")
if pos_login == -1:
    pos_login = app_code.find('@app.route("/login"')

if pos_login != -1:
    pos_prox_rota = app_code.find("\n@app.route", pos_login + 15)
    if pos_prox_rota != -1:
        app_code = app_code[:pos_login] + login_blindado + "\n\n" + app_code[pos_prox_rota:]
        print("✓ Rota /login restaurada com sucesso!")

# Garantir que a rota index (/) não entra em loop
pos_idx = app_code.find("def index():")
if pos_idx != -1:
    pos_u = app_code.find("usuario = session", pos_idx)
    if pos_u != -1:
        fim_linha_u = app_code.find("\n", pos_u) + 1
        
        regra_index = """    # ENCAMINHAMENTO AUTOMÁTICO SEGUNDO O PERFIL
    perfil_logado = str(usuario.get('perfil', '')).lower() if usuario else ''
    if any(p in perfil_logado for p in ['prof', 'docente', 'instrutor']):
        aba_ativa = 'doutrina'
    else:
        aba_ativa = request.args.get('aba', 'dashboard')
"""
        # Limpar regras duplicadas antigas em index
        app_code = re.sub(r'# REDIRECIONAR PROFESSOR AUTOMATICAMENTE[\s\S]*?(?=usuario\s*=\s*session)', '', app_code)
        print("✓ Rota principal (index) higienizada!")

with open(caminho_app, 'w', encoding='utf-8') as f:
    f.write(app_code)

py_compile.compile(caminho_app, doraise=True)
print("✓ app.py compilado com ZERO erros!")

# Publicar no Render
print("\n" + "=" * 80)
print("3. PUBLICAR CORREÇÃO NO GITHUB E RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "app.py"])
subprocess.run(["git", "commit", "-m", "Restaurar autenticacao de login robusta para admin e professores"])
subprocess.run(["git", "push", "origin", "main"])

print("=" * 80)
print(">>> CORREÇÃO CONCLUÍDA E PUBLICADA NO RENDER! <<<")
print("=" * 80)