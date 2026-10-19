import os
import jinja2

print("=" * 80)
print("A CONFIGURAR PORTAL DE ENTRADA, ROTA /logout E SEPARAÇÃO DE PERFIS...")
print("=" * 80)

os.makedirs('templates', exist_ok=True)
env = jinja2.Environment()

# =============================================================================
# 1. LOGÓTIPO OFICIAL DA ASSEMBLEIA DE DEUS EM MOÇAMBIQUE (VETORIAL HD)
# =============================================================================
logo_svg_html = """<div class="inline-flex items-center justify-center select-none">
    <svg viewBox="0 0 450 450" class="w-full h-full max-w-[170px] max-h-[170px] drop-shadow-md" xmlns="http://www.w3.org/2000/svg">
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

with open(os.path.join('templates', 'logo_ad.html'), 'w', encoding='utf-8') as f:
    f.write(logo_svg_html)
print("✓ templates/logo_ad.html criado!")

# =============================================================================
# 2. PORTA DE ENTRADA ESPECTACULAR E INTERATIVA (TEMPLATES/LOGIN.HTML)
# =============================================================================
login_html = """<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portal Oficial - Assembleia de Deus em Moçambique</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .celestial-bg {
            background: radial-gradient(circle at 50% 0%, #1e1b4b 0%, #0f172a 50%, #020617 100%);
        }
        .glow-gold {
            box-shadow: 0 0 45px -5px rgba(245, 158, 11, 0.35);
        }
    </style>
</head>
<body class="celestial-bg min-h-screen flex items-center justify-center p-4 font-sans text-slate-800">

    <div class="max-w-4xl w-full grid grid-cols-1 md:grid-cols-12 bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl overflow-hidden border border-amber-500/30 glow-gold">

        <!-- LADO ESQUERDO: BOAS-VINDAS INSTITUCIONAL -->
        <div class="md:col-span-5 bg-gradient-to-br from-indigo-950 via-slate-900 to-slate-950 p-8 text-white flex flex-col justify-between relative overflow-hidden border-r border-indigo-900/40">
            <div class="space-y-4 relative z-10 text-center sm:text-left">
                <div class="w-28 h-28 mx-auto sm:mx-0 bg-white rounded-3xl p-2 shadow-2xl flex items-center justify-center border-2 border-amber-400">
                    {% include 'logo_ad.html' %}
                </div>

                <div>
                    <span id="saudacao_tempo" class="bg-amber-400/20 text-amber-300 border border-amber-400/40 text-[9px] font-black uppercase px-2.5 py-0.5 rounded-full inline-block mb-1">
                        Paz do Senhor Jesus
                    </span>
                    <h1 class="text-xl font-black uppercase tracking-wide leading-tight">
                        ASSEMBLEIA DE DEUS
                    </h1>
                    <p class="text-[11px] text-blue-300 font-bold mt-0.5">República de Moçambique</p>
                </div>

                <div class="bg-white/5 border border-white/10 p-4 rounded-2xl text-xs space-y-2 text-indigo-100 backdrop-blur-sm">
                    <p class="font-extrabold text-amber-300 flex items-center gap-1.5 text-[11px]">
                        <span>🕊️</span> Bem-vindo à Casa do Senhor!
                    </p>
                    <p class="leading-relaxed text-[11px] text-justify text-slate-200">
                        Plataforma integrada de gestão ministerial, membresia e formação teológica. O acesso é direcionado estritamente à sua área de ministério e vocação.
                    </p>
                </div>
            </div>

            <div class="pt-6 relative z-10 border-t border-white/10 text-[10px] italic text-indigo-200 text-center font-serif">
                "Alegrei-me quando me disseram: Vamos à casa do Senhor!" (Salmo 122:1)
            </div>
        </div>

        <!-- LADO DIREITO: FORMULÁRIO COM ATALHOS POR PERFIL -->
        <div class="md:col-span-7 p-8 sm:p-10 flex flex-col justify-between space-y-6">

            <div class="space-y-1">
                <h2 class="text-2xl font-black text-slate-900">Acesso ao Sistema</h2>
                <p class="text-xs text-slate-500">Introduza as suas credenciais para entrar na sua área eclesiástica.</p>
            </div>

            {% if erro %}
            <div class="p-3 bg-rose-50 border-2 border-rose-300 rounded-xl text-rose-800 text-xs font-bold text-center">
                {{ erro }}
            </div>
            {% endif %}

            <form action="/login" method="POST" class="space-y-4 text-xs">
                <div>
                    <label class="block font-bold text-slate-700 mb-1">Nome de Utilizador *</label>
                    <div class="relative">
                        <span class="absolute left-3.5 top-3 text-slate-400">👤</span>
                        <input type="text" id="campo_usuario" name="usuario" required placeholder="Digite o seu utilizador" class="w-full h-11 pl-10 pr-3 border-2 border-slate-200 rounded-xl bg-slate-50 focus:bg-white focus:border-indigo-600 focus:outline-none font-bold">
                    </div>
                </div>

                <div>
                    <label class="block font-bold text-slate-700 mb-1">Palavra-passe *</label>
                    <div class="relative">
                        <span class="absolute left-3.5 top-3 text-slate-400">🔒</span>
                        <input type="password" id="campo_senha" name="senha" required placeholder="••••••••" class="w-full h-11 pl-10 pr-3 border-2 border-slate-200 rounded-xl bg-slate-50 focus:bg-white focus:border-indigo-600 focus:outline-none font-bold">
                    </div>
                </div>

                <button type="submit" class="w-full py-3.5 bg-gradient-to-r from-indigo-900 to-blue-900 hover:from-indigo-950 hover:to-blue-950 text-white font-black rounded-xl shadow-xl cursor-pointer text-sm transition transform hover:-translate-y-0.5">
                    Entrar no Meu Perfil →
                </button>
            </form>

            <div class="space-y-2 pt-2 border-t border-slate-200">
                <span class="text-[10px] uppercase font-bold text-slate-400 block tracking-wider">Perfis & Acessos Diretos:</span>
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
                        <span class="text-[9px] text-slate-500">Vê tudo (audita finanças)</span>
                    </button>
                    <button type="button" onclick="preencherLogin('anselmo', '123456')" class="p-2 bg-emerald-50/60 hover:bg-emerald-100 border border-emerald-200 rounded-xl text-left transition">
                        <span class="font-black text-emerald-950 block">🎓 Aluno / Estudante</span>
                        <span class="text-[9px] text-emerald-700">Vai direto para a Aula</span>
                    </button>
                </div>
            </div>

        </div>

    </div>

    <script>
        var hora = new Date().getHours();
        var saudacao = "Paz do Senhor • Bom dia";
        if (hora >= 12 && hora < 18) saudacao = "Paz do Senhor • Boa tarde";
        else if (hora >= 18 || hora < 5) saudacao = "Paz do Senhor • Boa noite";
        var el = document.getElementById('saudacao_tempo');
        if (el) el.innerText = saudacao;

        function preencherLogin(u, s) {
            document.getElementById('campo_usuario').value = u;
            document.getElementById('campo_senha').value = s;
        }
    </script>

</body>
</html>
"""

env.parse(login_html)
with open(os.path.join('templates', 'login.html'), 'w', encoding='utf-8') as f:
    f.write(login_html)
print("✓ templates/login.html criado com sucesso!")

# =============================================================================
# 3. ATUALIZAR APP.PY COM /logout CORRIGIDO E REDIRECIONAMENTOS BLINDADOS
# =============================================================================
with open('app.py', 'r', encoding='utf-8') as f:
    app_text = f.read()

# Bloco das rotas de Login, Logout e Index com proteção estrita de perfis
bloco_login_e_index = '''
# =============================================================================
# ROTAS DE AUTENTICAÇÃO, LOGOUT E NAVEGAÇÃO SEGURA POR PERFIS
# =============================================================================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/ensino/logout')
def aluno_logout():
    session.clear()
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        usuario = request.form.get('usuario', '').strip().lower()
        senha = request.form.get('senha', '').strip()
        m = "%s" if DATABASE_URL else "?"

        # 1. Verificar se é Aluno / Estudante
        aluno = consultar_um(f"SELECT * FROM doutrina WHERE LOWER(usuario) = {m} AND senha = {m}", (usuario, senha))
        if aluno:
            session.clear()
            session['aluno_id'] = aluno['id']
            session['aluno_nome'] = aluno['nome_aluno']
            session['usuario_perfil'] = 'aluno'
            return redirect('/ensino/aulas')

        # 2. Verificar se é Utilizador Administrativo
        u = consultar_um(f"SELECT * FROM usuarios_sistema WHERE LOWER(usuario) = {m} AND senha = {m}", (usuario, senha))
        if u:
            session.clear()
            session['usuario_id'] = u['id']
            session['usuario_nome'] = u['nome']
            session['usuario_perfil'] = u['perfil']
            session['usuario_nivel'] = u.get('nivel', 'local')
            session['congregacao_id'] = u.get('congregacao_id', 1)

            # REDIRECIONAMENTO IMEDIATO POR PERFIL
            if u['perfil'] == 'tesoureiro':
                return redirect('/?aba=tesouraria')
            elif u['perfil'] == 'secretario':
                return redirect('/?aba=membros')
            elif u['perfil'] == 'professor':
                return redirect('/?aba=doutrina')
            elif u['perfil'] in ['lideranca', 'pastor']:
                return redirect('/?aba=dashboard')
            else: # admin
                return redirect('/?aba=dashboard')
        else:
            erro = "Credenciais inválidas! Verifique o utilizador e a palavra-passe."

    return render_template('login.html', erro=erro)

@app.route('/')
def index():
    if not session.get('usuario_id') and not session.get('aluno_id'):
        return redirect('/login')

    # Aluno nunca acede à administração!
    if session.get('usuario_perfil') == 'aluno':
        return redirect('/ensino/aulas')

    perfil = session.get('usuario_perfil', '')
    aba = request.args.get('aba')

    # Se não especificou aba, atribui a aba natural do perfil
    if not aba:
        if perfil == 'secretario': aba = 'membros'
        elif perfil == 'tesoureiro': aba = 'tesouraria'
        elif perfil == 'professor': aba = 'doutrina'
        else: aba = 'dashboard'

    # PROTEÇÕES DE ACESSO NO SERVIDOR
    if perfil == 'secretario':
        # Secretariado NUNCA vê finanças, caixa nem ensino/doutrina!
        if aba in ['financas', 'tesouraria', 'doutrina']:
            return redirect('/?aba=membros')
    elif perfil == 'tesoureiro':
        # Tesoureira fica focada na sua área financeira
        if aba not in ['financas', 'tesouraria']:
            return redirect('/?aba=tesouraria')
    elif perfil == 'professor':
        # Professor só acede à doutrina
        if aba not in ['doutrina']:
            return redirect('/?aba=doutrina')
    elif perfil in ['pastor', 'lideranca']:
        # Liderança vê tudo MENOS lançamentos de caixa
        if aba in ['tesouraria', 'configuracoes']:
            return redirect('/?aba=financas')

    id_relatar = request.args.get('relatar_id')
    plano_para_relatar = None
    if id_relatar:
        m = "%s" if DATABASE_URL else "?"
        plano_para_relatar = consultar_um(f"SELECT * FROM planificacao WHERE id = {m}", (id_relatar,))
    return render_template('dashboard.html', aba_ativa=aba, plano_relatar=plano_para_relatar)
'''

import re

# Substituir o bloco anterior de login/logout/index pelo novo bloco
if "@app.route('/login'" in app_text:
    app_text = re.sub(
        r'@app\.route\(\'/logout\'[\s\S]*?return render_template\(\'dashboard\.html\'[\s\S]*?\)',
        bloco_login_e_index.strip(),
        app_text
    )
    if "@app.route('/logout'" not in app_text:
        app_text = re.sub(
            r'@app\.route\(\'/login\'[\s\S]*?return render_template\(\'dashboard\.html\'[\s\S]*?\)',
            bloco_login_e_index.strip(),
            app_text
        )

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_text)
print("✓ app.py: Rota /logout corrigida e blindagem de perfis atualizada!")

# =============================================================================
# 4. ATUALIZAR TEMPLATES/DASHBOARD.HTML (SEPARAÇÃO TOTAL DE ENSINO E SECRETARIA)
# =============================================================================
with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    dash_html = f.read()

# Menu lateral com seções estritamente divididas por perfil
menu_lateral_seguro = """            <nav class="p-3 space-y-1 text-xs font-semibold">
                
                <!-- VISÃO GERAL: LIDERANÇA E ADMIN -->
                {% if usuario_logado and usuario_logado.perfil in ['admin', 'pastor', 'lideranca'] %}
                <div class="px-3 py-2 text-[10px] font-bold uppercase tracking-wider text-slate-400">Visão Geral</div>
                <a href="/?aba=dashboard" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'dashboard' %}bg-indigo-600 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                    <span>🔬</span><span>Raio-X Demográfico</span>
                </a>
                {% endif %}

                <!-- SECRETARIA & MEMBRESIA: SECRETÁRIO, LIDERANÇA E ADMIN -->
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

                <!-- FINANÇAS & TESOURARIA: LIDERANÇA (AUDITA), TESOUREIRO E ADMIN -->
                {% if usuario_logado and usuario_logado.perfil in ['admin', 'pastor', 'lideranca', 'tesoureiro'] %}
                <div class="px-3 pt-3 pb-1 text-[10px] font-bold uppercase tracking-wider text-emerald-400">Finanças & Tesouraria</div>

                <a href="/?aba=financas" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'financas' %}bg-emerald-700 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                    <span>📊</span><span>5. Dashboard Financeiro</span>
                </a>

                <!-- LANÇAMENTOS: EXCLUSIVO TESOURARIA E ADMIN (LIDERANÇA NÃO LANÇA) -->
                {% if usuario_logado.perfil in ['tesoureiro', 'admin'] %}
                <a href="/?aba=tesouraria" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'tesouraria' %}bg-amber-600 text-white shadow-md{% else %}text-amber-300 hover:bg-slate-800{% endif %}">
                    <span>🔐</span><span>6. Caixa & Lançamentos</span>
                </a>
                {% endif %}
                {% endif %}

                <!-- ENSINO & DOUTRINA: SEPARADO! VISÍVEL APENAS PARA PROFESSOR, LIDERANÇA E ADMIN (NUNCA PARA SECRETÁRIO) -->
                {% if usuario_logado and usuario_logado.perfil in ['admin', 'pastor', 'lideranca', 'professor'] %}
                <div class="px-3 pt-3 pb-1 text-[10px] font-bold uppercase tracking-wider text-amber-400">Ensino & Formação</div>

                <a href="/?aba=doutrina" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'doutrina' %}bg-amber-700 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                    <span>📖</span><span>7. Doutrina & Batismo</span>
                </a>
                {% endif %}

                {% if usuario_logado and usuario_logado.perfil == 'admin' %}
                <div class="px-3 pt-3 pb-1 text-[10px] font-bold uppercase tracking-wider text-purple-400">Parâmetros Gerais</div>
                <a href="/?aba=configuracoes" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'configuracoes' %}bg-purple-700 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                    <span>⚙️</span><span>Gestor de Seletores</span>
                </a>
                {% endif %}
            </nav>"""

dash_html = re.sub(
    r'<nav class="p-3 space-y-1 text-xs font-semibold">[\s\S]*?<\/nav>',
    menu_lateral_seguro,
    dash_html
)

# Garantir que o botão Sair aponte sempre para /logout de forma limpa
dash_html = re.sub(
    r'<a href="\/logout"[\s\S]*?<\/a>',
    '<a href="/logout" class="px-3 py-1.5 bg-rose-600 hover:bg-rose-700 text-white rounded-xl text-xs font-bold transition flex items-center gap-1 shadow"><span>🚪</span><span>Sair</span></a>',
    dash_html
)

env.parse(dash_html)
with open(os.path.join('templates', 'dashboard.html'), 'w', encoding='utf-8') as f:
    f.write(dash_html)
print("✓ templates/dashboard.html: Menu lateral e botão Sair atualizados!")

print("=" * 80)
print(">>> CORREÇÃO CONCLUÍDA COM TOTAL SUCESSO! <<<")
print("=" * 80)