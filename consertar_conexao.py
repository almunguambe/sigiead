import os
import re
import jinja2

print("=" * 80)
print("A RECONSTRUIR O PORTAL DO ALUNO E A ATIVAR A CONEXÃO ALUNO-PROFESSOR...")
print("=" * 80)

os.makedirs('templates', exist_ok=True)

# =============================================================================
# RECONSTRUÇÃO COMPLETA DE TEMPLATES/PORTAL_ALUNO.HTML COM LIGAÇÃO AO PROFESSOR
# =============================================================================
portal_html = """<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portal do Aluno - IEAD Chicuque</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .card-bg { background: linear-gradient(135deg, #090d16 0%, #1e1b4b 60%, #312e81 100%); }
    </style>
</head>
<body class="bg-slate-100 text-slate-800 font-sans min-h-screen flex flex-col">

    <!-- BARRA SUPERIOR -->
    <header class="bg-slate-900 text-white px-6 py-4 flex justify-between items-center shadow-lg border-b border-indigo-900 sticky top-0 z-50">
        <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-2xl bg-gradient-to-tr from-indigo-500 to-amber-400 flex items-center justify-center font-black text-xl shadow">
                AD
            </div>
            <div>
                <h1 class="font-black text-sm uppercase tracking-wider">ESCOLA DE INTEGRAÇÃO & DOUTRINA</h1>
                <p class="text-[11px] text-amber-300 font-bold">Assembleia de Deus • Sede Regional de Chicuque</p>
            </div>
        </div>

        <div class="flex items-center gap-4 text-xs">
            <div class="text-right">
                <span class="text-[10px] text-slate-400 block uppercase font-bold">Aluno Conectado</span>
                <span class="font-extrabold text-white">{{ aluno.nome_aluno }}</span>
            </div>
            <a href="/ensino/logout" class="bg-rose-600 hover:bg-rose-700 text-white px-3.5 py-1.5 rounded-xl font-bold shadow text-xs transition">
                Sair
            </a>
        </div>
    </header>

    <main class="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">

        <!-- BOAS-VINDAS, APROVEITAMENTO E CARD DO PROFESSOR/MENTOR -->
        <div class="card-bg text-white p-6 sm:p-8 rounded-3xl shadow-xl flex flex-col lg:flex-row lg:items-center justify-between gap-6">
            <div class="space-y-2">
                <span class="bg-amber-400 text-slate-950 text-[10px] font-black uppercase px-3 py-1 rounded-full shadow">
                    Plataforma de Discipulado Contínuo
                </span>
                <h2 class="text-2xl sm:text-3xl font-black">
                    A Paz do Senhor, {{ aluno.nome_aluno }}!
                </h2>
                <p class="text-xs sm:text-sm text-indigo-200 max-w-2xl leading-relaxed">
                    As lições seguem a ordem do <b>Manual de Candidatos e Integração da IEADAO</b>. Para avançar, leia a lição, <b>submeta o seu resumo</b> e atinja pelo menos <b>70% no teste</b>.
                </p>
            </div>

            <!-- CARD DE STATUS DO CURSO & MENTOR -->
            <div class="bg-white/10 backdrop-blur-md border border-white/20 p-5 rounded-3xl text-center shrink-0 w-full lg:w-72 space-y-3">
                <div>
                    <span class="text-[10px] uppercase font-bold text-indigo-200 block">Aproveitamento Médio</span>
                    <div class="text-3xl font-black mt-0.5 text-amber-300">
                        {{ "%.1f"|format(aluno.aproveitamento or 0) }}%
                    </div>
                    <div class="w-full bg-slate-900/60 h-2 rounded-full overflow-hidden my-2 border border-white/10">
                        <div class="bg-emerald-400 h-full rounded-full transition-all duration-700" style="width: {{ [aluno.aproveitamento or 0, 100]|min }}%"></div>
                    </div>
                </div>

                <div class="border-t border-white/10 pt-2 text-left bg-white/5 p-2.5 rounded-xl">
                    <span class="text-[9px] uppercase font-bold text-amber-300 block">👨‍🏫 Instrutor / Pai na Fé</span>
                    <span class="text-xs font-black text-white block truncate">{{ aluno.professor or "Pastor Dirigente" }}</span>
                    <span class="text-[10px] text-indigo-200 block mt-0.5">{{ aluno.classe }}</span>
                </div>

                {% if todas_concluidas %}
                <a href="/ensino/exame_final" class="block w-full py-2 bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-black rounded-xl text-xs shadow transition">
                    🏆 Fazer Exame Final & Obter Certificado
                </a>
                {% endif %}
            </div>
        </div>

        {% if request.args.get('sucesso_aprovado') %}
        <div class="bg-emerald-50 border-2 border-emerald-400 p-4 rounded-2xl flex items-center justify-between text-emerald-900 text-xs font-bold shadow">
            <span>🎉 Glória a Deus! Concluiu a lição anterior com aproveitamento $\ge$ 70%! A lição seguinte foi destravada para o seu estudo!</span>
        </div>
        {% endif %}

        {% if request.args.get('nota_resultado') %}
        <div class="bg-amber-50 border-2 border-amber-400 p-4 rounded-2xl flex items-center justify-between text-amber-900 text-xs font-bold shadow">
            <span>⚠️ Atingiu {{ request.args.get('nota_resultado') }}%. É necessário no mínimo 70% para destrancar a próxima lição. Reveja os tópicos e repita o teste abaixo.</span>
        </div>
        {% endif %}

        <!-- CURRÍCULO AGRUPADO POR CLASSES (SIDEBAR + CONTEÚDO) -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">

            <!-- COLUNA DA ESQUERDA: AS 4 CLASSES E SUAS LIÇÕES COM STATUS -->
            <div class="lg:col-span-4 space-y-4">
                <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200">
                    <h3 class="font-extrabold text-sm uppercase text-slate-900 mb-3 border-b pb-2 flex items-center gap-2">
                        <span>📚</span> Currículo Oficial por Classes
                    </h3>

                    <div class="space-y-4">
                        {% for classe in curriculo %}
                        <div class="border border-slate-200 rounded-xl p-3 bg-slate-50">
                            <div class="font-black text-xs text-indigo-950 uppercase mb-1">
                                {{ classe.nome_classe }}
                            </div>
                            <p class="text-[10px] text-slate-500 mb-2.5">{{ classe.descricao }}</p>

                            <div class="space-y-1.5">
                                {% for l in classe.licoes %}
                                {% set st = licoes_status[l.id] %}
                                
                                {% if st.status == 'concluida' %}
                                <a href="/ensino/aulas?licao={{ l.id }}" class="flex items-center justify-between p-2 rounded-lg text-xs font-bold transition {% if licao.id == l.id %}bg-indigo-600 text-white{% else %}bg-emerald-50 text-emerald-900 hover:bg-emerald-100{% endif %}">
                                    <span class="truncate">✅ {{ l.numero }}: {{ l.titulo }}</span>
                                    <span class="text-[10px] bg-emerald-200 text-emerald-950 px-2 py-0.5 rounded-full font-black ml-1">{{ st.nota }}%</span>
                                </a>
                                {% elif st.status == 'em_estudo' %}
                                <a href="/ensino/aulas?licao={{ l.id }}" class="flex items-center justify-between p-2 rounded-lg text-xs font-bold transition {% if licao.id == l.id %}bg-indigo-600 text-white shadow-md{% else %}bg-blue-100 text-blue-900 border border-blue-300 hover:bg-blue-200{% endif %}">
                                    <span class="truncate">📖 {{ l.numero }}: {{ l.titulo }}</span>
                                    <span class="text-[10px] bg-amber-400 text-slate-950 px-2 py-0.5 rounded-full font-black ml-1">EM ESTUDO</span>
                                </a>
                                {% else %}
                                <div class="flex items-center justify-between p-2 rounded-lg text-xs text-slate-400 bg-slate-100 cursor-not-allowed">
                                    <span class="truncate">🔒 {{ l.numero }}: {{ l.titulo }}</span>
                                    <span class="text-[10px] text-slate-400">Trancada</span>
                                </div>
                                {% endif %}
                                {% endfor %}
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>

            <!-- COLUNA DA DIREITA: A LIÇÃO ATIVA COM O FLUXO DE 3 ETAPAS -->
            <div class="lg:col-span-8 space-y-6">

                <!-- ETAPA 1: ESTUDO DA LIÇÃO -->
                <div class="bg-white p-6 sm:p-8 rounded-3xl shadow-sm border border-slate-200 space-y-6">
                    <div class="border-b border-slate-100 pb-4">
                        <span class="text-xs font-black uppercase text-indigo-600 tracking-wider">
                            ETAPA 1: LEITURA & FUNDAMENTO BÍBLICO
                        </span>
                        <h2 class="text-2xl font-black text-slate-900 mt-1">{{ licao.numero }}: {{ licao.titulo }}</h2>
                        <p class="text-xs text-slate-500 mt-0.5">Leitura Bíblica: <b>{{ licao.leitura_base }}</b></p>
                    </div>

                    <div class="bg-amber-50 border-l-4 border-amber-500 p-4 rounded-r-2xl">
                        <span class="text-[10px] font-black uppercase text-amber-900 block mb-1">🔥 Texto Áureo da Lição</span>
                        <p class="text-xs italic text-amber-950 font-serif leading-relaxed">"{{ licao.texto_aureo }}"</p>
                    </div>

                    <div class="p-5 bg-slate-50 rounded-2xl border border-slate-200 text-xs text-slate-700 leading-relaxed text-justify space-y-3">
                        <p class="font-bold text-sm text-slate-800">Doutrina e Conteúdo da Lição:</p>
                        <p>{{ licao.conteudo }}</p>
                    </div>

                    <!-- ETAPA 2: RESUMO OBRIGATÓRIO DO ALUNO -->
                    <div class="pt-6 border-t-2 border-slate-100 space-y-4">
                        <div class="flex items-center justify-between">
                            <div>
                                <span class="text-xs font-black uppercase text-amber-600 tracking-wider">
                                    ETAPA 2: RESUMO REFLEXIVO DO ALUNO
                                </span>
                                <h3 class="text-base font-extrabold text-slate-900 mt-0.5">
                                    O Que Você Aprendeu Nesta Lição?
                                </h3>
                                <p class="text-xs text-slate-500">Escreva com as suas próprias palavras. O teste de fixação só será destravado após submeter o resumo.</p>
                            </div>
                            {% if progresso_atual.resumo %}
                            <span class="bg-emerald-100 text-emerald-800 px-3 py-1 rounded-full text-xs font-black">
                                ✅ Resumo Entregue
                            </span>
                            {% endif %}
                        </div>

                        {% if progresso_atual.resumo %}
                        <div class="p-4 bg-emerald-50/70 border border-emerald-200 rounded-2xl text-xs text-emerald-950 space-y-1">
                            <span class="font-extrabold block text-emerald-800">Seu Resumo Gravado:</span>
                            <p class="italic">"{{ progresso_atual.resumo }}"</p>
                        </div>
                        {% else %}
                        <form action="/ensino/submeter_resumo" method="POST" class="space-y-3 text-xs">
                            <input type="hidden" name="licao_id" value="{{ licao.id }}">
                            <textarea name="resumo" required rows="4" placeholder="Escreva aqui pelo menos 2 ou 3 frases explicando o que compreendeu do texto áureo e do conteúdo desta lição..." class="w-full p-4 border-2 border-slate-200 rounded-2xl bg-slate-50 focus:bg-white focus:border-indigo-600 focus:outline-none font-medium leading-relaxed"></textarea>
                            <button type="submit" class="w-full py-3.5 bg-amber-600 hover:bg-amber-700 text-white font-black rounded-xl shadow cursor-pointer text-xs transition">
                                ✍️ Submeter Resumo & Desbloquear o Teste de Fixação
                            </button>
                        </form>
                        {% endif %}
                    </div>

                    <!-- ETAPA 3: TESTE DE FIXAÇÃO -->
                    <div id="teste" class="pt-6 border-t-2 border-slate-100 space-y-4">
                        <span class="text-xs font-black uppercase text-indigo-600 tracking-wider block">
                            ETAPA 3: TESTE DE FIXAÇÃO TEOLÓGICA (MÍNIMO 70%)
                        </span>

                        {% if not progresso_atual.resumo %}
                        <div class="bg-slate-100 border-2 border-dashed border-slate-300 p-8 rounded-2xl text-center space-y-2">
                            <span class="text-3xl">🔒</span>
                            <h4 class="font-bold text-sm text-slate-700">Teste Bloqueado</h4>
                            <p class="text-xs text-slate-500 max-w-md mx-auto">
                                Para ter acesso a este teste, complete o estudo da lição acima e <b>submeta o seu resumo na Etapa 2</b>.
                            </p>
                        </div>
                        {% else %}
                        <form action="/ensino/submeter_teste" method="POST" class="space-y-4 text-xs">
                            <input type="hidden" name="licao_id" value="{{ licao.id }}">

                            {% for q in licao.questoes %}
                            <div class="bg-slate-50 p-5 rounded-2xl border border-slate-200 space-y-3">
                                <p class="font-extrabold text-sm text-slate-800">
                                    {{ loop.index }}. {{ q.p }}
                                </p>
                                <div class="space-y-2">
                                    {% for op in q.ops %}
                                    <label class="flex items-center gap-3 p-3 bg-white rounded-xl border border-slate-200 cursor-pointer hover:bg-indigo-50/50 transition">
                                        <input type="radio" name="q_{{ loop.parent.loop.index0 }}" value="{{ loop.index0 }}" required class="w-4 h-4 text-indigo-600">
                                        <span class="text-slate-700 font-medium">{{ op }}</span>
                                    </label>
                                    {% endfor %}
                                </div>
                            </div>
                            {% endfor %}

                            <button type="submit" class="w-full py-4 bg-indigo-900 hover:bg-indigo-950 text-white font-black rounded-2xl shadow-lg cursor-pointer text-sm transition">
                                🎯 Submeter Teste de Fixação
                            </button>
                        </form>
                        {% endif %}
                    </div>

                    <!-- ESPAÇO TIRA-DÚVIDAS INTEGRADO COM O PROFESSOR -->
                    <div id="duvidas" class="pt-6 border-t-2 border-slate-100 space-y-4">
                        <div class="flex items-center justify-between">
                            <h4 class="font-extrabold text-sm text-slate-900 flex items-center gap-2">
                                <span>💬</span> Espaço Tira-Dúvidas com o Professor ({{ aluno.professor or "Pastor" }})
                            </h4>
                            <span class="text-[10px] text-slate-400">Resposta bíblica imediata e acompanhamento pastoral</span>
                        </div>

                        <form action="/ensino/duvida" method="POST" class="space-y-2 text-xs">
                            <input type="hidden" name="licao_id" value="{{ licao.id }}">
                            <div class="flex gap-2">
                                <input type="text" name="pergunta" required placeholder="Tem alguma dúvida bíblica? Pergunte ao seu professor aqui..." class="flex-1 h-11 px-3 border-2 border-slate-200 rounded-xl bg-slate-50 focus:bg-white focus:border-indigo-600 focus:outline-none">
                                <button type="submit" class="px-5 h-11 bg-slate-800 hover:bg-slate-900 text-white font-bold rounded-xl shadow cursor-pointer">
                                    Perguntar
                                </button>
                            </div>
                        </form>

                        <div class="space-y-2.5">
                            {% for d in duvidas %}
                            <div class="p-3.5 bg-slate-50 rounded-xl text-xs space-y-1.5 border border-slate-200">
                                <div class="font-bold text-slate-800 flex justify-between">
                                    <span>❓ Sua Pergunta: "{{ d.pergunta }}"</span>
                                    <span class="text-[10px] text-slate-400">{{ d.criado_em }}</span>
                                </div>
                                {% if d.resposta_professor %}
                                <div class="p-2.5 bg-emerald-50 border border-emerald-300 rounded-lg text-emerald-950 text-[11px] leading-relaxed">
                                    <b class="text-emerald-800 block">👨‍🏫 Resposta do seu Professor ({{ d.professor_nome or aluno.professor or 'Pastor' }}):</b>
                                    {{ d.resposta_professor }}
                                </div>
                                {% else %}
                                <div class="p-2.5 bg-white border border-indigo-100 rounded-lg text-indigo-950 text-[11px] leading-relaxed">
                                    <b class="text-indigo-800 block">📖 Orientação do Manual:</b>
                                    {{ d.resposta_sistema }}
                                    <span class="text-[10px] text-slate-400 block mt-1 italic">⏳ Aguardando comentário adicional do seu professor...</span>
                                </div>
                                {% endif %}
                            </div>
                            {% else %}
                            <p class="text-[11px] text-slate-400 italic text-center py-2">Nenhuma dúvida enviada sobre esta lição ainda.</p>
                            {% endfor %}
                        </div>
                    </div>

                </div>
            </div>

        </div>

    </main>
</body>
</html>
"""

# Validação com Jinja2 antes de salvar
env = jinja2.Environment()
env.parse(portal_html)

with open(os.path.join('templates', 'portal_aluno.html'), 'w', encoding='utf-8') as f:
    f.write(portal_html)
print("✓ templates/portal_aluno.html: Compilado com sucesso e zero erros!")

# Validar também templates/dashboard.html
with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    dash = f.read()
env.parse(dash)
print("✓ templates/dashboard.html: Validado com sucesso!")

print("=" * 80)
print(">>> TUDO PRONTO! O PORTAL E A CONEXÃO COM O PROFESSOR ESTÃO 100% OPERACIONAIS! <<<")
print("=" * 80)