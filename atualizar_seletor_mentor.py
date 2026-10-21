import os
import re
import subprocess
import jinja2
import py_compile

print("=" * 80)
print("A CONFIGURAR SELETOR DINÂMICO DE INSTRUTOR / MENTOR...")
print("=" * 80)

caminho_dash = os.path.join('templates', 'dashboard.html')
caminho_app = 'app.py'

# =============================================================================
# 1. ATUALIZAR TEMPLATES/DASHBOARD.HTML (SUBSTITUIR INPUT POR SELECT DINÂMICO)
# =============================================================================
with open(caminho_dash, 'r', encoding='utf-8') as f:
    html = f.read()

novo_seletor_mentor = """<div>
                            <label class="block font-bold text-slate-700 mb-1 text-xs">Instrutor / Mentor *</label>
                            <select name="professor" required class="w-full h-11 px-3 bg-white border border-slate-300 rounded-xl font-bold text-xs text-slate-800 focus:border-indigo-600 focus:outline-none shadow-sm cursor-pointer truncate">
                                <option value="" disabled {% if not usuario_logado or usuario_logado.perfil not in ['professor', 'pastor'] %}selected{% endif %}>Selecione o Instrutor / Mentor...</option>
                                {% if professores_cadastrados %}
                                    {% for p in professores_cadastrados %}
                                    <option value="{{ p.nome }}" {% if usuario_logado and usuario_logado.nome == p.nome %}selected{% endif %}>👨‍🏫 {{ p.nome }}</option>
                                    {% endfor %}
                                {% endif %}
                                <option value="Anselmo Leonardo Munguambe" {% if usuario_logado and usuario_logado.nome == 'Anselmo Leonardo Munguambe' %}selected{% endif %}>👨‍🏫 Anselmo Leonardo Munguambe</option>
                                <option value="Pastor Dirigente" {% if usuario_logado and usuario_logado.nome == 'Pastor Dirigente' %}selected{% endif %}>👨‍🏫 Pastor Dirigente</option>
                            </select>
                        </div>"""

padrao_input_professor = r'<div>\s*<label[^>]*>Instrutor / Mentor[^<]*</label>\s*<input[^>]*name="professor"[^>]*>\s*</div>'

if re.search(padrao_input_professor, html):
    html = re.sub(padrao_input_professor, novo_seletor_mentor, html, count=1)
    print("✓ Campo de texto do Instrutor substituído por seletor dinâmico!")
else:
    print("Aviso: Padrão exato do input de professor não encontrado.")

# Validar sintaxe Jinja2
env = jinja2.Environment()
env.parse(html)
print("✓ templates/dashboard.html validado com ZERO erros no Jinja2!")

with open(caminho_dash, 'w', encoding='utf-8') as f:
    f.write(html)

# =============================================================================
# 2. GARANTIR EM APP.PY QUE TODOS OS PROFESSORES E PASTORES SEJAM CARREGADOS
# =============================================================================
with open(caminho_app, 'r', encoding='utf-8') as f:
    app_text = f.read()

# Assegurar consulta completa de docentes ativos
if "SELECT * FROM usuarios_sistema WHERE perfil = 'professor'" in app_text:
    app_text = app_text.replace(
        "SELECT * FROM usuarios_sistema WHERE perfil = 'professor'",
        "SELECT * FROM usuarios_sistema WHERE perfil IN ('professor', 'pastor')"
    )

with open(caminho_app, 'w', encoding='utf-8') as f:
    f.write(app_text)

try:
    py_compile.compile(caminho_app, doraise=True)
    print("✓ app.py compilado sem nenhum erro!")
except Exception as e:
    print(f"Erro em app.py: {e}")
    exit(1)

# =============================================================================
# 3. ENVIAR DIRETAMENTE PARA O GITHUB E O RENDER
# =============================================================================
print("=" * 80)
print("A ENVIAR ATUALIZAÇÃO PARA O GITHUB & RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "templates/dashboard.html", "app.py"], check=True)
subprocess.run(["git", "commit", "-m", "Associar aluno ao mentor: seletor dinamico de professores e mentores cadastrados"], check=True)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("=" * 80)
print(">>> PROCESSO CONCLUÍDO COM TOTAL SUCESSO! <<<")
print("=" * 80)