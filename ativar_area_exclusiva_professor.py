import os
import re
import py_compile
import subprocess
import jinja2

print("=" * 80)
print("A CRIAR ÁREA EXCLUSIVA DO PROFESSOR (/professor) E DESVINCULAR DO RAIO-X...")
print("=" * 80)

caminho_app = 'app.py'
caminho_dash = os.path.join('templates', 'dashboard.html')
caminho_prof = os.path.join('templates', 'area_professor.html')

# =============================================================================
# 1. RESTAURAR DASHBOARD.HTML ORIGINAL PARA O ADMINISTRADOR (COMMIT LIMPO)
# =============================================================================
try:
    res = subprocess.run(["git", "log", "--oneline", "templates/dashboard.html"], capture_output=True, text=True)
    linhas = [l.strip() for l in res.stdout.strip().splitlines() if l.strip()]
    hash_limpo = None
    for l in linhas:
        if "Demografia ministerial" in l:
            hash_limpo = l.split()[0]
            break
    if not hash_limpo and len(linhas) >= 5:
        hash_limpo = linhas[4].split()[0]

    if hash_limpo:
        subprocess.run(["git", "checkout", hash_limpo, "--", "templates/dashboard.html"], check=True)
        print(f"✓ templates/dashboard.html restaurado ao layout desktop limpo ({hash_limpo})!")
except Exception as e:
    print(f"Aviso Git: {e}")

# Limpeza preventiva de overflow nos selects do dashboard
if os.path.exists(caminho_dash):
    with open(caminho_dash, 'r', encoding='utf-8') as f:
        dash_txt = f.read()
    dash_txt = re.sub(r'\boverflow(-x)?-(auto|scroll)\b', '', dash_txt)
    with open(caminho_dash, 'w', encoding='utf-8') as f:
        f.write(dash_txt)

# =============================================================================
# 2. CRIAR O TEMPLATE DEDICADO DO PROFESSOR (templates/area_professor.html)
# =============================================================================
html_professor = """<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Área do Professor • SIGIEAD</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; }
    </style>
</head>
<body class="bg-slate-100 text-slate-800 min-h-screen flex flex-col antialiased">

    <!-- CABEÇALHO DO PROFESSOR (100% LARGURA, SEM BARRA LATERAL) -->
    <header class="bg-slate-900 text-white sticky top-0 z-50 shadow-md">
        <div class="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
            <div class="flex items-center gap-3">
                <div class="w-9 h-9 rounded-xl bg-amber-500/20 border border-amber-400/30 flex items-center justify-center text-amber-400 text-lg font-black shadow-inner">
                    📖
                </div>
                <div>
                    <h1 class="font-black text-sm tracking-tight text-white leading-tight">SIGIEAD • Chicuque</h1>
                    <span class="text-[10px] text-amber-400 font-bold block uppercase tracking-wider">
                        Área do Instrutor / Professor
                    </span>
                </div>
            </div>

            <div class="flex items-center gap-2 sm:gap-3">
                <span class="text-[10px] font-black px-2.5 py-1 rounded-lg bg-amber-500/20 text-amber-300 border border-amber-500/30 uppercase">
                    Professor
                </span>
                <a href="/logout" class="px-3.5 py-1.5 bg-rose-600 hover:bg-rose-700 text-white rounded-xl text-xs font-bold transition shadow-sm flex items-center gap-1">
                    <span>Sair</span>
                </a>
            </div>
        </div>
    </header>

    <!-- CONTEÚDO PRINCIPAL (100% DA LARGURA NO TELEMÓVEL) -->
    <main class="flex-1 max-w-6xl w-full mx-auto p-4 sm:p-6 space-y-5">

        <!-- BANNER DE BOAS-VINDAS -->
        <div class="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white p-5 sm:p-6 rounded-2xl shadow-lg border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div class="space-y-1">
                <div class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-amber-500/20 border border-amber-400/30 text-amber-300 text-[10px] font-black uppercase tracking-wider">
                    <span>👨‍🏫</span> Gabinete Pedagógico
                </div>
                <h2 class="text-xl sm:text-2xl font-black text-white">
                    Paz do Senhor, {{ usuario_logado.nome.split()[0] if usuario_logado and usuario_logado.nome else 'Professor' }}!
                </h2>
                <p class="text-xs text-slate-300 max-w-xl">
                    Painel de acompanhamento pedagógico das suas turmas de Doutrina, Batismo e Discipulado da Igreja de Chicuque.
                </p>
            </div>
            <div>
                <a href="/ensino/aulas" target="_blank" class="w-full sm:w-auto px-4 py-2.5 bg-amber-500 hover:bg-amber-600 text-slate-950 font-black rounded-xl text-xs transition shadow-md flex items-center justify-center gap-2">
                    <span>🎓</span>
                    <span>Sala Virtual do Aluno ↗</span>
                </a>
            </div>
        </div>

        <!-- INDICADORES DA TURMA -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
            <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
                <span class="text-[10px] font-bold uppercase text-slate-400 block tracking-wider">Formandos Inscritos</span>
                <span class="text-2xl sm:text-3xl font-black text-slate-900 block mt-1">
                    {{ doutrina|length if doutrina else 0 }}
                </span>
                <span class="text-[10px] text-emerald-600 font-bold block mt-0.5">● Alunos na Turma</span>
            </div>

            <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
                <span class="text-[10px] font-bold uppercase text-slate-400 block tracking-wider">Em Formação</span>
                <span class="text-2xl sm:text-3xl font-black text-indigo-900 block mt-1">
                    {{ doutrina|length if doutrina else 0 }}
                </span>
                <span class="text-[10px] text-indigo-600 font-bold block mt-0.5">Classes Ativas</span>
            </div>

            <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
                <span class="text-[10px] font-bold uppercase text-slate-400 block tracking-wider">Dúvidas Bíblicas</span>
                <span class="text-2xl sm:text-3xl font-black text-amber-600 block mt-1">
                    {{ duvidas|length if duvidas else 0 }}
                </span>
                <span class="text-[10px] text-slate-500 font-medium block mt-0.5">Mensagens pendentes</span>
            </div>

            <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
                <span class="text-[10px] font-bold uppercase text-slate-400 block tracking-wider">Ano Eclesiástico</span>
                <span class="text-xl sm:text-2xl font-black text-slate-800 block mt-1">
                    2026
                </span>
                <span class="text-[10px] text-slate-500 font-medium block mt-0.5">Igreja de Chicuque</span>
            </div>
        </div>

        <!-- GABINETE DE DÚVIDAS BÍBLICAS -->
        <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
            <div class="flex items-center justify-between border-b border-slate-100 pb-3">
                <div class="flex items-center gap-2">
                    <span class="text-lg">💬</span>
                    <h3 class="font-black text-sm text-slate-900 uppercase">Gabinete de Dúvidas Bíblicas</h3>
                </div>
                <span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800">
                    {{ duvidas|length if duvidas else 0 }} pendente(s)
                </span>
            </div>

            {% if duvidas and duvidas|length > 0 %}
                <div class="space-y-3">
                    {% for d in duvidas %}
                    <div class="p-3.5 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
                        <div class="flex items-center justify-between text-xs">
                            <span class="font-bold text-slate-900">{{ d.nome_aluno or 'Aluno' }}</span>
                            <span class="text-[10px] text-slate-400">{{ d.criado_em or '' }}</span>
                        </div>
                        <p class="text-xs text-slate-700 italic">"{{ d.duvida or d.mensagem or '' }}"</p>
                    </div>
                    {% endfor %}
                </div>
            {% else %}
                <div class="p-5 text-center text-slate-400 text-xs italic bg-slate-50/50 rounded-xl border border-dashed border-slate-200">
                    Nenhuma dúvida bíblica enviada pelos formandos no momento.
                </div>
            {% endif %}
        </div>

        <!-- LISTA DE FORMANDOS & TURMAS (SEM BOTÕES DE CADASTRO) -->
        <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-100 pb-3 gap-2">
                <div class="flex items-center gap-2">
                    <span class="text-lg">📋</span>
                    <div>
                        <h3 class="font-black text-sm text-slate-900 uppercase">Lista de Formandos & Turmas</h3>
                        <p class="text-[11px] text-slate-400">Acompanhamento dos formandos alocados</p>
                    </div>
                </div>
                <span class="text-xs font-bold text-indigo-900 bg-indigo-50 px-3 py-1 rounded-xl self-start sm:self-auto">
                    {{ doutrina|length if doutrina else 0 }} Aluno(s) Alocado(s)
                </span>
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
                                    {% if a.usuario %}
                                    <span class="block text-[10px] text-slate-400 font-normal">Login: {{ a.usuario }}</span>
                                    {% endif %}
                                </td>
                                <td class="p-3 text-indigo-900 font-semibold">
                                    {{ a.classe or 'Discipulado' }}
                                </td>
                                <td class="p-3 text-slate-600">
                                    {{ a.professor or usuario_logado.nome or 'Pastor Dirigente' }}
                                </td>
                                <td class="p-3 text-amber-800 font-bold">
                                    {{ a.licao_atual or 'Lição 1' }}
                                </td>
                                <td class="p-3 text-center">
                                    <span class="px-2.5 py-0.5 rounded-full text-[10px] font-black bg-blue-100 text-blue-800">
                                        {{ a.presencas or 0 }}
                                    </span>
                                </td>
                                <td class="p-3 text-center">
                                    <span class="px-2.5 py-0.5 rounded-full text-[10px] font-black bg-emerald-100 text-emerald-800">
                                        {{ a.situacao or 'Em Formação' }}
                                    </span>
                                </td>
                            </tr>
                            {% endfor %}
                        {% else %}
                            <tr>
                                <td colspan="6" class="p-6 text-center text-slate-400 italic">
                                    Nenhum formando inscrito no momento.
                                </td>
                            </tr>
                        {% endif %}
                    </tbody>
                </table>
            </div>
        </div>

    </main>

</body>
</html>"""

with open(caminho_prof, 'w', encoding='utf-8') as f:
    f.write(html_professor)

env = jinja2.Environment()
env.parse(html_professor)
print("✓ templates/area_professor.html validado com sucesso!")

# =============================================================================
# 3. ATUALIZAR APP.PY: ROTA /professor E REDIRECIONAMENTO COMPULSÓRIO NO INDEX
# =============================================================================
with open(caminho_app, 'r', encoding='utf-8') as f:
    app_code = f.read()

# Rota /professor
rota_prof_code = '''
@app.route('/professor')
def area_professor():
    if not session.get('usuario'):
        return redirect(url_for('login'))
    usuario = session.get('usuario')
    doutrina = consultar_todos("SELECT * FROM doutrina ORDER BY id DESC")
    try:
        duvidas = consultar_todos("SELECT * FROM duvidas_alunos ORDER BY id DESC")
    except Exception:
        duvidas = []
    return render_template('area_professor.html',
                           usuario_logado=usuario,
                           doutrina=doutrina,
                           duvidas=duvidas)
'''

if "@app.route('/professor')" not in app_code:
    app_code = app_code + "\n" + rota_prof_code
    print("✓ Rota @app.route('/professor') adicionada em app.py!")

# Guarda compulsória na PRIMEIRA LINHA de index()
guarda_index = """    # REDIRECIONAR PROFESSOR PARA A SUA ÁREA EXCLUSIVA
    u_sess = session.get('usuario') or {}
    if any(p in str(u_sess.get('perfil', '')).lower() for p in ['prof', 'docente', 'instrutor']):
        return redirect('/professor')
"""

if "REDIRECIONAR PROFESSOR PARA A SUA ÁREA EXCLUSIVA" not in app_code:
    pos_idx = app_code.find("def index():")
    if pos_idx != -1:
        fim_idx_linha = app_code.find("\n", pos_idx) + 1
        app_code = app_code[:fim_idx_linha] + guarda_index + app_code[fim_idx_linha:]
        print("✓ Guarda compulsória ativada na entrada da rota index()!")

# Redirecionamento na rota de login
if "def login():" in app_code and "redirect('/professor')" not in app_code:
    pos_login = app_code.find("def login():")
    pos_sess = app_code.find("session['usuario'] = user", pos_login)
    if pos_sess != -1:
        fim_s = app_code.find('\n', pos_sess) + 1
        redir_log = "            if any(p in str(user.get('perfil', '')).lower() for p in ['prof', 'docente', 'instrutor']):\n                return redirect('/professor')\n"
        app_code = app_code[:fim_s] + redir_log + app_code[fim_s:]
        print("✓ Redirecionamento de login configurado para /professor!")

with open(caminho_app, 'w', encoding='utf-8') as f:
    f.write(app_code)

py_compile.compile(caminho_app, doraise=True)
print("✓ app.py validado e compilado com ZERO erros!")

# =============================================================================
# 4. ENVIAR PARA O GITHUB E O RENDER
# =============================================================================
subprocess.run(["git", "add", "app.py", "templates/dashboard.html", "templates/area_professor.html"], check=True)
subprocess.run(["git", "commit", "-m", "Arquitetura definitiva: tela dedicada do professor em /professor e guarda compulsoria na raiz"], check=True)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("=" * 80)
print(">>> ÁREA DEDICADA PUBLICADA COM SUCESSO ABSOLUTO! <<<")
print("=" * 80)