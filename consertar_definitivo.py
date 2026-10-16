import os
import shutil
import re
import ast

print("=" * 70)
print("1. A AJUSTAR FORMULÁRIO E TABELA DINÂMICA NO DASHBOARD.HTML...")
print("=" * 70)

tpl_dash = os.path.join('templates', 'dashboard.html')
with open(tpl_dash, 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

# Isolar o formulário de novos convertidos
pos_btn_conv = html.find('Registar para Discipulado')
if pos_btn_conv != -1:
    pos_bloco_conv = html.rfind('Registar Novo Convertido', 0, pos_btn_conv)
    if pos_bloco_conv != -1:
        trecho_form = html[pos_bloco_conv:pos_btn_conv]
        if '/convertidos/novo' not in trecho_form:
            pos_input = html.find('<input', pos_bloco_conv, pos_btn_conv)
            if pos_input != -1:
                html = html[:pos_input] + '</form>\n<form action="/convertidos/novo" method="POST">\n                            ' + html[pos_input:]
                print("✓ Tag <form action=\"/convertidos/novo\" method=\"POST\"> associada!")

# Tabela dinâmica de Acompanhamento Espiritual
pos_acomp = html.find('Acompanhamento Espiritual')
if pos_acomp != -1 and '{% for' not in html[pos_acomp:pos_acomp+1200]:
    tabela_dinamica = """
            <table style="width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 13px;">
                <thead>
                    <tr style="border-bottom: 2px solid #e2e8f0; text-align: left; color: #475569;">
                        <th style="padding: 10px 8px;">Nome</th>
                        <th style="padding: 10px 8px;">Contacto</th>
                        <th style="padding: 10px 8px;">Estado Espiritual</th>
                    </tr>
                </thead>
                <tbody>
                    {% if convertidos %}
                        {% for c in convertidos %}
                        <tr style="border-bottom: 1px solid #f1f5f9;">
                            <td style="padding: 12px 8px; font-weight: bold; color: #1e293b;">{{ c.nome }}</td>
                            <td style="padding: 12px 8px; color: #475569;">{{ c.telefone or c.contato or '---' }}</td>
                            <td style="padding: 12px 8px;">
                                <span style="background-color: #dcfce7; color: #166534; padding: 4px 10px; border-radius: 6px; font-weight: bold; font-size: 12px;">
                                    {{ c.status_discipulado or 'Acompanhamento' }}
                                </span>
                            </td>
                        </tr>
                        {% endfor %}
                    {% else %}
                        <tr>
                            <td colspan="3" style="text-align: center; padding: 30px; color: #94a3b8;">
                                Nenhum novo convertido registado ainda.
                            </td>
                        </tr>
                    {% endif %}
                </tbody>
            </table>
    """
    fim_card = html.find('</div>', pos_acomp)
    if fim_card != -1:
        html = html[:pos_acomp + len('Acompanhamento Espiritual')] + "</h3>" + tabela_dinamica + html[fim_card:]
        print("✓ Tabela Acompanhamento Espiritual conectada ao banco!")

with open(tpl_dash, 'w', encoding='utf-8') as f:
    f.write(html)

print("=" * 70)
print("2. A LIMPAR DUPLICADOS E BLINDAR APP.PY...")
print("=" * 70)

with open('app.py', 'r', encoding='utf-8', errors='ignore') as f:
    app_py = f.read()

# Remover blocos anexados no fim que continham duplicados
marcador = "# ====================================================================="
if marcador in app_py:
    app_py = app_py.split(marcador)[0].rstrip() + "\n"

# Remove todas as ocorrências antigas da rota /convertidos/novo
padrao_remover = r"@app\.route\([^)]*'/convertidos/novo'[^)]*\)\s*\ndef\s+novo_convertido\s*\([^)]*\):[\s\S]*?(?=\n@app\.route|\ndef |\Z)"
app_py = re.sub(padrao_remover, "", app_py)

# Remove context processors antigos duplicados se existirem
app_py = re.sub(r"@app\.context_processor\s*\ndef\s+injetar_dados_tabelas[\s\S]*?(?=\n@app\.route|\ndef |\Z)", "", app_py)

# Adiciona uma única rota novo_convertido e o context processor limpos
bloco_novo = '''
@app.route('/convertidos/novo', methods=['POST'])
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
    if not data_decisao or data_decisao in ('mm/dd/yyyy', '---'):
        data_decisao = datetime.now().strftime('%Y-%m-%d')

    is_pg = ('psycopg' in str(type(conn)).lower()) or bool(os.environ.get('DATABASE_URL'))
    m = "%s" if is_pg else "?"

    sql = f"""INSERT INTO novos_convertidos 
              (nome, telefone, bairro, data_decisao, quem_convidou, culto_origem, status_discipulado)
              VALUES ({m}, {m}, {m}, {m}, {m}, {m}, {m})"""
    try:
        cur.execute(sql, (nome, telefone, bairro, data_decisao, quem_convidou, culto_origem, 'Acompanhamento'))
        if hasattr(conn, 'commit'): conn.commit()
        print(f"[SUCESSO CONVERTIDO]: Registado -> {nome}")
    except Exception as e:
        print("[ERRO AO GRAVAR CONVERTIDO]:", e)
        if hasattr(conn, 'rollback'):
            try: conn.rollback()
            except: pass

    return redirect('/?aba=convertidos')

@app.context_processor
def injetar_dados_tabelas():
    ctx = {'convertidos': [], 'cultos': []}
    try:
        conn = get_db()
        cur = conn.cursor() if hasattr(conn, 'cursor') else conn
        try:
            cur.execute("SELECT * FROM novos_convertidos ORDER BY id DESC LIMIT 50")
            if cur.description:
                cols = [c[0] for c in cur.description]
                ctx['convertidos'] = [dict(zip(cols, r)) for r in cur.fetchall()]
        except Exception: pass
        try:
            cur.execute("SELECT * FROM cultos ORDER BY id DESC LIMIT 50")
            if cur.description:
                cols_c = [c[0] for c in cur.description]
                ctx['cultos'] = [dict(zip(cols_c, r)) for r in cur.fetchall()]
        except Exception: pass
    except Exception: pass
    return ctx
'''

app_py = app_py.strip() + "\n\n" + bloco_novo.strip() + "\n"

ast.parse(app_py)
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_py)
print("✓ app.py gravado com sintaxe 100% válida e sem duplicados!")
