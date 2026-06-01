import os
from random import randint
from time import sleep

#Tabuleiros para cada uso
tabuleiroFeedbackJogador = [
    ['@',1,2,3,4,5,6,7,8,9,10],
    ['A',0,0,0,0,0,0,0,0,0,0],
    ['B',0,0,0,0,0,0,0,0,0,0],
    ['C',0,0,0,0,0,0,0,0,0,0],
    ['D',0,0,0,0,0,0,0,0,0,0],
    ['E',0,0,0,0,0,0,0,0,0,0],
    ['F',0,0,0,0,0,0,0,0,0,0],
    ['G',0,0,0,0,0,0,0,0,0,0],
    ['H',0,0,0,0,0,0,0,0,0,0],
    ['I',0,0,0,0,0,0,0,0,0,0],
    ['J',0,0,0,0,0,0,0,0,0,0]
]

tabuleiroFeedbackComputador = [
    ['@',1,2,3,4,5,6,7,8,9,10],
    ['A',0,0,0,0,0,0,0,0,0,0],
    ['B',0,0,0,0,0,0,0,0,0,0],
    ['C',0,0,0,0,0,0,0,0,0,0],
    ['D',0,0,0,0,0,0,0,0,0,0],
    ['E',0,0,0,0,0,0,0,0,0,0],
    ['F',0,0,0,0,0,0,0,0,0,0],
    ['G',0,0,0,0,0,0,0,0,0,0],
    ['H',0,0,0,0,0,0,0,0,0,0],
    ['I',0,0,0,0,0,0,0,0,0,0],
    ['J',0,0,0,0,0,0,0,0,0,0]
]

tabuleiroJogador = [
    ['@',1,2,3,4,5,6,7,8,9,10],
    ['A',0,0,0,0,0,0,0,0,0,0],
    ['B',0,0,0,0,0,0,0,0,0,0],
    ['C',0,0,0,0,0,0,0,0,0,0],
    ['D',0,0,0,0,0,0,0,0,0,0],
    ['E',0,0,0,0,0,0,0,0,0,0],
    ['F',0,0,0,0,0,0,0,0,0,0],
    ['G',0,0,0,0,0,0,0,0,0,0],
    ['H',0,0,0,0,0,0,0,0,0,0],
    ['I',0,0,0,0,0,0,0,0,0,0],
    ['J',0,0,0,0,0,0,0,0,0,0]
]

tabuleiroComputador = [
    ['@',1,2,3,4,5,6,7,8,9,10],
    ['A',0,0,0,0,0,0,0,0,0,0],
    ['B',0,0,0,0,0,0,0,0,0,0],
    ['C',0,0,0,0,0,0,0,0,0,0],
    ['D',0,0,0,0,0,0,0,0,0,0],
    ['E',0,0,0,0,0,0,0,0,0,0],
    ['F',0,0,0,0,0,0,0,0,0,0],
    ['G',0,0,0,0,0,0,0,0,0,0],
    ['H',0,0,0,0,0,0,0,0,0,0],
    ['I',0,0,0,0,0,0,0,0,0,0],
    ['J',0,0,0,0,0,0,0,0,0,0]
]

#  Começa pelo maior barco
tamanhoBarco = 5
# Letras numa lista para conmseguir o número da coordenada
letrasLinhas = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']


while tamanhoBarco > 0:
    for c in range (11):
        print (tabuleiroJogador[c])

    letraRow = input(f"Digite a linha de onde quer colocar o barco de tamanho {tamanhoBarco}: ").upper()
    if letraRow in letrasLinhas:
        rowBarco = letrasLinhas.index(letraRow) + 1
    else:
        print("Erro: Linha inválida! Escolha uma letra de A a J.")
        continue

    try:
        columBarco = int(input(f"Digite a coluna de onde quer colocar o barco de tamanho {tamanhoBarco}: "))
        if columBarco < 1 or columBarco > 10:
            print("Erro: Coluna deve ser entre 1 e 10.")
            continue
    except ValueError:
        print("Erro: Digite apenas números para a coluna!")
        continue
    if tamanhoBarco > 1:
        orientacaoBarco = input(f"Digite a orientação do barco V ou H: ").upper()
        if orientacaoBarco not in ['V','H']:
            print ('Erro: Orientação inválida! Use V ou H.')
    else:
        orientacaoBarco = "H"

    # Se passar das bordas da matriz, para
    if orientacaoBarco == 'V' and (rowBarco + tamanhoBarco - 1) > 10:
        print("Erro: O barco ultrapassa o limite inferior do tabuleiro!")
        continue
    elif orientacaoBarco == 'H' and (columBarco + tamanhoBarco - 1) > 10:
        print("Erro: O barco ultrapassa o limite lateral direito!")
        continue
    
    
    # Criamos variáveis temporárias para não estragar as originais durante o teste
    checaRow = rowBarco
    checaCol = columBarco
    podePosicionar = True

    for j in range(tamanhoBarco):
        if tabuleiroJogador[checaRow][checaCol] == '■':
            podePosicionar = False
            break # Se achou um único impedimento, já podemos parar de checar
            
        # Avança a simulação passo a passo
        if orientacaoBarco == 'V':
            checaRow += 1
        else:
            checaCol += 1

    # Se a simulação encontrou um barco no caminho, cancela o posicionamento
    if not podePosicionar:
        print("Erro: Já existe um barco bloqueando esse caminho! Escolha outra posição.")
        continue # Volta para o início do while, pedindo o mesmo barco de novo
    
    # Se passou em tudo (Limites E Sobreposição), desenha o barco
    for j in range(tamanhoBarco):
        tabuleiroJogador[rowBarco] [columBarco] = '■'
        if orientacaoBarco == 'V':
            rowBarco += 1
        else:
            columBarco += 1

    tamanhoBarco -= 1
    os.system('cls' if os.name == 'nt' else 'clear') # Limpa o terminal

while tamanhoBarco > 0:

    rowBarco = randint(1, 10)
    columBarco = randint(1,10)

    orientacao = ['V','H']
    x = randint(0,1)
    
    if tamanhoBarco > 1:
        orientacaoBarco = orientacao[x]
    else:
        orientacaoBarco = "H"

    # Se passar das bordas da matriz, para
    if orientacaoBarco == 'V' and (rowBarco + tamanhoBarco - 1) > 10:
        continue
    elif orientacaoBarco == 'H' and (columBarco + tamanhoBarco - 1) > 10:
        continue
    
    
    # Criamos variáveis temporárias para não estragar as originais durante o teste
    checaRow = rowBarco
    checaCol = columBarco
    podePosicionar = True

    for j in range(tamanhoBarco):
        if tabuleiroComputador[checaRow][checaCol] == '■':
            podePosicionar = False
            break # Se achou um único impedimento, já podemos parar de checar
            
        # Avança a simulação passo a passo
        if orientacaoBarco == 'V':
            checaRow += 1
        else:
            checaCol += 1

    # Se a simulação encontrou um barco no caminho, cancela o posicionamento
    if not podePosicionar:
        continue # Volta para o início do while, pedindo o mesmo barco de novo
    
    # Se passou em tudo (Limites E Sobreposição), desenha o barco
    for j in range(tamanhoBarco):
        tabuleiroComputador[rowBarco] [columBarco] = '■'
        if orientacaoBarco == 'V':
            rowBarco += 1
        else:
            columBarco += 1

    tamanhoBarco -= 1

for k in range(11):
    print (tabuleiroComputador[k])