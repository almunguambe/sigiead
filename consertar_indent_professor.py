import py_compile

print("=" * 80)
print("A CORRIGIR INDENTAÇÃO DA LINHA 197 EM APP.PY...")
print("=" * 80)

caminho_app = 'app.py'
with open(caminho_app, 'r', encoding='utf-8') as f:
    linhas = f.readlines()

novas_linhas = []
for linha in linhas:
    # Remove espaços indevidos no início do bloco de inicialização do professor
    if "SELECT id FROM usuarios_sistema WHERE usuario = 'professor'" in linha:
        novas_linhas.append("if not consultar_um(\"SELECT id FROM usuarios_sistema WHERE usuario = 'professor'\"):\n")
    elif "VALUES ('Professor de Doutrina'" in linha:
        novas_linhas.append("    executar_comando(\"INSERT INTO usuarios_sistema (nome, usuario, senha, nivel, perfil, congregacao_id, criado_em) VALUES ('Professor de Doutrina', 'professor', 'prof123', 'local', 'professor', 1, '2026-10-19 23:00')\")\n")
    elif "# Garantir conta de professor ativa" in linha:
        novas_linhas.append("# Garantir conta de professor ativa\n")
    else:
        novas_linhas.append(linha)

with open(caminho_app, 'w', encoding='utf-8') as f:
    f.writelines(novas_linhas)

# Validar estritamente a sintaxe antes do push
try:
    py_compile.compile(caminho_app, doraise=True)
    print("✓ app.py corrigido e compilado com SUCESSO ABSOLUTO (Zero erros de sintaxe)!")
except Exception as e:
    print(f"Erro detectado em app.py: {e}")
    exit(1)

print("=" * 80)
print(">>> CORREÇÃO CONCLUÍDA! PODE ENVIAR O PUSH PARA O GITHUB! <<<")
print("=" * 80)