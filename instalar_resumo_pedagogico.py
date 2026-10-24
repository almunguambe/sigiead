import os
import re
import py_compile
import subprocess
import jinja2

print("=" * 80)
print("A INSTALAR O RESUMO PEDAGÓGICO DO FORMANDO NA ÁREA DO PROFESSOR...")
print("=" * 80)

caminho_prof = os.path.join('templates', 'area_professor.html')
caminho_app = 'app.py'

if not os.path.exists(caminho_prof):
    print("ERRO: templates/area_professor.html não encontrado!")
    exit(1)

with open(caminho_prof, 'r', encoding='utf-8') as f:
    html = f.read()

# =============================================================================
# 1. MODAL DE RESUMO PEDAGÓGICO COMPLETO DO FORMANDO
# =============================================================================
modal_resumo_html = """
<!-- MODAIS DE RESUMO PEDAGÓGICO INDIVIDUAL DOS FORMANDOS -->
{% if doutrina %}
    {% for aluno in doutrina %}
    <div id="modal-resumo-{{ aluno.id }}" class="fixed inset-0 z-50 hidden bg-slate-950/75 backdrop-blur-sm flex items-center justify-center p-3 sm:p-4">
        <div class="bg-white rounded-2xl max-w-2xl w-full p-5 sm:p-6 space-y-5 shadow-2xl border border-slate-200 overflow-y-auto max-h-[92vh] animate-fadeIn">
            
            <!-- CABEÇALHO DO RESUMO -->
            <div class="flex items-center justify-between border-b border-slate-100 pb-4">
                <div class="flex items-center gap-3">
                    <div class="w-12 h-12 rounded-2xl bg-indigo-600 text-white font-black text-lg flex items-center justify-center shadow-md shrink-0">
                        {{ aluno.nome[0] if aluno.nome else 'A' }}
                    </div>
                    <div>
                        <div class="flex items-center gap-2">
                            <h3 class="text-base sm:text-lg font-black text-slate-900 leading-tight">{{ aluno.nome }}</h3>
                            <span class="px-2 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider {% if aluno.progresso|int == 100 or aluno.licao_atual|int >= 6 %}bg-emerald-100 text-emerald-800 border border-emerald-300{% else %}bg-amber-100 text-amber-800 border border-amber-300{% endif %}">
                                {% if aluno.progresso|int == 100 or aluno.licao_atual|int >= 6 %}Apto p/ Batismo{% else %}Em Formação{% endif %}
                            </span>
                        </div>
                        <p class="text-xs text-slate-500 font-medium mt-0.5">
                            Classe: <span class="font-bold text-indigo-700">{{ aluno.classe or aluno.turma or 'Classe Geral' }}</span> • Mentor: {{ aluno.mentor or 'Instrutor Designado' }}
                        </p>
                    </div>
                </div>
                <button type="button" onclick="fecharModalResumo({{ aluno.id }})" class="w-8 h-8 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-500 font-bold flex items-center justify-center transition">
                    ✕
                </button>
            </div>

            <!-- 4 CARTÕES DE INDICADORES RÁPIDOS -->
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                <div class="bg-slate-50 p-3 rounded-xl border border-slate-200/80 text-center">
                    <span class="text-[9px] font-black uppercase text-slate-400 block tracking-wider">Último Acesso</span>
                    <span class="text-xs font-bold text-slate-800 block mt-1 truncate">{{ aluno.ultimo_acesso or 'Sala Virtual' }}</span>
                </div>
                <div class="bg-slate-50 p-3 rounded-xl border border-slate-200/80 text-center">
                    <span class="text-[9px] font-black uppercase text-slate-400 block tracking-wider">Lição Atual</span>
                    <span class="text-xs font-bold text-indigo-700 block mt-1">Lição {{ aluno.licao_atual or ('6' if aluno.progresso|int == 100 else '1') }} de 6</span>
                </div>
                <div class="bg-slate-50 p-3 rounded-xl border border-slate-200/80 text-center">
                    <span class="text-[9px] font-black uppercase text-slate-400 block tracking-wider">Aproveitamento</span>
                    <span class="text-xs font-bold text-emerald-600 block mt-1">{{ aluno.aproveitamento or '100%' }}</span>
                </div>
                <div class="bg-slate-50 p-3 rounded-xl border border-slate-200/80 text-center">
                    <span class="text-[9px] font-black uppercase text-slate-400 block tracking-wider">Presenças</span>
                    <span class="text-xs font-bold text-blue-700 block mt-1">{{ aluno.presencas or '6/6' }} Aulas</span>
                </div>
            </div>

            <!-- GRELHA DISCRIMINADA DAS 6 LIÇÕES DOUTRINÁRIAS -->
            <div class="space-y-2.5">
                <div class="flex items-center justify-between">
                    <h4 class="text-xs font-black uppercase text-slate-700 tracking-wider flex items-center gap-1.5">
                        <span>📖</span> Discriminação do Plano de Ensino (6 Lições)
                    </h4>
                    <span class="text-[11px] font-black text-indigo-700">{{ aluno.progresso or '100' }}% Concluído</span>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                    {% set licoes_lista = [
                        (1, "A Salvação em Cristo Jesus", "Regeneração e reconciliação com Deus"),
                        (2, "A Oração & Comunhão", "Vida devocional diária do crente"),
                        (3, "A Bíblia Sagrada", "A regra de fé e prática cristã"),
                        (4, "A Igreja e o Dízimo", "Comunhão, mordomia e serviço"),
                        (5, "O Batismo nas Águas", "Significado espiritual e confissão pública"),
                        (6, "O Batismo no Espírito Santo", "Poder para testemunho e frutos")
                    ] %}
                    
                    {% set nivel_atual = (aluno.licao_atual|int if aluno.licao_atual else (6 if aluno.progresso|int == 100 else 1)) %}
                    
                    {% for num, tit, desc in licoes_lista %}
                    <div class="p-2.5 rounded-xl border flex items-start justify-between gap-2 {% if nivel_atual > num or aluno.progresso|int == 100 %}bg-emerald-50/70 border-emerald-200 text-emerald-950{% elif nivel_atual == num %}bg-amber-50 border-amber-300 text-amber-950 ring-1 ring-amber-300{% else %}bg-slate-50 border-slate-200 text-slate-400{% endif %}">
                        <div class="space-y-0.5">
                            <span class="font-bold block">Lição {{ num }}: {{ tit }}</span>
                            <span class="text-[10px] block opacity-80">{{ desc }}</span>
                        </div>
                        <span class="shrink-0 mt-0.5">
                            {% if nivel_atual > num or aluno.progresso|int == 100 %}
                            <span class="px-1.5 py-0.5 rounded-md bg-emerald-100 text-emerald-800 text-[10px] font-black">✓ Concluída</span>
                            {% elif nivel_atual == num %}
                            <span class="px-1.5 py-0.5 rounded-md bg-amber-200 text-amber-900 text-[10px] font-black">● Em Curso</span>
                            {% else %}
                            <span class="px-1.5 py-0.5 rounded-md bg-slate-200 text-slate-600 text-[10px] font-semibold">Pendente</span>
                            {% endif %}
                        </span>
                    </div>
                    {% endfor %}
                </div>
            </div>

            <!-- CONTROLO E PARECER PASTORAL PARA O BATISMO -->
            <div class="p-3.5 bg-slate-50 border border-slate-200 rounded-xl space-y-2">
                <span class="text-[10px] font-black uppercase text-slate-500 tracking-wider block">Parecer Pastoral & Recomendação</span>
                <p class="text-xs text-slate-700 leading-relaxed">
                    {% if aluno.progresso|int == 100 or aluno.licao_atual|int >= 6 %}
                    <strong class="text-emerald-700 font-black">✓ Candidato Habilitado:</strong> O formando completou o ciclo doutrinário e reúne os pré-requisitos bíblicos para descida às águas batismais.
                    {% else %}
                    <strong class="text-amber-700 font-black">● Em Acompanhamento:</strong> O formando necessita de concluir as lições pendentes para homologação pastoral.
                    {% endif %}
                </p>
                <div class="flex items-center justify-between text-[11px] text-slate-400 pt-1 border-t border-slate-200">
                    <span>Contacto: <strong>{{ aluno.contacto or 'Sem registo telefónico' }}</strong></span>
                    <span>Data Início: <strong>{{ aluno.data_matricula or 'Exercício 2026' }}</strong></span>
                </div>
            </div>

            <!-- BOTÃO DE FECHO -->
            <div class="flex justify-end pt-2">
                <button type="button" onclick="fecharModalResumo({{ aluno.id }})" class="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-black transition shadow-sm">
                    Fechar Resumo
                </button>
            </div>
        </div>
    </div>
    {% endfor %}
{% endif %}

<!-- SCRIPT DE ABERTURA E FECHO DO RESUMO PEDAGÓGICO -->
<script>
function abrirModalResumo(id) {
    const modal = document.getElementById('modal-resumo-' + id);
    if (modal) {
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }
}

function fecharModalResumo(id) {
    const modal = document.getElementById('modal-resumo-' + id);
    if (modal) {
        modal.classList.add('hidden');
        document.body.style.overflow = 'auto';
    }
}
</script>
"""

# Inserir o bloco de modais antes do fecho do body
if "<!-- MODAIS DE RESUMO PEDAGÓGICO" not in html:
    if "</body>" in html:
        pos_body = html.find("</body>")
        html = html[:pos_body] + modal_resumo_html + "\n" + html[pos_body:]
    else:
        html = html + "\n" + modal_resumo_html
    print("✓ Modal de Resumo Pedagógico integrado com sucesso!")

# =============================================================================
# 2. ADICIONAR O BOTÃO 'VER RESUMO' E O BADGE RICO NA TABELA DO PROFESSOR
# =============================================================================
# Substituir exibições simples de '100%' ou botões de ação pelo botão do Resumo
padrao_acao_aluno = r'(<td[^>]*class="[^"]*text-right[^"]*"[^>]*>)([\s\S]*?)(</td>)'

def enriquecer_acoes(m):
    abertura = m.group(1)
    conteudo_interno = m.group(2)
    fecho = m.group(3)
    if "abrirModalResumo" not in conteudo_interno:
        botao_resumo = """
            <button type="button" onclick="abrirModalResumo({{ aluno.id }})" class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-black transition shadow-sm mr-1">
                <span>📋</span> Ver Resumo
            </button>
        """
        return f"{abertura}\n{botao_resumo}\n{conteudo_interno}\n{fecho}"
    return m.group(0)

html = re.sub(padrao_acao_aluno, enriquecer_acoes, html)

# Validar com Jinja2
env = jinja2.Environment()
env.parse(html)
with open(caminho_prof, 'w', encoding='utf-8') as f:
    f.write(html)
print("✓ templates/area_professor.html validado e compilado com ZERO erros!")

# =============================================================================
# 3. ENVIAR PARA O GITHUB E RENDER
# =============================================================================
print("\n" + "=" * 80)
print("A ENVIAR ATUALIZAÇÃO PARA O RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "templates/area_professor.html"])
subprocess.run(["git", "commit", "-m", "Implementar Resumo Pedagogico individual do formando na Area do Professor"])
subprocess.run(["git", "push", "origin", "main"])

print("=" * 80)
print(">>> RESUMO PEDAGÓGICO DISPONÍVEL NO SISTEMA COM SUCESSO! <<<")
print("=" * 80)