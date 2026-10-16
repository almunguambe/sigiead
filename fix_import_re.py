import os
import ast

with open('app.py', 'r', encoding='utf-8') as f:
    conteudo = f.read()

# Garante que import re é a primeiríssima linha do arquivo
linhas = conteudo.splitlines(keepends=True)
if not any(l.strip() == 'import re' for l in linhas[:10]):
    conteudo = "import re\n" + conteudo

try:
    ast.parse(conteudo)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("✓ 'import re' adicionado no topo de app.py com sucesso!")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe: {e}")