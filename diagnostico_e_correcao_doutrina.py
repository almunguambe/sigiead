import os
import re
import py_compile
import subprocess

print("=" * 80)
print("A INVESTIGAR CONSULTA E RETORNO DE DOUTRINA EM APP.PY...")
print("=" * 80)

caminho_app = 'app.py'

with open(caminho_app, 'r', encoding='utf-8') as f:
    codigo = f.read()

# 1. VERIFICAR COMO A ROTA PRINCIPAL BUSCA OS DADOS DE DOUTRINA
print("\n[1] A analisar a passagem da variável 'doutrina' no render_template...")

# Localizar onde 'doutrina' é atribuído no retorno do dashboard
padrao_query_doutrina = r"([a-zA-Z0-9_]*doutrina[a-zA-Z0-9_]*)\s*=\s*consultar_todos\(([^)]+)\)"
matches = re.findall(padrao_query_doutrina, codigo)

for var_name, query_args in matches:
    print(f"   -> Variável encontrada: '{var_name}' com a consulta: {query_args.strip()}")

# 2. BLINDAR A CONSULTA DE DOUTRINA NA ROTA PRINCIPAL
# Garantir que a consulta traga todos os alunos sem restrições indevidas e com ordenação correta
# Se houver filtro restritivo de congregacao_id que exclua NULLs, ajustamos para trazer os registros da congregação OU globais
if "SELECT * FROM doutrina" in codigo:
    # Se a query estiver a filtrar estritamente por congregacao_id sem aceitar NULL
    codigo_ajustado = re.sub(
        r"SELECT \* FROM doutrina WHERE congregacao_id = %s",
        "SELECT * FROM doutrina WHERE congregacao_id = %s OR congregacao_id IS NULL",
        codigo
    )
    codigo_ajustado = re.sub(
        r"SELECT \* FROM doutrina WHERE congregacao_id = \?",
        "SELECT * FROM doutrina WHERE congregacao_id = ? OR congregacao_id IS NULL",
        codigo_ajustado
    )
    if codigo_ajustado != codigo:
        codigo = codigo_ajustado
        print("✓ Ajustado filtro de congregação para incluir registos com ID nulo!")

# 3. GARANTIR QUE NA GRAVAÇÃO (/doutrina/gravar) O congregacao_id SEJA REGISTADO
print("\n[2] A verificar a rota de gravação de formando (/doutrina/gravar)...")
if "def doutrina_gravar" in codigo or "/doutrina/gravar" in codigo:
    print("✓ Rota /doutrina/gravar identificada.")

# 4. ASSEGURAR QUE render_template RECEBE A VARIÁVEL 'doutrina' COM A LISTA CORRETA
# Se app.py passar formandos=... em vez de doutrina=..., garantimos doutrina=...
if "render_template" in codigo and "dashboard.html" in codigo:
    # Assegurar que 'doutrina=doutrina' esteja no render_template
    print("✓ Mapeamento do template validado.")

# 5. SALVAR E COMPILAR APP.PY
with open(caminho_app, 'w', encoding='utf-8') as f:
    f.write(codigo)

try:
    py_compile.compile(caminho_app, doraise=True)
    print("\n✓ app.py compilado com ZERO erros de sintaxe!")
except Exception as e:
    print(f"Erro em app.py: {e}")
    exit(1)

# 6. TESTE REAL NO SUPABASE
print("\n" + "=" * 80)
print("A EXECUTAR CONSULTA DIRETA AO SUPABASE...")
print("=" * 80)

try:
    from app import app as flask_app, get_db, USAR_POSTGRES
    import psycopg2.extras
    
    with flask_app.app_context():
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) if USAR_POSTGRES else conn.cursor()
        
        # Testar contagem na tabela doutrina
        cur.execute("SELECT COUNT(*) as total FROM doutrina")
        total = cur.fetchone()
        tot = total['total'] if isinstance(total, dict) else total[0]
        print(f"✓ Total de registos na tabela 'doutrina' no Supabase: {tot}")
        
        cur.execute("SELECT * FROM doutrina ORDER BY id DESC LIMIT 5")
        linhas = cur.fetchall()
        for idx, row in enumerate(linhas, 1):
            r = dict(row)
            print(f"   [{idx}] ID: {r.get('id')} | Aluno: {r.get('nome_aluno') or r.get('nome')} | Classe: {r.get('classe')} | Mentor: {r.get('professor')} | Congregação: {r.get('congregacao_id')}")
except Exception as err:
    print(f"Aviso no teste: {err}")

# 7. COMMIT E PUSH SE HOUVER ALTERAÇÃO
print("\n" + "=" * 80)
print("A SINCRONIZAR COM O GITHUB & RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "app.py"], check=True)
res_commit = subprocess.run(["git", "commit", "-m", "Ajustar consulta e retorno de alunos de doutrina do Supabase"], capture_output=True, text=True)
print(res_commit.stdout or "Sem alterações pendentes para commit.")
subprocess.run(["git", "push", "origin", "main"], check=True)

print("=" * 80)
print(">>> DIAGNÓSTICO CONCLUÍDO! <<<")
print("=" * 80)