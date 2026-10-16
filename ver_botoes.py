import re

print("=" * 60)
print("INSPEÇÃO DOS BOTÕES E FORMS NO DASHBOARD.HTML")
print("=" * 60)

with open('templates/dashboard.html', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

for termo in ["Registar para Discipulado", "Registar Presen"]:
    print(f"\n>>> PESQUISA: '{termo}' <<<")
    idx = html.find(termo)
    if idx != -1:
        ini = max(0, idx - 450)
        fim = min(len(html), idx + 250)
        print("--- Trecho ao redor do botão ---")
        print(html[ini:fim].strip())
        print("---")
        form_ini = html.rfind('<form', 0, idx)
        form_fim = html.find('</form>', idx)
        if form_ini != -1:
            tag = html[form_ini:html.find('>', form_ini)+1]
            print(f"Tag <form> anterior: {tag}")
            print(f"Fecha </form> após o botão? {'SIM' if (form_fim != -1 and form_fim > idx) else 'NÃO'}")
        else:
            print("⚠️ NÃO ESTÁ DENTRO DE NENHUMA TAG <form>!")
    else:
        print(f"Texto '{termo}' não encontrado no HTML!")

print("\n" + "=" * 60)
print("FUNÇÃO novo_convertido NO APP.PY")
print("=" * 60)
try:
    with open('app.py', 'r', encoding='utf-8', errors='ignore') as f:
        app_txt = f.read()
    idx_conv = app_txt.find("def novo_convertido")
    if idx_conv != -1:
        ini = max(0, app_txt.rfind('@app.route', 0, idx_conv))
        print(app_txt[ini:idx_conv+500].strip())
    else:
        print("Função 'novo_convertido' não localizada em app.py.")
except Exception as e:
    print(f"Erro ao ler app.py: {e}")
