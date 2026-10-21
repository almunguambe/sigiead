import re
import py_compile

print("=" * 80)
print("A LIMPAR A ROTA /LOGIN E A CORRIGIR A VARIÁVEL 'cid' EM APP.PY...")
print("=" * 80)

caminho_app = 'app.py'
with open(caminho_app, 'r', encoding='utf-8') as f:
    codigo = f.read()

# 1. REMOVER QUALQUER BLOCO DE ENSINO INDEVIDO DE TODAS AS ROTAS
padrao_bloco_ensino = r"[ \t]*# Carregar dados completos de Ensino[\s\S]*?stats_ensino = \{[\s\S]*?\n[ \t]*\}"
codigo_limpo = re.sub(padrao_bloco_ensino, "", codigo)

# 2. ASSEGURAR QUE def index() TEM cid DECLARADO LOGO NO INÍCIO
if "def index():" in codigo_limpo and "cid = session.get('congregacao_id', 1)" not in codigo_limpo[:codigo_limpo.find("return render_template('dashboard.html'")]:
    codigo_limpo = codigo_limpo.replace(
        "def index():\n",
        "def index():\n    cid = session.get('congregacao_id', 1) or 1\n",
        1
    )

# 3. BLOCO DE ENSINO BLINDADO E COM cid GARANTIDO
bloco_ensino_seguro = """
    # Carregar dados completos de Ensino & Doutrina com segurança absoluta
    cid = session.get('congregacao_id', 1) or 1
    opcoes = consultar_todos("SELECT * FROM opcoes_sistema")
    if 'doutrina' not in locals():
        doutrina = consultar_todos("SELECT * FROM doutrina WHERE congregacao_id = ? ORDER BY id DESC", (cid,))

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
    }
"""

# 4. INSERIR O BLOCO APENAS ANTES DO render_template DO DASHBOARD
padrao_dashboard = r"(return render_template\(['\"]dashboard\.html['\"])"
if re.search(padrao_dashboard, codigo_limpo):
    codigo_final = re.sub(padrao_dashboard, bloco_ensino_seguro + r"    \1", codigo_limpo, count=1)
    with open(caminho_app, 'w', encoding='utf-8') as f:
        f.write(codigo_final)
    print("✓ Rota /login limpa e bloco de ensino inserido exclusivamente em index() com 'cid' garantido!")
else:
    print("Aviso: Padrão render_template('dashboard.html') não encontrado.")

# 5. VALIDAÇÃO DE SINTAXE
try:
    py_compile.compile(caminho_app, doraise=True)
    print("✓ app.py compilado sem nenhum erro de sintaxe!")
except Exception as e:
    print(f"Erro detectado em app.py: {e}")
    exit(1)

print("=" * 80)
print(">>> PRONTO! SUBA A ATUALIZAÇÃO PARA O GITHUB! <<<")
print("=" * 80)