import re
import py_compile

print("=" * 80)
print("A CORRIGIR INDENTAÇÃO DA ROTA /financas/caixa/novo EM APP.PY...")
print("=" * 80)

caminho_app = 'app.py'
with open(caminho_app, 'r', encoding='utf-8') as f:
    codigo = f.read()

# Bloco exato e perfeitamente indentado da função caixa_gravar
funcao_corrigida = '''@app.route('/financas/caixa/novo', methods=['POST'])
def caixa_gravar():
    perfil = session.get('usuario_perfil', '')
    if perfil not in ['tesoureiro', 'admin']:
        return "<script>alert('Acesso negado! O lançamento de caixa é exclusivo da Tesouraria.'); window.location.href='/?aba=dashboard';</script>"

    cid = session.get('congregacao_id', 1)
    fd = request.form
    tipo = fd.get('tipo', 'Entrada').strip()
    conta = fd.get('conta', 'Caixa Físico').strip()
    try:
        val = float(fd.get('valor') or 0)
    except Exception:
        val = 0.0
    dt = fd.get('data_movimento', datetime.now().strftime('%Y-%m-%d')).strip()
    desc = fd.get('descricao', '').strip()
    destino_tipo = fd.get('destino_tipo', 'Igreja Geral').strip()
    depto = fd.get('departamento', 'Geral').strip()
    proposito = fd.get('proposito', '').strip()

    if tipo == 'Entrada':
        if destino_tipo == 'Igreja Mãe':
            categoria = "Igreja Mãe: " + fd.get('categoria_entrada_mae', 'Oferta Templo Sede').strip()
        elif destino_tipo == 'Departamento':
            categoria = f"Entrada: {depto}"
        else:
            categoria = "Igreja Geral: " + fd.get('categoria', 'Dízimos / Contribuições').strip()
    else:
        if destino_tipo == 'Igreja Mãe':
            categoria = "Igreja Mãe: " + fd.get('categoria_saida_mae', 'Despesa Templo Sede').strip()
        elif destino_tipo == 'Departamento':
            categoria = f"Saída: {depto}"
        else:
            categoria = "Igreja Geral: " + fd.get('categoria_saida_geral', 'Despesa Geral').strip()

    sql = """INSERT INTO caixa 
              (congregacao_id, tipo, categoria, valor, descricao, data_movimento, conta, destino_tipo, departamento, proposito, criado_em)
              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    executar_comando(sql, (cid, tipo, categoria, val, desc, dt, conta, destino_tipo, depto, proposito, datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=tesouraria')'''

# Substitui todo o bloco da rota /financas/caixa/novo pela versão corrigida
padrao_rota = r"@app\.route\('/financas/caixa/novo'[\s\S]*?return redirect\('/[?]aba=tesouraria'\)"

if re.search(padrao_rota, codigo):
    codigo = re.sub(padrao_rota, funcao_corrigida, codigo)
    with open(caminho_app, 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✓ Função caixa_gravar() reescrita com alinhamento padrão de 4 espaços!")
else:
    print("Erro: Padrão da rota não localizado diretamente para substituição.")

# Validação imediata de compilação
try:
    py_compile.compile(caminho_app, doraise=True)
    print("✓ Validação de sintaxe: app.py compilado sem nenhum erro de indentação!")
except Exception as e:
    print(f"Erro detectado em app.py: {e}")

print("=" * 80)
print(">>> CONCLUÍDO! PODE EXECUTAR: py app.py <<<")
print("=" * 80)