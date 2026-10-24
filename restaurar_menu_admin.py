import os
import re
import py_compile
import subprocess

caminho_dash = os.path.join('templates', 'dashboard.html')

with open(caminho_dash, 'r', encoding='utf-8') as f:
    html = f.read()

# Garantir que a barra lateral do Administrador fica visível no computador
html = html.replace('hidden md:flex md:w-64', 'flex w-64')
html = html.replace('class="hidden md:flex', 'class="flex')

with open(caminho_dash, 'w', encoding='utf-8') as f:
    f.write(html)

print("✓ Barra lateral do Administrador restaurada no computador!")

subprocess.run(["git", "add", "templates/dashboard.html"])
subprocess.run(["git", "commit", "-m", "Restaurar barra lateral visivel para o administrador no desktop"])
subprocess.run(["git", "push", "origin", "main"])

print(">>> MENU DO ADMINISTRADOR ATUALIZADO COM SUCESSO! <<<")