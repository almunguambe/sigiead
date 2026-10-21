import psycopg2
from psycopg2.extras import RealDictCursor

URL = "postgresql://postgres.okkdueivpeefwqdktdjs:MunguambeAnselmo@aws-1-eu-central-1.pooler.supabase.com:5432/postgres?sslmode=require"

try:
    conn = psycopg2.connect(URL)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    print("=" * 60)
    print("DIAGNÓSTICO EM TEMPO REAL DAS TABELAS NO SUPABASE:")
    print("=" * 60)
    
    for tab in ['congregacoes', 'usuarios_sistema', 'membros', 'caixa', 'doutrina', 'cultos']:
        cur.execute(f"SELECT COUNT(*) as total FROM {tab};")
        qtd = cur.fetchone()['total']
        print(f"• Tabela '{tab}': {qtd} registo(s)")

    print("=" * 60)
    cur.close()
    conn.close()
except Exception as e:
    print(f"Erro de leitura: {e}")