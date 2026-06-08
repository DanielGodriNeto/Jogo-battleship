<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:0f172a,100:10b981&height=180&section=header&text=Batalha%20Naval%202%20-%20v0.3&fontSize=38&fontColor=ffffff&animation=fadeIn&fontAlignY=35"/>

<h1 align="center">⚓ Batalha Naval 2 (Battleship Tactic Sim)</h1>
<h3 align="center">Simulador Tático de Combate Naval Avançado com Pygame</h3>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Engine-Pygame-green?style=for-the-badge" alt="Pygame" />
  <img src="https://img.shields.io/badge/Interface-Gr%C3%A1fica%20(2D)-orange?style=for-the-badge" alt="Interface" />
</p>

---

## 📝 Sobre o Projeto

Afastando-se do modelo clássico e estático de tabuleiro, o **Batalha Naval 2** é um simulador tático em tempo real e turnos desenvolvido com a biblioteca **Pygame**. Nele, os jogadores controlam embarcações customizáveis em um mundo aberto dinâmico dotado de mecânicas avançadas de navegação, economia, furtividade e customização modular de frotas. 

O jogo conta com uma renderização inteligente baseada em uma Viewport fixa com sistema de câmera livre e zoom escalável, mantendo a interface de usuário (HUD e menus) estática e responsiva.

---

## 🚀 Mecânicas e Funcionalidades de Destaque

- 🧭 **Navegação Realista (Fase Move):** Controle de direção baseado em ângulo de Leme (-45° a +45° com passos de 15°) e aceleração do Motor Diesel, gerando movimentações fluidas por vetores no mapa.
- 🟢 **Radar e Sistema de Sonar Ativo:** Linha verde giratória estilizada que detecta embarcações inimigas ruidosas (NPCs e Jogador 2) baseando o raio de escaneamento diretamente no nível de emissão de ruído do motor. Exibe coordenadas geográficas (Lat/Lon) em tempo real.
- 🌫️ **Névoa de Guerra (Fog of War):** Algoritmo de renderização que oculta elementos do mapa fora do raio de visão estratégico das embarcações, forçando o uso do sonar para rastreamento.
- 🛠️ **Fase de Construção Modular (Fase Build):** Permite encaixar fisicamente novos módulos na estrutura do navio. Os blocos podem ser rotacionados (`R`) antes da instalação e possuem caixas de colisão próprias.
- 🏪 **Loja de Upgrades (Fase Shop):** Sistema econômico com acúmulo de moedas para expandir o casco ou comprar componentes avançados:
  - *Motores:* Motor Diesel de fábrica, Motor Nuclear (Vel max 6) e Motor Termo-nuclear (Vel 8 e 100% silencioso).
  - *Armamentos & Defesa:* Morteiro Pesado, Blindagens que absorvem impacto de colisão.
  - *Utilidade:* Laboratórios (+20% de recompensa) e antenas de Radar (+4 tiles de visão).
- 🐟 **Ecosistema Vivo:** Renderização de peixes autônomos com movimentação baseada em ângulos aleatórios e geradores de partículas para fumaça, rastros de água e explosões.

---

## 🎮 Comandos do Jogo

O fluxo tático é dividido em fases bem definidas controladas por atalhos integrados:

### ⛵ Navegação (Fase Move)
* `←` `→` : Ajusta o ângulo do Leme.
* `↑` `↓` : Controla a velocidade de cruzeiro.
* `ENTER` : Confirma o movimento e encerra a fase.
* `Scroll do Mouse` / `Z` / `X` : Controle de Zoom In / Zoom Out do mapa.

### 🎯 Ataque (Fase Action)
* `Movimento do Mouse` : Mira o morteiro (exibe círculo de alcance do armamento).
* `Clique Esquerdo` : Dispara o morteiro na coordenada selecionada.
* `ESPAÇO` : Pula a fase de ataque.

### 🏪 Loja & Construção (Fase Shop / Build)
* `Clique nos Botões` : Seleciona o upgrade ou expansão de casco.
* `Clique Esquerdo no Casco` : Posiciona o módulo comprado.
* `R` : Rotaciona o módulo em 90°.
* `Clique Direito / ESC` : Cancela a colocação do item.

---

## 🛠️ Arquitetura do Código

A estrutura do projeto foi dividida seguindo boas práticas de organização de desenvolvimento de jogos (Modularização de Estados):
* `main.py`: Ponto de entrada que inicializa a janela do Pygame e dispara o loop central.
* `game.py`: Máquina de estados principal do jogo. Gerencia o controle de turnos, o fluxo de fases e atualizações de física.
* `entities.py`: Classes estruturadas que definem os comportamentos do Navio (`Ship`), Módulos (`Module`), navios piratas (`NPCShip`), peixes e vetores de partículas.
* `renderer.py`: Toda a pipeline gráfica e de desenho. Separa o mundo escalável por matriz de câmera da HUD fixa na tela.
* `radar.py`: Lógica matemática do sonar circular e cálculos trigonométricos de latitude e longitude.
* `constants.py`: Dicionários globais de propriedades, árvore de upgrades, paleta de cores hex/RGB e tamanhos de mapas (de Pequeno a Enorme).

---

## 👥 Desenvolvedores

* **Daniel Godri Neto**
* **Mateus Weiss Medeiros**

---

<div align="center">
  <sub>Desenvolvido para fins acadêmicos — Bacharelado em Ciência da Computação — PUCPR</sub>
</div>