import os
import re
import py_compile
import subprocess
import jinja2

print("=" * 80)
print("A APLICAR SANEAMENTO DEFINITIVO: DOUTRINA DO PROFESSOR & EXTINÇÃO DE BARRAS...")
print("=" * 80)

caminho_app = 'app.py'
caminho_dash = os.path.join('templates', 'dashboard.html')

# =============================================================================
# 1. BLINDAGEM TOTAL NO APP.PY (IMEDIATAMENTE ANTES DO RENDER_TEMPLATE)
# =============================================================================
with open(caminho_app, 'r', encoding='utf-8') as f:
    app_code = f.read()

# Remover quaisquer travas antigas mal posicionadas
app_code = re.sub(r"# REGRA ESTRITA: Professor[\s\S]*?aba_ativa = 'doutrina'\n", "", app_code)
app_code = re.sub(r"# Trava exclusiva para professores[\s\S]*?aba_ativa = 'doutrina'\n", "", app_code)

# Forçar aba_ativa = 'doutrina' IMEDIATAMENTE ANTES de render_template('dashboard.html'
regra_docente_saida = '''
    # FIX DEFINITIVO: Professor NUNCA recebe dashboard; recebe SEMPRE doutrina
    if usuario and any(c in str(usuario.get('perfil', '')).lower() for c in ['professor', 'docente', 'instrutor']):
        aba_ativa = 'doutrina'
'''

pos_render = app_code.find("return render_template('dashboard.html'")
if pos_render != -1:
    if "FIX DEFINITIVO: Professor NUNCA recebe dashboard" not in app_code:
        app_code = app_code[:pos_render] + regra_docente_saida + "    " + app_code[pos_render:]
        print("✓ Regra do professor inserida exatamente no ponto de saída do render_template!")
else:
    print("Aviso: Chamada a render_template('dashboard.html' não localizada diretamente.")

with open(caminho_app, 'w', encoding='utf-8') as f:
    f.write(app_code)

try:
    py_compile.compile(caminho_app, doraise=True)
    print("✓ app.py validado e compilado com ZERO erros de sintaxe!")
except Exception as e:
    print(f"Erro em app.py: {e}")
    exit(1)

# =============================================================================
# 2. SANEAMENTO CIRÚRGICO EM TEMPLATES/DASHBOARD.HTML
# =============================================================================
with open(caminho_dash, 'r', encoding='utf-8') as f:
    html = f.read()

# A) Limpar qualquer CSS intrusivo que tenha tentado estilar os selects globalmente
html = re.sub(r'<!-- (?:CSS GLOBAL ANTI-BARRA PRETA|SUPRESSÃO DEFINITIVA)[\s\S]*?<\/style>', '', html)

# B) Excluir o campo residual antigo "Categoria de Entrada Local" da Tesouraria
while "Categoria de Entrada Local" in html:
    idx = html.find("Categoria de Entrada Local")
    start_tag = html.rfind("<div", 0, idx)
    # Achar o fechamento dessa div
    end_tag = html.find("</div>", idx)
    if start_tag != -1 and end_tag != -1:
        end_tag += len("</div>")
        html = html[:start_tag] + html[end_tag:]
        print("✓ Bloco residual de 'Categoria de Entrada Local' removido da Tesouraria!")
    else:
        break

# C) Na aba Membros: reconstruir os campos após Estado Civil com tags limpas e fechadas
pos_ec = html.find("Estado Civil *")
if pos_ec != -1:
    pos_grid_start = html.rfind("<div class=\"grid", 0, pos_ec)
    if pos_grid_start == -1:
        pos_grid_start = html.rfind("<div", 0, pos_ec)
    
    # Procurar onde o formulário continua (Observações ou Botão de envio)
    pos_proximo = html.find("Observações", pos_ec)
    if pos_proximo == -1:
        pos_proximo = html.find("name=\"descricao\"", pos_ec)
    if pos_proximo == -1:
        pos_proximo = html.find("<button", pos_ec)
    
    if pos_proximo != -1:
        pos_div_antes_proximo = html.rfind("<div", 0, pos_proximo)
        
        bloco_membros_reconstruido = """<div class="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-3">
                                <div>
                                    <label class="block font-bold text-slate-700 mb-1 text-xs">Estado Civil *</label>
                                    <select name="estado_civil" required class="w-full h-11 px-3 bg-white border border-slate-300 rounded-xl text-xs font-semibold text-slate-800 focus:outline-none shadow-sm">
                                        <option value="Solteiro(a)">Solteiro(a)</option>
                                        <option value="Casado(a)" selected>Casado(a)</option>
                                        <option value="Viúvo(a)">Viúvo(a)</option>
                                        <option value="Divorciado(a)">Divorciado(a)</option>
                                    </select>
                                </div>
                                <div>
                                    <label class="block font-bold text-slate-700 mb-1 text-xs">Zona Territorial</label>
                                    <select name="zona" class="w-full h-11 px-3 bg-white border border-slate-300 rounded-xl text-xs font-semibold text-slate-800 focus:outline-none shadow-sm">
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
                                    <select name="celula" class="w-full h-11 px-3 bg-white border border-slate-300 rounded-xl text-xs font-semibold text-slate-800 focus:outline-none shadow-sm">
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
                                    <select name="baptizado" required class="w-full h-11 px-3 bg-white border border-slate-300 rounded-xl text-xs font-semibold text-slate-800 focus:outline-none shadow-sm">
                                        <option value="Sim">Baptizado nas Águas (Comunhão)</option>
                                        <option value="Não">Não Baptizado (Em Doutrina / Novo)</option>
                                    </select>
                                </div>
                                <div>
                                    <label class="block font-bold text-slate-700 mb-1 text-xs">Ministério / Departamento</label>
                                    <select name="departamento" class="w-full h-11 px-3 bg-white border border-slate-300 rounded-xl text-xs font-semibold text-slate-800 focus:outline-none shadow-sm">
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
        html = html[:pos_grid_start] + bloco_membros_reconstruido + html[pos_div_antes_proximo:]
        print("✓ Formulário de Membros reconstruído de forma estruturada e sem erros de fechamento!")

# D) Limpar classes de overflow em qualquer tag select restante no documento
def desinfectar_selects(doc):
    def sub_sel(m):
        tag = m.group(0)
        tag = re.sub(r'\boverflow(-x)?-(auto|scroll)\b', '', tag)
        tag = re.sub(r'class="([^"]*)"', lambda x: f'class="{" ".join(x.group(1).split())}"', tag)
        return tag
    return re.sub(r'<select[^>]*>', sub_sel, doc)

html = desinfectar_selects(html)

# E) Blindagem no Jinja2: garantir que o Raio-X só é processado se NÃO for professor
if "{% if aba_ativa == 'dashboard'" in html:
    html = re.sub(
        r"{% if aba_ativa == 'dashboard'[^%]*%}",
        "{% if aba_ativa == 'dashboard' and not (usuario_logado and ('professor' in usuario_logado.perfil|lower or 'docente' in usuario_logado.perfil|lower)) %}",
        html
    )
    print("✓ Condição Jinja2 do Raio-X blindada!")

# Validação estrita da árvore de tags Jinja2
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
print("A ENVIAR ATUALIZAÇÃO DEFINITIVA PARA O GITHUB & RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "app.py", "templates/dashboard.html"], check=True)
subprocess.run(["git", "commit", "-m", "Saneamento definitivo: forcar doutrina para professor no render_template e recompor campos de membros e tesouraria"], check=True)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("=" * 80)
print(">>> PROCESSO CONCLUÍDO COM SUCESSO! <<<")
print("=" * 80)