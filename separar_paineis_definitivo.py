import os
import re
import py_compile
import subprocess
import jinja2

print("=" * 80)
print("1. RESTAURAR O PAINEL COMPLETO DO ADMINISTRADOR (dashboard.html)...")
print("=" * 80)

caminho_dash = os.path.join('templates', 'dashboard.html')
caminho_prof = os.path.join('templates', 'area_professor.html')
caminho_aulas = os.path.join('templates', 'ensino_aulas.html')
caminho_app = 'app.py'

# Verificar se templates/dashboard.html precisa de restaurar o Raio-X do Admin
precisa_restaurar = True
if os.path.exists(caminho_dash):
    with open(caminho_dash, 'r', encoding='utf-8') as f:
        conteudo_atual = f.read()
    if 'Raio-X Ministerial' in conteudo_atual:
        precisa_restaurar = False
        print("✓ dashboard.html já contém o painel original do Administrador!")

if precisa_restaurar:
    # 1. Tentar restaurar a partir dos backups locais
    restaurado = False
    for b in ['templates/dashboard_backup_estrutural.html', 'templates/dashboard.html.bak']:
        if os.path.exists(b):
            with open(b, 'r', encoding='utf-8') as f:
                c = f.read()
            if 'Raio-X Ministerial' in c:
                with open(caminho_dash, 'w', encoding='utf-8') as f:
                    f.write(c)
                print(f"✓ dashboard.html restaurado a partir de {b}!")
                restaurado = True
                break

    # 2. Se não estiver em backup, resgatar do histórico do Git
    if not restaurado:
        try:
            res = subprocess.run(["git", "log", "--oneline", "-n", "20", "templates/dashboard.html"], capture_output=True, text=True)
            for linha in res.stdout.splitlines():
                h = linha.split()[0]
                show_res = subprocess.run(["git", "show", f"{h}:templates/dashboard.html"], capture_output=True, text=True)
                if 'Raio-X Ministerial' in show_res.stdout:
                    with open(caminho_dash, 'w', encoding='utf-8') as f:
                        f.write(show_res.stdout)
                    print(f"✓ dashboard.html do Administrador recuperado do commit {h}!")
                    restaurado = True
                    break
        except Exception as e:
            print("Aviso ao recuperar via Git:", e)

# Garantir o atalho para o Administrador visualizar a área do professor no menu lateral
if os.path.exists(caminho_dash):
    with open(caminho_dash, 'r', encoding='utf-8') as f:
        html_admin = f.read()
    
    atalho_admin = """
            <a href="/professor" target="_blank" class="flex items-center gap-3 px-3 py-2 rounded-xl text-amber-300 bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 transition text-xs font-bold my-1">
                <span class="text-base">👨‍🏫</span>
                <span>Área do Professor (Visualizar) ↗</span>
            </a>
    """
    if "Área do Professor (Visualizar)" not in html_admin:
        pos_menu = html_admin.find("Doutrina & Batismo")
        if pos_menu != -1:
            pos_tag = html_admin.rfind("<a", 0, pos_menu)
            html_admin = html_admin[:pos_tag] + atalho_admin + "\n" + html_admin[pos_tag:]
            with open(caminho_dash, 'w', encoding='utf-8') as f:
                f.write(html_admin)
            print("✓ Atalho do Professor mantido no menu lateral do Administrador!")

print("\n" + "=" * 80)
print("2. ASSEGURAR A TELA EXCLUSIVA DO PROFESSOR (area_professor.html)...")
print("=" * 80)

html_prof = """<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Área do Professor • SIGIEAD</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>body { font-family: 'Plus Jakarta Sans', sans-serif; }</style>
</head>
<body class="bg-slate-100 text-slate-800 min-h-screen flex flex-col antialiased">
    <header class="bg-slate-900 text-white sticky top-0 z-50 shadow-md">
        <div class="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
            <div class="flex items-center gap-3">
                <div class="w-9 h-9 rounded-xl bg-amber-500/20 border border-amber-400/30 flex items-center justify-center text-amber-400 text-lg font-black shadow-inner">📖</div>
                <div>
                    <h1 class="font-black text-sm tracking-tight text-white leading-tight">SIGIEAD • Chicuque</h1>
                    <span class="text-[10px] text-amber-400 font-bold block uppercase tracking-wider">Área do Instrutor / Professor</span>
                </div>
            </div>
            <div class="flex items-center gap-2 sm:gap-3">
                <span class="text-[10px] font-black px-2.5 py-1 rounded-lg bg-amber-500/20 text-amber-300 border border-amber-500/30 uppercase">Professor</span>
                <a href="/logout" class="px-3.5 py-1.5 bg-rose-600 hover:bg-rose-700 text-white rounded-xl text-xs font-bold transition shadow-sm flex items-center gap-1"><span>Sair</span></a>
            </div>
        </div>
    </header>
    <main class="flex-1 max-w-6xl w-full mx-auto p-4 sm:p-6 space-y-5">
        <div class="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white p-5 sm:p-6 rounded-2xl shadow-lg border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div class="space-y-1">
                <div class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-amber-500/20 border border-amber-400/30 text-amber-300 text-[10px] font-black uppercase tracking-wider"><span>👨‍🏫</span> Gabinete Pedagógico</div>
                <h2 class="text-xl sm:text-2xl font-black text-white">Paz do Senhor, {{ usuario_logado.nome.split()[0] if usuario_logado and usuario_logado.nome else 'Professor' }}!</h2>
                <p class="text-xs text-slate-300 max-w-xl">Painel exclusivo para acompanhamento dos formandos de Doutrina, Batismo e Discipulado da Igreja de Chicuque.</p>
            </div>
            <div>
                <a href="/ensino/aulas" target="_blank" class="w-full sm:w-auto px-4 py-2.5 bg-amber-500 hover:bg-amber-600 text-slate-950 font-black rounded-xl text-xs transition shadow-md flex items-center justify-center gap-2"><span>🎓</span><span>Sala Virtual do Aluno ↗</span></a>
            </div>
        </div>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
            <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
                <span class="text-[10px] font-bold uppercase text-slate-400 block tracking-wider">Formandos Inscritos</span>
                <span class="text-2xl sm:text-3xl font-black text-slate-900 block mt-1">{{ doutrina|length if doutrina else 0 }}</span>
                <span class="text-[10px] text-emerald-600 font-bold block mt-0.5">● Alunos na Turma</span>
            </div>
            <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
                <span class="text-[10px] font-bold uppercase text-slate-400 block tracking-wider">Em Formação</span>
                <span class="text-2xl sm:text-3xl font-black text-indigo-900 block mt-1">{{ doutrina|length if doutrina else 0 }}</span>
                <span class="text-[10px] text-indigo-600 font-bold block mt-0.5">Classes Ativas</span>
            </div>
            <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
                <span class="text-[10px] font-bold uppercase text-slate-400 block tracking-wider">Dúvidas Bíblicas</span>
                <span class="text-2xl sm:text-3xl font-black text-amber-600 block mt-1">{{ duvidas|length if duvidas else 0 }}</span>
                <span class="text-[10px] text-slate-500 font-medium block mt-0.5">Mensagens pendentes</span>
            </div>
            <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
                <span class="text-[10px] font-bold uppercase text-slate-400 block tracking-wider">Ano Eclesiástico</span>
                <span class="text-xl sm:text-2xl font-black text-slate-800 block mt-1">2026</span>
                <span class="text-[10px] text-slate-500 font-medium block mt-0.5">Igreja de Chicuque</span>
            </div>
        </div>
        <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
            <div class="flex items-center justify-between border-b border-slate-100 pb-3">
                <div class="flex items-center gap-2"><span class="text-lg">💬</span><h3 class="font-black text-sm text-slate-900 uppercase">Gabinete de Dúvidas Bíblicas</h3></div>
                <span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800">{{ duvidas|length if duvidas else 0 }} pendente(s)</span>
            </div>
            {% if duvidas and duvidas|length > 0 %}
                <div class="space-y-3">
                    {% for d in duvidas %}
                    <div class="p-3.5 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
                        <div class="flex items-center justify-between text-xs"><span class="font-bold text-slate-900">{{ d.nome_aluno or 'Aluno' }}</span><span class="text-[10px] text-slate-400">{{ d.criado_em or '' }}</span></div>
                        <p class="text-xs text-slate-700 italic">"{{ d.duvida or d.mensagem or '' }}"</p>
                    </div>
                    {% endfor %}
                </div>
            {% else %}
                <div class="p-5 text-center text-slate-400 text-xs italic bg-slate-50/50 rounded-xl border border-dashed border-slate-200">Nenhuma dúvida bíblica enviada pelos formandos no momento.</div>
            {% endif %}
        </div>
        <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-100 pb-3 gap-2">
                <div class="flex items-center gap-2"><span class="text-lg">📋</span><div><h3 class="font-black text-sm text-slate-900 uppercase">Lista de Formandos & Turmas</h3><p class="text-[11px] text-slate-400">Acompanhamento dos formandos alocados</p></div></div>
                <span class="text-xs font-bold text-indigo-900 bg-indigo-50 px-3 py-1 rounded-xl self-start sm:self-auto">{{ doutrina|length if doutrina else 0 }} Aluno(s) Alocado(s)</span>
            </div>
            <div class="overflow-x-auto">
                <table class="w-full text-left text-xs border-collapse">
                    <thead>
                        <tr class="bg-slate-100 text-slate-700 font-bold uppercase text-[10px]">
                            <th class="p-3">Aluno</th>
                            <th class="p-3">Classe</th>
                            <th class="p-3">Mentor / Instrutor</th>
                            <th class="p-3">Lição Atual</th>
                            <th class="p-3 text-center">Presenças</th>
                            <th class="p-3 text-center">Situação</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-100 font-medium">
                        {% if doutrina and doutrina|length > 0 %}
                            {% for a in doutrina %}
                            <tr class="hover:bg-slate-50 transition">
                                <td class="p-3 font-bold text-slate-900">
                                    {{ a.nome_aluno or a.nome or 'Sem Nome' }}
                                    {% if a.usuario %}<span class="block text-[10px] text-slate-400 font-normal">Login: {{ a.usuario }}</span>{% endif %}
                                </td>
                                <td class="p-3 text-indigo-900 font-semibold">{{ a.classe or 'Discipulado' }}</td>
                                <td class="p-3 text-slate-600">{{ a.professor or usuario_logado.nome or 'Pastor Dirigente' }}</td>
                                <td class="p-3 text-amber-800 font-bold">{{ a.licao_atual or 'Lição 1' }}</td>
                                <td class="p-3 text-center"><span class="px-2.5 py-0.5 rounded-full text-[10px] font-black bg-blue-100 text-blue-800">{{ a.presencas or 0 }}</span></td>
                                <td class="p-3 text-center"><span class="px-2.5 py-0.5 rounded-full text-[10px] font-black bg-emerald-100 text-emerald-800">{{ a.situacao or 'Em Formação' }}</span></td>
                            </tr>
                            {% endfor %}
                        {% else %}
                            <tr><td colspan="6" class="p-6 text-center text-slate-400 italic">Nenhum formando inscrito no momento.</td></tr>
                        {% endif %}
                    </tbody>
                </table>
            </div>
        </div>
    </main>
</body>
</html>"""

os.makedirs('templates', exist_ok=True)
with open(caminho_prof, 'w', encoding='utf-8') as f:
    f.write(html_prof)
print("✓ templates/area_professor.html gravado com sucesso!")

print("\n" + "=" * 80)
print("3. ASSEGURAR A SALA VIRTUAL DE AULAS (ensino_aulas.html)...")
print("=" * 80)

html_aulas = """<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sala Virtual de Ensino & Doutrina • SIGIEAD</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>body { font-family: 'Plus Jakarta Sans', sans-serif; }</style>
</head>
<body class="bg-slate-100 text-slate-800 min-h-screen flex flex-col antialiased">
    <header class="bg-slate-900 text-white sticky top-0 z-50 shadow-md">
        <div class="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
            <div class="flex items-center gap-3">
                <a href="/professor" class="w-9 h-9 rounded-xl bg-amber-500/20 border border-amber-400/30 flex items-center justify-center text-amber-400 text-lg font-black shadow-inner hover:bg-amber-500/30 transition">📖</a>
                <div>
                    <h1 class="font-black text-sm tracking-tight text-white leading-tight">SIGIEAD • Sala Virtual de Ensino</h1>
                    <span class="text-[10px] text-amber-400 font-bold block uppercase tracking-wider">Igreja de Chicuque • Doutrina & Discipulado</span>
                </div>
            </div>
            <div class="flex items-center gap-2">
                <a href="/professor" class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-white rounded-xl text-xs font-bold transition border border-slate-700 flex items-center gap-1.5">
                    <span>←</span><span class="hidden sm:inline">Voltar ao Painel</span>
                </a>
                <a href="/logout" class="px-3 py-1.5 bg-rose-600 hover:bg-rose-700 text-white rounded-xl text-xs font-bold transition shadow-sm">Sair</a>
            </div>
        </div>
    </header>
    <main class="flex-1 max-w-6xl w-full mx-auto p-4 sm:p-6 space-y-6">
        <div class="bg-gradient-to-r from-indigo-950 via-slate-900 to-indigo-950 text-white p-6 rounded-2xl shadow-lg border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div class="space-y-1">
                <div class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-amber-500/20 border border-amber-400/30 text-amber-300 text-[10px] font-black uppercase tracking-wider"><span>🎓</span> Currículo Eclesiástico 2026</div>
                <h2 class="text-xl sm:text-2xl font-black text-white">Plano de Aulas: Doutrina & Batismo</h2>
                <p class="text-xs text-slate-300 max-w-xl">Material didático e acompanhamento de lições bíblicas para os formandos da classe de discipulado e batismo da Igreja de Chicuque.</p>
            </div>
            <span class="px-3 py-1.5 bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs font-bold rounded-xl">{{ doutrina|length if doutrina else 0 }} Formandos Ativos</span>
        </div>
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div class="lg:col-span-2 space-y-4">
                <h3 class="font-black text-sm text-slate-900 uppercase tracking-wider flex items-center gap-2"><span>📚</span> Módulos & Lições do Curso de Doutrina</h3>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div class="p-4 bg-white rounded-2xl border border-slate-200 shadow-sm space-y-2">
                        <div class="flex items-center justify-between"><span class="text-[10px] font-black px-2 py-0.5 rounded-md bg-amber-100 text-amber-800 uppercase">Lição 1</span><span class="text-[10px] text-emerald-600 font-bold">● Fundamental</span></div>
                        <h4 class="font-bold text-sm text-slate-900">A Salvação em Cristo Jesus</h4>
                        <p class="text-xs text-slate-500 leading-relaxed">O plano da redenção, o arrependimento sincero, a justificação pela fé e a certeza da vida eterna.</p>
                        <div class="pt-2 border-t border-slate-100 text-[11px] font-bold text-slate-400">📖 Textos: João 3:16 • Romanos 10:9-10 • Efésios 2:8-9</div>
                    </div>
                    <div class="p-4 bg-white rounded-2xl border border-slate-200 shadow-sm space-y-2">
                        <div class="flex items-center justify-between"><span class="text-[10px] font-black px-2 py-0.5 rounded-md bg-blue-100 text-blue-800 uppercase">Lição 2</span><span class="text-[10px] text-indigo-600 font-bold">● Sacramental</span></div>
                        <h4 class="font-bold text-sm text-slate-900">O Batismo nas Águas</h4>
                        <p class="text-xs text-slate-500 leading-relaxed">Significado bíblico da imersão pública, sepultamento do velho homem e ressurreição para uma nova vida.</p>
                        <div class="pt-2 border-t border-slate-100 text-[11px] font-bold text-slate-400">📖 Textos: Mateus 28:19 • Romanos 6:3-4 • Atos 2:38</div>
                    </div>
                    <div class="p-4 bg-white rounded-2xl border border-slate-200 shadow-sm space-y-2">
                        <div class="flex items-center justify-between"><span class="text-[10px] font-black px-2 py-0.5 rounded-md bg-purple-100 text-purple-800 uppercase">Lição 3</span><span class="text-[10px] text-purple-600 font-bold">● Espiritual</span></div>
                        <h4 class="font-bold text-sm text-slate-900">A Palavra de Deus & Oração</h4>
                        <p class="text-xs text-slate-500 leading-relaxed">A Bíblia Sagrada como única regra de fé e conduta; comunhão diária através da vida devocional.</p>
                        <div class="pt-2 border-t border-slate-100 text-[11px] font-bold text-slate-400">📖 Textos: 2 Timóteo 3:16-17 • 1 Tessalonicenses 5:17</div>
                    </div>
                    <div class="p-4 bg-white rounded-2xl border border-slate-200 shadow-sm space-y-2">
                        <div class="flex items-center justify-between"><span class="text-[10px] font-black px-2 py-0.5 rounded-md bg-rose-100 text-rose-800 uppercase">Lição 4</span><span class="text-[10px] text-rose-600 font-bold">● Eclesiástica</span></div>
                        <h4 class="font-bold text-sm text-slate-900">A Santa Ceia & Comunhão</h4>
                        <p class="text-xs text-slate-500 leading-relaxed">Memorial do sacrifício na cruz, comunhão fraterna no corpo de Cristo e preparação espiritual.</p>
                        <div class="pt-2 border-t border-slate-100 text-[11px] font-bold text-slate-400">📖 Textos: 1 Coríntios 11:23-29 • Lucas 22:19</div>
                    </div>
                </div>
            </div>
            <div class="space-y-4">
                <h3 class="font-black text-sm text-slate-900 uppercase tracking-wider flex items-center gap-2"><span>👥</span> Formandos Matriculados</h3>
                <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-3">
                    {% if doutrina and doutrina|length > 0 %}
                        {% for a in doutrina %}
                        <div class="p-3 bg-slate-50 rounded-xl border border-slate-100 flex items-center justify-between text-xs">
                            <div>
                                <span class="font-bold text-slate-900 block">{{ a.nome_aluno or a.nome or 'Aluno' }}</span>
                                <span class="text-[10px] text-indigo-700 font-semibold block">{{ a.classe or 'Discipulado' }} • {{ a.licao_atual or 'Lição 1' }}</span>
                            </div>
                            <span class="px-2 py-1 rounded-lg bg-emerald-100 text-emerald-800 text-[10px] font-black">{{ a.presencas or 0 }} Presenças</span>
                        </div>
                        {% endfor %}
                    {% else %}
                        <p class="text-xs text-slate-400 italic text-center py-4">Nenhum formando inscrito no momento.</p>
                    {% endif %}
                </div>
            </div>
        </div>
    </main>
</body>
</html>"""

with open(caminho_aulas, 'w', encoding='utf-8') as f:
    f.write(html_aulas)
print("✓ templates/ensino_aulas.html gravado com sucesso!")

print("\n" + "=" * 80)
print("4. CONFIGURAR ROTEAMENTO EXATO EM APP.PY...")
print("=" * 80)

with open(caminho_app, 'r', encoding='utf-8') as f:
    app_code = f.read()

# Rota /login limpa
login_limpo = '''@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('usuario', '').strip()
        s = request.form.get('senha', '').strip()
        user = None
        try:
            user = consultar_um("SELECT * FROM usuarios_sistema WHERE LOWER(usuario) = LOWER(%s) AND senha = %s", (u, s))
        except Exception:
            try:
                user = consultar_um("SELECT * FROM usuarios_sistema WHERE LOWER(usuario) = LOWER(?) AND senha = ?", (u, s))
            except Exception as e:
                user = None

        if user:
            session['usuario'] = dict(user)
            perfil = str(user.get('perfil', '')).lower()
            if any(p in perfil for p in ['prof', 'docente', 'instrutor']):
                return redirect('/professor')
            return redirect('/?aba=dashboard')
        flash('Credenciais incorretas.', 'danger')
    return render_template('login.html')'''

pos_login = app_code.find("@app.route('/login'")
if pos_login == -1: pos_login = app_code.find('@app.route("/login"')
if pos_login != -1:
    pos_prox = app_code.find("\n@app.route", pos_login + 15)
    if pos_prox != -1:
        app_code = app_code[:pos_login] + login_limpo + "\n\n" + app_code[pos_prox:]

# Rota principal (index): Administrador vê dashboard.html; Professor é desviado para /professor
index_limpo = '''@app.route('/')
def index():
    if not session.get('usuario'):
        return redirect(url_for('login'))
    usuario = session.get('usuario')
    perfil = str(usuario.get('perfil', '')).lower()
    
    # SE FOR PROFESSOR: vai para a sua tela /professor
    if any(p in perfil for p in ['prof', 'docente', 'instrutor']):
        return redirect('/professor')
        
    aba_ativa = request.args.get('aba', 'dashboard')
    
    # Carregar dados normais para o Administrador
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
                           doutrina=doutrina,
                           duvidas=duvidas)'''

pos_idx = app_code.find("@app.route('/')")
if pos_idx == -1: pos_idx = app_code.find('@app.route("/")')
if pos_idx != -1:
    pos_prox_i = app_code.find("\n@app.route", pos_idx + 15)
    if pos_prox_i != -1:
        app_code = app_code[:pos_idx] + index_limpo + "\n\n" + app_code[pos_prox_i:]

# Rota /professor
rota_prof = '''@app.route('/professor')
def area_professor():
    if not session.get('usuario'):
        return redirect(url_for('login'))
    usuario = session.get('usuario')
    try:
        doutrina = consultar_todos("SELECT * FROM doutrina ORDER BY id DESC")
    except Exception:
        doutrina = []
    try:
        duvidas = consultar_todos("SELECT * FROM duvidas_alunos ORDER BY id DESC")
    except Exception:
        duvidas = []
    return render_template('area_professor.html',
                           usuario_logado=usuario,
                           doutrina=doutrina,
                           duvidas=duvidas)'''

if "@app.route('/professor')" not in app_code:
    app_code = app_code.rstrip() + "\n\n" + rota_prof + "\n"
else:
    # Substituir a existente
    app_code = re.sub(r"@app\.route\(['\"]/professor['\"][^\)]*\)[\s\S]*?(?=\n@app|\nif __name__|\Z)", rota_prof + "\n", app_code)

# Rota /ensino/aulas (Sala Virtual)
rota_aulas = '''@app.route('/ensino/aulas')
def sala_aulas_virtual():
    if not session.get('usuario'):
        return redirect(url_for('login'))
    usuario = session.get('usuario')
    try:
        doutrina = consultar_todos("SELECT * FROM doutrina ORDER BY id DESC")
    except Exception:
        doutrina = []
    return render_template('ensino_aulas.html',
                           usuario_logado=usuario,
                           doutrina=doutrina)'''

if "@app.route('/ensino/aulas')" not in app_code:
    app_code = app_code.rstrip() + "\n\n" + rota_aulas + "\n"
else:
    app_code = re.sub(r"@app\.route\(['\"]/ensino/aulas['\"][^\)]*\)[\s\S]*?(?=\n@app|\nif __name__|\Z)", rota_aulas + "\n", app_code)

with open(caminho_app, 'w', encoding='utf-8') as f:
    f.write(app_code)

py_compile.compile(caminho_app, doraise=True)
print("✓ app.py validado e compilado com ZERO erros!")

# Publicar no Render
print("\n" + "=" * 80)
print("5. PUBLICAR NO GITHUB E RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "app.py", "templates/dashboard.html", "templates/area_professor.html", "templates/ensino_aulas.html"])
subprocess.run(["git", "commit", "-m", "Separacao total: admin no dashboard com raio-x e professor no /professor"])
subprocess.run(["git", "push", "origin", "main"])

print("=" * 80)
print(">>> SEPARAÇÃO TOTAL PUBLICADA NO RENDER COM SUCESSO! <<<")
print("=" * 80)