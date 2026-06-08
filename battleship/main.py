# main.py — Ponto de entrada

"""
Bem-vindo ao Batalha Naval 2!

Controles:

NAVEGAÇÃO (Fase de Movimento):
  ← → : Ajusta o leme (-45° a +45°, passos de 15°)
  ↑ ↓ : Controla a velocidade (1 a máxima)
  ENTER: Confirma o movimento

ATAQUE (Fase de Ação):
  Mouse: Mira o alvo (círculo mostra o alcance)
  Clique: Dispara o morteiro
  ESPAÇO: Pula a fase de ataque

LOJA (Fase de Compras):
  Clique nos botões: Compra ou faz upgrade de módulos
  ENTER / ESPAÇO: Pula a loja

CONTROLES GERAIS:
  Scroll / Z / X: Zoom no mapa
  R: Volta para o menu (na tela de fim de jogo)

O radar mostra inimigos ruidosos com uma linha verde giratória.
"""

import pygame
from game import Game


def main():
    pygame.init()
    g = Game()
    g.run()


if __name__ == '__main__':
    main()
