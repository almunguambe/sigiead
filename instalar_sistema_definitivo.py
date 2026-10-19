import os
import re
import jinja2

print("=" * 80)
print("A CONFIGURAR GESTÃO DE UTILIZADORES, SUPABASE E RESTAURAÇÃO TOTAL...")
print("=" * 80)

os.makedirs('templates', exist_ok=True)
env = jinja2.Environment()

# =============================================================================
# 1. LOGÓTIPO OFICIAL DA ASSEMBLEIA DE DEUS EM MOÇAMBIQUE (VETORIAL HD)
# =============================================================================
logo_svg = """<div class="inline-flex items-center justify-center select-none">
    <svg viewBox="0 0 450 450" class="w-full h-full max-w-[160px] max-h-[160px] drop-shadow-md" xmlns="http://www.w3.org/2000/svg">
        <circle cx="225" cy="225" r="215" fill="#ffffff" stroke="#0044cc" stroke-width="4"/>
        <path id="textArc" d="M 50,225 A 175,175 0 1,1 400,225" fill="none"/>
        <text font-family="Arial, Helvetica, sans-serif" font-size="21" font-weight="900" fill="#000000" letter-spacing="1.5">
            <textPath href="#textArc" startOffset="50%" text-anchor="middle">
                IGREJA EVANGÉLICA ASSEMBLEIA DE DEUS
            </textPath>
        </text>
        <path d="M 235,120 C 260,115 315,115 320,135 C 325,160 325,185 300,195 C 275,205 260,230 250,265 C 240,290 255,340 240,365 C 230,380 205,385 190,370 C 175,355 195,315 210,290 C 225,265 220,240 200,215 C 180,190 215,160 220,135 Z" fill="#ff4d22" stroke="#d6340c" stroke-width="2"/>
        <rect x="233" y="90" width="14" height="270" fill="#0044cc"/>
        <rect x="180" y="140" width="120" height="14" fill="#0044cc"/>
        <path d="M 120,310 L 165,150 L 195,150 L 235,310 L 195,310 L 183,260 L 145,260 L 138,310 Z M 152,225 L 176,225 L 164,175 Z" fill="#0044cc"/>
        <path d="M 235,310 L 255,310 L 255,285 C 245,275 235,255 235,230 C 235,185 265,160 305,160 C 345,160 375,185 375,230 C 375,255 365,275 355,285 L 355,310 L 375,310 L 375,325 L 325,325 L 325,310 L 335,310 C 345,300 350,285 350,230 C 350,198 332,180 305,180 C 278,180 260,198 260,230 C 260,285 265,300 275,310 L 285,310 L 285,325 L 235,325 Z" fill="#0044cc"/>
    </svg>
</div>"""
with open('templates/logo_ad.html', 'w', encoding='utf-8') as f:
    f.write(logo_svg)

# =============================================================================
# 2. PORTA DE ENTRADA ESPECTACULAR (TEMPLATES/LOGIN.HTML)
# =============================================================================
login_html = """<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portal Oficial - Assembleia de Deus em Moçambique</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .celestial-bg { background: radial-gradient(circle at 50% 0%, #1e1b4b 0%, #0f172a 50%, #020617 100%); }
    </style>
</head>
<body class="celestial-bg min-h-screen flex items-center justify-center p-4 font-sans text-slate-800">

    <div class="max-w-4xl w-full grid grid-cols-1 md:grid-cols-12 bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl overflow-hidden border border-amber-500/30">

        <!-- LADO ESQUERDO: BOAS-VINDAS -->
        <div class="md:col-span-5 bg-gradient-to-br from-indigo-950 via-slate-900 to-slate-950 p-8 text-white flex flex-col justify-between border-r border-indigo-900/40">
            <div class="space-y-4">
                <div class="w-24 h-24 bg-white rounded-3xl p-2 shadow-2xl flex items-center justify-center border-2 border-amber-400 mx-auto md:mx-0">
                    {% include 'logo_ad.html' %}
                </div>
                <div>
                    <span id="saudacao_tempo" class="bg-amber-400/20 text-amber-300 border border-amber-400/40 text-[9px] font-black uppercase px-2.5 py-0.5 rounded-full inline-block mb-1">
                        Paz do Senhor Jesus
                    </span>
                    <h1 class="text-xl font-black uppercase tracking-wide leading-tight">ASSEMBLEIA DE DEUS</h1>
                    <p class="text-[11px] text-blue-300 font-bold mt-0.5">República de Moçambique</p>
                </div>
                <div class="bg-white/5 border border-white/10 p-3.5 rounded-2xl text-xs space-y-1.5 text-indigo-100">
                    <p class="font-extrabold text-amber-300 flex items-center gap-1.5 text-[11px]">
                        <span>🕊️</span> Bem-vindo à Casa do Senhor!
                    </p>
                    <p class="leading-relaxed text-[11px] text-slate-200 text-justify">
                        Plataforma integrada de gestão ministerial, membresia e formação teológica. O acesso é direcionado estritamente à sua área de ministério.
                    </p>
                </div>
            </div>
            <div class="pt-4 border-t border-white/10 text-[10px] italic text-indigo-200 text-center font-serif">
                "Alegrei-me quando me disseram: Vamos à casa do Senhor!" (Salmo 122:1)
            </div>
        </div>

        <!-- LADO DIREITO: FORMULÁRIO COM ATALHOS -->
        <div class="md:col-span-7 p-8 sm:p-10 flex flex-col justify-between space-y-5">
            <div class="space-y-1">
                <h2 class="text-2xl font-black text-slate-900">Acesso ao Sistema</h2>
                <p class="text-xs text-slate-500">Introduza as suas credenciais para entrar na sua área.</p>
            </div>

            {% if erro %}
            <div class="p-3 bg-rose-50 border-2 border-rose-300 rounded-xl text-rose-800 text-xs font-bold text-center">
                {{ erro }}
            </div>
            {% endif %}

            <form action="/login" method="POST" class="space-y-3.5 text-xs">
                <div>
                    <label class="block font-bold text-slate-700 mb-1">Utilizador *</label>
                    <input type="text" id="campo_usuario" name="usuario" required placeholder="Digite o seu utilizador" class="w-full h-11 px-3 border-2 border-slate-200 rounded-xl bg-slate-50 focus:bg-white focus:border-indigo-600 focus:outline-none font-bold">
                </div>

                <div>
                    <label class="block font-bold text-slate-700 mb-1">Palavra-passe *</label>
                    <input type="password" id="campo_senha" name="senha" required placeholder="••••••••" class="w-full h-11 px-3 border-2 border-slate-200 rounded-xl bg-slate-50 focus:bg-white focus:border-indigo-600 focus:outline-none font-bold">
                </div>

                <button type="submit" class="w-full py-3.5 bg-indigo-900 hover:bg-indigo-950 text-white font-black rounded-xl shadow cursor-pointer text-sm transition">
                    Entrar no Meu Perfil →
                </button>
            </form>

            <div class="space-y-2 pt-2 border-t border-slate-200">
                <span class="text-[10px] uppercase font-bold text-slate-400 block tracking-wider">Atalhos de Acesso Rápido:</span>
                <div class="grid grid-cols-2 gap-2 text-[10px]">
                    <button type="button" onclick="preencherLogin('secretaria', 'sec123')" class="p-2 bg-blue-50/60 hover:bg-blue-100 border border-blue-200 rounded-xl text-left transition">
                        <span class="font-black text-blue-950 block">📋 Secretariado</span>
                        <span class="text-[9px] text-blue-700">Membros, Cultos e Actos</span>
                    </button>
                    <button type="button" onclick="preencherLogin('tesouraria', 'tesouro123')" class="p-2 bg-amber-50/60 hover:bg-amber-100 border border-amber-200 rounded-xl text-left transition">
                        <span class="font-black text-amber-950 block">🔐 Tesoureira</span>
                        <span class="text-[9px] text-amber-700">Entra direto no Caixa</span>
                    </button>
                    <button type="button" onclick="preencherLogin('pastor', 'pastor123')" class="p-2 bg-slate-50 hover:bg-indigo-50 border rounded-xl text-left transition">
                        <span class="font-black text-indigo-950 block">⛪ Liderança / Pastor</span>
                        <span class="text-[9px] text-slate-500">Audita finanças e vê censo</span>
                    </button>
                    <button type="button" onclick="preencherLogin('anselmo', '123456')" class="p-2 bg-emerald-50/60 hover:bg-emerald-100 border border-emerald-200 rounded-xl text-left transition">
                        <span class="font-black text-emerald-950 block">🎓 Aluno / Formando</span>
                        <span class="text-[9px] text-emerald-700">Vai direto para a Aula</span>
                    </button>
                </div>
            </div>
        </div>

    </div>

    <script>
        var h = new Date().getHours();
        var s = "Paz do Senhor • Bom dia";
        if (h >= 12 && h < 18) s = "Paz do Senhor • Boa tarde";
        else if (h >= 18 || h < 5) s = "Paz do Senhor • Boa noite";
        var el = document.getElementById('saudacao_tempo');
        if (el) el.innerText = s;

        function preencherLogin(u, pwd) {
            document.getElementById('campo_usuario').value = u;
            document.getElementById('campo_senha').value = pwd;
        }
    </script>
</body>
</html>
"""
env.parse(login_html)
with open('templates/login.html', 'w', encoding='utf-8') as f:
    f.write(login_html)
print("✓ templates/login.html: Porta de entrada espetacular criada!")

# =============================================================================
# 3. ATUALIZAR APP.PY COM TODAS_LICOES, /logout E SUPABASE COMPATIBILITY
# =============================================================================
with open('app.py', 'r', encoding='utf-8') as f:
    app_text = f.read()

# 1. Garantir /logout e /ensino/logout no app.py
if "@app.route('/logout')" not in app_text:
    rotas_logout = """
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/ensino/logout')
def aluno_logout():
    session.clear()
    return redirect('/login')
"""
    app_text = rotas_logout + "\n" + app_text

# 2. Garantir rotas do Admin para criar utilizadores e recuperar senhas
rotas_admin_senhas = """
@app.route('/admin/usuarios/novo', methods=['POST'])
def admin_usuario_novo():
    if session.get('usuario_perfil') != 'admin':
        return redirect('/login')
    fd = request.form
    nome, usuario, senha, perfil = fd.get('nome', '').strip(), fd.get('usuario', '').strip().lower(), fd.get('senha', '123456').strip(), fd.get('perfil', 'secretario').strip()
    if nome and usuario and senha:
        existente = consultar_um("SELECT id FROM usuarios_sistema WHERE LOWER(usuario) = ?", (usuario,))
        if existente:
            return "<script>alert('Este utilizador já existe!'); window.history.back();</script>"
        executar_comando("INSERT INTO usuarios_sistema (nome, usuario, senha, nivel, perfil, criado_em) VALUES (?, ?, ?, ?, ?, ?)",
                         (nome, usuario, senha, perfil, perfil, datetime.now().strftime('%Y-%m-%d %H:%M')))
    return redirect('/?aba=configuracoes')

@app.route('/admin/usuarios/redefinir_senha', methods=['POST'])
def admin_usuario_redefinir_senha():
    if session.get('usuario_perfil') != 'admin':
        return redirect('/login')
    uid, nova = request.form.get('usuario_id'), request.form.get('nova_senha', '').strip()
    if uid and nova:
        executar_comando("UPDATE usuarios_sistema SET senha = ? WHERE id = ?", (nova, uid))
    return redirect('/?aba=configuracoes')

@app.route('/admin/usuarios/excluir/<int:id>')
def admin_usuario_excluir(id):
    if session.get('usuario_perfil') != 'admin':
        return redirect('/login')
    u = consultar_um("SELECT usuario FROM usuarios_sistema WHERE id = ?", (id,))
    if u and u.get('usuario') == 'admin':
        return "<script>alert('Não é permitido apagar o Administrador!'); window.history.back();</script>"
    executar_comando("DELETE FROM usuarios_sistema WHERE id = ?", (id,))
    return redirect('/?aba=configuracoes')

@app.route('/admin/alunos/redefinir_senha', methods=['POST'])
def admin_aluno_redefinir_senha():
    aid, nova = request.form.get('aluno_id'), request.form.get('nova_senha', '').strip()
    if aid and nova:
        executar_comando("UPDATE doutrina SET senha = ? WHERE id = ?", (nova, aid))
    return redirect('/?aba=doutrina')
"""

if "/admin/usuarios/redefinir_senha" not in app_text:
    app_text = rotas_admin_senhas + "\n" + app_text

# 3. Garantir a compatibilidade do Supabase no executar_comando e consultar_todos
app_text = app_text.replace("cur.execute(sql, params)", """if DATABASE_URL:
            sql = sql.replace('?', '%s')
        cur.execute(sql, params)""")

# 4. Injetar usuários em injetar_dados se não estiver
if "'usuarios_todos'" not in app_text:
    app_text = app_text.replace("return {", "usuarios_todos = consultar_todos('SELECT * FROM usuarios_sistema ORDER BY id ASC')\n    return {\n        'usuarios_todos': usuarios_todos,")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_text)
print("✓ app.py atualizado com /logout, compatibilidade Supabase e controlo de palavras-passe!")

# =============================================================================
# 4. ATUALIZAR TEMPLATES/DASHBOARD.HTML (SEPARAÇÃO DE PERFIS E MODAL DE SENHAS)
# =============================================================================
with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    dash_html = f.read()

# Menu lateral seguro e filtrado
menu_lateral_seguro = """            <nav class="p-3 space-y-1 text-xs font-semibold">
                
                <!-- VISÃO GERAL: LIDERANÇA E ADMIN -->
                {% if usuario_logado and usuario_logado.perfil in ['admin', 'pastor', 'lideranca'] %}
                <div class="px-3 py-2 text-[10px] font-bold uppercase tracking-wider text-slate-400">Visão Geral</div>
                <a href="/?aba=dashboard" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'dashboard' %}bg-indigo-600 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                    <span>🔬</span><span>Raio-X Demográfico</span>
                </a>
                {% endif %}

                <!-- SECRETARIA: MEMBROS, CULTOS E ACTOS (SECRETÁRIO, LIDERANÇA E ADMIN) -->
                {% if usuario_logado and usuario_logado.perfil in ['admin', 'pastor', 'lideranca', 'secretario'] %}
                <div class="px-3 pt-3 pb-1 text-[10px] font-bold uppercase tracking-wider text-slate-400">Geral & Frequência</div>

                <a href="/?aba=membros" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'membros' %}bg-indigo-600 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                    <span>👥</span><span>1. Membros ({{ demografia.membros_cadastrados }})</span>
                </a>

                <a href="/?aba=secretaria" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'secretaria' %}bg-indigo-600 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                    <span>📋</span><span>2. Secretaria & Planos</span>
                </a>

                <a href="/?aba=cultos" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'cultos' %}bg-indigo-600 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                    <span>⛪</span><span>3. Cultos & Presenças</span>
                </a>

                <a href="/?aba=convertidos" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'convertidos' %}bg-indigo-600 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                    <span>🌱</span><span>4. Novos Convertidos</span>
                </a>

                <a href="/?aba=actos" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'actos' %}bg-pink-700 text-white shadow-md{% else %}text-pink-300 hover:bg-slate-800{% endif %}">
                    <span>💒</span><span>Actos (Casamentos & Óbitos)</span>
                </a>
                {% endif %}

                <!-- FINANÇAS & TESOURARIA (SECRETÁRIO NUNCA VÊ) -->
                {% if usuario_logado and usuario_logado.perfil in ['admin', 'pastor', 'lideranca', 'tesoureiro'] %}
                <div class="px-3 pt-3 pb-1 text-[10px] font-bold uppercase tracking-wider text-emerald-400">Finanças & Tesouraria</div>

                <a href="/?aba=financas" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'financas' %}bg-emerald-700 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                    <span>📊</span><span>5. Dashboard Financeiro</span>
                </a>

                <!-- LANÇAMENTOS: EXCLUSIVO TESOURARIA E ADMIN -->
                {% if usuario_logado.perfil in ['tesoureiro', 'admin'] %}
                <a href="/?aba=tesouraria" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'tesouraria' %}bg-amber-600 text-white shadow-md{% else %}text-amber-300 hover:bg-slate-800{% endif %}">
                    <span>🔐</span><span>6. Caixa & Lançamentos</span>
                </a>
                {% endif %}
                {% endif %}

                <!-- ENSINO & DOUTRINA (NÃO APARECE NO SECRETARIADO NEM NA TESOURARIA) -->
                {% if usuario_logado and usuario_logado.perfil in ['admin', 'pastor', 'lideranca'] %}
                <div class="px-3 pt-3 pb-1 text-[10px] font-bold uppercase tracking-wider text-amber-400">Ensino & Formação</div>

                <a href="/?aba=doutrina" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'doutrina' %}bg-amber-700 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                    <span>📖</span><span>7. Doutrina & Batismo</span>
                </a>
                {% endif %}

                {% if usuario_logado and usuario_logado.perfil == 'admin' %}
                <div class="px-3 pt-3 pb-1 text-[10px] font-bold uppercase tracking-wider text-purple-400">Parâmetros & Controlo</div>
                <a href="/?aba=configuracoes" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'configuracoes' %}bg-purple-700 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                    <span>⚙️</span><span>Gestor de Contas & Seletores</span>
                </a>
                {% endif %}
            </nav>"""

dash_html = re.sub(r'<nav class="p-3 space-y-1 text-xs font-semibold">[\s\S]*?<\/nav>', menu_lateral_seguro, dash_html)

# Botão Sair com rota garantida /logout
dash_html = re.sub(
    r'<div class="p-4 border-t border-slate-800 text-xs text-slate-400[\s\S]*?<\/aside>',
    """        <div class="p-4 border-t border-slate-800 text-xs text-slate-400 flex items-center justify-between">
            <div>
                <p class="font-bold text-white">{{ usuario_logado.nome if usuario_logado else 'Utilizador' }}</p>
                <p class="text-[10px] text-amber-400 uppercase font-semibold">{{ usuario_logado.perfil if usuario_logado else 'Local' }}</p>
            </div>
            <a href="/logout" class="px-3 py-1.5 bg-rose-600 hover:bg-rose-700 text-white rounded-xl text-xs font-bold transition flex items-center gap-1 shadow cursor-pointer">
                <span>🚪</span><span>Sair</span>
            </a>
        </div>
    </aside>""",
    dash_html
)

# Painel de utilizadores dentro de configurações
painel_usuarios_html = """        <!-- GESTÃO DE UTILIZADORES E SENHAS (EXCLUSIVO ADMIN) -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-8 text-xs">
            <div class="lg:col-span-5 bg-white p-6 rounded-2xl shadow-sm border-2 border-indigo-200 space-y-4">
                <h3 class="font-black text-sm uppercase text-indigo-950 border-b pb-2 flex items-center gap-2">
                    <span>👤</span> Registar Novo Utilizador do Sistema
                </h3>
                <form action="/admin/usuarios/novo" method="POST" class="space-y-3">
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">Nome Completo do Operador *</label>
                        <input type="text" name="nome" required placeholder="Ex: Diác. Manuel da Silva" class="w-full h-10 px-3 border rounded-xl bg-slate-50 font-bold">
                    </div>
                    <div class="grid grid-cols-2 gap-2">
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">Utilizador (Login) *</label>
                            <input type="text" name="usuario" required placeholder="Ex: manuel" class="w-full h-10 px-3 border rounded-xl bg-slate-50 font-bold">
                        </div>
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">Palavra-passe *</label>
                            <input type="text" name="senha" value="123456" required class="w-full h-10 px-3 border rounded-xl bg-slate-50 font-bold">
                        </div>
                    </div>
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">Perfil / Nível de Acesso *</label>
                        <select name="perfil" required class="w-full h-10 px-2 border-2 border-indigo-300 rounded-xl bg-indigo-50/50 font-black text-indigo-950">
                            <option value="secretario">📋 Secretariado (Membros, Cultos e Actos)</option>
                            <option value="tesoureiro">🔐 Tesouraria (Caixa e Finanças Exclusivo)</option>
                            <option value="lideranca">⛪ Pastor / Liderança (Audita e vê censo)</option>
                            <option value="admin">⚙️ Administrador Geral (Acesso Total)</option>
                        </select>
                    </div>
                    <button type="submit" class="w-full py-3 bg-indigo-800 hover:bg-indigo-900 text-white font-black rounded-xl shadow cursor-pointer transition">
                        Gravar Conta de Utilizador
                    </button>
                </form>
            </div>

            <div class="lg:col-span-7 bg-white p-6 rounded-2xl shadow-sm border border-slate-200 space-y-3">
                <h3 class="font-extrabold text-sm text-slate-800 border-b pb-2 flex justify-between items-center">
                    <span>👥 Utilizadores Activos & Recuperação de Senhas</span>
                    <span class="bg-indigo-100 text-indigo-900 px-2.5 py-0.5 rounded-full font-black text-[11px]">{{ usuarios_todos|length }} Contas</span>
                </h3>

                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs">
                        <thead>
                            <tr class="border-b text-slate-500 font-bold">
                                <th class="py-2 px-1">Nome & Login</th>
                                <th class="py-2 px-1">Perfil</th>
                                <th class="py-2 px-1 text-right">Recuperar Senha</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for u in usuarios_todos %}
                            <tr class="border-b hover:bg-slate-50">
                                <td class="py-2.5 px-1">
                                    <div class="font-extrabold text-slate-900">{{ u.nome }}</div>
                                    <div class="text-[10px] text-slate-400">User: <b class="text-indigo-900">{{ u.usuario }}</b></div>
                                </td>
                                <td class="py-2.5 px-1">
                                    <span class="px-2 py-0.5 rounded font-black text-[10px] bg-slate-100 text-slate-800">{{ u.perfil|upper }}</span>
                                </td>
                                <td class="py-2.5 px-1 text-right space-x-1.5">
                                    <button onclick="abrirModalSenha('{{ u.id }}', '{{ u.nome }}')" class="px-2.5 py-1 bg-amber-500 hover:bg-amber-600 text-slate-950 rounded-lg font-black text-[10px] shadow">
                                        🔑 Mudar Senha
                                    </button>
                                    {% if u.usuario != 'admin' %}
                                    <a href="/admin/usuarios/excluir/{{ u.id }}" onclick="return confirm('Apagar utilizador?')" class="px-2 py-1 bg-rose-100 text-rose-700 rounded-lg font-bold text-[10px]">🗑️</a>
                                    {% endif %}
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- MODAL DE SENHA -->
        <div id="modal_redefinir_senha" class="hidden fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
            <div class="bg-white rounded-3xl p-6 max-w-sm w-full shadow-2xl space-y-4 text-xs border border-amber-300">
                <div class="flex justify-between items-center border-b pb-2">
                    <h4 class="font-black text-sm text-slate-900">🔑 Redefinir Palavra-passe</h4>
                    <button onclick="fecharModalSenha()" class="text-slate-400 hover:text-slate-600 font-black text-lg">&times;</button>
                </div>
                <form action="/admin/usuarios/redefinir_senha" method="POST" class="space-y-3">
                    <input type="hidden" id="modal_user_id" name="usuario_id">
                    <div>
                        <span class="text-slate-500 block mb-1">Operador selecionado:</span>
                        <b id="modal_user_nome" class="text-indigo-950 font-black text-sm block">---</b>
                    </div>
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">Nova Palavra-passe:</label>
                        <input type="text" name="nova_senha" required placeholder="Nova senha" class="w-full h-11 px-3 border-2 border-amber-400 rounded-xl bg-slate-50 font-bold">
                    </div>
                    <div class="flex gap-2 pt-2">
                        <button type="button" onclick="fecharModalSenha()" class="flex-1 py-2.5 bg-slate-200 text-slate-700 font-bold rounded-xl">Cancelar</button>
                        <button type="submit" class="flex-1 py-2.5 bg-amber-600 hover:bg-amber-700 text-white font-black rounded-xl shadow">Salvar</button>
                    </div>
                </form>
            </div>
        </div>

        <script>
            function abrirModalSenha(id, nome) {
                document.getElementById('modal_user_id').value = id;
                document.getElementById('modal_user_nome').innerText = nome;
                document.getElementById('modal_redefinir_senha').classList.remove('hidden');
            }
            function fecharModalSenha() {
                document.getElementById('modal_redefinir_senha').classList.add('hidden');
            }
        </script>"""

if '<!-- GESTÃO DE UTILIZADORES E SENHAS' not in dash_html:
    dash_html = dash_html.replace(
        "{% if aba_ativa == 'configuracoes' and usuario_logado.perfil == 'admin' %}\n        <div class=\"bg-purple-950",
        "{% if aba_ativa == 'configuracoes' and usuario_logado.perfil == 'admin' %}\n" + painel_usuarios_html + "\n        <div class=\"bg-purple-950"
    )

# Redefinir senha do aluno em Doutrina
if 'promptRedefinirSenhaAluno' not in dash_html:
    dash_html = dash_html.replace(
        "| Senha: <b>{{ d.senha or '123456' }}</b>",
        "| Senha: <b>{{ d.senha or '123456' }}</b> <button onclick=\"promptRedefinirSenhaAluno('{{ d.id }}', '{{ d.nome_aluno }}')\" class=\"ml-1 text-amber-600 hover:text-amber-800 font-black text-[9px] underline\">🔑 Mudar</button>"
    )
    dash_html = dash_html.replace(
        "</body>",
        """    <form id="form_senha_aluno" action="/admin/alunos/redefinir_senha" method="POST" class="hidden">
        <input type="hidden" id="aluno_senha_id" name="aluno_id">
        <input type="hidden" id="aluno_senha_val" name="nova_senha">
    </form>
    <script>
        function promptRedefinirSenhaAluno(id, nome) {
            var nova = prompt("Digite a nova palavra-passe para o formando " + nome + ":", "123456");
            if (nova && nova.trim() !== "") {
                document.getElementById('aluno_senha_id').value = id;
                document.getElementById('aluno_senha_val').value = nova.trim();
                document.getElementById('form_senha_aluno').submit();
            }
        }
    </script>
</body>"""
    )

env.parse(dash_html)
with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(dash_html)
print("✓ templates/dashboard.html atualizado com gestão de senhas e separação por perfis!")

print("=" * 80)
print(">>> INSTALAÇÃO CONCLUÍDA COM SUCESSO ABSOLUTO! ZERO CORTES! <<<")
print("=" * 80)