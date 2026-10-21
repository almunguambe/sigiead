import re
import py_compile

print("=" * 80)
print("A CORRIGIR TRATAMENTO DE SQL COM '%' E INTERPOLAÇÃO EM APP.PY...")
print("=" * 80)

caminho_app = 'app.py'
with open(caminho_app, 'r', encoding='utf-8') as f:
    codigo = f.read()

# 1. Substituir a linha 215 pela versão segura parametrizada
codigo = codigo.replace(
    'executar_comando("UPDATE congregacoes SET nome = \'Igreja de Chicuque\' WHERE id = 1 OR nome LIKE \'%Sede Regional%\'")\n',
    'executar_comando("UPDATE congregacoes SET nome = \'Igreja de Chicuque\' WHERE id = 1 OR nome LIKE ?", (\'%Sede Regional%\',))\n'
)
codigo = codigo.replace(
    "executar_comando(\"UPDATE congregacoes SET nome = 'Igreja de Chicuque' WHERE id = 1 OR nome LIKE '%Sede Regional%'\")\n",
    "executar_comando(\"UPDATE congregacoes SET nome = 'Igreja de Chicuque' WHERE id = 1 OR nome LIKE ?\", ('%Sede Regional%',))\n"
)

# 2. Atualizar funções de banco para NÃO interpolar se params estiver vazio
bloco_db_seguro = '''def executar_comando(sql, params=()):
    conn = get_db()
    try:
        if USAR_POSTGRES:
            with conn.cursor() as cur:
                if params:
                    sql_pg = sql.replace('?', '%s')
                    cur.execute(sql_pg, params)
                else:
                    cur.execute(sql)
            conn.commit()
        else:
            with conn:
                if params:
                    conn.execute(sql, params)
                else:
                    conn.execute(sql)
    except Exception as e:
        print(f"[ERRO DB EXECUTAR]: {e} | SQL: {sql}")
        raise e
    finally:
        conn.close()

def consultar_todos(sql, params=()):
    conn = get_db()
    try:
        if USAR_POSTGRES:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if params:
                    sql_pg = sql.replace('?', '%s')
                    cur.execute(sql_pg, params)
                else:
                    cur.execute(sql)
                res = cur.fetchall()
                return [dict(r) for r in res]
        else:
            cur = conn.cursor()
            if params:
                cur.execute(sql, params)
            else:
                cur.execute(sql)
            res = cur.fetchall()
            return [dict(r) for r in res]
    except Exception as e:
        print(f"[ERRO DB CONSULTAR TODOS]: {e} | SQL: {sql}")
        return []
    finally:
        conn.close()

def consultar_um(sql, params=()):
    conn = get_db()
    try:
        if USAR_POSTGRES:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if params:
                    sql_pg = sql.replace('?', '%s')
                    cur.execute(sql_pg, params)
                else:
                    cur.execute(sql)
                res = cur.fetchone()
                return dict(res) if res else None
        else:
            cur = conn.cursor()
            if params:
                cur.execute(sql, params)
            else:
                cur.execute(sql)
            res = cur.fetchone()
            return dict(res) if res else None
    except Exception as e:
        print(f"[ERRO DB CONSULTAR UM]: {e} | SQL: {sql}")
        return None
    finally:
        conn.close()'''

padrao_antigo = r"def executar_comando\(sql, params=\(\)\):[\s\S]*?def consultar_um\(sql, params=\(\)\):[\s\S]*?finally:\s*conn\.close\(\)"

if re.search(padrao_antigo, codigo):
    codigo = re.sub(padrao_antigo, bloco_db_seguro, codigo)
    print("✓ Funções de banco corrigidas: execução direta sem parâmetros e tradução segura com parâmetros!")
else:
    print("Aviso: Padrão regex exato não encontrado, aplicando substituição por bloco.")
    # Localizar início de def executar_comando e fim de def consultar_um
    p_ini = codigo.find("def executar_comando(sql, params=()):")
    if p_ini != -1:
        p_fim = codigo.find("def inicializar_banco():", p_ini)
        if p_fim != -1:
            codigo = codigo[:p_ini] + bloco_db_seguro + "\n\n" + codigo[p_fim:]
            print("✓ Funções de banco substituídas com sucesso!")

with open(caminho_app, 'w', encoding='utf-8') as f:
    f.write(codigo)

try:
    py_compile.compile(caminho_app, doraise=True)
    print("✓ app.py compilado sem nenhum erro!")
except Exception as e:
    print(f"Erro em app.py: {e}")
    exit(1)

print("=" * 80)
print(">>> TUDO PRONTO! SUBA A CORREÇÃO PARA O GITHUB! <<<")
print("=" * 80)