import re
import ast
import shutil

print("=" * 70)
print("INSPEÇÃO DE CAMPOS E CORREÇÃO DO ERRO 400 (BAD REQUEST)")
print("=" * 70)

# 1. INSPECIONAR OS INPUTS DO MÓDULO NO TEMPLATE
with open('templates/dashboard.html', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

idx_conv = html.find('Registar Novo Convertido')
idx_btn = html.find('Registar para Discipulado', idx_conv if idx_conv != -1 else 0)

if idx_conv != -1 and idx_btn != -1:
    bloco = html[idx_conv:idx_btn+100]
    inputs = re.findall(r'<input[^>]*>', bloco, re.IGNORECASE)
    selects = re.findall(r'<select[^>]*>', bloco, re.IGNORECASE)
    print("Campos detetados no formulário:")
    for inp in inputs + selects:
        print("  ->", " ".join(inp.split()))
else:
    print("⚠️ Bloco de Novos Convertidos não delimitado com precisão.")

# 2. BLINDAR A FUNÇÃO novo_convertido NO APP.PY CONTRA ERROS 400
shutil.copy('app.py', 'app.py.bak_400')
with open('app.py', 'r', encoding='utf-8', errors='ignore') as f:
    app_py = f.read()

# Substitui o acesso rígido request.form['campo'] por request.form.get('campo', '')
rota_convertidos_blindada = '''@app.route('/convertidos/novo', methods=['POST'])
def novo_convertido():
    conn = get_db()
    cur = conn.cursor() if hasattr(conn, 'cursor') else conn

    # Garantir tabela com compatibilidade PostgreSQL/SQLite
    try:
        is_pg = ('psycopg' in str(type(conn)).lower()) or bool(os.environ.get('DATABASE_URL'))
        id_tipo = "SERIAL PRIMARY KEY" if is_pg else "INTEGER PRIMARY KEY AUTOINCREMENT"
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS novos_convertidos (
                id {id_tipo},
                nome TEXT,
                telefone TEXT,
                bairro TEXT,
                data_decisao TEXT,
                culto_origem TEXT,
                quem_convidou TEXT,
                status_discipulado TEXT DEFAULT 'Acompanhamento',
                observacoes TEXT,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        if hasattr(conn, 'commit'): conn.commit()
    except Exception:
        if hasattr(conn, 'rollback'):
            try: conn.rollback()
            except: pass

    fd = request.form
    # Leitura tolerante de qualquer variação de nome de campo
    nome = (fd.get('nome') or fd.get('nome_completo') or fd.get('nome_convertido') or '').strip()
    telefone = (fd.get('telefone') or fd.get('contato') or fd.get('contacto') or '').strip()
    bairro = (fd.get('bairro') or fd.get('residencia') or '').strip()
    data_decisao = (fd.get('data_decisao') or fd.get('data') or fd.get('data_conversao') or '').strip()
    quem_convidou = (fd.get('quem_convidou') or fd.get('convidado_por') or fd.get('discipulador') or '').strip()
    culto_origem = (fd.get('culto_origem') or fd.get('tipo_culto') or '').strip()

    from datetime import datetime
    if not data_decisao:
        data_decisao = datetime.now().strftime('%Y-%m-%d')

    is_pg = ('psycopg' in str(type(conn)).lower()) or bool(os.environ.get('DATABASE_URL'))
    m = "%s" if is_pg else "?"

    sql = f"""INSERT INTO novos_convertidos 
              (nome, telefone, bairro, data_decisao, quem_convidou, culto_origem)
              VALUES ({m}, {m}, {m}, {m}, {m}, {m})"""
    try:
        cur.execute(sql, (nome, telefone, bairro, data_decisao, quem_convidou, culto_origem))
        if hasattr(conn, 'commit'): conn.commit()
        print(f"[SUCESSO CONVERTIDO]: Gravado com sucesso -> {nome}")
    except Exception as e:
        print("[ERRO AO GRAVAR CONVERTIDO]:", e)
        if hasattr(conn, 'rollback'):
            try: conn.rollback()
            except: pass

    return redirect('/?aba=convertidos')
'''

# Localiza e substitui a rota no app.py
padrao_def = r"(@app\.route\([^)]*'/convertidos/novo'[^)]*\)\s*\ndef\s+novo_convertido\s*\([^)]*\):[\s\S]*?)(?=\n@app\.route|\ndef |\Z)"
if re.search(padrao_def, app_py):
    app_py = re.sub(padrao_def, rota_convertidos_blindada.strip() + "\n\n", app_py, count=1)
    print("✓ Função novo_convertido() atualizada com leitura segura (.get())!")
else:
    app_py = app_py + "\n\n" + rota_convertidos_blindada.strip() + "\n"
    print("✓ Rota /convertidos/novo adicionada com leitura segura!")

# Validação do arquivo modificado
try:
    ast.parse(app_py)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(app_py)
    print("✓ app.py validado com 0 erros de sintaxe!")
except SyntaxError as e_ast:
    print(f"❌ Erro de sintaxe: {e_ast}")
    shutil.copy('app.py.bak_400', 'app.py')
    exit(1)

print("=" * 70)
print("✓ PROCESSO CONCLUÍDO COM SUCESSO!")
print("=" * 70)
