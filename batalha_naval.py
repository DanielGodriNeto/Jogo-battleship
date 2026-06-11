import os
from random import randint
from time import sleep
import pyfiglet
import subprocess
import sys

try:
    import pyfiglet
except ImportError:
    try:
        # Tenta instalar automaticamente caso não exista
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyfiglet"])
        import pyfiglet
    except:
        pyfiglet = None

# --- Configurações de Cores ANSI ---
RESET  = "\033[0m"
BOLD   = "\033[1m"
RED    = "\033[31m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
BLUE   = "\033[34m"
CYAN   = "\033[36m"
WHITE  = "\033[37m"
BG_BLUE = "\033[44m"

def exibir_tabuleiro(tabuleiro):
    """Imprime o tabuleiro formatado com cores."""
    for linha in tabuleiro:
        for item in linha:
            if item == 0:   print(f"{CYAN}🌊{RESET}", end=" ")
            elif item == '■': print(f"{WHITE}🚢{RESET}", end=" ")
            elif item == 'X': print(f"{RED}💥{RESET}", end=" ")
            elif item == 'O': print(f"{YELLOW}💧{RESET}", end=" ")
            elif str(item) == '10':
                print(f"{BOLD}{GREEN}{item}{RESET}", end=" ")
            elif str(item).isdigit() or len(str(item)) == 1:
                print(f"{BOLD}{GREEN}{item}{RESET}", end="  ")
            else: print(item, end="  ")
        print()
    print()

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

# Quantidade de vida baseada no numero de espaços com barco
vidaJogador = 15
vidaPC = 15

#  Começa pelo maior barco
tamanhoBarco = 5
tamanhoBarcoPC = 5
# Letras numa lista para conmseguir o número da coordenada
letrasLinhas = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

# --- Tela Inicial ---
os.system('cls' if os.name == 'nt' else 'clear')
if pyfiglet:
    print(pyfiglet.figlet_format("Batalha Naval", font="standard"))
else:
    print(f"\n{BOLD}{CYAN}=== BATALHA NAVAL ==={RESET}\n")

print(f"""{CYAN}
╔══════════════════════════════════════════════════════════════╗
║                     CRÉDITOS DO JOGO                         ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║                  ⚓ Desenvolvedores ⚓                       ║
║                                                              ║
║                   Mateus Weiss Medeiros                      ║
║                     Daniel Godri Neto                        ║
║                   Gustavo Gomes Luciano                      ║
║                                                              ║
║                                                              ║
║          Obrigado por jogar nossa Batalha Naval!             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
{RESET}""")

print(f"\n{BOLD}{GREEN}Pressione ENTER para começar...{RESET}")
input() # Espera o usuário pressionar Enter

# Remove a tela de créditos do final do jogo, pois agora está na inicial

# --- Fim da Tela Inicial ---





while tamanhoBarco > 0:
    os.system('cls' if os.name == 'nt' else 'clear')
    if pyfiglet:
        print(pyfiglet.figlet_format("Batalha Naval", font="standard"))
    else:
        print(f"\n{BOLD}{CYAN}=== BATALHA NAVAL ==={RESET}\n")
    print(f"\n{BOLD}{BLUE}=== FASE DE POSICIONAMENTO: JOGADOR ==={RESET}")
    exibir_tabuleiro(tabuleiroJogador)
    
    # Coleta e valida a linha do barco
    letraRow = input(f"Digite a linha de onde quer colocar o barco de tamanho {tamanhoBarco}: ").upper()
    if letraRow in letrasLinhas:
        rowBarco = letrasLinhas.index(letraRow) + 1
    else:
        print(f"{RED}Erro: Linha inválida! Escolha uma letra de A a J.{RESET}")
        continue

    # Coleta e valida a coluna do barco
    try:
        columBarco = int(input(f"Digite a coluna de onde quer colocar o barco de tamanho {tamanhoBarco}: "))
        if columBarco < 1 or columBarco > 10:
            print(f"{RED}Erro: Coluna deve ser entre 1 e 10.{RESET}")
            continue
    except ValueError:
        print(f"{RED}Erro: Digite apenas números para a coluna!{RESET}")
        continue

    # Destroier de tamanho 1 não precisa escolher orientação
    if tamanhoBarco > 1:
        orientacaoBarco = input(f"Digite a orientação do barco V ou H: ").upper()
        if orientacaoBarco not in ['V','H']:
            print (f'{RED}Erro: Orientação inválida! Use V ou H.{RESET}')
            continue
    else:
        orientacaoBarco = "H"

    # Se passar das bordas da matriz, para
    if orientacaoBarco == 'V' and (rowBarco + tamanhoBarco - 1) > 10:
        print(f"{RED}Erro: O barco ultrapassa o limite inferior do tabuleiro!{RESET}")
        continue
    elif orientacaoBarco == 'H' and (columBarco + tamanhoBarco - 1) > 10:
        print(f"{RED}Erro: O barco ultrapassa o limite lateral direito!{RESET}")
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
        print(f"{RED}Erro: Já existe um barco bloqueando esse caminho! Escolha outra posição.{RESET}")
        continue # Volta para o início do while, pedindo o mesmo barco de novo
    
    # Se passou em tudo (Limites E Sobreposição), desenha o barco
    checaRow = rowBarco
    checaCol = columBarco
    for j in range(tamanhoBarco):
        tabuleiroJogador[checaRow][checaCol] = '■'
        if orientacaoBarco == 'V':
            checaRow += 1
        else:
            checaCol += 1

    tamanhoBarco -= 1

while tamanhoBarcoPC > 0:

    # Sorteia uma linha e coluna aleatoria para o PC
    rowBarco = randint(1, 10)
    columBarco = randint(1,10)

    # Sorteia uma orientacao aleatoria para o PC
    orientacao = ['V','H']
    x = randint(0,1)
    
    if tamanhoBarcoPC > 1:
        orientacaoBarco = orientacao[x]
    else:
        orientacaoBarco = "H"

    # Se o barco do PC passar das bordas da matriz, recomeça o sorteio
    if orientacaoBarco == 'V' and (rowBarco + tamanhoBarcoPC - 1) > 10:
        continue
    elif orientacaoBarco == 'H' and (columBarco + tamanhoBarcoPC - 1) > 10:
        continue
    
    
    # Criamos variáveis temporárias para não estragar as originais durante o teste do PC
    checaRow = rowBarco
    checaCol = columBarco
    podePosicionar = True

    for j in range(tamanhoBarcoPC):
        if tabuleiroComputador[checaRow][checaCol] == '■':
            podePosicionar = False
            break # Se achou um único impedimento, para de checar
            
        # Avança a simulação do PC passo a passo
        if orientacaoBarco == 'V':
            checaRow += 1
        else:
            checaCol += 1

    # Se a simulação encontrou um barco no caminho do PC, cancela o posicionamento
    if not podePosicionar:
        continue # Volta para o início do while, sorteando o barco de novo
    
    # Se passou em tudo, desenha o barco do PC no tabuleiro secreto dele
    checaRow = rowBarco
    checaCol = columBarco
    for j in range(tamanhoBarcoPC):
        tabuleiroComputador[checaRow][checaCol] = '■'
        if orientacaoBarco == 'V':
            checaRow += 1
        else:
            checaCol += 1

    tamanhoBarcoPC -= 1

# Variavel para controlar quem joga (True = Humano, False = Computador)
turnoJogador = True

while vidaJogador > 0 and vidaPC > 0:
    if turnoJogador:
        os.system('cls' if os.name == 'nt' else 'clear')
        if pyfiglet:
            print(pyfiglet.figlet_format("Batalha Naval", font="standard"))
        else:
            print(f"\n{BOLD}{CYAN}=== BATALHA NAVAL ==={RESET}\n")
        print(f"{BOLD}{BLUE}--- SEU TURNO ---{RESET}")
        print(f"Vidas Inimigas: {RED}{vidaPC}{RESET}")
        exibir_tabuleiro(tabuleiroFeedbackComputador) # Exibe o tabuleiro antes de pedir o tiro
        
        # Coleta e valida a linha do tiro
        tiroRow = input(f"Digite a linha de onde quer atirar: ").upper()
        if tiroRow in letrasLinhas:
            rowTiro = letrasLinhas.index(tiroRow) + 1
        else:
            print(f"{RED}Erro: Linha inválida! Escolha uma letra de A a J.{RESET}")
            continue

        # Coleta e valida a coluna do tiro
        try:
            columTiro = int(input(f"Digite a coluna de onde quer atirar: "))
            if columTiro < 1 or columTiro > 10:
                print(f"{RED}Erro: Coluna deve ser entre 1 e 10.{RESET}")
                continue
        except ValueError:
            print(f"{RED}Erro: Digite apenas números para a coluna!{RESET}")
            continue

        # Checar se o tiro ja foi dado antes no computador
        if tabuleiroFeedbackComputador[rowTiro][columTiro] in ['X', 'O']:
            print(f"{YELLOW}Aviso: Você já atirou nessa coordenada!{RESET}")
            continue

        # Verificar se acertou um barco do computador
        if tabuleiroComputador[rowTiro][columTiro] == '■':
            print(f"{BOLD}{GREEN}POOOW! Você acertou uma embarcação inimiga!{RESET}")
            tabuleiroFeedbackComputador[rowTiro][columTiro] = 'X' # Marca acerto no tabuleiro de feedback
            tabuleiroComputador[rowTiro][columTiro] = 'X' # Desativa o barco no tabuleiro do PC
            vidaPC -= 1
        else:
            print(f"{CYAN}Splash! Água... Você errou o alvo.{RESET}")
            tabuleiroFeedbackComputador[rowTiro][columTiro] = 'O' # Marca agua no tabuleiro de feedback
            turnoJogador = False

        sleep(2.5) # Tempo para jogador ver se acertou ou não
        os.system('cls' if os.name == 'nt' else 'clear') # Limpa o terminal para a proxima rodada
    else:
        os.system('cls' if os.name == 'nt' else 'clear')
        if pyfiglet:
            print(pyfiglet.figlet_format("Batalha Naval", font="standard"))
        else:
            print(f"\n{BOLD}{CYAN}=== BATALHA NAVAL ==={RESET}\n")
        print(f"{BOLD}{YELLOW}--- TURNO DO COMPUTADOR ---{RESET}")
        # Sorteia coordenadas aleatórias para o tiro do computador
        tiroRowPC = randint(1, 10)
        tiroColumPc = randint(1, 10)

        # Checar se o computador ja atirou nessa coordenada antes
        if tabuleiroFeedbackJogador[tiroRowPC][tiroColumPc] in ['X', 'O']:
            continue # Se ja atirou, repete o while sem mudar o turno para sortear de novo

        # Verificar se o computador acertou o jogador
        if tabuleiroJogador[tiroRowPC][tiroColumPc] == '■': 
            # Traduz o número da linha de volta para letra (ex: 1 vira 'A') para expor no print
            print(f"{RED}KABOOM! O Computador atirou em {letrasLinhas[tiroRowPC-1]}{tiroColumPc} e ACERTOU seu barco!{RESET}")
            tabuleiroFeedbackJogador[tiroRowPC][tiroColumPc] = 'X' 
            tabuleiroJogador[tiroRowPC][tiroColumPc] = 'X' # CORREÇÃO: adicionado = 'X' para desativar o barco atingido
            vidaJogador -= 1
            # Nota: como ele acertou, turnoJogador continua False (vez do PC de novo)
        else:
            print(f"O Computador atirou em {letrasLinhas[tiroRowPC-1]}{tiroColumPc} e errou na água.")
            tabuleiroFeedbackJogador[tiroRowPC][tiroColumPc] = 'O' 
            turnoJogador = True # CORREÇÃO: Alterna para True para voltar a ser a vez do Humano

        sleep(2.5) # Dá tempo para o jogador ler o que o PC fez antes de limpar a tela
        os.system('cls' if os.name == 'nt' else 'clear')
# Apresenta quem foi o vencedor
sleep(2.5)
os.system('cls' if os.name == 'nt' else 'clear')
print(f"\n{BOLD}{GREEN}🏆 PARABÉNS! Você afundou a frota inimiga e venceu a batalha!{RESET}" if vidaPC == 0 else f"\n{BOLD}{RED}💀 DERROTA! Sua frota foi dizimada pelo computador...{RESET}")