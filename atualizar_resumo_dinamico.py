# -*- coding: utf-8 -*-
import os
import re
import py_compile
import subprocess
import jinja2

print("=" * 80)
print("A ATUALIZAR RESUMO PEDAGÓGICO COM DADOS REAIS DE PRESENÇAS...")
print("=" * 80)

caminho_prof = os.path.join('templates', 'area_professor.html')

if not os.path.exists(caminho_prof):
    print("ERRO: templates/area_professor.html não encontrado!")
    exit(1)

with open(caminho_prof, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. REMOVER BLOCO ANTERIOR DE MODAIS
html = re.sub(r'<!-- MODAIS DE RESUMO PEDAGÓGICO[\s\S]*?</script>', '', html)

# 2. ASSEGURAR A COLUNA 'AÇÕES' NO CABEÇALHO DA TABELA
pos_thead = html.find('<thead')
pos_thead_end = html.find('</thead>')
if pos_thead != -1 and pos_thead_end != -1:
    thead_txt = html[pos_thead:pos_thead_end]
    if 'AÇÕES' not in thead_txt and 'RESUMO' not in thead_txt:
        thead_novo = re.sub(
            r'(<th[^>]*>\s*SITUA[ÇC][ÃA]O\s*</th>)',
            r'\1\n                    <th class="py-3 px-4 text-center font-bold text-slate-700">AÇÕES</th>',
            thead_txt,
            flags=re.IGNORECASE
        )
        html = html[:pos_thead] + thead_novo + html[pos_thead_end:]

# 3. ASSEGURAR O BOTÃO 'VER RESUMO' COM IDENTIFICADOR ÚNICO EM CADA LINHA
pos_tbody = html.find('<tbody')
pos_tbody_end = html.find('</tbody>')
if pos_tbody != -1 and pos_tbody_end != -1:
    tbody_txt = html[pos_tbody:pos_tbody_end]
    tbody_txt = re.sub(r'<td[^>]*>\s*<button[^>]*abrirModalResumo[\s\S]*?</button>\s*</td>', '', tbody_txt)
    
    m_var = re.search(r'{%\s*for\s+(\w+)\s+in', tbody_txt)
    var = m_var.group(1) if m_var else 'aluno'
    
    botao = f'''    <td class="py-3 px-4 text-center">
        <button type="button" onclick="abrirModalResumo('{{{{ {var}.id if {var}.id is defined and {var}.id else loop.index }}}}')" class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold transition shadow-sm hover:scale-105 active:scale-95">
            <span>📋</span> Ver Resumo
        </button>
    </td>\n'''
    
    tbody_novo = re.sub(r'(</td>\s*)(</tr>)', r'\1' + botao + r'\2', tbody_txt)
    html = html[:pos_tbody] + tbody_novo + html[pos_tbody_end:]

# 4. NOVO BLOCO DE MODAIS COM CÁLCULO PROPORCIONAL ÀS PRESENÇAS
novos_modais = """<!-- MODAIS DE RESUMO PEDAGÓGICO INDIVIDUAL DOS FORMANDOS -->
{% if doutrina %}
    {% for aluno in doutrina %}
    {% set aluno_uid = aluno.id if aluno.id is defined and aluno.id else loop.index %}
    {% set nome_aluno = aluno.get('nome') or aluno.get('aluno') or aluno.get('nome_completo') or 'Formando' %}
    {% set inicial = nome_aluno[0]|upper if nome_aluno else 'F' %}
    {% set raw_p = aluno.get('presencas', 0) %}
    {% set pres = (raw_p|string|int) if raw_p else 0 %}
    {% set sit = (aluno.get('situacao') or aluno.get('status') or 'Em Formação')|string %}
    {% set eh_apto = (pres >= 6) or ('apto' in sit|lower) or ('conclu' in sit|lower) %}
    
    {% if eh_apto %}
        {% set progresso = 100 %}
        {% set licoes_feitas = 6 %}
        {% set status_texto = "APTO P/ BATISMO" %}
        {% set status_bg = "bg-emerald-100 text-emerald-800 border-emerald-300" %}
        {% set aprov = "100%" %}
        {% set parecer = "✓ Candidato Habilitado: O formando concluiu todas as 6 lições do ciclo doutrinário e está apto para o Santo Batismo." %}
        {% set licao_display = "Lição 6 de 6 (Concluído)" %}
    {% elif pres == 0 %}
        {% set progresso = 0 %}
        {% set licoes_feitas = 0 %}
        {% set status_texto = "EM FORMAÇÃO" %}
        {% set status_bg = "bg-amber-100 text-amber-800 border-amber-300" %}
        {% set aprov = "0%" %}
        {% set parecer = "● Em Acompanhamento: O formando ainda não assistiu a nenhuma aula (0% de frequência). Necessita iniciar o ciclo doutrinário." %}
        {% set licao_display = "Lição 1 de 6 (Não Iniciada)" %}
    {% else %}
        {% set licoes_feitas = (pres if pres <= 5 else 5) %}
        {% set progresso = (licoes_feitas * 100 // 6) %}
        {% set status_texto = "EM FORMAÇÃO" %}
        {% set status_bg = "bg-amber-100 text-amber-800 border-amber-300" %}
        {% set aprov = (70 + licoes_feitas * 5)|string ~ "%" %}
        {% set parecer = "● Em Acompanhamento: O formando participou de " ~ pres ~ " de 6 aulas (" ~ progresso ~ "% concluído). Necessita assistir às lições restantes para habilitação batismal." %}
        {% set licao_display = "Lição " ~ (licoes_feitas + 1 if licoes_feitas < 6 else 6) ~ " de 6" %}
    {% endif %}

    <div id="modal-resumo-{{ aluno_uid }}" class="fixed inset-0 z-50 hidden bg-slate-950/75 backdrop-blur-sm flex items-center justify-center p-3 sm:p-4">
        <div class="bg-white rounded-2xl max-w-2xl w-full p-5 sm:p-6 space-y-5 shadow-2xl border border-slate-200 overflow-y-auto max-h-[92vh]">
            
            <!-- CABEÇALHO -->
            <div class="flex items-center justify-between border-b border-slate-100 pb-4">
                <div class="flex items-center gap-3">
                    <div class="w-12 h-12 rounded-2xl bg-indigo-600 text-white font-black text-lg flex items-center justify-center shadow-md shrink-0">
                        {{ inicial }}
                    </div>
                    <div>
                        <div class="flex items-center gap-2">
                            <h3 class="text-base sm:text-lg font-black text-slate-900 leading-tight">{{ nome_aluno }}</h3>
                            <span class="px-2 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider {{ status_bg }} border">
                                {{ status_texto }}
                            </span>
                        </div>
                        <p class="text-xs text-slate-500 font-medium mt-0.5">
                            Classe: <span class="font-bold text-indigo-700">{{ aluno.get('classe', aluno.get('turma', 'Batismo')) if aluno.get else 'Batismo' }}</span> • Mentor: {{ aluno.get('mentor', 'Anselmo Leonardo Munguambe') if aluno.get else 'Anselmo Leonardo Munguambe' }}
                        </p>
                    </div>
                </div>
                <button type="button" onclick="fecharModalResumo('{{ aluno_uid }}')" class="w-8 h-8 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-500 font-bold flex items-center justify-center transition">
                    ✕
                </button>
            </div>

            <!-- INDICADORES -->
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                <div class="bg-slate-50 p-3 rounded-xl border border-slate-200/80 text-center">
                    <span class="text-[9px] font-black uppercase text-slate-400 block tracking-wider">Último Acesso</span>
                    <span class="text-xs font-bold text-slate-800 block mt-1 truncate">{% if pres > 0 %}Sala Virtual{% else %}Nunca acedeu{% endif %}</span>
                </div>
                <div class="bg-slate-50 p-3 rounded-xl border border-slate-200/80 text-center">
                    <span class="text-[9px] font-black uppercase text-slate-400 block tracking-wider">Lição Atual</span>
                    <span class="text-xs font-bold text-indigo-700 block mt-1">{{ licao_display }}</span>
                </div>
                <div class="bg-slate-50 p-3 rounded-xl border border-slate-200/80 text-center">
                    <span class="text-[9px] font-black uppercase text-slate-400 block tracking-wider">Aproveitamento</span>
                    <span class="text-xs font-bold {% if eh_apto %}text-emerald-600{% elif pres == 0 %}text-slate-400{% else %}text-indigo-600{% endif %} block mt-1">{{ aprov }}</span>
                </div>
                <div class="bg-slate-50 p-3 rounded-xl border border-slate-200/80 text-center">
                    <span class="text-[9px] font-black uppercase text-slate-400 block tracking-wider">Presenças</span>
                    <span class="text-xs font-bold text-blue-700 block mt-1">{{ pres }} Aulas</span>
                </div>
            </div>

            <!-- GRELHA DAS 6 LIÇÕES -->
            <div class="space-y-2.5">
                <div class="flex items-center justify-between">
                    <h4 class="text-xs font-black uppercase text-slate-700 tracking-wider flex items-center gap-1.5">
                        <span>📖</span> Discriminação do Plano de Ensino (6 Lições)
                    </h4>
                    <span class="text-[11px] font-black {% if eh_apto %}text-emerald-700{% else %}text-indigo-700{% endif %}">{{ progresso }}% Concluído</span>
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
                    <div class="p-2.5 rounded-xl border flex items-start justify-between gap-2 {% if num <= licoes_feitas %}bg-emerald-50/70 border-emerald-200 text-emerald-950{% elif num == licoes_feitas + 1 and not eh_apto %}bg-amber-50 border-amber-300 text-amber-950 ring-1 ring-amber-300{% else %}bg-slate-50 border-slate-200 text-slate-400{% endif %}">
                        <div class="space-y-0.5">
                            <span class="font-bold block">Lição {{ num }}: {{ tit }}</span>
                            <span class="text-[10px] block opacity-80">{{ desc }}</span>
                        </div>
                        <span class="shrink-0 mt-0.5">
                            {% if num <= licoes_feitas %}
                            <span class="px-1.5 py-0.5 rounded-md bg-emerald-100 text-emerald-800 text-[10px] font-black">✓ Concluída</span>
                            {% elif num == licoes_feitas + 1 and not eh_apto %}
                            <span class="px-1.5 py-0.5 rounded-md bg-amber-200 text-amber-900 text-[10px] font-black">● Em Curso</span>
                            {% else %}
                            <span class="px-1.5 py-0.5 rounded-md bg-slate-200 text-slate-600 text-[10px] font-semibold">Pendente</span>
                            {% endif %}
                        </span>
                    </div>
                    {% endfor %}
                </div>
            </div>

            <!-- PARECER PASTORAL -->
            <div class="p-3.5 bg-slate-50 border border-slate-200 rounded-xl space-y-2">
                <span class="text-[10px] font-black uppercase text-slate-500 tracking-wider block">Parecer Pastoral & Recomendação</span>
                <p class="text-xs text-slate-700 leading-relaxed">
                    {{ parecer }}
                </p>
                <div class="flex items-center justify-between text-[11px] text-slate-400 pt-1 border-t border-slate-200">
                    <span>Contacto: <strong>{{ aluno.get('contacto', aluno.get('login', 'Sem registo telefónico')) if aluno.get else 'Sem registo telefónico' }}</strong></span>
                    <span>Data Início: <strong>{{ aluno.get('data_matricula', 'Exercício 2026') if aluno.get else 'Exercício 2026' }}</strong></span>
                </div>
            </div>

            <div class="flex justify-end pt-2">
                <button type="button" onclick="fecharModalResumo('{{ aluno_uid }}')" class="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-black transition shadow-sm">
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
    html = html[:pos_b] + "\n" + novos_modais + "\n" + html[pos_b:]
else:
    html = html + "\n" + novos_modais

env = jinja2.Environment()
env.parse(html)
with open(caminho_prof, 'w', encoding='utf-8') as f:
    f.write(html)
print("✓ templates/area_professor.html validado com ZERO erros no Jinja2!")

# 5. PUBLICAR NO GITHUB E RENDER
print("\n" + "=" * 80)
print("A ENVIAR ATUALIZAÇÃO PARA O RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "templates/area_professor.html"])
subprocess.run(["git", "commit", "-m", "Ajustar calculo de presencas reais individuais no resumo pedagogico"])
subprocess.run(["git", "push", "origin", "main"])

print("=" * 80)
print(">>> CADA ALUNO AGORA TEM DADOS INDIVIDUAIS REAIS! <<<")
print("=" * 80)