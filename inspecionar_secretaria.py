import re

print("=" * 70)
print("INSPEÇÃO CIRÚRGICA: SECRETARIA & PLANOS")
print("=" * 70)

with open('templates/dashboard.html', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

# 1. Localizar o formulário de Planificação
pos_plan = html.find('Planificar Nova Actividade')
pos_btn = html.find('Gravar Planificação')

if pos_plan != -1 and pos_btn != -1:
    bloco_form = html[max(0, pos_plan-150):pos_btn+200]
    form_tag = re.search(r'<form[^>]*>', html[max(0, pos_plan-300):pos_btn])
    btn_tag = re.search(r'<button[^>]*>[\s\S]*?Gravar Planificação[\s\S]*?</button>', bloco_form)
    
    print("-> Tag <form> detetada:")
    print("  ", form_tag.group(0) if form_tag else "⚠️ NENHUMA TAG <form> ENCONTRADA ANTES DO BOTÃO!")
    
    print("\n-> Botão 'Gravar Planificação' detetado:")
    print("  ", btn_tag.group(0) if btn_tag else "⚠️ Tag do botão não isolada.")
    
    # Verificar se há inputs com 'name'
    inputs = re.findall(r'<(?:input|select|textarea)[^>]*name=[\'"][^\'"]*[\'"][^>]*>', bloco_form)
    print(f"\n-> Campos com atributo 'name' encontrados: {len(inputs)}")
    for inp in inputs[:5]:
        print("   *", inp)
else:
    print("⚠️ Bloco 'Planificar Nova Actividade' não encontrado no HTML.")

# 2. Inspecionar a Tabela 'Monitoramento do Cronograma Eclesiástico'
print("\n" + "=" * 70)
pos_tab = html.find('Monitoramento do Cronograma Eclesiástico')
if pos_tab != -1:
    trecho_tab = html[pos_tab:pos_tab+1200]
    tem_jinja = '{% for' in trecho_tab or '{{' in trecho_tab
    print(f"-> A tabela lateral usa dados dinâmicos do banco? {'SIM (Jinja2 ativo)' if tem_jinja else 'NÃO (Linhas fixas em HTML)'}")
    print("--- Amostra do conteúdo da tabela lateral ---")
    linhas_tr = re.findall(r'<tr[^>]*>[\s\S]*?</tr>', trecho_tab)
    for l in linhas_tr[:2]:
        print("  ", " ".join(l.split())[:120])
else:
    print("⚠️ Tabela lateral não localizada.")

print("=" * 70)
