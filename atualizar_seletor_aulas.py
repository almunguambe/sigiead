import os
import re
import subprocess
import jinja2

print("=" * 80)
print("A ATUALIZAR O SELETOR: DISCIPULADO, BATISMO E MINISTERIAL...")
print("=" * 80)

caminho = os.path.join('templates', 'dashboard.html')

with open(caminho, 'r', encoding='utf-8') as f:
    html = f.read()

# Novo bloco limpo com as 3 modalidades de ensino e sem barra de rolagem preta
novo_bloco_seletor = """
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
                        <div>
                            <label class="block font-bold text-slate-700 mb-1 text-xs">Tipo de Aula / Formação *</label>
                            <select name="classe" required class="w-full h-11 px-3 bg-white border border-slate-300 rounded-xl font-bold text-xs text-slate-800 focus:border-indigo-600 focus:outline-none shadow-sm cursor-pointer">
                                <option value="Discipulado">📖 Discipulado (Novos Convertidos)</option>
                                <option value="Batismo">🌊 Batismo (Preparação Batismal)</option>
                                <option value="Ministerial">🎓 Ministerial (Escola Ministerial)</option>
                            </select>
                        </div>
                        <div>
                            <label class="block font-bold text-slate-700 mb-1 text-xs">Instrutor / Mentor</label>
                            <input type="text" name="professor" placeholder="Pr. / Diác. / Instrutor" class="w-full h-11 px-3 border border-slate-300 rounded-xl bg-white font-medium text-xs text-slate-800 focus:border-indigo-600 focus:outline-none shadow-sm">
                        </div>
                    </div>
"""

# Localizar o bloco da Classe e do Mentor dentro do formulário de Doutrina
pos_select = html.find('name="classe"')
if pos_select != -1:
    pos_grid = html.rfind('<div class="grid', 0, pos_select)
    pos_prof = html.find('name="professor"', pos_grid)
    pos_div_close1 = html.find('</div>', pos_prof)
    pos_grid_close = html.find('</div>', pos_div_close1 + len('</div>'))
    
    end_pos = pos_grid_close + len('</div>')
    html = html[:pos_grid] + novo_bloco_seletor + html[end_pos:]
    print("✓ Linha do seletor substituída com sucesso!")
else:
    print("Aviso: 'name=\"classe\"' não localizado diretamente.")

# Validar rigorosamente a sintaxe Jinja2
env = jinja2.Environment()
env.parse(html)
print("✓ Validação Jinja2: APROVADO! Zero erros de sintaxe.")

with open(caminho, 'w', encoding='utf-8') as f:
    f.write(html)
print("✓ templates/dashboard.html atualizado!")

# Enviar commit e push direto para o Render
print("=" * 80)
print("A ENVIAR ATUALIZAÇÃO PARA O GITHUB & RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "templates/dashboard.html"], check=True)
subprocess.run(["git", "commit", "-m", "Ajustar seletor de ensino: Discipulado, Batismo e Ministerial sem scrollbar"], check=True)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("=" * 80)
print(">>> ATUALIZAÇÃO CONCLUÍDA COM TOTAL SUCESSO! <<<")
print("=" * 80)