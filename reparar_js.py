import os
import re

print("=" * 70)
print("REPARANDO ERRO DE JAVASCRIPT NA LINHA 8559...")
print("=" * 70)

caminho = os.path.join('templates', 'dashboard.html')
with open(caminho, 'r', encoding='utf-8', errors='ignore') as f:
    linhas = f.readlines()

print(f"Total de linhas no template: {len(linhas)}")

# Exibir as últimas linhas para identificar a tag corrompida
ini = max(0, len(linhas) - 30)
print("\n--- ÚLTIMAS LINHAS DO FICHEIRO ---")
for i, l in enumerate(linhas[ini:], start=ini+1):
    print(f"{i}: {l.rstrip()}")
print("---------------------------------\n")

conteudo = "".join(linhas)

# 1. Remover blocos de script mal fechados ou anexados incorretamente no final
conteudo = re.sub(r'<!--\s*=================\s*SCRIPT DE SOMA[\s\S]*?$', '', conteudo)
conteudo = re.sub(r'<script>\s*function somarPresencasTempoReal[\s\S]*?$', '', conteudo)

# 2. Assegurar que todas as tags <script> abertas estão devidamente fechadas com </script>
abertos = len(re.findall(r'<script\b', conteudo, re.IGNORECASE))
fechados = len(re.findall(r'</script>', conteudo, re.IGNORECASE))

print(f"Contagem de scripts: <script> = {abertos} | </script> = {fechados}")

if abertos > fechados:
    diferenca = abertos - fechados
    print(f"⚠️ Detectadas {diferenca} tag(s) <script> sem fecho. Adicionando </script>...")
    conteudo = conteudo.rstrip() + ("\n</script>" * diferenca)

# 3. Adicionar o script de forma isolada e sintaticamente limpa
script_limpo = """
<script>
// Funcao global de troca de abas e soma protegida
function somarPresencasTempoReal() {
    try {
        var campos = ['homens_adultos', 'mulheres_adultas', 'jovens_rapazes', 'jovens_mocas', 'criancas_meninos', 'criancas_meninas', 'visitantes_homens', 'visitantes_mulheres'];
        var total = 0;
        campos.forEach(function(n) {
            var el = document.querySelector('input[name="' + n + '"]');
            if (el) total += (parseInt(el.value, 10) || 0);
        });
        var out = document.getElementById('total_presentes_display');
        if (out) out.value = total;
    } catch(e) {}
}

document.addEventListener('input', function(e) {
    if (e.target && e.target.type === 'number') somarPresencasTempoReal();
});
</script>
"""

conteudo = conteudo.rstrip() + "\n" + script_limpo.strip() + "\n"

with open(caminho, 'w', encoding='utf-8') as f:
    f.write(conteudo)

print("✓ templates/dashboard.html corrigido e limpo com sucesso!")
print("=" * 70)
