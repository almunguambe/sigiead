import os
import re
import py_compile
import jinja2

print("=" * 80)
print("A RESTAURAR A ESTRUTURA DO DASHBOARD: BARRA LATERAL + TELA CHEIA...")
print("=" * 80)

caminho_dash = os.path.join('templates', 'dashboard.html')
with open(caminho_dash, 'r', encoding='utf-8') as f:
    html_atual = f.read()

# Backup de segurança antes de qualquer alteração
with open(os.path.join('templates', 'dashboard_backup_estrutural.html'), 'w', encoding='utf-8') as f:
    f.write(html_atual)

# 1. RECUPERAR CONTEÚDO DAS OUTRAS ABAS (MEMBROS, CULTOS, SECRETARIA, FINANCAS, CONFIG)
def extrair_aba(nome, html):
    padrao = rf'({{% if aba_ativa == [\'"]{nome}[\'"] %}}[\s\S]*?)(?={{{{%\s*if\s+aba_ativa|{{{{%\s*endif\s*%}}|$)'
    m = re.search(padrao, html)
    if m:
        bloco = m.group(1).strip()
        if not bloco.endswith('{% endif %}'):
            bloco += '\n{% endif %}'
        return bloco
    return ""

aba_dash = extrair_aba('dashboard', html_atual)
aba_membros = extrair_aba('membros', html_atual)
aba_secretaria = extrair_aba('secretaria', html_atual)
aba_cultos = extrair_aba('cultos', html_atual)
aba_convertidos = extrair_aba('convertidos', html_atual)
aba_actos = extrair_aba('actos', html_atual)
aba_financas = extrair_aba('financas', html_atual)
aba_tesouraria = extrair_aba('tesouraria', html_atual)
aba_config = extrair_aba('configuracoes', html_atual) or extrair_aba('config', html_atual)

# 2. DEFINIR O NOVO BLOCO DE DOUTRINA EM TELA CHEIA (WIDESCREEN & RESPONSIVO)
bloco_doutrina_perfeito = """{% if aba_ativa == 'doutrina' %}
        <!-- CABEÇALHO DO MÓDULO PEDAGÓGICO (LARGURA TOTAL) -->
        <div class="w-full bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white p-6 rounded-3xl shadow-xl mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
                <div class="inline-flex items-center gap-2 bg-amber-500/20 text-amber-300 px-3 py-1 rounded-full text-[10px] font-black uppercase mb-1 border border-amber-400/30">
                    <span>📖</span> ESCOLA MINISTERIAL & DOUTRINA BÍBLICA
                </div>
                <h2 class="text-2xl font-black">Situação Geral de Ensino, Formandos & Instrutores</h2>
                <p class="text-xs text-indigo-200 mt-0.5">Acompanhamento curricular, aprovação para Batismo nas Águas e credenciamento docente</p>
            </div>
            <div class="flex gap-2">
                <a href="/ensino/aulas" target="_blank" class="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl text-xs shadow flex items-center gap-1.5 transition">
                    <span>🎓</span><span>Abrir Sala de Aula do Aluno ↗</span>
                </a>
            </div>
        </div>

        <!-- 4 CARDS ESTATÍSTICOS (EXPANDIDOS EM 4 COLUNAS NA TELA) -->
        <div class="w-full grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6 text-xs">
            <div class="bg-white p-5 rounded-2xl shadow-sm border-l-4 border-indigo-600 border-slate-200">
                <span class="text-slate-500 text-[10px] font-bold uppercase block">Total de Formandos</span>
                <span class="text-2xl font-black text-indigo-950 mt-1 block">{{ stats_ensino.total_alunos if stats_ensino else doutrina|length }} Alunos</span>
                <span class="text-[10px] text-slate-400">Inscritos no currículo oficial</span>
            </div>
            <div class="bg-white p-5 rounded-2xl shadow-sm border-l-4 border-emerald-500 border-slate-200">
                <span class="text-slate-500 text-[10px] font-bold uppercase block">Aptos / Prontos para Batismo</span>
                <span class="text-2xl font-black text-emerald-700 mt-1 block">🌊 {{ stats_ensino.aptos if stats_ensino else 0 }} Prontos</span>
                <span class="text-[10px] text-emerald-600 font-bold">Aproveitamento >= 70%</span>
            </div>
            <div class="bg-white p-5 rounded-2xl shadow-sm border-l-4 border-amber-500 border-slate-200">
                <span class="text-slate-500 text-[10px] font-bold uppercase block">Em Formação Ativa</span>
                <span class="text-2xl font-black text-amber-700 mt-1 block">📖 {{ stats_ensino.em_formacao if stats_ensino else 0 }} Alunos</span>
                <span class="text-[10px] text-slate-400">Em estudo nas classes</span>
            </div>
            <div class="bg-white p-5 rounded-2xl shadow-sm border-l-4 border-blue-500 border-slate-200">
                <span class="text-slate-500 text-[10px] font-bold uppercase block">Corpo Docente</span>
                <span class="text-2xl font-black text-blue-900 mt-1 block">👨‍🏫 {{ professores_cadastrados|length if professores_cadastrados else 0 }} Instrutor(es)</span>
                <span class="text-[10px] text-slate-400">Com credencial de ensino</span>
            </div>
        </div>

        <!-- BARRA DE CLASSES EM FUNCIONAMENTO -->
        <div class="w-full bg-white p-4.5 rounded-2xl shadow-sm border border-slate-200 text-xs flex flex-wrap items-center justify-between gap-3 mb-6">
            <span class="font-extrabold text-slate-700 uppercase text-[11px]">Classes em Funcionamento:</span>
            <div class="flex flex-wrap gap-2">
                {% if lista_classes %}
                    {% for cl in lista_classes %}
                    <span class="px-3 py-1 bg-slate-100 text-slate-800 rounded-lg font-bold text-[11px] border border-slate-200">
                        {{ cl }}
                    </span>
                    {% endfor %}
                {% else %}
                    <span class="px-3 py-1 bg-slate-100 text-slate-800 rounded-lg font-bold text-[11px]">Preparação para Batismo nas Águas</span>
                    <span class="px-3 py-1 bg-slate-100 text-slate-800 rounded-lg font-bold text-[11px]">Discipulado de Novos Convertidos</span>
                {% endif %}
            </div>
        </div>

        <!-- GABINETE DO INSTRUTOR (DÚVIDAS BÍBLICAS PENDENTES) -->
        <div class="w-full bg-white p-6 rounded-2xl shadow-sm border border-slate-200 mb-6 space-y-3">
            <div class="flex justify-between items-center border-b pb-3">
                <div class="flex items-center gap-2">
                    <span class="text-xl">👨‍🏫</span>
                    <div>
                        <h3 class="font-black text-sm text-slate-900 uppercase">Gabinete do Instrutor: Dúvidas Bíblicas dos Formandos</h3>
                        <p class="text-xs text-slate-500">Responda diretamente às perguntas bíblicas enviadas pelos alunos na sala de aula.</p>
                    </div>
                </div>
                <span class="bg-amber-100 text-amber-900 px-3 py-1 rounded-full text-xs font-black">
                    {{ duvidas_pendentes|length if duvidas_pendentes else 0 }} Pendente(s)
                </span>
            </div>

            <div class="space-y-3 pt-1">
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
                        <input type="text" name="resposta" required placeholder="Escreva a resposta bíblica e conselho pastoral para o aluno..." class="flex-1 h-10 px-3 border-2 border-slate-300 rounded-xl bg-white text-xs focus:border-indigo-600 focus:outline-none">
                        <button type="submit" class="px-4 h-10 bg-indigo-900 hover:bg-indigo-950 text-white font-bold rounded-xl text-xs shadow cursor-pointer">
                            Enviar Resposta →
                        </button>
                    </form>
                </div>
                {% else %}
                <p class="text-xs text-slate-400 italic text-center py-2">Glória a Deus! Nenhuma dúvida bíblica pendente no momento.</p>
                {% endfor %}
            </div>
        </div>

        <!-- ÁREA DE CADASTROS: ALUNOS & PROFESSORES (LADO A LADO) -->
        <div class="w-full grid grid-cols-1 lg:grid-cols-12 gap-6 mb-6">

            <!-- FORMULÁRIO 1: INSCREVER FORMANDO -->
            <div class="lg:col-span-7 bg-white p-6 rounded-2xl shadow-sm border border-slate-200 space-y-4">
                <div class="border-b pb-3">
                    <h3 class="font-black text-sm text-slate-900 uppercase flex items-center gap-2">
                        <span>🎓</span> 1. Inscrever Formando com Login
                    </h3>
                    <p class="text-[11px] text-slate-500">Gera credenciais automáticas para o aluno aceder no telemóvel</p>
                </div>

                <form action="/doutrina/gravar" method="POST" class="space-y-3 text-xs">
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">Nome Completo do Aluno *</label>
                        <input type="text" name="nome_aluno" required placeholder="Ex: Jacinto Manuel Bata Saranga" class="w-full h-11 px-3 border border-slate-300 rounded-xl focus:border-indigo-600 focus:outline-none">
                    </div>

                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        <div class="min-w-0">
                            <label class="block font-bold text-slate-700 mb-1">Classe *</label>
                            <select name="classe" required class="w-full h-11 px-3 border border-slate-300 rounded-xl bg-white font-bold text-xs text-slate-800 focus:border-indigo-600 focus:outline-none shadow-sm cursor-pointer truncate">
                                {% if lista_classes %}
                                    {% for cl in lista_classes %}
                                    <option value="{{ cl }}">{{ cl }}</option>
                                    {% endfor %}
                                {% else %}
                                    <option value="Preparação para Batismo nas Águas">Preparação para Batismo nas Águas</option>
                                    <option value="Discipulado de Novos Convertidos">Discipulado de Novos Convertidos</option>
                                {% endif %}
                            </select>
                        </div>
                        <div class="min-w-0">
                            <label class="block font-bold text-slate-700 mb-1">Instrutor / Mentor *</label>
                            <select name="professor" required class="w-full h-11 px-3 border border-slate-300 rounded-xl bg-white font-bold text-xs text-slate-800 focus:border-indigo-600 focus:outline-none shadow-sm cursor-pointer truncate">
                                {% if lista_professores %}
                                    {% for prof in lista_professores %}
                                    <option value="{{ prof }}">{{ prof }}</option>
                                    {% endfor %}
                                {% else %}
                                    <option value="Anselmo Leonardo Munguambe">Anselmo Leonardo Munguambe</option>
                                    <option value="Pastor Dirigente">Pastor Dirigente</option>
                                {% endif %}
                            </select>
                        </div>
                    </div>

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
                    <p class="text-[11px] text-slate-500">Credencia um docente com login restrito ao ensino</p>
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
                        ℹ️ <b>Privacidade garantida:</b> O professor apenas acede ao acompanhamento dos alunos e às dúvidas bíblicas, sem visualização financeira.
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
                    <span class="text-xs text-indigo-900 font-bold">{{ professores_cadastrados|length if professores_cadastrados else 0 }}</span>
                </div>

                <div class="space-y-2.5 text-xs">
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
                    {% else %}
                    <p class="text-slate-400 italic text-center py-4">Nenhum professor cadastrado ainda.</p>
                    {% endfor %}
                </div>
            </div>

        </div>
{% endif %}"""

# 3. CONSTRUIR O HTML COMPLETO COM ESTRUTURA LIMPA (SIDEBAR + MAIN)
html_limpo = f"""<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SIGIEAD - Painel de Gestão</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#1e1b4b">
    <meta name="mobile-web-app-capable" content="yes">
    <link rel="apple-touch-icon" href="/static/img/logo.png">
</head>
<body class="bg-slate-100 text-slate-800 font-sans antialiased min-h-screen flex flex-col md:flex-row">

    <!-- BARRA LATERAL (SIDEBAR COM LARGURA FIXA E BEM FECHADA) -->
    <aside class="w-full md:w-64 bg-slate-900 text-white min-h-screen p-4 flex flex-col justify-between shrink-0 shadow-2xl">
        <div>
            <!-- LOGO / IDENTIDADE -->
            <div class="flex items-center gap-3 px-2 py-3 mb-4 border-b border-slate-800">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 to-indigo-600 flex items-center justify-center text-white text-lg font-black shadow-lg">
                    ✝
                </div>
                <div>
                    <h1 class="text-sm font-black tracking-wider text-white">SIGIEAD</h1>
                    <p class="text-[10px] text-indigo-300 font-semibold truncate">Assembleia de Deus</p>
                </div>
            </div>

            <!-- LINKS DO MENU -->
            <nav class="space-y-1.5 text-xs font-semibold">
                {{% if usuario_logado and usuario_logado.perfil != 'professor' %}}
                <a href="/?aba=dashboard" class="flex items-center gap-3 px-3 py-2 rounded-xl transition {{% if aba_ativa == 'dashboard' %}}bg-indigo-600 text-white shadow-md{{% else %}}text-slate-300 hover:bg-slate-800{{% endif %}}">
                    <span>📊</span><span>Raio-X Demográfico</span>
                </a>

                <div class="pt-3 pb-1 px-3 text-[10px] uppercase font-bold text-slate-500 tracking-wider">Geral & Frequência</div>
                
                <a href="/?aba=membros" class="flex items-center gap-3 px-3 py-2 rounded-xl transition {{% if aba_ativa == 'membros' %}}bg-indigo-600 text-white shadow-md{{% else %}}text-slate-300 hover:bg-slate-800{{% endif %}}">
                    <span>👥</span><span>1. Membros ({{{{ total_membros if total_membros is defined else 0 }}}})</span>
                </a>
                <a href="/?aba=secretaria" class="flex items-center gap-3 px-3 py-2 rounded-xl transition {{% if aba_ativa == 'secretaria' %}}bg-indigo-600 text-white shadow-md{{% else %}}text-slate-300 hover:bg-slate-800{{% endif %}}">
                    <span>📋</span><span>2. Secretaria & Planos</span>
                </a>
                <a href="/?aba=cultos" class="flex items-center gap-3 px-3 py-2 rounded-xl transition {{% if aba_ativa == 'cultos' %}}bg-indigo-600 text-white shadow-md{{% else %}}text-slate-300 hover:bg-slate-800{{% endif %}}">
                    <span>⛪</span><span>3. Cultos & Presenças</span>
                </a>
                <a href="/?aba=convertidos" class="flex items-center gap-3 px-3 py-2 rounded-xl transition {{% if aba_ativa == 'convertidos' %}}bg-indigo-600 text-white shadow-md{{% else %}}text-slate-300 hover:bg-slate-800{{% endif %}}">
                    <span>🌱</span><span>4. Novos Convertidos</span>
                </a>
                <a href="/?aba=actos" class="flex items-center gap-3 px-3 py-2 rounded-xl transition {{% if aba_ativa == 'actos' %}}bg-indigo-600 text-white shadow-md{{% else %}}text-slate-300 hover:bg-slate-800{{% endif %}}">
                    <span>💍</span><span>Actos (Casamentos & Óbitos)</span>
                </a>
                {{% endif %}}

                <div class="pt-3 pb-1 px-3 text-[10px] uppercase font-bold text-slate-500 tracking-wider">Ensino & Formação</div>

                <a href="/?aba=doutrina" class="flex items-center gap-3 px-3 py-2 rounded-xl transition {{% if aba_ativa == 'doutrina' %}}bg-amber-600 text-white shadow-md font-bold{{% else %}}text-slate-300 hover:bg-slate-800{{% endif %}}">
                    <span>📖</span><span>7. Doutrina & Batismo</span>
                </a>
                <a href="/ensino/aulas" target="_blank" class="flex items-center gap-3 px-3 py-2 rounded-xl text-blue-300 hover:bg-slate-800 transition">
                    <span>🎓</span><span>Sala de Aula (Aluno) ↗</span>
                </a>

                {{% if usuario_logado and usuario_logado.perfil not in ['secretario', 'professor'] %}}
                <div class="pt-3 pb-1 px-3 text-[10px] uppercase font-bold text-slate-500 tracking-wider">Finanças & Tesouraria</div>
                <a href="/?aba=financas" class="flex items-center gap-3 px-3 py-2 rounded-xl transition {{% if aba_ativa == 'financas' %}}bg-indigo-600 text-white shadow-md{{% else %}}text-slate-300 hover:bg-slate-800{{% endif %}}">
                    <span>📊</span><span>5. Dashboard Financeiro</span>
                </a>
                <a href="/?aba=tesouraria" class="flex items-center gap-3 px-3 py-2 rounded-xl transition {{% if aba_ativa == 'tesouraria' %}}bg-indigo-600 text-white shadow-md{{% else %}}text-slate-300 hover:bg-slate-800{{% endif %}}">
                    <span>🔒</span><span>6. Caixa & Lançamentos</span>
                </a>
                {{% endif %}}

                {{% if usuario_logado and usuario_logado.perfil in ['admin', 'pastor'] %}}
                <div class="pt-3 pb-1 px-3 text-[10px] uppercase font-bold text-slate-500 tracking-wider">Parâmetros & Controlo</div>
                <a href="/?aba=configuracoes" class="flex items-center gap-3 px-3 py-2 rounded-xl transition {{% if aba_ativa == 'configuracoes' %}}bg-indigo-600 text-white shadow-md{{% else %}}text-slate-300 hover:bg-slate-800{{% endif %}}">
                    <span>⚙️</span><span>Gestor de Contas & Seletores</span>
                </a>
                {{% endif %}}
            </nav>
        </div>

        <!-- RODAPÉ DA SIDEBAR: USUÁRIO E LOGOUT -->
        <div class="pt-4 border-t border-slate-800 flex items-center justify-between">
            <div class="truncate mr-2">
                <span class="block text-xs font-bold text-white truncate">{{{{ usuario_logado.nome if usuario_logado else 'Utilizador' }}}}</span>
                <span class="block text-[10px] text-amber-400 font-extrabold uppercase">{{{{ usuario_logado.perfil if usuario_logado else 'ACESSO' }}}}</span>
            </div>
            <a href="/logout" class="px-3 py-1.5 bg-rose-600 hover:bg-rose-700 text-white rounded-lg text-xs font-bold transition shrink-0">
                Sair
            </a>
        </div>
    </aside>

    <!-- ÁREA DE CONTEÚDO PRINCIPAL (OCUPA 100% DO RESTO DA TELA) -->
    <main class="flex-1 p-4 md:p-8 bg-slate-100 min-h-screen overflow-y-auto w-full">
        {aba_dash}
        {aba_membros}
        {aba_secretaria}
        {aba_cultos}
        {aba_convertidos}
        {aba_actos}
        {aba_financas}
        {aba_tesouraria}
        {bloco_doutrina_perfeito}
        {aba_config}
    </main>

</body>
</html>
"""

# 4. VALIDAR TEMPLATE COM O PARSER DO JINJA2
env = jinja2.Environment()
env.parse(html_limpo)

with open(caminho_dash, 'w', encoding='utf-8') as f:
    f.write(html_limpo)

print("✓ templates/dashboard.html totalmente reconstruído e validado com sucesso!")
print("=" * 80)
print(">>> LAYOUT REPARADO COM SUCESSO! FAÇA O COMMIT E PUSH! <<<")
print("=" * 80)