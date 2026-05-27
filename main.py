# main.py — Ponto de entrada

"""
╔══════════════════════════════════════════════════════════════╗
║         BATALHA NAVAL 2  —  v0.3                            ║
╠══════════════════════════════════════════════════════════════╣
║  NAVEGAÇÃO (fase move):                                       ║
║    ← →   Leme (-90° / +90°, passo 15°)                       ║
║    ↑ ↓   Velocidade (1–max)                                   ║
║    ENTER Confirmar movimento                                  ║
║    Scroll / Z / X  Zoom in / out                             ║
║                                                               ║
║  ATAQUE (fase action):                                        ║
║    Mouse  Mirar alvo (círculo = alcance)                      ║
║    Click  Disparar morteiro                                   ║
║    SPACE  Pular ataque                                        ║
║                                                               ║
║  LOJA (fase shop):                                            ║
║    Clique nos botões — inclui Expandir Casco                  ║
║    ENTER / SPACE = pular                                      ║
║                                                               ║
║  CONSTRUÇÃO (fase build):                                     ║
║    Click Esq  Colocar módulo no casco                         ║
║    R          Rotacionar                                      ║
║    Click Dir / ESC  Cancelar                                  ║
║                                                               ║
║  RADAR:  Linha verde girando detecta inimigos ruidosos        ║
║  R = Menu (na tela de fim de jogo)                            ║
╚══════════════════════════════════════════════════════════════╝
"""

import pygame
from game import Game


def main():
    pygame.init()
    g = Game()
    g.run()


if __name__ == '__main__':
    main()
