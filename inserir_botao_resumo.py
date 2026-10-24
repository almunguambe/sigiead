import os
import re
import py_compile
import subprocess
import jinja2

print("=" * 80)
print("A INSERIR COLUNA DE AÇÕES E BOTÃO 'VER RESUMO' NA TABELA...")
print("=" * 80)

caminho_prof = os.path.join('templates', 'area_professor.html')

if not os.path.exists(caminho_prof):
    print("ERRO: templates/area_professor.html não encontrado!")
    exit(1)

with open(caminho_prof, 'r', encoding='utf-8') as f:
    html = f.read()

# =============================================================================
# 1. ADICIONAR CABEÇALHO 'AÇÕES' NA THEAD
# =============================================================================
pos_thead = html.find('<thead')
pos_thead_end = html.find('</thead>')

if pos_thead != -1 and pos_thead_end != -1:
    thead_txt = html[pos_thead:pos_thead_end]
    if 'AÇÕES' not in thead_txt and 'RESUMO' not in thead_txt:
        # Adicionar <th>AÇÕES</th> logo a seguir a SITUAÇÃO
        thead_novo = re.sub(
            r'(<th[^>]*>\s*SITUA[ÇC][ÃA]O\s*</th>)',
            r'\1\n                    <th class="py-3 px-4 text-center font-bold text-slate-700">AÇÕES</th>',
            thead_txt,
            flags=re.IGNORECASE
        )
        html = html[:pos_thead] + thead_novo + html[pos_thead_end:]
        print("✓ Coluna <th>AÇÕES</th> adicionada ao cabeçalho da tabela!")

# =============================================================================
# 2. INSERIR O BOTÃO 'VER RESUMO' EM CADA LINHA DA TBODY
# =============================================================================
pos_tbody = html.find('<tbody')
pos_tbody_end = html.find('</tbody>')

if pos_tbody != -1 and pos_tbody_end != -1:
    tbody_txt = html[pos_tbody:pos_tbody_end]
    
    # Identificar a variável do loop (geralmente 'aluno' ou 'formando')
    m_var = re.search(r'{%\s*for\s+(\w+)\s+in', tbody_txt)
    var_aluno = m_var.group(1) if m_var else 'aluno'
    print(f"✓ Variável de aluno detetada no loop: '{var_aluno}'")
    
    botao_td = f'''    <td class="py-3 px-4 text-center">
        <button type="button" onclick="abrirModalResumo('{{{{ {var_aluno}.id }}}}')" class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold transition shadow-sm hover:scale-105 active:scale-95">
            <span>📋</span> Ver Resumo
        </button>
    </td>\n'''
    
    if 'abrirModalResumo' not in tbody_txt:
        # Inserir a nova coluna com o botão antes de fechar cada linha </tr>
        tbody_novo = re.sub(r'(</td>\s*)(</tr>)', r'\1' + botao_td + r'\2', tbody_txt)
        html = html[:pos_tbody] + tbody_novo + html[pos_tbody_end:]
        print("✓ Botão '📋 Ver Resumo' inserido em todas as linhas dos formandos!")

# =============================================================================
# 3. GARANTIR QUE A JANELA MODAL ESTÁ PRESENTE NO FINAL DO FICHEIRO
# =============================================================================
if 'id="modal-resumo-' not in html:
    modal_bloco = """
<!-- MODAIS DE RESUMO PEDAGÓGICO INDIVIDUAL DOS FORMANDOS -->
{% if doutrina %}
    {% for aluno in doutrina %}
    {% set raw_prog = aluno.get('progresso', 100) if aluno.get else 100 %}
    {% set prog = (raw_prog|string|replace('%', '')|int) if raw_prog else 100 %}
    {% set raw_licao = aluno.get('licao_atual', 6) if aluno.get else 6 %}
    {% set nivel_atual = (raw_licao|string|int) if raw_licao else 6 %}
    {% set ult_acesso = aluno.get('ultimo_acesso', 'Sala Virtual') if aluno.get else 'Sala Virtual' %}
    {% set aprov = aluno.get('aproveitamento', '100%') if aluno.get else '100%' %}
    {% set pres = aluno.get('presencas', '6/6') if aluno.get else '6/6' %}

    <div id="modal-resumo-{{ aluno.id }}" class="fixed inset-0 z-50 hidden bg-slate-950/75 backdrop-blur-sm flex items-center justify-center p-3 sm:p-4">
        <div class="bg-white rounded-2xl max-w-2xl w-full p-5 sm:p-6 space-y-5 shadow-2xl border border-slate-200 overflow-y-auto max-h-[92vh]">
            
            <div class="flex items-center justify-between border-b border-slate-100 pb-4">
                <div class="flex items-center gap-3">
                    <div class="w-12 h-12 rounded-2xl bg-indigo-600 text-white font-black text-lg flex items-center justify-center shadow-md shrink-0">
                        {{ aluno.nome[0] if aluno.nome else 'A' }}
                    </div>
                    <div>
                        <div class="flex items-center gap-2">
                            <h3 class="text-base sm:text-lg font-black text-slate-900 leading-tight">{{ aluno.nome }}</h3>
                            <span class="px-2 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider {% if prog >= 100 or nivel_atual >= 6 %}bg-emerald-100 text-emerald-800 border border-emerald-300{% else %}bg-amber-100 text-amber-800 border border-amber-300{% endif %}">
                                {% if prog >= 100 or nivel_atual >= 6 %}Apto p/ Batismo{% else %}Em Formação{% endif %}
                            </span>
                        </div>
                        <p class="text-xs text-slate-500 font-medium mt-0.5">
                            Classe: <span class="font-bold text-indigo-700">{{ aluno.get('classe', aluno.get('turma', 'Classe Geral')) if aluno.get else 'Classe Geral' }}</span> • Mentor: {{ aluno.get('mentor', 'Instrutor Designado') if aluno.get else 'Instrutor Designado' }}
                        </p>
                    </div>
                </div>
                <button type="button" onclick="fecharModalResumo('{{ aluno.id }}')" class="w-8 h-8 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-500 font-bold flex items-center justify-center transition">
                    ✕
                </button>
            </div>

            <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                <div class="bg-slate-50 p-3 rounded-xl border border-slate-200/80 text-center">
                    <span class="text-[9px] font-black uppercase text-slate-400 block tracking-wider">Último Acesso</span>
                    <span class="text-xs font-bold text-slate-800 block mt-1 truncate">{{ ult_acesso }}</span>
                </div>
                <div class="bg-slate-50 p-3 rounded-xl border border-slate-200/80 text-center">
                    <span class="text-[9px] font-black uppercase text-slate-400 block tracking-wider">Lição Atual</span>
                    <span class="text-xs font-bold text-indigo-700 block mt-1">Lição {{ nivel_atual }} de 6</span>
                </div>
                <div class="bg-slate-50 p-3 rounded-xl border border-slate-200/80 text-center">
                    <span class="text-[9px] font-black uppercase text-slate-400 block tracking-wider">Aproveitamento</span>
                    <span class="text-xs font-bold text-emerald-600 block mt-1">{{ aprov }}</span>
                </div>
                <div class="bg-slate-50 p-3 rounded-xl border border-slate-200/80 text-center">
                    <span class="text-[9px] font-black uppercase text-slate-400 block tracking-wider">Presenças</span>
                    <span class="text-xs font-bold text-blue-700 block mt-1">{{ pres }} Aulas</span>
                </div>
            </div>

            <div class="space-y-2.5">
                <div class="flex items-center justify-between">
                    <h4 class="text-xs font-black uppercase text-slate-700 tracking-wider flex items-center gap-1.5">
                        <span>📖</span> Discriminação do Plano de Ensino (6 Lições)
                    </h4>
                    <span class="text-[11px] font-black text-indigo-700">{{ prog }}% Concluído</span>
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
                    
                    {% for num, tit, desc in licoes_lista %}
                    <div class="p-2.5 rounded-xl border flex items-start justify-between gap-2 {% if nivel_atual > num or prog >= 100 %}bg-emerald-50/70 border-emerald-200 text-emerald-950{% elif nivel_atual == num %}bg-amber-50 border-amber-300 text-amber-950 ring-1 ring-amber-300{% else %}bg-slate-50 border-slate-200 text-slate-400{% endif %}">
                        <div class="space-y-0.5">
                            <span class="font-bold block">Lição {{ num }}: {{ tit }}</span>
                            <span class="text-[10px] block opacity-80">{{ desc }}</span>
                        </div>
                        <span class="shrink-0 mt-0.5">
                            {% if nivel_atual > num or prog >= 100 %}
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

            <div class="p-3.5 bg-slate-50 border border-slate-200 rounded-xl space-y-2">
                <span class="text-[10px] font-black uppercase text-slate-500 tracking-wider block">Parecer Pastoral & Recomendação</span>
                <p class="text-xs text-slate-700 leading-relaxed">
                    {% if prog >= 100 or nivel_atual >= 6 %}
                    <strong class="text-emerald-700 font-black">✓ Candidato Habilitado:</strong> O formando completou o ciclo doutrinário e reúne os pré-requisitos bíblicos para descida às águas batismais.
                    {% else %}
                    <strong class="text-amber-700 font-black">● Em Acompanhamento:</strong> O formando necessita de concluir as lições pendentes para homologação pastoral.
                    {% endif %}
                </p>
                <div class="flex items-center justify-between text-[11px] text-slate-400 pt-1 border-t border-slate-200">
                    <span>Contacto: <strong>{{ aluno.get('contacto', 'Sem registo telefónico') if aluno.get else 'Sem registo telefónico' }}</strong></span>
                    <span>Data Início: <strong>{{ aluno.get('data_matricula', 'Exercício 2026') if aluno.get else 'Exercício 2026' }}</strong></span>
                </div>
            </div>

            <div class="flex justify-end pt-2">
                <button type="button" onclick="fecharModalResumo('{{ aluno.id }}')" class="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-black transition shadow-sm">
                    Fechar Resumo
                </button>
            </div>
        </div>
    </div>
    {% endfor %}
{% endif %}

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
</script>"""
    if "</body>" in html:
        pos_b = html.find("</body>")
        html = html[:pos_b] + "\n" + modal_bloco + "\n" + html[pos_b:]
    else:
        html = html + "\n" + modal_bloco

# Validar sintaxe Jinja2
env = jinja2.Environment()
env.parse(html)
with open(caminho_prof, 'w', encoding='utf-8') as f:
    f.write(html)
print("✓ templates/area_professor.html validado e gravado com sucesso!")

# =============================================================================
# 4. ENVIAR PARA O GITHUB E RENDER
# =============================================================================
print("\n" + "=" * 80)
print("A ENVIAR ATUALIZAÇÃO PARA O RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "templates/area_professor.html"])
subprocess.run(["git", "commit", "-m", "Adicionar coluna de Acoes e botao Ver Resumo na tabela do professor"])
subprocess.run(["git", "push", "origin", "main"])

print("=" * 80)
print(">>> ATUALIZAÇÃO CONCLUÍDA E PUBLICADA NO RENDER! <<<")
print("=" * 80)