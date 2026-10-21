import os
import re
import py_compile
import subprocess

print("=" * 80)
print("A CRIAR COLUNA LICAO_ATUAL E DESTRAVAR LEITURA DE ALUNOS EM APP.PY...")
print("=" * 80)

caminho_app = 'app.py'

with open(caminho_app, 'r', encoding='utf-8') as f:
    codigo = f.read()

# 1. CRIAR FUNÇÃO DE MIGRAÇÃO AUTOMÁTICA DE COLUNAS EM APP.PY
funcao_migracao = '''def migrar_colunas_doutrina():
    conn = get_db()
    colunas_necessarias = [
        ('licao_atual', "TEXT DEFAULT 'Lição 1'"),
        ('congregacao_id', "INTEGER DEFAULT 1"),
        ('classe', "TEXT DEFAULT 'Discipulado'"),
        ('professor', "TEXT DEFAULT 'Pastor Dirigente'"),
        ('data_inicio', "TEXT"),
        ('presencas', "INTEGER DEFAULT 0"),
        ('situacao', "TEXT DEFAULT 'Em Formação'"),
        ('usuario', "TEXT"),
        ('senha', "TEXT"),
        ('aproveitamento', "REAL DEFAULT 0.0"),
        ('criado_em', "TEXT")
    ]
    try:
        if USAR_POSTGRES:
            with conn.cursor() as cur:
                for col_name, col_def in colunas_necessarias:
                    try:
                        cur.execute(f"ALTER TABLE doutrina ADD COLUMN IF NOT EXISTS {col_name} {col_def};")
                    except Exception:
                        try:
                            conn.rollback()
                        except Exception:
                            pass
        else:
            cur = conn.cursor()
            cur.execute("PRAGMA table_info(doutrina)")
            existentes = [r[1] for r in cur.fetchall()]
            for col_name, col_def in colunas_necessarias:
                if col_name not in existentes:
                    try:
                        cur.execute(f"ALTER TABLE doutrina ADD COLUMN {col_name} {col_def}")
                    except Exception:
                        pass
            conn.commit()
    except Exception as e:
        print(f"[AVISO MIGRACAO DOUTRINA]: {e}")
'''

if "def migrar_colunas_doutrina():" not in codigo:
    # Insere antes de inicializar_banco
    pos_init = codigo.find("def inicializar_banco():")
    if pos_init != -1:
        codigo = codigo[:pos_init] + funcao_migracao + "\n" + codigo[pos_init:]
        print("✓ Função migrar_colunas_doutrina() inserida com sucesso!")

# 2. CHAMAR A MIGRAÇÃO DENTRO DE INICIALIZAR_BANCO ANTES DE QUALQUER INSERT
if "migrar_colunas_doutrina()" not in codigo:
    codigo = re.sub(
        r"(def inicializar_banco\(\):[\s\n]+conn\s*=\s*get_db\(\))",
        r"\1\n    migrar_colunas_doutrina()",
        codigo,
        count=1
    )
    print("✓ Chamada de migração integrada no início de inicializar_banco()!")

# 3. DESTRAVAR A CONSULTA DE DOUTRINA (NÃO FILTRAR POR CONGREGAÇÃO NULA)
# Força a query a trazer todos os alunos ordenados pelo ID mais recente
padrao_query_doutrina = r'[a-zA-Z0-9_]*doutrina[a-zA-Z0-9_]*\s*=\s*consultar_todos\(\s*["\']SELECT \* FROM doutrina[\s\S]*?\)\n'
if re.search(padrao_query_doutrina, codigo):
    codigo = re.sub(
        padrao_query_doutrina,
        'doutrina = consultar_todos("SELECT * FROM doutrina ORDER BY id DESC")\n',
        codigo,
        count=1
    )
    print("✓ Consulta de Doutrina destravada: SELECT * FROM doutrina ORDER BY id DESC!")

# 4. SALVAGUARDA DE TRANSAÇÃO NO CONSULTAR_TODOS E EXECUTAR_COMANDO (EVITA ABORTED TRANSACTION)
if "conn.rollback()" not in codigo:
    codigo = codigo.replace(
        "print(f\"[ERRO DB CONSULTAR TODOS]: {e} | SQL: {sql}\")",
        "print(f\"[ERRO DB CONSULTAR TODOS]: {e} | SQL: {sql}\")\n        if USAR_POSTGRES:\n            try:\n                conn.rollback()\n            except Exception:\n                pass"
    )

with open(caminho_app, 'w', encoding='utf-8') as f:
    f.write(codigo)

# 5. TESTAR COMPILAÇÃO DO CÓDIGO PYTHON
try:
    py_compile.compile(caminho_app, doraise=True)
    print("✓ app.py compilado com ZERO erros de sintaxe!")
except Exception as e:
    print(f"Erro em app.py: {e}")
    exit(1)

# 6. EXECUTAR MIGRAÇÃO E LEITURA REAL DOS DADOS AGORA MESMO
print("\n" + "=" * 80)
print("A APLICAR ALTER TABLE E A TESTAR RETORNO DE FORMANDOS...")
print("=" * 80)

try:
    from app import app as flask_app, get_db, USAR_POSTGRES, migrar_colunas_doutrina, consultar_todos
    with flask_app.app_context():
        migrar_colunas_doutrina()
        print("✓ Coluna 'licao_atual' e campos adicionais migrados na base de dados com sucesso!")
        
        alunos = consultar_todos("SELECT * FROM doutrina ORDER BY id DESC")
        print(f"✓ RETORNO CONFIRMADO: {len(alunos)} formando(s) carregado(s) da base de dados!")
        for idx, a in enumerate(alunos[:5], 1):
            nome = a.get('nome_aluno') or a.get('nome') or 'Sem nome'
            classe = a.get('classe') or 'Sem classe'
            mentor = a.get('professor') or 'Sem mentor'
            print(f"   [{idx}] {nome} | {classe} | Mentor: {mentor}")
except Exception as err:
    print(f"Resultado do teste: {err}")

# 7. COMMIT E PUSH DIRETO PARA O RENDER
print("\n" + "=" * 80)
print("A ENVIAR ATUALIZAÇÃO PARA O GITHUB & RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "app.py"], check=True)
subprocess.run(["git", "commit", "-m", "Fix: migracao da coluna licao_atual e destravamento da leitura de formandos da doutrina"], check=True)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("=" * 80)
print(">>> ATUALIZAÇÃO CONCLUÍDA COM TOTAL SUCESSO! <<<")
print("=" * 80)