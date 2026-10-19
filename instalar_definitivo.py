import os
import jinja2

print("=" * 80)
print("A INSTALAR PORTAL ESPECTACULAR, PERFIS RBAC E RESTAURAÇÃO TOTAL...")
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
print("✓ templates/logo_ad.html: Logótipo oficial gravado!")

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

        <!-- LADO ESQUERDO: APRESENTAÇÃO INSTITUCIONAL & BOAS-VINDAS -->
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
                        Um ambiente eclesiástico integrado, seguro e transparente para a expansão do Reino de Deus. Cada servo e formando é direcionado imediatamente à sua área de vocação e ministério.
                    </p>
                </div>
            </div>

            <div class="pt-6 relative z-10 border-t border-white/10 text-[10px] italic text-indigo-200 text-center font-serif">
                "Alegrei-me quando me disseram: Vamos à casa do Senhor!" (Salmo 122:1)
            </div>
        </div>

        <!-- LADO DIREITO: FORMULÁRIO COM ATALHOS DE PERFIL -->
        <div class="md:col-span-7 p-8 sm:p-10 flex flex-col justify-between space-y-6">

            <div class="space-y-1">
                <h2 class="text-2xl font-black text-slate-900">Acesso ao Sistema</h2>
                <p class="text-xs text-slate-500">Introduza as suas credenciais para entrar diretamente na sua área.</p>
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
                    <button type="button" onclick="preencherLogin('pastor', 'pastor123')" class="p-2 bg-slate-50 hover:bg-indigo-50 border rounded-xl text-left transition">
                        <span class="font-black text-indigo-950 block">⛪ Liderança / Pastor</span>
                        <span class="text-[9px] text-slate-500">Vê tudo (sem lançar caixa)</span>
                    </button>
                    <button type="button" onclick="preencherLogin('tesouraria', 'tesouro123')" class="p-2 bg-amber-50/60 hover:bg-amber-100 border border-amber-200 rounded-xl text-left transition">
                        <span class="font-black text-amber-950 block">🔐 Tesoureira</span>
                        <span class="text-[9px] text-amber-700">Entra direto no Caixa</span>
                    </button>
                    <button type="button" onclick="preencherLogin('secretaria', 'sec123')" class="p-2 bg-blue-50/60 hover:bg-blue-100 border border-blue-200 rounded-xl text-left transition">
                        <span class="font-black text-blue-950 block">📋 Secretariado</span>
                        <span class="text-[9px] text-blue-700">Membros e Actos (sem finanças)</span>
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
# 3. ATUALIZAR O APP.PY COM REDIRECIONAMENTOS RIGOROSOS E TODAS AS VARIÁVEIS
# =============================================================================
with open('app.py', 'r', encoding='utf-8') as f:
    app_py_code = f.read()

# Substituir a rota /login e a rota /
import re

novo_bloco_login_e_index = '''@app.route('/login', methods=['GET', 'POST'])
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
            session['usuario_nivel'] = u['nivel']
            session['congregacao_id'] = u.get('congregacao_id', 1)

            # REDIRECIONAMENTOS AUTOMÁTICOS BASEADOS NO PERFIL
            if u['perfil'] == 'tesoureiro':
                return redirect('/?aba=tesouraria')
            elif u['perfil'] == 'secretario':
                return redirect('/?aba=membros')
            elif u['perfil'] in ['lideranca', 'pastor']:
                return redirect('/?aba=dashboard')
            else:
                return redirect('/?aba=dashboard')
        else:
            erro = "Credenciais inválidas! Verifique o utilizador e a palavra-passe."

    return render_template('login.html', erro=erro)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/')
def index():
    if not session.get('usuario_id') and not session.get('aluno_id'):
        return redirect('/login')

    # Aluno nunca entra na administração! Vai direto para a aula!
    if session.get('usuario_perfil') == 'aluno':
        return redirect('/ensino/aulas')

    aba = request.args.get('aba', 'dashboard')
    perfil = session.get('usuario_perfil', '')

    # BLINDAGENS DE ACESSO POR PERFIL NO SERVIDOR
    if perfil == 'secretario' and aba in ['financas', 'tesouraria']:
        return redirect('/?aba=membros')
    if perfil in ['lideranca', 'pastor'] and aba == 'tesouraria':
        return redirect('/?aba=financas')

    id_relatar = request.args.get('relatar_id')
    plano_para_relatar = None
    if id_relatar:
        m = "%s" if DATABASE_URL else "?"
        plano_para_relatar = consultar_um(f"SELECT * FROM planificacao WHERE id = {m}", (id_relatar,))
    return render_template('dashboard.html', aba_ativa=aba, plano_relatar=plano_para_relatar)'''

app_py_code = re.sub(
    r'@app\.route\(\'/login\'[\s\S]*?return render_template\(\'dashboard\.html\'[\s\S]*?\)',
    novo_bloco_login_e_index,
    app_py_code
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_py_code)
print("✓ app.py: Lógica de autenticação e redirecionamento de perfis atualizada!")

# =============================================================================
# 4. RECONSTRUIR TEMPLATES/DASHBOARD.HTML COM TODAS AS ABAS E SEGURANÇA
# =============================================================================
dash_completo = """<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IEAD Moçambique - {{ congregacao.nome }}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.getRegistrations().then(function(regs) {
                for (let r of regs) r.unregister();
            });
        }
    </script>
</head>
<body class="bg-slate-100 text-slate-800 font-sans min-h-screen flex">

    <!-- MENU LATERAL COM O LOGO OFICIAL -->
    <aside class="w-64 bg-slate-900 text-white flex flex-col justify-between min-h-screen shrink-0 shadow-xl">
        <div>
            <div class="p-4 border-b border-slate-800 flex items-center gap-3">
                <div class="w-12 h-12 bg-white rounded-full p-1 flex items-center justify-center shrink-0 shadow">
                    {% include 'logo_ad.html' %}
                </div>
                <div class="overflow-hidden">
                    <h1 class="font-extrabold text-xs uppercase tracking-wide leading-tight text-white truncate">
                        ASSEMBLEIA DE DEUS
                    </h1>
                    <p class="text-[10px] text-amber-400 font-semibold truncate">{{ congregacao.nome }}</p>
                    <p class="text-[9px] text-slate-400 truncate">{{ congregacao.distrito }}</p>
                </div>
            </div>

            <nav class="p-3 space-y-1 text-xs font-semibold">
                <div class="px-3 py-2 text-[10px] font-bold uppercase tracking-wider text-slate-400">Visão Geral</div>
                
                <a href="/?aba=dashboard" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'dashboard' %}bg-indigo-600 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                    <span>🔬</span><span>Raio-X Demográfico</span>
                </a>

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

                <!-- BLOCO FINANCEIRO CONTROLADO POR PERFIL -->
                {% if usuario_logado and usuario_logado.perfil != 'secretario' %}
                <div class="px-3 pt-3 pb-1 text-[10px] font-bold uppercase tracking-wider text-emerald-400">Finanças & Tesouraria</div>

                <!-- Dashboard Financeiro: Liderança/Pastor, Tesouraria e Admin -->
                <a href="/?aba=financas" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'financas' %}bg-emerald-700 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                    <span>📊</span><span>5. Dashboard Financeiro</span>
                </a>

                <!-- Caixa & Lançamentos: EXCLUSIVO DA TESOURARIA E ADMIN (Liderança e Secretaria NÃO VÊEM) -->
                {% if usuario_logado.perfil in ['tesoureiro', 'admin'] %}
                <a href="/?aba=tesouraria" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'tesouraria' %}bg-amber-600 text-white shadow-md{% else %}text-amber-300 hover:bg-slate-800{% endif %}">
                    <span>🔐</span><span>6. Caixa & Lançamentos</span>
                </a>
                {% endif %}
                {% endif %}

                <div class="px-3 pt-3 pb-1 text-[10px] font-bold uppercase tracking-wider text-amber-400">Ensino & Parâmetros</div>

                <a href="/?aba=doutrina" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'doutrina' %}bg-amber-700 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                    <span>📖</span><span>7. Doutrina & Batismo</span>
                </a>

                {% if usuario_logado and usuario_logado.perfil == 'admin' %}
                <a href="/?aba=configuracoes" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'configuracoes' %}bg-purple-700 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                    <span>⚙️</span><span>Gestor de Seletores</span>
                </a>
                {% endif %}
            </nav>
        </div>

        <div class="p-4 border-t border-slate-800 text-xs text-slate-400 flex items-center justify-between">
            <div>
                <p class="font-bold text-white">{{ usuario_logado.nome if usuario_logado else 'Utilizador' }}</p>
                <p class="text-[10px] text-amber-400 uppercase font-semibold">{{ usuario_logado.perfil if usuario_logado else 'Local' }}</p>
            </div>
            <a href="/logout" class="px-2 py-1 bg-slate-800 hover:bg-rose-700 text-slate-300 hover:text-white rounded text-[10px] font-bold">Sair</a>
        </div>
    </aside>

    <!-- ÁREA PRINCIPAL -->
    <main class="flex-1 p-6 overflow-y-auto">

        <!-- ========================================================= -->
        <!-- ABA: RAIO-X ECLESIÁSTICO & DEMOGRAFIA (ZERO FINANÇAS)     -->
        <!-- ========================================================= -->
        {% if aba_ativa == 'dashboard' %}
        <div class="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white p-6 rounded-3xl shadow-xl mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div class="flex items-center gap-4">
                <div class="w-16 h-16 bg-white rounded-2xl p-1.5 shrink-0 hidden sm:block">
                    {% include 'logo_ad.html' %}
                </div>
                <div>
                    <div class="inline-flex items-center gap-2 bg-indigo-500/20 text-indigo-300 px-3 py-1 rounded-full text-[10px] font-black uppercase mb-1 border border-indigo-400/30">
                        <span>🔬</span> CENSO MINISTERIAL • DEMOGRAFIA PROFUNDA
                    </div>
                    <h2 class="text-2xl font-black">Raio-X Eclesiástico: {{ congregacao.nome }}</h2>
                    <p class="text-xs text-indigo-200 mt-0.5">Estatística de almas congregadas sem interferência financeira • {{ congregacao.distrito }}</p>
                </div>
            </div>
            <div class="bg-white/10 p-4 rounded-2xl border border-white/10 text-center shrink-0">
                <span class="text-[10px] uppercase font-bold text-indigo-200 block">Total de Almas no Rebanho</span>
                <span class="text-3xl font-black text-amber-300">{{ demografia.total_almas }} Vidas</span>
                <span class="text-[10px] text-slate-300 block mt-0.5">{{ demografia.membros_cadastrados }} Membros • {{ demografia.novos_convertidos }} em Discipulado</span>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-8 text-xs">
            <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 space-y-2">
                <div class="text-slate-500 text-[10px] font-bold uppercase tracking-wider">Distribuição por Género</div>
                <div class="flex justify-between items-baseline">
                    <span class="text-2xl font-black text-slate-900">👨 {{ demografia.homens }} <span class="text-xs font-normal text-slate-400">Homens</span></span>
                    <span class="text-2xl font-black text-indigo-900">👩 {{ demografia.mulheres }} <span class="text-xs font-normal text-slate-400">Mulheres</span></span>
                </div>
                <div class="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden flex border">
                    <div class="bg-blue-600 h-full" style="width: {{ demografia.perc_homens }}%"></div>
                    <div class="bg-pink-500 h-full" style="width: {{ demografia.perc_mulheres }}%"></div>
                </div>
                <div class="flex justify-between text-[10px] text-slate-500 font-bold">
                    <span>Homens: {{ demografia.perc_homens }}%</span>
                    <span>Mulheres: {{ demografia.perc_mulheres }}%</span>
                </div>
            </div>

            <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 space-y-1.5">
                <div class="text-slate-500 text-[10px] font-bold uppercase tracking-wider">Composição Etária</div>
                <div class="flex justify-between items-center text-slate-800 font-bold pt-1">
                    <span>👶 Crianças (Boa Esperança):</span>
                    <span class="text-blue-700 font-black">{{ demografia.criancas }}</span>
                </div>
                <div class="flex justify-between items-center text-slate-800 font-bold">
                    <span>👦 Juventude Cristã:</span>
                    <span class="text-indigo-700 font-black">{{ demografia.jovens }}</span>
                </div>
                <div class="flex justify-between items-center text-slate-800 font-bold">
                    <span>👨‍👩‍👧‍👦 Adultos & Seniores:</span>
                    <span class="text-amber-800 font-black">{{ demografia.adultos }}</span>
                </div>
            </div>

            <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 space-y-1.5">
                <div class="text-slate-500 text-[10px] font-bold uppercase tracking-wider">Situação Eclesiástica</div>
                <div class="flex justify-between items-center text-emerald-800 font-bold pt-1">
                    <span>🌊 Membros Baptizados:</span>
                    <span class="font-black">{{ demografia.batizados }}</span>
                </div>
                <div class="flex justify-between items-center text-amber-800 font-bold">
                    <span>🌱 Não Baptizados / Doutrina:</span>
                    <span class="font-black">{{ demografia.nao_batizados }}</span>
                </div>
                <div class="flex justify-between items-center text-blue-800 font-bold">
                    <span>📖 Novos Convertidos:</span>
                    <span class="font-black">{{ demografia.novos_convertidos }}</span>
                </div>
            </div>

            <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 space-y-1.5">
                <div class="text-slate-500 text-[10px] font-bold uppercase tracking-wider">Actos & Planificação</div>
                <div class="flex justify-between items-center text-slate-800 font-bold pt-1">
                    <span>💒 Casamentos Registados:</span>
                    <span class="text-pink-600 font-black">{{ demografia.total_casamentos }}</span>
                </div>
                <div class="flex justify-between items-center text-slate-800 font-bold">
                    <span>🕊️ Óbitos / Falecimentos:</span>
                    <span class="text-slate-600 font-black">{{ demografia.total_obitos }}</span>
                </div>
                <div class="flex justify-between items-center text-slate-800 font-bold">
                    <span>🎯 Metas Executadas:</span>
                    <span class="text-emerald-700 font-black">{{ demografia.taxa_execucao }}%</span>
                </div>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8 text-xs">
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 space-y-4">
                <h3 class="font-extrabold text-sm text-slate-900 border-b pb-2 flex items-center gap-2">
                    <span>📍</span> Cartografia Ministerial: Zonas e Células Familiares
                </h3>
                <div class="space-y-3">
                    <div>
                        <span class="font-bold text-slate-600 text-[11px] uppercase block mb-1.5">Distribuição por Zonas da Cidade:</span>
                        <div class="grid grid-cols-2 gap-2">
                            {% for z, qtd in demografia.zonas.items() %}
                            <div class="p-2.5 bg-slate-50 border rounded-xl flex justify-between items-center">
                                <span class="font-semibold text-slate-700 truncate">{{ z }}</span>
                                <span class="bg-indigo-100 text-indigo-900 px-2 py-0.5 rounded-full font-black text-[11px]">{{ qtd }}</span>
                            </div>
                            {% else %}
                            <p class="text-slate-400 italic">Nenhuma zona cadastrada.</p>
                            {% endfor %}
                        </div>
                    </div>

                    <div class="pt-2 border-t">
                        <span class="font-bold text-slate-600 text-[11px] uppercase block mb-1.5">Células Familiares Activas:</span>
                        <div class="flex flex-wrap gap-2">
                            {% for c, qtd in demografia.celulas.items() %}
                            <span class="bg-slate-100 border text-slate-800 px-3 py-1 rounded-xl font-bold flex items-center gap-1.5">
                                <span>🏠 {{ c }}:</span>
                                <b class="text-indigo-900">{{ qtd }} membros</b>
                            </span>
                            {% else %}
                            <p class="text-slate-400 italic">Nenhuma célula registada.</p>
                            {% endfor %}
                        </div>
                    </div>
                </div>
            </div>

            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 space-y-4">
                <h3 class="font-extrabold text-sm text-slate-900 border-b pb-2 flex items-center gap-2">
                    <span>✝️</span> Estatística do Corpo Ministerial & Obreiros
                </h3>
                <div class="grid grid-cols-2 gap-3">
                    {% for cg, qtd in demografia.cargos.items() %}
                    <div class="p-3 bg-slate-50 border rounded-xl flex justify-between items-center">
                        <div>
                            <span class="font-bold text-slate-800 block">{{ cg }}</span>
                            <span class="text-[10px] text-slate-400">Serviço Ministerial</span>
                        </div>
                        <span class="text-base font-black text-indigo-950">{{ qtd }}</span>
                    </div>
                    {% else %}
                    <p class="text-slate-400 italic">Nenhum obreiro registado.</p>
                    {% endfor %}
                </div>
            </div>
        </div>
        {% endif %}

        <!-- ========================================================= -->
        <!-- ABA: ACTOS ECLESIÁSTICOS (CASAMENTOS & ÓBITOS)            -->
        <!-- ========================================================= -->
        {% if aba_ativa == 'actos' %}
        <div class="bg-gradient-to-r from-pink-950 via-slate-900 to-slate-900 text-white p-6 rounded-3xl shadow mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
                <div class="inline-flex items-center gap-2 bg-pink-500/20 text-pink-300 px-3 py-1 rounded-full text-[10px] font-black uppercase mb-1 border border-pink-400/30">
                    <span>💒</span> REGISTO DE ACTOS PASTORAIS & NOTARIAIS
                </div>
                <h2 class="text-2xl font-black">Registo de Casamentos & Registo de Óbitos</h2>
                <p class="text-xs text-pink-200 mt-0.5">Gestão solene dos matrimónios e registo de condolências da membresia</p>
            </div>
            <div class="flex gap-3">
                <a href="/secretaria/relatorio-anual" target="_blank" class="px-4 py-2 bg-amber-500 hover:bg-amber-600 text-slate-950 font-black rounded-xl text-xs shadow flex items-center gap-1.5">
                    <span>📄</span><span>Ver no Relatório Anual Oficial</span>
                </a>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 text-xs">
            <div class="space-y-4">
                <div class="bg-white p-6 rounded-2xl shadow-sm border-2 border-pink-200 space-y-4">
                    <h3 class="font-black text-sm uppercase text-pink-950 border-b pb-2 flex items-center gap-2">
                        <span>💍</span> Registar Casamento Celebrado
                    </h3>
                    <form action="/actos/casamento/novo" method="POST" class="space-y-3">
                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <label class="block font-bold text-slate-700 mb-1">Categoria *</label>
                                <select name="tipo" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-bold">
                                    <option value="Jovens">Casamento de Jovens</option>
                                    <option value="Adultos">Casamento de Adultos</option>
                                </select>
                            </div>
                            <div>
                                <label class="block font-bold text-slate-700 mb-1">Data da Cerimónia *</label>
                                <input type="date" name="data_casamento" required class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-bold">
                            </div>
                        </div>
                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <label class="block font-bold text-slate-700 mb-1">Nome do Noivo *</label>
                                <input type="text" name="noivo" required placeholder="Nome completo" class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                            </div>
                            <div>
                                <label class="block font-bold text-slate-700 mb-1">Nome da Noiva *</label>
                                <input type="text" name="noiva" required placeholder="Nome completo" class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                            </div>
                        </div>
                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <label class="block font-bold text-slate-700 mb-1">Pastor / Ministro Oficiante</label>
                                <input type="text" name="ministro" placeholder="Pr. ..." class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                            </div>
                            <div>
                                <label class="block font-bold text-slate-700 mb-1">Regime / Certidão Civil</label>
                                <input type="text" name="certidao" placeholder="Nº Registo Civil / Assento" class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                            </div>
                        </div>
                        <button type="submit" class="w-full py-3 bg-pink-700 hover:bg-pink-800 text-white font-black rounded-xl shadow cursor-pointer transition">
                            💍 Gravar Registo de Casamento
                        </button>
                    </form>
                </div>

                <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200">
                    <h4 class="font-extrabold text-xs text-slate-800 mb-3 border-b pb-2 flex justify-between items-center">
                        <span>📋 Casamentos Registados</span>
                        <span class="bg-pink-100 text-pink-900 px-2.5 py-0.5 rounded-full font-black">{{ casamentos|length }}</span>
                    </h4>
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-xs">
                            <thead>
                                <tr class="border-b text-slate-500 font-bold">
                                    <th class="py-2 px-1">Data</th>
                                    <th class="py-2 px-1">Noivos</th>
                                    <th class="py-2 px-1">Tipo</th>
                                    <th class="py-2 px-1 text-right">Ação</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for cs in casamentos %}
                                <tr class="border-b hover:bg-slate-50">
                                    <td class="py-2.5 px-1 font-semibold">{{ cs.data_casamento }}</td>
                                    <td class="py-2.5 px-1">
                                        <div class="font-bold text-slate-900">{{ cs.noivo }} & {{ cs.noiva }}</div>
                                        <div class="text-[10px] text-slate-400">Oficiante: {{ cs.ministro or 'Pastor' }}</div>
                                    </td>
                                    <td class="py-2.5 px-1"><span class="bg-pink-50 text-pink-800 px-2 py-0.5 rounded font-bold text-[10px]">{{ cs.tipo }}</span></td>
                                    <td class="py-2.5 px-1 text-right"><a href="/actos/casamento/remover/{{ cs.id }}" onclick="return confirm('Excluir?')" class="text-rose-500 hover:text-rose-700 font-bold text-xs">Excluir</a></td>
                                </tr>
                                {% else %}
                                <tr><td colspan="4" class="py-6 text-center text-slate-400 italic">Nenhum casamento registado no período.</td></tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div class="space-y-4">
                <div class="bg-white p-6 rounded-2xl shadow-sm border-2 border-slate-300 space-y-4">
                    <h3 class="font-black text-sm uppercase text-slate-900 border-b pb-2 flex items-center gap-2">
                        <span>🕊️</span> Registar Óbito / Falecimento
                    </h3>
                    <form action="/actos/obito/novo" method="POST" class="space-y-3">
                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <label class="block font-bold text-slate-700 mb-1">Nome do Irmão(ã) Falecido *</label>
                                <input type="text" name="nome_falecido" required placeholder="Nome completo" class="w-full h-10 px-3 border rounded-xl bg-slate-50 font-bold">
                            </div>
                            <div>
                                <label class="block font-bold text-slate-700 mb-1">Género / Sexo *</label>
                                <select name="genero" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-bold">
                                    <option value="Masculino">Homem</option>
                                    <option value="Feminino">Mulher</option>
                                </select>
                            </div>
                        </div>
                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <label class="block font-bold text-slate-700 mb-1">Categoria Eclesiástica *</label>
                                <select name="categoria" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-bold text-indigo-950">
                                    <option value="Baptizados">Baptizado Adulto</option>
                                    <option value="Juventude">Juventude</option>
                                    <option value="Boa Esperança">Boa Esperança (Criança)</option>
                                    <option value="Novos Convertidos">Novo Convertido</option>
                                    <option value="Diáconos">Diácono / Diaconisa</option>
                                    <option value="Evangelistas">Evangelista</option>
                                    <option value="Presbíteros">Presbítero</option>
                                    <option value="Pastores">Pastor</option>
                                    <option value="Mães Pastoras">Mãe Pastora</option>
                                </select>
                            </div>
                            <div>
                                <label class="block font-bold text-slate-700 mb-1">Data do Falecimento *</label>
                                <input type="date" name="data_falecimento" required class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-bold">
                            </div>
                        </div>
                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <label class="block font-bold text-slate-700 mb-1">Local do Funeral / Cemitério</label>
                                <input type="text" name="local_funeral" placeholder="Ex: Chicuque / Maxixe" class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                            </div>
                            <div>
                                <label class="block font-bold text-slate-700 mb-1">Contacto da Família</label>
                                <input type="text" name="contacto_familia" placeholder="+258..." class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                            </div>
                        </div>
                        <button type="submit" class="w-full py-3 bg-slate-800 hover:bg-slate-900 text-white font-black rounded-xl shadow cursor-pointer transition">
                            🕊️ Gravar Registo de Óbito
                        </button>
                    </form>
                </div>

                <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200">
                    <h4 class="font-extrabold text-xs text-slate-800 mb-3 border-b pb-2 flex justify-between items-center">
                        <span>📋 Registo de Óbitos no Ano</span>
                        <span class="bg-slate-200 text-slate-800 px-2.5 py-0.5 rounded-full font-black">{{ obitos|length }}</span>
                    </h4>
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-xs">
                            <thead>
                                <tr class="border-b text-slate-500 font-bold">
                                    <th class="py-2 px-1">Data</th>
                                    <th class="py-2 px-1">Falecido</th>
                                    <th class="py-2 px-1">Categoria</th>
                                    <th class="py-2 px-1 text-right">Ação</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for ob in obitos %}
                                <tr class="border-b hover:bg-slate-50">
                                    <td class="py-2.5 px-1 font-semibold">{{ ob.data_falecimento }}</td>
                                    <td class="py-2.5 px-1">
                                        <div class="font-bold text-slate-900">{{ ob.nome_falecido }}</div>
                                        <div class="text-[10px] text-slate-400">Funeral: {{ ob.local_funeral or '---' }}</div>
                                    </td>
                                    <td class="py-2.5 px-1"><span class="bg-slate-100 text-slate-800 px-2 py-0.5 rounded font-bold text-[10px]">{{ ob.categoria }}</span></td>
                                    <td class="py-2.5 px-1 text-right"><a href="/actos/obito/remover/{{ ob.id }}" onclick="return confirm('Excluir?')" class="text-rose-500 hover:text-rose-700 font-bold text-xs">Excluir</a></td>
                                </tr>
                                {% else %}
                                <tr><td colspan="4" class="py-6 text-center text-slate-400 italic">Nenhum óbito registado no período. Graças a Deus!</td></tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- ========================================================= -->
        <!-- ABA 1: MEMBROS & RELATÓRIOS OFICIAIS                     -->
        <!-- ========================================================= -->
        {% if aba_ativa == 'membros' %}
        <div class="bg-indigo-900 text-white p-5 rounded-2xl shadow mb-6 flex justify-between items-center">
            <div>
                <h2 class="text-xl font-extrabold">👥 Cadastro Geral de Membresia</h2>
                <p class="text-xs text-indigo-200 mt-1">Registo oficial com geração automática de credenciais e certificados</p>
            </div>
            <a href="/membros/relatorio-geral" target="_blank" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl text-xs shadow flex items-center gap-2">
                📄 Gerar Livro Geral Completo (A4 / PDF)
            </a>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div class="lg:col-span-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">➕ Cadastrar Ficha Oficial</h3>
                <form action="/membros/novo" method="POST" class="space-y-3 text-xs">
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Nome Completo *</label>
                        <input type="text" name="nome" required placeholder="Nome completo do membro" class="w-full h-10 px-3 border rounded-xl bg-slate-50 font-bold">
                    </div>
                    <div class="grid grid-cols-2 gap-2">
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">BI / Cédula</label>
                            <input type="text" name="bi" placeholder="Nº de Documento" class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                        </div>
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Género / Sexo *</label>
                            <select name="genero" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-bold text-slate-800">
                                <option value="Masculino">Homem (Masculino)</option>
                                <option value="Feminino">Mulher (Feminino)</option>
                            </select>
                        </div>
                    </div>
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Contacto / WhatsApp</label>
                        <input type="text" name="contacto" placeholder="+258..." class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                    </div>
                    <div class="grid grid-cols-3 gap-2">
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Estado Civil *</label>
                            <select name="estado_civil" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-bold text-indigo-900">
                                {% for op in opcoes.get('estado_civil', []) %}
                                <option value="{{ op.valor }}">{{ op.valor }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Zona</label>
                            <select name="zona" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-semibold">
                                {% for op in opcoes.get('zona', []) %}<option value="{{ op.valor }}">{{ op.valor }}</option>{% endfor %}
                            </select>
                        </div>
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Célula</label>
                            <select name="celula" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-semibold">
                                {% for op in opcoes.get('celula', []) %}<option value="{{ op.valor }}">{{ op.valor }}</option>{% endfor %}
                            </select>
                        </div>
                    </div>
                    <div class="grid grid-cols-2 gap-2">
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Cargo Ministerial</label>
                            <select name="cargo" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-semibold">
                                {% for op in opcoes.get('cargo', []) %}<option value="{{ op.valor }}">{{ op.valor }}</option>{% endfor %}
                            </select>
                        </div>
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Departamento</label>
                            <select name="departamento" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-semibold">
                                {% for op in opcoes.get('departamento', []) %}<option value="{{ op.valor }}">{{ op.valor }}</option>{% endfor %}
                            </select>
                        </div>
                    </div>
                    <div class="grid grid-cols-2 gap-2">
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Ano Conversão</label>
                            <input type="number" name="ano_conversao" placeholder="Ex: 2021" class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                        </div>
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Data Batismo</label>
                            <input type="date" name="data_batismo" class="w-full h-10 px-2 border rounded-xl bg-emerald-50 border-emerald-300">
                        </div>
                    </div>
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Residência (Bairro / Local)</label>
                        <input type="text" name="local_residencia" placeholder="Ex: Chicuque - Perto do Hospital" class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                    </div>
                    <button type="submit" class="w-full py-3 bg-emerald-700 hover:bg-emerald-800 text-white font-bold rounded-xl shadow cursor-pointer transition">
                        Gravar Ficha de Membro
                    </button>
                </form>
            </div>

            <div class="lg:col-span-8 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">📋 Membros Registados ({{ membros|length }})</h3>
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse text-xs">
                        <thead>
                            <tr class="border-b-2 border-slate-200 text-slate-500">
                                <th class="py-2 px-2">Membro</th>
                                <th class="py-2 px-2">Zona & Célula</th>
                                <th class="py-2 px-2">Cargo & Depto</th>
                                <th class="py-2 px-2">Batismo</th>
                                <th class="py-2 px-2 text-right">Documentos</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for m in membros %}
                            <tr class="border-b border-slate-100 hover:bg-slate-50">
                                <td class="py-2.5 px-2">
                                    <div class="font-bold text-slate-900">{{ m.nome }}</div>
                                    <div class="text-[10px] text-slate-400">{{ m.genero or 'Homem' }} • {{ m.estado_civil or '---' }} • {{ m.local_residencia or m.bairro or '---' }}</div>
                                </td>
                                <td class="py-2.5 px-2 text-slate-600">
                                    <div class="font-semibold">{{ m.zona or 'Zona Geral' }}</div>
                                    <div class="text-[10px] text-slate-400">{{ m.celula or '---' }}</div>
                                </td>
                                <td class="py-2.5 px-2">
                                    <span class="bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded font-bold text-[11px]">{{ m.cargo }}</span>
                                    <div class="text-[10px] text-slate-500 mt-0.5">{{ m.departamento }}</div>
                                </td>
                                <td class="py-2.5 px-2">
                                    {% if m.data_batismo %}
                                    <span class="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full font-bold text-[10px]">🌊 {{ m.data_batismo }}</span>
                                    {% else %}
                                    <span class="text-slate-400 text-[10px] italic">Não Batizado</span>
                                    {% endif %}
                                </td>
                                <td class="py-2.5 px-2 text-right space-x-1">
                                    <a href="/membros/{{ m.id }}/cartao" target="_blank" class="px-2 py-1 bg-indigo-600 hover:bg-indigo-700 text-white rounded font-bold text-[10px] shadow inline-block" title="Cartão de Membro">🪪 Cartão</a>
                                    {% if m.data_batismo %}
                                    <a href="/membros/{{ m.id }}/batismo" target="_blank" class="px-2 py-1 bg-emerald-600 hover:bg-emerald-700 text-white rounded font-bold text-[10px] shadow inline-block" title="Certificado de Batismo">🌊 Batismo</a>
                                    {% endif %}
                                    <a href="/membros/{{ m.id }}/recomendacao" target="_blank" class="px-2 py-1 bg-amber-600 hover:bg-amber-700 text-white rounded font-bold text-[10px] shadow inline-block" title="Carta de Recomendação">📜 Carta</a>
                                </td>
                            </tr>
                            {% else %}
                            <tr><td colspan="5" class="py-8 text-center text-slate-400">Nenhum membro registado.</td></tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- ========================================================= -->
        <!-- ABA 2: SECRETARIA & PLANIFICAÇÃO (COM BALANÇO ANUAL)      -->
        <!-- ========================================================= -->
        {% if aba_ativa == 'secretaria' %}
        <div class="bg-indigo-900 text-white p-5 rounded-2xl shadow mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
                <h2 class="text-xl font-extrabold">📋 Secretaria & Planificação de Actividades</h2>
                <p class="text-xs text-indigo-200 mt-0.5">Gestão de cronograma, execução de metas e prestação oficial de contas</p>
            </div>
            <div class="flex flex-wrap items-center gap-2.5">
                <a href="/secretaria/balanco" class="px-3.5 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-black rounded-xl text-xs shadow flex items-center gap-1.5 transition">
                    <span>🎯</span><span>Balanço Anual & Questionamentos</span>
                </a>
                <a href="/secretaria/relatorio-anual" target="_blank" class="px-3.5 py-2.5 bg-amber-500 hover:bg-amber-600 text-slate-950 font-black rounded-xl text-xs shadow flex items-center gap-1.5 transition">
                    <span>📄</span><span>Emitir Relatório Oficial (2026)</span>
                </a>
            </div>
        </div>

        {% if plano_relatar %}
        <div class="bg-amber-50 border-2 border-amber-300 p-6 rounded-2xl shadow mb-6">
            <h3 class="font-extrabold text-base text-amber-900 mb-3">📝 Prestação de Contas: {{ plano_relatar.actividade }}</h3>
            <form action="/secretaria/planificacao/relatar" method="POST" class="space-y-3.5 text-xs">
                <input type="hidden" name="plano_id" value="{{ plano_relatar.id }}">
                <div><label class="block font-bold text-slate-700 mb-1">Feedback do que foi realizado *</label><textarea name="feedback" required rows="3" class="w-full p-3 border rounded-xl bg-white"></textarea></div>
                <div class="grid grid-cols-4 gap-3 bg-white p-3 rounded-xl border border-amber-200">
                    <div><label class="block text-slate-500">Homens</label><input type="number" name="participantes_homens" value="0" min="0" class="w-full h-9 px-2 border rounded font-bold"></div>
                    <div><label class="block text-slate-500">Mulheres</label><input type="number" name="participantes_mulheres" value="0" min="0" class="w-full h-9 px-2 border rounded font-bold"></div>
                    <div><label class="block text-slate-500">Jovens</label><input type="number" name="participantes_jovens" value="0" min="0" class="w-full h-9 px-2 border rounded font-bold"></div>
                    <div><label class="block text-slate-500">Crianças</label><input type="number" name="participantes_criancas" value="0" min="0" class="w-full h-9 px-2 border rounded font-bold"></div>
                </div>
                <div class="grid grid-cols-2 gap-3 pt-2">
                    <div><label class="block font-semibold text-slate-700 mb-1">Data Real</label><input type="date" name="data_execucao" required class="w-full h-10 px-2 border rounded-xl bg-white"></div>
                    <div class="flex items-end"><button type="submit" class="w-full h-10 bg-emerald-700 hover:bg-emerald-800 text-white font-bold rounded-xl shadow cursor-pointer">✅ Concluir Feedback</button></div>
                </div>
            </form>
        </div>
        {% endif %}

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div class="lg:col-span-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">📌 Planificar Actividade</h3>
                <form action="/secretaria/planificacao/nova" method="POST" class="space-y-3.5 text-xs">
                    <div><label class="block font-semibold mb-1">Departamento</label><select name="departamento" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-bold">{% for op in opcoes.get('departamento', []) %}<option value="{{ op.valor }}">{{ op.valor }}</option>{% endfor %}</select></div>
                    <div><label class="block font-semibold mb-1">Tipo de Evento</label><select name="tipo_evento" class="w-full h-10 px-2 border rounded-xl bg-slate-50">{% for op in opcoes.get('tipo_evento', []) %}<option value="{{ op.valor }}">{{ op.valor }}</option>{% endfor %}</select></div>
                    <div><label class="block font-semibold mb-1">Nome Actividade *</label><input type="text" name="actividade" required class="w-full h-10 px-3 border rounded-xl bg-slate-50"></div>
                    <div class="grid grid-cols-2 gap-2">
                        <div><label class="block font-semibold mb-1">Data Prevista</label><input type="date" name="data_prevista" required class="w-full h-10 px-2 border rounded-xl bg-slate-50"></div>
                        <div><label class="block font-semibold mb-1">Frequência</label><select name="frequencia" class="w-full h-10 px-2 border rounded-xl bg-slate-50"><option value="Pontual / Única">Pontual / Única</option><option value="Semanal">Semanal</option><option value="Mensal">Mensal</option></select></div>
                    </div>
                    <div><label class="block font-semibold mb-1">Responsável</label><input type="text" name="responsavel" class="w-full h-10 px-3 border rounded-xl bg-slate-50"></div>
                    <button type="submit" class="w-full py-3 bg-indigo-800 hover:bg-indigo-900 text-white font-bold rounded-xl shadow cursor-pointer">Gravar Planificação</button>
                </form>
            </div>
            <div class="lg:col-span-8 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">📊 Cronograma ({{ planificacoes|length }})</h3>
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse text-xs">
                        <thead><tr class="border-b-2 border-slate-200 text-slate-500"><th class="py-2.5 px-2">Actividade</th><th class="py-2.5 px-2">Data</th><th class="py-2.5 px-2">Status</th><th class="py-2.5 px-2 text-right">Ação</th></tr></thead>
                        <tbody>
                            {% for p in planificacoes %}
                            <tr class="border-b border-slate-100 hover:bg-slate-50">
                                <td class="py-3 px-2 font-bold text-indigo-900">{{ p.actividade }}<div class="text-[11px] text-slate-500">{{ p.departamento }}</div></td>
                                <td class="py-3 px-2">{{ p.data_prevista }}</td>
                                <td class="py-3 px-2">{% if p.status == 'Executado' %}<span class="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-bold">✅ Executado</span>{% else %}<span class="bg-blue-100 text-blue-800 px-2 py-0.5 rounded font-bold">Planeado</span>{% endif %}</td>
                                <td class="py-3 px-2 text-right">{% if p.status != 'Executado' %}<a href="/?aba=secretaria&relatar_id={{ p.id }}" class="px-2.5 py-1 bg-amber-600 text-white rounded font-bold">📝 Relatar</a>{% else %}<span class="text-emerald-700 font-bold">Concluído</span>{% endif %}</td>
                            </tr>
                            {% else %}
                            <tr><td colspan="4" class="py-8 text-center text-slate-400">Nenhum plano registado.</td></tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- ========================================================= -->
        <!-- ABA 3: CULTOS COM GRELHA DISCRIMINADA COMPLETA            -->
        <!-- ========================================================= -->
        {% if aba_ativa == 'cultos' %}
        <div class="bg-indigo-900 text-white p-5 rounded-2xl shadow mb-6">
            <h2 class="text-xl font-extrabold">⛪ Registo de Cultos & Estatística Completa de Presenças</h2>
            <p class="text-xs text-indigo-200 mt-1">Estatística oficial discriminada por género em todas as faixas etárias</p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div class="lg:col-span-5 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">📝 Lançar Culto</h3>
                <form action="/cultos/novo" method="POST" class="space-y-3 text-xs">
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block font-semibold mb-1">Data *</label>
                            <input type="date" name="data_culto" required class="w-full h-10 px-2 border rounded-xl bg-slate-50">
                        </div>
                        <div>
                            <label class="block font-semibold mb-1">Tipo de Culto</label>
                            <select name="tipo_culto" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-bold">
                                {% for op in opcoes.get('tipo_culto', []) %}<option value="{{ op.valor }}">{{ op.valor }}</option>{% endfor %}
                            </select>
                        </div>
                    </div>

                    <div class="p-3 bg-slate-50 rounded-xl border border-slate-200 space-y-2">
                        <div class="font-bold text-slate-700 text-[11px] uppercase tracking-wider">Assistência Discriminada por Género</div>
                        
                        <div class="grid grid-cols-2 gap-2">
                            <div><label class="text-slate-500 font-semibold">👨 Homens Adultos</label><input type="number" name="homens_adultos" value="0" min="0" oninput="somarCulto()" class="campo-soma w-full h-8 px-2 border rounded bg-white font-bold"></div>
                            <div><label class="text-slate-500 font-semibold">👩 Mulheres Adultas</label><input type="number" name="mulheres_adultas" value="0" min="0" oninput="somarCulto()" class="campo-soma w-full h-8 px-2 border rounded bg-white font-bold"></div>
                            <div><label class="text-slate-500 font-semibold">👦 Jovens (Rapazes)</label><input type="number" name="jovens_rapazes" value="0" min="0" oninput="somarCulto()" class="campo-soma w-full h-8 px-2 border rounded bg-white font-bold"></div>
                            <div><label class="text-slate-500 font-semibold">👧 Jovens (Moças)</label><input type="number" name="jovens_mocas" value="0" min="0" oninput="somarCulto()" class="campo-soma w-full h-8 px-2 border rounded bg-white font-bold"></div>
                            
                            <div class="bg-blue-50/60 p-1.5 rounded-lg border border-blue-200">
                                <label class="text-blue-900 font-bold text-[11px] block">👶 Crianças (Meninos)</label>
                                <input type="number" name="criancas_meninos" value="0" min="0" oninput="somarCulto()" class="campo-soma w-full h-8 px-2 border border-blue-300 rounded bg-white font-bold text-blue-900">
                            </div>
                            <div class="bg-pink-50/60 p-1.5 rounded-lg border border-pink-200">
                                <label class="text-pink-900 font-bold text-[11px] block">👧 Crianças (Meninas)</label>
                                <input type="number" name="criancas_meninas" value="0" min="0" oninput="somarCulto()" class="campo-soma w-full h-8 px-2 border border-pink-300 rounded bg-white font-bold text-pink-900">
                            </div>

                            <div><label class="text-slate-500">Visitantes (H)</label><input type="number" name="visitantes_homens" value="0" min="0" oninput="somarCulto()" class="campo-soma w-full h-8 px-2 border rounded bg-white"></div>
                            <div><label class="text-slate-500">Visitantes (M)</label><input type="number" name="visitantes_mulheres" value="0" min="0" oninput="somarCulto()" class="campo-soma w-full h-8 px-2 border rounded bg-white"></div>
                        </div>

                        <div class="grid grid-cols-2 gap-2 pt-2 border-t">
                            <div>
                                <label class="font-bold text-amber-700">🔥 Vidas no Altar (Apelos)</label>
                                <input type="number" name="apelos" value="0" min="0" class="w-full h-9 px-2 border-2 border-amber-300 rounded bg-amber-50 font-bold text-center">
                            </div>
                            <div>
                                <label class="font-bold text-blue-800">📊 Total de Presentes</label>
                                <input type="number" id="total_presentes" name="total_presentes" value="0" readonly class="w-full h-9 px-2 border-2 border-blue-400 rounded bg-blue-50 font-extrabold text-center text-blue-900 text-sm">
                            </div>
                        </div>
                    </div>

                    <div class="grid grid-cols-2 gap-3">
                        <div><label class="block font-semibold mb-1">Pregador</label><input type="text" name="pregador" placeholder="Nome do Pregador" class="w-full h-10 px-3 border rounded-xl bg-slate-50"></div>
                        <div><label class="block font-semibold mb-1">Tema / Texto</label><input type="text" name="tema_mensagem" placeholder="Ex: Isaías 40:31" class="w-full h-10 px-3 border rounded-xl bg-slate-50"></div>
                    </div>

                    <button type="submit" class="w-full py-3 bg-indigo-700 hover:bg-indigo-800 text-white font-bold rounded-xl shadow cursor-pointer">
                        Gravar Relatório de Culto
                    </button>
                </form>
            </div>

            <div class="lg:col-span-7 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">📚 Histórico de Cultos ({{ cultos|length }})</h3>
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs">
                        <thead>
                            <tr class="border-b-2 border-slate-200 text-slate-500">
                                <th class="py-2.5 px-2">Data</th>
                                <th class="py-2.5 px-2">Culto & Pregador</th>
                                <th class="py-2.5 px-2 text-center">Crianças (M/F)</th>
                                <th class="py-2.5 px-2 text-center">Total</th>
                                <th class="py-2.5 px-2 text-center">Apelos</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for c in cultos %}
                            <tr class="border-b border-slate-100 hover:bg-slate-50">
                                <td class="py-3 px-2 font-semibold">{{ c.data_culto }}</td>
                                <td class="py-3 px-2 font-bold text-slate-800">{{ c.tipo_culto }}<div class="text-[11px] text-slate-400">{{ c.pregador or '---' }}</div></td>
                                <td class="py-3 px-2 text-center font-bold text-slate-600">
                                    👦 {{ c.criancas_meninos or 0 }} | 👧 {{ c.criancas_meninas or 0 }}
                                </td>
                                <td class="py-3 px-2 text-center font-black text-blue-900 bg-blue-50/50 rounded-lg">{{ c.total_presentes }}</td>
                                <td class="py-3 px-2 text-center font-black text-amber-700">{{ c.apelos }}</td>
                            </tr>
                            {% else %}
                            <tr><td colspan="5" class="py-8 text-center text-slate-400">Nenhum culto registado.</td></tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- ========================================================= -->
        <!-- ABA 4: NOVOS CONVERTIDOS                                  -->
        <!-- ========================================================= -->
        {% if aba_ativa == 'convertidos' %}
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div class="lg:col-span-5 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">🌱 Registar Novo Convertido</h3>
                <form action="/convertidos/novo" method="POST" class="space-y-3.5 text-xs">
                    <div><label class="block font-semibold mb-1">Nome Completo *</label><input type="text" name="nome" required class="w-full h-11 px-3 border rounded-xl bg-blue-50/50"></div>
                    <div><label class="block font-semibold mb-1">Contacto</label><input type="text" name="telefone" class="w-full h-11 px-3 border rounded-xl bg-blue-50/50"></div>
                    <div><label class="block font-semibold mb-1">Data Decisão</label><input type="date" name="data_decisao" required class="w-full h-11 px-3 border rounded-xl bg-white"></div>
                    <div><label class="block font-semibold mb-1">Bairro</label><input type="text" name="bairro" class="w-full h-11 px-3 border rounded-xl bg-blue-50/50"></div>
                    <button type="submit" class="w-full py-3.5 bg-emerald-700 hover:bg-emerald-800 text-white font-bold rounded-xl shadow cursor-pointer">Registar para Discipulado</button>
                </form>
            </div>
            <div class="lg:col-span-7 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">Acompanhamento Espiritual ({{ convertidos|length }})</h3>
                <table class="w-full text-left text-xs">
                    <thead><tr class="border-b-2 border-slate-200 text-slate-500"><th class="py-3 px-3">Nome</th><th class="py-3 px-3">Contacto</th><th class="py-3 px-3">Bairro</th></tr></thead>
                    <tbody>
                        {% for c in convertidos %}
                        <tr class="border-b border-slate-100 hover:bg-slate-50"><td class="py-3 px-3 font-bold">{{ c.nome }}</td><td class="py-3 px-3">{{ c.telefone or '---' }}</td><td class="py-3 px-3">{{ c.bairro or '---' }}</td></tr>
                        {% else %}
                        <tr><td colspan="3" class="py-8 text-center text-slate-400">Nenhum convertido registado.</td></tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
        {% endif %}

        <!-- ========================================================= -->
        <!-- ABA 5: DASHBOARD FINANCEIRO COMPLETO (RESTAURADA 100%)    -->
        <!-- ========================================================= -->
        {% if aba_ativa == 'financas' and (usuario_logado.perfil != 'secretario') %}
        <div class="bg-emerald-950 text-white p-6 rounded-2xl shadow mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
                <h2 class="text-2xl font-black">📊 Dashboard Financeiro & Transparência</h2>
                <p class="text-xs text-emerald-300 mt-1">Visão analítica completa das finanças da congregação (Sede Chicuque)</p>
            </div>
            <div class="text-right flex flex-wrap items-center gap-3">
                <div class="bg-white/10 px-3 py-1.5 rounded-xl border border-white/10 text-right">
                    <span class="text-[9px] uppercase font-bold text-amber-300 block">💵 Caixa Físico</span>
                    <span class="text-sm font-black text-white">{{ "%.2f"|format(kpis.saldo_caixa_fisico or 0) }} MT</span>
                </div>
                <div class="bg-white/10 px-3 py-1.5 rounded-xl border border-white/10 text-right">
                    <span class="text-[9px] uppercase font-bold text-blue-300 block">🏦 Conta Bancária</span>
                    <span class="text-sm font-black text-white">{{ "%.2f"|format(kpis.saldo_banco or 0) }} MT</span>
                </div>
                <div>
                    <span class="text-[10px] uppercase font-bold text-emerald-300 block">Saldo Geral Total</span>
                    <span class="text-2xl font-black text-white">{{ "%.2f"|format(kpis.saldo_caixa) }} MT</span>
                </div>
                {% if usuario_logado.perfil in ['tesoureiro', 'admin'] %}
                <a href="/?aba=tesouraria" class="px-3.5 py-2 bg-amber-500 hover:bg-amber-600 text-slate-950 font-black rounded-xl text-xs shadow flex items-center gap-1.5">
                    <span>🔐</span><span>Lançamentos</span>
                </a>
                {% endif %}
            </div>
        </div>

        <!-- 3 CARDS ANALÍTICOS SEPARADOS: IGREJA LOCAL, IGREJA MÃE E DEPARTAMENTOS -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-5 mb-8 text-xs">
            <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200">
                <div class="font-extrabold text-slate-800 uppercase flex items-center justify-between border-b pb-2 mb-2">
                    <span>🏛️ Igreja Geral (Local)</span>
                    <span class="text-[10px] bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-bold">Chicuque</span>
                </div>
                <div class="flex justify-between items-center text-emerald-700 font-bold">
                    <span>Entradas Locais:</span>
                    <span>+ {{ "%.2f"|format(kpis.geral_in or 0) }} MT</span>
                </div>
                <div class="flex justify-between items-center text-rose-700 font-bold mt-1">
                    <span>Despesas Locais:</span>
                    <span>- {{ "%.2f"|format(kpis.geral_out or 0) }} MT</span>
                </div>
                <div class="border-t pt-2 mt-2 flex justify-between items-center font-black text-slate-900">
                    <span>Saldo Operacional:</span>
                    <span>{{ "%.2f"|format((kpis.geral_in or 0) - (kpis.geral_out or 0)) }} MT</span>
                </div>
            </div>

            <div class="bg-white p-5 rounded-2xl shadow-sm border border-amber-200 bg-amber-50/30">
                <div class="font-extrabold text-amber-950 uppercase flex items-center justify-between border-b border-amber-200 pb-2 mb-2">
                    <span>🏢 Igreja Mãe (Sede)</span>
                    <span class="text-[10px] bg-amber-200 text-amber-950 px-2 py-0.5 rounded font-black">Remessas</span>
                </div>
                <div class="flex justify-between items-center text-blue-800 font-bold">
                    <span>Apoio Recebido:</span>
                    <span>+ {{ "%.2f"|format(kpis.mae_in or 0) }} MT</span>
                </div>
                <div class="flex justify-between items-center text-rose-700 font-bold mt-1">
                    <span>Remessas / Dízimo Dízimos:</span>
                    <span>- {{ "%.2f"|format(kpis.mae_out or 0) }} MT</span>
                </div>
                <div class="border-t border-amber-200 pt-2 mt-2 flex justify-between items-center font-black text-amber-950">
                    <span>Balanço c/ a Sede:</span>
                    <span>{{ "%.2f"|format((kpis.mae_in or 0) - (kpis.mae_out or 0)) }} MT</span>
                </div>
            </div>

            <div class="bg-white p-5 rounded-2xl shadow-sm border border-indigo-200 bg-indigo-50/30">
                <div class="font-extrabold text-indigo-950 uppercase flex items-center justify-between border-b border-indigo-200 pb-2 mb-2">
                    <span>👥 Departamentos</span>
                    <span class="text-[10px] bg-indigo-200 text-indigo-950 px-2 py-0.5 rounded font-black">Fundos</span>
                </div>
                <div class="flex justify-between items-center text-emerald-700 font-bold">
                    <span>Arrecadação Deptos:</span>
                    <span>+ {{ "%.2f"|format(kpis.depto_in or 0) }} MT</span>
                </div>
                <div class="flex justify-between items-center text-rose-700 font-bold mt-1">
                    <span>Gastos Deptos:</span>
                    <span>- {{ "%.2f"|format(kpis.depto_out or 0) }} MT</span>
                </div>
                <div class="border-t border-indigo-200 pt-2 mt-2 flex justify-between items-center font-black text-indigo-950">
                    <span>Fundo Departamental:</span>
                    <span>{{ "%.2f"|format((kpis.depto_in or 0) - (kpis.depto_out or 0)) }} MT</span>
                </div>
            </div>
        </div>

        <!-- 4 CARDS DE RESUMO GERAL -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
            <div class="bg-white p-5 rounded-2xl shadow-sm border-l-4 border-emerald-500 border-slate-200">
                <div class="text-slate-500 text-xs font-bold uppercase">Entradas Totais</div>
                <div class="text-2xl font-black text-emerald-700 mt-1">+ {{ "%.2f"|format(kpis.total_entradas) }} MT</div>
                <div class="text-[11px] text-slate-400 mt-1">Dízimos e Ofertas</div>
            </div>
            <div class="bg-white p-5 rounded-2xl shadow-sm border-l-4 border-rose-500 border-slate-200">
                <div class="text-slate-500 text-xs font-bold uppercase">Saídas & Despesas</div>
                <div class="text-2xl font-black text-rose-700 mt-1">- {{ "%.2f"|format(kpis.total_saidas) }} MT</div>
                <div class="text-[11px] text-slate-400 mt-1">Taxa de consumo: {{ kpis.taxa_gasto }}%</div>
            </div>
            <div class="bg-white p-5 rounded-2xl shadow-sm border-l-4 border-indigo-500 border-slate-200">
                <div class="text-slate-500 text-xs font-bold uppercase">Total em Dízimos</div>
                <div class="text-2xl font-black text-indigo-900 mt-1">{{ "%.2f"|format(kpis.total_dizimos) }} MT</div>
                <div class="text-[11px] text-slate-400 mt-1">Fidelidade Ministerial</div>
            </div>
            <div class="bg-white p-5 rounded-2xl shadow-sm border-l-4 border-amber-500 border-slate-200">
                <div class="text-slate-500 text-xs font-bold uppercase">Missões & Obras</div>
                <div class="text-2xl font-black text-amber-700 mt-1">{{ "%.2f"|format(kpis.total_missoes) }} MT</div>
                <div class="text-[11px] text-slate-400 mt-1">Campanhas e Construção</div>
            </div>
        </div>

        <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 mb-8">
            <h3 class="font-bold text-sm text-slate-800 uppercase tracking-wider mb-4">📊 Distribuição por Categoria Financeira</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                {% for cat, val in kpis.categorias_caixa.items() %}
                <div class="p-3 bg-slate-50 rounded-xl border border-slate-200">
                    <div class="flex justify-between items-center mb-1.5 font-bold">
                        <span class="text-slate-700">{{ cat }}</span>
                        <span class="text-indigo-950 font-extrabold">{{ "%.2f"|format(val) }} MT</span>
                    </div>
                    <div class="w-full bg-slate-200 h-2 rounded-full overflow-hidden">
                        {% set perc = (val / kpis.total_entradas * 100)|int if kpis.total_entradas > 0 else 10 %}
                        <div class="bg-emerald-600 h-2 rounded-full" style="width: {{ [perc, 100]|min }}%"></div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>

        <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
            <h3 class="font-bold text-base mb-4 border-b pb-2">📋 Livro Razão de Movimentos ({{ caixa|length }} registos)</h3>
            <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse text-xs">
                    <thead>
                        <tr class="border-b-2 border-slate-200 text-slate-500">
                            <th class="py-2.5 px-2">Data</th>
                            <th class="py-2.5 px-2">Conta</th>
                            <th class="py-2.5 px-2">Tipo</th>
                            <th class="py-2.5 px-2">Categoria & Descrição</th>
                            <th class="py-2.5 px-2 text-right">Valor</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for cx in caixa %}
                        <tr class="border-b border-slate-100 hover:bg-slate-50">
                            <td class="py-3 px-2 text-slate-600">{{ cx.data_movimento }}</td>
                            <td class="py-3 px-2">
                                {% if 'banco' in (cx.conta or '')|lower %}
                                <span class="bg-blue-100 text-blue-900 px-2 py-0.5 rounded font-black text-[10px]">🏦 Banco</span>
                                {% else %}
                                <span class="bg-amber-100 text-amber-900 px-2 py-0.5 rounded font-black text-[10px]">💵 Caixa</span>
                                {% endif %}
                            </td>
                            <td class="py-3 px-2">
                                <span class="{% if cx.tipo == 'Entrada' %}bg-emerald-100 text-emerald-800{% else %}bg-rose-100 text-rose-800{% endif %} px-2.5 py-1 rounded-full font-bold text-[11px]">{{ cx.tipo }}</span>
                            </td>
                            <td class="py-3 px-2 font-bold">{{ cx.categoria }}<div class="text-[11px] text-slate-400 font-normal">{{ cx.descricao }}</div></td>
                            <td class="py-3 px-2 text-right font-extrabold {% if cx.tipo == 'Entrada' %}text-emerald-700{% else %}text-rose-700{% endif %}">
                                {{ "%.2f"|format(cx.valor or 0) }} MT
                            </td>
                        </tr>
                        {% else %}
                        <tr><td colspan="5" class="py-8 text-center text-slate-400">Nenhum movimento gravado.</td></tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
        {% endif %}

        <!-- ========================================================= -->
        <!-- ABA 6: CAIXA & TESOURARIA (EXCLUSIVO TESOURARIA E ADMIN)  -->
        <!-- ========================================================= -->
        {% if aba_ativa == 'tesouraria' and usuario_logado.perfil in ['tesoureiro', 'admin'] %}
        <div class="bg-amber-950 text-white p-6 rounded-2xl shadow mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
                <div class="inline-flex items-center gap-2 bg-amber-500/20 text-amber-300 px-3 py-1 rounded-full text-[10px] font-black uppercase mb-1 border border-amber-400/30">
                    <span>🔐</span> ACESSO RESTRITO • GABINETE DA TESOURARIA
                </div>
                <h2 class="text-2xl font-black">Lançamentos de Caixa & Movimentação Financeira</h2>
                <p class="text-xs text-amber-200 mt-0.5">Gestão separada: Igreja em Geral (Local), Igreja Mãe (Sede) e Departamentos</p>
            </div>
            <div class="flex items-center gap-3">
                <div class="bg-white/10 px-3.5 py-2 rounded-xl text-right border border-white/10">
                    <span class="text-[9px] uppercase font-bold text-amber-300 block">Caixa Físico</span>
                    <span class="text-sm font-black text-white">{{ "%.2f"|format(kpis.saldo_caixa_fisico or 0) }} MT</span>
                </div>
                <div class="bg-white/10 px-3.5 py-2 rounded-xl text-right border border-white/10">
                    <span class="text-[9px] uppercase font-bold text-blue-300 block">Conta Bancária</span>
                    <span class="text-sm font-black text-white">{{ "%.2f"|format(kpis.saldo_banco or 0) }} MT</span>
                </div>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div class="lg:col-span-5 bg-white p-6 rounded-2xl shadow-sm border-2 border-amber-300">
                <h3 class="font-extrabold text-base mb-4 border-b pb-2 text-amber-950 flex items-center gap-2">
                    <span>✍️</span> Lançar Entrada ou Saída de Valores
                </h3>
                
                <form action="/financas/caixa/novo" method="POST" class="space-y-4 text-xs">
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">Tipo de Movimento *</label>
                            <select id="tipo_movimento" name="tipo" onchange="atualizarFormularioTesouraria()" class="w-full h-11 px-2 border-2 border-slate-200 rounded-xl bg-slate-50 font-black text-sm">
                                <option value="Entrada">🟢 Entrada (+)</option>
                                <option value="Saída">🔴 Saída (-)</option>
                            </select>
                        </div>
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">Conta Financeira *</label>
                            <select name="conta" required class="w-full h-11 px-2 border-2 border-slate-200 rounded-xl bg-slate-50 font-black text-xs text-indigo-900">
                                <option value="Caixa Físico">💵 Caixa Físico (Numerário)</option>
                                <option value="Conta Bancária">🏦 Conta Bancária</option>
                            </select>
                        </div>
                    </div>

                    <div>
                        <label class="block font-bold text-slate-700 mb-1">Âmbito do Movimento (Onde entra / De onde sai) *</label>
                        <select id="destino_tipo" name="destino_tipo" onchange="atualizarFormularioTesouraria()" class="w-full h-11 px-3 border-2 border-indigo-300 rounded-xl bg-indigo-50/50 font-black text-xs text-indigo-950">
                            <option value="Igreja Geral">🏛️ 1. Igreja em Geral (Local / Sede Chicuque)</option>
                            <option value="Igreja Mãe">🏢 2. Igreja Mãe (Sede / Remessas)</option>
                            <option value="Departamento">👥 3. Departamentos da Igreja</option>
                        </select>
                    </div>

                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">Data da Operação *</label>
                            <input type="date" name="data_movimento" required class="w-full h-11 px-2 border-2 border-slate-200 rounded-xl bg-slate-50 font-bold">
                        </div>
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">Valor (MZN) *</label>
                            <input type="number" step="0.01" name="valor" required placeholder="Ex: 2500.00" class="w-full h-11 px-3 border-2 border-emerald-400 rounded-xl bg-emerald-50/50 font-black text-emerald-950 text-base">
                        </div>
                    </div>

                    <!-- ENTRADA NA IGREJA GERAL -->
                    <div id="box_entrada_geral" class="space-y-2 p-3.5 bg-emerald-50/70 rounded-xl border border-emerald-200">
                        <div class="font-black text-emerald-900 text-[10px] uppercase">Receita da Igreja Local (Sede Chicuque)</div>
                        <label class="block font-semibold text-slate-700 mb-1">Categoria de Entrada Local *</label>
                        <select name="categoria" class="w-full h-10 px-2 border rounded-xl bg-white font-bold text-slate-800">
                            {% for op in opcoes.get('categoria_caixa', []) %}
                            <option value="{{ op.valor }}">{{ op.valor }}</option>
                            {% endfor %}
                        </select>
                    </div>

                    <!-- ENTRADA DA IGREJA MÃE -->
                    <div id="box_entrada_mae" class="hidden space-y-2 p-3.5 bg-blue-50/70 rounded-xl border border-blue-200">
                        <div class="font-black text-blue-900 text-[10px] uppercase">Valores Recebidos da Igreja Mãe / Sede</div>
                        <label class="block font-semibold text-slate-700 mb-1">Tipo de Entrada da Igreja Mãe *</label>
                        <select name="categoria_entrada_mae" class="w-full h-10 px-2 border-2 border-blue-300 rounded-xl bg-white font-bold text-blue-950">
                            {% for op in opcoes.get('categoria_entrada_mae', []) %}
                            <option value="{{ op.valor }}">{{ op.valor }}</option>
                            {% else %}
                            <option value="Apoio / Subsídio da Igreja Mãe">Apoio / Subsídio da Igreja Mãe</option>
                            <option value="Fundo Missionário da Sede">Fundo Missionário da Sede</option>
                            {% endfor %}
                        </select>
                    </div>

                    <!-- ENTRADA EM DEPARTAMENTOS -->
                    <div id="box_entrada_depto" class="hidden space-y-3 p-3.5 bg-emerald-50/70 rounded-xl border border-emerald-200">
                        <div class="font-black text-emerald-900 text-[10px] uppercase">Entrada Destinada ao Departamento</div>
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">Qual Departamento recebe? *</label>
                            <select name="departamento" class="w-full h-10 px-2 border-2 border-emerald-300 rounded-xl bg-white font-extrabold text-indigo-900">
                                {% for op in opcoes.get('departamento', []) %}
                                <option value="{{ op.valor }}">{{ op.valor }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">Tipo de Entrada Departamental *</label>
                            <select name="categoria_entrada_depto" class="w-full h-10 px-2 border rounded-xl bg-white font-semibold">
                                {% for op in opcoes.get('categoria_entrada_depto', []) %}
                                <option value="{{ op.valor }}">{{ op.valor }}</option>
                                {% else %}
                                <option value="Quotas / Mensalidades do Depto">Quotas / Mensalidades do Depto</option>
                                <option value="Oferta de Culto do Depto">Oferta de Culto do Depto</option>
                                <option value="Bazar / Venda do Depto">Bazar / Arrecadação de Fundos</option>
                                {% endfor %}
                            </select>
                        </div>
                    </div>

                    <!-- SAÍDA DA IGREJA GERAL -->
                    <div id="box_saida_geral" class="hidden space-y-2 p-3.5 bg-rose-50/70 rounded-xl border border-rose-200">
                        <div class="font-black text-rose-900 text-[10px] uppercase">Despesas de Funcionamento Local</div>
                        <label class="block font-bold text-slate-700 mb-1">Selecione a Despesa Local *</label>
                        <select name="categoria_saida_geral" class="w-full h-10 px-2 border-2 border-slate-300 rounded-xl bg-white font-extrabold text-slate-800">
                            {% for op in opcoes.get('categoria_saida_geral', []) %}
                            <option value="{{ op.valor }}">{{ op.valor }}</option>
                            {% else %}
                            <option value="Energia (Electricidade / Credelec)">💡 Energia (Electricidade / Credelec)</option>
                            <option value="Água">🚰 Água</option>
                            <option value="Vogal (Apoio Pastoral / Transporte)">🚗 Vogal (Subsídio / Apoio Pastoral)</option>
                            <option value="Santa Ceia (Pão e Vinho)">🍞 Santa Ceia (Pão / Vinho / Elementos)</option>
                            {% endfor %}
                        </select>
                    </div>

                    <!-- SAÍDA PARA A IGREJA MÃE -->
                    <div id="box_saida_mae" class="hidden space-y-2 p-3.5 bg-amber-50/70 rounded-xl border-2 border-amber-300">
                        <div class="font-black text-amber-950 text-[10px] uppercase">Remessas Enviadas à Igreja Mãe (Sede)</div>
                        <label class="block font-bold text-amber-900 mb-1">Selecione o Tipo de Remessa / Envio *</label>
                        <select name="categoria_saida_mae" class="w-full h-10 px-2 border-2 border-amber-400 rounded-xl bg-white font-black text-amber-950 text-xs">
                            {% for op in opcoes.get('categoria_saida_mae', []) %}
                            <option value="{{ op.valor }}">{{ op.valor }}</option>
                            {% else %}
                            <option value="Dízimo dos Dízimos (Remessa Oficial)">📜 Dízimo dos Dízimos (Remessa Oficial)</option>
                            <option value="Quota da Sede Provincial">🏢 Quota da Sede Provincial</option>
                            {% endfor %}
                        </select>
                    </div>

                    <!-- SAÍDA PARA DEPARTAMENTOS -->
                    <div id="box_saida_depto" class="hidden space-y-3 p-3.5 bg-rose-50/70 rounded-xl border border-rose-200">
                        <div class="font-black text-rose-900 text-[10px] uppercase">Saída / Fundo Destinado a Departamento</div>
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">Qual Departamento recebe o valor? *</label>
                            <select name="departamento" class="w-full h-10 px-2 border-2 border-rose-300 rounded-xl bg-white font-extrabold text-indigo-900">
                                {% for op in opcoes.get('departamento', []) %}
                                <option value="{{ op.valor }}">{{ op.valor }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        <div>
                            <label class="block font-bold text-rose-900 mb-1">Propósito da Saída (Justificativa Obrigatória) *</label>
                            <textarea name="proposito" rows="2" placeholder="Ex: Compra de materiais didáticos da EBD / Lanche da vigília..." class="w-full p-2.5 border-2 border-rose-300 rounded-xl bg-white font-medium"></textarea>
                        </div>
                    </div>

                    <div>
                        <label class="block font-bold text-slate-700 mb-1">Observações Adicionais / Recibo</label>
                        <input type="text" name="descricao" placeholder="Nº do recibo, beneficiário ou detalhe complementar..." class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                    </div>

                    <button type="submit" class="w-full py-3.5 bg-emerald-700 hover:bg-emerald-800 text-white font-black rounded-xl shadow cursor-pointer text-sm transition">
                        💾 Confirmar e Lançar Movimento
                    </button>
                </form>
            </div>

            <div class="lg:col-span-7 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2 text-slate-800 flex justify-between items-center">
                    <span>📋 Últimos Lançamentos Efetuados</span>
                    <span class="text-xs bg-slate-100 text-slate-600 px-2.5 py-1 rounded-full font-bold">Total: {{ caixa|length }}</span>
                </h3>
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs">
                        <thead>
                            <tr class="border-b-2 border-slate-200 text-slate-500">
                                <th class="py-2.5 px-2">Data</th>
                                <th class="py-2.5 px-2">Conta</th>
                                <th class="py-2.5 px-2">Âmbito & Classificação</th>
                                <th class="py-2.5 px-2 text-right">Valor</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for cx in caixa[:15] %}
                            <tr class="border-b border-slate-100 hover:bg-slate-50">
                                <td class="py-2.5 px-2 text-slate-600 font-semibold">{{ cx.data_movimento }}</td>
                                <td class="py-2.5 px-2">
                                    {% if 'banco' in (cx.conta or '')|lower %}
                                    <span class="bg-blue-100 text-blue-900 px-2 py-0.5 rounded font-black text-[10px]">🏦 Banco</span>
                                    {% else %}
                                    <span class="bg-amber-100 text-amber-900 px-2 py-0.5 rounded font-black text-[10px]">💵 Caixa</span>
                                    {% endif %}
                                </td>
                                <td class="py-2.5 px-2">
                                    <div class="flex items-center gap-1.5">
                                        {% if cx.destino_tipo == 'Igreja Mãe' %}
                                        <span class="bg-purple-100 text-purple-900 px-1.5 py-0.5 rounded text-[9px] font-black">🏢 Igreja Mãe</span>
                                        {% elif cx.destino_tipo == 'Departamento' %}
                                        <span class="bg-indigo-100 text-indigo-900 px-1.5 py-0.5 rounded text-[9px] font-black">👥 Depto</span>
                                        {% else %}
                                        <span class="bg-slate-200 text-slate-800 px-1.5 py-0.5 rounded text-[9px] font-black">🏛️ Local</span>
                                        {% endif %}
                                        <span class="font-bold {% if cx.tipo == 'Entrada' %}text-emerald-950{% else %}text-rose-950{% endif %}">
                                            {{ cx.categoria }}
                                        </span>
                                    </div>
                                    {% if cx.descricao %}
                                    <div class="text-[10px] text-slate-500 truncate max-w-xs mt-0.5">{{ cx.descricao }}</div>
                                    {% endif %}
                                </td>
                                <td class="py-2.5 px-2 text-right font-black {% if cx.tipo == 'Entrada' %}text-emerald-700{% else %}text-rose-700{% endif %}">
                                    {% if cx.tipo == 'Entrada' %}+{% else %}-{% endif %} {{ "%.2f"|format(cx.valor or 0) }} MT
                                </td>
                            </tr>
                            {% else %}
                            <tr><td colspan="4" class="py-8 text-center text-slate-400">Nenhum lançamento efetuado ainda.</td></tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <script>
            function atualizarFormularioTesouraria() {
                var tipo = document.getElementById('tipo_movimento').value;
                var destinoTipo = document.getElementById('destino_tipo').value;

                var bEntGeral = document.getElementById('box_entrada_geral');
                var bEntMae = document.getElementById('box_entrada_mae');
                var bEntDepto = document.getElementById('box_entrada_depto');

                var bSaiGeral = document.getElementById('box_saida_geral');
                var bSaiMae = document.getElementById('box_saida_mae');
                var bSaiDepto = document.getElementById('box_saida_depto');

                bEntGeral.classList.add('hidden');
                bEntMae.classList.add('hidden');
                bEntDepto.classList.add('hidden');
                bSaiGeral.classList.add('hidden');
                bSaiMae.classList.add('hidden');
                bSaiDepto.classList.add('hidden');

                if (tipo === 'Entrada') {
                    if (destinoTipo === 'Igreja Geral') {
                        bEntGeral.classList.remove('hidden');
                    } else if (destinoTipo === 'Igreja Mãe') {
                        bEntMae.classList.remove('hidden');
                    } else if (destinoTipo === 'Departamento') {
                        bEntDepto.classList.remove('hidden');
                    }
                } else {
                    if (destinoTipo === 'Igreja Geral') {
                        bSaiGeral.classList.remove('hidden');
                    } else if (destinoTipo === 'Igreja Mãe') {
                        bSaiMae.classList.remove('hidden');
                    } else if (destinoTipo === 'Departamento') {
                        bSaiDepto.classList.remove('hidden');
                    }
                }
            }
        </script>
        {% endif %}

        <!-- ========================================================= -->
        <!-- ABA 7: DOUTRINA & BATISMO (COM GABINETE DO PROFESSOR)     -->
        <!-- ========================================================= -->
        {% if aba_ativa == 'doutrina' %}
        <div class="bg-amber-950 text-white p-6 rounded-2xl shadow mb-6 flex justify-between items-center">
            <div>
                <h2 class="text-2xl font-black">📖 Dashboard de Doutrina & Preparação Batismal</h2>
                <p class="text-xs text-amber-300 mt-1">Acompanhamento e aprovação de formandos para o Batismo nas Águas</p>
            </div>
            <div class="text-right">
                <span class="text-xs uppercase font-bold text-amber-300">Total Formandos</span>
                <div class="text-2xl font-black text-emerald-400">✅ {{ kpis.total_doutrina }} Inscritos</div>
            </div>
        </div>

        <!-- PAINEL DO PROFESSOR: ACOMPANHAMENTO E RESPOSTA A DÚVIDAS -->
        <div class="bg-white p-6 rounded-2xl shadow-sm border-2 border-indigo-200 space-y-4 mb-6 text-xs">
            <div class="border-b pb-2 flex justify-between items-center">
                <div>
                    <h3 class="font-extrabold text-base text-indigo-950 flex items-center gap-2">
                        <span>👨‍🏫</span> Gabinete do Instrutor / Professor de Doutrina & Discipulado
                    </h3>
                    <p class="text-[11px] text-slate-500">Responda diretamente às dúvidas bíblicas enviadas pelos seus formandos.</p>
                </div>
                <span class="bg-amber-100 text-amber-900 px-3 py-1 rounded-full text-xs font-black">
                    {{ duvidas_pendentes|length }} Dúvidas Pendentes
                </span>
            </div>

            <div class="space-y-3">
                {% for d in duvidas_pendentes %}
                <div class="p-4 bg-slate-50 rounded-2xl border border-slate-200 space-y-2">
                    <div class="flex justify-between items-center font-bold text-slate-800">
                        <span>❓ Pergunta do Aluno: "{{ d.pergunta }}"</span>
                        <span class="text-[10px] text-slate-400">{{ d.criado_em }}</span>
                    </div>
                    <form action="/doutrina/responder_duvida" method="POST" class="space-y-2">
                        <input type="hidden" name="duvida_id" value="{{ d.id }}">
                        <div class="grid grid-cols-1 sm:grid-cols-4 gap-2">
                            <input type="text" name="professor_nome" value="Pastor / Instrutor" placeholder="Seu Nome / Cargo" class="h-9 px-2.5 border rounded-xl bg-white font-bold">
                            <input type="text" name="resposta_professor" required placeholder="Escreva a resposta pastoral para o aluno..." class="sm:col-span-2 h-9 px-3 border-2 border-indigo-300 rounded-xl bg-white font-medium focus:outline-none">
                            <button type="submit" class="h-9 bg-indigo-700 hover:bg-indigo-800 text-white font-black rounded-xl shadow">
                                Enviar Resposta ao Aluno
                            </button>
                        </div>
                    </form>
                </div>
                {% else %}
                <p class="text-xs text-slate-400 py-2 italic text-center">Nenhuma dúvida bíblica pendente no momento.</p>
                {% endfor %}
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div class="lg:col-span-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">🎓 Inscrever Formando com Login</h3>
                <form action="/doutrina/novo" method="POST" class="space-y-3 text-xs">
                    <div>
                        <label class="block font-semibold mb-1">Nome Completo do Aluno *</label>
                        <input type="text" name="nome_aluno" required placeholder="Nome do formando" class="w-full h-10 px-3 border rounded-xl bg-slate-50 font-bold">
                    </div>
                    <div class="grid grid-cols-2 gap-2">
                        <div>
                            <label class="block font-semibold mb-1">Classe *</label>
                            <select name="classe" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-bold">
                                {% for op in opcoes.get('classe_doutrina', []) %}<option value="{{ op.valor }}">{{ op.valor }}</option>{% endfor %}
                            </select>
                        </div>
                        <div>
                            <label class="block font-semibold mb-1">Instrutor / Mentor</label>
                            <input type="text" name="professor" placeholder="Pr. / Diác." class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                        </div>
                    </div>
                    
                    <div class="p-3 bg-amber-50 rounded-xl border border-amber-200 space-y-2">
                        <div class="font-bold text-amber-900 text-[10px] uppercase">Acesso à Área de Ensino do Aluno</div>
                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <label class="block text-slate-600 mb-0.5">Usuário</label>
                                <input type="text" name="usuario" placeholder="Ex: anselmo" class="w-full h-8 px-2 border rounded bg-white font-bold">
                            </div>
                            <div>
                                <label class="block text-slate-600 mb-0.5">Senha</label>
                                <input type="text" name="senha" value="123456" class="w-full h-8 px-2 border rounded bg-white font-bold">
                            </div>
                        </div>
                    </div>

                    <div>
                        <label class="block font-semibold mb-1">Data Início</label>
                        <input type="date" name="data_inicio" required class="w-full h-10 px-2 border rounded-xl bg-slate-50">
                    </div>

                    <button type="submit" class="w-full py-3 bg-amber-700 hover:bg-amber-800 text-white font-bold rounded-xl shadow cursor-pointer">
                        Gravar Inscrição & Credenciais
                    </button>
                </form>
            </div>

            <div class="lg:col-span-8 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">📋 Lista de Formandos & Acompanhamento</h3>
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs">
                        <thead>
                            <tr class="border-b-2 border-slate-200 text-slate-500">
                                <th class="py-2.5 px-2">Aluno & Credenciais</th>
                                <th class="py-2.5 px-2">Classe & Professor</th>
                                <th class="py-2.5 px-2 text-center">Aproveitamento</th>
                                <th class="py-2.5 px-2">Situação</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for d in doutrina %}
                            <tr class="border-b border-slate-100 hover:bg-slate-50">
                                <td class="py-2.5 px-2">
                                    <div class="font-bold text-slate-900">{{ d.nome_aluno }}</div>
                                    <div class="text-[10px] text-slate-500">Usuário: <b class="text-indigo-900">{{ d.usuario or '---' }}</b> | Senha: <b>{{ d.senha or '123456' }}</b></div>
                                </td>
                                <td class="py-2.5 px-2 text-slate-700">
                                    <div class="font-semibold">{{ d.classe }}</div>
                                    <div class="text-[10px] text-slate-400">Mentor: {{ d.professor or 'Pastor' }}</div>
                                </td>
                                <td class="py-2.5 px-2 text-center">
                                    <span class="px-2.5 py-1 rounded-full font-black text-xs {% if (d.aproveitamento or 0) >= 70 %}bg-emerald-100 text-emerald-800{% else %}bg-amber-100 text-amber-800{% endif %}">
                                        {{ "%.0f"|format(d.aproveitamento or 0) }}%
                                    </span>
                                </td>
                                <td class="py-2.5 px-2">
                                    {% if (d.aproveitamento or 0) >= 70 or 'apto' in d.situacao|lower %}
                                    <span class="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-bold text-[10px]">✅ Apto / Aprovado</span>
                                    {% else %}
                                    <span class="bg-slate-100 text-slate-700 px-2 py-0.5 rounded font-bold text-[10px]">Em Formação</span>
                                    {% endif %}
                                </td>
                            </tr>
                            {% else %}
                            <tr><td colspan="4" class="py-8 text-center text-slate-400">Nenhum formando inscrito.</td></tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- ========================================================= -->
        <!-- ABA 8: GESTOR DE SELETORES (CONTROLO TOTAL DO ADM)        -->
        <!-- ========================================================= -->
        {% if aba_ativa == 'configuracoes' and usuario_logado.perfil == 'admin' %}
        <div class="bg-purple-950 text-white p-5 rounded-2xl shadow mb-6">
            <h2 class="text-xl font-extrabold">⚙️ Gestor Geral de Seletores do Sistema</h2>
            <p class="text-xs text-purple-300 mt-1">O administrador tem controlo absoluto para adicionar, corrigir a linguagem/nomes e remover qualquer opção</p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div class="lg:col-span-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2 text-purple-950">➕ Adicionar Nova Opção</h3>
                <form action="/config/opcoes/adicionar" method="POST" class="space-y-4 text-xs">
                    <div>
                        <label class="block font-semibold mb-1 text-slate-700">Lista que deseja atualizar: *</label>
                        <select name="categoria" required class="w-full h-11 px-3 border-2 border-slate-200 rounded-xl bg-slate-50 font-black text-indigo-950">
                            <option value="departamento">📁 Departamentos da Igreja</option>
                            <option value="cargo">✝️ Cargos Ministeriais</option>
                            <option value="zona">📍 Zonas da Igreja</option>
                            <option value="celula">🏠 Células Familiares</option>
                            <option value="estado_civil">💍 Estado Civil</option>
                            <option value="tipo_culto">⛪ Tipos de Cultos</option>
                            <option value="tipo_evento">🎪 Tipos de Eventos / Planificação</option>
                            <option value="categoria_caixa">💰 Receitas da Igreja Local</option>
                            <option value="categoria_saida_geral">💡 Despesas Locais (Energia, Água...)</option>
                            <option value="categoria_saida_mae">📜 Remessas Sede (Dízimo dos Dízimos)</option>
                            <option value="categoria_entrada_mae">🏢 Apoios Recebidos da Igreja Mãe</option>
                            <option value="categoria_entrada_depto">🏷️ Entradas em Departamentos</option>
                            <option value="classe_doutrina">📖 Classes de Doutrina</option>
                        </select>
                    </div>
                    <div>
                        <label class="block font-semibold mb-1 text-slate-700">Nome / Designação da Opção: *</label>
                        <input type="text" name="valor" required placeholder="Ex: Departamento de Casais" class="w-full h-11 px-3 border-2 border-slate-200 rounded-xl bg-slate-50 font-bold focus:border-purple-600 focus:outline-none">
                    </div>
                    <button type="submit" class="w-full py-3.5 bg-purple-700 hover:bg-purple-800 text-white font-black rounded-xl shadow cursor-pointer text-sm transition">
                        Gravar Nova Opção
                    </button>
                </form>
            </div>

            <div class="lg:col-span-8 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2 text-slate-800 flex justify-between items-center">
                    <span>📋 Todas as Opções Ativas nos Menus</span>
                    <span class="text-xs bg-slate-100 text-slate-600 px-2.5 py-1 rounded-full font-bold">Total: {{ opcoes.values()|map('length')|sum }} opções</span>
                </h3>
                
                <div class="space-y-4 text-xs max-h-[600px] overflow-y-auto pr-2">
                    {% for cat, itens in opcoes.items() %}
                    <div class="border border-slate-200 rounded-2xl p-4 bg-slate-50 space-y-2">
                        <div class="font-black text-slate-800 uppercase tracking-wider text-[11px] flex justify-between items-center">
                            <span>📌 {{ cat.replace('_', ' ').title() }}</span>
                            <span class="bg-slate-200 text-slate-700 px-2 py-0.5 rounded-full text-[10px]">{{ itens|length }} opções</span>
                        </div>
                        <div class="flex flex-wrap gap-2">
                            {% for op in itens %}
                            <div class="inline-flex items-center gap-2 bg-white border border-slate-300 px-3 py-1.5 rounded-xl text-slate-800 font-semibold shadow-sm">
                                <span>{{ op.valor }}</span>
                                <div class="flex items-center gap-1 border-l pl-2 border-slate-200">
                                    <button onclick="editarOpcao('{{ op.id }}', '{{ op.valor }}')" class="text-blue-600 hover:text-blue-800 font-bold" title="Corrigir / Renomear">✏️</button>
                                    <a href="/config/opcoes/remover/{{ op.id }}" onclick="return confirm('Remover definitivamente a opção {{ op.valor }}?')" class="text-rose-500 hover:text-rose-700 font-black text-sm" title="Excluir">×</a>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>

        <div id="modal_editar_opcao" class="hidden fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
            <div class="bg-white rounded-3xl p-6 max-w-sm w-full shadow-2xl space-y-4 text-xs border">
                <div class="flex justify-between items-center border-b pb-2">
                    <h4 class="font-black text-sm text-slate-900">✏️ Corrigir / Renomear Opção</h4>
                    <button onclick="fecharModalEditar()" class="text-slate-400 hover:text-slate-600 font-black text-lg">&times;</button>
                </div>
                <form action="/config/opcoes/editar" method="POST" class="space-y-3">
                    <input type="hidden" id="edit_opcao_id" name="id">
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">Novo Nome / Linguagem Correta:</label>
                        <input type="text" id="edit_opcao_valor" name="valor" required class="w-full h-11 px-3 border-2 border-indigo-400 rounded-xl bg-white font-bold focus:outline-none">
                    </div>
                    <div class="flex gap-2 pt-2">
                        <button type="button" onclick="fecharModalEditar()" class="flex-1 py-2.5 bg-slate-200 text-slate-700 font-bold rounded-xl">Cancelar</button>
                        <button type="submit" class="flex-1 py-2.5 bg-indigo-700 hover:bg-indigo-800 text-white font-bold rounded-xl shadow">Salvar Correção</button>
                    </div>
                </form>
            </div>
        </div>

        <script>
            function editarOpcao(id, valorAtual) {
                document.getElementById('edit_opcao_id').value = id;
                document.getElementById('edit_opcao_valor').value = valorAtual;
                document.getElementById('modal_editar_opcao').classList.remove('hidden');
            }
            function fecharModalEditar() {
                document.getElementById('modal_editar_opcao').classList.add('hidden');
            }
        </script>
        {% endif %}

    </main>

    <script>
        function somarCulto() {
            var inputs = document.querySelectorAll('.campo-soma');
            var tot = 0;
            inputs.forEach(function(i) { tot += (parseInt(i.value, 10) || 0); });
            var el = document.getElementById('total_presentes');
            if (el) el.value = tot;
        }
    </script>
</body>
</html>
"""

env.parse(dash_completo)
with open(os.path.join('templates', 'dashboard.html'), 'w', encoding='utf-8') as f:
    f.write(dash_completo)
print("✓ templates/dashboard.html: Dashboard completo com todas as grelhas e campos restaurado!")

print("=" * 80)
print(">>> INSTALAÇÃO DEFINITIVA CONCLUÍDA COM SUCESSO ABSOLUTO! <<<")
print("=" * 80)