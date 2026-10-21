import os
import re
import py_compile
import jinja2

print("=" * 80)
print("A CORRIGIR ERRO 500 E A BLINDAR O MÓDULO DE ENSINO EM APP.PY...")
print("=" * 80)

caminho_app = 'app.py'
with open(caminho_app, 'r', encoding='utf-8') as f:
    app_text = f.read()

# 1. GARANTIR A CRIAÇÃO DA TABELA duvidas_alunos E progresso_licoes EM inicializar_banco()
tabelas_ensino_sql = """
        cur.execute(\"\"\"CREATE TABLE IF NOT EXISTS duvidas_alunos (
            id SERIAL PRIMARY KEY, aluno_id INT, licao_id TEXT, pergunta TEXT, 
            resposta_sistema TEXT, resposta_professor TEXT, professor_nome TEXT, criado_em TEXT
        );\"\"\")
        cur.execute(\"\"\"CREATE TABLE IF NOT EXISTS progresso_licoes (
            id SERIAL PRIMARY KEY, aluno_id INT, licao_id TEXT, resumo_aluno TEXT, 
            nota_teste REAL DEFAULT 0, status TEXT, criado_em TEXT
        );\"\"\")
"""
if "CREATE TABLE IF NOT EXISTS duvidas_alunos" not in app_text:
    app_text = app_text.replace(
        "conn.commit()",
        tabelas_ensino_sql + "\n        conn.commit()",
        1
    )

# 2. ATIVAR TRATAMENTO DE ERROS COM DIAGNÓSTICO EM TEMPO REAL NO NAVEGADOR
handler_500 = """
# =============================================================================
# CAPTURA DE ERRO 500 COM DIAGNÓSTICO DETALHADO NO ECRÃ
# =============================================================================
@app.errorhandler(500)
def erro_interno_servidor(e):
    import traceback
    return f'''
    <div style="font-family:sans-serif; padding:30px; background:#fff1f2; color:#9f1239; border:2px solid #f43f5e; border-radius:15px; margin:20px;">
        <h2 style="margin-top:0;">⚠️ Detalhes do Erro Interno (500):</h2>
        <pre style="background:#ffffff; padding:15px; border-radius:10px; border:1px solid #fda4af; overflow-x:auto; font-size:12px; color:#1e1b4b;">{traceback.format_exc()}</pre>
        <p><a href="/" style="color:#4338ca; font-weight:bold;">← Voltar à Página Principal</a></p>
    </div>
    ''', 500
"""

if "@app.errorhandler(500)" not in app_text:
    app_text = app_text.replace(
        "if __name__ == '__main__':",
        handler_500 + "\nif __name__ == '__main__':"
    )

# 3. RECONSTRUIR O BLOCO DE ENSINO NA ROTA index() COM CARREGAMENTO SEGURO
bloco_antigo_busca = r'# Carregar dados completos de Ensino & Doutrina[\s\S]*?stats_ensino = \{[\s\S]*?\}'

bloco_novo_busca = """# Carregar dados completos de Ensino & Doutrina com segurança
    opcoes = consultar_todos("SELECT * FROM opcoes_sistema")
    professores_cadastrados = consultar_todos("SELECT * FROM usuarios_sistema WHERE perfil = 'professor' AND congregacao_id = ? ORDER BY nome ASC", (cid,))
    duvidas_pendentes = consultar_todos(\"\"\"
        SELECT d.*, a.nome_aluno as aluno_nome 
        FROM duvidas_alunos d 
        LEFT JOIN doutrina a ON d.aluno_id = a.id 
        WHERE d.resposta_professor IS NULL OR d.resposta_professor = '' 
        ORDER BY d.id DESC
    \"\"\")
    
    classes_padrao = [
        'Preparação para Batismo nas Águas',
        'Discipulado de Novos Convertidos',
        'Classe I - Primeiros Passos',
        'Classe II - Vida Cristã',
        'Classe III - Maturidade Cristã',
        'Classe IV - Candidatos ao Batismo'
    ]
    classes_db = [op['valor'] for op in opcoes if isinstance(op, dict) and op.get('categoria') == 'classe_doutrina']
    lista_classes = list(dict.fromkeys(classes_padrao + classes_db))

    professores_padrao = ['Anselmo Leonardo Munguambe', 'Pastor Dirigente']
    nomes_prof_sistema = [p['nome'] for p in professores_cadastrados if isinstance(p, dict) and p.get('nome')]
    lista_professores = list(dict.fromkeys(professores_padrao + nomes_prof_sistema))

    aptos_count = len([a for a in doutrina if isinstance(a, dict) and a.get('situacao') == 'Apto / Aprovado'])
    stats_ensino = {
        'total_alunos': len(doutrina),
        'aptos': aptos_count,
        'em_formacao': len(doutrina) - aptos_count,
        'total_professores': len(professores_cadastrados),
        'total_duvidas': len(duvidas_pendentes)
    }"""

if re.search(bloco_antigo_busca, app_text):
    app_text = re.sub(bloco_antigo_busca, bloco_novo_busca, app_text)
    print("✓ Bloco de dados pedagógicos reconfigurado com carregamento seguro de 'opcoes'!")

with open(caminho_app, 'w', encoding='utf-8') as f:
    f.write(app_text)

try:
    py_compile.compile(caminho_app, doraise=True)
    print("✓ app.py: Compilação concluída sem erros!")
except Exception as e:
    print(f"Erro em app.py: {e}")
    exit(1)

# =============================================================================
# 4. BLINDAR TEMPLATES/DASHBOARD.HTML (FILTROS DE FORMATO E COMPARAÇÕES)
# =============================================================================
caminho_dash = os.path.join('templates', 'dashboard.html')
with open(caminho_dash, 'r', encoding='utf-8') as f:
    dash_html = f.read()

# Proteger conversões numéricas na tabela de alunos
dash_html = dash_html.replace(
    '{{ "%.0f"|format(a.aproveitamento or 0) }}%',
    '{{ "%.0f"|format(a.aproveitamento|float if a.aproveitamento else 0) }}%'
)
dash_html = dash_html.replace(
    '{% if (a.aproveitamento or 0) >= 70 %}',
    '{% if (a.aproveitamento|float if a.aproveitamento else 0) >= 70 %}'
)
dash_html = dash_html.replace(
    '{% if a.situacao != \'Apto / Aprovado\' and (a.aproveitamento or 0) >= 70 %}',
    '{% if a.situacao != \'Apto / Aprovado\' and (a.aproveitamento|float if a.aproveitamento else 0) >= 70 %}'
)

env = jinja2.Environment()
env.parse(dash_html)
with open(caminho_dash, 'w', encoding='utf-8') as f:
    f.write(dash_html)
print("✓ templates/dashboard.html blindado contra inconsistências de tipos!")

print("=" * 80)
print(">>> CORREÇÃO CONCLUÍDA COM TOTAL SUCESSO! <<<")
print("=" * 80)