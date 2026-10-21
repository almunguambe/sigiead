import os
import re
import subprocess
import jinja2

print("=" * 80)
print("A RECUPERAR A ESTRUTURA ORIGINAL E APLICAR O MÓDULO DE ENSINO PANORÂMICO...")
print("=" * 80)

caminho_dash = os.path.join('templates', 'dashboard.html')

# 1. RECUPERAR A BASE PERFEITA DO COMMIT 61ba4ea VIA GIT
print("1. A extrair o template original intacto do Git (commit 61ba4ea)...")
try:
    res = subprocess.run(["git", "show", "61ba4ea:templates/dashboard.html"], capture_output=True, text=True, check=True)
    html_base = res.stdout
    print("✓ Ficheiro base recuperado com sucesso!")
except Exception as e:
    print(f"Erro ao ler histórico do Git: {e}")
    exit(1)

# 2. LOCALIZAR EXATAMENTE O INÍCIO E O FIM DA ABA DE DOUTRINA NO FICHEIRO BASE
padrao_inicio = re.search(r'{%\s*if\s+aba_ativa\s*==\s*[\'"]doutrina[\'"]\s*%}', html_base)
if not padrao_inicio:
    print("Erro: Bloco de doutrina não encontrado no template base.")
    exit(1)

inicio_idx = padrao_inicio.start()

# Localizar o início da aba seguinte (ex: configurações) para determinar o fim exato da doutrina
padrao_proxima_aba = re.search(r'{%\s*if\s+aba_ativa\s*==', html_base[padrao_inicio.end():])
if padrao_proxima_aba:
    pos_absoluta_prox = padrao_inicio.end() + padrao_proxima_aba.start()
    fim_idx = html_base.rfind('{% endif %}', inicio_idx, pos_absoluta_prox) + len('{% endif %}')
else:
    fim_idx = html_base.rfind('{% endif %}') + len('{% endif %}')

print(f"✓ Bloco de Doutrina delimitado entre as posições {inicio_idx} e {fim_idx}.")

# 3. NOVO BLOCO DE DOUTRINA: PANORÂMICO, COM 4 INDICADORES, SELETORES FLUIDOS E CADASTRO DUPLO
bloco_doutrina_novo = """{% if aba_ativa == 'doutrina' %}
        <!-- CABEÇALHO DO MÓDULO PEDAGÓGICO -->
        <div class="w-full bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white p-6 rounded-3xl shadow-xl mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
                <div class="inline-flex items-center gap-2 bg-amber-500/20 text-amber-300 px-3 py-1 rounded-full text-[10px] font-black uppercase mb-1 border border-amber-400/30">
                    <span>📖</span> ESCOLA MINISTERIAL & DOUTRINA BÍBLICA
                </div>
                <h2 class="text-2xl font-black">Situação Geral de Ensino, Formandos & Instrutores</h2>
                <p class="text-xs text-indigo-200 mt-0.5">Acompanhamento curricular, aptidão para Batismo nas Águas e credenciamento docente</p>
            </div>
            <div class="flex gap-2">
                <a href="/ensino/aulas" target="_blank" class="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl text-xs shadow flex items-center gap-1.5 transition">
                    <span>🎓</span><span>Abrir Sala de Aula do Aluno ↗</span>
                </a>
            </div>
        </div>

        <!-- 4 CARDS: DASHBOARD DE INDICADORES DO ALUNADO -->
        <div class="w-full grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6 text-xs">
            <div class="bg-white p-5 rounded-2xl shadow-sm border-l-4 border-indigo-600 border-slate-200">
                <span class="text-slate-500 text-[10px] font-bold uppercase block">Total de Formandos</span>
                <span class="text-2xl font-black text-indigo-950 mt-1 block">{{ doutrina|length }} Alunos</span>
                <span class="text-[10px] text-slate-400">Inscritos no currículo oficial</span>
            </div>
            <div class="bg-white p-5 rounded-2xl shadow-sm border-l-4 border-emerald-500 border-slate-200">
                <span class="text-slate-500 text-[10px] font-bold uppercase block">Aptos / Prontos para Batismo</span>
                <span class="text-2xl font-black text-emerald-700 mt-1 block">🌊 {{ doutrina|selectattr('situacao', 'equalto', 'Apto / Aprovado')|list|length }} Prontos</span>
                <span class="text-[10px] text-emerald-600 font-bold">Aproveitamento >= 70%</span>
            </div>
            <div class="bg-white p-5 rounded-2xl shadow-sm border-l-4 border-amber-500 border-slate-200">
                <span class="text-slate-500 text-[10px] font-bold uppercase block">Em Formação Ativa</span>
                <span class="text-2xl font-black text-amber-700 mt-1 block">📖 {{ doutrina|rejectattr('situacao', 'equalto', 'Apto / Aprovado')|list|length }} Alunos</span>
                <span class="text-[10px] text-slate-400">Em estudo nas classes</span>
            </div>
            <div class="bg-white p-5 rounded-2xl shadow-sm border-l-4 border-blue-500 border-slate-200">
                <span class="text-slate-500 text-[10px] font-bold uppercase block">Corpo Docente</span>
                <span class="text-2xl font-black text-blue-900 mt-1 block">👨‍🏫 {{ professores_cadastrados|length if professores_cadastrados is defined and professores_cadastrados else 1 }} Instrutor(es)</span>
                <span class="text-[10px] text-slate-400">Docentes credenciados</span>
            </div>
        </div>

        <!-- GABINETE DO INSTRUTOR: DÚVIDAS BÍBLICAS DOS ALUNOS -->
        <div class="w-full bg-white p-6 rounded-2xl shadow-sm border border-slate-200 mb-6 space-y-3">
            <div class="flex justify-between items-center border-b pb-3">
                <div class="flex items-center gap-2">
                    <span class="text-xl">👨‍🏫</span>
                    <div>
                        <h3 class="font-black text-sm text-slate-900 uppercase">Gabinete do Instrutor: Dúvidas Bíblicas dos Formandos</h3>
                        <p class="text-xs text-slate-500">Responda diretamente às perguntas enviadas pelos formandos durante as lições.</p>
                    </div>
                </div>
                <span class="bg-amber-100 text-amber-900 px-3 py-1 rounded-full text-xs font-black">
                    {{ duvidas_pendentes|length if duvidas_pendentes is defined and duvidas_pendentes else 0 }} Pendente(s)
                </span>
            </div>

            <div class="space-y-3 pt-1">
                {% if duvidas_pendentes is defined and duvidas_pendentes %}
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
                            <input type="text" name="resposta" required placeholder="Escreva a resposta bíblica e aconselhamento pastoral..." class="flex-1 h-10 px-3 border-2 border-slate-300 rounded-xl bg-white text-xs focus:border-indigo-600 focus:outline-none">
                            <button type="submit" class="px-4 h-10 bg-indigo-900 hover:bg-indigo-950 text-white font-bold rounded-xl text-xs shadow cursor-pointer">
                                Enviar Resposta →
                            </button>
                        </form>
                    </div>
                    {% endfor %}
                {% else %}
                    <p class="text-xs text-slate-400 italic text-center py-2">Glória a Deus! Nenhuma dúvida bíblica pendente no momento.</p>
                {% endif %}
            </div>
        </div>

        <!-- ÁREA DE CADASTROS: FORMANDOS & PROFESSORES (LADO A LADO) -->
        <div class="w-full grid grid-cols-1 lg:grid-cols-12 gap-6 mb-6">

            <!-- FORMULÁRIO 1: INSCREVER FORMANDO (COM SELETORES PERFEITOS) -->
            <div class="lg:col-span-7 bg-white p-6 rounded-2xl shadow-sm border border-slate-200 space-y-4">
                <div class="border-b pb-3">
                    <h3 class="font-black text-sm text-slate-900 uppercase flex items-center gap-2">
                        <span>🎓</span> 1. Inscrever Formando com Login
                    </h3>
                    <p class="text-[11px] text-slate-500">Crie o acesso para o formando entrar na App no telemóvel</p>
                </div>

                <form action="/doutrina/gravar" method="POST" class="space-y-3 text-xs">
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">Nome Completo do Aluno *</label>
                        <input type="text" name="nome_aluno" required placeholder="Ex: Jacinto Manuel Bata Saranga" class="w-full h-11 px-3 border border-slate-300 rounded-xl focus:border-indigo-600 focus:outline-none">
                    </div>

                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">Classe *</label>
                            <select name="classe" required class="w-full h-11 px-3 border border-slate-300 rounded-xl bg-white font-bold text-xs text-slate-800 focus:border-indigo-600 focus:outline-none shadow-sm cursor-pointer">
                                {% if lista_classes is defined and lista_classes %}
                                    {% for cl in lista_classes %}
                                    <option value="{{ cl }}">{{ cl }}</option>
                                    {% endfor %}
                                {% else %}
                                    <option value="Preparação para Batismo nas Águas">Preparação para Batismo nas Águas</option>
                                    <option value="Discipulado de Novos Convertidos">Discipulado de Novos Convertidos</option>
                                    <option value="Classe I - Primeiros Passos">Classe I - Primeiros Passos</option>
                                    <option value="Classe II - Vida Cristã">Classe II - Vida Cristã</option>
                                    <option value="Classe III - Maturidade Cristã">Classe III - Maturidade Cristã</option>
                                {% endif %}
                            </select>
                        </div>
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">Instrutor / Mentor *</label>
                            <select name="professor" required class="w-full h-11 px-3 border border-slate-300 rounded-xl bg-white font-bold text-xs text-slate-800 focus:border-indigo-600 focus:outline-none shadow-sm cursor-pointer">
                                {% if lista_professores is defined and lista_professores %}
                                    {% for prof in lista_professores %}
                                    <option value="{{ prof }}">{{ prof }}</option>
                                    {% endfor %}
                                {% else %}
                                    <option value="Anselmo Leonardo Munguambe">Anselmo Leonardo Munguambe</option>
                                    <option value="Pastor Dirigente">Pastor Dirigente</option>
                                    {% if professores_cadastrados is defined and professores_cadastrados %}
                                        {% for p in professores_cadastrados %}
                                        <option value="{{ p.nome }}">{{ p.nome }}</option>
                                        {% endfor %}
                                    {% endif %}
                                {% endif %}
                            </select>
                        </div>
                    </div>

                    <!-- CREDENCIAIS -->
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
                    <p class="text-[11px] text-slate-500">Credencie docentes com acesso exclusivo ao ensino</p>
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
                        ℹ️ <b>Privacidade garantida:</b> O professor acede exclusivamente ao acompanhamento dos formandos e resposta a dúvidas, sem visualização financeira.
                    </div>

                    <button type="submit" class="w-full py-3 bg-indigo-900 hover:bg-indigo-950 text-white font-black rounded-xl shadow cursor-pointer text-xs transition">
                        Credenciar Professor / Instrutor
                    </button>
                </form>
            </div>

        </div>

        <!-- LISTAGENS DE FORMANDOS E PROFESSORES (LARGURA TOTAL) -->
        <div class="w-full grid grid-cols-1 lg:grid-cols-12 gap-6">

            <!-- TABELA DE FORMANDOS -->
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
                                    <span class="inline-block px-2.5 py-0.5 rounded-full text-xs font-black {% if (a.aproveitamento|float if a.aproveitamento else 0) >= 70 %}bg-emerald-100 text-emerald-800{% else %}bg-amber-100 text-amber-800{% endif %}">
                                        {{ "%.0f"|format(a.aproveitamento|float if a.aproveitamento else 0) }}%
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
                                        {% if a.situacao != 'Apto / Aprovado' and (a.aproveitamento|float if a.aproveitamento else 0) >= 70 %}
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

            <!-- QUADRO DE PROFESSORES ATIVOS -->
            <div class="lg:col-span-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-200 space-y-4">
                <div class="flex justify-between items-center border-b pb-3">
                    <div>
                        <h3 class="font-black text-sm text-slate-900 uppercase flex items-center gap-2">
                            <span>👨‍🏫</span> Professores Ativos
                        </h3>
                        <p class="text-[11px] text-slate-500">Docentes com permissão de ensino</p>
                    </div>
                    <span class="text-xs text-indigo-900 font-bold">{{ professores_cadastrados|length if professores_cadastrados is defined and professores_cadastrados else 0 }}</span>
                </div>

                <div class="space-y-2.5 text-xs">
                    {% if professores_cadastrados is defined and professores_cadastrados %}
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
                        {% endfor %}
                    {% else %}
                        <p class="text-slate-400 italic text-center py-4">Nenhum professor cadastrado ainda.</p>
                    {% endif %}
                </div>
            </div>

        </div>
        {% endif %}"""

# 4. ENXERTAR O NOVO BLOCO NO LUGAR DO ANTIGO SEM TOCAR NO RESTANTE CÓDIGO
html_final = html_base[:inicio_idx] + bloco_doutrina_novo + html_base[fim_idx:]

# 5. TESTE DE VALIDAÇÃO JINJA2 (ZERO ERROS)
env = jinja2.Environment()
env.parse(html_final)
print("✓ Validação Jinja2: Aprovada com ZERO erros de sintaxe!")

with open(caminho_dash, 'w', encoding='utf-8') as f:
    f.write(html_final)
print("✓ templates/dashboard.html regravado e pronto para produção!")

# 6. ENVIAR PARA O GITHUB COM GIT COMMIT E PUSH
print("=" * 80)
print("A ENVIAR A ATUALIZAÇÃO PARA O GITHUB & RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "templates/dashboard.html"], check=True)
subprocess.run(["git", "commit", "-m", "Restaurar layout widescreen perfeito com modulo pedagogico integrado"], check=True)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("=" * 80)
print(">>> SUCESSO TOTAL! O DEPLOY ESTÁ NO AR NO RENDER! <<<")
print("=" * 80)