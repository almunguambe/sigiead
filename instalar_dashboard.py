import os

print("=" * 70)
print("A INSTALAR O NOVO PAINEL LIMPO (TEMPLATES/DASHBOARD.HTML)...")
print("=" * 70)

os.makedirs('templates', exist_ok=True)

html_conteudo = """<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IEAD Chicuque - Gestão Eclesiástica Integrada</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.getRegistrations().then(function(regs) {
                for (let r of regs) r.unregister();
            });
        }
    </script>
</head>
<body class="bg-slate-100 text-slate-800 font-sans min-h-screen flex">

    <!-- BARRA LATERAL (MENU) -->
    <aside class="w-64 bg-slate-900 text-white flex flex-col justify-between min-h-screen shrink-0 shadow-xl">
        <div>
            <div class="p-5 border-b border-slate-800 flex items-center gap-3">
                <div class="w-11 h-11 rounded-full bg-white text-slate-900 flex items-center justify-center font-black text-lg shrink-0 shadow">
                    AD
                </div>
                <div>
                    <h1 class="font-extrabold text-sm tracking-wide leading-tight">ASSEMBLEIA<br>DE DEUS</h1>
                    <p class="text-[11px] text-blue-300 mt-0.5">Sede Chicuque • Gestão 360°</p>
                </div>
            </div>

            <nav class="p-3 space-y-1.5 text-xs font-semibold">
                <div class="px-3 py-2 text-[10px] font-bold uppercase tracking-wider text-slate-400">
                    Geral & Frequência
                </div>

                <a href="/?aba=membros" class="flex items-center gap-3 px-3.5 py-3 rounded-xl transition {% if aba_ativa == 'membros' %}bg-indigo-600 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                    <span>👥</span>
                    <span>1. Membros ({{ membros|length }})</span>
                </a>

                <a href="/?aba=secretaria" class="flex items-center gap-3 px-3.5 py-3 rounded-xl transition {% if aba_ativa == 'secretaria' %}bg-indigo-600 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                    <span>📋</span>
                    <span>2. Secretaria & Planos</span>
                </a>

                <a href="/?aba=cultos" class="flex items-center gap-3 px-3.5 py-3 rounded-xl transition {% if aba_ativa == 'cultos' %}bg-indigo-600 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                    <span>⛪</span>
                    <span>3. Cultos & Presenças</span>
                </a>

                <a href="/?aba=convertidos" class="flex items-center gap-3 px-3.5 py-3 rounded-xl transition {% if aba_ativa == 'convertidos' %}bg-indigo-600 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                    <span>🌱</span>
                    <span>4. Novos Convertidos</span>
                </a>

                <div class="px-3 pt-4 pb-1 text-[10px] font-bold uppercase tracking-wider text-emerald-400">
                    Finanças & Tesouraria
                </div>

                <a href="/?aba=financas" class="flex items-center gap-3 px-3.5 py-3 rounded-xl transition {% if aba_ativa == 'financas' %}bg-indigo-600 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                    <span>💰</span>
                    <span>5. Movimentos de Caixa</span>
                </a>

                <div class="px-3 pt-4 pb-1 text-[10px] font-bold uppercase tracking-wider text-amber-400">
                    Doutrina & Batismo
                </div>

                <a href="/?aba=doutrina" class="flex items-center gap-3 px-3.5 py-3 rounded-xl transition {% if aba_ativa == 'doutrina' %}bg-indigo-600 text-white shadow-md{% else %}text-slate-300 hover:bg-slate-800{% endif %}">
                    <span>📖</span>
                    <span>6. Doutrina & Candidatos</span>
                </a>
            </nav>
        </div>

        <div class="p-4 border-t border-slate-800 text-xs text-slate-400 flex items-center justify-between">
            <div>
                <p class="font-bold text-white">admin</p>
                <p class="text-[11px] text-amber-400">Pastor / Administração</p>
            </div>
            <span class="w-2.5 h-2.5 rounded-full bg-emerald-400" title="Sistema Operacional"></span>
        </div>
    </aside>

    <!-- CONTEÚDO PRINCIPAL (RENDERIZAÇÃO DIRETA SEM JAVASCRIPT COMPLEXO) -->
    <main class="flex-1 p-6 overflow-y-auto">

        <!-- 1. MEMBROS -->
        {% if aba_ativa == 'membros' %}
        <div class="bg-indigo-900 text-white p-5 rounded-2xl shadow mb-6 flex justify-between items-center">
            <div>
                <h2 class="text-xl font-extrabold">👥 Registo Geral de Membros</h2>
                <p class="text-xs text-indigo-200 mt-1">Cadastro de membros em comunhão e liderança da IEAD Chicuque</p>
            </div>
            <span class="bg-indigo-700 px-4 py-2 rounded-xl text-xs font-bold">Total: {{ membros|length }}</span>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div class="lg:col-span-5 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">➕ Cadastrar Membro</h3>
                <form action="/membros/novo" method="POST" class="space-y-3.5 text-xs">
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Nome Completo *</label>
                        <input type="text" name="nome" required placeholder="Ex: Criscencia Justino Munguambe" class="w-full h-10 px-3 border rounded-xl bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    </div>
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Documento (BI)</label>
                            <input type="text" name="bi" placeholder="Ex: 800100034567" class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                        </div>
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Contacto / Telefone</label>
                            <input type="text" name="contacto" placeholder="+258 84/82..." class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                        </div>
                    </div>
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Cargo</label>
                            <select name="cargo" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-semibold">
                                <option value="Membro em Comunhão">Membro em Comunhão</option>
                                <option value="Activista / Obreiro">Activista / Obreiro</option>
                                <option value="Diácono / Diaconisa">Diácono / Diaconisa</option>
                                <option value="Presbítero">Presbítero</option>
                                <option value="Evangelista">Evangelista</option>
                                <option value="Pastor">Pastor</option>
                            </select>
                        </div>
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Departamento</label>
                            <select name="departamento" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-semibold">
                                <option value="Geral">Geral</option>
                                <option value="Juventude Cristã">Juventude Cristã</option>
                                <option value="Círculo de Oração">Círculo de Oração</option>
                                <option value="Escola Dominical">Escola Dominical</option>
                                <option value="Evangelismo">Evangelismo</option>
                                <option value="Louvor">Louvor</option>
                            </select>
                        </div>
                    </div>
                    <button type="submit" class="w-full py-3 mt-2 bg-emerald-700 hover:bg-emerald-800 text-white font-bold rounded-xl shadow cursor-pointer transition">
                        Gravar Ficha de Membro
                    </button>
                </form>
            </div>

            <div class="lg:col-span-7 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">📋 Membros Registados ({{ membros|length }})</h3>
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse text-xs">
                        <thead>
                            <tr class="border-b-2 border-slate-200 text-slate-500">
                                <th class="py-2.5 px-2">Nome</th>
                                <th class="py-2.5 px-2">Contacto</th>
                                <th class="py-2.5 px-2">Cargo & Depto</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for m in membros %}
                            <tr class="border-b border-slate-100 hover:bg-slate-50">
                                <td class="py-3 px-2 font-bold text-slate-800">{{ m.nome }}</td>
                                <td class="py-3 px-2 text-slate-600">{{ m.contacto or '---' }}</td>
                                <td class="py-3 px-2">
                                    <span class="bg-indigo-50 text-indigo-700 px-2 py-1 rounded-md font-bold">{{ m.cargo }}</span>
                                    <span class="text-slate-500 ml-1">• {{ m.departamento }}</span>
                                </td>
                            </tr>
                            {% else %}
                            <tr>
                                <td colspan="3" class="py-8 text-center text-slate-400">Nenhum membro registado ainda.</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- 2. SECRETARIA & PLANIFICAÇÃO -->
        {% if aba_ativa == 'secretaria' %}
        <div class="bg-indigo-900 text-white p-5 rounded-2xl shadow mb-6">
            <h2 class="text-xl font-extrabold">📋 Secretaria Geral & Planificação de Actividades</h2>
            <p class="text-xs text-indigo-200 mt-1">Conforme o Modelo Oficial de Relatório da Assembleia de Deus</p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div class="lg:col-span-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">📌 Planificar Nova Actividade</h3>
                <form action="/secretaria/planificacao/nova" method="POST" class="space-y-3.5 text-xs">
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Departamento</label>
                        <select name="departamento" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-bold">
                            <option value="Juventude Cristã">Juventude Cristã</option>
                            <option value="Círculo de Oração">Círculo de Oração</option>
                            <option value="Escola Dominical">Escola Dominical</option>
                            <option value="Evangelismo & Missões">Evangelismo & Missões</option>
                            <option value="Direcção Geral">Direcção Geral</option>
                        </select>
                    </div>
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Tipo de Evento</label>
                        <select name="tipo_evento" class="w-full h-10 px-2 border rounded-xl bg-slate-50">
                            <option value="Seminário">Seminário</option>
                            <option value="Retiro Espiritual">Retiro Espiritual</option>
                            <option value="Aniversário de Departamento">Aniversário de Departamento</option>
                            <option value="Cruzada Evangelística">Cruzada Evangelística</option>
                            <option value="Conferência">Conferência</option>
                        </select>
                    </div>
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Nome da Actividade *</label>
                        <input type="text" name="actividade" required placeholder="Ex: 1º Seminário da Juventude" class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                    </div>
                    <div class="grid grid-cols-2 gap-2">
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Data Prevista</label>
                            <input type="date" name="data_prevista" required class="w-full h-10 px-2 border rounded-xl bg-slate-50">
                        </div>
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Frequência</label>
                            <select name="frequencia" class="w-full h-10 px-2 border rounded-xl bg-slate-50">
                                <option value="Pontual / Única">Pontual / Única</option>
                                <option value="Semanal">Semanal</option>
                                <option value="Mensal">Mensal</option>
                            </select>
                        </div>
                    </div>
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Responsável Directo</label>
                        <input type="text" name="responsavel" placeholder="Ex: Laura" class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                    </div>
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Contacto / WhatsApp</label>
                        <input type="text" name="contacto" placeholder="Ex: +258 84..." class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                    </div>
                    <button type="submit" class="w-full py-3 mt-2 bg-indigo-800 hover:bg-indigo-900 text-white font-bold rounded-xl shadow cursor-pointer transition">
                        Gravar Planificação
                    </button>
                </form>
            </div>

            <div class="lg:col-span-8 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">📊 Cronograma Eclesiástico ({{ planificacoes|length }})</h3>
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse text-xs">
                        <thead>
                            <tr class="border-b-2 border-slate-200 text-slate-500">
                                <th class="py-2.5 px-2">Actividade / Depto</th>
                                <th class="py-2.5 px-2">Data</th>
                                <th class="py-2.5 px-2">Responsável</th>
                                <th class="py-2.5 px-2">Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for p in planificacoes %}
                            <tr class="border-b border-slate-100 hover:bg-slate-50">
                                <td class="py-3 px-2">
                                    <div class="font-bold text-indigo-900">{{ p.actividade or p.titulo }}</div>
                                    <div class="text-[11px] text-slate-500">{{ p.departamento }} • {{ p.tipo_evento }}</div>
                                </td>
                                <td class="py-3 px-2 font-semibold text-slate-700">{{ p.data_prevista }}</td>
                                <td class="py-3 px-2 text-slate-600">
                                    <span class="font-semibold text-slate-800">{{ p.responsavel or '---' }}</span>
                                    {% if p.contacto %}<br><span class="text-[11px] text-slate-400">{{ p.contacto }}</span>{% endif %}
                                </td>
                                <td class="py-3 px-2">
                                    <span class="bg-blue-100 text-blue-800 px-2.5 py-1 rounded-full font-bold text-[11px]">
                                        {{ p.status or 'Planeado' }}
                                    </span>
                                </td>
                            </tr>
                            {% else %}
                            <tr>
                                <td colspan="4" class="py-8 text-center text-slate-400">Nenhuma actividade planificada ainda.</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- 3. CULTOS & PRESENÇAS -->
        {% if aba_ativa == 'cultos' %}
        <div class="bg-indigo-900 text-white p-5 rounded-2xl shadow mb-6">
            <h2 class="text-xl font-extrabold">⛪ Registo de Cultos & Presenças</h2>
            <p class="text-xs text-indigo-200 mt-1">Estatística oficial de cultos e vidas no altar</p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div class="lg:col-span-5 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">📝 Lançar Culto</h3>
                <form action="/cultos/novo" method="POST" class="space-y-3 text-xs">
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Data *</label>
                            <input type="date" name="data_culto" required class="w-full h-10 px-2 border rounded-xl bg-slate-50">
                        </div>
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Tipo de Culto</label>
                            <select name="tipo_culto" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-bold">
                                <option value="Culto de Domingo">Culto de Domingo</option>
                                <option value="Estudo Bíblico">Estudo Bíblico</option>
                                <option value="Culto de Oração">Culto de Oração</option>
                                <option value="Santa Ceia">Santa Ceia</option>
                            </select>
                        </div>
                    </div>

                    <div class="p-3 bg-slate-50 rounded-xl border border-slate-200 space-y-2">
                        <div class="font-bold text-slate-700 text-[11px] uppercase">Contagem</div>
                        <div class="grid grid-cols-2 gap-2">
                            <div><label class="text-slate-500">Homens</label><input type="number" name="homens_adultos" value="0" min="0" oninput="somarCulto()" class="campo-soma w-full h-8 px-2 border rounded bg-white"></div>
                            <div><label class="text-slate-500">Mulheres</label><input type="number" name="mulheres_adultas" value="0" min="0" oninput="somarCulto()" class="campo-soma w-full h-8 px-2 border rounded bg-white"></div>
                            <div><label class="text-slate-500">Jovens (R)</label><input type="number" name="jovens_rapazes" value="0" min="0" oninput="somarCulto()" class="campo-soma w-full h-8 px-2 border rounded bg-white"></div>
                            <div><label class="text-slate-500">Jovens (M)</label><input type="number" name="jovens_mocas" value="0" min="0" oninput="somarCulto()" class="campo-soma w-full h-8 px-2 border rounded bg-white"></div>
                            <div><label class="text-slate-500">Crianças</label><input type="number" name="criancas_meninos" value="0" min="0" oninput="somarCulto()" class="campo-soma w-full h-8 px-2 border rounded bg-white"></div>
                            <div><label class="text-slate-500">Visitantes</label><input type="number" name="visitantes_homens" value="0" min="0" oninput="somarCulto()" class="campo-soma w-full h-8 px-2 border rounded bg-white"></div>
                        </div>
                        <div class="grid grid-cols-2 gap-2 pt-2 border-t">
                            <div>
                                <label class="font-bold text-amber-700">🔥 Apelos</label>
                                <input type="number" name="apelos" value="0" min="0" class="w-full h-9 px-2 border-2 border-amber-300 rounded bg-amber-50 font-bold text-center">
                            </div>
                            <div>
                                <label class="font-bold text-blue-800">📊 Total</label>
                                <input type="number" id="total_presentes" name="total_presentes" value="0" readonly class="w-full h-9 px-2 border-2 border-blue-400 rounded bg-blue-50 font-extrabold text-center text-blue-900">
                            </div>
                        </div>
                    </div>

                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Pregador</label>
                            <input type="text" name="pregador" placeholder="Nome do Pregador" class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                        </div>
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Tema / Texto</label>
                            <input type="text" name="tema_mensagem" placeholder="Ex: Salmo 23" class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                        </div>
                    </div>

                    <button type="submit" class="w-full py-3 bg-indigo-700 hover:bg-indigo-800 text-white font-bold rounded-xl shadow cursor-pointer transition">
                        Gravar Relatório de Culto
                    </button>
                </form>
            </div>

            <div class="lg:col-span-7 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">📚 Histórico de Cultos ({{ cultos|length }})</h3>
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse text-xs">
                        <thead>
                            <tr class="border-b-2 border-slate-200 text-slate-500">
                                <th class="py-2.5 px-2">Data</th>
                                <th class="py-2.5 px-2">Culto & Pregador</th>
                                <th class="py-2.5 px-2 text-center">Presentes</th>
                                <th class="py-2.5 px-2 text-center">Apelos</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for c in cultos %}
                            <tr class="border-b border-slate-100 hover:bg-slate-50">
                                <td class="py-3 px-2 font-semibold text-slate-700">{{ c.data_culto }}</td>
                                <td class="py-3 px-2">
                                    <div class="font-bold text-slate-800">{{ c.tipo_culto }}</div>
                                    <div class="text-[11px] text-slate-500">{{ c.pregador or '---' }}</div>
                                </td>
                                <td class="py-3 px-2 text-center">
                                    <span class="bg-blue-100 text-blue-900 px-3 py-1 rounded-full font-bold">{{ c.total_presentes }}</span>
                                </td>
                                <td class="py-3 px-2 text-center">
                                    <span class="bg-amber-100 text-amber-800 px-2.5 py-1 rounded-full font-bold">{{ c.apelos }}</span>
                                </td>
                            </tr>
                            {% else %}
                            <tr>
                                <td colspan="4" class="py-8 text-center text-slate-400">Nenhum culto registado ainda.</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- 4. NOVOS CONVERTIDOS -->
        {% if aba_ativa == 'convertidos' %}
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div class="lg:col-span-5 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">🌱 Registar Novo Convertido</h3>
                <form action="/convertidos/novo" method="POST" class="space-y-3.5 text-xs">
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Nome Completo *</label>
                        <input type="text" name="nome" required placeholder="Ex: Criscencia Justino Munguambe" class="w-full h-11 px-3 border rounded-xl bg-blue-50/50 focus:bg-white">
                    </div>
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Contacto / Telefone</label>
                        <input type="text" name="telefone" placeholder="+258 82/84..." class="w-full h-11 px-3 border rounded-xl bg-blue-50/50 focus:bg-white">
                    </div>
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Data da Decisão</label>
                        <input type="date" name="data_decisao" required class="w-full h-11 px-3 border rounded-xl bg-white">
                    </div>
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Bairro / Residência</label>
                        <input type="text" name="bairro" placeholder="Ex: Chicuque" class="w-full h-11 px-3 border rounded-xl bg-blue-50/50 focus:bg-white">
                    </div>
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Quem Convidou / Discipulador</label>
                        <input type="text" name="quem_convidou" placeholder="Ex: Orlando" class="w-full h-11 px-3 border rounded-xl bg-blue-50/50 focus:bg-white">
                    </div>
                    <button type="submit" class="w-full py-3.5 bg-emerald-700 hover:bg-emerald-800 text-white font-bold rounded-xl shadow cursor-pointer transition text-sm">
                        Registar para Discipulado
                    </button>
                </form>
            </div>

            <div class="lg:col-span-7 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">Acompanhamento Espiritual ({{ convertidos|length }})</h3>
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse text-xs">
                        <thead>
                            <tr class="border-b-2 border-slate-200 text-slate-600 bg-slate-50">
                                <th class="py-3 px-3">Nome</th>
                                <th class="py-3 px-3">Contacto</th>
                                <th class="py-3 px-3">Bairro</th>
                                <th class="py-3 px-3">Estado</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for c in convertidos %}
                            <tr class="border-b border-slate-100 hover:bg-slate-50">
                                <td class="py-3.5 px-3 font-bold text-slate-800">
                                    {{ c.nome }}
                                    <div class="text-[11px] font-normal text-slate-400">{{ c.data_decisao }}</div>
                                </td>
                                <td class="py-3.5 px-3 text-slate-600">{{ c.telefone or '---' }}</td>
                                <td class="py-3.5 px-3 text-slate-600">{{ c.bairro or '---' }}</td>
                                <td class="py-3.5 px-3">
                                    <span class="bg-emerald-100 text-emerald-800 px-3 py-1 rounded-full font-bold text-[11px]">
                                        {{ c.status_discipulado or 'Acompanhamento' }}
                                    </span>
                                </td>
                            </tr>
                            {% else %}
                            <tr>
                                <td colspan="4" class="py-10 text-center text-slate-400">Nenhum novo convertido registado ainda.</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- 5. FINANÇAS & CAIXA -->
        {% if aba_ativa == 'financas' %}
        <div class="bg-emerald-900 text-white p-5 rounded-2xl shadow mb-6">
            <h2 class="text-xl font-extrabold">💰 Tesouraria & Movimentos de Caixa</h2>
            <p class="text-xs text-emerald-200 mt-1">Dízimos, ofertas e despesas da IEAD Chicuque</p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div class="lg:col-span-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">➕ Lançamento no Caixa</h3>
                <form action="/financas/caixa/novo" method="POST" class="space-y-3.5 text-xs">
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Tipo</label>
                            <select name="tipo" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-bold">
                                <option value="Entrada">🟢 Entrada (+)</option>
                                <option value="Saída">🔴 Saída (-)</option>
                            </select>
                        </div>
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Data</label>
                            <input type="date" name="data_movimento" required class="w-full h-10 px-2 border rounded-xl bg-slate-50">
                        </div>
                    </div>
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Categoria</label>
                        <select name="categoria" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-semibold">
                            <option value="Dízimos">Dízimos</option>
                            <option value="Oferta de Culto">Oferta de Culto</option>
                            <option value="Oferta de Missões">Oferta de Missões</option>
                            <option value="Fundo de Construção">Fundo de Construção</option>
                            <option value="Despesa Operacional">Despesa Operacional</option>
                        </select>
                    </div>
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Valor (MZN) *</label>
                        <input type="number" step="0.01" name="valor" required placeholder="Ex: 2500.00" class="w-full h-10 px-3 border rounded-xl bg-slate-50 font-bold text-sm">
                    </div>
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Descrição</label>
                        <input type="text" name="descricao" placeholder="Detalhes..." class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                    </div>
                    <button type="submit" class="w-full py-3 bg-emerald-700 hover:bg-emerald-800 text-white font-bold rounded-xl shadow cursor-pointer transition">
                        Gravar Movimento
                    </button>
                </form>
            </div>

            <div class="lg:col-span-8 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">📊 Livro Caixa ({{ caixa|length }})</h3>
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse text-xs">
                        <thead>
                            <tr class="border-b-2 border-slate-200 text-slate-500">
                                <th class="py-2.5 px-2">Data</th>
                                <th class="py-2.5 px-2">Tipo</th>
                                <th class="py-2.5 px-2">Categoria</th>
                                <th class="py-2.5 px-2 text-right">Valor</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for cx in caixa %}
                            <tr class="border-b border-slate-100 hover:bg-slate-50">
                                <td class="py-3 px-2 text-slate-600">{{ cx.data_movimento }}</td>
                                <td class="py-3 px-2">
                                    <span class="{% if cx.tipo == 'Entrada' %}bg-emerald-100 text-emerald-800{% else %}bg-rose-100 text-rose-800{% endif %} px-2 py-0.5 rounded font-bold">
                                        {{ cx.tipo }}
                                    </span>
                                </td>
                                <td class="py-3 px-2 font-bold">{{ cx.categoria }}</td>
                                <td class="py-3 px-2 text-right font-extrabold {% if cx.tipo == 'Entrada' %}text-emerald-700{% else %}text-rose-700{% endif %}">
                                    {{ cx.valor }} MT
                                </td>
                            </tr>
                            {% else %}
                            <tr>
                                <td colspan="4" class="py-8 text-center text-slate-400">Nenhum movimento no caixa.</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- 6. DOUTRINA & BATISMO -->
        {% if aba_ativa == 'doutrina' %}
        <div class="bg-amber-900 text-white p-5 rounded-2xl shadow mb-6">
            <h2 class="text-xl font-extrabold">📖 Escola de Doutrina & Candidatos ao Batismo</h2>
            <p class="text-xs text-amber-200 mt-1">Preparação batismal e formação discipular</p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div class="lg:col-span-5 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">🎓 Inscrever Candidato</h3>
                <form action="/doutrina/novo" method="POST" class="space-y-3.5 text-xs">
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Nome do Candidato *</label>
                        <input type="text" name="nome_aluno" required placeholder="Nome completo" class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                    </div>
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Classe</label>
                        <select name="classe" class="w-full h-10 px-2 border rounded-xl bg-slate-50 font-bold">
                            <option value="Preparação para Batismo">Preparação para Batismo</option>
                            <option value="Discipulado de Novos Convertidos">Discipulado de Novos Convertidos</option>
                            <option value="Formação de Líderes">Formação de Líderes</option>
                        </select>
                    </div>
                    <div>
                        <label class="block font-semibold text-slate-600 mb-1">Lição Atual</label>
                        <select name="licao_atual" class="w-full h-10 px-2 border rounded-xl bg-slate-50">
                            <option value="Lição 1 - Salvação">Lição 1 - Salvação</option>
                            <option value="Lição 2 - Oração e Bíblia">Lição 2 - Oração e Bíblia</option>
                            <option value="Lição 3 - O Batismo nas Águas">Lição 3 - O Batismo nas Águas</option>
                            <option value="Lição 4 - Santa Ceia">Lição 4 - Santa Ceia</option>
                            <option value="Apto para o Batismo">✅ Apto para o Batismo</option>
                        </select>
                    </div>
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Instrutor</label>
                            <input type="text" name="professor" placeholder="Pr. / Diác." class="w-full h-10 px-3 border rounded-xl bg-slate-50">
                        </div>
                        <div>
                            <label class="block font-semibold text-slate-600 mb-1">Data Início</label>
                            <input type="date" name="data_inicio" required class="w-full h-10 px-2 border rounded-xl bg-slate-50">
                        </div>
                    </div>
                    <button type="submit" class="w-full py-3 bg-amber-700 hover:bg-amber-800 text-white font-bold rounded-xl shadow cursor-pointer transition">
                        Gravar Candidato
                    </button>
                </form>
            </div>

            <div class="lg:col-span-7 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 class="font-bold text-base mb-4 border-b pb-2">📋 Formandos & Candidatos ({{ doutrina|length }})</h3>
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse text-xs">
                        <thead>
                            <tr class="border-b-2 border-slate-200 text-slate-500">
                                <th class="py-2.5 px-2">Nome</th>
                                <th class="py-2.5 px-2">Classe</th>
                                <th class="py-2.5 px-2">Progresso</th>
                                <th class="py-2.5 px-2">Situação</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for d in doutrina %}
                            <tr class="border-b border-slate-100 hover:bg-slate-50">
                                <td class="py-3 px-2 font-bold text-slate-800">{{ d.nome_aluno }}</td>
                                <td class="py-3 px-2 text-slate-600">{{ d.classe }}</td>
                                <td class="py-3 px-2 font-semibold text-amber-900">{{ d.licao_atual }}</td>
                                <td class="py-3 px-2">
                                    <span class="bg-amber-100 text-amber-800 px-2 py-0.5 rounded font-bold text-[11px]">{{ d.situacao }}</span>
                                </td>
                            </tr>
                            {% else %}
                            <tr>
                                <td colspan="4" class="py-8 text-center text-slate-400">Nenhum candidato inscrito ainda.</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        {% endif %}

    </main>

    <!-- SCRIPT DE SOMA DIRETO -->
    <script>
        function somarCulto() {
            var inputs = document.querySelectorAll('.campo-soma');
            var tot = 0;
            inputs.forEach(function(i) { tot += (parseInt(i.value, 10) || 0); });
            var el = document.getElementById('total_presentes');
            if (el) el.value = tot;
        }
    </script>
</body>
</html>
"""

with open(os.path.join('templates', 'dashboard.html'), 'w', encoding='utf-8') as f:
    f.write(html_conteudo)

print("✓ templates/dashboard.html GERADO COM SUCESSO E SEM ERROS DE JS!")
print("=" * 70)