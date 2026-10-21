import os
import re
import py_compile
import jinja2

print("=" * 80)
print("A INTEGRAR PAINEL DE ENSINO: SITUAÇÃO GERAL, CADASTRO DE ALUNOS & PROFESSORES...")
print("=" * 80)

# =============================================================================
# 1. ATUALIZAR APP.PY: ROTAS DE PROFESSORES, DADOS E INDICADORES PEDAGÓGICOS
# =============================================================================
caminho_app = 'app.py'
with open(caminho_app, 'r', encoding='utf-8') as f:
    app_text = f.read()

# 1.1 Rota para cadastrar e excluir professores diretamente na aba doutrina
rotas_professores = """
# =============================================================================
# GESTÃO DE PROFESSORES E GABINETE PEDAGÓGICO
# =============================================================================
@app.route('/doutrina/gravar_professor', methods=['POST'])
def doutrina_gravar_professor():
    if not session.get('usuario_id'):
        return redirect('/login')
    if session.get('usuario_perfil') not in ['admin', 'pastor']:
        return "<script>alert('Apenas o Administrador ou Pastor pode cadastrar novos professores.'); window.location.href='/?aba=doutrina';</script>"

    cid = session.get('congregacao_id', 1)
    nome = request.form.get('nome_professor', '').strip()
    usuario = request.form.get('usuario_professor', '').strip().lower()
    senha = request.form.get('senha_professor', '').strip()

    if nome and usuario and senha:
        existe = consultar_um("SELECT id FROM usuarios_sistema WHERE usuario = ?", (usuario,))
        if existe:
            return "<script>alert('Este nome de usuário já existe! Por favor, escolha outro.'); window.location.href='/?aba=doutrina';</script>"
        
        executar_comando(
            "INSERT INTO usuarios_sistema (nome, usuario, senha, nivel, perfil, congregacao_id, criado_em) VALUES (?, ?, ?, 'local', 'professor', ?, ?)",
            (nome, usuario, senha, cid, datetime.now().strftime('%Y-%m-%d %H:%M'))
        )
    return redirect('/?aba=doutrina')

@app.route('/doutrina/professor/eliminar/<int:prof_id>')
def doutrina_eliminar_professor(prof_id):
    if not session.get('usuario_id') or session.get('usuario_perfil') not in ['admin', 'pastor']:
        return redirect('/?aba=doutrina')
    executar_comando("DELETE FROM usuarios_sistema WHERE id = ? AND perfil = 'professor'", (prof_id,))
    return redirect('/?aba=doutrina')
"""

if "/doutrina/gravar_professor" not in app_text:
    app_text = app_text.replace(
        "if __name__ == '__main__':",
        rotas_professores + "\nif __name__ == '__main__':"
    )

# 1.2 Injetar carregamento completo das variáveis de ensino na rota index()
bloco_dados_ensino = """
    # Carregar dados completos de Ensino & Doutrina
    professores_cadastrados = consultar_todos("SELECT * FROM usuarios_sistema WHERE perfil = 'professor' AND congregacao_id = ? ORDER BY nome ASC", (cid,))
    duvidas_pendentes = consultar_todos(\"\"\"
        SELECT d.*, a.nome_aluno as aluno_nome 
        FROM duvidas_alunos d 
        LEFT JOIN doutrina a ON d.aluno_id = a.id 
        WHERE d.resposta_professor IS NULL OR d.resposta_professor = '' 
        ORDER BY d.id DESC
    \"\"\")
    
    classes_padrao = [
        'Preparação para Batismo nas Águas',
        'Discipulado de Novos Convertidos',
        'Classe I - Primeiros Passos',
        'Classe II - Vida Cristã',
        'Classe III - Maturidade Cristã',
        'Classe IV - Candidatos ao Batismo'
    ]
    classes_db = [op['valor'] for op in opcoes if op.get('categoria') == 'classe_doutrina']
    lista_classes = list(dict.fromkeys(classes_padrao + classes_db))

    professores_padrao = ['Anselmo Leonardo Munguambe', 'Pastor Dirigente']
    nomes_prof_sistema = [p['nome'] for p in professores_cadastrados]
    lista_professores = list(dict.fromkeys(professores_padrao + nomes_prof_sistema))

    # Estatísticas de Ensino
    aptos_count = len([a for a in doutrina if a.get('situacao') == 'Apto / Aprovado'])
    stats_ensino = {
        'total_alunos': len(doutrina),
        'aptos': aptos_count,
        'em_formacao': len(doutrina) - aptos_count,
        'total_professores': len(professores_cadastrados),
        'total_duvidas': len(duvidas_pendentes)
    }
"""

if "stats_ensino = {" not in app_text:
    app_text = app_text.replace(
        "return render_template(",
        bloco_dados_ensino + "\n    return render_template("
    )
    # Adicionar aos parâmetros do template
    app_text = app_text.replace(
        "doutrina=doutrina,",
        "doutrina=doutrina,\n        professores_cadastrados=professores_cadastrados,\n        duvidas_pendentes=duvidas_pendentes,\n        lista_classes=lista_classes,\n        lista_professores=lista_professores,\n        stats_ensino=stats_ensino,"
    )

with open(caminho_app, 'w', encoding='utf-8') as f:
    f.write(app_text)

try:
    py_compile.compile(caminho_app, doraise=True)
    print("✓ app.py: Rotas e estatísticas de ensino compiladas com sucesso!")
except Exception as e:
    print(f"Erro em app.py: {e}")
    exit(1)

# =============================================================================
# 2. ATUALIZAR TEMPLATES/DASHBOARD.HTML (INTERFACE INTEGRADA DE DOUTRINA)
# =============================================================================
caminho_dash = os.path.join('templates', 'dashboard.html')
with open(caminho_dash, 'r', encoding='utf-8') as f:
    dash_html = f.read()

bloco_antigo_doutrina = r'{% if aba_ativa == \'doutrina\' %}[\s\S]*?{% if aba_ativa == \'configuracoes\' %}'

bloco_novo_doutrina = """{% if aba_ativa == 'doutrina' %}
        <!-- CABEÇALHO DO MÓDULO PEDAGÓGICO -->
        <div class="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white p-6 rounded-3xl shadow-xl mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
                <div class="inline-flex items-center gap-2 bg-amber-500/20 text-amber-300 px-3 py-1 rounded-full text-[10px] font-black uppercase mb-1 border border-amber-400/30">
                    <span>📖</span> ESCOLA MINISTERIAL & DOUTRINA BÍBLICA
                </div>
                <h2 class="text-2xl font-black">Situação Geral de Ensino, Formandos & Instrutores</h2>
                <p class="text-xs text-indigo-200 mt-0.5">Acompanhamento curricular, aprovação para Batismo nas Águas e credenciamento docente</p>
            </div>
            <div class="flex gap-2">
                <a href="/ensino/aulas" target="_blank" class="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl text-xs shadow flex items-center gap-1.5 transition">
                    <span>🎓</span><span>Abrir Sala de Aula do Aluno ↗</span>
                </a>
            </div>
        </div>

        <!-- JANELA 1: SITUAÇÃO GERAL DO ENSINO (DASHBOARD ANALÍTICO) -->
        <div class="mb-6 space-y-4">
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
                <div class="bg-white p-5 rounded-2xl shadow-sm border-l-4 border-indigo-600 border-slate-200">
                    <span class="text-slate-500 text-[10px] font-bold uppercase block">Total de Formandos</span>
                    <span class="text-2xl font-black text-indigo-950 mt-1 block">{{ stats_ensino.total_alunos if stats_ensino else doutrina|length }} Alunos</span>
                    <span class="text-[10px] text-slate-400">Inscritos no currículo oficial</span>
                </div>
                <div class="bg-white p-5 rounded-2xl shadow-sm border-l-4 border-emerald-500 border-slate-200">
                    <span class="text-slate-500 text-[10px] font-bold uppercase block">Aptos / Prontos para Batismo</span>
                    <span class="text-2xl font-black text-emerald-700 mt-1 block">🌊 {{ stats_ensino.aptos if stats_ensino else 0 }} Prontos</span>
                    <span class="text-[10px] text-emerald-600 font-bold">Aproveitamento >= 70%</span>
                </div>
                <div class="bg-white p-5 rounded-2xl shadow-sm border-l-4 border-amber-500 border-slate-200">
                    <span class="text-slate-500 text-[10px] font-bold uppercase block">Em Formação Ativa</span>
                    <span class="text-2xl font-black text-amber-700 mt-1 block">📖 {{ stats_ensino.em_formacao if stats_ensino else 0 }} Alunos</span>
                    <span class="text-[10px] text-slate-400">Em estudo nas classes</span>
                </div>
                <div class="bg-white p-5 rounded-2xl shadow-sm border-l-4 border-blue-500 border-slate-200">
                    <span class="text-slate-500 text-[10px] font-bold uppercase block">Corpo Docente</span>
                    <span class="text-2xl font-black text-blue-900 mt-1 block">👨‍🏫 {{ professores_cadastrados|length }} Instrutor(es)</span>
                    <span class="text-[10px] text-slate-400">Com credencial de ensino</span>
                </div>
            </div>

            <!-- DISTRIBUIÇÃO DAS CLASSES -->
            <div class="bg-white p-4.5 rounded-2xl shadow-sm border border-slate-200 text-xs flex flex-wrap items-center justify-between gap-3">
                <span class="font-extrabold text-slate-700 uppercase text-[11px]">Classes em Funcionamento:</span>
                <div class="flex flex-wrap gap-2">
                    {% for cl in lista_classes %}
                    <span class="px-3 py-1 bg-slate-100 hover:bg-slate-200 text-slate-800 rounded-lg font-bold text-[11px] border border-slate-200">
                        {{ cl }}
                    </span>
                    {% endfor %}
                </div>
            </div>
        </div>

        <!-- JANELA 2: GABINETE DO INSTRUTOR (DÚVIDAS BÍBLICAS PENDENTES) -->
        <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 mb-6 space-y-3">
            <div class="flex justify-between items-center border-b pb-3">
                <div class="flex items-center gap-2">
                    <span class="text-xl">👨‍🏫</span>
                    <div>
                        <h3 class="font-black text-sm text-slate-900 uppercase">Gabinete do Instrutor: Dúvidas Bíblicas dos Formandos</h3>
                        <p class="text-xs text-slate-500">Responda às questões enviadas pelos alunos durante as lições.</p>
                    </div>
                </div>
                <span class="bg-amber-100 text-amber-900 px-3 py-1 rounded-full text-xs font-black">
                    {{ duvidas_pendentes|length if duvidas_pendentes else 0 }} Pendente(s)
                </span>
            </div>

            <div class="space-y-3 pt-1">
                {% for d in duvidas_pendentes %}
                <div class="p-4 bg-amber-50/60 border border-amber-300 rounded-2xl space-y-2 text-xs">
                    <div class="flex justify-between items-center font-bold text-slate-800">
                        <span class="text-indigo-900">👤 Formando: {{ d.aluno_nome or 'Aluno' }} • Lição: {{ d.licao_id }}</span>
                        <span class="text-[10px] text-slate-400">{{ d.criado_em }}</span>
                    </div>
                    <p class="font-bold text-slate-900 italic bg-white p-2.5 rounded-xl border border-amber-200">
                        "{{ d.pergunta }}"
                    </p>
                    <form action="/ensino/responder_duvida" method="POST" class="flex gap-2 pt-1">
                        <input type="hidden" name="duvida_id" value="{{ d.id }}">
                        <input type="text" name="resposta" required placeholder="Escreva aqui a resposta bíblica e conselho pastoral..." class="flex-1 h-10 px-3 border-2 border-slate-300 rounded-xl bg-white text-xs focus:border-indigo-600 focus:outline-none">
                        <button type="submit" class="px-4 h-10 bg-indigo-900 hover:bg-indigo-950 text-white font-bold rounded-xl text-xs shadow cursor-pointer">
                            Enviar Resposta →
                        </button>
                    </form>
                </div>
                {% else %}
                <p class="text-xs text-slate-400 italic text-center py-2">Glória a Deus! Nenhuma dúvida bíblica pendente no momento.</p>
                {% endfor %}
            </div>
        </div>

        <!-- JANELA 3: ÁREA DE CADASTROS (ALUNOS & PROFESSORES) -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-6">

            <!-- FORMULÁRIO 1: INSCREVER FORMANDO (COM SELETORES PERFEITOS) -->
            <div class="lg:col-span-7 bg-white p-6 rounded-2xl shadow-sm border border-slate-200 space-y-4">
                <div class="border-b pb-3">
                    <h3 class="font-black text-sm text-slate-900 uppercase flex items-center gap-2">
                        <span>🎓</span> 1. Inscrever Formando com Login
                    </h3>
                    <p class="text-[11px] text-slate-500">Cria o acesso do aluno para estudar na App de Ensino</p>
                </div>

                <form action="/doutrina/gravar" method="POST" class="space-y-3 text-xs">
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">Nome Completo do Aluno *</label>
                        <input type="text" name="nome_aluno" required placeholder="Ex: Jacinto Manuel Bata Saranga" class="w-full h-11 px-3 border border-slate-300 rounded-xl focus:border-indigo-600 focus:outline-none">
                    </div>

                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        <div class="min-w-0">
                            <label class="block font-bold text-slate-700 mb-1">Classe *</label>
                            <select name="classe" required class="w-full h-11 px-3 border border-slate-300 rounded-xl bg-white font-bold text-xs text-slate-800 focus:border-indigo-600 focus:outline-none shadow-sm cursor-pointer truncate">
                                {% for cl in lista_classes %}
                                <option value="{{ cl }}">{{ cl }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        <div class="min-w-0">
                            <label class="block font-bold text-slate-700 mb-1">Instrutor / Mentor *</label>
                            <select name="professor" required class="w-full h-11 px-3 border border-slate-300 rounded-xl bg-white font-bold text-xs text-slate-800 focus:border-indigo-600 focus:outline-none shadow-sm cursor-pointer truncate">
                                {% for prof in lista_professores %}
                                <option value="{{ prof }}">{{ prof }}</option>
                                {% endfor %}
                            </select>
                        </div>
                    </div>

                    <!-- CAIXA DOURADA: CREDENCIAIS DO FORMANDO -->
                    <div class="p-3.5 bg-amber-50/80 border border-amber-200 rounded-xl space-y-2">
                        <span class="font-extrabold text-[10px] uppercase text-amber-900 block tracking-wide">
                            🔑 CREDENCIAIS DO ALUNO PARA O APLICATIVO
                        </span>
                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <label class="block text-[10px] font-bold text-slate-600">Usuário:</label>
                                <input type="text" name="usuario" required placeholder="Ex: jsaranga" class="w-full h-8 px-2 border border-amber-300 rounded-lg bg-white font-bold text-xs">
                            </div>
                            <div>
                                <label class="block text-[10px] font-bold text-slate-600">Senha Inicial:</label>
                                <input type="text" name="senha" required value="123456" class="w-full h-8 px-2 border border-amber-300 rounded-lg bg-white font-bold text-xs">
                            </div>
                        </div>
                    </div>

                    <div>
                        <label class="block font-bold text-slate-700 mb-1">Data Início</label>
                        <input type="date" name="data_inicio" class="w-full h-10 px-3 border border-slate-300 rounded-xl focus:border-indigo-600 focus:outline-none">
                    </div>

                    <button type="submit" class="w-full py-3 bg-amber-600 hover:bg-amber-700 text-white font-black rounded-xl shadow cursor-pointer text-xs transition">
                        Gravar Inscrição & Credenciais
                    </button>
                </form>
            </div>

            <!-- FORMULÁRIO 2: CADASTRAR PROFESSOR / INSTRUTOR -->
            <div class="lg:col-span-5 bg-white p-6 rounded-2xl shadow-sm border border-slate-200 space-y-4">
                <div class="border-b pb-3">
                    <h3 class="font-black text-sm text-slate-900 uppercase flex items-center gap-2">
                        <span>👨‍🏫</span> 2. Cadastrar Professor / Instrutor
                    </h3>
                    <p class="text-[11px] text-slate-500">Credencia um docente com login restrito ao ensino</p>
                </div>

                <form action="/doutrina/gravar_professor" method="POST" class="space-y-3 text-xs">
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">Nome Completo do Professor *</label>
                        <input type="text" name="nome_professor" required placeholder="Ex: Diác. Paulo Mateus" class="w-full h-11 px-3 border border-slate-300 rounded-xl focus:border-indigo-600 focus:outline-none">
                    </div>

                    <div class="p-3.5 bg-indigo-50/80 border border-indigo-200 rounded-xl space-y-2">
                        <span class="font-extrabold text-[10px] uppercase text-indigo-900 block tracking-wide">
                            🔐 ACESSO DO PROFESSOR AO SISTEMA
                        </span>
                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <label class="block text-[10px] font-bold text-slate-600">Usuário:</label>
                                <input type="text" name="usuario_professor" required placeholder="Ex: prof.paulo" class="w-full h-8 px-2 border border-indigo-300 rounded-lg bg-white font-bold text-xs">
                            </div>
                            <div>
                                <label class="block text-[10px] font-bold text-slate-600">Senha:</label>
                                <input type="text" name="senha_professor" required value="prof123" class="w-full h-8 px-2 border border-indigo-300 rounded-lg bg-white font-bold text-xs">
                            </div>
                        </div>
                    </div>

                    <div class="p-3 bg-slate-50 rounded-xl border border-slate-200 text-[10px] text-slate-500">
                        ℹ️ <b>Privacidade garantida:</b> O professor apenas terá acesso ao acompanhamento dos formandos e resposta às dúvidas, sem visualização financeira.
                    </div>

                    <button type="submit" class="w-full py-3 bg-indigo-900 hover:bg-indigo-950 text-white font-black rounded-xl shadow cursor-pointer text-xs transition">
                        Credenciar Professor / Instrutor
                    </button>
                </form>
            </div>

        </div>

        <!-- JANELA 4: LISTAGENS DE ACOMPANHAMENTO (ALUNOS & PROFESSORES) -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">

            <!-- TABELA DE FORMANDOS & SITUAÇÃO DE ENSINO -->
            <div class="lg:col-span-8 bg-white p-6 rounded-2xl shadow-sm border border-slate-200 space-y-4">
                <div class="flex justify-between items-center border-b pb-3">
                    <div>
                        <h3 class="font-black text-sm text-slate-900 uppercase flex items-center gap-2">
                            <span>📋</span> Lista de Formandos & Progresso Curricular
                        </h3>
                        <p class="text-xs text-slate-500">Aproveitamento nos testes e aptidão ao Batismo</p>
                    </div>
                    <span class="text-xs text-indigo-900 font-bold">{{ doutrina|length }} Formando(s)</span>
                </div>

                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs border-collapse">
                        <thead>
                            <tr class="bg-slate-100 text-slate-700 font-bold uppercase text-[10px]">
                                <th class="p-2.5">Aluno & Credenciais</th>
                                <th class="p-2.5">Classe & Mentor</th>
                                <th class="p-2.5 text-center">Aproveitamento</th>
                                <th class="p-2.5 text-center">Situação</th>
                                <th class="p-2.5 text-center">Ações</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for a in doutrina %}
                            <tr class="border-b hover:bg-slate-50">
                                <td class="p-2.5 font-bold text-slate-900">
                                    {{ a.nome_aluno }}
                                    <span class="block text-[10px] text-slate-400 font-normal">
                                        Usuário: <b class="text-indigo-900">{{ a.usuario or 'Sem login' }}</b> | Senha: <b>{{ a.senha or '******' }}</b>
                                    </span>
                                </td>
                                <td class="p-2.5 text-slate-700">
                                    <span class="font-bold block">{{ a.classe }}</span>
                                    <span class="text-[10px] text-slate-500">Mentor: {{ a.professor or 'Pastor' }}</span>
                                </td>
                                <td class="p-2.5 text-center">
                                    <span class="inline-block px-2.5 py-0.5 rounded-full text-xs font-black {% if (a.aproveitamento or 0) >= 70 %}bg-emerald-100 text-emerald-800{% else %}bg-amber-100 text-amber-800{% endif %}">
                                        {{ "%.0f"|format(a.aproveitamento or 0) }}%
                                    </span>
                                </td>
                                <td class="p-2.5 text-center">
                                    {% if a.situacao == 'Apto / Aprovado' %}
                                    <span class="bg-emerald-100 text-emerald-900 px-2.5 py-1 rounded-full font-black text-[10px]">
                                        ✅ Apto p/ Batismo
                                    </span>
                                    {% else %}
                                    <span class="bg-blue-100 text-blue-900 px-2.5 py-1 rounded-full font-bold text-[10px]">
                                        Em Formação
                                    </span>
                                    {% endif %}
                                </td>
                                <td class="p-2.5 text-center">
                                    <div class="flex items-center justify-center gap-1.5">
                                        {% if a.situacao != 'Apto / Aprovado' and (a.aproveitamento or 0) >= 70 %}
                                        <a href="/doutrina/aprovar/{{ a.id }}" class="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-[10px] font-black shadow" title="Aprovar para Batismo">
                                            Aprovar
                                        </a>
                                        {% endif %}
                                        <a href="/doutrina/eliminar/{{ a.id }}" onclick="return confirm('Deseja realmente remover este formando?')" class="p-1 text-rose-500 hover:text-rose-700" title="Eliminar Formando">
                                            🗑️
                                        </a>
                                    </div>
                                </td>
                            </tr>
                            {% else %}
                            <tr>
                                <td colspan="5" class="p-4 text-center text-slate-400 italic">Nenhum formando inscrito ainda.</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- QUADRO DE PROFESSORES / INSTRUTORES REGISTADOS -->
            <div class="lg:col-span-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-200 space-y-4">
                <div class="flex justify-between items-center border-b pb-3">
                    <div>
                        <h3 class="font-black text-sm text-slate-900 uppercase flex items-center gap-2">
                            <span>👨‍🏫</span> Professores Ativos
                        </h3>
                        <p class="text-[11px] text-slate-500">Docentes com permissão de ensino</p>
                    </div>
                    <span class="text-xs text-indigo-900 font-bold">{{ professores_cadastrados|length }}</span>
                </div>

                <div class="space-y-2.5 text-xs">
                    {% for p in professores_cadastrados %}
                    <div class="p-3 bg-slate-50 rounded-xl border border-slate-200 flex justify-between items-center">
                        <div>
                            <span class="font-bold text-slate-900 block">{{ p.nome }}</span>
                            <span class="text-[10px] text-slate-500">Usuário: <b class="text-indigo-900">{{ p.usuario }}</b></span>
                        </div>
                        <a href="/doutrina/professor/eliminar/{{ p.id }}" onclick="return confirm('Deseja remover o acesso deste professor?')" class="text-rose-500 hover:text-rose-700 p-1" title="Remover Professor">
                            🗑️
                        </a>
                    </div>
                    {% else %}
                    <p class="text-slate-400 italic text-center py-4">Nenhum professor cadastrado ainda.</p>
                    {% endfor %}
                </div>
            </div>

        </div>
        {% endif %}

        {% if aba_ativa == 'configuracoes' %}"""

dash_html = re.sub(bloco_antigo_doutrina, bloco_novo_doutrina, dash_html)

env = jinja2.Environment()
env.parse(dash_html)
with open(caminho_dash, 'w', encoding='utf-8') as f:
    f.write(dash_html)

print("✓ templates/dashboard.html atualizado e validado sem erros!")
print("=" * 80)
print(">>> TUDO PRONTO! EXECUTE O SCRIPT E FAÇA O PUSH PARA O GITHUB! <<<")
print("=" * 80)