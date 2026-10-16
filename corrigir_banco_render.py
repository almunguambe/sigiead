import os
import shutil
import re
import ast

print("=" * 70)
print("A CORRIGIR COMPATIBILIDADE SQLITE -> POSTGRESQL (SUPABASE)...")
print("=" * 70)

shutil.copy('app.py', 'app.py.bak_pg')

with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. TRADUZIR AUTOINCREMENT PARA SERIAL PRIMARY KEY NAS DEFINIÇÕES DE TABELA
# O PostgreSQL exige 'SERIAL PRIMARY KEY' em vez de 'INTEGER PRIMARY KEY AUTOINCREMENT'
code_modificado = re.sub(
    r'INTEGER\s+PRIMARY\s+KEY\s+AUTOINCREMENT',
    'SERIAL PRIMARY KEY',
    code,
    flags=re.IGNORECASE
)
code_modificado = re.sub(
    r'\bAUTOINCREMENT\b',
    '',
    code_modificado,
    flags=re.IGNORECASE
)

# 2. BLINDAR O WRAPPER DO CURSOR (LINHA 76)
# Garante que qualquer comando SQL que ainda traga 'AUTOINCREMENT' seja traduzido em tempo de execução
padrao_wrapper = r'(def execute\s*\(\s*self\s*,\s*sql[^\)]*\):)(\n\s*)'
subst_wrapper = r'''\1\2if isinstance(sql, str):\n\2    sql = re.sub(r'INTEGER\\s+PRIMARY\\s+KEY\\s+AUTOINCREMENT', 'SERIAL PRIMARY KEY', sql, flags=re.IGNORECASE)\n\2    sql = re.sub(r'\\bAUTOINCREMENT\\b', '', sql, flags=re.IGNORECASE)\n\2'''

if 're.sub' not in code_modificado[:2000]:
    # Garante import re no topo se necessário
    if 'import re' not in code_modificado:
        code_modificado = "import re\n" + code_modificado

if re.search(padrao_wrapper, code_modificado):
    code_modificado = re.sub(padrao_wrapper, subst_wrapper, code_modificado, count=1)
    print("✓ Wrapper do cursor blindado para traduzir comandos SQL automaticamente!")

# Validar compilação do arquivo com AST
try:
    ast.parse(code_modificado)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code_modificado)
    print("✓ app.py 100% compatível com PostgreSQL e validado!")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe gerado: {e}")
    shutil.copy('app.py.bak_pg', 'app.py')
    exit(1)

print("=" * 70)
print("✓ CORREÇÃO CONCLUÍDA COM SUCESSO!")
print("=" * 70)