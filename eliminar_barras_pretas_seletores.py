import os
import re
import py_compile
import subprocess
import jinja2

print("=" * 80)
print("A ELIMINAR BARRAS PRETAS E A MODERNIZAR TODOS OS SELETORES...")
print("=" * 80)

# Estilo CSS global para eliminar qualquer barra preta e scrollbar em <select>
css_seletores_limpos = """
    <!-- ESTILO GLOBAL PARA ELIMINAR BARRAS PRETAS NOS SELETORES -->
    <style>
        select {
            -webkit-appearance: none !important;
            -moz-appearance: none !important;
            appearance: none !important;
            background-color: #ffffff !important;
            color: #0f172a !important;
            background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2364748b' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e") !important;
            background-repeat: no-repeat !important;
            background-position: right 0.85rem center !important;
            background-size: 1rem !important;
            padding-right: 2.5rem !important;
            overflow: hidden !important;
            scrollbar-width: none !important; /* Firefox */
            -ms-overflow-style: none !important;  /* IE/Edge */
        }
        select::-webkit-scrollbar {
            display: none !important;
            width: 0 !important;
            height: 0 !important;
        }
    </style>
"""

templates_alvo = [
    os.path.join('templates', 'dashboard.html'),
    os.path.join('templates', 'area_professor.html'),
    os.path.join('templates', 'ensino_aulas.html')
]

env = jinja2.Environment()

for caminho in templates_alvo:
    if not os.path.exists(caminho):
        continue
    
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # 1. Remover classes de overflow dos <select>
    conteudo = re.sub(r'(<select[^>]*class="[^"]*)\boverflow(-x|-y)?-(auto|scroll|hidden)\b([^"]*)"', r'\1\4"', conteudo)

    # 2. Substituir fundos pretos (bg-slate-900 / bg-slate-800) em <select> por fundo branco limpo
    conteudo = re.sub(r'(<select[^>]*class="[^"]*)\bbg-slate-(800|900)\b([^"]*)"', r'\1bg-white text-slate-800 border-slate-200\3"', conteudo)

    # 3. Inserir o CSS de limpeza no <head> se ainda não existir
    if "ESTILO GLOBAL PARA ELIMINAR BARRAS PRETAS NOS SELETORES" not in conteudo:
        if "</head>" in conteudo:
            pos_head = conteudo.find("</head>")
            conteudo = conteudo[:pos_head] + css_seletores_limpos + "\n" + conteudo[pos_head:]
        elif "<body" in conteudo:
            pos_body = conteudo.find("<body")
            conteudo = conteudo[:pos_body] + css_seletores_limpos + "\n" + conteudo[pos_body:]

    # Validar integridade com Jinja2
    try:
        env.parse(conteudo)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print(f"✓ {caminho}: Barras pretas removidas e seletores estilizados com sucesso!")
    except Exception as e:
        print(f"Erro ao processar {caminho}: {e}")

# =============================================================================
# ENVIAR ATUALIZAÇÃO PARA O GITHUB E RENDER
# =============================================================================
print("\n" + "=" * 80)
print("A ENVIAR ATUALIZAÇÃO PARA O RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "templates/dashboard.html", "templates/area_professor.html", "templates/ensino_aulas.html"])
subprocess.run(["git", "commit", "-m", "Limpeza visual: eliminadas barras pretas e scrollbars de todos os seletores"])
subprocess.run(["git", "push", "origin", "main"])

print("=" * 80)
print(">>> TODOS OS SELETORES ATUALIZADOS COM SUCESSO ABSOLUTO! <<<")
print("=" * 80)