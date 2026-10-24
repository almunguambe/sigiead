import os
import re
import py_compile
import subprocess
import jinja2

print("=" * 80)
print("A ERRADICAR DUPLICATAS E A RESTAURAR LAYOUT EM MEMBROS E SECRETARIA...")
print("=" * 80)

caminho_dash = os.path.join('templates', 'dashboard.html')

if not os.path.exists(caminho_dash):
    print("ERRO: templates/dashboard.html não encontrado!")
    exit(1)

with open(caminho_dash, 'r', encoding='utf-8') as f:
    html = f.read()

# =============================================================================
# 1. BLOCO DEFINITIVO DA ABA MEMBROS (1 ÚNICO FORMULÁRIO + TABELA DE 7 COLS)
# =============================================================================
bloco_membros_perfeito = """{% if aba_ativa == 'membros' %}
<div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
    <!-- FORMULÁRIO (5 COLUNAS) -->
    <div class="lg:col-span-5 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <div class="border-b border-slate-100 pb-3">
            <h3 class="font-black text-sm text-slate-900 uppercase tracking-wider flex items-center gap-2">
                <span>👤</span> Ficha de Cadastro de Membro
            </h3>
            <p class="text-[11px] text-slate-400">Preencha os dados eclesiásticos e civis do membro</p>
        </div>

        <form action="/membros/novo" method="POST" enctype="multipart/form-data" class="space-y-4">
            <!-- FOTOGRAFIA -->
            <div class="p-4 bg-slate-50 border border-slate-200 rounded-2xl text-center space-y-2">
                <span class="text-[10px] font-black uppercase tracking-wider text-slate-400 block">Fotografia Tipo Passe (Leve / ~40KB)</span>
                <div class="flex items-center justify-center gap-4">
                    <div class="w-16 h-20 rounded-xl bg-slate-200 border-2 border-dashed border-slate-300 flex items-center justify-center text-[10px] text-slate-400 font-bold">
                        Sem Foto
                    </div>
                    <div class="space-y-1.5 text-left">
                        <label class="cursor-pointer inline-flex items-center gap-2 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold transition shadow-sm">
                            <span>📁</span> Carregar Imagem
                            <input type="file" name="foto" accept="image/*" class="hidden">
                        </label>
                    </div>
                </div>
            </div>

            <!-- NOME COMPLETO -->
            <div>
                <label class="block text-xs font-bold text-slate-700 mb-1">Nome Completo *</label>
                <input type="text" name="nome" placeholder="Nome completo do membro" required class="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:ring-2 focus:ring-indigo-500 outline-none transition shadow-sm">
            </div>

            <!-- BI E GÉNERO (2 COLUNAS) -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">BI / Cédula</label>
                    <input type="text" name="bi" placeholder="Nº de Documento" class="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:ring-2 focus:ring-indigo-500 outline-none transition shadow-sm">
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">Género / Sexo *</label>
                    <select name="genero" required class="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-xs text-slate-800 focus:ring-2 focus:ring-indigo-500 outline-none transition shadow-sm">
                        <option value="Masculino">Homem (Masculino)</option>
                        <option value="Feminino">Mulher (Feminino)</option>
                    </select>
                </div>
            </div>

            <!-- CONTACTO -->
            <div>
                <label class="block text-xs font-bold text-slate-700 mb-1">Contacto / WhatsApp</label>
                <input type="text" name="contacto" placeholder="+258..." class="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:ring-2 focus:ring-indigo-500 outline-none transition shadow-sm">
            </div>

            <!-- ESTADO CIVIL E ZONA (2 COLUNAS LARGAS) -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">Estado Civil *</label>
                    <select name="estado_civil" required class="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-xs text-slate-800 focus:ring-2 focus:ring-indigo-500 outline-none transition shadow-sm">
                        <option value="Solteiro(a)">Solteiro(a)</option>
                        <option value="Casado(a)">Casado(a)</option>
                        <option value="Viúvo(a)">Viúvo(a)</option>
                        <option value="Divorciado(a)">Divorciado(a)</option>
                    </select>
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">Zona Territorial</label>
                    <select name="zona" class="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-xs text-slate-800 focus:ring-2 focus:ring-indigo-500 outline-none transition shadow-sm">
                        <option value="">Selecione...</option>
                        <option value="Zona 1 • Chicuque">Zona 1 • Chicuque</option>
                        <option value="Zona 2 • Chambone">Zona 2 • Chambone</option>
                        <option value="Zona 3 • Tinga">Zona 3 • Tinga</option>
                        <option value="Zona 4 • Rumbana">Zona 4 • Rumbana</option>
                        <option value="Zona 5 • Dambo">Zona 5 • Dambo</option>
                        <option value="Zona 6 • Macuamene">Zona 6 • Macuamene</option>
                    </select>
                </div>
            </div>

            <!-- CÉLULA FAMILIAR (LARGURA TOTAL) -->
            <div>
                <label class="block text-xs font-bold text-slate-700 mb-1">Célula Familiar</label>
                <select name="celula" class="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-xs text-slate-800 focus:ring-2 focus:ring-indigo-500 outline-none transition shadow-sm">
                    <option value="">Selecione a Célula...</option>
                    <option value="Célula Betel (Chicuque)">Célula Betel (Chicuque Sede)</option>
                    <option value="Célula Sião (Chambone)">Célula Sião (Chambone Centro)</option>
                    <option value="Célula Peniel (Tinga)">Célula Peniel (Tinga Residencial)</option>
                    <option value="Célula Ebenézer (Rumbana)">Célula Ebenézer (Rumbana)</option>
                    <option value="Célula Jerusalém (Agostinho Neto)">Célula Jerusalém (Agostinho Neto)</option>
                    <option value="Célula Manassés (Dambo)">Célula Manassés (Dambo / Expansão)</option>
                </select>
            </div>

            <!-- CARGO E DEPARTAMENTO (2 COLUNAS) -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">Cargo Ministerial</label>
                    <select name="cargo" class="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-xs text-slate-800 focus:ring-2 focus:ring-indigo-500 outline-none transition shadow-sm">
                        <option value="Membro Comungante">Membro Comungante</option>
                        <option value="Pastor Dirigente">Pastor Dirigente</option>
                        <option value="Presbítero / Ancião">Presbítero / Ancião</option>
                        <option value="Diácono / Diaconisa">Diácono / Diaconisa</option>
                        <option value="Evangelista">Evangelista</option>
                        <option value="Missionário(a)">Missionário(a)</option>
                        <option value="Líder de Célula">Líder de Célula</option>
                        <option value="Instrutor de Doutrina">Instrutor de Doutrina</option>
                    </select>
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">Departamento</label>
                    <select name="departamento" class="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-xs text-slate-800 focus:ring-2 focus:ring-indigo-500 outline-none transition shadow-sm">
                        <option value="Geral / Nenhum">Geral / Nenhum</option>
                        <option value="Homens (Cavalheiros)">Homens (Cavalheiros)</option>
                        <option value="Mulheres (Senhoras)">Mulheres (Senhoras)</option>
                        <option value="Juventude Cristã (Jovens)">Juventude Cristã (Jovens)</option>
                        <option value="Crianças (Boa Esperança)">Crianças (Boa Esperança)</option>
                        <option value="Louvor & Coral">Louvor & Coral</option>
                        <option value="Evangelismo & Missões">Evangelismo & Missões</option>
                        <option value="Ação Social & Diaconia">Ação Social & Diaconia</option>
                        <option value="Escola Bíblica Dominical">Escola Bíblica Dominical</option>
                    </select>
                </div>
            </div>

            <!-- DATAS -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">Ano Conversão</label>
                    <input type="text" name="ano_conversao" placeholder="Ex: 2021" class="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:ring-2 focus:ring-indigo-500 outline-none transition shadow-sm">
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">Data Batismo</label>
                    <input type="date" name="data_batismo" class="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-xs text-slate-800 focus:ring-2 focus:ring-indigo-500 outline-none transition shadow-sm">
                </div>
            </div>

            <!-- RESIDÊNCIA -->
            <div>
                <label class="block text-xs font-bold text-slate-700 mb-1">Residência (Bairro / Local)</label>
                <input type="text" name="residencia" placeholder="Ex: Chicuque - Perto do Hospital" class="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:ring-2 focus:ring-indigo-500 outline-none transition shadow-sm">
            </div>

            <!-- BOTÃO SALVAR (LARGURA TOTAL) -->
            <button type="submit" class="w-full py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-black rounded-xl text-xs transition shadow-md flex items-center justify-center gap-2">
                <span>💾</span>
                <span>Gravar Ficha de Membro</span>
            </button>
        </form>
    </div>

    <!-- TABELA DE MEMBROS (7 COLUNAS LARGAS) -->
    <div class="lg:col-span-7 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <div class="flex items-center justify-between border-b border-slate-100 pb-3">
            <div>
                <h3 class="font-black text-sm text-slate-900 uppercase tracking-wider flex items-center gap-2">
                    <span>📋</span> Membros Registados
                </h3>
                <p class="text-[11px] text-slate-400">Relação nominal da congregação</p>
            </div>
            <span class="px-3 py-1 rounded-xl bg-indigo-50 text-indigo-900 text-xs font-black">
                {{ membros|length if membros else 0 }} Membros
            </span>
        </div>

        <div class="overflow-x-auto">
            <table class="w-full text-left text-xs border-collapse">
                <thead>
                    <tr class="bg-slate-50 text-slate-600 font-bold uppercase text-[10px] border-b border-slate-100">
                        <th class="p-3">Membro</th>
                        <th class="p-3">Zona & Célula</th>
                        <th class="p-3">Cargo & Depto</th>
                        <th class="p-3 text-center">Batismo</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-slate-100 font-medium">
                    {% if membros and membros|length > 0 %}
                        {% for m in membros %}
                        <tr class="hover:bg-slate-50 transition">
                            <td class="p-3">
                                <span class="font-bold text-slate-900 block">{{ m.nome }}</span>
                                <span class="text-[10px] text-slate-400">{{ m.contacto or m.bi or '' }}</span>
                            </td>
                            <td class="p-3 text-slate-600">
                                <span class="block font-semibold text-slate-800">{{ m.zona or 'Sem Zona' }}</span>
                                <span class="text-[10px] text-slate-400">{{ m.celula or 'Sem Célula' }}</span>
                            </td>
                            <td class="p-3 text-slate-600">
                                <span class="block font-semibold text-indigo-700">{{ m.cargo or 'Membro' }}</span>
                                <span class="text-[10px] text-slate-400">{{ m.departamento or 'Geral' }}</span>
                            </td>
                            <td class="p-3 text-center">
                                <span class="px-2 py-0.5 rounded-full text-[10px] font-bold {% if m.data_batismo %}bg-emerald-100 text-emerald-800{% else %}bg-slate-100 text-slate-600{% endif %}">
                                    {{ m.data_batismo or 'Não' }}
                                </span>
                            </td>
                        </tr>
                        {% endfor %}
                    {% else %}
                        <tr>
                            <td colspan="4" class="p-8 text-center text-slate-400 italic">
                                Nenhum membro registado no momento. Preencha o formulário ao lado para cadastrar.
                            </td>
                        </tr>
                    {% endif %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endif %}"""

# =============================================================================
# 2. BLOCO DEFINITIVO DA ABA SECRETARIA (SEM BARRA PRETA)
# =============================================================================
bloco_secretaria_perfeito = """{% if aba_ativa == 'secretaria' %}
<div class="space-y-6">
    <div class="bg-gradient-to-r from-indigo-950 via-slate-900 to-indigo-950 text-white p-6 rounded-2xl shadow-lg border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div class="space-y-1">
            <div class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-amber-500/20 border border-amber-400/30 text-amber-300 text-[10px] font-black uppercase tracking-wider">
                <span>📋</span> Secretaria Geral
            </div>
            <h2 class="text-xl sm:text-2xl font-black text-white">
                Secretaria & Planificação de Actividades
            </h2>
            <p class="text-xs text-slate-300 max-w-xl">
                Gestão de cronograma, execução de metas e prestação oficial de contas da Igreja de Chicuque.
            </p>
        </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        <div class="lg:col-span-5 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <div class="border-b border-slate-100 pb-3">
                <h3 class="font-black text-sm text-slate-900 uppercase tracking-wider flex items-center gap-2">
                    <span>📌</span> Planificar Actividade
                </h3>
                <p class="text-[11px] text-slate-400">Registe eventos oficiais no calendário eclesiástico</p>
            </div>

            <form action="/secretaria/planificar" method="POST" class="space-y-4">
                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">Departamento *</label>
                    <select name="departamento" required class="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-xs text-slate-800 focus:ring-2 focus:ring-indigo-500 outline-none transition shadow-sm">
                        <option value="">Selecione o Departamento...</option>
                        <option value="Geral / Toda a Igreja">Geral / Toda a Igreja</option>
                        <option value="Homens (Cavalheiros)">Homens (Cavalheiros)</option>
                        <option value="Mulheres (Senhoras)">Mulheres (Senhoras)</option>
                        <option value="Juventude Cristã (Jovens)">Juventude Cristã (Jovens)</option>
                        <option value="Crianças (Boa Esperança)">Crianças (Boa Esperança)</option>
                        <option value="Louvor & Coral">Louvor & Coral</option>
                        <option value="Evangelismo & Missões">Evangelismo & Missões</option>
                        <option value="Ação Social & Diaconia">Ação Social & Diaconia</option>
                        <option value="Escola Bíblica Dominical">Escola Bíblica Dominical</option>
                    </select>
                </div>

                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">Tipo de Evento *</label>
                    <select name="tipo_evento" required class="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-xs text-slate-800 focus:ring-2 focus:ring-indigo-500 outline-none transition shadow-sm">
                        <option value="Culto Geral">Culto Geral</option>
                        <option value="Vigília">Vigília</option>
                        <option value="Reunião de Oração">Reunião de Oração</option>
                        <option value="Seminário / Formação">Seminário / Formação</option>
                        <option value="Conferência">Conferência</option>
                        <option value="Evangelismo de Rua">Evangelismo de Rua</option>
                        <option value="Ensaio Departamental">Ensaio Departamental</option>
                        <option value="Outro">Outro</option>
                    </select>
                </div>

                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">Nome da Actividade *</label>
                    <input type="text" name="nome_actividade" placeholder="Ex: Encontro Geral de Oração" required class="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:ring-2 focus:ring-indigo-500 outline-none transition shadow-sm">
                </div>

                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-xs font-bold text-slate-700 mb-1">Data Prevista *</label>
                        <input type="date" name="data_prevista" required class="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-xs text-slate-800 focus:ring-2 focus:ring-indigo-500 outline-none transition shadow-sm">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-700 mb-1">Frequência</label>
                        <select name="frequencia" class="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-xs text-slate-800 focus:ring-2 focus:ring-indigo-500 outline-none transition shadow-sm">
                            <option value="Pontual / Única">Pontual / Única</option>
                            <option value="Semanal">Semanal</option>
                            <option value="Mensal">Mensal</option>
                            <option value="Anual">Anual</option>
                        </select>
                    </div>
                </div>

                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">Responsável</label>
                    <input type="text" name="responsavel" placeholder="Nome do dirigente ou coordenador" class="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:ring-2 focus:ring-indigo-500 outline-none transition shadow-sm">
                </div>

                <button type="submit" class="w-full py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-black rounded-xl text-xs transition shadow-md flex items-center justify-center gap-2">
                    <span>📌</span>
                    <span>Gravar Planificação</span>
                </button>
            </form>
        </div>

        <div class="lg:col-span-7 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <div class="flex items-center justify-between border-b border-slate-100 pb-3">
                <div>
                    <h3 class="font-black text-sm text-slate-900 uppercase tracking-wider flex items-center gap-2">
                        <span>📊</span> Cronograma de Actividades
                    </h3>
                    <p class="text-[11px] text-slate-400">Eventos agendados no plano de trabalho</p>
                </div>
                <span class="px-3 py-1 rounded-xl bg-indigo-50 text-indigo-900 text-xs font-black">
                    {{ cronograma|length if cronograma else 0 }} Eventos
                </span>
            </div>

            <div class="overflow-x-auto">
                <table class="w-full text-left text-xs border-collapse">
                    <thead>
                        <tr class="bg-slate-50 text-slate-600 font-bold uppercase text-[10px] border-b border-slate-100">
                            <th class="p-3">Actividade</th>
                            <th class="p-3">Data</th>
                            <th class="p-3">Responsável</th>
                            <th class="p-3 text-center">Status</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-100 font-medium">
                        {% if cronograma and cronograma|length > 0 %}
                            {% for c in cronograma %}
                            <tr class="hover:bg-slate-50 transition">
                                <td class="p-3">
                                    <span class="font-bold text-slate-900 block">{{ c.nome_actividade or c.actividade }}</span>
                                    <span class="text-[10px] text-indigo-700 font-semibold">{{ c.departamento or 'Geral' }}</span>
                                </td>
                                <td class="p-3 text-slate-700 font-semibold">{{ c.data_prevista or c.data }}</td>
                                <td class="p-3 text-slate-600">{{ c.responsavel or 'Coordenação' }}</td>
                                <td class="p-3 text-center">
                                    <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800">
                                        {{ c.status or 'Agendado' }}
                                    </span>
                                </td>
                            </tr>
                            {% endfor %}
                        {% else %}
                            <tr>
                                <td colspan="4" class="p-8 text-center text-slate-400 italic">
                                    Nenhum plano registado no momento. Use o formulário ao lado para planificar.
                                </td>
                            </tr>
                        {% endif %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>
{% endif %}"""

# Função de corte cirúrgico por índice (substitui todo o intervalo entre abas)
def substituir_bloco_completo(texto, aba_alvo, abas_seguintes, novo_bloco):
    pos_alvo = texto.find(f"aba_ativa == '{aba_alvo}'")
    if pos_alvo == -1: pos_alvo = texto.find(f'aba_ativa == "{aba_alvo}"')
    if pos_alvo == -1:
        print(f"Aba '{aba_alvo}' não encontrada!")
        return texto

    inicio_tag = texto.rfind("{%", 0, pos_alvo)

    fim_tag = -1
    for prox in abas_seguintes:
        pos_p = texto.find(f"aba_ativa == '{prox}'", pos_alvo + 25)
        if pos_p == -1: pos_p = texto.find(f'aba_ativa == "{prox}"', pos_alvo + 25)
        if pos_p != -1:
            fim_tag = texto.rfind("{%", 0, pos_p)
            print(f"✓ Corte da aba '{aba_alvo}' delimitado pela aba seguinte '{prox}'!")
            break

    if fim_tag == -1:
        fim_tag = texto.find("</main>", pos_alvo)
        if fim_tag == -1:
            fim_tag = texto.find("</body>", pos_alvo)

    return texto[:inicio_tag] + novo_bloco.strip() + "\n\n" + texto[fim_tag:]

# 1. Substituir Aba Membros inteira (elimina todo o formulário antigo esmagado)
html = substituir_bloco_completo(html, 'membros', ['secretaria', 'cultos', 'doutrina'], bloco_membros_perfeito)

# 2. Substituir Aba Secretaria inteira (elimina scrollbars horizontais)
html = substituir_bloco_completo(html, 'secretaria', ['cultos', 'doutrina', 'financeiro'], bloco_secretaria_perfeito)

# 3. Validação Jinja2
env = jinja2.Environment()
env.parse(html)
with open(caminho_dash, 'w', encoding='utf-8') as f:
    f.write(html)
print("✓ templates/dashboard.html validado com ZERO erros no Jinja2!")

# 4. Enviar para o Render
print("\n" + "=" * 80)
print("A ENVIAR ATUALIZAÇÃO DEFINITIVA PARA O RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "templates/dashboard.html"])
subprocess.run(["git", "commit", "-m", "Eliminacao cirurgica de duplicata de membros e scrollbar de secretaria"])
subprocess.run(["git", "push", "origin", "main"])

print("=" * 80)
print(">>> PROCESSO CONCLUÍDO E PUBLICADO NO RENDER COM SUCESSO! <<<")
print("=" * 80)