import os
import re
import subprocess
import jinja2

print("=" * 80)
print("A APLICAR RAIO-X DEMOGRÁFICO EXECUTIVO (ZONAS & CÉLULAS FAMILIARES)...")
print("=" * 80)

caminho_dash = os.path.join('templates', 'dashboard.html')

with open(caminho_dash, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. LOCALIZAR A SEÇÃO DO DASHBOARD ESTRITAMENTE DENTRO DE <main> (DEPOIS DE </aside>)
pos_aside_end = html.find('</aside>')
if pos_aside_end == -1:
    print("Erro: tag </aside> não encontrada.")
    exit(1)

pos_main = html.find('<main', pos_aside_end)
if pos_main == -1:
    pos_main = pos_aside_end

pos_dash_main = html.find("{% if aba_ativa == 'dashboard' %}", pos_main)
if pos_dash_main == -1:
    print("Erro: Bloco do dashboard não encontrado dentro de <main>.")
    exit(1)

# Função para identificar o fecho exato do bloco no Jinja2
def encontrar_matching_endif(texto, pos_inicio):
    pos = texto.find("%}", pos_inicio) + 2
    contador = 1
    tag_pat = re.compile(r"{%\s*(if\b|endif\b)")
    for match in tag_pat.finditer(texto, pos):
        tag = match.group(1)
        if tag.startswith('if'):
            contador += 1
        elif tag == 'endif':
            contador -= 1
            if contador == 0:
                return texto.find("%}", match.start()) + 2
    return -1

pos_dash_fim = encontrar_matching_endif(html, pos_dash_main)
if pos_dash_fim == -1:
    print("Erro: Fecho {% endif %} do dashboard não encontrado.")
    exit(1)

# 2. NOVO BLOCO EXECUTIVO DO RAIO-X COM DEMOGRAFIA DE ZONAS E CÉLULAS
novo_raiox_executivo = """{% if aba_ativa == 'dashboard' %}
        <!-- CABEÇALHO EXECUTIVO DO RAIO-X DEMOGRÁFICO -->
        <div class="w-full bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white p-6 rounded-3xl shadow-xl mb-6 flex flex-col md:flex-row md:items-center justify-between gap-5 border border-slate-800">
            <div class="flex items-center gap-4">
                <div class="w-14 h-14 rounded-2xl bg-gradient-to-tr from-amber-500 to-indigo-600 p-0.5 shadow-lg flex items-center justify-center shrink-0">
                    <div class="w-full h-full bg-slate-900 rounded-[14px] flex items-center justify-center text-white text-xl font-black">
                        ✝
                    </div>
                </div>
                <div>
                    <div class="inline-flex items-center gap-2 bg-indigo-500/20 text-indigo-300 px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider mb-1.5 border border-indigo-400/30">
                        <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span> CENSO ECLESIÁSTICO & DEMOGRAFIA INTEGRAL
                    </div>
                    <h2 class="text-2xl font-black tracking-tight text-white">Raio-X Ministerial: Igreja de Chicuque</h2>
                    <p class="text-xs text-slate-300">Panorama demográfico de membros, células familiares e zonas territoriais em Maxixe</p>
                </div>
            </div>
            
            <div class="bg-white/5 backdrop-blur-md px-5 py-3.5 rounded-2xl border border-white/10 flex items-center gap-4 shrink-0">
                <div>
                    <span class="text-[10px] uppercase font-bold text-slate-400 block tracking-wider">Total de Almas no Rebanho</span>
                    <div class="flex items-baseline gap-2">
                        <span class="text-3xl font-black text-amber-400">{{ (total_membros|default(0)) + (doutrina|length if doutrina is defined else 0) }}</span>
                        <span class="text-xs text-slate-300 font-semibold">Vidas</span>
                    </div>
                    <span class="text-[10px] text-slate-400 block mt-0.5">{{ total_membros|default(0) }} Membros • {{ doutrina|length if doutrina is defined else 0 }} em Doutrina</span>
                </div>
            </div>
        </div>

        <!-- 4 CARDS ANALÍTICOS EXECUTIVOS (KPIs) -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6 text-xs">
            
            <!-- CARD 1: DISTRIBUIÇÃO POR GÉNERO -->
            <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 hover:shadow-md transition flex flex-col justify-between">
                <div>
                    <div class="flex items-center justify-between mb-3">
                        <span class="text-[11px] font-black uppercase tracking-wider text-slate-500">Distribuição por Género</span>
                        <span class="p-2 rounded-xl bg-indigo-50 text-indigo-600">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path></svg>
                        </span>
                    </div>

                    <div class="grid grid-cols-2 gap-3 py-2">
                        <div class="p-3 bg-slate-50 rounded-xl border border-slate-100">
                            <span class="text-[10px] font-bold text-slate-500 block uppercase">Homens</span>
                            <span class="text-2xl font-black text-slate-800">{{ total_homens|default(0) }}</span>
                        </div>
                        <div class="p-3 bg-rose-50/60 rounded-xl border border-rose-100">
                            <span class="text-[10px] font-bold text-rose-600 block uppercase">Mulheres</span>
                            <span class="text-2xl font-black text-rose-900">{{ total_mulheres|default(0) }}</span>
                        </div>
                    </div>
                </div>

                <div class="pt-3 border-t border-slate-100">
                    <div class="w-full bg-slate-100 rounded-full h-2 flex overflow-hidden">
                        <div class="bg-indigo-600 h-2" style="width: 50%"></div>
                        <div class="bg-rose-500 h-2" style="width: 50%"></div>
                    </div>
                    <div class="flex justify-between text-[10px] text-slate-400 font-bold mt-1.5">
                        <span>Homens</span>
                        <span>Mulheres</span>
                    </div>
                </div>
            </div>

            <!-- CARD 2: COMPOSIÇÃO ETÁRIA -->
            <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 hover:shadow-md transition flex flex-col justify-between">
                <div>
                    <div class="flex items-center justify-between mb-3">
                        <span class="text-[11px] font-black uppercase tracking-wider text-slate-500">Pirâmide Geracional</span>
                        <span class="p-2 rounded-xl bg-amber-50 text-amber-600">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
                        </span>
                    </div>

                    <div class="space-y-2 text-xs">
                        <div class="flex justify-between items-center">
                            <span class="text-slate-600 font-semibold flex items-center gap-1.5">
                                <span class="w-2 h-2 rounded-full bg-amber-400"></span> Crianças (Boa Esperança):
                            </span>
                            <span class="font-black text-slate-800">{{ total_criancas|default(0) }}</span>
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-slate-600 font-semibold flex items-center gap-1.5">
                                <span class="w-2 h-2 rounded-full bg-blue-500"></span> Juventude Cristã:
                            </span>
                            <span class="font-black text-slate-800">{{ total_jovens|default(0) }}</span>
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-slate-600 font-semibold flex items-center gap-1.5">
                                <span class="w-2 h-2 rounded-full bg-indigo-600"></span> Adultos & Seniores:
                            </span>
                            <span class="font-black text-slate-800">{{ total_adultos|default(0) }}</span>
                        </div>
                    </div>
                </div>

                <div class="pt-3 border-t border-slate-100 flex items-center justify-between text-[10px] text-slate-400">
                    <span>Faixas Activas</span>
                    <span class="font-bold text-slate-600">3 Gerações</span>
                </div>
            </div>

            <!-- CARD 3: SITUAÇÃO ECLESIÁSTICA -->
            <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 hover:shadow-md transition flex flex-col justify-between">
                <div>
                    <div class="flex items-center justify-between mb-3">
                        <span class="text-[11px] font-black uppercase tracking-wider text-slate-500">Maturidade Eclesiástica</span>
                        <span class="p-2 rounded-xl bg-emerald-50 text-emerald-600">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                        </span>
                    </div>

                    <div class="space-y-2 text-xs">
                        <div class="flex justify-between items-center">
                            <span class="text-emerald-700 font-semibold flex items-center gap-1.5">
                                <span class="w-2 h-2 rounded-full bg-emerald-500"></span> Membros Baptizados:
                            </span>
                            <span class="font-black text-emerald-900">{{ total_baptizados|default(0) }}</span>
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-amber-700 font-semibold flex items-center gap-1.5">
                                <span class="w-2 h-2 rounded-full bg-amber-500"></span> Em Formação / Doutrina:
                            </span>
                            <span class="font-black text-amber-900">{{ doutrina|length if doutrina is defined else 0 }}</span>
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-blue-700 font-semibold flex items-center gap-1.5">
                                <span class="w-2 h-2 rounded-full bg-blue-500"></span> Novos Convertidos:
                            </span>
                            <span class="font-black text-blue-900">{{ total_convertidos|default(0) }}</span>
                        </div>
                    </div>
                </div>

                <div class="pt-3 border-t border-slate-100 flex items-center justify-between text-[10px]">
                    <span class="text-slate-400">Aptos p/ Santa Ceia</span>
                    <span class="font-bold text-emerald-700">{{ total_baptizados|default(0) }} Membros</span>
                </div>
            </div>

            <!-- CARD 4: ACTOS & PLANIFICAÇÃO -->
            <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 hover:shadow-md transition flex flex-col justify-between">
                <div>
                    <div class="flex items-center justify-between mb-3">
                        <span class="text-[11px] font-black uppercase tracking-wider text-slate-500">Actos & Planificação</span>
                        <span class="p-2 rounded-xl bg-purple-50 text-purple-600">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                        </span>
                    </div>

                    <div class="space-y-2 text-xs">
                        <div class="flex justify-between items-center">
                            <span class="text-slate-600 font-semibold flex items-center gap-1.5">
                                <span class="w-2 h-2 rounded-full bg-purple-500"></span> Casamentos no Ano:
                            </span>
                            <span class="font-black text-purple-900">{{ total_casamentos|default(0) }}</span>
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-slate-600 font-semibold flex items-center gap-1.5">
                                <span class="w-2 h-2 rounded-full bg-slate-400"></span> Óbitos / Falecimentos:
                            </span>
                            <span class="font-black text-slate-700">{{ total_obitos|default(0) }}</span>
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-slate-600 font-semibold flex items-center gap-1.5">
                                <span class="w-2 h-2 rounded-full bg-emerald-500"></span> Eficácia de Metas:
                            </span>
                            <span class="font-black text-emerald-600">100%</span>
                        </div>
                    </div>
                </div>

                <div class="pt-3 border-t border-slate-100 flex items-center justify-between text-[10px] text-slate-400">
                    <span>Estado Pastoral</span>
                    <span class="font-bold text-emerald-600">Pleno</span>
                </div>
            </div>

        </div>

        <!-- SEÇÃO 1: CARTOGRAFIA DEMOGRÁFICA POR ZONAS (MAXIXE & CHICUQUE) -->
        <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 mb-6">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-100 pb-4 mb-4 gap-2">
                <div class="flex items-center gap-3">
                    <div class="p-2.5 bg-indigo-50 text-indigo-700 rounded-xl">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                    </div>
                    <div>
                        <h3 class="font-black text-sm text-slate-900 uppercase">Cartografia Ministerial: Demografia por Zonas e Bairros</h3>
                        <p class="text-xs text-slate-500">Membros residentes e cobertura congregacional na cidade de Maxixe</p>
                    </div>
                </div>
                <span class="text-xs font-bold text-indigo-700 bg-indigo-50 px-3 py-1 rounded-full border border-indigo-100 shrink-0 self-start sm:self-auto">
                    📍 Cidade de Maxixe • Inhambane
                </span>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5 text-xs">
                <div class="p-4 bg-slate-50 rounded-xl border border-slate-200 hover:border-indigo-300 transition">
                    <div class="flex items-center justify-between mb-1.5">
                        <span class="text-[10px] font-bold text-indigo-900 uppercase tracking-wide">Zona 1 • Sede Regional</span>
                        <span class="w-2 h-2 rounded-full bg-emerald-500" title="Ativa"></span>
                    </div>
                    <span class="font-black text-slate-900 block text-sm">Chicuque (Templo Central)</span>
                    <span class="text-[11px] text-slate-500 block mt-0.5">Sede Administrativa e Cultos Gerais</span>
                    <div class="mt-3 pt-2.5 border-t border-slate-200 flex items-center justify-between text-[11px]">
                        <span class="text-slate-500 font-medium">Membros Vinculados:</span>
                        <span class="font-black text-indigo-950">{{ total_membros|default(0) }} fiéis</span>
                    </div>
                </div>

                <div class="p-4 bg-slate-50 rounded-xl border border-slate-200 hover:border-indigo-300 transition">
                    <div class="flex items-center justify-between mb-1.5">
                        <span class="text-[10px] font-bold text-slate-500 uppercase tracking-wide">Zona 2 • Bairro Urbano</span>
                        <span class="w-2 h-2 rounded-full bg-blue-500"></span>
                    </div>
                    <span class="font-black text-slate-900 block text-sm">Chambone</span>
                    <span class="text-[11px] text-slate-500 block mt-0.5">Núcleo Central da Cidade de Maxixe</span>
                    <div class="mt-3 pt-2.5 border-t border-slate-200 flex items-center justify-between text-[11px]">
                        <span class="text-slate-500 font-medium">Membros Vinculados:</span>
                        <span class="font-black text-slate-800">Núcleo Urbano</span>
                    </div>
                </div>

                <div class="p-4 bg-slate-50 rounded-xl border border-slate-200 hover:border-indigo-300 transition">
                    <div class="flex items-center justify-between mb-1.5">
                        <span class="text-[10px] font-bold text-slate-500 uppercase tracking-wide">Zona 3 • Área Residencial</span>
                        <span class="w-2 h-2 rounded-full bg-blue-500"></span>
                    </div>
                    <span class="font-black text-slate-900 block text-sm">Tinga</span>
                    <span class="text-[11px] text-slate-500 block mt-0.5">Zona de Alta Densidade Familiar</span>
                    <div class="mt-3 pt-2.5 border-t border-slate-200 flex items-center justify-between text-[11px]">
                        <span class="text-slate-500 font-medium">Membros Vinculados:</span>
                        <span class="font-black text-slate-800">Ponto Familiar</span>
                    </div>
                </div>

                <div class="p-4 bg-slate-50 rounded-xl border border-slate-200 hover:border-indigo-300 transition">
                    <div class="flex items-center justify-between mb-1.5">
                        <span class="text-[10px] font-bold text-slate-500 uppercase tracking-wide">Zona 4 • Bairro de Expansão</span>
                        <span class="w-2 h-2 rounded-full bg-amber-500"></span>
                    </div>
                    <span class="font-black text-slate-900 block text-sm">Rumbana / Agostinho Neto</span>
                    <span class="text-[11px] text-slate-500 block mt-0.5">Crescimento Populacional Contínuo</span>
                    <div class="mt-3 pt-2.5 border-t border-slate-200 flex items-center justify-between text-[11px]">
                        <span class="text-slate-500 font-medium">Membros Vinculados:</span>
                        <span class="font-black text-slate-800">Células Ativas</span>
                    </div>
                </div>

                <div class="p-4 bg-slate-50 rounded-xl border border-slate-200 hover:border-indigo-300 transition">
                    <div class="flex items-center justify-between mb-1.5">
                        <span class="text-[10px] font-bold text-slate-500 uppercase tracking-wide">Zona 5 • Periferia & Litoral</span>
                        <span class="w-2 h-2 rounded-full bg-amber-500"></span>
                    </div>
                    <span class="font-black text-slate-900 block text-sm">Dambo / Malalane</span>
                    <span class="text-[11px] text-slate-500 block mt-0.5">Frente de Evangelismo e Oração</span>
                    <div class="mt-3 pt-2.5 border-t border-slate-200 flex items-center justify-between text-[11px]">
                        <span class="text-slate-500 font-medium">Membros Vinculados:</span>
                        <span class="font-black text-slate-800">Missão Local</span>
                    </div>
                </div>

                <div class="p-4 bg-slate-50 rounded-xl border border-slate-200 hover:border-indigo-300 transition">
                    <div class="flex items-center justify-between mb-1.5">
                        <span class="text-[10px] font-bold text-slate-500 uppercase tracking-wide">Zona 6 • Extensão</span>
                        <span class="w-2 h-2 rounded-full bg-purple-500"></span>
                    </div>
                    <span class="font-black text-slate-900 block text-sm">Macuamene / Bembe</span>
                    <span class="text-[11px] text-slate-500 block mt-0.5">Pontos de Pregação e Visitação</span>
                    <div class="mt-3 pt-2.5 border-t border-slate-200 flex items-center justify-between text-[11px]">
                        <span class="text-slate-500 font-medium">Membros Vinculados:</span>
                        <span class="font-black text-slate-800">Visitação</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- SEÇÃO 2: REDE DE CÉLULAS FAMILIARES NOS LARES (6 CÉLULAS ESTRUTURADAS) -->
        <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 mb-6">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-100 pb-4 mb-4 gap-2">
                <div class="flex items-center gap-3">
                    <div class="p-2.5 bg-amber-50 text-amber-700 rounded-xl">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path></svg>
                    </div>
                    <div>
                        <h3 class="font-black text-sm text-slate-900 uppercase">Rede de Células Familiares: A Igreja nos Lares</h3>
                        <p class="text-xs text-slate-500">Grupos de comunhão semanal, estudo bíblico e discipulado nos bairros</p>
                    </div>
                </div>
                <span class="text-xs font-bold text-amber-800 bg-amber-50 px-3 py-1 rounded-full border border-amber-200 shrink-0 self-start sm:self-auto">
                    🏠 6 Células Estruturadas
                </span>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5 text-xs">
                <div class="p-4 bg-slate-50 rounded-xl border border-slate-200 hover:border-amber-400 transition">
                    <div class="flex items-center justify-between mb-1">
                        <span class="font-black text-slate-900 text-sm">Célula Betel</span>
                        <span class="px-2 py-0.5 bg-emerald-100 text-emerald-800 text-[10px] font-bold rounded-md">Ativa</span>
                    </div>
                    <span class="text-[11px] text-slate-500 block mb-2">Bairro Chicuque Sede</span>
                    <div class="space-y-1 text-[11px] pt-2 border-t border-slate-200 text-slate-600">
                        <div class="flex justify-between">
                            <span>Reunião Semanal:</span>
                            <b class="text-slate-800">Quintas • 17h30</b>
                        </div>
                        <div class="flex justify-between">
                            <span>Liderança:</span>
                            <b class="text-indigo-900">Diaconato Local</b>
                        </div>
                    </div>
                </div>

                <div class="p-4 bg-slate-50 rounded-xl border border-slate-200 hover:border-amber-400 transition">
                    <div class="flex items-center justify-between mb-1">
                        <span class="font-black text-slate-900 text-sm">Célula Sião</span>
                        <span class="px-2 py-0.5 bg-emerald-100 text-emerald-800 text-[10px] font-bold rounded-md">Ativa</span>
                    </div>
                    <span class="text-[11px] text-slate-500 block mb-2">Bairro Chambone Centro</span>
                    <div class="space-y-1 text-[11px] pt-2 border-t border-slate-200 text-slate-600">
                        <div class="flex justify-between">
                            <span>Reunião Semanal:</span>
                            <b class="text-slate-800">Terças • 18h00</b>
                        </div>
                        <div class="flex justify-between">
                            <span>Liderança:</span>
                            <b class="text-indigo-900">Líder Designado</b>
                        </div>
                    </div>
                </div>

                <div class="p-4 bg-slate-50 rounded-xl border border-slate-200 hover:border-amber-400 transition">
                    <div class="flex items-center justify-between mb-1">
                        <span class="font-black text-slate-900 text-sm">Célula Peniel</span>
                        <span class="px-2 py-0.5 bg-emerald-100 text-emerald-800 text-[10px] font-bold rounded-md">Ativa</span>
                    </div>
                    <span class="text-[11px] text-slate-500 block mb-2">Bairro Tinga</span>
                    <div class="space-y-1 text-[11px] pt-2 border-t border-slate-200 text-slate-600">
                        <div class="flex justify-between">
                            <span>Reunião Semanal:</span>
                            <b class="text-slate-800">Quartas • 17h00</b>
                        </div>
                        <div class="flex justify-between">
                            <span>Liderança:</span>
                            <b class="text-indigo-900">Coordenação Local</b>
                        </div>
                    </div>
                </div>

                <div class="p-4 bg-slate-50 rounded-xl border border-slate-200 hover:border-amber-400 transition">
                    <div class="flex items-center justify-between mb-1">
                        <span class="font-black text-slate-900 text-sm">Célula Ebenézer</span>
                        <span class="px-2 py-0.5 bg-emerald-100 text-emerald-800 text-[10px] font-bold rounded-md">Ativa</span>
                    </div>
                    <span class="text-[11px] text-slate-500 block mb-2">Bairro Rumbana</span>
                    <div class="space-y-1 text-[11px] pt-2 border-t border-slate-200 text-slate-600">
                        <div class="flex justify-between">
                            <span>Reunião Semanal:</span>
                            <b class="text-slate-800">Sextas • 17h30</b>
                        </div>
                        <div class="flex justify-between">
                            <span>Liderança:</span>
                            <b class="text-indigo-900">Obreiro de Apoio</b>
                        </div>
                    </div>
                </div>

                <div class="p-4 bg-slate-50 rounded-xl border border-slate-200 hover:border-amber-400 transition">
                    <div class="flex items-center justify-between mb-1">
                        <span class="font-black text-slate-900 text-sm">Célula Jerusalém</span>
                        <span class="px-2 py-0.5 bg-emerald-100 text-emerald-800 text-[10px] font-bold rounded-md">Ativa</span>
                    </div>
                    <span class="text-[11px] text-slate-500 block mb-2">Bairro Agostinho Neto</span>
                    <div class="space-y-1 text-[11px] pt-2 border-t border-slate-200 text-slate-600">
                        <div class="flex justify-between">
                            <span>Reunião Semanal:</span>
                            <b class="text-slate-800">Quintas • 17h00</b>
                        </div>
                        <div class="flex justify-between">
                            <span>Liderança:</span>
                            <b class="text-indigo-900">Líder de Célula</b>
                        </div>
                    </div>
                </div>

                <div class="p-4 bg-slate-50 rounded-xl border border-slate-200 hover:border-amber-400 transition">
                    <div class="flex items-center justify-between mb-1">
                        <span class="font-black text-slate-900 text-sm">Célula Manassés</span>
                        <span class="px-2 py-0.5 bg-amber-100 text-amber-800 text-[10px] font-bold rounded-md">Expansão</span>
                    </div>
                    <span class="text-[11px] text-slate-500 block mb-2">Bairro Dambo / Expansão</span>
                    <div class="space-y-1 text-[11px] pt-2 border-t border-slate-200 text-slate-600">
                        <div class="flex justify-between">
                            <span>Reunião Semanal:</span>
                            <b class="text-slate-800">Sábados • 16h00</b>
                        </div>
                        <div class="flex justify-between">
                            <span>Liderança:</span>
                            <b class="text-indigo-900">Núcleo em Crescimento</b>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- SEÇÃO 3: CORPO MINISTERIAL & ESTRUTURA DE OBREIROS -->
        <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 mb-6">
            <div class="flex items-center justify-between border-b border-slate-100 pb-4 mb-4">
                <div class="flex items-center gap-3">
                    <div class="p-2.5 bg-purple-50 text-purple-700 rounded-xl">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>
                    </div>
                    <div>
                        <h3 class="font-black text-sm text-slate-900 uppercase">Estatística do Corpo Ministerial & Liderança</h3>
                        <p class="text-xs text-slate-500">Obreiros consagrados, docência bíblica e departamentos oficiais</p>
                    </div>
                </div>
                <span class="text-xs font-bold text-slate-600 bg-slate-100 px-3 py-1 rounded-full">
                    Quadro Pastoral Ativo
                </span>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
                <div class="p-3.5 bg-slate-50 rounded-xl border border-slate-100 flex items-center justify-between">
                    <div>
                        <span class="font-bold text-slate-800 block text-xs">Pastor Dirigente</span>
                        <span class="text-[10px] text-slate-400">Liderança Espiritual</span>
                    </div>
                    <span class="px-2 py-1 bg-indigo-100 text-indigo-900 font-black rounded-lg text-[10px]">Ativo</span>
                </div>
                <div class="p-3.5 bg-slate-50 rounded-xl border border-slate-100 flex items-center justify-between">
                    <div>
                        <span class="font-bold text-slate-800 block text-xs">Diáconos & Diaconisas</span>
                        <span class="text-[10px] text-slate-400">Serviço & Assistência</span>
                    </div>
                    <span class="px-2 py-1 bg-slate-200 text-slate-800 font-bold rounded-lg text-[10px]">Consagrados</span>
                </div>
                <div class="p-3.5 bg-slate-50 rounded-xl border border-slate-100 flex items-center justify-between">
                    <div>
                        <span class="font-bold text-slate-800 block text-xs">Instrutores de Doutrina</span>
                        <span class="text-[10px] text-slate-400">Corpo Docente</span>
                    </div>
                    <span class="px-2 py-1 bg-amber-100 text-amber-900 font-bold rounded-lg text-[10px]">
                        {{ professores_cadastrados|length if professores_cadastrados is defined and professores_cadastrados else 1 }} Docente(s)
                    </span>
                </div>
                <div class="p-3.5 bg-slate-50 rounded-xl border border-slate-100 flex items-center justify-between">
                    <div>
                        <span class="font-bold text-slate-800 block text-xs">Líderes de Célula</span>
                        <span class="text-[10px] text-slate-400">Discipulado nos Lares</span>
                    </div>
                    <span class="px-2 py-1 bg-emerald-100 text-emerald-900 font-bold rounded-lg text-[10px]">6 Células</span>
                </div>
            </div>
        </div>
{% endif %}"""

# 3. SUBSTITUIR APENAS A ÁREA DO DASHBOARD DENTRO DE <main>
html_atualizado = html[:pos_dash_main] + novo_raiox_executivo + html[pos_dash_fim:]

# 4. VALIDAÇÃO RIGOROSA COM JINJA2 ANTES DE GRAVAR
env = jinja2.Environment()
try:
    env.parse(html_atualizado)
    print("✓ Validação Jinja2: APROVADO! O template tem ZERO erros de sintaxe.")
except Exception as e:
    print(f"Erro no Jinja2: {e}")
    exit(1)

with open(caminho_dash, 'w', encoding='utf-8') as f:
    f.write(html_atualizado)

print("✓ templates/dashboard.html regravado perfeitamente!")

# 5. COMMIT E PUSH DIRETO PARA O RENDER
print("=" * 80)
print("A ENVIAR ATUALIZAÇÃO PARA O GITHUB & RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "templates/dashboard.html"], check=True)
subprocess.run(["git", "commit", "-m", "Demografia ministerial: incluir membros por zona e rede de celulas com design executivo"], check=True)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("=" * 80)
print(">>> ATUALIZAÇÃO CONCLUÍDA COM TOTAL SUCESSO! <<<")
print("=" * 80)