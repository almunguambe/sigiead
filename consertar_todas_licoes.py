import os
import py_compile

print("=" * 80)
print("A CORRIGIR DEFINIÇÃO GLOBAL DE TODAS_LICOES EM APP.PY...")
print("=" * 80)

bloco_licoes = '''
# =============================================================================
# CURRÍCULO DE ENSINO: CONTEÚDO INTEGRAL E PROFUNDO (MANUAL DA IEADAO)
# =============================================================================
CURRICULO_CLASSES = [
    {
        'id_classe': 'classe_1',
        'nome_classe': 'Classe I - Primeiros Passos',
        'descricao': 'Rudimentos da Fé Cristã e Fundamentos da Salvação',
        'licoes': [
            {
                'id': 'c1_l1',
                'numero': 'Lição 1',
                'titulo': 'O Pecado e o Perdão',
                'texto_aureo': 'Porque o salário do pecado é a morte, mas o dom gratuito de Deus é a vida eterna, por Cristo Jesus nosso Senhor. (Rm 6:23)',
                'leitura_base': 'Rm 3:23; Is 59:2; 1Jo 1:7-9; Pv 28:13; Hb 9:22',
                'conteudo': 'Pecar significa literalmente "Errar o Alvo" da Santa Vontade de Deus. Desobedecer é a causa no coração e Transgredir é o efeito visível contra a Lei moral. Na cruz, Cristo operou a Expiação e deu-nos reconciliação.',
                'conteudo_completo': {
                    'introducao': 'Se o pecado não fosse uma triste realidade, seria desnecessária a Salvação consumada por Jesus no Calvário. A doutrina bíblica do pecado e da redenção é o alicerce fundamental para a caminhada cristã.',
                    'pontos_doutrinarios': [
                        {
                            'titulo': '1. O Significado de Pecar: Errar o Alvo',
                            'detalhes': 'Pecar significa literalmente "Errar o Alvo", isto é, errar o alvo de fazer a Vontade de Deus e assim ferirmos a Sua santidade e os Seus propósitos para as nossas vidas.'
                        },
                        {
                            'titulo': '2. Transgressão e Desobediência à Lei Moral de Deus',
                            'detalhes': 'Pecar significa Transgredir a Lei de Deus. Uma pessoa que transgride a Lei Moral de Deus está em desobediência ao Criador (Ex 20:3-17; 1Jo 3:4; Rm 5:14,19; Rm 8:7).\\n\\n• A DIFERENÇA BÍBLICA: Desobedecer é a causa e Transgredir o efeito.\\n• A desobediência está escondida no coração e a transgressão sempre está exposta e manifesta nas ações.'
                        },
                        {
                            'titulo': '3. Lista de Pecados Condenados pelas Escrituras',
                            'detalhes': 'A Bíblia apresenta com clareza as obras da carne que afastam o homem da presença de Deus: Marcos 7:21-22; Romanos 1:29-31; Gálatas 5:19-21; Efésios 5:3; Colossenses 3:5-9.'
                        },
                        {
                            'titulo': '4. A Situação do Homem Perante o Pecado',
                            'tabela': [
                                {'situacao': 'Imoralidade', 'descricao': 'Desfiguração total da imagem divina.', 'versiculos': 'Rm 3:9-12'},
                                {'situacao': 'Inimigo', 'descricao': 'Separação espiritual da presença de Deus.', 'versiculos': 'Is 59:2; Gl 5:4'},
                                {'situacao': 'Morte', 'descricao': 'Separação definitiva e eterna do Criador.', 'versiculos': 'Rm 3:23; Rm 6:23a'}
                            ]
                        },
                        {
                            'titulo': '5. Posição do Homem para se Libertar do Pecado',
                            'detalhes': 'a) Reconhecer que é pecador perante o Deus Santo (Sl 51:3; Rm 3:23);\\nb) Saber que Deus ama o pecador e enviou Seu Filho (Jo 3:16; Rm 5:8);\\nc) Arrepender-se dos seus pecados com genuína dor na alma (Sl 51:1; At 2:37-38);\\nd) Crer e aceitar a Cristo como seu único Salvador e Senhor (Jo 1:12; Jo 3:3,18; At 16:30-31; 1Jo 5:12-13).'
                        },
                        {
                            'titulo': '6. O Perdão de Deus: Expiação e Substituição',
                            'detalhes': 'Deus perdoou-nos em Cristo (Mc 2:5; Lc 7:48; 1Jo 1:9). Cristo ofereceu Expiação e Propiciação — pagou com a Sua própria vida inocente o preço justo da ira santa de Deus. "Sem derramamento de sangue não há remissão" (Hb 9:22).'
                        }
                    ],
                    'proverbio_chave': 'O que encobre as suas transgressões, nunca prosperará; mas o que as confessa e deixa, alcançará misericórdia. (Provérbios 28:13)'
                },
                'questoes': [
                    {'p': 'Qual é a diferença entre desobedecer e transgredir ensinada no Manual?', 'ops': ['Transgredir é no coração e desobedecer é o ato físico.', 'Desobedecer é a causa oculta no coração e transgredir é o efeito exposto.', 'Não há qualquer diferença bíblica.', 'Desobedecer aplica-se só a crianças.'], 'c': 1},
                    {'p': 'O que acontece espiritualmente quando Cristo perdoa o crente segundo a Lição 1?', 'ops': ['Apenas adia o castigo temporal.', 'Não só tira o pecado (o mal), mas coloca algo santo que o substitui (Amor, Graça, Paz e Gozo).', 'Exige pagamento monetário à congregação.', 'Dispensa a necessidade de oração.'], 'c': 1},
                    {'p': 'Conforme a tabela da Situação do Homem perante o Pecado, o que descreve a Imoralidade?', 'ops': ['Desfiguração da imagem divina (Rm 3:9-12).', 'Apenas a perda de bens materiais.', 'Sentimento passageiro de desânimo.', 'Infração de regras civis de trânsito.'], 'c': 0}
                ]
            },
            {
                'id': 'c1_l2',
                'numero': 'Lição 2',
                'titulo': 'Salvação e Senhorio de Cristo',
                'texto_aureo': 'Assim que, se alguém está em Cristo, nova criatura é; as coisas velhas já passaram; eis que tudo se fez novo. (2Co 5:17)',
                'leitura_base': 'Ef 2:8-10; Jo 1:12; 1Co 8:6; Cl 1:21-22',
                'conteudo': 'Somos salvos pela graça por meio da fé, e as obras acompanham como fruto. Cristo quer ser Salvador e dominar como Senhor sobre o trono do nosso coração.',
                'conteudo_completo': {
                    'introducao': 'A salvação é um dom gratuito de Deus por meio da fé e não por obras, para que ninguém se glorie (Ef 2:8-9). As boas obras são o resultado natural e inseparável da salvação operada no coração regenerado.',
                    'pontos_doutrinarios': [
                        {'titulo': '1. Passos para a Filiação Divina', 'detalhes': 'Ouvir a Palavra (Rm 10:17), Crer no que Deus revelou (Jo 3:16), Arrepender-se e Confessar (Rm 10:9; 1Jo 1:9) e Receber a Cristo no trono da vida (Jo 1:12; Ap 3:20).'},
                        {'titulo': '2. Cristo Salvador e Senhor', 'detalhes': 'Cristo não quer apenas livrar-nos da condenação eterna, mas dominar e reger o trono do nosso coração, trazendo equilíbrio e paz interior.'}
                    ],
                    'proverbio_chave': 'Cristo não só pode e quer salvar, mas deseja dominar como Senhor da nossa vida.'
                },
                'questoes': [
                    {'p': 'Qual é a relação entre fé, obras e salvação em Efésios 2:8-10?', 'ops': ['As obras compram o perdão.', 'Somos salvos pela graça por meio da fé, e as obras acompanham como fruto.', 'O crente salvo não precisa de praticar boas obras.', 'A fé sem moralidade basta.'], 'c': 1}
                ]
            },
            {
                'id': 'c1_l5',
                'numero': 'Lição 5',
                'titulo': 'A Bíblia - Manual de Fé dos Cristãos',
                'texto_aureo': 'Lâmpada para os meus pés é a tua palavra e luz para o meu caminho. (Sl 119:105)',
                'leitura_base': '2Tm 3:16; Js 1:8; Sl 1:2; 2Pe 1:21',
                'conteudo': 'A Bíblia contém 66 livros (39 no AT e 27 no NT). O Autor é Deus, o Intérprete é o Espírito Santo e o Tema Central é Jesus Cristo.',
                'conteudo_completo': {
                    'introducao': 'Não se pode conhecer e obedecer a Deus e à Sua santa Vontade sem conhecermos a Sua Palavra revelada. A Bíblia é infalível e a nossa regra soberana de conduta.',
                    'pontos_doutrinarios': [
                        {'titulo': '1. Inspiração e Origem Divina', 'detalhes': 'Cerca de 40 homens escreveram as Escrituras num período de 1600 anos. O Autor é Deus, o Intérprete é o Espírito Santo e o Tema Central é Cristo Jesus.'},
                        {'titulo': '2. Estrutura Canónica', 'detalhes': 'A Bíblia contém 66 livros (39 no Antigo Testamento e 27 no Novo Testamento).'}
                    ],
                    'proverbio_chave': 'Toda a Escritura é divinamente inspirada e proveitosa para ensinar e redarguir. (2Tm 3:16)'
                },
                'questoes': [
                    {'p': 'Quantos livros compõem o cânon bíblico?', 'ops': ['39 no Antigo Testamento e 27 no Novo Testamento (Total: 66 livros).', '46 no AT e 27 no NT.', '30 no AT e 36 no NT.', '50 no AT e 16 no NT.'], 'c': 0}
                ]
            }
        ]
    },
    {
        'id_classe': 'classe_2',
        'nome_classe': 'Classe II - Vida Cristã',
        'descricao': 'Disciplina Espiritual, Oração, Jejum e Mordomia',
        'licoes': [
            {
                'id': 'c2_l1',
                'numero': 'Lição 1',
                'titulo': 'Oração e Jejum',
                'texto_aureo': 'Servindo a Deus em jejuns e orações, de noite e de dia. (Lc 2:37)',
                'leitura_base': '1Ts 5:17; Is 58:6-7; Mt 6:16-18; Zc 7:5',
                'conteudo': 'Orar é um mandamento vital. O jejum quebranta a carne e aguça a sensibilidade espiritual.',
                'conteudo_completo': {
                    'introducao': 'A oração é a respiração da alma e o jejum é o aprimoramento da sensibilidade espiritual através da subjugação do corpo.',
                    'pontos_doutrinarios': [
                        {'titulo': '1. Oração Contínua', 'detalhes': 'Orar é um mandamento vital (1Ts 5:17). O Espírito Santo ajuda nas nossas fraquezas e intercede por nós.'},
                        {'titulo': '2. O Espírito do Jejum Bíblico', 'detalhes': 'O jejum bíblico não serve para ostentação, mas para quebrantamento e aproximação de Deus acompanhado de amor ao próximo (Is 58:6-7).'}
                    ],
                    'proverbio_chave': 'O importante a guardar no jejum é para quem o estamos fazendo.'
                },
                'questoes': [
                    {'p': 'Qual é o verdadeiro espírito do jejum segundo Isaías 58?', 'ops': ['Exibição de piedade aos homens.', 'Quebrantamento para sensibilidade espiritual acompanhado de amor ao próximo.', 'Greve de fome para forçar Deus.', 'Apenas dieta corporal.'], 'c': 1}
                ]
            }
        ]
    },
    {
        'id_classe': 'classe_3',
        'nome_classe': 'Classe III - Maturidade Cristã',
        'descricao': 'Santificação, Consciência do Corpo e Firmeza da Fé',
        'licoes': [
            {
                'id': 'c3_l2',
                'numero': 'Lição 5',
                'titulo': 'Fé: Factos, Não Sentimentos',
                'texto_aureo': 'A fé é o firme fundamento das coisas que se esperam e a prova das coisas que não se vêem. (Hb 11:1)',
                'leitura_base': '2Co 5:7; 2Tm 3:14-16; Jr 17:9',
                'conteudo': 'A Locomotiva é o FACTO (a Palavra de Deus), o Carro de Ligação é a FÉ e o Vagão são os SENTIMENTOS. O comboio anda pela locomotiva, nunca pelo vagão.',
                'conteudo_completo': {
                    'introducao': 'O crente vive por fé na Palavra eterna de Deus e não guiado pelas emoções instáveis da alma.',
                    'pontos_doutrinarios': [
                        {'titulo': '1. A Ilustração do Comboio', 'detalhes': 'A Locomotiva é o FACTO (a Palavra de Deus), o Carro de Ligação é a FÉ e o Vagão Traseiro são os SENTIMENTOS. O comboio anda pela locomotiva, nunca pelo vagão das emoções.'},
                        {'titulo': '2. A Firmeza na Promessa', 'detalhes': 'Mesmo quando não sentimos nada, continuamos firmes porque a Palavra de Deus nunca falha.'}
                    ],
                    'proverbio_chave': 'Porque andamos por fé e não por vista. (2 Coríntios 5:7)'
                },
                'questoes': [
                    {'p': 'Na analogia do comboio da fé, o que representa a Locomotiva?', 'ops': ['Os sentimentos de alegria.', 'O Facto soberano de Deus e as promessas da Sua Palavra.', 'A aprovação dos homens.', 'Os nossos jejuns.'], 'c': 1}
                ]
            }
        ]
    },
    {
        'id_classe': 'classe_4',
        'nome_classe': 'Classe IV - Candidatos ao Baptismo',
        'descricao': 'Ordenanças Sagradas e Preparação Batismal',
        'licoes': [
            {
                'id': 'c4_l1',
                'numero': 'Lição 1',
                'titulo': 'Baptismo nas Águas e Ceia do Senhor',
                'texto_aureo': 'De sorte que foram baptizados os que de bom grado receberam a sua palavra. (At 2:41)',
                'leitura_base': 'Rm 6:4; 1Co 11:23-29; Mt 28:19',
                'conteudo': 'O Baptismo simboliza morte e ressurreição com Cristo. A Santa Ceia contempla Passado Comemorativo, Presente Instrutivo e Futuro Inspirador.',
                'conteudo_completo': {
                    'introducao': 'As duas ordenanças deixadas por Jesus Cristo para a Sua Igreja são o Baptismo nas Águas e a Santa Ceia.',
                    'pontos_doutrinarios': [
                        {'titulo': '1. Baptismo nas Águas', 'detalhes': 'Símbolo da nossa morte e sepultamento para o pecado e ressurreição para Deus ao emergir das águas (Rm 6:4).'},
                        {'titulo': '2. As Três Dimensões da Ceia', 'detalhes': 'Passado Comemorativo (a cruz), Presente Instrutivo (o autoexame de comunhão) e Futuro Inspirador (a Vinda do Senhor).'}
                    ],
                    'proverbio_chave': 'Fazei isto em memória de mim até que Ele venha.'
                },
                'questoes': [
                    {'p': 'Quais são as três dimensões da Ceia do Senhor segundo o Manual?', 'ops': ['Passado Comemorativo, Presente Instrutivo e Futuro Inspirador.', 'Ontem, hoje e amanhã.', 'Nenhum olhar específico.', 'Apenas recordar os discípulos.'], 'c': 0}
                ]
            }
        ]
    }
]

TODAS_LICOES = []
for cl in CURRICULO_CLASSES:
    for lic in cl['licoes']:
        TODAS_LICOES.append({**lic, 'id_classe': cl['id_classe'], 'nome_classe': cl['nome_classe']})
MAPA_LICOES = {l['id']: l for l in TODAS_LICOES}
'''

with open('app.py', 'r', encoding='utf-8') as f:
    codigo_app = f.read()

# Remover quaisquer ocorrências antigas para evitar duplicados fora de ordem
import re
codigo_limpo = re.sub(r'CURRICULO_CLASSES\s*=\s*\[[\s\S]*?MAPA_LICOES\s*=\s*\{l\[\'id\'\]: l for l in TODAS_LICOES\}', '', codigo_app)

# Injetar o bloco logo após a criação da instância do Flask (escopo global de topo)
alvo_topo = "app = Flask(__name__)"
pos = codigo_limpo.find(alvo_topo)

if pos != -1:
    fim_alvo = pos + len(alvo_topo)
    codigo_final = codigo_limpo[:fim_alvo] + "\n" + bloco_licoes + "\n" + codigo_limpo[fim_alvo:]
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(codigo_final)
    print("✓ app.py: 'TODAS_LICOES' injetado no escopo global com sucesso!")
else:
    # Caso não encontre exatamente o alvo, injeta no início
    codigo_final = bloco_licoes + "\n" + codigo_limpo
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(codigo_final)
    print("✓ app.py: 'TODAS_LICOES' injetado no início do ficheiro!")

# Validar sintaxe Python do ficheiro app.py
try:
    py_compile.compile('app.py', doraise=True)
    print("✓ Validação de sintaxe: app.py compilado sem erros!")
except Exception as e:
    print(f"Erro de sintaxe em app.py: {e}")

print("=" * 80)
print(">>> CORREÇÃO CONCLUÍDA! PODE INICIAR O SERVIDOR COM: py app.py <<<")
print("=" * 80)