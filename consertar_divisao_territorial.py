import py_compile

print("=" * 80)
print("A INJETAR O DICIONÁRIO OFICIAL DIVISAO_TERRITORIAL EM APP.PY...")
print("=" * 80)

caminho_app = 'app.py'
with open(caminho_app, 'r', encoding='utf-8') as f:
    codigo = f.read()

# Dicionário com todas as províncias e distritos de Moçambique
bloco_divisao = '''
# =============================================================================
# DIVISÃO TERRITORIAL OFICIAL DE MOÇAMBIQUE (PROVÍNCIAS E DISTRITOS)
# =============================================================================
DIVISAO_TERRITORIAL = {
    "Inhambane": [
        "Maxixe (Cidade/Distrito)", "Inhambane (Cidade)", "Homoíne", "Jangamo",
        "Massinga", "Morrumbene", "Vilankulo", "Zavala", "Inharrime",
        "Panda", "Funhalouro", "Mabote", "Govuro"
    ],
    "Gaza": [
        "Xai-Xai (Cidade)", "Chókwè", "Bilene", "Chibuto", "Mandlakazi",
        "Guijá", "Mabalane", "Chigubo", "Chicualacuala", "Massingir", "Massangena", "Limpopo"
    ],
    "Maputo Província": [
        "Matola (Cidade)", "Boane", "Marracuene", "Manhiça", "Moamba", "Namaacha", "Matutuíne"
    ],
    "Maputo Cidade": [
        "KaMpfumo", "Nlhamankulu", "KaMaxakeni", "KaMavota", "KaMubukwana", "KaTembe", "KaNyaka"
    ],
    "Sofala": [
        "Beira (Cidade)", "Dondo", "Nhamatanda", "Búzi", "Gorongosa", "Cheringoma",
        "Marromeu", "Caia", "Chemba", "Machanga", "Muanza", "Chibabava"
    ],
    "Manica": [
        "Chimoio (Cidade)", "Gondola", "Manica", "Mossurize", "Sussundenga", "Báruè",
        "Guro", "Macossa", "Tambara", "Vanduzi", "Macate"
    ],
    "Tete": [
        "Tete (Cidade)", "Moatize", "Angónia", "Tsangano", "Mutarara", "Changara",
        "Cahora Bassa", "Magoe", "Zumbo", "Marávia", "Chifunde", "Macanga", "Dôa", "Marara"
    ],
    "Zambézia": [
        "Quelimane (Cidade)", "Mocuba", "Gurué", "Alto Molócue", "Milange", "Morrumbala",
        "Maganja da Costa", "Namacurra", "Nicoadala", "Pebane", "Gilé", "Ile", "Inhassunge",
        "Lugela", "Mopeia", "Chinde", "Derre", "Luabo", "Mulevala", "Molumbo"
    ],
    "Nampula": [
        "Nampula (Cidade)", "Nacala-Porto", "Angoche", "Ilha de Moçambique", "Monapo",
        "Meconta", "Mogovolas", "Murrupula", "Ribaue", "Malema", "Moma", "Mossuril",
        "Muecate", "Nacala-a-Velha", "Eráti", "Memba", "Lalaua", "Larde", "Liúpo"
    ],
    "Niassa": [
        "Lichinga (Cidade)", "Cuamba", "Mandimba", "Lago (Metangula)", "Sanga", "Mavago",
        "Marrupa", "Majune", "Mecanhelas", "Muembe", "Ngauma", "Nipepe", "Chimbonila"
    ],
    "Cabo Delgado": [
        "Pemba (Cidade)", "Montepuez", "Mocímboa da Praia", "Palma", "Mueda", "Chiúre",
        "Ancuabe", "Balama", "Namuno", "Meluco", "Macomia", "Quissanga", "Ibo", "Muidumbe"
    ]
}
'''

# Injetar logo após 'app = Flask(__name__)' se ainda não existir
if "DIVISAO_TERRITORIAL =" not in codigo:
    if "app = Flask(__name__)" in codigo:
        codigo = codigo.replace("app = Flask(__name__)", "app = Flask(__name__)\n" + bloco_divisao, 1)
        print("✓ DIVISAO_TERRITORIAL adicionado logo após a inicialização do Flask!")
    else:
        codigo = bloco_divisao + "\n" + codigo
        print("✓ DIVISAO_TERRITORIAL adicionado ao início do ficheiro app.py!")

with open(caminho_app, 'w', encoding='utf-8') as f:
    f.write(codigo)

# Teste estrito de compilação
try:
    py_compile.compile(caminho_app, doraise=True)
    print("✓ app.py compilado com SUCESSO ABSOLUTO (Zero erros de sintaxe)!")
except Exception as e:
    print(f"Erro detectado em app.py: {e}")
    exit(1)

print("=" * 80)
print(">>> PRONTO! EXECUTE OS COMANDOS GIT PARA ATUALIZAR O RENDER! <<<")
print("=" * 80)