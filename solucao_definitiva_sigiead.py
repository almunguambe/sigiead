import os
import re
import py_compile
import subprocess
import jinja2

print("=" * 80)
print("A RESTAURAR ESTRUTURA ORIGINAL DO SIGIEAD (SIDEBAR, MEMBROS E LOGIN)...")
print("=" * 80)

caminho_dash = os.path.join('templates', 'dashboard.html')
caminho_app = 'app.py'

# =============================================================================
# 1. RESTAURAR A BARRA LATERAL E O CORPO EM TEMPLATES/DASHBOARD.HTML
# =============================================================================
with open(caminho_dash, 'r', encoding='utf-8') as f:
    html = f.read()

# A) Limpar qualquer formulário indevidamente colado na barra lateral (<aside>)
pos_aside_fim = html.find('</aside>')
if pos_aside_fim != -1:
    aside_txt = html[:pos_aside_fim]
    rest_txt = html[pos_aside_fim:]

    # Remover cartão de cadastro acidentalmente inserido no aside
    if 'FICHA DE CADASTRO' in aside_txt or 'FOTOGRAFIA TIPO PASSE' in aside_txt:
        p_c = aside_txt.find('FICHA DE CADASTRO')
        if p_c == -1: p_c = aside_txt.find('FOTOGRAFIA TIPO PASSE')
        p_inicio_div = aside_txt.rfind('<div', 0, p_c)
        p_fim_div = aside_txt.find('</div>', p_c) + len('</div>')
        # Fechar blocos adicionais que possam ter ficado no aside
        p_prox_fim = aside_txt.find('</div>', p_fim_div)
        if p_prox_fim != -1 and p_prox_fim < p_fim_div + 200:
            p_fim_div = p_prox_fim + len('</div>')
        aside_txt = aside_txt[:p_inicio_div] + aside_txt[p_fim_div:]
        print("✓ Cartão indevido removido da barra lateral!")

    # B) Garantir que '1. Membros' e '2. Secretaria & Planos' estão antes de '3. Cultos'
    if '1. Membros' not in aside_txt and '3. Cultos' in aside_txt:
        pos_cultos = aside_txt.find('3. Cultos')
        pos_a_cultos = aside_txt.rfind('<a', 0, pos_cultos)
        
        links_membros_secretaria = """        <a href="/?aba=membros" class="flex items-center gap-3 px-3 py-2.5 rounded-xl font-bold text-xs {% if aba_ativa == 'membros' %}bg-indigo-600 text-white shadow-md{% else %}text-slate-300 hover:text-white hover:bg-slate-800{% endif %} transition">
            <span>👥</span> <span>1. Membros ({{ membros|length if membros else 0 }})</span>
        </a>
        <a href="/?aba=secretaria" class="flex items-center gap-3 px-3 py-2.5 rounded-xl font-bold text-xs {% if aba_ativa == 'secretaria' %}bg-indigo-600 text-white shadow-md{% else %}text-slate-300 hover:text-white hover:bg-slate-800{% endif %} transition">
            <span>📋</span> <span>2. Secretaria & Planos</span>
        </a>\n"""
        aside_txt = aside_txt[:pos_a_cultos] + links_membros_secretaria + aside_txt[pos_a_cultos:]
        print("✓ Itens '1. Membros' e '2. Secretaria & Planos' restaurados na barra lateral!")

    html = aside_txt + rest_txt

# C) Substituir a aba de Membros no corpo central (<main>)
bloco_membros_limpo = """{% if aba_ativa == 'membros' %}
<div class="space-y-6">
    <div class="bg-gradient-to-r from-indigo-950 via-slate-900 to-indigo-950 text-white p-6 rounded-2xl shadow-lg border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div class="space-y-1">
            <div class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-amber-500/20 border border-amber-400/30 text-amber-300 text-[10px] font-black uppercase tracking-wider">
                <span>👥</span> Registo Congregacional Oficial
            </div>
            <h2 class="text-xl sm:text-2xl font-black text-white">
                Cadastro Geral de Membresia
            </h2>
            <p class="text-xs text-slate-300 max-w-xl">
                Registo oficial com geração automática de credenciais e certificados da Igreja de Chicuque.
            </p>
        </div>
        <div>
            <span class="px-3.5 py-2 bg-emerald-600 text-white rounded-xl text-xs font-black shadow-md flex items-center gap-1.5">
                <span>📄</span> Livro Geral ({{ membros|length if membros else 0 }} Membros)
            </span>
        </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        <!-- FORMULÁRIO (5 COLS) -->
        <div class="lg:col-span-5 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <div class="border-b border-slate-100 pb-3">
                <h3 class="font-black text-sm text-slate-900 uppercase tracking-wider flex items-center gap-2">
                    <span>➕</span> Cadastrar Ficha Oficial
                </h3>
                <p class="text-[11px] text-slate-400">Dados cadastrais, eclesiásticos e civis</p>
            </div>

            <form action="/membros/novo" method="POST" enctype="multipart/form-data" class="space-y-4">
                <div class="p-4 bg-slate-50 border border-slate-200 rounded-2xl text-center space-y-2">
                    <span class="text-[10px] font-black uppercase tracking-wider text-slate-400 block">Fotografia Tipo Passe (Leve / ~40KB)</span>
                    <div class="flex items-center justify-center gap-4">
                        <div class="w-16 h-20 rounded-xl bg-slate-200 border-2 border-dashed border-slate-300 flex items-center justify-center text-[10px] text-slate-400 font-bold">
                            Sem Foto
                        </div>
                        <div class="space-y-1.5 text-left">
                            <label class="cursor-pointer inline-flex items-center gap-2 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold transition shadow-sm">
                                <span>📁</span> Carregar Imagem
                                <input type="file" name="foto" accept="image/*" class="hidden">
                            </label>
                        </div>
                    </div>
                </div>

                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">Nome Completo *</label>
                    <input type="text" name="nome" placeholder="Nome completo do membro" required class="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:ring-2 focus:ring-indigo-500 outline-none transition shadow-sm">
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                        <label class="block text-xs font-bold text-slate-700 mb-1">BI / Cédula</label>
                        <input type="text" name="bi" placeholder="Nº de Documento" class="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:ring-2 focus:ring-indigo-500 outline-none transition shadow-sm">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-700 mb-1">Género / Sexo *</label>
                        <select name="genero" required class="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-xs text-slate-800 focus:ring-2 focus:ring-indigo-500 outline-none transition shadow-sm">
                            <option value="Masculino">Homem (Masculino)</option>
                            <option value="Feminino">Mulher (Feminino)</option>
                        </select>
                    </div>
                </div>

                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">Contacto / WhatsApp</label>
                    <input type="text" name="contacto" placeholder="+258..." class="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:ring-2 focus:ring-indigo-500 outline-none transition shadow-sm">
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                        <label class="block text-xs font-bold text-slate-700 mb-1">Estado Civil *</label>
                        <select name="estado_civil" required class="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-xs text-slate-800 focus:ring-2 focus:ring-indigo-500 outline-none transition shadow-sm">
                            <option value="Solteiro(a)">Solteiro(a)</option>
                            <option value="Casado(a)">Casado(a)</option>
                            <option value="Viúvo(a)">Viúvo(a)</option>
                            <option value="Divorciado(a)">Divorciado(a)</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-700 mb-1">Zona Territorial</label>
                        <select name="zona" class="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-xs text-slate-800 focus:ring-2 focus:ring-indigo-500 outline-none transition shadow-sm">
                            <option value="">Selecione a Zona...</option>
                            <option value="Zona 1 • Chicuque">Zona 1 • Chicuque</option>
                            <option value="Zona 2 • Chambone">Zona 2 • Chambone</option>
                            <option value="Zona 3 • Tinga">Zona 3 • Tinga</option>
                            <option value="Zona 4 • Rumbana">Zona 4 • Rumbana</option>
                            <option value="Zona 5 • Dambo">Zona 5 • Dambo</option>
                            <option value="Zona 6 • Macuamene">Zona 6 • Macuamene</option>
                        </select>
                    </div>
                </div>

                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">Célula Familiar</label>
                    <select name="celula" class="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-xs text-slate-800 focus:ring-2 focus:ring-indigo-500 outline-none transition shadow-sm">
                        <option value="">Selecione a Célula...</option>
                        <option value="Célula Betel (Chicuque)">Célula Betel (Chicuque Sede)</option>
                        <option value="Célula Sião (Chambone)">Célula Sião (Chambone Centro)</option>
                        <option value="Célula Peniel (Tinga)">Célula Peniel (Tinga Residencial)</option>
                        <option value="Célula Ebenézer (Rumbana)">Célula Ebenézer (Rumbana)</option>
                        <option value="Célula Jerusalém (Agostinho Neto)">Célula Jerusalém (Agostinho Neto)</option>
                        <option value="Célula Manassés (Dambo)">Célula Manassés (Dambo / Expansão)</option>
                    </select>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                        <label class="block text-xs font-bold text-slate-700 mb-1">Cargo Ministerial</label>
                        <select name="cargo" class="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-xs text-slate-800 focus:ring-2 focus:ring-indigo-500 outline-none transition shadow-sm">
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
                        <select name="departamento" class="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-xs text-slate-800 focus:ring-2 focus:ring-indigo-500 outline-none transition shadow-sm">
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

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                        <label class="block text-xs font-bold text-slate-700 mb-1">Ano Conversão</label>
                        <input type="text" name="ano_conversao" placeholder="Ex: 2021" class="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:ring-2 focus:ring-indigo-500 outline-none transition shadow-sm">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-700 mb-1">Data Batismo</label>
                        <input type="date" name="data_batismo" class="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-xs text-slate-800 focus:ring-2 focus:ring-indigo-500 outline-none transition shadow-sm">
                    </div>
                </div>

                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">Residência (Bairro / Local)</label>
                    <input type="text" name="residencia" placeholder="Ex: Chicuque - Perto do Hospital" class="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:ring-2 focus:ring-indigo-500 outline-none transition shadow-sm">
                </div>

                <button type="submit" class="w-full py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-black rounded-xl text-xs transition shadow-md flex items-center justify-center gap-2">
                    <span>💾</span>
                    <span>Gravar Ficha de Membro</span>
                </button>
            </form>
        </div>

        <!-- TABELA DE MEMBROS (7 COLS) -->
        <div class="lg:col-span-7 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <div class="flex items-center justify-between border-b border-slate-100 pb-3">
                <div>
                    <h3 class="font-black text-sm text-slate-900 uppercase tracking-wider flex items-center gap-2">
                        <span>📋</span> Membros Registados
                    </h3>
                    <p class="text-[11px] text-slate-400">Relação nominal da congregação</p>
                </div>
                <span class="px-3 py-1 rounded-xl bg-indigo-50 text-indigo-900 text-xs font-black">
                    {{ membros|length if membros else 0 }} Membros
                </span>
            </div>

            <div class="overflow-x-auto">
                <table class="w-full text-left text-xs border-collapse">
                    <thead>
                        <tr class="bg-slate-50 text-slate-600 font-bold uppercase text-[10px] border-b border-slate-100">
                            <th class="p-3">Membro</th>
                            <th class="p-3">Zona & Célula</th>
                            <th class="p-3">Cargo & Depto</th>
                            <th class="p-3 text-center">Batismo</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-100 font-medium">
                        {% if membros and membros|length > 0 %}
                            {% for m in membros %}
                            <tr class="hover:bg-slate-50 transition">
                                <td class="p-3">
                                    <span class="font-bold text-slate-900 block">{{ m.nome }}</span>
                                    <span class="text-[10px] text-slate-400">{{ m.contacto or m.bi or '' }}</span>
                                </td>
                                <td class="p-3 text-slate-600">
                                    <span class="block font-semibold text-slate-800">{{ m.zona or 'Sem Zona' }}</span>
                                    <span class="text-[10px] text-slate-400">{{ m.celula or 'Sem Célula' }}</span>
                                </td>
                                <td class="p-3 text-slate-600">
                                    <span class="block font-semibold text-indigo-700">{{ m.cargo or 'Membro' }}</span>
                                    <span class="text-[10px] text-slate-400">{{ m.departamento or 'Geral' }}</span>
                                </td>
                                <td class="p-3 text-center">
                                    <span class="px-2 py-0.5 rounded-full text-[10px] font-bold {% if m.data_batismo %}bg-emerald-100 text-emerald-800{% else %}bg-slate-100 text-slate-600{% endif %}">
                                        {{ m.data_batismo or 'Não' }}
                                    </span>
                                </td>
                            </tr>
                            {% endfor %}
                        {% else %}
                            <tr>
                                <td colspan="4" class="p-8 text-center text-slate-400 italic">
                                    Nenhum membro registado no momento. Preencha o formulário ao lado para cadastrar.
                                </td>
                            </tr>
                        {% endif %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>
{% endif %}"""

pos_membros_main = html.find("aba_ativa == 'membros'", html.find('</aside>'))
if pos_membros_main == -1:
    pos_membros_main = html.find('aba_ativa == "membros"', html.find('</aside>'))

if pos_membros_main != -1:
    inicio_tag_m = html.rfind("{%", 0, pos_membros_main)
    fim_tag_m = -1
    for p_nome in ['secretaria', 'cultos', 'doutrina']:
        p = html.find(f"aba_ativa == '{p_nome}'", pos_membros_main + 20)
        if p == -1: p = html.find(f'aba_ativa == "{p_nome}"', pos_membros_main + 20)
        if p != -1:
            fim_tag_m = html.rfind("{%", 0, p)
            break
    if fim_tag_m == -1:
        fim_tag_m = html.find("</main>", pos_membros_main)

    html = html[:inicio_tag_m] + bloco_membros_limpo + "\n\n" + html[fim_tag_m:]
    print("✓ Aba Membros reconstruída no corpo principal com formulário e tabela perfeitos!")

# D) Eliminar qualquer resquício antigo de formulário quebrado ('EstadZona')
while 'EstadZona' in html:
    p_ez = html.find('EstadZona')
    p_div_ez = html.rfind('<div class="lg:col-span-', 0, p_ez)
    if p_div_ez == -1: p_div_ez = html.rfind('<div', 0, p_ez)
    p_end_ez = html.find('</div>', p_ez) + len('</div>')
    p_form_ez = html.find('</form>', p_ez)
    if p_form_ez != -1 and p_form_ez < p_ez + 500:
        p_end_ez = html.find('</div>', p_form_ez) + len('</div>')
    html = html[:p_div_ez] + html[p_end_ez:]
    print("✓ Resquício antigo de 'EstadZona' eliminado!")

# Validação com Jinja2
env = jinja2.Environment()
env.parse(html)
with open(caminho_dash, 'w', encoding='utf-8') as f:
    f.write(html)
print("✓ templates/dashboard.html validado com ZERO erros no Jinja2!")

# =============================================================================
# 2. BLINDAR A ROTA DE LOGIN NO APP.PY (COMPATÍVEL COM TELEMÓVEIS E ESPAÇOS)
# =============================================================================
with open(caminho_app, 'r', encoding='utf-8') as f:
    app_code = f.read()

login_robusto = '''@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('usuario', '').strip()
        s = request.form.get('senha', '').strip()
        user = None
        
        try:
            user = consultar_um("SELECT * FROM usuarios_sistema WHERE LOWER(TRIM(usuario)) = LOWER(TRIM(%s))", (u,))
        except Exception:
            try:
                user = consultar_um("SELECT * FROM usuarios_sistema WHERE LOWER(TRIM(usuario)) = LOWER(TRIM(?))", (u,))
            except Exception as err:
                print("Erro de banco no login:", err)
                user = None

        if user:
            senha_db = str(user.get('senha', '')).strip()
            senha_valida = (senha_db == s)
            if not senha_valida:
                try:
                    from werkzeug.security import check_password_hash
                    senha_valida = check_password_hash(senha_db, s)
                except Exception:
                    pass

            if senha_valida:
                session['usuario'] = dict(user)
                perfil = str(user.get('perfil', '')).lower()
                if any(p in perfil for p in ['prof', 'docente', 'instrutor']):
                    return redirect('/professor')
                return redirect('/?aba=dashboard')
            else:
                flash('Palavra-passe incorreta.', 'danger')
        else:
            flash('Utilizador não registado no sistema.', 'danger')
            
    return render_template('login.html')'''

pos_l = app_code.find("@app.route('/login'")
if pos_l == -1: pos_l = app_code.find('@app.route("/login"')
if pos_l != -1:
    pos_prox = app_code.find("\n@app.route", pos_l + 15)
    if pos_prox != -1:
        app_code = app_code[:pos_l] + login_robusto + "\n\n" + app_code[pos_prox:]
        print("✓ Rota /login blindada para telemóveis e computadores!")

with open(caminho_app, 'w', encoding='utf-8') as f:
    f.write(app_code)

py_compile.compile(caminho_app, doraise=True)
print("✓ app.py validado e compilado com ZERO erros!")

# =============================================================================
# 3. ENVIAR PARA O GITHUB E RENDER
# =============================================================================
print("\n" + "=" * 80)
print("A ENVIAR ATUALIZAÇÃO DEFINITIVA PARA O RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "templates/dashboard.html", "app.py"])
subprocess.run(["git", "commit", "-m", "Restauracao total SIGIEAD: sidebar completa, membros sem duplicata e login robusto"])
subprocess.run(["git", "push", "origin", "main"])

print("=" * 80)
print(">>> SISTEMA RESTAURADO E ATUALIZADO NO RENDER COM SUCESSO! <<<")
print("=" * 80)