import py_compile

print("=" * 80)
print("A CORRIGIR INDENTAÇÃO DA ATUALIZAÇÃO DE CHICUQUE EM APP.PY...")
print("=" * 80)

caminho_app = 'app.py'
with open(caminho_app, 'r', encoding='utf-8') as f:
    linhas = f.readlines()

novas_linhas = []
for linha in linhas:
    if "UPDATE congregacoes SET nome = 'Igreja de Chicuque'" in linha:
        # Alinha à coluna 0 (sem espaços no início)
        novas_linhas.append("executar_comando(\"UPDATE congregacoes SET nome = 'Igreja de Chicuque' WHERE id = 1 OR nome LIKE '%Sede Regional%'\")\n")
    elif "# Garantir nome correto de Chicuque" in linha:
        novas_linhas.append("# Garantir nome correto de Chicuque como congregação com suas zonas\n")
    else:
        novas_linhas.append(linha)

with open(caminho_app, 'w', encoding='utf-8') as f:
    f.writelines(novas_linhas)

# Validação estrita da compilação
try:
    py_compile.compile(caminho_app, doraise=True)
    print("✓ app.py corrigido e compilado com SUCESSO ABSOLUTO!")
except Exception as e:
    print(f"Erro detectado em app.py: {e}")
    exit(1)

print("=" * 80)
print(">>> PRONTO! EXECUTE AGORA: py app.py <<<")
print("=" * 80)