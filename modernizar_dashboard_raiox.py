import os
import re
import shutil
import subprocess
import jinja2

print("=" * 80)
print("A MODERNIZAR O RAIO-X DEMOGRÁFICO COM DESIGN EXECUTIVO PROFISSIONAL...")
print("=" * 80)

caminho_dash = os.path.join('templates', 'dashboard.html')

# 1. CRIAR BACKUP DE SEGURANÇA LOCAL
shutil.copyfile(caminho_dash, caminho_dash + ".bak")
print("✓ Backup de segurança criado: templates/dashboard.html.bak")

with open(caminho_dash, 'r', encoding='utf-8') as f:
    conteudo = f.read()

# 2. NOVO RAIO-X EXECUTIVO: ELEGANTE, PROFISSIONAL E MODERNO
novo_raiox_executivo = """{% if aba_ativa == 'dashboard' %}
        <!-- CABEÇALHO DO RAIO-X EM ESTILO EXECUTIVO -->
        <div class="w-full bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white p-6 rounded-3xl shadow-xl mb-6 flex flex-col md:flex-row md:items-center justify-between gap-5 border border-slate-800">
            <div class="flex items-center gap-4">
                <div class="w-14 h-14 rounded-2xl bg-gradient-to-tr from-indigo-600 to-indigo-400 p-0.5 shadow-lg flex items-center justify-center shrink-0">
                    <div class="w-full h-full bg-slate-900 rounded-[14px] flex items-center justify-center">
                        <svg class="w-7 h-7 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                        </svg>
                    </div>
                </div>
                <div>
                    <div class="inline-flex items-center gap-2 bg-indigo-500/20 text-indigo-300 px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider mb-1.5 border border-indigo-400/30">
                        <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span> CENSO ECLESIÁSTICO & DEMOGRAFIA INTEGRAL
                    </div>
                    <h2 class="text-2xl font-black tracking-tight text-white">Raio-X Ministerial: Igreja de Chicuque</h2>
                    <p class="text-xs text-slate-300">Panorama demográfico de fiéis, faixas etárias e situação eclesiástica em Maxixe</p>
                </div>
            </div>
            
            <div class="bg-white/5 backdrop-blur-md px-5 py-3.5 rounded-2xl border border-white/10 flex items-center gap-4 shrink-0">
                <div>
                    <span class="text-[10px] uppercase font-bold text-slate-400 block tracking-wider">Total de Almas no Rebanho</span>
                    <div class="flex items-baseline gap-2">
                        <span class="text-3xl font-black text-amber-400">{{ (total_membros|default(0)) + (doutrina|length|default(0)) }}</span>
                        <span class="text-xs text-slate-300 font-semibold">Vidas</span>
                    </div>
                    <span class="text-[10px] text-slate-400 block mt-0.5">{{ total_membros|default(0) }} Membros • {{ doutrina|length|default(0) }} em Formação</span>
                </div>
            </div>
        </div>

        <!-- 4 CARDS ANALÍTICOS EXECUTIVOS -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            
            <!-- CARD 1: DISTRIBUIÇÃO POR GÉNERO -->
            <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 hover:shadow-md transition-all duration-200 flex flex-col justify-between">
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
            <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 hover:shadow-md transition-all duration-200 flex flex-col justify-between">
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
            <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 hover:shadow-md transition-all duration-200 flex flex-col justify-between">
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
                            <span class="font-black text-amber-900">{{ doutrina|length|default(0) }}</span>
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
            <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 hover:shadow-md transition-all duration-200 flex flex-col justify-between">
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

        <!-- PAINEL INFERIOR: CARTOGRAFIA E CORPO MINISTERIAL -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            
            <!-- CARTOGRAFIA MINISTERIAL -->
            <div class="lg:col-span-7 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <div class="flex items-center justify-between border-b border-slate-100 pb-4 mb-4">
                    <div class="flex items-center gap-3">
                        <div class="p-2.5 bg-indigo-50 text-indigo-700 rounded-xl">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                        </div>
                        <div>
                            <h3 class="font-black text-sm text-slate-900 uppercase">Cartografia Ministerial & Células</h3>
                            <p class="text-xs text-slate-500">Distribuição por zonas geográficas e núcleos de oração</p>
                        </div>
                    </div>
                    <span class="text-xs font-bold text-indigo-700 bg-indigo-50 px-3 py-1 rounded-full border border-indigo-100">
                        Maxixe • Inhambane
                    </span>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                    <div class="p-3.5 bg-slate-50 rounded-xl border border-slate-200">
                        <div class="flex items-center justify-between mb-1">
                            <span class="text-[10px] font-bold text-slate-500 uppercase">Zona Principal</span>
                            <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
                        </div>
                        <span class="font-black text-slate-900 block text-sm">Chicuque Sede</span>
                        <span class="text-[10px] text-slate-400 mt-1 block">Templo Central</span>
                    </div>

                    <div class="p-3.5 bg-slate-50 rounded-xl border border-slate-200">
                        <div class="flex items-center justify-between mb-1">
                            <span class="text-[10px] font-bold text-slate-500 uppercase">Células nos Lares</span>
                            <span class="w-2 h-2 rounded-full bg-blue-500"></span>
                        </div>
                        <span class="font-black text-slate-900 block text-sm">Núcleos Activos</span>
                        <span class="text-[10px] text-slate-400 mt-1 block">Reuniões nos Bairros</span>
                    </div>

                    <div class="p-3.5 bg-slate-50 rounded-xl border border-slate-200">
                        <div class="flex items-center justify-between mb-1">
                            <span class="text-[10px] font-bold text-slate-500 uppercase">Expansão</span>
                            <span class="w-2 h-2 rounded-full bg-amber-500"></span>
                        </div>
                        <span class="font-black text-slate-900 block text-sm">Evangelização</span>
                        <span class="text-[10px] text-slate-400 mt-1 block">Pontos de Pregação</span>
                    </div>
                </div>
            </div>

            <!-- ESTATÍSTICA DO CORPO MINISTERIAL & OBREIROS -->
            <div class="lg:col-span-5 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <div class="flex items-center justify-between border-b border-slate-100 pb-4 mb-4">
                    <div class="flex items-center gap-3">
                        <div class="p-2.5 bg-amber-50 text-amber-700 rounded-xl">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>
                        </div>
                        <div>
                            <h3 class="font-black text-sm text-slate-900 uppercase">Corpo Ministerial</h3>
                            <p class="text-xs text-slate-500">Liderança e obreiros consagrados</p>
                        </div>
                    </div>
                    <span class="text-xs font-bold text-slate-600 bg-slate-100 px-2.5 py-1 rounded-full">
                        Quadro Ativo
                    </span>
                </div>

                <div class="space-y-2 text-xs">
                    <div class="flex justify-between items-center p-2.5 bg-slate-50 rounded-xl border border-slate-100">
                        <span class="font-bold text-slate-800">Pastor Dirigente & Auxiliares</span>
                        <span class="px-2 py-0.5 bg-indigo-100 text-indigo-900 font-black rounded-lg text-[10px]">Ativo</span>
                    </div>
                    <div class="flex justify-between items-center p-2.5 bg-slate-50 rounded-xl border border-slate-100">
                        <span class="font-bold text-slate-800">Diáconos & Diaconisas</span>
                        <span class="px-2 py-0.5 bg-slate-200 text-slate-800 font-bold rounded-lg text-[10px]">Ordem Eclesiástica</span>
                    </div>
                    <div class="flex justify-between items-center p-2.5 bg-slate-50 rounded-xl border border-slate-100">
                        <span class="font-bold text-slate-800">Instrutores de Doutrina</span>
                        <span class="px-2 py-0.5 bg-amber-100 text-amber-900 font-bold rounded-lg text-[10px]">Docência</span>
                    </div>
                </div>
            </div>

        </div>
{% endif %}"""

# 3. LOCALIZADOR BALANCED DE BLOCO JINJA2 (SUBSTITUI APENAS A ABA DASHBOARD)
def encontrar_bloco(texto, nome_aba):
    padrao = rf"{{%\s*if\s+aba_ativa\s*==\s*['\"]{nome_aba}['\"]\s*%}}"
    m = re.search(padrao, texto)
    if not m:
        return None, None
    ini = m.start()
    pos = m.end()
    contador = 1
    tag_pat = re.compile(r"{%\s*(if\b|endif\b)")
    for match in tag_pat.finditer(texto, pos):
        t = match.group(1)
        if t.startswith('if'):
            contador += 1
        elif t == 'endif':
            contador -= 1
            if contador == 0:
                fim = texto.find('%}', match.start()) + 2
                return ini, fim
    return None, None

ini_dash, fim_dash = encontrar_bloco(conteudo, 'dashboard')
if ini_dash is not None:
    conteudo_atualizado = conteudo[:ini_dash] + novo_raiox_executivo + conteudo[fim_dash:]
    print("✓ Bloco do Raio-X localizado e substituído com isolamento absoluto!")
else:
    print("Erro: Bloco de dashboard não encontrado.")
    exit(1)

# 4. VALIDAÇÃO RIGOROSA NO PARSER JINJA2 (ZERO ERROS ANTES DE GRAVAR)
env = jinja2.Environment()
try:
    env.parse(conteudo_atualizado)
    print("✓ Validação Jinja2: APROVADO COM ZERO ERROS DE SINTAXE!")
except Exception as e:
    print(f"Erro na validação do Jinja2: {e}")
    exit(1)

with open(caminho_dash, 'w', encoding='utf-8') as f:
    f.write(conteudo_atualizado)
print("✓ templates/dashboard.html regravado com sucesso!")

# 5. COMMIT E PUSH PARA O RENDER
print("=" * 80)
print("A ENVIAR ATUALIZAÇÃO PARA O GITHUB & RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "templates/dashboard.html"], check=True)
subprocess.run(["git", "commit", "-m", "Design executivo: modernizar Raio-X com graficos SVG e estetica enterprise"], check=True)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("=" * 80)
print(">>> ATUALIZAÇÃO EXECUTIVA CONCLUÍDA COM SUCESSO TOTAL! <<<")
print("=" * 80)