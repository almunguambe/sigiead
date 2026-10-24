import os
import re
import py_compile
import subprocess
import jinja2

print("=" * 80)
print("A INVESTIGAR E ELIMINAR BARRAS PRETAS EM TODOS OS SELETORES...")
print("=" * 80)

caminho_dash = os.path.join('templates', 'dashboard.html')

if not os.path.exists(caminho_dash):
    print("ERRO: templates/dashboard.html não encontrado!")
    exit(1)

with open(caminho_dash, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. MOSTRAR NO TERMINAL O CÓDIGO EXATO DO CAMPO CÉLULA
pos_cel = html.find('name="celula"')
if pos_cel == -1:
    pos_cel = html.find("Célula")

if pos_cel != -1:
    inicio = max(0, pos_cel - 200)
    fim = min(len(html), pos_cel + 350)
    print("\n[TRECHO DO CÓDIGO ENCONTRADO NO CAMPO CÉLULA]:")
    print("-" * 50)
    print(html[inicio:fim])
    print("-" * 50)

# 2. REMOVER QUALQUER BORDA PRETA, LINHA ESCURA OU DIVISOR EM SELETORES
html = re.sub(r'<div[^>]*class="[^"]*(bg-black|bg-slate-900|bg-slate-800|h-1|h-0\.5|border-black)[^"]*"[^>]*>\s*</div>', '', html)

# 3. APLICAR RESET DE COR E CONTORNO PARA ELIMINAR BARRAS PRETAS
css_reset = """
    <!-- RESET DEFINITIVO: ELIMINA BARRAS PRETAS E SCROLLBARS NOS SELETORES -->
    <style id="reset-seletores-limpos">
        /* Força todos os formulários em modo claro (evita contornos pretos do Chrome no Windows) */
        html, body, form, input, select, textarea, div {
            color-scheme: light !important;
        }

        /* Todos os seletores com fundo branco, cantos arredondados e borda cinzenta suave */
        select {
            background-color: #ffffff !important;
            color: #0f172a !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 0.75rem !important;
            outline: none !important;
            box-shadow: none !important;
            scrollbar-width: none !important;
            -ms-overflow-style: none !important;
        }

        select:focus {
            outline: none !important;
            border-color: #f59e0b !important;
            box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.15) !important;
        }

        select::-webkit-scrollbar {
            display: none !important;
            width: 0 !important;
            height: 0 !important;
        }
    </style>
"""

# Limpeza de blocos de estilo antigos
html = re.sub(r'<!-- ESTILO GLOBAL PARA ELIMINAR BARRAS PRETAS NOS SELETORES -->[\s\S]*?</style>', '', html)
html = re.sub(r'<!-- RESET DEFINITIVO: ELIMINA BARRAS PRETAS[\s\S]*?</style>', '', html)

if "</head>" in html:
    pos_h = html.find("</head>")
    html = html[:pos_h] + css_reset + "\n" + html[pos_h:]
elif "<body" in html:
    pos_b = html.find("<body")
    pos_b_close = html.find(">", pos_b) + 1
    html = html[:pos_b_close] + "\n" + css_reset + html[pos_b_close:]

# Validação Jinja2
env = jinja2.Environment()
try:
    env.parse(html)
    print("\n✓ templates/dashboard.html validado com ZERO erros no Jinja2!")
except Exception as e:
    print(f"Erro no Jinja2: {e}")
    exit(1)

with open(caminho_dash, 'w', encoding='utf-8') as f:
    f.write(html)

# 4. ENVIAR PARA O RENDER
print("\n" + "=" * 80)
print("A ENVIAR ATUALIZAÇÃO PARA O RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "templates/dashboard.html"])
subprocess.run(["git", "commit", "-m", "Eliminar definitivamente qualquer barra preta ou borda escura nos seletores"])
subprocess.run(["git", "push", "origin", "main"])

print("=" * 80)
print(">>> ATUALIZAÇÃO ENVIADA COM SUCESSO! <<<")
print("=" * 80)