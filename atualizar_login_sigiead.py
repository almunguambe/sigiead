import os
import re
import jinja2

print("=" * 80)
print("A ATUALIZAR INTERFACE PARA SIGIEAD E A REMOVER ATALHOS DE ACESSO...")
print("=" * 80)

# =============================================================================
# 1. NOVA TELA DE LOGIN: BRANDING SIGIEAD E FORMULÁRIO LIMPO
# =============================================================================
login_html_sigiead = """<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SIGIEAD - Igreja Evangélica Assembleia de Deus</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .celestial-bg {
            background: radial-gradient(circle at 50% 0%, #1e1b4b 0%, #0f172a 50%, #020617 100%);
        }
        .glow-gold {
            box-shadow: 0 0 50px -5px rgba(245, 158, 11, 0.3);
        }
    </style>
</head>
<body class="celestial-bg min-h-screen flex items-center justify-center p-4 font-sans text-slate-800">

    <div class="max-w-4xl w-full grid grid-cols-1 md:grid-cols-12 bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl overflow-hidden border border-amber-500/30 glow-gold">

        <!-- LADO ESQUERDO: IDENTIDADE INSTITUCIONAL SIGIEAD -->
        <div class="md:col-span-5 bg-gradient-to-br from-indigo-950 via-slate-900 to-slate-950 p-8 text-white flex flex-col justify-between border-r border-indigo-900/40">
            <div class="space-y-4">
                <!-- LOGÓTIPO OFICIAL DA IGREJA -->
                <div class="w-24 h-24 bg-white rounded-3xl p-2 shadow-2xl flex items-center justify-center border-2 border-amber-400 mx-auto md:mx-0">
                    {% include 'logo_ad.html' %}
                </div>

                <div>
                    <span id="saudacao_tempo" class="bg-amber-400/20 text-amber-300 border border-amber-400/40 text-[9px] font-black uppercase px-2.5 py-0.5 rounded-full inline-block mb-1.5">
                        Paz do Senhor Jesus
                    </span>
                    <!-- SIGLA OFICIAL -->
                    <h1 class="text-3xl font-black uppercase tracking-wider text-amber-400 leading-none">
                        SIGIEAD
                    </h1>
                    <!-- SIGNIFICADO POR EXTENSO -->
                    <p class="text-[11px] font-extrabold uppercase text-slate-100 mt-1 leading-snug">
                        Sistema Integrado de Gestão da Igreja Evangélica Assembleia de Deus
                    </p>
                    <p class="text-[10px] text-blue-300 font-semibold mt-0.5">República de Moçambique</p>
                </div>

                <div class="bg-white/5 border border-white/10 p-4 rounded-2xl text-xs space-y-2 text-indigo-100">
                    <p class="font-extrabold text-amber-300 flex items-center gap-1.5 text-[11px]">
                        <span>🕊️</span> Bem-vindo à Casa do Senhor!
                    </p>
                    <p class="leading-relaxed text-[11px] text-slate-200 text-justify">
                        Plataforma unificada para membresia, congregações, cultos, formação bíblica e finanças. O direcionamento para cada painel é realizado automaticamente após autenticação das suas credenciais.
                    </p>
                </div>
            </div>

            <div class="pt-6 border-t border-white/10 text-[10px] italic text-indigo-200 text-center font-serif">
                "Alegrei-me quando me disseram: Vamos à casa do Senhor!" (Salmo 122:1)
            </div>
        </div>

        <!-- LADO DIREITO: FORMULÁRIO DE ENTRADA EXCLUSIVO (SEM ATALHOS) -->
        <div class="md:col-span-7 p-8 sm:p-12 flex flex-col justify-center space-y-6">

            <div class="space-y-1">
                <div class="inline-flex items-center gap-2 bg-indigo-50 text-indigo-900 border border-indigo-200 px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider">
                    <span>🔐</span> Portal de Autenticação
                </div>
                <h2 class="text-2xl font-black text-slate-900">Acesso ao SIGIEAD</h2>
                <p class="text-xs text-slate-500">Introduza as suas credenciais para entrar na sua congregação e ministério.</p>
            </div>

            {% if erro %}
            <div class="p-3.5 bg-rose-50 border-2 border-rose-300 rounded-xl text-rose-800 text-xs font-bold text-center">
                {{ erro }}
            </div>
            {% endif %}

            <form action="/login" method="POST" class="space-y-4 text-xs">
                <div>
                    <label class="block font-bold text-slate-700 mb-1.5 text-[11px]">Nome de Utilizador *</label>
                    <div class="relative">
                        <span class="absolute left-3.5 top-3.5 text-slate-400">👤</span>
                        <input type="text" name="usuario" required placeholder="Digite o seu utilizador" class="w-full h-12 pl-10 pr-3 border-2 border-slate-200 rounded-xl bg-slate-50 focus:bg-white focus:border-indigo-600 focus:outline-none font-bold text-slate-900">
                    </div>
                </div>

                <div>
                    <label class="block font-bold text-slate-700 mb-1.5 text-[11px]">Palavra-passe *</label>
                    <div class="relative">
                        <span class="absolute left-3.5 top-3.5 text-slate-400">🔒</span>
                        <input type="password" name="senha" required placeholder="••••••••" class="w-full h-12 pl-10 pr-3 border-2 border-slate-200 rounded-xl bg-slate-50 focus:bg-white focus:border-indigo-600 focus:outline-none font-bold text-slate-900">
                    </div>
                </div>

                <button type="submit" class="w-full py-4 bg-gradient-to-r from-indigo-900 to-blue-900 hover:from-indigo-950 hover:to-blue-950 text-white font-black rounded-xl shadow-xl cursor-pointer text-sm transition transform hover:-translate-y-0.5 mt-2">
                    Entrar no Sistema →
                </button>
            </form>

            <div class="pt-4 border-t border-slate-200 text-center text-[10px] text-slate-400">
                <span>SIGIEAD • Igreja Evangélica Assembleia de Deus em Moçambique</span>
            </div>

        </div>

    </div>

    <script>
        var hora = new Date().getHours();
        var saudacao = "Paz do Senhor • Bom dia";
        if (hora >= 12 && hora < 18) saudacao = "Paz do Senhor • Boa tarde";
        else if (hora >= 18 || hora < 5) saudacao = "Paz do Senhor • Boa noite";
        var el = document.getElementById('saudacao_tempo');
        if (el) el.innerText = saudacao;
    </script>

</body>
</html>
"""

env = jinja2.Environment()
env.parse(login_html_sigiead)
with open('templates/login.html', 'w', encoding='utf-8') as f:
    f.write(login_html_sigiead)
print("✓ templates/login.html: Atualizado com a marca SIGIEAD e sem atalhos!")

# =============================================================================
# 2. ATUALIZAR BARRA LATERAL EM DASHBOARD.HTML COM A SIGLA SIGIEAD
# =============================================================================
with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    dash_html = f.read()

dash_html = re.sub(
    r'<h1 class="font-extrabold text-xs uppercase tracking-wide leading-tight text-white truncate">[\s\S]*?<\/h1>',
    '<h1 class="font-extrabold text-xs uppercase tracking-wider text-amber-400 truncate">SIGIEAD</h1>',
    dash_html
)

env.parse(dash_html)
with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(dash_html)
print("✓ templates/dashboard.html: Topo da barra lateral atualizado com a sigla SIGIEAD!")

print("=" * 80)
print(">>> ATUALIZAÇÃO CONCLUÍDA COM TOTAL SUCESSO! <<<")
print("=" * 80)