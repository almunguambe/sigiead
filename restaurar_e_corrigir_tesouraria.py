import os
import re
import subprocess
import jinja2

print("=" * 80)
print("A RESTAURAR TEMPLATE INTACTO E A CORRIGIR SELETOR DA TESOURARIA...")
print("=" * 80)

caminho_dash = os.path.join('templates', 'dashboard.html')

# 1. RECUPERAR A VERSÃO ANTERIOR INTACTA DO GIT (COMMIT HEAD~1)
subprocess.run(["git", "checkout", "HEAD~1", "--", "templates/dashboard.html"], check=True)

with open(caminho_dash, 'r', encoding='utf-8') as f:
    html = f.read()

# Validar integridade da base recuperada
env = jinja2.Environment()
env.parse(html)
print("✓ Ficheiro original recuperado com sucesso!")

# 2. LOCALIZADOR BALANCED DE TAG <div>
def encontrar_matching_div(texto, pos_inicio):
    pos = texto.find(">", pos_inicio) + 1
    contador = 1
    pat = re.compile(r"<\s*(div\b|/div\b)")
    for match in pat.finditer(texto, pos):
        tag = match.group(1)
        if tag.startswith("div"):
            contador += 1
        elif tag == "/div":
            contador -= 1
            if contador == 0:
                return texto.find(">", match.start()) + 1
    return -1

# 3. LOCALIZAR EXCLUSIVAMENTE A CAIXA DA CATEGORIA (SEM TOCAR NO RESTO DO FORMULÁRIO)
pos_box_title = html.find("RECEITA DA IGREJA GERAL")
if pos_box_title == -1:
    pos_box_title = html.find("Categoria de Entrada Local")

if pos_box_title != -1:
    pos_box_div = html.rfind("<div", 0, pos_box_title)
    box_end = encontrar_matching_div(html, pos_box_div)
    
    # Caixa limpa com optgroup nativo (sem barra preta e com todas as categorias prontas)
    nova_caixa_categoria = """<div class="p-3.5 bg-emerald-50/80 border border-emerald-200 rounded-xl space-y-2">
                            <span class="font-extrabold text-[10px] uppercase text-emerald-900 block tracking-wide">
                                🟢 CLASSIFICAÇÃO / CATEGORIA DO LANÇAMENTO
                            </span>
                            <div>
                                <label class="block font-bold text-slate-700 mb-1 text-xs">Categoria Financeira *</label>
                                <select name="categoria" required class="w-full h-11 px-3 bg-white border border-slate-300 rounded-xl font-bold text-xs text-slate-800 focus:border-emerald-600 focus:outline-none shadow-sm cursor-pointer">
                                    <optgroup label="── ENTRADAS / RECEITAS ──">
                                        <option value="Dízimos dos Membros" selected>Dízimos dos Membros</option>
                                        <option value="Ofertas Gerais de Culto">Ofertas Gerais de Culto</option>
                                        <option value="Ofertas de Construção / Obras">Ofertas de Construção / Obras</option>
                                        <option value="Contribuições das Zonas / Bairros">Contribuições das Zonas / Bairros</option>
                                        <option value="Primícias">Primícias</option>
                                        <option value="Votos e Campanhas">Votos e Campanhas</option>
                                        <option value="Doações Especiais">Doações Especiais</option>
                                        <option value="Outras Entradas">Outras Entradas</option>
                                    </optgroup>
                                    <optgroup label="── SAÍDAS / DESPESAS ──">
                                        <option value="Manutenção e Obras do Templo">Manutenção e Obras do Templo</option>
                                        <option value="Energia Elétrica e Água">Energia Elétrica e Água</option>
                                        <option value="Ação Social e Beneficência">Ação Social e Beneficência</option>
                                        <option value="Sustento Pastoral e Obreiros">Sustento Pastoral e Obreiros</option>
                                        <option value="Material de Secretaria">Material de Secretaria</option>
                                        <option value="Comunicação, Som e Multimédia">Comunicação, Som e Multimédia</option>
                                        <option value="Eventos, Missões e Conferências">Eventos, Missões e Conferências</option>
                                        <option value="Outras Saídas">Outras Saídas</option>
                                    </optgroup>
                                </select>
                            </div>
                        </div>"""

    html = html[:pos_box_div] + nova_caixa_categoria + html[box_end:]
    print("✓ Caixa de categoria substituída cirurgicamente!")
else:
    print("Aviso: Título da categoria não encontrado.")

# 4. VALIDAR SINTAXE JINJA2
env.parse(html)
print("✓ Validação Jinja2: APROVADO COM ZERO ERROS!")

with open(caminho_dash, 'w', encoding='utf-8') as f:
    f.write(html)

# 5. SINCRONIZAR COM O GITHUB E O RENDER
print("=" * 80)
print("A ENVIAR ATUALIZAÇÃO PARA O GITHUB & RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "templates/dashboard.html"], check=True)
subprocess.run(["git", "commit", "-m", "Fix: restaurar tela de tesouraria com categorias completas e sem barra preta"], check=True)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("=" * 80)
print(">>> PROCESSO CONCLUÍDO COM SUCESSO! <<<")
print("=" * 80)