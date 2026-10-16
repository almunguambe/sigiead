import re

print("=" * 70)
print("DIAGNÓSTICO SEGURO DE BOTÕES E GRAVAÇÃO (APENAS LEITURA)")
print("=" * 70)

# 1. Inspecionar o template dashboard.html
with open('templates/dashboard.html', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

modulos = [
    ('Novos Convertidos', 'Registar Novo Convertido'),
    ('Escala de Púlpito', 'Escala de Púlpito'),
    ('Livro de Casamentos', 'Livro de Casamentos'),
    ('Livro de Óbitos', 'Livro de Óbitos')
]

for nome, termo in modulos:
    print(f"\n>>> MÓDULO: {nome} <<<")
    idx = html.find(termo)
    if idx == -1:
        print(f"  [!] Termo '{termo}' não localizado no HTML.")
        continue
    
    trecho = html[idx:idx+900]
    
    # Verifica se existe tag <form antes do botão
    tem_form = '<form' in html[max(0, idx-300):idx+300]
    print(f"  - Contém tag <form>? {'SIM' if tem_form else 'NÃO (Está dentro de <div> estática)'}")
    
    # Inspeciona os botões presentes no bloco
    botoes = re.findall(r'<button[^>]*>[\s\S]*?</button>', trecho, re.IGNORECASE)
    if botoes:
        for b in botoes:
            b_clean = " ".join(b.split())
            print(f"  - Botão encontrado: {b_clean[:110]}")
    else:
        print("  - Nenhum botão encontrado neste bloco.")

# 2. Inspecionar as rotas existentes no app.py
print("\n" + "=" * 70)
print("ROTAS DE GRAVAÇÃO MAPEADAS NO APP.PY:")
print("=" * 70)
with open('app.py', 'r', encoding='utf-8', errors='ignore') as f:
    app_code = f.read()

rotas = re.findall(r'(@app\.route\([^)]+\)\s*\ndef\s+[a-zA-Z0-9_]+)', app_code)
encontradas = 0
for r in rotas:
    r_uniline = " ".join(r.split())
    if any(k in r_uniline.lower() for k in ['convert', 'discip', 'escala', 'casam', 'obit', 'secretaria', 'culto']):
        print(f"  -> {r_uniline}")
        encontradas += 1

if encontradas == 0:
    print("  [!] Nenhuma rota específica para estes módulos foi encontrada no app.py.")
print("=" * 70)