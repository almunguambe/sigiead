import os
import re

caminho = os.path.join('templates', 'dashboard.html')
with open(caminho, 'r', encoding='utf-8', errors='ignore') as f:
    linhas = f.readlines()

print("=" * 70)
print("INSPEÇÃO DA LINHA 353 E ARREDORES:")
print("=" * 70)

ini = max(0, 345 - 1)
fim = min(len(linhas), 365)
for i in range(ini, fim):
    marcador = " >>> LINHA 353 >>> " if (i + 1) == 353 else "                   "
    print(f"{i+1:4d}{marcador}{linhas[i].rstrip()}")

# Correção: envolver variáveis Jinja soltas dentro de tags <script> com aspas ou filtro tojson
conteudo = "".join(linhas)

# Corrige injeções como: = {{ aba_ativa }}; -> = "{{ aba_ativa }}";
conteudo_corrigido = re.sub(r'=\s*\{\{\s*([a-zA-Z0-9_]+)\s*\}\}\s*;', r'= "{{ \1 }}";', conteudo)

# Garante que o container principal de conteúdo não fique oculto se o JS falhar
conteudo_corrigido = conteudo_corrigido.replace('id="conteudo_principal" class="hidden"', 'id="conteudo_principal"')

with open(caminho, 'w', encoding='utf-8') as f:
    f.write(conteudo_corrigido)

print("\n" + "=" * 70)
print("✓ Injeções Jinja2 em JavaScript corrigidas com aspas defensivas!")
print("=" * 70)
