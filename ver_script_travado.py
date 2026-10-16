with open('templates/dashboard.html', 'r', encoding='utf-8', errors='ignore') as f:
    linhas = f.readlines()

print("=" * 70)
print(f"TOTAL DE LINHAS NO DASHBOARD: {len(linhas)}")
print("=" * 70)

# 1. Rastrear exatamente onde cada script abre e fecha
in_script = False
aberto_em = 0

print("RASTREAMENTO DE TAGS <script>:")
for num, linha in enumerate(linhas, 1):
    tem_abre = '<script' in linha.lower()
    tem_fecha = '</script>' in linha.lower()
    
    if tem_abre and not tem_fecha:
        if in_script:
            print(f"🚨 ERRO: <script> aberto na linha {num} sem fechar o anterior (da linha {aberto_em})!")
        in_script = True
        aberto_em = num
        print(f"  -> Linha {num:4d}: <script> aberto")
    elif tem_fecha and not tem_abre:
        in_script = False
        print(f"  <- Linha {num:4d}: </script> fechado (fechou o da linha {aberto_em})")
    elif tem_abre and tem_fecha:
        print(f"  <-> Linha {num:4d}: <script> inline completo")

if in_script:
    print(f"\n🚨 AVISO CRÍTICO: O <script> aberto na linha {aberto_em} NUNCA FOI FECHADO!")

# 2. Exibir o que existe ao redor da linha 8559
print("\n" + "=" * 70)
print("CONTEÚDO AO REDOR DA LINHA 8559:")
print("=" * 70)
ini = max(0, 8550 - 1)
fim = min(len(linhas), 8565)
for i in range(ini, fim):
    marcador = " >>> ERRO AQUI >>> " if (i + 1) == 8559 else "                   "
    print(f"{i+1:4d}{marcador}{linhas[i].rstrip()}")
print("=" * 70)
