import os
import re
import jinja2

print("=" * 80)
print("A CORRIGIR CICLO ANINHADO DO TESTE EM TEMPLATES/PORTAL_ALUNO.HTML...")
print("=" * 80)

caminho_template = os.path.join('templates', 'portal_aluno.html')

if not os.path.exists(caminho_template):
    print(f"Erro: O ficheiro {caminho_template} não foi encontrado!")
    exit(1)

with open(caminho_template, 'r', encoding='utf-8') as f:
    conteudo = f.read()

# 1. Definir q_idx logo após iniciar a iteração das questões
conteudo = re.sub(
    r'({%\s*for\s+q\s+in\s+licao\.questoes\s*%})',
    r'\1\n                            {% set q_idx = loop.index0 %}',
    conteudo
)

# 2. Substituir a referência inválida loop.parent por q_idx
conteudo = re.sub(
    r'name="q_{{\s*loop\.parent\.loop\.index0\s*}}"',
    r'name="q_{{ q_idx }}"',
    conteudo
)
conteudo = re.sub(
    r'name="q_{{\s*loop\.parent\.index0\s*}}"',
    r'name="q_{{ q_idx }}"',
    conteudo
)

# 3. Validar a sintaxe do template com o compilador do Jinja2
try:
    env = jinja2.Environment()
    env.parse(conteudo)
    with open(caminho_template, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("✓ templates/portal_aluno.html corrigido e validado com sucesso!")
except Exception as e:
    print(f"Erro ao validar template Jinja2: {e}")
    exit(1)

print("=" * 80)
print(">>> CORREÇÃO CONCLUÍDA! PODE INICIAR O SERVIDOR COM: py app.py <<<")
print("=" * 80)