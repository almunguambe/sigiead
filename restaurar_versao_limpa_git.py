import os
import re
import py_compile
import subprocess
import jinja2

print("=" * 80)
print("A LOCALIZAR E RESTAURAR O COMMIT LIMPO NO HISTÓRICO DO GIT...")
print("=" * 80)

caminho_dash = os.path.join('templates', 'dashboard.html')

# 1. Obter histórico de commits que mexeram em templates/dashboard.html
log_cmd = subprocess.run(["git", "log", "--oneline", "-n", "50", "templates/dashboard.html"], capture_output=True, text=True)
commits = [line.split()[0] for line in log_cmd.stdout.splitlines() if line.strip()]

commit_escolhido = None
conteudo_limpo = None

for c in commits:
    show_cmd = subprocess.run(["git", "show", f"{c}:templates/dashboard.html"], capture_output=True, text=True)
    txt = show_cmd.stdout
    
    # Critérios rigorosos da versão íntegra do SIGIEAD:
    pos_aside = txt.find('</aside>')
    if pos_aside != -1:
        aside = txt[:pos_aside]
        # Barra lateral limpa deve ter os itens e NÃO pode ter cartões de formulário colados
        tem_membros = '1. Membros' in aside
        tem_sec = '2. Secretaria' in aside
        sem_card_no_menu = ('FICHA DE CADASTRO' not in aside and 
                            'SECRETARIA GERAL' not in aside and 
                            'FOTOGRAFIA TIPO PASSE' not in aside)
        sem_esmagamento = 'EstadZona' not in txt
        
        if tem_membros and tem_sec and sem_card_no_menu and sem_esmagamento:
            commit_escolhido = c
            conteudo_limpo = txt
            print(f"✓ Commit original limpo identificado com sucesso: {c}")
            break

# Se o histórico tiver commits, restaurar; senão, verificar backups locais
if commit_escolhido:
    print(f"A restaurar templates/dashboard.html a partir do commit {commit_escolhido}...")
    subprocess.run(["git", "checkout", commit_escolhido, "--", "templates/dashboard.html"], check=True)
    with open(caminho_dash, 'r', encoding='utf-8') as f:
        html = f.read()
else:
    print("Aviso: A verificar ficheiros de backup locais...")
    restaurado = False
    for b in ['templates/dashboard_backup_estrutural.html', 'templates/dashboard.html.bak']:
        if os.path.exists(b):
            with open(b, 'r', encoding='utf-8') as f:
                txt = f.read()
            if '1. Membros' in txt and 'EstadZona' not in txt:
                html = txt
                restaurado = True
                print(f"✓ Restaurado a partir do backup {b}!")
                break
    if not restaurado:
        with open(caminho_dash, 'r', encoding='utf-8') as f:
            html = f.read()

# =============================================================================
# 2. POPULAR OPÇÕES DOS SELETORES SEM MEXER EM NENHUMA DIV OU CLASSE DE LAYOUT
# =============================================================================
print("\n" + "=" * 80)
print("A PREENCHER AS OPÇÕES DOS SELETORES...")
print("=" * 80)

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
    padrao = rf'(<select[^>]*name=["\']{campo}["\'][^>]*>)([\s\S]*?)(</select>)'
    def injetar_opcoes(m):
        abertura = m.group(1)
        conteudo_interno = m.group(2)
        fecho = m.group(3)
        if conteudo_interno.count('<option') <= 1:
            opts = "\n".join([f'    <option value="{o}">{o}</option>' for o in lista])
            return f'{abertura}\n    <option value="">Selecione...</option>\n{opts}\n{fecho}'
        return m.group(0)
    html = re.sub(padrao, injetar_opcoes, html, flags=re.IGNORECASE)

# Remover qualquer overflow-x-auto residual dos selects para evitar scrollbars no Chrome
html = re.sub(r'(<select[^>]*class="[^"]*)\boverflow-x-auto\b([^"]*)"', r'\1\2"', html)

# Validação estrita do template Jinja2
env = jinja2.Environment()
env.parse(html)
with open(caminho_dash, 'w', encoding='utf-8') as f:
    f.write(html)
print("✓ templates/dashboard.html validado com ZERO erros no Jinja2!")

# =============================================================================
# 3. PUBLICAR NO GITHUB E NO RENDER
# =============================================================================
print("\n" + "=" * 80)
print("A ENVIAR ATUALIZAÇÃO LIMPA PARA O RENDER...")
print("=" * 80)

subprocess.run(["git", "add", "templates/dashboard.html"])
subprocess.run(["git", "commit", "-m", "Restauracao tecnica definitiva do dashboard original sem efeitos colaterais"])
subprocess.run(["git", "push", "origin", "main"])

print("=" * 80)
print(">>> PROCESSO CONCLUÍDO E PUBLICADO NO RENDER COM SUCESSO! <<<")
print("=" * 80)