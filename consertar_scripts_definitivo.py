import os
import shutil
import re

print("=" * 70)
print("EXTIRPANDO BLOCO DE SCRIPTS CORROMPIDOS (LINHAS 2000 A 2099)...")
print("=" * 70)

caminho = os.path.join('templates', 'dashboard.html')
shutil.copy(caminho, caminho + '.bak_trava')

with open(caminho, 'r', encoding='utf-8', errors='ignore') as f:
    linhas = f.readlines()

print(f"Total de linhas atual: {len(linhas)}")

# Cortar exatamente na linha 2000 (onde o fechamento original terminou em 1999)
linhas_limpas = linhas[:2000]

conteudo_base = "".join(linhas_limpas).rstrip()

# Injetar UM ÚNICO bloco de script, perfeitamente fechado e isolado
script_definitivo = """

<!-- SCRIPT DE APOIO UNIFICADO (CALCULO DE CULTOS E CONTROLE) -->
<script>
function somarPresencasTempoReal() {
    try {
        var campos = [
            'homens_adultos', 'mulheres_adultas',
            'jovens_rapazes', 'jovens_mocas',
            'criancas_meninos', 'criancas_meninas',
            'visitantes_homens', 'visitantes_mulheres'
        ];
        var total = 0;
        campos.forEach(function(nome) {
            var el = document.querySelector('input[name="' + nome + '"]');
            if (el) {
                total += (parseInt(el.value, 10) || 0);
            }
        });
        var display = document.getElementById('total_presentes_display');
        if (display) {
            display.value = total;
        }
    } catch (e) {}
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
</body>
</html>
"""

html_final = conteudo_base + script_definitivo

with open(caminho, 'w', encoding='utf-8') as f:
    f.write(html_final)

print("✓ Linhas corrompidas eliminadas e bloco de apoio reinserido de forma limpa!")

# Verificação de segurança: checar contagem de scripts
abertos = len(re.findall(r'<script\b', html_final, re.IGNORECASE))
fechados = len(re.findall(r'</script>', html_final, re.IGNORECASE))
print(f"-> Verificação de tags: <script> = {abertos} | </script> = {fechados}")

if abertos == fechados:
    print("✓ EQUILÍBRIO PERFEITO: Nenhuma tag aberta sem fecho!")
else:
    print("⚠️ Atenção: discrepância remanescente nas tags.")

print("=" * 70)
