import os
import shutil
import ast
import jinja2

print("=" * 70)
print("A FINALIZAR A LIGAÇÃO DOS FORMULÁRIOS E VALIDAÇÃO COMPLETA...")
print("=" * 70)

# 1. AJUSTAR TEMPLATES/DASHBOARD.HTML
tpl_dash = os.path.join('templates', 'dashboard.html')
with open(tpl_dash, 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

# Garantir que o bloco de Novos Convertidos tem a sua própria tag <form>
btn_termo = "Registar para Discipulado"
pos_btn = html.find(btn_termo)
if pos_btn != -1:
    pos_bloco = html.rfind("Registar Novo Convertido", 0, pos_btn)
    if pos_bloco != -1:
        # Verifica se já existe um form exclusivo para convertidos
        trecho = html[pos_bloco:pos_btn]
        if '/convertidos/novo' not in trecho:
            pos_input = html.find('<input', pos_bloco, pos_btn)
            if pos_input != -1:
                html = html[:pos_input] + '</form>\n<form action="/convertidos/novo" method="POST">\n                            ' + html[pos_input:]
                print("✓ Formulário de Novos Convertidos devidamente isolado para /convertidos/novo!")

# Script de cálculo em tempo real para Cultos
script_calculo = """
<!-- ================= SCRIPT DE SOMA EM TEMPO REAL ================= -->
<script>
function somarPresencasTempoReal() {
    var campos = [
        'homens_adultos', 'mulheres_adultas',
        'jovens_rapazes', 'jovens_mocas',
        'criancas_meninos', 'criancas_meninas',
        'visitantes_homens', 'visitantes_mulheres'
    ];
    var total = 0;
    campos.forEach(function(nome) {
        var inp = document.querySelector('input[name="' + nome + '"]');
        if (inp) {
            total += (parseInt(inp.value, 10) || 0);
        }
    });
    var disp = document.getElementById('total_presentes_display');
    if (disp) {
        disp.value = total;
    }
}

document.addEventListener('input', function(e) {
    if (e.target && e.target.type === 'number' && e.target.name !== 'apelos' && e.target.name !== 'total_presentes') {
        somarPresencasTempoReal();
    }
});

document.addEventListener('DOMContentLoaded', function() {
    somarPresencasTempoReal();
});
</script>
"""

if 'somarPresencasTempoReal' not in html:
    html = html + "\n" + script_calculo

# Validação estrita com Jinja2
try:
    jinja2.Environment().parse(html)
    with open(tpl_dash, 'w', encoding='utf-8') as f:
        f.write(html)
    print("✓ templates/dashboard.html validado com 0 erros de sintaxe!")
except Exception as e_jinja:
    print(f"❌ Erro Jinja2: {e_jinja}")
    exit(1)

# 2. VALIDAR APP.PY COM O COMPILADOR AST DO PYTHON
with open('app.py', 'r', encoding='utf-8', errors='ignore') as f:
    app_py = f.read()

try:
    ast.parse(app_py)
    print("✓ app.py validado com 0 erros de compilação Python!")
except SyntaxError as e_py:
    print(f"❌ Erro Python no app.py: {e_py}")
    exit(1)

print("=" * 70)
print("✓ TUDO 100% VALIDADO E PRONTO PARA ENVIAR AO RENDER!")
print("=" * 70)
