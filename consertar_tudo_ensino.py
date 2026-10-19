import os
import py_compile
import jinja2

print("=" * 80)
print("A CORRIGIR ENSINO TEOLÓGICO, NOTAS EXPLICATIVAS E TEMPLATES JINJA2...")
print("=" * 80)

# =============================================================================
# 1. CRIAR ENSINO_DADOS.PY COM TODAS AS LIÇÕES E NOTAS EXPLICATIVAS PROFUNDAS
# =============================================================================
conteudo_ensino_dados = '''# -*- coding: utf-8 -*-
"""
MÓDULO DE CURRÍCULO E DOUTRINA - MANUAL OFICIAL DA IEADAO
Assembleia de Deus em Moçambique
"""

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
                'texto_aureo': 'Porque o salário do pecado é a morte, mas o dom gratuito de Deus é a vida eterna, por Cristo Jesus nosso Senhor. (Romanos 6:23)',
                'leitura_base': 'Rm 3:23; Is 59:2; 1Jo 1:7-9; Pv 28:13; Hb 9:22',
                'conteudo': 'Pecar significa literalmente "Errar o Alvo" da Santa Vontade de Deus. Desobedecer é a causa no coração e Transgredir é o efeito visível contra a Lei moral. Na cruz, Cristo operou a Expiação e deu reconciliação plena.',
                'conteudo_completo': {
                    'introducao': 'Se o pecado não fosse uma realidade espiritual trágica e destruidora, seria desnecessária a Salvação consumada por Cristo Jesus no Calvário. Para o novo crente, compreender o que é o pecado e como Deus o perdoa é o alicerce essencial para nunca mais viver debaixo da culpa e da acusação do inimigo.',
                    'pontos_doutrinarios': [
                        {
                            'titulo': '1. O Significado Bíblico de Pecar: Errar o Alvo Divino',
                            'detalhes': 'Na língua original das Escrituras (grego "Hamartia"), pecar significa literalmente "Errar o Alvo". Não se trata de uma simples fraqueza humana ou acidente biológico; trata-se de errar o alvo soberano da Santa Vontade de Deus para a nossa existência e ferir a Sua santidade.',
                            'nota_explicativa': 'Para o novo crente: Deus criou o ser humano com um propósito nobre de comunhão e santidade. Quando pecamos, é como se um arqueiro atirasse uma flecha para o lado oposto do alvo pretendido pelo Criador.'
                        },
                        {
                            'titulo': '2. Desobediência no Coração e Transgressão nos Atos',
                            'detalhes': 'A Bíblia estabelece uma distinção essencial:\\n• Desobedecer é a CAUSA que nasce escondida no interior do coração (Ex 20:3-17; Rm 8:7).\\n• Transgredir é o EFEITO prático: é o ato de pisar ou ultrapassar conscientemente os limites da Lei Moral de Deus.\\nO pecado começa sempre no silêncio do pensamento antes de se manifestar em palavras ou atitudes visíveis.',
                            'nota_explicativa': 'Vigilância diária: Vigie os seus pensamentos e desejos secretos. Se cortarmos a semente da desobediência no coração através da oração, ela nunca chegará a florescer na árvore amarga da transgressão pública.'
                        },
                        {
                            'titulo': '3. A Situação Trágica do Homem perante a Lei de Deus',
                            'tabela': [
                                {'situacao': 'Imoralidade Total', 'descricao': 'Desfiguração e corrupção da imagem moral de Deus na alma.', 'versiculos': 'Rm 3:9-12'},
                                {'situacao': 'Inimizade e Separação', 'descricao': 'Abismo espiritual que corta a comunhão com a presença do Senhor.', 'versiculos': 'Is 59:2; Gl 5:4'},
                                {'situacao': 'Morte Espiritual e Eterna', 'descricao': 'Condenação definitiva e separação permanente do Criador.', 'versiculos': 'Rm 3:23; Rm 6:23'}
                            ],
                            'detalhes': 'Diante do pecado, nenhum homem possui recursos próprios, moralidade, ritos tradicionais ou esmolas para se justificar perante a justiça divina.',
                            'nota_explicativa': 'Lembre-se: Diante de Deus, a moralidade humana sem Cristo é insuficiente. Todos estávamos no mesmo abismo até que a misericórdia de Deus nos alcançou pelo sacrifício da cruz.'
                        },
                        {
                            'titulo': '4. Os Passos Bíblicos da Libertação do Pecado',
                            'detalhes': 'a) Reconhecer humildemente a sua condição de pecador (Sl 51:3; Rm 3:23);\\nb) Compreender que Deus o ama de forma incondicional e enviou o Seu Filho (Jo 3:16; Rm 5:8);\\nc) Arrepender-se com dor sincera na alma e decisão firme de mudança (Sl 51:1; At 2:37-38);\\nd) Crer e receber a Jesus como único Salvador e Senhor (Jo 1:12; At 16:30-31; 1Jo 5:12-13).',
                            'nota_explicativa': 'Diferença entre Remorso e Arrependimento: O remorso chora por medo do castigo ou vergonha pública (como Judas, que se enforcou sem perdão). O arrependimento bíblico (Metanoia) chora por ter ofendido a Deus, abandona a prática errada e corre para os braços de Cristo (como Pedro, que foi restaurado).'
                        },
                        {
                            'titulo': '5. O Perdão Divino: Expiação, Propiciação e a Regra de Ouro da Graça',
                            'detalhes': 'O perdão de Deus não é vista grossa: custou a vida do Cordeiro inocente (Hb 9:22). Cristo ofereceu Expiação (cobriu as nossas faltas) e Propiciação (saciou a santa justiça de Deus no Calvário).\\n\\nA REGRA DE OURO DA GRAÇA: Quando Cristo perdoa, Ele não apenas cancela o pecado do passado; Ele habita no coração e coloca virtudes santas que substituem o mal: Amor, Graça, Paz, Pureza e Gozo no Espírito Santo!',
                            'nota_explicativa': 'Consolo para o seu coração: O sangue de Jesus tem poder suficiente para limpar qualquer pecado confessado (1Jo 1:7-9). Se você já se arrependeu e confessou, rejeite qualquer acusação do maligno: em Cristo, você é plenamente perdoado e aceite pelo Pai celeste!'
                        }
                    ],
                    'proverbio_chave': 'O que encobre as suas transgressões nunca prosperará; mas o que as confessa e deixa, alcançará misericórdia. (Provérbios 28:13)'
                },
                'questoes': [
                    {'p': 'Qual é a diferença bíblica entre desobedecer e transgredir ensinada na Lição 1?', 'ops': ['Transgredir é apenas infantil e desobedecer é crime civil.', 'Desobedecer é a causa oculta no coração e transgredir é o efeito manifesto em ações.', 'Não há qualquer distinção nas Escrituras.', 'Desobedecer aplica-se apenas aos israelitas.'], 'c': 1},
                    {'p': 'O que acontece espiritualmente pela "Regra de Ouro da Graça" quando Cristo perdoa o crente?', 'ops': ['Apenas suspende temporariamente o castigo.', 'Não só perdoa o mal, mas implanta no coração Amor, Graça, Paz e Gozo no Espírito Santo.', 'Exige pagamento monetário imediato.', 'Dispensa a necessidade de oração.'], 'c': 1},
                    {'p': 'Qual a diferença crucial entre remorso humano e arrependimento bíblico?', 'ops': ['O remorso é bíblico e o arrependimento é pagão.', 'O remorso tem medo das consequências ou vergonha; o arrependimento sente dor por ofender a Deus e abandona o pecado.', 'Não há diferença entre Judas e Pedro.', 'Remorso só acontece na velhice.'], 'c': 1}
                ]
            },
            {
                'id': 'c1_l2',
                'numero': 'Lição 2',
                'titulo': 'Salvação e Senhorio de Cristo',
                'texto_aureo': 'Assim que, se alguém está em Cristo, nova criatura é; as coisas velhas já passaram; eis que tudo se fez novo. (2 Coríntios 5:17)',
                'leitura_base': 'Ef 2:8-10; Jo 1:12; 1Co 8:6; Cl 1:21-22; Lucas 6:46; Romanos 10:9-10',
                'conteudo': 'A salvação é um dom gratuito da graça recebido mediante a fé, e não mérito de obras humanas. Contudo, ser salvo exige render o trono do coração a Cristo: Ele não quer ser apenas o Salvador do inferno, mas o Senhor soberano de toda a nossa conduta diária.',
                'conteudo_completo': {
                    'introducao': 'A salvação não é uma conquista humana, um troféu de boa conduta moral ou um mérito religioso: é um presente inestimável e imerecido concedido por Deus através da morte vicária e ressurreição de Jesus Cristo. Uma vez salvos, entramos numa nova realidade onde Cristo passa a governar a nossa vontade com amor, santidade e direção.',
                    'pontos_doutrinarios': [
                        {
                            'titulo': '1. A Salvação é pela Graça Mediante a Fé, Não por Obras (Efésios 2:8-10)',
                            'detalhes': 'A Escritura declara enfaticamente: "Porque pela graça sois salvos, por meio da fé; e isto não vem de vós, é dom de Deus. Não vem das obras, para que ninguém se glorie." (Ef 2:8-9).\\n\\n• GRAÇA significa favor imerecido: Deus nos deu aquilo que não tínhamos como pagar.\\n• FÉ é a mão vazia do pecador que se estende para receber a dádiva da vida eterna.\\n• AS BOAS OBRAS não são a raiz ou causa da salvação, mas sim o seu fruto inseparável. Somos salvos não PELAS obras, mas PARA as boas obras que Deus preparou para andarmos nelas (Ef 2:10).',
                            'nota_explicativa': 'Nota para o novo na fé: Nunca pense que você precisa "limpar-se sozinho" antes de vir a Jesus. Ninguém toma banho para depois entrar na água; é a água que limpa o corpo! Venha a Cristo tal como está: a salvação é pela graça mediante a fé, e Ele mesmo transformará os seus hábitos e desejos pelo Seu Santo Espírito.'
                        },
                        {
                            'titulo': '2. Os 5 Passos Bíblicos da Apropriação da Salvação',
                            'detalhes': 'Como uma pessoa perdida torna-se legitimamente filha de Deus?\\n\\n1. OUVIR com reverência a Palavra de Deus (Romanos 10:17 - A fé vem pelo ouvir da Palavra de Cristo);\\n2. CRER de todo o coração no sacrifício redentor de Jesus (João 3:16; Hebreus 11:6);\\n3. ARREPENDER-SE com mudança sincera de mente e abandono do pecado (Atos 2:38; 3:19);\\n4. CONFESSAR publicamente a Jesus perante os homens (Romanos 10:9-10 - "Com o coração se crê para justiça, e com a boca se faz confissão para a salvação");\\n5. RECEBER A CRISTO no trono da existência (João 1:12 - "A todos quantos o receberam, deu-lhes o poder de serem feitos filhos de Deus").',
                            'nota_explicativa': 'Atenção aos novos convertidos: Não basta crer em Jesus apenas na mente ou concordar que Ele existiu como figura histórica. Até os demónios creem e estremecem (Tg 2:19). Crer para salvação significa depositar a sua confiança total em Jesus, entregando-Lhe o rumo do seu presente e da sua eternidade.'
                        },
                        {
                            'titulo': '3. A Distinção Crucial: Cristo como Salvador versus Cristo como SENHOR',
                            'detalhes': 'Esta é uma das maiores falhas doutrinárias dos nossos dias: muitos desejam Jesus apenas como "Salvador" (querem ser livres do fogo do inferno, da doença ou da pobreza), mas recusam-se a recebê-Lo como "SENHOR" (*Kyrios* em grego: Dono absoluto, Rei soberano, Comandante e Governador).\\n\\n• Jesus pergunta: "Por que me chamais Senhor, Senhor, e não fazeis o que eu digo?" (Lucas 6:46).\\n• Se Cristo é o seu Senhor, Ele é o dono da sua boca (rejeitando a mentira e a fofoca), dono do seu corpo (rejeitando a fornicação, feitiçaria e bebidas alcoólicas), dono do seu dinheiro (sendo fiel nos dízimos e ofertas com alegria) e dono das suas decisões familiares.',
                            'nota_explicativa': 'A Ilustração do Trono do Coração: Imagine o seu coração como uma sala com um único trono. Existem apenas duas posições:\\n1. O "Eu" sentado no trono e Jesus de pé num canto (o crente vive segundo as suas próprias paixões mundanas e colhe frustração).\\n2. Cristo sentado no trono supremo e o "Eu" ajoelhado aos Seus pés obedecendo (a vida vive em plenitude de comunhão, paz profunda e direção do Espírito Santo). Quem está no trono do seu coração hoje?'
                        },
                        {
                            'titulo': '4. A Nova Criatura e a Certeza da Vida Eterna (2 Coríntios 5:17)',
                            'detalhes': 'A salvação gera uma transformação sobrenatural no interior do crente: a REGENERAÇÃO. O novo convertido não é uma versão reformada ou remendada do velho homem; ele é uma NOVA CRIATURA: as coisas velhas (vícios, ódios, feitiçarias, imoralidades) passaram; eis que tudo se fez novo!\\n\\n• O Espírito Santo passa a habitar dentro de si e testifica ao seu espírito que você é filho de Deus (Romanos 8:16).\\n• A certeza da salvação não se baseia em sentimentos passageiros, mas na promessa infalível de Cristo: "Aquele que crê no Filho tem a vida eterna" (João 3:36; 1 João 5:11-13).',
                            'nota_explicativa': 'Conselho Pastoral para a sua caminhada diária: Quando os velhos amigos do mundo o convidarem para os antigos caminhos do pecado, declare com mansidão e firmeza: "Aquele homem velho morreu no dia em que entreguei a minha vida a Jesus. Hoje sou uma nova criatura e sirvo a um novo Senhor!".'
                        }
                    ],
                    'proverbio_chave': 'Cristo não quer apenas ser o Salvador do seu passado; Ele deseja reinar como Senhor soberano do seu presente e do seu futuro.'
                },
                'questoes': [
                    {'p': 'Qual é a relação bíblica correta entre Fé, Obras e Salvação (Efésios 2:8-10)?', 'ops': ['As boas obras compram o direito de entrada no céu.', 'Somos salvos pela graça por meio da fé; as boas obras são o resultado e fruto inseparável da salvação.', 'Quem tem fé não precisa de praticar boas obras.', 'A salvação é dividida: 50% de Cristo e 50% de ritos humanos.'], 'c': 1},
                    {'p': 'O que significa na prática aceitar Jesus Cristo não apenas como Salvador, mas como SENHOR (Kyrios)?', 'ops': ['Apenas frequentar o templo aos domingos.', 'Rendermo-nos a Ele como Dono e Rei absoluto, obedecendo à Sua Palavra em todas as decisões da vida (família, finanças, hábitos e palavras).', 'Exigir que Deus cumpra todos os nossos caprichos.', 'Decorar os nomes dos 12 apóstolos.'], 'c': 1},
                    {'p': 'De acordo com 2 Coríntios 5:17, o que ocorre no coração daquele que está genuinamente em Cristo?', 'ops': ['Uma simples reforma moral passageira.', 'Regeneração espiritual completa: nova criatura é, as coisas velhas já passaram e tudo se fez novo.', 'Permanece exatamente igual com os mesmos hábitos do mundo.', 'Perde a alegria de viver.'], 'c': 1}
                ]
            },
            {
                'id': 'c1_l5',
                'numero': 'Lição 5',
                'titulo': 'A Bíblia - Manual de Fé e Conduta Cristã',
                'texto_aureo': 'Lâmpada para os meus pés é a tua palavra e luz para o meu caminho. (Salmo 119:105)',
                'leitura_base': '2Tm 3:16-17; Josué 1:8; Sl 1:1-3; 2Pe 1:20-21; Hb 4:12',
                'conteudo': 'A Bíblia Sagrada é a revelação inerrante e infalível de Deus para a humanidade. Composta por 66 livros (39 no Antigo Testamento e 27 no Novo Testamento), ela é a nossa única regra de fé e prática superior a qualquer tradição humana.',
                'conteudo_completo': {
                    'introducao': 'Não é possível crescer na fé cristã nem conhecer a vontade de Deus sem o contato constante com as Sagradas Escrituras. A Bíblia é o alimento da alma e a bússola que guia o crente em segurança pelas tempestades deste mundo.',
                    'pontos_doutrinarios': [
                        {
                            'titulo': '1. Inspiração e Origem Divina das Escrituras',
                            'detalhes': 'A Bíblia não nasceu da mente de pensadores humanos. Foi escrita por cerca de 40 homens (reis, pescadores, pastores e médicos) durante um período de aproximadamente 1600 anos, em três línguas (hebraico, aramaico e grego), e mantém perfeita unidade doutrinária sem contradições.\\n\\n• O AUTOR soberano é Deus;\\n• O INTÉRPRETE infalível é o Espírito Santo;\\n• O TEMA CENTRAL de Gênesis ao Apocalipse é Cristo Jesus e a redenção humana.',
                            'nota_explicativa': 'Como ler a Bíblia todos os dias: Antes de abrir a Bíblia, faça sempre uma oração breve: "Senhor Espírito Santo, ilumina o meu entendimento para que eu compreenda a Tua Palavra e a aplique na minha vida hoje". Comece lendo os Evangelhos (Mateus, Marcos, Lucas e João).'
                        },
                        {
                            'titulo': '2. Estrutura Canónica e Divisão das Escrituras',
                            'detalhes': 'A Bíblia Cristã contém 66 livros divididos em dois grandes testamentos:\\n• Antigo Testamento (39 Livros): Lei (Pentateuco), Históricos, Poéticos e Proféticos.\\n• Novo Testamento (27 Livros): Evangelhos, Histórico (Atos), Epístolas Paulinas, Epístolas Gerais e Revelação (Apocalipse).\\nNenhum crente pode retirar ou acrescentar palavras ao texto canónico sagrado (Ap 22:18-19).',
                            'nota_explicativa': 'A Bíblia acima das tradições humanas: Nenhum costume cultural, sonho de falsos profetas ou tradição religiosa tem autoridade igual ou superior à Bíblia Sagrada. Tudo o que confrontar a Palavra de Deus deve ser rejeitado pelo crente com mansidão e firmeza.'
                        }
                    ],
                    'proverbio_chave': 'Toda a Escritura é divinamente inspirada por Deus e proveitosa para ensinar, redarguir, corrigir e instruir em justiça. (2 Timóteo 3:16)'
                },
                'questoes': [
                    {'p': 'Quantos livros compõem o cânon bíblico oficial aceito pela Igreja?', 'ops': ['39 no Antigo Testamento e 27 no Novo Testamento (Total: 66 livros).', '46 no AT e 27 no NT.', '50 no AT e 20 no NT.', '66 no AT e 66 no NT.'], 'c': 0},
                    {'p': 'Qual a postura do crente quando uma tradição humana contradiz a Bíblia?', 'ops': ['A tradição humana fica sempre acima das Escrituras.', 'A Bíblia Sagrada é a autoridade suprema e inerrante; qualquer ensinamento oposto deve ser rejeitado.', 'Deve-se misturar os dois costumes.', 'Depende da estação do ano.'], 'c': 1}
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
                'titulo': 'Oração e Jejum: O Oxigênio da Alma',
                'texto_aureo': 'Orai sem cessar. Em tudo dai graças, porque esta é a vontade de Deus em Cristo Jesus para convosco. (1 Tessalonicenses 5:17-18)',
                'leitura_base': '1Ts 5:17; Is 58:6-7; Mt 6:5-18; Lc 18:1; Zc 7:5',
                'conteudo': 'A oração é a conversa confiante do filho com o seu Pai celestial. O jejum não compra a vontade de Deus nem é greve de fome; é a disciplina sagrada de submeter os apetites da carne para aguçar a sensibilidade do espírito.',
                'conteudo_completo': {
                    'introducao': 'Uma vida cristã sem oração constante é como uma árvore sem raízes. O novo crente aprende a falar com Deus como uma criança fala com o pai que a ama.',
                    'pontos_doutrinarios': [
                        {
                            'titulo': '1. A Prática da Oração Contínua e os Elementos da Comunhão',
                            'detalhes': 'Orar é respirar espiritualmente. A oração bíblica segue o equilíbrio ensinado por Jesus na Oração Modelo (Mateus 6:9-13):\\n• Adoração ao Santo Nome do Pai;\\n• Submissão à Sua soberana Vontade;\\n• Petição pelas necessidades diárias do pão;\\n• Confissão de pecados e perdão sincero aos irmãos;\\n• Proteção contra as ciladas do maligno.',
                            'nota_explicativa': 'Como orar diariamente: Deus não procura palavras rebuscadas ou rituais mecânicos decorados. Fale com Deus com sinceridade, no quarto secreto, expondo as suas fraquezas, dores e louvores.'
                        },
                        {
                            'titulo': '2. O Verdadeiro Jejum Bíblico (Isaías 58)',
                            'detalhes': 'O jejum bíblico não tem o objetivo de forçar ou chantagear Deus para obter bênçãos materiais. O seu propósito é quebrantar a carne, humilhar o orgulho e intensificar a busca espiritual.\\nO jejum que agrada a Deus segundo Isaías 58 vem acompanhado de justiça, libertação de opressões, amor fraternal e partilha de alimento com o necessitado.',
                            'nota_explicativa': 'Conselho prático de jejum: Comece jejuando pequenas refeições (ex: o pequeno-almoço matinal até ao meio-dia), dedicando esse tempo de fome à oração e leitura bíblica fervorosa.'
                        }
                    ],
                    'proverbio_chave': 'O importante no jejum não é o que o seu estômago deixa de comer, mas sim para quem o seu coração se está a consagrar.'
                },
                'questoes': [
                    {'p': 'Qual é o verdadeiro espírito e propósito do jejum segundo Isaías 58?', 'ops': ['Uma greve de fome para obrigar Deus a conceder riquezas.', 'Quebrantamento da carne para sensibilidade espiritual, acompanhado de arrependimento e atos de misericórdia e amor.', 'Uma dieta física estética de emagrecimento.', 'Uma exibição de santidade para impressionar os homens.'], 'c': 1}
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
                'titulo': 'Fé: Fundamentada em Factos, Não em Sentimentos',
                'texto_aureo': 'Ora, a fé é o firme fundamento das coisas que se esperam, e a prova das coisas que se não veem. (Hebreus 11:1)',
                'leitura_base': '2Co 5:7; 2Tm 3:14-16; Jr 17:9; Rm 8:38-39',
                'conteudo': 'O crente vive alicerçado nas promessas imutáveis da Palavra de Deus e não na instabilidade das emoções da alma. A fé segura a âncora da verdade quando as tempestades dos sentimentos se levantam.',
                'conteudo_completo': {
                    'introducao': 'Um dos maiores perigos na caminhada cristã é avaliar a comunhão com Deus pelo modo como nos "sentimos" em determinado dia. Sentimentos oscilam; a Palavra de Deus permanece para sempre.',
                    'pontos_doutrinarios': [
                        {
                            'titulo': '1. A Ilustração do Comboio: Facto, Fé e Sentimentos',
                            'detalhes': 'Imagine um comboio formado por três partes:\\n• A LOCOMOTIVA é o FACTO: a Pessoa de Deus e as promessas eternas da Sua Palavra na Bíblia;\\n• O CARRO DE LIGAÇÃO é a FÉ: a nossa confiança plena e inabalável na Locomotiva;\\n• O VAGÃO TRASEIRO são os SENTIMENTOS: alegria, lágrimas, arrepios ou tristeza passageira.\\n\\nO comboio anda pela força motriz da Locomotiva (o Facto da Palavra), nunca pela instabilidade do vagão traseiro (os sentimentos).',
                            'nota_explicativa': 'Quando não sentir arrepios: Mesmo num dia em que você se sinta desanimado, cansado ou frio, lembre-se: Deus continua no trono, o seu nome continua escrito no Livro da Vida e o sacrifício de Jesus não perdeu a eficácia! Andamos por fé e não por vista ou emoção (2Co 5:7).'
                        }
                    ],
                    'proverbio_chave': 'Porque andamos por fé, e não por vista. (2 Coríntios 5:7)'
                },
                'questoes': [
                    {'p': 'Na clássica ilustração do comboio da fé, o que representa a Locomotiva?', 'ops': ['Os nossos sentimentos e emoções variáveis.', 'O Facto eterno de Deus e a autoridade imutável das promessas da Sua Palavra.', 'A aprovação e elogios dos parentes.', 'Os nossos jejuns prolongados.'], 'c': 1}
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
                'texto_aureo': 'De sorte que foram baptizados os que de bom grado receberam a sua palavra. (Atos 2:41)',
                'leitura_base': 'Rm 6:3-4; 1Co 11:23-29; Mt 28:19; Cl 2:12',
                'conteudo': 'As duas ordenanças deixadas por Jesus Cristo para a Sua Igreja são o Baptismo nas Águas por imersão (testemunho público de morte e ressurreição) e a Santa Ceia (memorial solene do sacrifício até que Ele venha).',
                'conteudo_completo': {
                    'introducao': 'O baptismo não é salvação por si mesmo, mas é o testemunho público e solene de que o crente já pertence a Jesus e morreu para o império das trevas.',
                    'pontos_doutrinarios': [
                        {
                            'titulo': '1. O Significado Teológico do Baptismo nas Águas por Imersão',
                            'detalhes': 'A palavra baptizar no original significa "imergir, submergir totalmente". Ao descer às águas, o candidato sepulta publicamente o velho homem, os velhos vícios e o passado sem Cristo; ao emergir das águas, ressurge vitorioso para andar em novidade de vida para a glória de Deus (Romanos 6:3-4).',
                            'nota_explicativa': 'Passo de obediência sagrada: O baptismo nas águas é o "casamento público" da sua alma com Cristo. A aliança já foi feita no coração; o baptismo declara perante a Igreja, os homens e os principados espirituais que você agora pertence à família de Deus.'
                        },
                        {
                            'titulo': '2. As Três Dimensões Espirituais da Santa Ceia do Senhor (1 Coríntios 11:23-29)',
                            'detalhes': '• PASSADO COMEMORATIVO: Olhamos para trás, para a Cruz do Calvário, lembrando com reverência o corpo moído e o sangue derramado de Jesus;\\n• PRESENTE INSTRUTIVO: Autoexame interior ("Examine-se, pois, o homem a si mesmo") para renovar a comunhão com Deus e a reconciliação com o próximo;\\n• FUTURO INSPIRADOR: Olhamos com santa esperança para a frente: "Fazei isto... até que Ele venha!" Ceamos anunciando o regresso iminente de Cristo em glória!',
                            'nota_explicativa': 'Autoexame na Ceia: Participar da mesa do Senhor não exige perfeição humana, mas exige sinceridade, arrependimento de coração e estar em paz com os seus irmãos e familiares.'
                        }
                    ],
                    'proverbio_chave': 'Fazei isto em memória de mim até que Ele venha.'
                },
                'questoes': [
                    {'p': 'Quais são as três dimensões espirituais da Ceia do Senhor ensinadas no Manual da IEADAO?', 'ops': ['Passado Comemorativo, Presente Instrutivo e Futuro Inspirador.', 'Tristeza de ontem, trabalho de hoje e descanso de amanhã.', 'Nenhuma dimensão específica.', 'Apenas recordar os discípulos primitivos.'], 'c': 0}
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

with open('ensino_dados.py', 'w', encoding='utf-8') as f:
    f.write(conteudo_ensino_dados)
print("✓ ensino_dados.py criado com sucesso!")

# =============================================================================
# 2. REPARAR APP.PY: LIMPAR DEFINIÇÕES QUEBRADAS E IMPORTAR DE ENSINO_DADOS
# =============================================================================
with open('app.py', 'r', encoding='utf-8') as f:
    app_text = f.read()

import re

# Remover qualquer bloco anterior quebrado de CURRICULO_CLASSES em app.py
app_text = re.sub(
    r'CURRICULO_CLASSES\s*=\s*\[[\s\S]*?MAPA_LICOES\s*=\s*\{l\[\'id\'\]:\s*l\s*for\s*l\s*in\s*TODAS_LICOES\}',
    '# Curriculo importado de ensino_dados.py',
    app_text
)

# Se ainda não tiver o import, adicionar logo após a inicialização do Flask
if 'from ensino_dados import CURRICULO_CLASSES' not in app_text:
    app_text = app_text.replace(
        "app = Flask(__name__)",
        "app = Flask(__name__)\nfrom ensino_dados import CURRICULO_CLASSES, TODAS_LICOES, MAPA_LICOES"
    )

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_text)

try:
    py_compile.compile('app.py', doraise=True)
    print("✓ app.py compilado com ZERO erros de sintaxe!")
except Exception as e:
    print(f"Erro em app.py: {e}")
    exit(1)

# =============================================================================
# 3. RECONSTRUIR TEMPLATES/PORTAL_ALUNO.HTML COM VALIDAÇÃO JINJA2 COMPLETA
# =============================================================================
portal_html_limpo = """<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portal do Aluno - IEAD Moçambique</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .card-bg { background: linear-gradient(135deg, #090d16 0%, #1e1b4b 60%, #312e81 100%); }
        table, th, td { border: 1px solid #cbd5e1 !important; }
    </style>
</head>
<body class="bg-slate-100 text-slate-800 font-sans min-h-screen flex flex-col">

    <header class="bg-slate-900 text-white px-6 py-4 flex justify-between items-center shadow-lg border-b border-indigo-900 sticky top-0 z-50">
        <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-2xl bg-gradient-to-tr from-indigo-500 to-amber-400 flex items-center justify-center font-black text-xl shadow">
                AD
            </div>
            <div>
                <h1 class="font-black text-sm uppercase tracking-wider">ESCOLA DE INTEGRAÇÃO & DOUTRINA</h1>
                <p class="text-[11px] text-amber-300 font-bold">Assembleia de Deus • Sede Regional de Chicuque</p>
            </div>
        </div>

        <div class="flex items-center gap-4 text-xs">
            <div class="text-right">
                <span class="text-[10px] text-slate-400 block uppercase font-bold">Aluno Conectado</span>
                <span class="font-extrabold text-white">{{ aluno.nome_aluno }}</span>
            </div>
            <a href="/logout" class="bg-rose-600 hover:bg-rose-700 text-white px-3.5 py-1.5 rounded-xl font-bold shadow text-xs transition">
                Sair
            </a>
        </div>
    </header>

    <main class="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">

        <div class="card-bg text-white p-6 sm:p-8 rounded-3xl shadow-xl flex flex-col lg:flex-row lg:items-center justify-between gap-6">
            <div class="space-y-2">
                <span class="bg-amber-400 text-slate-950 text-[10px] font-black uppercase px-3 py-1 rounded-full shadow">
                    Plataforma Oficial de Formação Ministerial
                </span>
                <h2 class="text-2xl sm:text-3xl font-black">
                    Graça e Paz, {{ aluno.nome_aluno }}!
                </h2>
                <p class="text-xs sm:text-sm text-indigo-200 max-w-2xl leading-relaxed">
                    Você está estudando o <b>Manual Oficial de Candidatos e Integração da IEADAO</b> na íntegra. Leia com atenção as notas explicativas, elabore o seu resumo e responda ao teste teológico.
                </p>
            </div>

            <div class="bg-white/10 backdrop-blur-md border border-white/20 p-5 rounded-3xl text-center shrink-0 w-full lg:w-72 space-y-3">
                <div>
                    <span class="text-[10px] uppercase font-bold text-indigo-200 block">Aproveitamento Curricular</span>
                    <div class="text-3xl font-black mt-0.5 text-amber-300">
                        {{ "%.1f"|format(aluno.aproveitamento or 0) }}%
                    </div>
                    <div class="w-full bg-slate-900/60 h-2 rounded-full overflow-hidden my-2 border border-white/10">
                        <div class="bg-emerald-400 h-full rounded-full transition-all duration-700" style="width: {{ [aluno.aproveitamento or 0, 100]|min }}%"></div>
                    </div>
                </div>

                <div class="border-t border-white/10 pt-2 text-left bg-white/5 p-2.5 rounded-xl">
                    <span class="text-[9px] uppercase font-bold text-amber-300 block">👨‍🏫 Instrutor / Pai na Fé</span>
                    <span class="text-xs font-black text-white block truncate">{{ aluno.professor or "Pastor Dirigente" }}</span>
                    <span class="text-[10px] text-indigo-200 block mt-0.5">{{ aluno.classe }}</span>
                </div>

                {% if todas_concluidas %}
                <a href="/ensino/exame_final" class="block w-full py-2 bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-black rounded-xl text-xs shadow transition">
                    🏆 Fazer Exame Final & Obter Certificado
                </a>
                {% endif %}
            </div>
        </div>

        {% if request.args.get('sucesso_aprovado') %}
        <div class="bg-emerald-50 border-2 border-emerald-400 p-4 rounded-2xl flex items-center justify-between text-emerald-900 text-xs font-bold shadow">
            <span>🎉 Glória a Deus! Concluiu a lição anterior com aproveitamento maior ou igual a 70%! A lição seguinte foi destravada para o seu estudo!</span>
        </div>
        {% endif %}

        {% if request.args.get('nota_resultado') %}
        <div class="bg-amber-50 border-2 border-amber-400 p-4 rounded-2xl flex items-center justify-between text-amber-900 text-xs font-bold shadow">
            <span>⚠️ Atingiu {{ request.args.get('nota_resultado') }}%. É necessário no mínimo 70% para destrancar a próxima lição. Reveja os tópicos e repita o teste abaixo.</span>
        </div>
        {% endif %}

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">

            <!-- COLUNA ESQUERDA: LISTA DE CLASSES E LIÇÕES -->
            <div class="lg:col-span-4 space-y-4">
                <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200">
                    <h3 class="font-extrabold text-sm uppercase text-slate-900 mb-3 border-b pb-2 flex items-center gap-2">
                        <span>📚</span> Currículo Oficial por Classes
                    </h3>

                    <div class="space-y-4">
                        {% for classe in curriculo %}
                        <div class="border border-slate-200 rounded-xl p-3 bg-slate-50">
                            <div class="font-black text-xs text-indigo-950 uppercase mb-1">
                                {{ classe.nome_classe }}
                            </div>
                            <p class="text-[10px] text-slate-500 mb-2.5">{{ classe.descricao }}</p>

                            <div class="space-y-1.5">
                                {% for l in classe.licoes %}
                                {% set st = licoes_status[l.id] %}
                                
                                {% if st.status == 'concluida' %}
                                <a href="/ensino/aulas?licao={{ l.id }}" class="flex items-center justify-between p-2 rounded-lg text-xs font-bold transition {% if licao.id == l.id %}bg-indigo-600 text-white{% else %}bg-emerald-50 text-emerald-900 hover:bg-emerald-100{% endif %}">
                                    <span class="truncate">✅ {{ l.numero }}: {{ l.titulo }}</span>
                                    <span class="text-[10px] bg-emerald-200 text-emerald-950 px-2 py-0.5 rounded-full font-black ml-1">{{ st.nota }}%</span>
                                </a>
                                {% elif st.status == 'em_estudo' %}
                                <a href="/ensino/aulas?licao={{ l.id }}" class="flex items-center justify-between p-2 rounded-lg text-xs font-bold transition {% if licao.id == l.id %}bg-indigo-600 text-white shadow-md{% else %}bg-blue-100 text-blue-900 border border-blue-300 hover:bg-blue-200{% endif %}">
                                    <span class="truncate">📖 {{ l.numero }}: {{ l.titulo }}</span>
                                    <span class="text-[10px] bg-amber-400 text-slate-950 px-2 py-0.5 rounded-full font-black ml-1">EM ESTUDO</span>
                                </a>
                                {% else %}
                                <div class="flex items-center justify-between p-2 rounded-lg text-xs text-slate-400 bg-slate-100 cursor-not-allowed">
                                    <span class="truncate">🔒 {{ l.numero }}: {{ l.titulo }}</span>
                                    <span class="text-[10px] text-slate-400">Trancada</span>
                                </div>
                                {% endif %}
                                {% endfor %}
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>

            <!-- COLUNA DIREITA: CONTEÚDO PROFUNDO COM NOTAS EXPLICATIVAS -->
            <div class="lg:col-span-8 space-y-6">

                <div class="bg-white p-6 sm:p-8 rounded-3xl shadow-sm border border-slate-200 space-y-6">
                    <div class="border-b border-slate-100 pb-4">
                        <span class="text-xs font-black uppercase text-indigo-600 tracking-wider">
                            ETAPA 1: ESTUDO DOUTRINÁRIO PROFUNDO (MANUAL DA IEADAO)
                        </span>
                        <h2 class="text-2xl sm:text-3xl font-black text-slate-900 mt-1">{{ licao.numero }}: {{ licao.titulo }}</h2>
                        <p class="text-xs text-slate-500 mt-0.5">Leitura Bíblica de Apoio: <b>{{ licao.leitura_base }}</b></p>
                    </div>

                    <div class="bg-amber-50 border-l-4 border-amber-500 p-4 rounded-r-2xl">
                        <span class="text-[10px] font-black uppercase text-amber-900 block mb-1">🔥 Texto Áureo da Lição</span>
                        <p class="text-sm italic text-amber-950 font-serif leading-relaxed">"{{ licao.texto_aureo }}"</p>
                    </div>

                    <div class="text-xs text-slate-700 leading-relaxed text-justify bg-slate-50 p-4 rounded-2xl border border-slate-200">
                        <p class="font-bold text-slate-900 mb-1">Prefácio Temático:</p>
                        <p>{{ licao.conteudo_completo.introducao }}</p>
                    </div>

                    <!-- PONTOS DOUTRINÁRIOS COM NOTAS EXPLICATIVAS -->
                    <div class="space-y-4 text-xs">
                        {% for pt in licao.conteudo_completo.pontos_doutrinarios %}
                        <div class="p-5 rounded-2xl border border-slate-200 bg-white shadow-sm space-y-3">
                            <h4 class="font-black text-sm text-indigo-950 flex items-center gap-1.5">
                                <span class="w-2.5 h-2.5 rounded-full bg-indigo-600"></span> {{ pt.titulo }}
                            </h4>

                            {% if pt.detalhes %}
                            <p class="text-slate-700 leading-relaxed text-justify whitespace-pre-line">{{ pt.detalhes }}</p>
                            {% endif %}

                            <!-- CAIXA DOURADA: NOTA EXPLICATIVA & ORIENTAÇÃO PASTORAL -->
                            {% if pt.nota_explicativa %}
                            <div class="bg-amber-50/90 border-l-4 border-amber-500 p-4 rounded-r-2xl space-y-1.5 text-slate-800 shadow-sm">
                                <span class="font-black text-[11px] uppercase tracking-wider text-amber-900 flex items-center gap-1.5">
                                    <span>💡</span> Nota Explicativa & Orientação Pastoral:
                                </span>
                                <p class="text-xs text-amber-950 leading-relaxed whitespace-pre-line text-justify font-medium">
                                    {{ pt.nota_explicativa }}
                                </p>
                            </div>
                            {% endif %}

                            {% if pt.tabela %}
                            <div class="overflow-x-auto pt-2">
                                <table class="w-full text-left border-collapse text-xs">
                                    <thead>
                                        <tr class="bg-slate-100 font-bold uppercase text-[10px]">
                                            <th class="p-2 w-1/4">Situação</th>
                                            <th class="p-2">Descrição Espiritual</th>
                                            <th class="p-2 w-1/4">Versículos</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for l in pt.tabela %}
                                        <tr class="hover:bg-slate-50">
                                            <td class="p-2 font-bold text-rose-900">{{ l.situacao }}</td>
                                            <td class="p-2 text-slate-700">{{ l.descricao }}</td>
                                            <td class="p-2 font-semibold text-indigo-900">{{ l.versiculos }}</td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                            {% endif %}
                        </div>
                        {% endfor %}
                    </div>

                    {% if licao.conteudo_completo.proverbio_chave %}
                    <div class="bg-gradient-to-r from-indigo-900 to-indigo-950 text-white p-4 rounded-2xl border border-indigo-800 text-xs text-center font-bold">
                        📖 {{ licao.conteudo_completo.proverbio_chave }}
                    </div>
                    {% endif %}

                    <!-- ETAPA 2: RESUMO REFLEXIVO DO ALUNO -->
                    <div class="pt-6 border-t-2 border-slate-100 space-y-4">
                        <div class="flex items-center justify-between">
                            <div>
                                <span class="text-xs font-black uppercase text-amber-600 tracking-wider">
                                    ETAPA 2: RESUMO REFLEXIVO DO ALUNO
                                </span>
                                <h3 class="text-base font-extrabold text-slate-900 mt-0.5">
                                    O Que Você Compreendeu Nesta Lição?
                                </h3>
                                <p class="text-xs text-slate-500">Escreva com as suas palavras. O teste é destrancado após submeter o resumo.</p>
                            </div>
                            {% if progresso_atual.resumo %}
                            <span class="bg-emerald-100 text-emerald-800 px-3 py-1 rounded-full text-xs font-black">
                                ✅ Resumo Entregue
                            </span>
                            {% endif %}
                        </div>

                        {% if progresso_atual.resumo %}
                        <div class="p-4 bg-emerald-50/70 border border-emerald-200 rounded-2xl text-xs text-emerald-950 space-y-1">
                            <span class="font-extrabold block text-emerald-800">Seu Resumo Gravado:</span>
                            <p class="italic">"{{ progresso_atual.resumo }}"</p>
                        </div>
                        {% else %}
                        <form action="/ensino/submeter_resumo" method="POST" class="space-y-3 text-xs">
                            <input type="hidden" name="licao_id" value="{{ licao.id }}">
                            <textarea name="resumo" required rows="4" placeholder="Escreva aqui detalhadamente o que compreendeu dos pontos doutrinários acima..." class="w-full p-4 border-2 border-slate-200 rounded-2xl bg-slate-50 focus:bg-white focus:border-indigo-600 focus:outline-none font-medium leading-relaxed"></textarea>
                            <button type="submit" class="w-full py-3.5 bg-amber-600 hover:bg-amber-700 text-white font-black rounded-xl shadow cursor-pointer text-xs transition">
                                ✍️ Submeter Resumo & Desbloquear o Teste de Fixação
                            </button>
                        </form>
                        {% endif %}
                    </div>

                    <!-- ETAPA 3: TESTE DE FIXAÇÃO TEOLÓGICA -->
                    <div id="teste" class="pt-6 border-t-2 border-slate-100 space-y-4">
                        <span class="text-xs font-black uppercase text-indigo-600 tracking-wider block">
                            ETAPA 3: TESTE DE FIXAÇÃO TEOLÓGICA (MÍNIMO 70%)
                        </span>

                        {% if not progresso_atual.resumo %}
                        <div class="bg-slate-100 border-2 border-dashed border-slate-300 p-8 rounded-2xl text-center space-y-2">
                            <span class="text-3xl">🔒</span>
                            <h4 class="font-bold text-sm text-slate-700">Teste Bloqueado</h4>
                            <p class="text-xs text-slate-500 max-w-md mx-auto">
                                Para ter acesso a este teste, complete a leitura da lição e <b>submeta o seu resumo na Etapa 2</b>.
                            </p>
                        </div>
                        {% else %}
                        <form action="/ensino/submeter_teste" method="POST" class="space-y-4 text-xs">
                            <input type="hidden" name="licao_id" value="{{ licao.id }}">

                            {% for q in licao.questoes %}
                            {% set q_idx = loop.index0 %}
                            <div class="bg-slate-50 p-5 rounded-2xl border border-slate-200 space-y-3">
                                <p class="font-extrabold text-sm text-slate-800">
                                    {{ loop.index }}. {{ q.p }}
                                </p>
                                <div class="space-y-2">
                                    {% for op in q.ops %}
                                    <label class="flex items-center gap-3 p-3 bg-white rounded-xl border border-slate-200 cursor-pointer hover:bg-indigo-50/50 transition">
                                        <input type="radio" name="q_{{ q_idx }}" value="{{ loop.index0 }}" required class="w-4 h-4 text-indigo-600">
                                        <span class="text-slate-700 font-medium">{{ op }}</span>
                                    </label>
                                    {% endfor %}
                                </div>
                            </div>
                            {% endfor %}

                            <button type="submit" class="w-full py-4 bg-indigo-900 hover:bg-indigo-950 text-white font-black rounded-2xl shadow-lg cursor-pointer text-sm transition">
                                🎯 Submeter Teste de Fixação
                            </button>
                        </form>
                        {% endif %}
                    </div>

                    <!-- ETAPA 4: ESPAÇO TIRA-DÚVIDAS -->
                    <div id="duvidas" class="pt-6 border-t-2 border-slate-100 space-y-4">
                        <div class="flex items-center justify-between">
                            <h4 class="font-extrabold text-sm text-slate-900 flex items-center gap-2">
                                <span>💬</span> Espaço Tira-Dúvidas com o Professor ({{ aluno.professor or "Pastor" }})
                            </h4>
                            <span class="text-[10px] text-slate-400">Resposta bíblica e acompanhamento pastoral</span>
                        </div>

                        <form action="/ensino/duvida" method="POST" class="space-y-2 text-xs">
                            <input type="hidden" name="licao_id" value="{{ licao.id }}">
                            <div class="flex gap-2">
                                <input type="text" name="pergunta" required placeholder="Tem alguma dúvida bíblica sobre esta lição? Pergunte aqui..." class="flex-1 h-11 px-3 border-2 border-slate-200 rounded-xl bg-slate-50 focus:bg-white focus:border-indigo-600 focus:outline-none">
                                <button type="submit" class="px-5 h-11 bg-slate-800 hover:bg-slate-900 text-white font-bold rounded-xl shadow cursor-pointer">
                                    Perguntar
                                </button>
                            </div>
                        </form>

                        <div class="space-y-2.5">
                            {% for d in duvidas %}
                            <div class="p-3.5 bg-slate-50 rounded-xl text-xs space-y-1.5 border border-slate-200">
                                <div class="font-bold text-slate-800 flex justify-between">
                                    <span>❓ Sua Pergunta: "{{ d.pergunta }}"</span>
                                    <span class="text-[10px] text-slate-400">{{ d.criado_em }}</span>
                                </div>
                                {% if d.resposta_professor %}
                                <div class="p-2.5 bg-emerald-50 border border-emerald-300 rounded-lg text-emerald-950 text-[11px] leading-relaxed">
                                    <b class="text-emerald-800 block">👨‍🏫 Resposta do seu Professor ({{ d.professor_nome or aluno.professor or 'Pastor' }}):</b>
                                    {{ d.resposta_professor }}
                                </div>
                                {% else %}
                                <div class="p-2.5 bg-white border border-indigo-100 rounded-lg text-indigo-950 text-[11px] leading-relaxed">
                                    <b class="text-indigo-800 block">📖 Orientação do Manual:</b>
                                    {{ d.resposta_sistema }}
                                    <span class="text-[10px] text-slate-400 block mt-1 italic">⏳ Aguardando comentário adicional do seu professor...</span>
                                </div>
                                {% endif %}
                            </div>
                            {% else %}
                            <p class="text-[11px] text-slate-400 italic text-center py-2">Nenhuma dúvida enviada sobre esta lição ainda.</p>
                            {% endfor %}
                        </div>
                    </div>

                </div>
            </div>

        </div>

    </main>
</body>
</html>
"""

# Validar com Jinja2
env = jinja2.Environment()
env.parse(portal_html_limpo)

with open('templates/portal_aluno.html', 'w', encoding='utf-8') as f:
    f.write(portal_html_limpo)
print("✓ templates/portal_aluno.html reconstruído e validado pelo compilador Jinja2 com ZERO erros!")

print("=" * 80)
print(">>> TUDO PRONTO COM TOTAL SUCESSO! EXECUTE: py app.py <<<")
print("=" * 80)