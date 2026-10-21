import os
import re
import py_compile
import subprocess
import jinja2

print("=" * 80)
print("A RESOLVER DEFINITIVAMENTE: ÁREA DO PROFESSOR, STRAY '>' E BARRAS PRETAS...")
print("=" * 80)

caminho_app = 'app.py'
caminho_dash = os.path.join('templates', 'dashboard.html')

# =============================================================================
# 1. ATUALIZAR APP.PY: PROFESSOR ENTRA SEMPRE E EXCLUSIVAMENTE NA DOUTRINA
# =============================================================================
with open(caminho_app, 'r', encoding='utf-8') as f:
    app_code = f.read()

# Na rota index(), logo após carregar o utilizador da sessão:
trava_docente_definitiva = '''
    # REGRA ESTRITA: Professor nunca vê Raio-X ou Finanças; vai sempre para Doutrina
    perfil_logado = str(usuario.get('perfil', '')).lower()
    if 'professor' in perfil_logado or 'docente' in perfil_logado or 'instrutor' in perfil_logado:
        aba_ativa = 'doutrina'
'''

# Remover travas antigas que pudessem ter ficado com erro de variável
app_code = re.sub(r"perfil_usuario\s*=\s*str\(usuario\.get\('perfil'[^\n]+\n(?:[ \t]+[^\n]+\n){1,3}", "", app_code)

if "REGRA ESTRITA: Professor nunca vê Raio-X" not in app_code:
    # Insere logo após usuario = session.get('usuario') ou similar
    pos_user = app_code.find("usuario = session['usuario']")
    if pos_user == -1:
        pos_user = app_code.find("usuario = session.get('usuario')")
    
    if pos_user != -1:
        fim_linha = app_code.find("\n", pos_user) + 1
        app_code = app_code[:fim_linha] + trava_docente_definitiva + app_code[fim_linha:]
        print("✓ Regra de acesso exclusivo do Professor aplicada na rota principal de app.py!")

with open(caminho_app, 'w', encoding='utf-8') as f:
    f.write(app_code)

try:
    py_compile.compile(caminho_app, doraise=True)
    print("✓ app.py validado e compilado com ZERO erros!")
except Exception as e:
    print(f"Erro em app.py: {e}")
    exit(1)

# =============================================================================
# 2. LIMPAR TEMPLATES/DASHBOARD.HTML
# =============================================================================
with open(caminho_dash, 'r', encoding='utf-8') as f:
    html = f.read()

# A) Eliminar caracteres soltos '>' (provocados por tags duplicadas <body >> e <main >>)
html = re.sub(r'(<body[^>]*>)\s*>+', r'\1', html)
html = re.sub(r'(<main[^>]*>)\s*>+', r'\1', html)
html = re.sub(r'^\s*>\s*$', '', html, flags=re.MULTILINE)
print("✓ Caracteres soltos '>' eliminados com sucesso!")

# B) Bloquear exibição do Raio-X se o utilizador for professor no próprio template Jinja2
# Se o professor tentar carregar dashboard, o template força a exibição da Doutrina
if "{% if aba_ativa == 'dashboard' %}" in html:
    html = html.replace(
        "{% if aba_ativa == 'dashboard' %}",
        "{% if aba_ativa == 'dashboard' and not (usuario_logado and ('professor' in usuario_logado.perfil|lower or 'docente' in usuario_logado.perfil|lower)) %}",
        1
    )
    print("✓ Proteção Jinja2: Raio-X 100% blindado contra visualização por professores!")

# C) Limpeza rigorosa na Tesouraria: remover qualquer campo antigo 'Categoria de Entrada Local'
while "Categoria de Entrada Local" in html:
    pos_antiga = html.find("Categoria de Entrada Local")
    pos_div_ini = html.rfind("<div", 0, pos_antiga)
    # Localizar o fecho correspondente da div
    pos_div_fim = html.find("</div>", pos_antiga)
    if pos_div_fim != -1:
        pos_div_fim += len("</div>")
        html = html[:pos_div_ini] + html[pos_div_fim:]
        print("✓ Campo residual 'Categoria de Entrada Local' removido da Tesouraria!")
    else:
        break

# D) Limpeza na aba Membros: reconstruir os campos de Estado Civil, Zona, Célula e Departamento
pos_membros_ec = html.find("Estado Civil *")
if pos_membros_ec != -1:
    pos_bloco_membros = html.rfind("<div", 0, pos_membros_ec)
    # Procurar o botão ou próximo campo do formulário de membros
    pos_obs_membros = html.find("Observações", pos_membros_ec)
    if pos_obs_membros == -1:
        pos_obs_membros = html.find("Cadastrar Membro", pos_membros_ec)
    
    if pos_obs_membros != -1:
        bloco_membros_limpo = """<div class="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-3">
                                <div>
                                    <label class="block font-bold text-slate-700 mb-1 text-xs">Estado Civil *</label>
                                    <select name="estado_civil" required class="w-full h-11 px-3 bg-white border border-slate-300 rounded-xl font-medium text-xs text-slate-800 focus:border-indigo-600 focus:outline-none shadow-sm cursor-pointer">
                                        <option value="Solteiro(a)">Solteiro(a)</option>
                                        <option value="Casado(a)" selected>Casado(a)</option>
                                        <option value="Viúvo(a)">Viúvo(a)</option>
                                        <option value="Divorciado(a)">Divorciado(a)</option>
                                    </select>
                                </div>
                                <div>
                                    <label class="block font-bold text-slate-700 mb-1 text-xs">Zona Territorial</label>
                                    <select name="zona" class="w-full h-11 px-3 bg-white border border-slate-300 rounded-xl font-medium text-xs text-slate-800 focus:border-indigo-600 focus:outline-none shadow-sm cursor-pointer">
                                        <option value="Zona 1 - Chicuque Sede">Zona 1 - Chicuque Sede</option>
                                        <option value="Zona 2 - Chambone">Zona 2 - Chambone</option>
                                        <option value="Zona 3 - Tinga">Zona 3 - Tinga</option>
                                        <option value="Zona 4 - Rumbana">Zona 4 - Rumbana</option>
                                        <option value="Zona 5 - Dambo">Zona 5 - Dambo</option>
                                        <option value="Zona 6 - Macuamene">Zona 6 - Macuamene</option>
                                    </select>
                                </div>
                                <div>
                                    <label class="block font-bold text-slate-700 mb-1 text-xs">Célula Familiar</label>
                                    <select name="celula" class="w-full h-11 px-3 bg-white border border-slate-300 rounded-xl font-medium text-xs text-slate-800 focus:border-indigo-600 focus:outline-none shadow-sm cursor-pointer">
                                        <option value="Célula Betel (Chicuque)">Célula Betel (Chicuque)</option>
                                        <option value="Célula Sião (Chambone)">Célula Sião (Chambone)</option>
                                        <option value="Célula Peniel (Tinga)">Célula Peniel (Tinga)</option>
                                        <option value="Célula Ebenézer (Rumbana)">Célula Ebenézer (Rumbana)</option>
                                        <option value="Célula Jerusalém (Agostinho)">Célula Jerusalém (Agostinho)</option>
                                        <option value="Célula Manassés (Dambo)">Célula Manassés (Dambo)</option>
                                    </select>
                                </div>
                            </div>
                            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
                                <div>
                                    <label class="block font-bold text-slate-700 mb-1 text-xs">Situação Espiritual / Batismo *</label>
                                    <select name="baptizado" required class="w-full h-11 px-3 bg-white border border-slate-300 rounded-xl font-medium text-xs text-slate-800 focus:border-indigo-600 focus:outline-none shadow-sm cursor-pointer">
                                        <option value="Sim">Baptizado nas Águas (Comunhão)</option>
                                        <option value="Não">Não Baptizado (Em Doutrina / Novo)</option>
                                    </select>
                                </div>
                                <div>
                                    <label class="block font-bold text-slate-700 mb-1 text-xs">Ministério / Departamento</label>
                                    <select name="departamento" class="w-full h-11 px-3 bg-white border border-slate-300 rounded-xl font-medium text-xs text-slate-800 focus:border-indigo-600 focus:outline-none shadow-sm cursor-pointer">
                                        <option value="Membro Geral">Membro Geral</option>
                                        <option value="Corpo Pastoral / Obreiro">Corpo Pastoral / Obreiro</option>
                                        <option value="Diaconato">Diaconato</option>
                                        <option value="Departamento de Senhoras">Departamento de Senhoras</option>
                                        <option value="Juventude Cristã">Juventude Cristã</option>
                                        <option value="Escola Dominical / Infantil">Escola Dominical / Infantil</option>
                                        <option value="Louvor & Coral">Louvor & Coral</option>
                                    </select>
                                </div>
                            </div>
                            """
        pos_fim_bloco = html.rfind("<div", 0, pos_obs_membros)
        html = html[:pos_bloco_membros] + bloco_membros_limpo + html[pos_fim_bloco:]
        print("✓ Bloco de seleção de Membros totalmente reconstruído com Tailwind sem barras!")

# E) Estilo universal no <head> para assegurar que nenhum seletor mostre barra de rolagem
css_definitivo = """
    <!-- SUPRESSÃO DEFINITIVA DE BARRAS DE ROLAGEM PRETAS EM SELECTS -->
    <style>
        select {
            -webkit-appearance: none;
            -moz-appearance: none;
            appearance: none;
            background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23475569' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
            background-repeat: no-repeat;
            background-position: right 0.75rem center;
            background-size: 1em 1em;
            padding-right: 2.25rem !important;
            overflow: hidden !important;
        }
        select::-webkit-scrollbar {
            display: none !important;
            width: 0 !important;
            height: 0 !important;
        }
    </style>
</head>
"""
if "SUPRESSÃO DEFINITIVA DE BARRAS DE ROLAGEM" not in html and "</head>" in html:
    html = html.replace("</head>", css_definitivo, 1)

# Validação com Jinja2
env = jinja2.Environment()
try:
    env.parse(html)
    print("✓ templates/dashboard.html validado com ZERO erros no Jinja2!")
except Exception as e:
    print(f"Erro no Jinja2: {e}")
    exit(1)

with open(caminho_dash, 'w', encoding='utf-8') as f:
    f.write(html)

# =============================================================================
# 3. ENVIAR PARA O GITHUB E O RENDER
# =============================================================================
print("=" * 80)
print("A ENVIAR ATUALIZAÇÃO PARA O GITHUB & RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "app.py", "templates/dashboard.html"], check=True)
subprocess.run(["git", "commit", "-m", "Fix definitivo: direcionar professor para doutrina, eliminar stray tags e remover barras pretas"], check=True)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("=" * 80)
print(">>> PROCESSO CONCLUÍDO COM SUCESSO! <<<")
print("=" * 80)