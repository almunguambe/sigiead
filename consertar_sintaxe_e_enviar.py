import os
import re
import py_compile
import subprocess
import jinja2

print("=" * 80)
print("A REPARAR SINTAXE DE APP.PY E A CONCLUIR RESTAURAÇÃO...")
print("=" * 80)

caminho_app = 'app.py'
caminho_dash = os.path.join('templates', 'dashboard.html')

# 1. RECUPERAR A ESTRUTURA BASE DE APP.PY DO GIT HEAD (ELIMINA O ERRO DE SINTAXE NA LINHA 596)
subprocess.run(["git", "checkout", "HEAD", "--", "app.py"], check=True)
print("✓ app.py recuperado do Git HEAD sem erros de sintaxe!")

with open(caminho_app, 'r', encoding='utf-8') as f:
    app_code = f.read()

# 2. AJUSTE CIRÚRGICO NA CONSULTA DA TABELA CAIXA (SUBSTITUIR data_operacao INEXISTENTE)
if "data_operacao DESC" in app_code:
    app_code = app_code.replace("data_operacao DESC", "id DESC")
    print("✓ Coluna inexistente data_operacao corrigida na tabela caixa!")

# 3. ENCAMINHAMENTO NATIVO DO PROFESSOR (SEM QUEBRAR INDENTAÇÃO)
# Na rota /login: se for professor, entra em ?aba=doutrina
padrao_login = r"(session\['usuario'\]\s*=\s*user)"
novo_login = r"""\1
            if any(p in str(user.get('perfil', '')).lower() for p in ['prof', 'docente', 'instrutor']):
                return redirect('/?aba=doutrina')"""

if re.search(padrao_login, app_code):
    app_code = re.sub(padrao_login, novo_login, app_code, count=1)
    print("✓ Redirecionamento de login do professor inserido com indentação limpa!")

# Na rota index(): se a URL não tiver ?aba= e for professor, abre doutrina
padrao_aba = r"aba_ativa\s*=\s*request\.args\.get\(['\"]aba['\"],\s*['\"]dashboard['\"]\)"
novo_aba = """aba_req = request.args.get('aba')
    if not aba_req:
        perfil_u = str(usuario.get('perfil', '')).lower() if 'usuario' in locals() and usuario else ''
        aba_ativa = 'doutrina' if any(p in perfil_u for p in ['prof', 'docente', 'instrutor']) else 'dashboard'
    else:
        aba_ativa = aba_req"""

if re.search(padrao_aba, app_code):
    app_code = re.sub(padrao_aba, novo_aba, app_code, count=1)
    print("✓ Aba padrão da rota index() ajustada: professor abre sempre Doutrina!")

with open(caminho_app, 'w', encoding='utf-8') as f:
    f.write(app_code)

# 4. VALIDAÇÃO RIGOROSA DE COMPILAÇÃO
try:
    py_compile.compile(caminho_app, doraise=True)
    print("✓ app.py validado e compilado com ZERO erros!")
except Exception as e:
    print(f"Erro em app.py: {e}")
    exit(1)

# 5. ASSEGURAR QUE O TEMPLATE DASHBOARD RESTAURADO ESTÁ 100% VÁLIDO NO JINJA2
with open(caminho_dash, 'r', encoding='utf-8') as f:
    dash_html = f.read()

# Remover overflow-x dos selects que ativavam as barras pretas
dash_html = re.sub(r'\boverflow(-x)?-(auto|scroll)\b', '', dash_html)

env = jinja2.Environment()
env.parse(dash_html)
with open(caminho_dash, 'w', encoding='utf-8') as f:
    f.write(dash_html)
print("✓ templates/dashboard.html limpo e aprovado no Jinja2!")

# 6. SINCRONIZAR COM GITHUB E RENDER
print("=" * 80)
print("A ENVIAR ATUALIZAÇÃO DEFINITIVA PARA O GITHUB & RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "app.py", "templates/dashboard.html"], check=True)
subprocess.run(["git", "commit", "-m", "Restauracao: layout desktop original do admin, direcionamento do professor e sem overflow"], check=True)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("=" * 80)
print(">>> RESTAURAÇÃO CONCLUÍDA E PUBLICADA COM SUCESSO! <<<")
print("=" * 80)