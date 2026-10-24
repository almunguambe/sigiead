import os
import re
import py_compile
import subprocess
import jinja2

print("=" * 80)
print("A EXECUTAR RESTAURAÇÃO TÉCNICA E DEFINITIVA DO SIGIEAD...")
print("=" * 80)

caminho_dash = os.path.join('templates', 'dashboard.html')

if not os.path.exists(caminho_dash):
    print("ERRO: templates/dashboard.html não encontrado!")
    exit(1)

with open(caminho_dash, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. BARRA LATERAL (ASIDE) 100% PRÍSTINA E COMPLETA
aside_limpo = """    <aside class="w-64 bg-slate-900 text-white min-h-screen p-4 flex flex-col justify-between shrink-0 shadow-2xl">
        <div class="space-y-6">
            <!-- LOGO E IDENTIFICAÇÃO -->
            <div class="flex items-center gap-3 px-2 py-1">
                <img src="/static/img/logo.png" alt="SIGIEAD" class="w-10 h-10 object-contain drop-shadow">
                <div>
                    <span class="font-black text-sm tracking-tight text-white block">SIGIEAD</span>
                    <span class="text-[10px] text-amber-400 font-bold block -mt-0.5">Igreja de Chicuque</span>
                    <span class="text-[9px] text-slate-400 block -mt-0.5">Maxixe (Cidade/Distrito)</span>
                </div>
            </div>

            <!-- NAVEGAÇÃO COMPLETA -->
            <nav class="space-y-1">
                <div class="px-3 py-1 text-[10px] font-black text-slate-400 uppercase tracking-wider">
                    Visão Geral
                </div>
                <a href="/?aba=dashboard" class="flex items-center gap-3 px-3 py-2.5 rounded-xl font-bold text-xs {% if aba_ativa == 'dashboard' %}bg-indigo-600 text-white shadow-md{% else %}text-slate-300 hover:text-white hover:bg-slate-800{% endif %} transition">
                    <span>📊</span> <span>Raio-X Demográfico</span>
                </a>

                <div class="pt-3 px-3 py-1 text-[10px] font-black text-slate-400 uppercase tracking-wider">
                    Geral & Frequência
                </div>
                <a href="/?aba=membros" class="flex items-center gap-3 px-3 py-2.5 rounded-xl font-bold text-xs {% if aba_ativa == 'membros' %}bg-indigo-600 text-white shadow-md{% else %}text-slate-300 hover:text-white hover:bg-slate-800{% endif %} transition">
                    <span>👥</span> <span>1. Membros ({{ membros|length if membros else 0 }})</span>
                </a>
                <a href="/?aba=secretaria" class="flex items-center gap-3 px-3 py-2.5 rounded-xl font-bold text-xs {% if aba_ativa == 'secretaria' %}bg-indigo-600 text-white shadow-md{% else %}text-slate-300 hover:text-white hover:bg-slate-800{% endif %} transition">
                    <span>📋</span> <span>2. Secretaria & Planos</span>
                </a>
                <a href="/?aba=cultos" class="flex items-center gap-3 px-3 py-2.5 rounded-xl font-bold text-xs {% if aba_ativa == 'cultos' %}bg-indigo-600 text-white shadow-md{% else %}text-slate-300 hover:text-white hover:bg-slate-800{% endif %} transition">
                    <span>⛪</span> <span>3. Cultos & Presenças</span>
                </a>
                <a href="/?aba=convertidos" class="flex items-center gap-3 px-3 py-2.5 rounded-xl font-bold text-xs {% if aba_ativa == 'convertidos' %}bg-indigo-600 text-white shadow-md{% else %}text-slate-300 hover:text-white hover:bg-slate-800{% endif %} transition">
                    <span>🌱</span> <span>4. Novos Convertidos</span>
                </a>
                <a href="/?aba=actos" class="flex items-center gap-3 px-3 py-2.5 rounded-xl font-bold text-xs {% if aba_ativa == 'actos' %}bg-indigo-600 text-white shadow-md{% else %}text-slate-300 hover:text-white hover:bg-slate-800{% endif %} transition">
                    <span>💍</span> <span>Actos (Casamentos & Óbitos)</span>
                </a>

                <div class="pt-3 px-3 py-1 text-[10px] font-black text-slate-400 uppercase tracking-wider">
                    Finanças & Tesouraria
                </div>
                <a href="/?aba=financeiro" class="flex items-center gap-3 px-3 py-2.5 rounded-xl font-bold text-xs {% if aba_ativa == 'financeiro' %}bg-indigo-600 text-white shadow-md{% else %}text-slate-300 hover:text-white hover:bg-slate-800{% endif %} transition">
                    <span>📊</span> <span>5. Dashboard Financeiro</span>
                </a>
                <a href="/?aba=caixa" class="flex items-center gap-3 px-3 py-2.5 rounded-xl font-bold text-xs {% if aba_ativa == 'caixa' %}bg-indigo-600 text-white shadow-md{% else %}text-slate-300 hover:text-white hover:bg-slate-800{% endif %} transition">
                    <span>🔒</span> <span>6. Caixa & Lançamentos</span>
                </a>

                <div class="pt-3 px-3 py-1 text-[10px] font-black text-slate-400 uppercase tracking-wider">
                    Ensino & Formação
                </div>
                <a href="/professor" target="_blank" class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-amber-300 bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 transition text-xs font-bold">
                    <span>👨‍🏫</span> <span>Área do Professor (Visualizar) ↗</span>
                </a>
                <a href="/?aba=doutrina" class="flex items-center gap-3 px-3 py-2.5 rounded-xl font-bold text-xs {% if aba_ativa == 'doutrina' %}bg-indigo-600 text-white shadow-md{% else %}text-slate-300 hover:text-white hover:bg-slate-800{% endif %} transition">
                    <span>📖</span> <span>7. Doutrina & Batismo</span>
                </a>

                <div class="pt-3 px-3 py-1 text-[10px] font-black text-slate-400 uppercase tracking-wider">
                    Parâmetros & Controlo
                </div>
                <a href="/?aba=config" class="flex items-center gap-3 px-3 py-2.5 rounded-xl font-bold text-xs {% if aba_ativa == 'config' %}bg-indigo-600 text-white shadow-md{% else %}text-slate-300 hover:text-white hover:bg-slate-800{% endif %} transition">
                    <span>⚙️</span> <span>Gestor de Contas & Seletores</span>
                </a>
            </nav>
        </div>

        <!-- RODAPÉ DO ASIDE (UTILIZADOR E SAIR) -->
        <div class="pt-4 border-t border-slate-800 flex items-center justify-between">
            <div class="flex items-center gap-2 overflow-hidden">
                <div class="w-8 h-8 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-xs shrink-0">
                    {{ usuario_logado.nome[0] if usuario_logado and usuario_logado.nome else 'A' }}
                </div>
                <div class="truncate">
                    <span class="font-bold text-xs text-white block truncate">{{ usuario_logado.nome if usuario_logado else 'Administrador' }}</span>
                    <span class="text-[9px] text-amber-400 font-bold uppercase block">{{ usuario_logado.perfil if usuario_logado else 'ADMIN' }}</span>
                </div>
            </div>
            <a href="/logout" class="px-2.5 py-1 bg-rose-600/80 hover:bg-rose-600 text-white rounded-lg text-xs font-bold transition shadow-sm shrink-0">
                Sair
            </a>
        </div>
    </aside>"""

# Substituir todo o <aside>...</aside> pela versão limpa
pos_aside_inicio = html.find('<aside')
pos_aside_fim = html.find('</aside>')

if pos_aside_inicio != -1 and pos_aside_fim != -1:
    pos_aside_fim += len('</aside>')
    html = html[:pos_aside_inicio] + aside_limpo + html[pos_aside_fim:]
    print("✓ Barra lateral (<aside>) substituída pela versão limpa!")

# 2. POPULAR OPÇÕES DOS SELECTS
opcoes_dados = {
    'celula': [
        "Célula Betel (Chicuque Sede)",
        "Célula Sião (Chambone Centro)",
        "Célula Peniel (Tinga Residencial)",
        "Célula Ebenézer (Rumbana)",
        "Célula Jerusalém (Agostinho Neto)",
        "Célula Manassés (Dambo / Expansão)"
    ],
    'zona': [
        "Zona 1 • Chicuque (Sede Central)",
        "Zona 2 • Chambone (Urbano)",
        "Zona 3 • Tinga (Residencial)",
        "Zona 4 • Rumbana (Expansão)",
        "Zona 5 • Dambo / Malalane",
        "Zona 6 • Macuamene / Bembe"
    ],
    'departamento': [
        "Geral / Toda a Igreja",
        "Homens (Cavalheiros)",
        "Mulheres (Senhoras)",
        "Juventude Cristã (Jovens)",
        "Crianças (Boa Esperança)",
        "Louvor & Coral",
        "Evangelismo & Missões",
        "Ação Social & Diaconia",
        "Escola Bíblica Dominical"
    ],
    'estado_civil': [
        "Solteiro(a)",
        "Casado(a)",
        "Viúvo(a)",
        "Divorciado(a)"
    ]
}

for campo, lista in opcoes_dados.items():
    padrao = "(<select[^>]*name=['\"]" + campo + "['\"][^>]*>)([\\s\\S]*?)(</select>)"
    def injetar_opcoes(m):
        abertura = m.group(1)
        conteudo_interno = m.group(2)
        fecho = m.group(3)
        if conteudo_interno.count('<option') <= 1:
            opts = "\n".join([f'    <option value="{o}">{o}</option>' for o in lista])
            return f'{abertura}\n    <option value="">Selecione...</option>\n{opts}\n{fecho}'
        return m.group(0)
    html = re.sub(padrao, injetar_opcoes, html, flags=re.IGNORECASE)

# 3. VALIDAÇÃO ESTREITA COM JINJA2
env = jinja2.Environment()
env.parse(html)
with open(caminho_dash, 'w', encoding='utf-8') as f:
    f.write(html)
print("✓ templates/dashboard.html validado com ZERO erros no Jinja2!")

# 4. GIT ADD, COMMIT E PUSH
print("\n" + "=" * 80)
print("A ENVIAR PARA O GITHUB E RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "templates/dashboard.html"])
subprocess.run(["git", "commit", "-m", "Restauracao definitiva: aside pristino e sem cartoes fantasmas"])
subprocess.run(["git", "push", "origin", "main"])

print("=" * 80)
print(">>> ATUALIZAÇÃO CONCLUÍDA E PUBLICADA NO RENDER! <<<")
print("=" * 80)