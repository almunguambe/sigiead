import re

print("=" * 75)
print("AUDITORIA GERAL DE BOTÕES, FORMULÁRIOS E ROTAS (IEAD CHICUQUE)")
print("=" * 75)

# 1. LER TODAS AS ROTAS EXISTENTES NO APP.PY
with open('app.py', 'r', encoding='utf-8', errors='ignore') as f:
    app_py = f.read()

rotas_app = {}
padrao_rotas = re.findall(r"@app\.route\(\s*['\"]([^'\"]+)['\"]\s*(?:,\s*methods=\[([^\]]+)\])?\s*\)\s*\ndef\s+([a-zA-Z0-9_]+)", app_py)
for url, metodos, func in padrao_rotas:
    m_list = [m.replace("'", "").replace('"', '').strip() for m in metodos.split(',')] if metodos else ['GET']
    rotas_app[url] = {'metodos': m_list, 'funcao': func}

print(f"✓ Total de rotas mapeadas no app.py: {len(rotas_app)}\n")

# 2. ANALISAR TODOS OS FORMULÁRIOS NO TEMPLATES/DASHBOARD.HTML
with open('templates/dashboard.html', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

# Detetar todos os forms e suas posições
forms_abertos = list(re.finditer(r'<form\b([^>]*)>', html, re.IGNORECASE))
forms_fechados = list(re.finditer(r'</form>', html, re.IGNORECASE))

print(f"Contagem de Tags: <form> abertos: {len(forms_abertos)} | </form> fechados: {len(forms_fechados)}")
if len(forms_abertos) != len(forms_fechados):
    print("⚠️ ALERTA GRAVE: Há tags <form> abertas sem o respetivo </form>! Isso quebra os botões seguintes.\n")

print("-" * 75)
print(f"{'MÓDULO / FORMULÁRIO':<30} | {'ACTION':<25} | {'STATUS NO APP.PY'}")
print("-" * 75)

for idx, f_match in enumerate(forms_abertos, 1):
    attr = f_match.group(1)
    act_match = re.search(r'action=[\'"]([^\'"]*)[\'"]', attr)
    method_match = re.search(r'method=[\'"]([^\'"]*)[\'"]', attr)
    
    action = act_match.group(1) if act_match else "(Sem action)"
    metodo = (method_match.group(1) if method_match else "GET").upper()
    
    # Identificar contexto do formulário pelo texto anterior
    pos = f_match.start()
    trecho_anterior = html[max(0, pos-200):pos]
    titulos = re.findall(r'<(?:h1|h2|h3|h4|span|div)[^>]*>([^<]{3,30})</', trecho_anterior)
    nome_modulo = titulos[-1].strip() if titulos else f"Formulário #{idx}"

    # Validar se a rota existe no app.py
    if action in rotas_app:
        rota_info = rotas_app[action]
        if metodo in rota_info['metodos']:
            status = f"✅ OK ({metodo} -> {rota_info['funcao']})"
        else:
            status = f"❌ ERRO 405 (Método {metodo} não permitido em {action})"
    elif action == "(Sem action)" or action == "#" or action == "":
        status = "⚠️ Sem destino (recarrega a mesma página)"
    else:
        status = f"🚨 404 NOT FOUND (URL '{action}' não existe no backend!)"

    print(f"{nome_modulo[:28]:<30} | {action[:24]:<25} | {status}")

# 3. VERIFICAR MÓDULOS ESPECÍFICOS QUE ESTÃO SEM TAG <FORM>
print("\n" + "=" * 75)
print("VERIFICAÇÃO DE MÓDULOS CRÍTICOS:")
print("=" * 75)

modulos_chave = {
    'Secretaria / Planificação': ['planificacao', 'Secretaria & Planos'],
    'Cultos & Presenças': ['cultos', 'Registar Presen'],
    'Novos Convertidos': ['convertidos', 'Registar para Discipulado'],
    'Escala de Púlpito': ['escalas', 'Escala de Púlpito'],
    'Livro de Casamentos': ['casamentos', 'Livro de Casamentos'],
    'Livro de Óbitos': ['mortes', 'Livro de Óbitos']
}

for mod, pistas in modulos_chave.items():
    pos = -1
    for p in pistas:
        pos = html.find(p)
        if pos != -1: break
    
    if pos != -1:
        # Verifica se nos 800 caracteres seguintes há tag <form
        bloco = html[pos:pos+1200]
        tem_form = '<form' in bloco or '<form' in html[max(0, pos-400):pos]
        tem_submit = 'type="submit"' in bloco or 'type=\'submit\'' in bloco
        print(f"• {mod:<26}: {'[FORM: SIM]' if tem_form else '[FORM: NÃO DETETADO]'} | {'[SUBMIT: SIM]' if tem_submit else '[SUBMIT: NÃO]'}")
    else:
        print(f"• {mod:<26}: Módulo não localizado no dashboard.html")

print("=" * 75)
