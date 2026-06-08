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
        self.SCREEN_W = VP_PIXELS_W + SIDEBAR_W
        self.SCREEN_H = VP_PIXELS_H + BOTTOM_H
        self.screen   = pygame.display.set_mode((self.SCREEN_W, self.SCREEN_H))
        pygame.display.set_caption("Batalha Naval 2  |  v0.4")
        self.clock    = pygame.time.Clock()

        self.font_xs = pygame.font.SysFont('consolas', 11)
        self.font_sm = pygame.font.SysFont('consolas', 13)
        self.font_md = pygame.font.SysFont('consolas', 15, bold=True)
        self.font_lg = pygame.font.SysFont('consolas', 20, bold=True)

        self.tile = BASE_TILE
        self.zoom = 1.0

        self.state      = 'menu'
        self.map_choice = DEFAULT_MAP
        self.renderer   = Renderer(self)

        self.ships     : list[Ship]     = []
        self.npcs      : list           = []
        self.particles : list[Particle] = []
        self.messages  : list[str]      = []
        self.phase     = 'move'
        self.winner    = None
        self.turn      = 0
        self.turn_absolute = 0
        self.grid_size = MAP_SIZES[DEFAULT_MAP]
        self.map_grid  = [['water'] * self.grid_size for _ in range(self.grid_size)]
        self.radar     = Radar()

        self._menu_buttons = []
        self._shop_rects   = []
        self._ghost        = None
        self.cam_x = 0.0
        self.cam_y = 0.0
        self.steering = 0.0
        self.speed    = 2

        # Tooltip: (módulo, posição na tela) ou None

    # ─────────────────────── Geração de ilhas ──────────────────────────────────
    def generate_islands(self):
        gs = self.grid_size
        self.map_grid = [['water'] * gs for _ in range(gs)]
        margin = 6
        protected = set()
        for px, py in [(4, 4), (gs - 8, gs - 8)]:
            for dx in range(-6, 12):
                for dy in range(-6, 12):
                    protected.add((px + dx, py + dy))

        max_radius  = max(3, min(7, gs // 10))
        num_islands = max(2, gs // 12)
        placed = attempts = 0

        while placed < num_islands and attempts < num_islands * 20:
            attempts += 1
            radius = random.randint(2, max_radius)
            cx = random.randint(margin + radius, gs - margin - radius - 1)
            cy = random.randint(margin + radius, gs - margin - radius - 1)
            if any((cx + dx, cy + dy) in protected
                   for dx in range(-radius - 2, radius + 3)
                   for dy in range(-radius - 2, radius + 3)):
                continue
            for dx in range(-radius - 1, radius + 2):
                for dy in range(-radius - 1, radius + 2):
                    gx, gy = cx + dx, cy + dy
                    if not (0 < gx < gs - 1 and 0 < gy < gs - 1):
                        continue
                    dist = math.hypot(dx, dy) + random.uniform(-0.8, 0.8)
                    if   dist < radius * 0.28: self.map_grid[gy][gx] = 'stone'
                    elif dist < radius * 0.62: self.map_grid[gy][gx] = 'grass'
                    elif dist < radius:        self.map_grid[gy][gx] = 'sand'
            placed += 1

    # ─────────────────────── Init partida ──────────────────────────────────────
    def _init_game(self, map_key=DEFAULT_MAP):
        self.grid_size = MAP_SIZES[map_key]
        self.tile, self.zoom = BASE_TILE, 1.0
        self.generate_islands()

        self.ships = [
            self._build_ship(4, 4, 0, 0),
            self._build_ship(self.grid_size - 8, self.grid_size - 8, 180, 1),
        ]

        water_tiles = [
            (x, y) for y in range(2, self.grid_size - 2)
            for x in range(2, self.grid_size - 2)
            if self.map_grid[y][x] == 'water'
        ]
        random.shuffle(water_tiles)
        self.npcs = []
        fish_count = min(12, len(water_tiles))
        npc_count  = min(4,  len(water_tiles) - fish_count)
        for i in range(fish_count):
            self.npcs.append(Fish(*water_tiles[i]))
        for i in range(npc_count):
            self.npcs.append(NPCShip(*map(float, water_tiles[fish_count + i])))

        self.turn = self.turn_absolute = 0
        self.phase    = 'move'
        self.winner   = None
        self.steering = 0.0
        self.speed    = 2
        self.particles = []
        self.messages  = []
        self.radar     = Radar()

        self._refresh_ghost()
        self._center_cam()
        self._log("╔ Vez do Jogador 1 — Mover barco ╗")
        self.state = 'play'

    def _build_ship(self, gx, gy, angle, pid) -> Ship:
        """Cria navio já com todos os módulos instalados em posições fixas."""
        s = Ship(gx, gy, angle, pid)
        # Linha 0 do casco: armor (col 1), mortar (col 2)
        # Linha 1 do casco: engine (cols 0-1), radar (col 2)
        s.modules.append(Module('engine',   rx=0, ry=1))
        s.modules.append(Module('mortar',   rx=2, ry=0))
        s.modules.append(Module('armor',    rx=1, ry=0))
        s.modules.append(Module('research', rx=0, ry=0))
        s.modules.append(Module('radar',    rx=2, ry=1))
        return s

    # ─────────────────────── Zoom / câmera ─────────────────────────────────────
    def _set_zoom(self, factor):
        self.zoom = max(0.4, min(2.5, factor))
        self.tile = max(6, int(BASE_TILE * self.zoom))
        self._center_cam()

    def _vp_w(self): return VP_PIXELS_W
    def _vp_h(self): return VP_PIXELS_H

    def _center_cam(self):
        if not self.ships: return
        cx, cy = self.ships[self.turn].center()
        vc = self._vp_w() / self.tile
        vr = self._vp_h() / self.tile
        self.cam_x = max(0.0, min(self.grid_size - vc, cx - vc / 2))
        self.cam_y = max(0.0, min(self.grid_size - vr, cy - vr / 2))

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
        for _ in range(28):
            self.particles.append(Particle(sx, sy))

    def _check_island_collision(self, ship: Ship):
        hit_tiles = set()
        for wx, wy in ship.world_tiles():
            if 0 <= wx < self.grid_size and 0 <= wy < self.grid_size:
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

    def _check_collision(self):
        t0, t1 = set(self.ships[0].world_tiles()), set(self.ships[1].world_tiles())
        overlap = t0 & t1
        if overlap:
            self._log("⚠ Colisão!")
            for wx, wy in overlap:
                if not self.ships[1].has_armor(): self.ships[0].take_damage_at(wx, wy)
                if not self.ships[0].has_armor(): self.ships[1].take_damage_at(wx, wy)
                self._explode_at_tile(wx, wy)
            self._check_win()

    # ─────────────────────── Mecânica principal ────────────────────────────────
    def _execute_move(self):
        ship = self.ships[self.turn]
        ship.apply_move(self.steering, self.speed, self.grid_size)
        self._center_cam()
        self._log(f"Jogador {self.turn+1} navegou! Rumo {ship.angle:.0f}°, velocidade {self.speed}")
        self._check_island_collision(ship)
        if self.winner: return
        self._check_collision()
        if self.winner: return
        if ship.has_mortar():
            self.phase = 'action'
            self._log(f"J{self.turn+1} — Ataque! Clique no alvo (SPACE=pular)")
        else:
            self._open_shop()
        self.steering = 0.0
        self.speed    = 2

    def _fire_mortar(self, tx, ty):
        shooter = self.ships[self.turn]
        target  = self.ships[1 - self.turn]
        cx, cy  = shooter.center()
        if math.hypot(tx - cx, ty - cy) > shooter.mortar_range() + 0.5: # Adicionado uma pequena tolerância
            self._log("Fora do alcance!"); return
        for npc in self.npcs:
            if npc.alive and npc.take_damage_at(tx, ty):
                reward = int(npc.money_reward() * (1.5 if shooter.has_research() else 1.0))
                shooter.money += reward
                self._log(f"NPC abatido! +${reward}")
                self._explode_at_tile(tx, ty)
                self._open_shop()
                return
        damage_dealt = shooter.mortar_damage()
        if target.take_damage_at(tx, ty, damage_dealt):
            self._log(f"Acerto! -{damage_dealt} HP")
            self._explode_at_tile(tx, ty)
            self._check_win()
            if not self.winner: self._open_shop()
        else:
            self._log("Errou!")
            self._open_shop()

    def _check_win(self):
        for i, s in enumerate(self.ships):
            if not s.alive:
                self.winner = 1 - i
                self.phase  = 'end'
                self._log(f"╔ JOGADOR {self.winner+1} VENCEU! ╗")

    def _open_shop(self):
        self.phase = 'shop'
        self._log(f"J{self.turn+1} — Loja. ENTER=pular")

    def _end_turn(self):
        self.turn = 1 - self.turn
        self.turn_absolute += 1
        self.phase    = 'move'
        self.steering = 0.0
        self.speed    = 2
        self._refresh_ghost()
        self._center_cam()
        self._log(f"╔ Vez do Jogador {self.turn+1} — Mover barco ╗")

    def _refresh_ghost(self):
        if self.ships:
            self._ghost = self.ships[self.turn].preview_move(self.steering, self.speed, self.grid_size)

    # ─────────────────────── NPCs ──────────────────────────────────────────────
    def _update_npcs(self):
        if self.phase == 'action': return
        for npc in self.npcs:
            if isinstance(npc, NPCShip): npc.update(self.map_grid)
            else:                        npc.update()
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
                if e.key == pygame.K_r and self.phase == 'end':
                    self.state = 'menu'; return
                if self.winner: continue

                if self.phase == 'move':
                    if   e.key == pygame.K_LEFT:  self.steering = max(-45.0, self.steering - 15); self._refresh_ghost()
                    elif e.key == pygame.K_RIGHT: self.steering = min( 45.0, self.steering + 15); self._refresh_ghost()
                    elif e.key == pygame.K_UP:    self.speed = min(self.ships[self.turn].max_speed, self.speed + 1); self._refresh_ghost()
                    elif e.key == pygame.K_DOWN:  self.speed = max(1, self.speed - 1); self._refresh_ghost()
                    elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER): self._execute_move()
                    elif e.key == pygame.K_z: self._set_zoom(self.zoom + 0.15)
                    elif e.key == pygame.K_x: self._set_zoom(self.zoom - 0.15)

                elif self.phase == 'action':
                    if e.key in (pygame.K_SPACE, pygame.K_RETURN):
                        self._log("Ataque pulado."); self._open_shop()
                    elif e.key == pygame.K_z: self._set_zoom(self.zoom + 0.15)
                    elif e.key == pygame.K_x: self._set_zoom(self.zoom - 0.15)

                elif self.phase == 'shop':
                    if e.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER):
                        self._end_turn()

            if e.type == pygame.MOUSEBUTTONDOWN and not self.winner:
                mx, my = e.pos

                if self.phase == 'action' and self._in_vp(mx, my) and e.button == 1:
                    tx, ty = self.s2w(mx, my)
                    self._fire_mortar(int(tx), int(ty))

                elif self.phase == 'shop':
                    for rect, action, mod_type in self._shop_rects:
                        if rect.collidepoint(mx, my):
                            if action == 'skip':
                                self._end_turn(); return
                            
                            ship = self.ships[self.turn]
                            can_afford = False
                            
                            if action == 'upgrade':
                                up = UPGRADE_TREE.get(mod_type)
                                can_afford = up is not None and ship.money >= MODULE_DEFS[up]['cost']
                            elif action == 'repair':
                                can_afford = ship.money >= 30
                            elif action == 'buy':
                                can_afford = ship.money >= MODULE_DEFS[mod_type]['cost']

                            if can_afford:
                                ship.apply_purchase(action, mod_type)
                                self._log("Transação concluída.")
                            else:
                                self._log("Dinheiro insuficiente!")
                            return

    # ─────────────────────── Render ────────────────────────────────────────────
    def draw(self):
        if self.state == 'menu':
            self.renderer.draw_menu()
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

        r.draw_sidebar()
        r.draw_bottom()

    def update(self):
        if self.state == 'play':
            self._update_npcs()
            # Atualiza e remove partículas mortas
            for p in self.particles: p.update()
            self.particles = [p for p in self.particles if p.life > 0]
            self.radar.update(self.ships, self.npcs, self.turn, self.map_grid, self.grid_size)

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)