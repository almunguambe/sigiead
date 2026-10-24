import os
import re
import py_compile
import subprocess
import jinja2

print("=" * 80)
print("A PREENCHER OPÇÕES DOS SELETORES E A ELIMINAR BARRAS PRETAS...")
print("=" * 80)

caminho_dash = os.path.join('templates', 'dashboard.html')
caminho_app = 'app.py'

# =============================================================================
# 1. ATUALIZAR TEMPLATES/DASHBOARD.HTML COM OPÇÕES COMPLETAS E CSS LIMPO
# =============================================================================
with open(caminho_dash, 'r', encoding='utf-8') as f:
    html = f.read()

# Substituir o bloco dos seletores do formulário de membros por versões ricas com opções
bloco_seletores_membros = """
                    <!-- ESTADO CIVIL, ZONA E CÉLULA COM OPÇÕES COMPLETAS -->
                    <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
                        <div>
                            <label class="block text-xs font-bold text-slate-700 mb-1">Estado Civil *</label>
                            <select name="estado_civil" class="w-full px-3 py-2.5 bg-white border border-slate-300 rounded-xl text-slate-800 text-xs font-medium focus:ring-2 focus:ring-amber-500 focus:border-amber-500 outline-none transition shadow-sm" required>
                                <option value="">Selecione...</option>
                                <option value="Solteiro(a)">Solteiro(a)</option>
                                <option value="Casado(a)">Casado(a)</option>
                                <option value="Viúvo(a)">Viúvo(a)</option>
                                <option value="Divorciado(a)">Divorciado(a)</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-slate-700 mb-1">Zona Territorial</label>
                            <select name="zona" id="select_zona" class="w-full px-3 py-2.5 bg-white border border-slate-300 rounded-xl text-slate-800 text-xs font-medium focus:ring-2 focus:ring-amber-500 focus:border-amber-500 outline-none transition shadow-sm">
                                <option value="">Selecione a Zona...</option>
                                <option value="Zona 1 • Chicuque (Sede Central)">Zona 1 • Chicuque (Sede Central)</option>
                                <option value="Zona 2 • Chambone (Urbano)">Zona 2 • Chambone (Urbano)</option>
                                <option value="Zona 3 • Tinga (Residencial)">Zona 3 • Tinga (Residencial)</option>
                                <option value="Zona 4 • Rumbana (Expansão)">Zona 4 • Rumbana (Expansão)</option>
                                <option value="Zona 5 • Dambo / Malalane">Zona 5 • Dambo / Malalane</option>
                                <option value="Zona 6 • Macuamene / Bembe">Zona 6 • Macuamene / Bembe</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-slate-700 mb-1">Célula Familiar</label>
                            <select name="celula" id="select_celula" class="w-full px-3 py-2.5 bg-white border border-slate-300 rounded-xl text-slate-800 text-xs font-medium focus:ring-2 focus:ring-amber-500 focus:border-amber-500 outline-none transition shadow-sm">
                                <option value="">Selecione a Célula...</option>
                                <option value="Célula Betel (Chicuque)">Célula Betel (Chicuque Sede)</option>
                                <option value="Célula Sião (Chambone)">Célula Sião (Chambone Centro)</option>
                                <option value="Célula Peniel (Tinga)">Célula Peniel (Tinga Residencial)</option>
                                <option value="Célula Ebenézer (Rumbana)">Célula Ebenézer (Rumbana)</option>
                                <option value="Célula Jerusalém (Agostinho Neto)">Célula Jerusalém (Agostinho Neto)</option>
                                <option value="Célula Manassés (Dambo)">Célula Manassés (Dambo / Expansão)</option>
                            </select>
                        </div>
                    </div>

                    <!-- CARGO MINISTERIAL E DEPARTAMENTO COM OPÇÕES COMPLETAS -->
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-3">
                        <div>
                            <label class="block text-xs font-bold text-slate-700 mb-1">Cargo Ministerial</label>
                            <select name="cargo" class="w-full px-3 py-2.5 bg-white border border-slate-300 rounded-xl text-slate-800 text-xs font-medium focus:ring-2 focus:ring-amber-500 focus:border-amber-500 outline-none transition shadow-sm">
                                <option value="Membro Comungante">Membro Comungante</option>
                                <option value="Pastor Dirigente">Pastor Dirigente</option>
                                <option value="Presbítero / Ancião">Presbítero / Ancião</option>
                                <option value="Diácono / Diaconisa">Diácono / Diaconisa</option>
                                <option value="Evangelista">Evangelista</option>
                                <option value="Missionário(a)">Missionário(a)</option>
                                <option value="Líder de Célula">Líder de Célula</option>
                                <option value="Instrutor de Doutrina">Instrutor de Doutrina</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-slate-700 mb-1">Departamento</label>
                            <select name="departamento" class="w-full px-3 py-2.5 bg-white border border-slate-300 rounded-xl text-slate-800 text-xs font-medium focus:ring-2 focus:ring-amber-500 focus:border-amber-500 outline-none transition shadow-sm">
                                <option value="Geral / Nenhum">Geral / Nenhum</option>
                                <option value="Homens (Cavalheiros)">Homens (Cavalheiros)</option>
                                <option value="Mulheres (Senhoras)">Mulheres (Senhoras)</option>
                                <option value="Juventude Cristã (Jovens)">Juventude Cristã (Jovens)</option>
                                <option value="Crianças (Boa Esperança)">Crianças (Boa Esperança)</option>
                                <option value="Louvor & Coral">Louvor & Coral</option>
                                <option value="Evangelismo & Missões">Evangelismo & Missões</option>
                                <option value="Ação Social & Diaconia">Ação Social & Diaconia</option>
                                <option value="Escola Bíblica Dominical">Escola Bíblica Dominical</option>
                            </select>
                        </div>
                    </div>
"""

# Localizar o bloco antigo de Estado Civil até Departamento
padrao_busca = r'<label[^>]*>\s*Estado Civil[\s\S]*?</select>\s*</div>\s*</div>'
if re.search(padrao_busca, html):
    html = re.sub(padrao_busca, bloco_seletores_membros, html, count=1)
    print("✓ Seletores de Estado Civil, Zona, Célula, Cargo e Departamento preenchidos com sucesso!")

# Estilo CSS para garantir que as opções e o fundo do seletor sejam 100% brancos
css_limpeza = """
    <!-- ESTILO DOS SELETORES: FUNDO BRANCO E SEM BARRAS PRETAS -->
    <style id="css-seletores-limpos">
        select {
            background-color: #ffffff !important;
            color: #0f172a !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 0.75rem !important;
            outline: none !important;
            box-shadow: none !important;
            cursor: pointer !important;
        }
        select option {
            background-color: #ffffff !important;
            color: #0f172a !important;
            padding: 8px 12px !important;
        }
        select:focus {
            border-color: #f59e0b !important;
            box-shadow: 0 0 0 2px rgba(245, 158, 11, 0.2) !important;
        }
    </style>
"""

html = re.sub(r'<!-- ESTILO DOS SELETORES[\s\S]*?</style>', '', html)
if "</head>" in html:
    pos_head = html.find("</head>")
    html = html[:pos_head] + css_limpeza + "\n" + html[pos_head:]
elif "<body" in html:
    pos_body = html.find("<body")
    pos_body_close = html.find(">", pos_body) + 1
    html = html[:pos_body_close] + "\n" + css_limpeza + html[pos_body_close:]

env = jinja2.Environment()
env.parse(html)
with open(caminho_dash, 'w', encoding='utf-8') as f:
    f.write(html)
print("✓ templates/dashboard.html validado com sucesso!")

# =============================================================================
# 2. ATUALIZAR APP.PY: CARREGAR A LISTA DE MEMBROS NO PAINEL DO ADMINISTRADOR
# =============================================================================
with open(caminho_app, 'r', encoding='utf-8') as f:
    app_code = f.read()

# Na rota index(), garantir o carregamento de membros
carregamento_dados_admin = """    # Carregar dados gerais para o Administrador
    try:
        membros = consultar_todos("SELECT * FROM membros ORDER BY id DESC")
    except Exception:
        membros = []
    try:
        doutrina = consultar_todos("SELECT * FROM doutrina ORDER BY id DESC")
    except Exception:
        doutrina = []
    try:
        duvidas = consultar_todos("SELECT * FROM duvidas_alunos ORDER BY id DESC")
    except Exception:
        duvidas = []
        
    return render_template('dashboard.html',
                           usuario_logado=usuario,
                           aba_ativa=aba_ativa,
                           membros=membros,
                           doutrina=doutrina,
                           duvidas=duvidas)"""

padrao_retorno_index = r"# Carregar dados normais para o Administrador[\s\S]*?duvidas=duvidas\)"
if re.search(padrao_retorno_index, app_code):
    app_code = re.sub(padrao_retorno_index, carregamento_dados_admin, app_code, count=1)
    print("✓ app.py: Lista de membros integrada no retorno da rota index()!")

with open(caminho_app, 'w', encoding='utf-8') as f:
    f.write(app_code)

py_compile.compile(caminho_app, doraise=True)
print("✓ app.py validado e compilado com ZERO erros!")

# =============================================================================
# 3. ENVIAR PARA O GITHUB E RENDER
# =============================================================================
print("\n" + "=" * 80)
print("A ENVIAR ATUALIZAÇÃO PARA O RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "templates/dashboard.html", "app.py"])
subprocess.run(["git", "commit", "-m", "Preencher opcoes em todos os seletores e remover barras pretas"])
subprocess.run(["git", "push", "origin", "main"])

print("=" * 80)
print(">>> ATUALIZAÇÃO CONCLUÍDA E PUBLICADA NO RENDER! <<<")
print("=" * 80)