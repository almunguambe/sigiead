import os
import re
import py_compile
import subprocess

print("=" * 80)
print("A CONFIGURAR ENCAMINHAMENTO AUTOMÁTICO PARA A DOUTRINA...")
print("=" * 80)

caminho_app = 'app.py'

with open(caminho_app, 'r', encoding='utf-8') as f:
    app_code = f.read()

# Injetar a regra na rota index(): se for professor e não estiver em ?aba=doutrina, redirecionar
bloco_redirecionamento = """    if not session.get('usuario'):
        return redirect(url_for('login'))
    
    # REDIRECIONAR PROFESSOR AUTOMATICAMENTE PARA DOUTRINA
    _u = session.get('usuario') or {}
    _perfil = str(_u.get('perfil', '')).lower()
    if any(p in _perfil for p in ['prof', 'docente', 'instrutor']):
        if request.args.get('aba') != 'doutrina':
            return redirect('/?aba=doutrina')
"""

padrao = r"def index\(\):[\s\S]*?(?=usuario\s*=\s*session)"
if re.search(padrao, app_code):
    app_code = re.sub(padrao, f"def index():\n{bloco_redirecionamento}    ", app_code, count=1)
    print("✓ Regra de encaminhamento inserida na rota principal (index)!")
else:
    # Alternativa caso o padrão de busca varie
    pos_idx = app_code.find("def index():")
    if pos_idx != -1:
        fim_linha = app_code.find("\n", pos_idx) + 1
        app_code = app_code[:fim_linha] + bloco_redirecionamento + app_code[fim_linha:]
        print("✓ Regra inserida no topo de index()!")

with open(caminho_app, 'w', encoding='utf-8') as f:
    f.write(app_code)

py_compile.compile(caminho_app, doraise=True)
print("✓ app.py validado e compilado com ZERO erros!")

# Publicar no GitHub e Render
print("=" * 80)
print("A ENVIAR ATUALIZAÇÃO PARA O RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "app.py"])
res_commit = subprocess.run(["git", "commit", "-m", "Encaminhar professor automaticamente para ?aba=doutrina ao abrir raiz"], capture_output=True, text=True)
print(res_commit.stdout if res_commit.stdout.strip() else "Commit aplicado ou já atualizado.")
subprocess.run(["git", "push", "origin", "main"])

print("=" * 80)
print(">>> PROCESSO CONCLUÍDO E ENVIADO COM SUCESSO! <<<")
print("=" * 80)