print("=" * 80)
print("A FIXAR VERSÃO ESTÁVEL PYTHON 3.11.9 PARA O RENDER...")
print("=" * 80)

# 1. Criar ficheiro .python-version (padrão oficial do Render)
with open('.python-version', 'w', encoding='utf-8') as f:
    f.write('3.11.9\n')
print("✓ .python-version criado com Python 3.11.9!")

# 2. Atualizar runtime.txt
with open('runtime.txt', 'w', encoding='utf-8') as f:
    f.write('python-3.11.9\n')
print("✓ runtime.txt atualizado!")

print("=" * 80)
print(">>> PRONTO PARA O COMMIT E PUSH! <<<")
print("=" * 80)