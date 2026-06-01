import os
from random import randint
from time import sleep

# Tabuleiros para cada uso
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

# Começa pelo maior barco (tamanho 5) e vai diminuindo até 1
tamanhoBarco = 5
# Letras numa lista para conseguir o número da coordenada
letrasLinhas = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

# Loop principal para posicionar todos os barcos
while tamanhoBarco > 0:
    # Mostra o tabuleiro atual do jogador na tela
    for c in range (11):
        print (tabuleiroJogador[c])

    # Recebe os dados de posicionamento do usuário
    letraRow = input(f"Digite a linha de onde quer colocar o barco de tamanho {tamanhoBarco}: ")
    if letraRow in letrasLinhas:
        rowBarco = letrasLinhas.index(letraRow) + 1 # Transforma a letra no índice da linha do tabuleiro

    columBarco = int(input(f"Digite a coluna de onde quer colocar o barco de tamanho {tamanhoBarco}: "))
    orientacaoBarco = input(f"Digite a orientação do barco V ou H: ").upper()

    podePosicionar = True
    
    # Verifica se o barco sai para fora das bordas do tabuleiro
    if orientacaoBarco == 'V' and (rowBarco + tamanhoBarco - 1) > 10:
        print("Erro: O barco ultrapassa o limite inferior do tabuleiro!")
        sleep(2)
        continue
    elif orientacaoBarco == 'H' and (columBarco + tamanhoBarco - 1) > 10:
        print("Erro: O barco ultrapassa o limite lateral direito!")
        sleep(2)
        continue
        
    # Variáveis temporárias para não estragar as originais durante o teste
    checaRow = rowBarco
    checaCol = columBarco
    
    # Varre as posições onde o barco vai passar para ver se estão vazias
    for j in range(tamanhoBarco):
        if tabuleiroJogador[checaRow][checaCol] == '■':
            podePosicionar = False
            break # Se achou um único impedimento, para
            
        # Avança passo a passo
        if orientacaoBarco == 'V':
            checaRow += 1
        else:
            checaCol += 1

    # Se encontrou um barco no caminho, cancela o posicionamento
    if not podePosicionar:
        print("Erro: Já existe um barco bloqueando esse caminho! Escolha outra posição.")
        sleep(2)
        continue # Volta para o início do while, pedindo o mesmo barco de novo
    
    # Se passou em tudo (Limites e Sobreposição), desenha o barco
    for j in range(tamanhoBarco):
        tabuleiroJogador[rowBarco] [columBarco] = '■'
        if orientacaoBarco == 'V':
            rowBarco += 1
        else:
            columBarco += 1
            
    tamanhoBarco -= 1 # Passa para o próximo tamanho de barco
    os.system('cls' if os.name == 'nt' else 'clear') # Limpa o terminal para a próxima jogada