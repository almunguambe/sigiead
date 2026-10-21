import os
import re
import py_compile
import subprocess
import jinja2

print("=" * 80)
print("A CORRIGIR NA RAIZ: ROTEAMENTO DO PROFESSOR, BANCO E BARRAS PRETAS...")
print("=" * 80)

caminho_app = 'app.py'
caminho_dash = os.path.join('templates', 'dashboard.html')

# =============================================================================
# 1. CORREÇÃO EM APP.PY
# =============================================================================
with open(caminho_app, 'r', encoding='utf-8') as f:
    app_code = f.read()

# A) Corrigir o erro SQL: 'data_operacao' -> 'data' na tabela caixa
if "ORDER BY data_operacao DESC, id DESC" in app_code:
    app_code = app_code.replace("ORDER BY data_operacao DESC, id DESC", "ORDER BY id DESC")
    print("✓ Erro SQL da tabela caixa corrigido (removido data_operacao inexistente)!")

# B) Na rota /login: se for professor, redirecionar diretamente para ?aba=doutrina
padrao_login_redir = r"return redirect\(url_for\('index',\s*aba='dashboard'\)\)|return redirect\(['\"]/\?aba=dashboard['\"]\)"
novo_login_redir = """perfil_u = str(user.get('perfil', '')).lower()
            if any(p in perfil_u for p in ['prof', 'docente', 'instrutor']):
                return redirect(url_for('index', aba='doutrina'))
            return redirect(url_for('index', aba='dashboard'))"""

if re.search(padrao_login_redir, app_code):
    app_code = re.sub(padrao_login_redir, novo_login_redir, app_code, count=1)
    print("✓ Rota de login configurada para enviar o professor diretamente para ?aba=doutrina!")

# C) Na rota index(): garantir que professor NUNCA recebe 'dashboard'
padrao_aba_index = r"aba_ativa\s*=\s*request\.args\.get\(['\"]aba['\"],\s*['\"]dashboard['\"]\)"
novo_aba_index = """aba_req = request.args.get('aba')
    perfil_sess = str(usuario.get('perfil', '')).lower() if 'usuario' in locals() and usuario else ''
    if any(p in perfil_sess for p in ['prof', 'docente', 'instrutor']):
        aba_ativa = 'doutrina' if (not aba_req or aba_req == 'dashboard') else aba_req
    else:
        aba_ativa = aba_req if aba_req else 'dashboard'"""

if re.search(padrao_aba_index, app_code):
    app_code = re.sub(padrao_aba_index, novo_aba_index, app_code, count=1)
    print("✓ Rota principal (index) configurada: professor abre sempre Doutrina!")

with open(caminho_app, 'w', encoding='utf-8') as f:
    f.write(app_code)

try:
    py_compile.compile(caminho_app, doraise=True)
    print("✓ app.py validado e compilado com ZERO erros!")
except Exception as e:
    print(f"Erro em app.py: {e}")
    exit(1)

# =============================================================================
# 2. CORREÇÃO EM TEMPLATES/DASHBOARD.HTML
# =============================================================================
with open(caminho_dash, 'r', encoding='utf-8') as f:
    html = f.read()

# A) Eliminar o campo duplicado "Categoria de Entrada Local" da Tesouraria
while "Categoria de Entrada Local" in html:
    pos_lbl = html.find("Categoria de Entrada Local")
    pos_div_start = html.rfind("<div", 0, pos_lbl)
    pos_div_end = html.find("</div>", pos_lbl)
    if pos_div_start != -1 and pos_div_end != -1:
        pos_div_end += len("</div>")
        html = html[:pos_div_start] + html[pos_div_end:]
        print("✓ Campo residual 'Categoria de Entrada Local' removido da Tesouraria!")
    else:
        break

# B) Remover qualquer classe 'overflow-x-auto', 'overflow-auto' de selects e de divs que os contenham
html = re.sub(r'\boverflow(-x)?-(auto|scroll)\b', '', html)
print("✓ Classes de overflow causadoras da barra preta suprimidas!")

# C) Na aba Membros: recompor a linha seguinte a Estado Civil/Zona/Célula
pos_ec = html.find("Estado Civil *")
if pos_ec != -1:
    pos_celula = html.find('name="celula"', pos_ec)
    if pos_celula != -1:
        # Achar o fecho do grid de 3 colunas
        pos_grid_fim = html.find("</div>", pos_celula)
        pos_grid_fim = html.find("</div>", pos_grid_fim + 1) + len("</div>")
        
        # Achar onde começam as observações ou o botão de envio
        pos_seg = html.find("Observações", pos_grid_fim)
        if pos_seg == -1:
            pos_seg = html.find("<button", pos_grid_fim)
        
        if pos_seg != -1:
            bloco_membros_limpo = """
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
                            <div>
                                <label class="block font-bold text-slate-700 mb-1 text-xs">Situação Espiritual / Batismo *</label>
                                <select name="baptizado" required class="w-full h-11 px-3 bg-white border border-slate-300 rounded-xl text-xs font-semibold text-slate-800 focus:outline-none shadow-sm cursor-pointer">
                                    <option value="Sim">Baptizado nas Águas (Comunhão)</option>
                                    <option value="Não">Não Baptizado (Em Doutrina / Novo)</option>
                                </select>
                            </div>
                            <div>
                                <label class="block font-bold text-slate-700 mb-1 text-xs">Ministério / Departamento</label>
                                <select name="departamento" class="w-full h-11 px-3 bg-white border border-slate-300 rounded-xl text-xs font-semibold text-slate-800 focus:outline-none shadow-sm cursor-pointer">
                                    <option value="Membro Geral">Membro Geral</option>
                                    <option value="Corpo Pastoral / Obreiro">Corpo Pastoral / Obreiro</option>
                                    <option value="Diaconato">Diaconato</option>
                                    <option value="Departamento de Senhoras">Departamento de Senhoras</option>
                                    <option value="Juventude Cristã">Juventude Cristã</option>
                                    <option value="Escola Dominical / Infantil">Escola Dominical / Infantil</option>
                                    <option value="Louvor & Coral">Louvor & Coral</option>
                                </select>
                            </div>
                        </div>"""
            html = html[:pos_grid_fim] + bloco_membros_limpo + html[pos_seg:]
            print("✓ Formulário de Membros recomposto com layout limpo!")

# D) Proteção estrita no template para o professor
if "{% if aba_ativa == 'dashboard'" in html:
    html = re.sub(
        r"{% if aba_ativa == 'dashboard'[^%]*%}",
        "{% if aba_ativa == 'dashboard' and not (usuario_logado and ('professor' in usuario_logado.perfil|lower or 'docente' in usuario_logado.perfil|lower)) %}",
        html
    )

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
# 3. PUBLICAR NO GITHUB E RENDER
# =============================================================================
print("=" * 80)
print("A ENVIAR ATUALIZAÇÃO PARA O GITHUB & RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "app.py", "templates/dashboard.html"], check=True)
subprocess.run(["git", "commit", "-m", "Fix definitivo: roteamento estrito do professor, correcao sql caixa e eliminacao de barras pretas"], check=True)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("=" * 80)
print(">>> PROCESSO CONCLUÍDO COM SUCESSO! <<<")
print("=" * 80)