import os
import re
import py_compile
import jinja2

print("=" * 80)
print("A CONFIGURAR PAINEL DO PROFESSOR, DASHBOARD PEDAGÓGICO E FICHA DO ALUNO...")
print("=" * 80)

# =============================================================================
# 1. ATUALIZAR APP.PY: PERFIL DO PROFESSOR, ROTA DE RESPOSTA E DADOS DO ALUNO
# =============================================================================
caminho_app = 'app.py'
with open(caminho_app, 'r', encoding='utf-8') as f:
    app_text = f.read()

# 1.1 Redirecionamento de login para perfil 'professor'
if "perfil == 'professor'" not in app_text:
    app_text = app_text.replace(
        "elif perfil == 'tesoureiro':\n            return redirect('/?aba=tesouraria')",
        "elif perfil == 'tesoureiro':\n            return redirect('/?aba=tesouraria')\n        elif perfil == 'professor':\n            return redirect('/?aba=doutrina')"
    )

# 1.2 Restringir abas para o perfil professor no index
filtro_professor = """    if perfil == 'professor' and aba_ativa not in ['doutrina']:
        aba_ativa = 'doutrina'"""
if "perfil == 'professor' and aba_ativa not in ['doutrina']" not in app_text:
    app_text = app_text.replace(
        "if perfil == 'secretario' and aba_ativa in ['financas', 'tesouraria']:\n        aba_ativa = 'membros'",
        "if perfil == 'secretario' and aba_ativa in ['financas', 'tesouraria']:\n        aba_ativa = 'membros'\n" + filtro_professor
    )

# 1.3 Adicionar rota para o professor responder dúvidas bíblicas
rota_resposta_duvida = """
# =============================================================================
# GABINETE DO PROFESSOR: RESPONDER DÚVIDAS DOS ALUNOS
# =============================================================================
@app.route('/ensino/responder_duvida', methods=['POST'])
def ensino_responder_duvida():
    if not session.get('usuario_id'):
        return redirect('/login')

    duvida_id = request.form.get('duvida_id')
    resposta = request.form.get('resposta', '').strip()
    u_nome = session.get('usuario_nome', 'Professor')

    if duvida_id and resposta:
        executar_comando(
            "UPDATE duvidas_alunos SET resposta_professor = ?, professor_nome = ? WHERE id = ?",
            (resposta, u_nome, duvida_id)
        )
    return redirect('/?aba=doutrina')
"""

if "/ensino/responder_duvida" not in app_text:
    app_text = app_text.replace(
        "if __name__ == '__main__':",
        rota_resposta_duvida + "\nif __name__ == '__main__':"
    )

# 1.4 Garantir conta padrão de Professor no Supabase / Banco
conta_prof_sql = """
    # Garantir conta de professor ativa
    if not consultar_um("SELECT id FROM usuarios_sistema WHERE usuario = 'professor'"):
        executar_comando("INSERT INTO usuarios_sistema (nome, usuario, senha, nivel, perfil, congregacao_id, criado_em) VALUES ('Professor de Doutrina', 'professor', 'prof123', 'local', 'professor', 1, '2026-10-19 23:00')")
"""
if "SELECT id FROM usuarios_sistema WHERE usuario = 'professor'" not in app_text:
    app_text = app_text.replace("inicializar_banco()\n", "inicializar_banco()\n" + conta_prof_sql + "\n")

with open(caminho_app, 'w', encoding='utf-8') as f:
    f.write(app_text)

try:
    py_compile.compile(caminho_app, doraise=True)
    print("✓ app.py: Lógica do Professor e rotas pedagógicas integradas!")
except Exception as e:
    print(f"Erro em app.py: {e}")
    exit(1)

# =============================================================================
# 2. ATUALIZAR TEMPLATES/DASHBOARD.HTML (DASHBOARD PEDAGÓGICO E GABINETE)
# =============================================================================
caminho_dash = os.path.join('templates', 'dashboard.html')
with open(caminho_dash, 'r', encoding='utf-8') as f:
    dash_html = f.read()

# 2.1 Ajustar visibilidade da barra lateral para o Professor
dash_html = re.sub(
    r'<!-- MENU LATERAL -->[\s\S]*?Finanças & Tesouraria',
    """<!-- MENU LATERAL -->
        <nav class="space-y-1.5 text-xs font-semibold">
            {% if usuario_logado and usuario_logado.perfil != 'professor' %}
            <a href="/?aba=dashboard" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'dashboard' %}bg-indigo-600 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                <span>📊</span><span>Raio-X Demográfico</span>
            </a>

            <div class="pt-4 pb-1 px-3 text-[10px] uppercase font-bold text-slate-500 tracking-wider">Geral & Frequência</div>
            
            <a href="/?aba=membros" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'membros' %}bg-indigo-600 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                <span>👥</span><span>1. Membros ({{ total_membros }})</span>
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
            <a href="/?aba=actos" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'actos' %}bg-indigo-600 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                <span>💍</span><span>Actos (Casamentos & Óbitos)</span>
            </a>
            {% endif %}

            <div class="pt-4 pb-1 px-3 text-[10px] uppercase font-bold text-slate-500 tracking-wider">Ensino & Formação</div>

            <a href="/?aba=doutrina" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition {% if aba_ativa == 'doutrina' %}bg-amber-600 text-white shadow-md font-bold{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                <span>📖</span><span>7. Doutrina & Batismo</span>
            </a>
            <a href="/ensino/aulas" target="_blank" class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-blue-300 hover:bg-slate-800 transition">
                <span>🎓</span><span>Sala de Aula (Aluno) ↗</span>
            </a>

            {% if usuario_logado and usuario_logado.perfil not in ['secretario', 'professor'] %}
            <div class="pt-4 pb-1 px-3 text-[10px] uppercase font-bold text-slate-500 tracking-wider">Finanças & Tesouraria""",
    dash_html
)

# 2.2 Reconstruir o conteúdo da aba 'doutrina' com o Dashboard Pedagógico completo
bloco_antigo_doutrina = r'{% if aba_ativa == \'doutrina\' %}[\s\S]*?{% if aba_ativa == \'configuracoes\' %}'

bloco_novo_doutrina = """{% if aba_ativa == 'doutrina' %}
        <!-- CABEÇALHO DO MÓDULO PEDAGÓGICO -->
        <div class="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white p-6 rounded-3xl shadow-xl mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
                <div class="inline-flex items-center gap-2 bg-amber-500/20 text-amber-300 px-3 py-1 rounded-full text-[10px] font-black uppercase mb-1 border border-amber-400/30">
                    <span>📖</span> ESCOLA MINISTERIAL & DOUTRINA BÍBLICA
                </div>
                <h2 class="text-2xl font-black">Painel de Acompanhamento do Alunado</h2>
                <p class="text-xs text-indigo-200 mt-0.5">Gestão pedagógica, progresso curricular e preparação para o Batismo nas Águas</p>
            </div>
            <div class="flex gap-2">
                <a href="/ensino/aulas" target="_blank" class="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl text-xs shadow flex items-center gap-1.5 transition">
                    <span>🎓</span><span>Ver Sala de Aula Virtual ↗</span>
                </a>
            </div>
        </div>

        <!-- 4 CARDS: DASHBOARD DE INDICADORES DO ALUNADO -->
        {% set total_alunos = doutrina|length %}
        {% set aptos = doutrina|selectattr('situacao', 'equalto', 'Apto / Aprovado')|list|length %}
        {% set em_formacao = total_alunos - aptos %}
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6 text-xs">
            <div class="bg-white p-4.5 rounded-2xl shadow-sm border-l-4 border-indigo-600 border-slate-200">
                <span class="text-slate-500 text-[10px] font-bold uppercase block">Total de Formandos</span>
                <span class="text-2xl font-black text-indigo-950 mt-1 block">{{ total_alunos }} Alunos</span>
                <span class="text-[10px] text-slate-400">Inscritos no currículo oficial</span>
            </div>
            <div class="bg-white p-4.5 rounded-2xl shadow-sm border-l-4 border-emerald-500 border-slate-200">
                <span class="text-slate-500 text-[10px] font-bold uppercase block">Aptos / Batismo Concluído</span>
                <span class="text-2xl font-black text-emerald-700 mt-1 block">🌊 {{ aptos }} Prontos</span>
                <span class="text-[10px] text-emerald-600 font-bold">Aproveitamento >= 70%</span>
            </div>
            <div class="bg-white p-4.5 rounded-2xl shadow-sm border-l-4 border-amber-500 border-slate-200">
                <span class="text-slate-500 text-[10px] font-bold uppercase block">Em Formação Ativa</span>
                <span class="text-2xl font-black text-amber-700 mt-1 block">📖 {{ em_formacao }} Alunos</span>
                <span class="text-[10px] text-slate-400">Em estudo nas classes</span>
            </div>
            <div class="bg-white p-4.5 rounded-2xl shadow-sm border-l-4 border-blue-500 border-slate-200">
                <span class="text-slate-500 text-[10px] font-bold uppercase block">Perfil Conectado</span>
                <span class="text-xl font-black text-slate-800 mt-1 block truncate">{{ usuario_logado.nome }}</span>
                <span class="text-[10px] text-indigo-600 font-bold uppercase">{{ usuario_logado.perfil }}</span>
            </div>
        </div>

        <!-- GABINETE DO INSTRUTOR: DÚVIDAS BÍBLICAS PENDENTES -->
        <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 mb-6 space-y-3">
            <div class="flex justify-between items-center border-b pb-3">
                <div class="flex items-center gap-2">
                    <span class="text-xl">👨‍🏫</span>
                    <div>
                        <h3 class="font-black text-sm text-slate-900 uppercase">Gabinete do Instrutor: Dúvidas Bíblicas dos Formandos</h3>
                        <p class="text-xs text-slate-500">Responda diretamente às perguntas bíblicas enviadas pelos alunos na sala de aula.</p>
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
                        <input type="text" name="resposta" required placeholder="Escreva a resposta bíblica e conselho pastoral para o aluno..." class="flex-1 h-10 px-3 border-2 border-slate-300 rounded-xl bg-white text-xs focus:border-indigo-600 focus:outline-none">
                        <button type="submit" class="px-4 h-10 bg-indigo-900 hover:bg-indigo-950 text-white font-bold rounded-xl text-xs shadow cursor-pointer">
                            Enviar Resposta →
                        </button>
                    </form>
                </div>
                {% else %}
                <p class="text-xs text-slate-400 italic text-center py-3">Glória a Deus! Nenhuma dúvida bíblica pendente no momento.</p>
                {% endfor %}
            </div>
        </div>

        <!-- FORMULÁRIO DE INSCRIÇÃO & TABELA DE ALUNOS COM FICHA DE DESEMPENHO -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">

            <!-- COLUNA ESQUERDA: INSCREVER FORMANDO COM LOGIN -->
            <div class="lg:col-span-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-200 space-y-4">
                <div class="border-b pb-3">
                    <h3 class="font-black text-sm text-slate-900 uppercase flex items-center gap-2">
                        <span>🎓</span> Inscrever Formando com Login
                    </h3>
                    <p class="text-[11px] text-slate-500">Crie o acesso para o aluno entrar no app no telemóvel</p>
                </div>

                <form action="/doutrina/gravar" method="POST" class="space-y-3 text-xs">
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">Nome Completo do Aluno *</label>
                        <input type="text" name="nome_aluno" required placeholder="Nome do formando" class="w-full h-10 px-3 border border-slate-300 rounded-xl focus:border-indigo-600 focus:outline-none">
                    </div>

                    <div class="grid grid-cols-2 gap-2">
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">Classe *</label>
                            <select name="classe" class="w-full h-10 px-2 border border-slate-300 rounded-xl focus:border-indigo-600 focus:outline-none font-bold text-[11px]">
                                <option value="Classe I - Primeiros Passos">Classe I - Primeiros Passos</option>
                                <option value="Classe II - Vida Cristã">Classe II - Vida Cristã</option>
                                <option value="Classe III - Maturidade">Classe III - Maturidade</option>
                                <option value="Classe IV - Candidatos ao Batismo">Classe IV - Batismo</option>
                            </select>
                        </div>
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">Instrutor / Mentor</label>
                            <input type="text" name="professor" value="{{ usuario_logado.nome if usuario_logado.perfil == 'professor' else '' }}" placeholder="Nome do Instrutor" class="w-full h-10 px-2 border border-slate-300 rounded-xl focus:border-indigo-600 focus:outline-none">
                        </div>
                    </div>

                    <!-- CAIXA DOURADA: CREDENCIAIS DE ACESSO -->
                    <div class="p-3 bg-amber-50/80 border border-amber-200 rounded-xl space-y-2">
                        <span class="font-extrabold text-[10px] uppercase text-amber-900 block">ACESSO À ÁREA DE ENSINO DO ALUNO</span>
                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <label class="block text-[10px] font-bold text-slate-600">Usuário:</label>
                                <input type="text" name="usuario" required placeholder="Ex: anselmo" class="w-full h-8 px-2 border border-amber-300 rounded-lg bg-white font-bold text-xs">
                            </div>
                            <div>
                                <label class="block text-[10px] font-bold text-slate-600">Senha:</label>
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

            <!-- COLUNA DIREITA: LISTA DE FORMANDOS COM FICHA & NOTAS DETALHADAS -->
            <div class="lg:col-span-8 bg-white p-6 rounded-2xl shadow-sm border border-slate-200 space-y-4">
                <div class="flex justify-between items-center border-b pb-3">
                    <div>
                        <h3 class="font-black text-sm text-slate-900 uppercase flex items-center gap-2">
                            <span>📋</span> Lista de Formandos & Registo de Acompanhamento
                        </h3>
                        <p class="text-xs text-slate-500">Controlo de frequência, aproveitamento e liberação batismal</p>
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
                                    <span class="bg-emerald-100 text-emerald-900 px-2 py-0.5 rounded-full font-black text-[10px]">
                                        ✅ Apto / Aprovado
                                    </span>
                                    {% else %}
                                    <span class="bg-blue-100 text-blue-900 px-2 py-0.5 rounded-full font-bold text-[10px]">
                                        Em Formação
                                    </span>
                                    {% endif %}
                                </td>
                                <td class="p-2.5 text-center">
                                    <div class="flex items-center justify-center gap-1.5">
                                        {% if a.situacao != 'Apto / Aprovado' and (a.aproveitamento or 0) >= 70 %}
                                        <a href="/doutrina/aprovar/{{ a.id }}" class="px-2 py-1 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-[10px] font-black shadow" title="Aprovar para Batismo">
                                            Aprovar
                                        </a>
                                        {% endif %}
                                        <a href="/doutrina/eliminar/{{ a.id }}" onclick="return confirm('Deseja realmente remover este formando?')" class="p-1 text-rose-500 hover:text-rose-700" title="Eliminar Inscrição">
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

        </div>
        {% endif %}

        {% if aba_ativa == 'configuracoes' %}"""

dash_html = re.sub(bloco_antigo_doutrina, bloco_novo_doutrina, dash_html)

# Validar sintaxe Jinja2
env = jinja2.Environment()
env.parse(dash_html)

with open(caminho_dash, 'w', encoding='utf-8') as f:
    f.write(dash_html)
print("✓ templates/dashboard.html atualizado com o Dashboard Pedagógico e Gabinete do Professor!")

print("=" * 80)
print(">>> ATUALIZAÇÃO CONCLUÍDA COM TOTAL SUCESSO! <<<")
print("=" * 80)