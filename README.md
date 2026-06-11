<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:0f172a,100:10b981&height=180&section=header&text=Batalha%20Naval%202%20-%20v0.4&fontSize=38&fontColor=ffffff&animation=fadeIn&fontAlignY=35"/>

<h1 align="center">⚓ Batalha Naval 2 (Battleship Tactic Sim)</h1>
<h3 align="center">Simulador Tático de Combate Naval Avançado com Pygame</h3>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Engine-Pygame-green?style=for-the-badge" alt="Pygame" />
  <img src="https://img.shields.io/badge/Interface-Gr%C3%A1fica%20(2D)-orange?style=for-the-badge" alt="Interface" />
  <img src="https://img.shields.io/badge/Interface-Terminal%20(CLI)-lightgrey?style=for-the-badge" alt="CLI" />
</p>

---

## 📝 Sobre o Projeto
Este repositório contém duas versões distintas do clássico jogo de Batalha Naval, demonstrando a evolução de lógica de programação e interface:

Afastando-se do modelo clássico e estático de tabuleiro, o **Batalha Naval 2** é um simulador tático em tempo real e turnos desenvolvido com a biblioteca **Pygame**. Nele, os jogadores controlam embarcações customizáveis em um mundo aberto dinâmico dotado de mecânicas avançadas de navegação, economia, furtividade e customização modular de frotas. 
1.  **Versão Clássica (CLI):** Um jogo direto no terminal contra a IA, focado na lógica pura e visual retrô com emojis.
2.  **Batalha Naval 2 (Gráfico):** Um simulador tático modular com física, economia e névoa de guerra.

---

## 💻 Versão de Terminal (CLI)
Localizada na raiz como `batalha_naval.py`, esta versão oferece a experiência clássica:
- 🎨 **Interface Colorida:** Utiliza códigos ANSI para renderizar o tabuleiro no terminal.
- 🤖 **IA Desafiadora:** Jogue contra um computador que realiza disparos aleatórios inteligentes.
- 🚢 **Fase de Posicionamento:** Coloque sua frota (5 navios) estrategicamente usando coordenadas (A-J, 1-10).

**Como rodar:** `python batalha_naval.py`

---

## ⚓ Batalha Naval 2 (Versão Pygame)
A versão principal do projeto. Afastando-se do modelo estático, é um simulador tático desenvolvido com **Pygame**. Nele, os jogadores controlam embarcações customizáveis em um mundo aberto dinâmico.

O jogo conta com uma renderização inteligente baseada em uma Viewport fixa com sistema de câmera livre e zoom escalável, mantendo a interface de usuário (HUD e menus) estática e responsiva.

---

## 🚀 Mecânicas e Funcionalidades v0.4

- 🧭 **Navegação Tática (Fase Move):** Sistema de "Ghost Ship" que permite prever a trajetória baseada no ângulo do leme (-45° a +45°) e na potência do motor antes de confirmar o movimento.
- 🛠️ **Dano Modular Dinâmico:** O navio não possui apenas uma "barra de vida" global. Tiros podem atingir módulos específicos (Motores, Armas, Radar). Se o motor for destruído, sua velocidade cai; se o morteiro for atingido, você perde a capacidade de ataque.
- 🟢 **Sonar Baseado em Ruído:** O alcance da detecção no radar depende do motor do oponente. Motores nucleares são ruidosos e fáceis de detectar, enquanto o **Motor Termo-nuclear** permite navegação silenciosa (furtiva).
- 🏝️ **Geração Procedural de Mundo:** Mapas gerados aleatoriamente com biomas de Areia, Grama e Montanhas. O sistema garante áreas de spawn limpas e gera ilhas com formatos orgânicos.
- 🌫️ **Névoa de Guerra (Fog of War):** Visão limitada ao raio estratégico do navio. O módulo de **Radar** expande essa visão, permitindo identificar ameaças antes de ser visto.
- 🏪 **Economia e Upgrades (Fase Shop):** Destruir piratas (NPCs) ou peixes gera moedas para reparos ou melhorias:
  - *Motores:* Diesel (Básico), Nuclear (Rápido/Ruidoso) e Termo-nuclear (Rápido/Silencioso).
  - *Ataque:* Morteiro Pesado (maior alcance e dano duplo).
  - *Defesa:* Blindagem (Armor) que protege os módulos contra danos de colisão em ilhas.
  - *Utilidade:* Laboratório de Pesquisa (bônus de $ em abates).
- 🐟 **Ecosistema Vivo:** Renderização de peixes autônomos com movimentação baseada em ângulos aleatórios e geradores de partículas para fumaça, rastros de água e explosões.

---

## 🎮 Comandos do Jogo

O jogo alterna entre os Jogadores 1 e 2, passando por 3 fases em cada turno:

### ⛵ Navegação (Fase Move)
* `←` `→` : Ajusta o ângulo do Leme (passos de 15°).
* `↑` `↓` : Define a velocidade (limitada pelo motor atual).
* `ENTER` : Executa a navegação e verifica colisões.

### 🎯 Ataque (Fase Action)
* `Mouse` : Mira o alvo (o círculo amarelo indica o alcance máximo).
* `Clique Esquerdo` : Dispara contra a coordenada.
* `ESPAÇO` : Pula a fase de ataque.

### 🏪 Loja (Fase Shop)
* `Clique nos Botões` : Compra módulos, faz Upgrades ou repara peças danificadas.
* `ENTER` : Finaliza o turno e passa a vez.

### 🎥 Câmera e Geral
* `Scroll / Z / X` : Zoom dinâmico no mapa.
* `R` : Reinicia o jogo (disponível na tela de vitória).

---
## 🛠️ Arquitetura do Código

A estrutura do projeto foi dividida seguindo boas práticas de organização de desenvolvimento de jogos (Modularização de Estados):
* `main.py`: Ponto de entrada que inicializa a janela do Pygame e dispara o loop central.
* `game.py`: Máquina de estados principal do jogo. Gerencia o controle de turnos, o fluxo de fases e atualizações de física.
* `entities.py`: Classes estruturadas que definem os comportamentos do Navio (`Ship`), Módulos (`Module`), navios piratas (`NPCShip`), peixes e vetores de partículas.
* `renderer.py`: Toda a pipeline gráfica e de desenho. Separa o mundo escalável por matriz de câmera da HUD fixa na tela.
* `radar.py`: Lógica matemática do sonar circular e cálculos trigonométricos de latitude e longitude.
* `constants.py`: Centraliza o balanceamento do jogo (preços, HP, cores e tamanhos de mapa).

---

## 👥 Desenvolvedores

* **Daniel Godri Neto**
* **Mateus Weiss Medeiros**
* **Gustavo Gomes Luciano**

---

<div align="center">
  <sub>Desenvolvido para fins acadêmicos — Bacharelado em Ciência da Computação — PUCPR</sub>
</div>
