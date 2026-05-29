# constants.py — Constantes globais e paleta de cores

BASE_TILE   = 36
VP_COLS     = 20
VP_ROWS     = 16
# Tamanho fixo da viewport em pixels — não muda com zoom
VP_PIXELS_W = VP_COLS * BASE_TILE
VP_PIXELS_H = VP_ROWS * BASE_TILE
SIDEBAR_W   = 270
BOTTOM_H    = 90

MAP_SIZES   = {'Pequeno': 48, 'Médio': 80, 'Grande': 128, 'Enorme': 200}
DEFAULT_MAP = 'Médio'

FOG_RADIUS_BASE = 5
FPS = 60

# Mutável via _init_game
GRID_SIZE = MAP_SIZES[DEFAULT_MAP]

# ── Paleta ────────────────────────────────────────────────────────────────────
C = {
    'water_a'   : ( 22,  82, 140),
    'water_b'   : ( 18,  70, 122),
    'grid_line' : ( 15,  58, 100),
    # --- Cores das Ilhas ---
    'sand'      : (235, 210, 140),  # Praia / Bordas
    'grass'     : ( 55, 140,  75),  # Interior verde
    'stone'     : (110, 115, 125),  # Centro rochoso / Pico
    # -----------------------
    'ui_bg'     : ( 10,  14,  22),
    'ui_panel'  : ( 20,  26,  40),
    'ui_border' : ( 44,  56,  84),
    'text'      : (210, 220, 240),
    'text_dim'  : (110, 124, 150),
    'highlight' : (255, 220,  50),
    'p1'        : ( 50, 210, 130),
    'p2'        : (220,  70,  70),
    'hull'      : (100,  90,  72),
    'mortar'    : (190, 140,  30),
    'armor'     : ( 80, 150, 200),
    'engine'    : (150,  60, 160),
    'research'  : ( 60, 170,  80),
    'npc_fish'  : ( 80, 200, 180),
    'npc_ship'  : (160, 140,  60),
    'damaged'   : (190,  55,  30),
    'destroyed' : ( 36,  30,  26),
    'ghost'     : (180, 190, 255),
    'ghost_path': (100, 110, 190),
    'ghost_fill': ( 50,  60, 110),
    'exp_a'     : (255, 180,  40),
    'exp_b'     : (255, 100,  20),
    'exp_c'     : (255, 240, 100),
    'money'     : (255, 215,   0),
    'btn'       : ( 34,  50,  80),
    'btn_hover' : ( 60,  90, 140),
    'btn_buy'   : ( 30,  90,  50),
    'btn_buy_h' : ( 50, 140,  80),
    'btn_dis'   : ( 40,  40,  50),
    'fish_col'  : ( 60, 190, 170),
    # Radar
    'radar_bg'  : (  4,  18,  10),
    'radar_grid': (  0,  60,  20),
    'radar_line': (  0, 220,  80),
    'radar_ping': ( 80, 255, 120),
    'radar_enemy': (255, 100,  40),
}

# ── Módulos ───────────────────────────────────────────────────────────────────
MODULE_DEFS = {
    # Tipo          nome                 largura   altura  hp      color  variavel    custo                      descricao
    'hull'      : {'name':'Casco',           'w':3,'h':2,'hp':6,  'color':'hull',     'cost':0,   'rx':0,'ry':0, 'desc':'Estrutura principal'},
    'mortar'    : {'name':'Morteiro',        'w':1,'h':1,'hp':2,  'color':'mortar',   'cost':120, 'rx':2,'ry':0, 'desc':'Canhão 1×1, alcance 14'},
    'armor'     : {'name':'Armadura',        'w':1,'h':1,'hp':5,  'color':'armor',    'cost':80,  'rx':1,'ry':0, 'desc':'Absorve dano de colisão'},
    'engine'    : {'name':'Motor Diesel',    'w':2,'h':1,'hp':3,  'color':'engine',   'cost':0,   'rx':0,'ry':1, 'desc':'Vel max 4, incluso'},
    'research'  : {'name':'Laboratório',     'w':2,'h':1,'hp':2,  'color':'research', 'cost':150, 'rx':0,'ry':0, 'desc':'+50% recompensa'},
    'radar'     : {'name':'Radar',           'w':1,'h':1,'hp':2,  'color':'research', 'cost':200, 'rx':2,'ry':1, 'desc':'+4 tiles de visão'},
    # Upgrades de motor
    'engine_nuclear'  : {'name':'Motor Nuclear',       'w':2,'h':1,'hp':4,'color':'engine','cost':300,'rx':0,'ry':1,'desc':'Vel max 6'},
    'engine_thermo'   : {'name':'Motor Termo-nuclear', 'w':2,'h':1,'hp':5,'color':'engine','cost':600,'rx':0,'ry':1,'desc':'Vel 8, silencioso'},
    # Upgrade de morteiro
    'mortar_heavy'    : {'name':'Morteiro Pesado',     'w':1,'h':1,'hp':3,'color':'mortar','cost':250,'rx':2,'ry':0,'desc':'Alcance 20, dano 2'},
}

UPGRADE_TREE = {
    'engine'        : 'engine_nuclear',
    'engine_nuclear': 'engine_thermo',
    'mortar'        : 'mortar_heavy',
}

# Expansao do tamanho do barco
HULL_UPGRADES = [
    (4, 3,  250),   # 3x2 → 4x3
    (5, 4,  500),   # 4x3 → 5x4
    (6, 5,  750),   # 5x4 → 6x5
    (7, 6, 1000),   # 6x5 → 7x6
]

# Direções cardeais: (nome, dx, dy, ângulo)
DIRS = {
    'N': (0, -1,  270),
    'S': (0,  1,   90),
    'E': (1,  0,    0),
    'W': (-1, 0,  180),
}
