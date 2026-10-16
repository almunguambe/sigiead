import os
import shutil
import re
import ast

print("=" * 70)
print("A ELIMINAR DUPLICADOS E A BLINDAR A ROTA NO APP.PY...")
print("=" * 70)

shutil.copy('app.py', 'app.py.bak_dup')

with open('app.py', 'r', encoding='utf-8', errors='ignore') as f:
    code = f.read()

# 1. Remover o bloco anexado no final do arquivo a partir do marcador
marcador = "# ====================================================================="
if marcador in code:
    code = code.split(marcador)[0].rstrip() + "\n"
    print("✓ Bloco duplicado do final do arquivo removido!")

# 2. Atualizar a rota /convertidos/novo original para ser tolerante a erros (.get())
padrao_original = r"(@app\.route\([^)]*'/convertidos/novo'[^)]*\)\s*\ndef\s+novo_convertido\s*\([^)]*\):[\s\S]*?)(?=\n@app\.route|\ndef |\Z)"

nova_funcao = '''@app.route('/convertidos/novo', methods=['POST'])
def novo_convertido():
    conn = get_db()
    cur = conn.cursor() if hasattr(conn, 'cursor') else conn

    fd = request.form
    nome = (fd.get('nome') or fd.get('nome_completo') or fd.get('nome_convertido') or 'Sem Nome').strip()
    telefone = (fd.get('telefone') or fd.get('contato') or fd.get('contacto') or '').strip()
    bairro = (fd.get('bairro') or fd.get('residencia') or '').strip()
    data_decisao = (fd.get('data_decisao') or fd.get('data') or fd.get('data_conversao') or '').strip()
    quem_convidou = (fd.get('quem_convidou') or fd.get('convidado_por') or fd.get('discipulador') or '').strip()
    culto_origem = (fd.get('culto_origem') or fd.get('tipo_culto') or 'Geral').strip()

    from datetime import datetime
    if not data_decisao:
        data_decisao = datetime.now().strftime('%Y-%m-%d')

    is_pg = ('psycopg' in str(type(conn)).lower()) or bool(os.environ.get('DATABASE_URL'))
    m = "%s" if is_pg else "?"

    sql = f"""INSERT INTO novos_convertidos 
              (nome, telefone, bairro, data_decisao, quem_convidou, culto_origem, status_discipulado)
              VALUES ({m}, {m}, {m}, {m}, {m}, {m}, {m})"""
    try:
        cur.execute(sql, (nome, telefone, bairro, data_decisao, quem_convidou, culto_origem, 'Acompanhamento'))
        if hasattr(conn, 'commit'):
            conn.commit()
        print(f"[SUCESSO CONVERTIDO]: Registado: {nome}")
    except Exception as e:
        print("[ERRO AO GRAVAR CONVERTIDO]:", e)
        if hasattr(conn, 'rollback'):
            try: conn.rollback()
            except: pass

    return redirect('/?aba=convertidos')'''

if re.search(padrao_original, code):
    code = re.sub(padrao_original, nova_funcao + "\n\n", code, count=1)
    print("✓ Função original novo_convertido() atualizada com leitura segura!")
else:
    code = code + "\n\n" + nova_funcao + "\n"

# 3. Remover qualquer eventual duplicado extra de 'def novo_convertido'
ocorrencias = list(re.finditer(padrao_original, code))
if len(ocorrencias) > 1:
    for extra in ocorrencias[1:]:
        code = code[:extra.start()] + code[extra.end():]
    print(f"✓ {len(ocorrencias) - 1} função(ões) duplicada(s) eliminada(s)!")

# 4. Validar sintaxe Python com AST
try:
    ast.parse(code)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("✓ app.py gravado e 100% validado sintaticamente!")
except SyntaxError as e:
    print(f"❌ Erro de compilação: {e}")
    shutil.copy('app.py.bak_dup', 'app.py')
    exit(1)

print("=" * 70)
print("✓ PROCESSO CONCLUÍDO COM SUCESSO!")
print("=" * 70)
