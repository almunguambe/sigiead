import os
import re
import py_compile
import jinja2

print("=" * 80)
print("A SEPARAR DEFINITIVAMENTE MISSÕES E CONSTRUÇÃO / OBRAS...")
print("=" * 80)

# =============================================================================
# 1. ATUALIZAR TEMPLATES/DASHBOARD.HTML (SUBSTITUIÇÃO PRECISA E GARANTIDA)
# =============================================================================
caminho_dash = os.path.join('templates', 'dashboard.html')
with open(caminho_dash, 'r', encoding='utf-8') as f:
    dash_html = f.read()

# 1. Ajustar a grelha de 4 para 5 colunas
dash_html = dash_html.replace('lg:grid-cols-4 gap-5 mb-8', 'sm:grid-cols-2 lg:grid-cols-5 gap-4 mb-8')

# 2. Definir os dois cards independentes
novos_dois_cards = """            <!-- CARD 4: MISSÕES -->
            <div class="bg-white p-4.5 rounded-2xl shadow-sm border-l-4 border-amber-500 border-slate-200">
                <div class="text-slate-500 text-[11px] font-bold uppercase flex items-center justify-between">
                    <span>🌍 Missões</span>
                    <span class="text-[9px] bg-amber-100 text-amber-900 px-1.5 py-0.5 rounded font-black">Campo</span>
                </div>
                <div class="text-xl font-black text-amber-700 mt-1">{{ "%.2f"|format(kpis.total_missoes or 0) }} MT</div>
                <div class="text-[10px] text-slate-400 mt-1">Evangelismo & Obreiros</div>
            </div>
            <!-- CARD 5: CONSTRUÇÃO & OBRAS -->
            <div class="bg-white p-4.5 rounded-2xl shadow-sm border-l-4 border-cyan-600 border-slate-200">
                <div class="text-slate-500 text-[11px] font-bold uppercase flex items-center justify-between">
                    <span>🏗️ Construção</span>
                    <span class="text-[9px] bg-cyan-100 text-cyan-900 px-1.5 py-0.5 rounded font-black">Obras</span>
                </div>
                <div class="text-xl font-black text-cyan-800 mt-1">{{ "%.2f"|format(kpis.total_construcao or 0) }} MT</div>
                <div class="text-[10px] text-slate-400 mt-1">Infraestrutura do Templo</div>
            </div>"""

# Substituir qualquer bloco de div que contenha "Missões & Obras"
padrao_card_antigo = r'<div class="[^"]*border-amber-500[^"]*">[\s\S]*?Missões & Obras[\s\S]*?<\/div>'

if re.search(padrao_card_antigo, dash_html):
    dash_html = re.sub(padrao_card_antigo, novos_dois_cards, dash_html)
    print("✓ Card 'Missões & Obras' substituído com sucesso por 2 cards separados!")
else:
    # Substituição por texto literal caso a classe varie
    texto_antigo = """<div class="text-slate-500 text-xs font-bold uppercase">Missões & Obras</div>
                <div class="text-2xl font-black text-amber-700 mt-1">{{ "%.2f"|format(kpis.total_missoes) }} MT</div>
                <div class="text-[11px] text-slate-400 mt-1">Campanhas e Construção</div>"""
    
    # Se encontrar o miolo, substitui a div envolvente
    if "Missões & Obras" in dash_html:
        dash_html = re.sub(r'<div[^>]*border-amber-500[^>]*>[\s\S]*?Campanhas e Construção[\s\S]*?<\/div>', novos_dois_cards, dash_html)
        print("✓ Card substituído por correspondência de conteúdo!")
    else:
        print("Aviso: 'Missões & Obras' já não estava presente ou o nome difere.")

# Validar com Jinja2
env = jinja2.Environment()
env.parse(dash_html)
with open(caminho_dash, 'w', encoding='utf-8') as f:
    f.write(dash_html)

# =============================================================================
# 2. ATUALIZAR APP.PY: GARANTIR CÁLCULOS SEPARADOS DE MISSÕES E CONSTRUÇÃO
# =============================================================================
caminho_app = 'app.py'
with open(caminho_app, 'r', encoding='utf-8') as f:
    app_text = f.read()

# Garantir o cálculo independente no app.py
if "'total_construcao'" not in app_text:
    # 1. Definir cálculo
    calculo_duplo = """total_missoes = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Entrada' and ('miss' in str(c.get('categoria', '')).lower() or 'evangel' in str(c.get('categoria', '')).lower())])
    total_construcao = sum([float(c.get('valor') or 0) for c in caixa if c.get('tipo') == 'Entrada' and ('constru' in str(c.get('categoria', '')).lower() or 'obra' in str(c.get('categoria', '')).lower() or 'tijol' in str(c.get('categoria', '')).lower() or 'cimento' in str(c.get('categoria', '')).lower())])"""

    app_text = re.sub(
        r"total_missoes\s*=\s*sum\(\[float\(c\.get\('valor'\)[\s\S]*?\]\)",
        calculo_duplo,
        app_text
    )

    # 2. Injetar no retorno dos KPIs
    app_text = app_text.replace(
        "'total_missoes': total_missoes,",
        "'total_missoes': total_missoes, 'total_construcao': total_construcao,"
    )
    print("✓ app.py: Adicionado 'total_construcao' aos KPIs!")

with open(caminho_app, 'w', encoding='utf-8') as f:
    f.write(app_text)

try:
    py_compile.compile('app.py', doraise=True)
    print("✓ app.py compilado sem erros!")
except Exception as e:
    print(f"Erro em app.py: {e}")

print("=" * 80)
print(">>> CONCLUÍDO COM SUCESSO! REINICIE O SERVIDOR COM: py app.py <<<")
print("=" * 80)