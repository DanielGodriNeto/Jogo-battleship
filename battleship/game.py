# game.py

import pygame
import sys
import math
import random

from constants import (
    BASE_TILE, VP_PIXELS_W, VP_PIXELS_H, SIDEBAR_W, BOTTOM_H,
    MAP_SIZES, DEFAULT_MAP, FOG_RADIUS_BASE, FPS, C, MODULE_DEFS, UPGRADE_TREE
)
from entities import Ship, Fish, NPCShip, Module, Particle
from renderer import Renderer
from radar import Radar


class Game:
    def __init__(self):
        self.SCREEN_W = VP_PIXELS_W # Janela do jogo with
        self.SCREEN_H = VP_PIXELS_H # Janela do jogo height
        self.screen   = pygame.display.set_mode((self.SCREEN_W, self.SCREEN_H))
        pygame.display.set_caption("Batalha Naval 2  |  v0.4")
        self.clock    = pygame.time.Clock()

        #Fontes do jogo tamanho, negrito e tipo
        self.font_xs = pygame.font.SysFont('consolas', 11)
        self.font_sm = pygame.font.SysFont('consolas', 13)
        self.font_md = pygame.font.SysFont('consolas', 15, bold=True)
        self.font_lg = pygame.font.SysFont('consolas', 20, bold=True)
        
        #Estado do jogo: 'menu', 'play', 'end'
        self.state      = 'menu'
        self.map_choice = DEFAULT_MAP
        self.renderer   = Renderer(self)
        # Cria dois navios, um para cada jogador, e os posiciona em cantos opostos do mapa. O método _build_ship() instala os módulos iniciais (motor, morteiro, armadura, pesquisa e radar) em posições fixas no casco.
        self.ships     : list[Ship]     = []
        self.npcs      : list           = []
        self.particles : list[Particle] = []
        self.messages  : list[str]      = []
        self.radar     = Radar()
        self.winner    = None
        self.turn      = 0
        self.turn_absolute = 0
        self.grid_w, self.grid_h = MAP_SIZES[DEFAULT_MAP]
        self._set_zoom(1.0) # Inicializa tile e zoom baseados no grid_w/h
        self.map_grid  = [['water'] * self.grid_w for _ in range(self.grid_h)]

        self._menu_buttons = []
        self._shop_rects   = []
        self._ghost        = None
        self.cam_x = 0.0
        self.cam_y = 0.0
        self.transition_timer = 0
        self.last_phase = None
        self.steering = 0.0
        self.speed    = 2

        # Tooltip: (módulo, posição na tela) ou None

    # ─────────────────────── Geração de ilhas ──────────────────────────────────
    def generate_islands(self):
        gw, gh = self.grid_w, self.grid_h
        self.map_grid = [['water'] * gw for _ in range(gh)]
        margin = 2 # Reduzido para permitir ilhas em mapas de baixa altura
        protected = set()
        for px, py in [(4, 4), (gw - 8, gh - 8)]:
            for dx in range(-3, 7): # Proteção de spawn mais compacta
                for dy in range(-3, 7):
                    protected.add((px + dx, py + dy))

        max_radius  = max(2, min(5, gh // 6)) 
        num_islands = max(3, gw // 10)
        placed = attempts = 0

        while placed < num_islands and attempts < num_islands * 20:
            attempts += 1
            radius = random.randint(2, max_radius)
            
            # Calcula os limites e verifica se o intervalo é válido para evitar o ValueError
            x_min, x_max = margin + radius, gw - margin - radius - 1
            y_min, y_max = margin + radius, gh - margin - radius - 1
            if x_min >= x_max or y_min >= y_max: continue

            cx = random.randint(x_min, x_max)
            cy = random.randint(y_min, y_max)
            if any((cx + dx, cy + dy) in protected
                   for dx in range(-radius - 2, radius + 3)
                   for dy in range(-radius - 2, radius + 3)):
                continue
            for dx in range(-radius - 1, radius + 2):
                for dy in range(-radius - 1, radius + 2):
                    gx, gy = cx + dx, cy + dy
                    if not (0 < gx < gw - 1 and 0 < gy < gh - 1):
                        continue
                    dist = math.hypot(dx, dy) + random.uniform(-0.8, 0.8)
                    if   dist < radius * 0.28: self.map_grid[gy][gx] = 'stone'
                    elif dist < radius * 0.62: self.map_grid[gy][gx] = 'grass'
                    elif dist < radius:        self.map_grid[gy][gx] = 'sand'
            placed += 1

    # ─────────────────────── Init partida ──────────────────────────────────────
    def _init_game(self, map_key=DEFAULT_MAP):
        self.grid_w, self.grid_h = MAP_SIZES[map_key]
        self._set_zoom(1.0)
        self.generate_islands()
        self.radar = Radar()

        self.ships = [
            self._build_ship(4, 4, 0, 0),
            self._build_ship(self.grid_w - 8, self.grid_h - 8, 180, 1),
        ]

        self.npcs = []
        self.turn = self.turn_absolute = 0
        self.phase    = 'move' # Começa pelo planejamento de movimento
        self.winner   = None
        self._reset_controls()
        self.particles = []

        self._refresh_ghost()
        self._center_cam()
        self._log("╔ J1: Planeje seu movimento! ╗")
        self.state = 'play'

    # COlocar modulos nos barcos para todo barco comecar com os mesmos modulos
    def _build_ship(self, gx, gy, angle, pid) -> Ship:
        """Cria navio já com todos os módulos instalados em posições fixas."""
        s = Ship(gx, gy, angle, pid)
        # Organização do Casco 3x2 (sem sobreposições):
        s.modules.append(Module('research', rx=0, ry=0)) # Ocupa (0,0) e (1,0)
        s.modules.append(Module('mortar',   rx=2, ry=0)) # Ocupa (2,0)
        s.modules.append(Module('engine',   rx=0, ry=1)) # Ocupa (0,1) e (1,1)
        return s

    def _reset_controls(self):
        """Centraliza o reset de comandos para o próximo movimento/turno."""
        self.steering = 0.0
        self.speed    = 2

    # ─────────────────────── Zoom / câmera ─────────────────────────────────────
    def _set_zoom(self, factor):
        # Garante que o tile nunca seja menor do que o necessário para cobrir a tela
        # Usamos float para o cálculo do min_tile para evitar saltos bruscos
        min_t_w = self._vp_w() / self.grid_w
        min_t_h = self._vp_h() / self.grid_h
        min_tile = math.ceil(max(min_t_w, min_t_h))
        
        # Clampa o fator de zoom (min_zoom depende do tamanho da janela e do mapa)
        self.zoom = max(min_tile / BASE_TILE, min(2.5, factor))
        
        # Atualiza o tamanho real do tile
        self.tile = max(min_tile, int(BASE_TILE * self.zoom))
        self._center_cam()

    def _vp_w(self): return self.SCREEN_W
    def _vp_h(self): return self.SCREEN_H
    
    def _center_cam(self):
        if not self.ships: return
        
        cx, cy = self.ships[self.turn].center()
        vw, vh = self._vp_w() / self.tile, self._vp_h() / self.tile

        # Tenta centralizar no navio, mas respeita as bordas do mapa
        if self.grid_w > vw:
            self.cam_x = max(0.0, min(self.grid_w - vw, cx - vw / 2))
        else:
            self.cam_x = (self.grid_w - vw) / 2 # Centraliza mapa pequeno na tela

        if self.grid_h > vh:
            self.cam_y = max(0.0, min(self.grid_h - vh, cy - vh / 2))
        else:
            self.cam_y = (self.grid_h - vh) / 2

    # Parte que converte coordenadas do mundo para coordenadas da tela
    # Essa parte funciona pegando a posicao do tile no mundo e subtraindo a posicao da camera que depois multiplica pelo tamanho do tile
    # Formula: sx = (gx - cam_x) * tile, sy = (gy - cam_y) * tile
    def w2s(self, gx, gy):
        return (int((gx - self.cam_x) * self.tile),
                int((gy - self.cam_y) * self.tile))

    def s2w(self, sx, sy):
        return (sx / self.tile + self.cam_x,
                sy / self.tile + self.cam_y)

    def _in_vp(self, sx, sy):
        return 0 <= sx < self._vp_w() and 0 <= sy < self._vp_h()

    # ─────────────────────── Log ───────────────────────────────────────────────
    def _log(self, msg):
        self.messages.append(msg)
        if len(self.messages) > 7:
            self.messages.pop(0)

    # ─────────────────────── Visibilidade ──────────────────────────────────────
    # Neblina calcula quais tiles estao dentro do raio de visao usando a formula matematica 
    # dx* dx + dy * dy <= r * r, onde dx e dy sao as diferencas entre as coordenadas do tile e do centro do navio, e r é o raio de visao. 
    # O resultado é um conjunto de coordenadas de tiles que estao visiveis para o jogador.
    def _visible_tiles(self) -> set:
        if not self.ships: return set()
        cx, cy = self.ships[self.turn].center()
        r  = self.ships[self.turn].fog_radius()
        r2 = r * r
        icx, icy = int(cx), int(cy)
        return {(icx + dx, icy + dy)
                for dx in range(-r - 1, r + 2)
                for dy in range(-r - 1, r + 2)
                if dx * dx + dy * dy <= r2}

    # ─────────────────────── Explosão / colisão ────────────────────────────────
    def _explode_at_tile(self, wx, wy):
        sx, sy = self.w2s(wx + 0.5, wy + 0.5)
        # Criação de partículas removida

    def _check_island_collision(self, ship: Ship):
        hit_tiles = set()
        for wx, wy in ship.world_tiles():
            if 0 <= wx < self.grid_w and 0 <= wy < self.grid_h:
                if self.map_grid[wy][wx] != 'water':
                    hit_tiles.add((wx, wy))
            else:
                hit_tiles.add((wx, wy))
        if not hit_tiles: return
        self._log("⚠ Encalhado em uma ilha!")
        for wx, wy in hit_tiles:
            ship.take_damage_at(wx, wy)
            self._explode_at_tile(wx, wy)
        self._check_win()

    #Detecta colisao comparando os tiles ocupados pelos dois navios. Se houver eles levam dano e gera uma explosao
    def _check_collision(self):
        t0, t1 = set(self.ships[0].world_tiles()), set(self.ships[1].world_tiles())
        overlap = t0 & t1
        if overlap:
            self._log("⚠ Colisão!")
            for wx, wy in overlap:
                self.ships[0].take_damage_at(wx, wy)
                self.ships[1].take_damage_at(wx, wy)
                self._explode_at_tile(wx, wy)
            self._check_win()

    # ─────────────────────── Mecânica principal ────────────────────────────────
    def _execute_move(self):
        ship = self.ships[self.turn]
        ship.pending_move = (self.steering, self.speed)
        self.phase = 'action'

    def _resolve_round(self):
        # 1. Movimentação simultânea
        for s in self.ships:
            st, sp = s.pending_move
            s.apply_move(st, sp, self.grid_w, self.grid_h)
            self._check_island_collision(s)
        
        self._check_collision()
        if self.winner: return

        # 2. Resolução dos disparos
        # Pegamos os tiros planejados antes de limpar os dados
        p1_shot = self.ships[0].pending_shot
        p2_shot = self.ships[1].pending_shot

        if p1_shot:
            self.turn = 0
            self._fire_mortar(p1_shot[0], p1_shot[1], auto_shop=False)
        
        if p2_shot and not self.winner:
            self.turn = 1
            self._fire_mortar(p2_shot[0], p2_shot[1], auto_shop=False)

        self._check_win()
        # Limpa planos para a próxima rodada
        for s in self.ships:
            s.pending_move = (0.0, 0)
            s.pending_shot = None

        # 3. Finaliza a rodada e prepara transição para o J1 começar de novo
        if not self.winner:
            self.phase = 'resolved'
            self._end_turn()
        self._reset_controls()

    def _fire_mortar(self, tx, ty, auto_shop=True):
        shooter = self.ships[self.turn]
        target  = self.ships[1 - self.turn]
        
        # Verifica acerto em NPCs primeiro
        for npc in self.npcs:
            if npc.alive and npc.take_damage_at(tx, ty):
                reward = int(npc.money_reward() * (1.5 if shooter.has_research() else 1.0))
                shooter.money += reward
                self._hit_success("🎯 HIT! NPC abatido", tx, ty, auto_shop)
                return

        if target.take_damage_at(tx, ty, shooter.mortar_damage()):
            self._hit_success("🎯 HIT!", tx, ty, auto_shop)
        else:
            self._log("🌊 MISS!")
            if auto_shop: self._open_shop()

    def _check_win(self):
        for i, s in enumerate(self.ships):
            if not s.alive:
                self.winner = 1 - i
                self.phase  = 'end'
                self._log(f"╔ JOGADOR {self.winner+1} VENCEU! ╗")

    def _hit_success(self, msg, tx, ty, auto_shop=True):
        """Helper para centralizar lógica de acerto."""
        self._log(msg)
        self._explode_at_tile(tx, ty)
        self._check_win()
        if not self.winner and auto_shop:
            self._open_shop()

    def _open_shop(self):
        self.phase = 'shop'
        self._log(f"J{self.turn+1} — Loja. ENTER=pular")

    def _end_turn(self):
        self.last_phase = self.phase
        self.phase = 'transition'
        self.transition_timer = pygame.time.get_ticks()

    def _apply_turn_switch(self):
        # Logica de transição complexa para o novo fluxo
        if self.turn == 0 and self.last_phase == 'action':
            # P1 terminou de planejar -> Vai para J2 planejar
            self.turn = 1
            self.phase = 'move'
            self._reset_controls()
            self._refresh_ghost()
            self._center_cam()
            self._log("╔ J2: Planeje seu movimento e ataque! ╗")
        elif self.last_phase == 'resolved':
            # Rodada resolvida -> Volta para o J1 planejar novo movimento
            self.turn = 0
            self.turn_absolute += 1
            self.phase = 'move'
            self._reset_controls()
            self._refresh_ghost()
            self._center_cam()
            self._log(f"══ INÍCIO DA RODADA {self.turn_absolute+1} ══")

    def _refresh_ghost(self):
        if self.ships:
            self._ghost = self.ships[self.turn].preview_move(self.steering, self.speed, self.grid_w, self.grid_h)

    # ─────────────────────── NPCs ──────────────────────────────────────────────
    def _update_npcs(self):
        # Atualização de NPCs removida
        self.npcs = [n for n in self.npcs if n.alive]

    # ─────────────────────── Eventos ───────────────────────────────────────────
    def handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if self.state == 'menu':
                if e.type == pygame.MOUSEBUTTONDOWN:
                    for rect, action in self._menu_buttons:
                        if rect.collidepoint(e.pos):
                            if action == 'start': self._init_game(self.map_choice)
                            elif action in MAP_SIZES: self.map_choice = action
                return

            if e.type == pygame.MOUSEWHEEL:
                self._set_zoom(self.zoom + e.y * 0.12)
                continue

            if e.type == pygame.KEYDOWN:
                # Atalhos universais de Zoom
                if e.key == pygame.K_z: self._set_zoom(self.zoom + 0.15)
                elif e.key == pygame.K_x: self._set_zoom(self.zoom - 0.15)
                
                if e.key == pygame.K_r and self.phase == 'end':
                    self.state = 'menu'; return
                
                if self.phase == 'transition':
                    if e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        if pygame.time.get_ticks() - self.transition_timer >= 3000:
                            self._apply_turn_switch()
                    return

                if self.winner: continue
                
                ship = self.ships[self.turn]

                if self.phase == 'action':
                    if e.key in (pygame.K_SPACE, pygame.K_RETURN):
                        self._log("Ataque ignorado.")
                        if self.turn == 1: self._resolve_round()
                        else: self._end_turn()
                
                if self.phase == 'move':
                    if   e.key == pygame.K_LEFT:  self.steering = max(-45.0, self.steering - 15); self._refresh_ghost()
                    elif e.key == pygame.K_RIGHT: self.steering = min( 45.0, self.steering + 15); self._refresh_ghost()
                    elif e.key == pygame.K_UP:    self.speed = min(self.ships[self.turn].max_speed, self.speed + 1); self._refresh_ghost()
                    elif e.key == pygame.K_DOWN:  self.speed = max(1, self.speed - 1); self._refresh_ghost()
                    elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER): self._execute_move()

                elif self.phase == 'shop':
                    if e.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER): self._end_turn()

            if e.type == pygame.MOUSEBUTTONDOWN and not self.winner:
                mx, my = e.pos
                if self.phase == 'action' and self._in_vp(mx, my) and e.button == 1:
                    tx, ty = self.s2w(mx, my)
                    self.ships[self.turn].pending_shot = (int(tx), int(ty))
                    if self.turn == 1:
                        self._resolve_round()
                    else:
                        self._end_turn()
                elif self.phase == 'shop':
                    self._handle_shop_click(mx, my)

    def _handle_shop_click(self, mx, my):
        """Processa cliques na interface da loja."""
        for rect, action, mod_type in self._shop_rects:
            if rect.collidepoint(mx, my):
                if action == 'skip': self._end_turn(); return
                
                ship = self.ships[self.turn]
                costs = {'repair': 30, 'buy': MODULE_DEFS.get(mod_type, {}).get('cost', 0)}
                if action == 'upgrade':
                    up = UPGRADE_TREE.get(mod_type)
                    cost = MODULE_DEFS[up]['cost'] if up else 9999
                else: cost = costs.get(action, 9999)

                if ship.money >= cost:
                    ship.apply_purchase(action, mod_type)
                    self._log("Compra realizada!")
                else: self._log("Dinheiro insuficiente!")
                return

    # ─────────────────────── Render ────────────────────────────────────────────
    def draw(self):
        if self.state == 'menu':
            self.renderer.draw_menu()
            return

        if self.phase == 'end':
            self.renderer.draw_victory_screen()
            return

        if self.phase == 'transition':
            self.renderer.draw_transition_screen()
            return

        r       = self.renderer
        visible = self._visible_tiles()

        r.draw_world(visible)
        r.draw_fog(visible)

        for s in self.ships:
            r.draw_ship(s, visible)

        r.draw_particles(self.particles)

        if self.phase == 'move':
            r.draw_ghost(self._ghost, self.ships[self.turn])

        if self.phase == 'action':
            r.draw_mortar_range(self.ships[self.turn])
            r.draw_crosshair()
            
        # Desenha o Radar no canto superior direito
        radar_size = 150
        self.radar.draw(self.screen, self.SCREEN_W - radar_size - 20, 20, 
                        radar_size, radar_size / self.grid_w, 
                        self.ships, self.npcs, self.turn, self.grid_w, self.grid_h)

        # r.draw_sidebar() e r.draw_bottom() removidos

    def update(self):
        if self.state == 'play':
            self.radar.update(self.ships, self.npcs, self.turn, self.map_grid, self.grid_w, self.grid_h)
            self._check_win()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)