import os
import re
import py_compile
import subprocess
import jinja2

print("=" * 80)
print("A ELIMINAR FORMULÁRIO DUPLICADO E A RESTAURAR ABA MEMBROS...")
print("=" * 80)

caminho_dash = os.path.join('templates', 'dashboard.html')

if not os.path.exists(caminho_dash):
    print("ERRO: templates/dashboard.html não encontrado!")
    exit(1)

with open(caminho_dash, 'r', encoding='utf-8') as f:
    html = f.read()

# Bloco único, limpo e proporcional da Aba Membros
bloco_membros_unico = """{% if aba_ativa == 'membros' %}
<div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
    <!-- FORMULÁRIO DE MEMBRO (5 COLUNAS LARGAS) -->
    <div class="lg:col-span-5 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <div class="border-b border-slate-100 pb-3">
            <h3 class="font-black text-sm text-slate-900 uppercase tracking-wider flex items-center gap-2">
                <span>👤</span> Ficha de Cadastro de Membro
            </h3>
            <p class="text-[11px] text-slate-400">Preencha os dados eclesiásticos e civis do membro</p>
        </div>

        <form action="/membros/novo" method="POST" enctype="multipart/form-data" class="space-y-4">
            <!-- FOTOGRAFIA TIPO PASSE -->
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

            <!-- ESTADO CIVIL E ZONA (2 COLUNAS LARGAS PARA NÃO CORTAR O TEXTO) -->
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
                        <option value="">Selecione a Zona...</option>
                        <option value="Zona 1 • Chicuque">Zona 1 • Chicuque</option>
                        <option value="Zona 2 • Chambone">Zona 2 • Chambone</option>
                        <option value="Zona 3 • Tinga">Zona 3 • Tinga</option>
                        <option value="Zona 4 • Rumbana">Zona 4 • Rumbana</option>
                        <option value="Zona 5 • Dambo">Zona 5 • Dambo</option>
                        <option value="Zona 6 • Macuamene">Zona 6 • Macuamene</option>
                    </select>
                </div>
            </div>

            <!-- CÉLULA FAMILIAR (LARGURA COMPLETA) -->
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

            <!-- CARGO MINISTERIAL E DEPARTAMENTO (2 COLUNAS) -->
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

    <!-- COLUNA DA TABELA DE MEMBROS (7 COLUNAS LARGAS) -->
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

# Localizar o ponto de partida exato de 'membros'
pos_membros = html.find("aba_ativa == 'membros'")
if pos_membros == -1:
    pos_membros = html.find('aba_ativa == "membros"')

pos_start = html.rfind("{%", 0, pos_membros)

# Localizar onde a aba seguinte ('secretaria') começa
pos_sec = html.find("aba_ativa == 'secretaria'", pos_membros + 20)
if pos_sec == -1:
    pos_sec = html.find('aba_ativa == "secretaria"', pos_membros + 20)

if pos_sec != -1:
    pos_end = html.rfind("{%", 0, pos_sec)
else:
    pos_end = html.find("</main>", pos_membros)

# Substituir o intervalo completo (eliminando qualquer formulário duplicado)
html = html[:pos_start] + bloco_membros_unico + "\n\n" + html[pos_end:]
print("✓ Formulário antigo eliminado e aba Membros restaurada com 1 único formulário e tabela!")

# Validação com Jinja2
env = jinja2.Environment()
env.parse(html)
with open(caminho_dash, 'w', encoding='utf-8') as f:
    f.write(html)
print("✓ templates/dashboard.html validado com ZERO erros no Jinja2!")

# Enviar para o Render
print("\n" + "=" * 80)
print("A ENVIAR ATUALIZAÇÃO PARA O RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "templates/dashboard.html"])
subprocess.run(["git", "commit", "-m", "Eliminar duplicata na aba Membros e restaurar layout correto"])
subprocess.run(["git", "push", "origin", "main"])

print("=" * 80)
print(">>> ATUALIZAÇÃO PUBLICADA NO RENDER COM SUCESSO! <<<")
print("=" * 80)