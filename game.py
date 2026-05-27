# game.py — Classe principal do jogo

import pygame
import sys
import math
import random

from constants import (
    BASE_TILE, VP_PIXELS_W, VP_PIXELS_H, SIDEBAR_W, BOTTOM_H,
    MAP_SIZES, DEFAULT_MAP, FOG_RADIUS_BASE, FPS, C, MODULE_DEFS, HULL_UPGRADES
)
from entities import Ship, Fish, NPCShip, Module, Particle
from renderer import Renderer
from radar import Radar


class Game:
    def __init__(self):
        self.SCREEN_W = VP_PIXELS_W + SIDEBAR_W
        self.SCREEN_H = VP_PIXELS_H + BOTTOM_H
        self.screen   = pygame.display.set_mode((self.SCREEN_W, self.SCREEN_H))
        pygame.display.set_caption("Batalha Naval 2  |  v0.3")
        self.clock    = pygame.time.Clock()

        self.font_xs = pygame.font.SysFont('consolas', 11)
        self.font_sm = pygame.font.SysFont('consolas', 13)
        self.font_md = pygame.font.SysFont('consolas', 15, bold=True)
        self.font_lg = pygame.font.SysFont('consolas', 20, bold=True)

        # Zoom: só o mundo escala — HUD fica fixo
        self.tile = BASE_TILE
        self.zoom = 1.0

        self.state      = 'menu'
        self.map_choice = DEFAULT_MAP

        self.renderer = Renderer(self)

        # Atributos inicializados antes de _init_game
        self.ships     : list[Ship]     = []
        self.npcs      : list           = []
        self.particles : list[Particle] = []
        self.messages  : list[str]      = []
        self.phase     = 'move'
        self.winner    = None
        self.turn      = 0
        self.turn_absolute = 0
        self.grid_size = MAP_SIZES[DEFAULT_MAP]
        self.radar     = Radar()
        self._menu_buttons = []
        self._shop_rects   = []
        self._ghost        = None
        self.pending_mod   = None
        self.cam_x = 0.0
        self.cam_y = 0.0
        self.steering = 0.0
        self.speed    = 2

    # ─────────────────────── Init partida ─────────────────────────────────────
    def _init_game(self, map_key=DEFAULT_MAP):
        self.grid_size = MAP_SIZES[map_key]
        self.tile, self.zoom = BASE_TILE, 1.0

        self.ships = [
            self._build_ship(4, 4, 0, 0),
            self._build_ship(self.grid_size - 8, self.grid_size - 8, 180, 1),
        ]

        self.npcs = []
        for _ in range(12):
            self.npcs.append(Fish(random.randint(2, self.grid_size - 2),
                                  random.randint(2, self.grid_size - 2)))
        for _ in range(4):
            self.npcs.append(NPCShip(random.uniform(10, self.grid_size - 10),
                                     random.uniform(10, self.grid_size - 10)))

        self.turn           = 0
        self.turn_absolute  = 0
        self.phase          = 'move'
        self.winner         = None
        self.steering       = 0.0
        self.speed          = 2
        self.particles      = []
        self.messages       = []
        self.pending_mod    = None
        self.radar          = Radar()

        self._refresh_ghost()
        self._center_cam()
        self._log("╔ Vez do Jogador 1 — Mover barco ╗")
        self.state = 'play'

    def _build_ship(self, gx, gy, angle, pid) -> Ship:
        s = Ship(gx, gy, angle, pid)
        s.modules.append(Module('hull'))
        s.modules.append(Module('engine'))
        s.modules.append(Module('mortar'))
        return s

    # ─────────────────────── Zoom ─────────────────────────────────────────────
    def _set_zoom(self, factor):
        """Aplica zoom apenas ao mundo. HUD e minimapa ficam fixos."""
        self.zoom = max(0.4, min(2.5, factor))
        self.tile = max(6, int(BASE_TILE * self.zoom))
        self._center_cam()

    # ─────────────────────── Câmera ───────────────────────────────────────────
    def _vp_w(self): return VP_PIXELS_W
    def _vp_h(self): return VP_PIXELS_H

    def _center_cam(self):
        cx, cy = self.ships[self.turn].center()
        vis_cols = self._vp_w() / self.tile
        vis_rows = self._vp_h() / self.tile
        self.cam_x = max(0.0, min(self.grid_size - vis_cols, cx - vis_cols / 2))
        self.cam_y = max(0.0, min(self.grid_size - vis_rows, cy - vis_rows / 2))

    # ─────────────────────── Conversão coord ──────────────────────────────────
    def w2s(self, gx, gy):
        """Mundo → tela (só a área do viewport)."""
        return (
            int((gx - self.cam_x) * self.tile),
            int((gy - self.cam_y) * self.tile),
        )

    def s2w(self, sx, sy):
        """Tela → mundo (float)."""
        return (
            sx / self.tile + self.cam_x,
            sy / self.tile + self.cam_y,
        )

    def _in_vp(self, sx, sy):
        return 0 <= sx < self._vp_w() and 0 <= sy < self._vp_h()

    # ─────────────────────── Log ──────────────────────────────────────────────
    def _log(self, msg):
        self.messages.append(msg)
        if len(self.messages) > 7:
            self.messages.pop(0)

    # ─────────────────────── Neblina ──────────────────────────────────────────
    def _visible_tiles(self) -> set:
        cx, cy = self.ships[self.turn].center()
        r      = self.ships[self.turn].fog_radius()
        r2     = r * r
        icx, icy = int(cx), int(cy)
        return {(icx + dx, icy + dy) for dx in range(-r - 1, r + 2)
                for dy in range(-r - 1, r + 2) if dx * dx + dy * dy <= r2}

    # ─────────────────────── Explosão ─────────────────────────────────────────
    def _explode_at_tile(self, wx, wy):
        sx, sy = self.w2s(wx + 0.5, wy + 0.5)
        for _ in range(28):
            self.particles.append(Particle(sx, sy))

    # ─────────────────────── Mecânica ─────────────────────────────────────────
    def _execute_move(self):
        ship = self.ships[self.turn]
        ship.apply_move(self.steering, self.speed)
        self._center_cam()
        self._log(f"J{self.turn+1} navegou! Rumo {ship.angle:.0f}°, vel {self.speed}")

        self._check_collision()
        if self.winner:
            return

        if ship.has_mortar():
            self.phase = 'action'
            self._log(f"J{self.turn+1} — Ataque! Clique no alvo (SPACE=pular)")
        else:
            self._open_shop()

        self.steering = 0.0
        self.speed    = 2

    def _check_collision(self):
        t0 = set(self.ships[0].world_tiles())
        t1 = set(self.ships[1].world_tiles())
        overlap = t0 & t1
        if overlap:
            self._log("⚠ COLISÃO!")
            for wx, wy in overlap:
                if not self.ships[1].has_armor(): self.ships[0].take_damage_at(wx, wy)
                if not self.ships[0].has_armor(): self.ships[1].take_damage_at(wx, wy)
                self._explode_at_tile(wx, wy)
            self._check_win()

    def _fire_mortar(self, tx, ty):
        shooter = self.ships[self.turn]
        target  = self.ships[1 - self.turn]
        cx, cy  = shooter.center()

        if math.hypot(tx - cx, ty - cy) > shooter.mortar_range():
            self._log("Fora do alcance!")
            return

        dmg     = shooter.mortar_damage()
        hit_npc = False

        for npc in list(self.npcs):
            if npc.alive and npc.take_damage_at(tx, ty, dmg):
                reward = int(npc.money_reward() * 1.2) if shooter.has_research() else npc.money_reward()
                shooter.money += reward
                self._log(f"NPC destruído! +${reward}")
                hit_npc = True
                break

        if not hit_npc:
            hit = target.take_damage_at(tx, ty, dmg)
            self._explode_at_tile(tx, ty)
            self._log(f"J{self.turn+1} → ({tx},{ty}) — {'ACERTO!' if hit else 'água.'}")
            if hit and not target.alive:
                reward = int(500 * 1.2) if shooter.has_research() else 500
                shooter.money += reward
                self._log(f"+${reward} (barco destruído!)")

        self._explode_at_tile(tx, ty)
        self._check_win()
        if not self.winner:
            self._open_shop()

    def _open_shop(self):
        self.phase = 'shop'
        self._log(f"J{self.turn+1} — Loja (ENTER=pular)")

    def _check_win(self):
        for i, ship in enumerate(self.ships):
            if not ship.alive:
                self.winner = 1 - i
                self.phase  = 'end'
                self._log(f"══ JOGADOR {self.winner+1} VENCEU! ══")
                self._log("Pressione R para reiniciar.")

    def _end_turn(self):
        self.turn          = 1 - self.turn
        self.turn_absolute += 1
        self.phase         = 'move'
        self.steering      = 0.0
        self.speed         = 2
        self._refresh_ghost()
        self._center_cam()
        self._log(f"Vez do Jogador {self.turn+1} — Mover barco")

    def _refresh_ghost(self):
        if self.ships:
            self._ghost = self.ships[self.turn].preview_move(self.steering, self.speed)

    # ─────────────────────── Construção ───────────────────────────────────────
    def _is_valid_placement(self, ship: Ship, mod: Module, rx, ry) -> bool:
        """Verifica se o módulo pode ser colocado em (rx, ry) relativo ao barco."""
        mod.rx, mod.ry = rx, ry
        new_tiles = set(mod.local_tiles())
        h = ship.hull
        if not h:
            return False

        # Deve estar dentro do casco
        hull_tiles = set(h.local_tiles())
        if not new_tiles.issubset(hull_tiles):
            return False

        # Não pode sobrepor módulos existentes
        existing = set()
        for m in ship.modules:
            if not m.destroyed and m.type != 'hull':
                existing.update(m.local_tiles())
        if new_tiles & existing:
            return False

        return True

    # ─────────────────────── NPCs ─────────────────────────────────────────────
    def _update_npcs(self):
        if self.phase == 'action':
            return
        for npc in self.npcs:
            npc.update()
        self.npcs = [n for n in self.npcs if n.alive]

    # ─────────────────────── Eventos ──────────────────────────────────────────
    def handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            # ── MENU ─────────────────────────────────────────────────────────
            if self.state == 'menu':
                if e.type == pygame.MOUSEBUTTONDOWN:
                    for (rect, action) in self._menu_buttons:
                        if rect.collidepoint(e.pos):
                            if action == 'start':
                                self._init_game(self.map_choice)
                            elif action in MAP_SIZES:
                                self.map_choice = action
                return

            # ── SCROLL DO MOUSE (zoom) ────────────────────────────────────────
            if e.type == pygame.MOUSEWHEEL:
                self._set_zoom(self.zoom + e.y * 0.12)
                continue

            # ── TECLADO ───────────────────────────────────────────────────────
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r and self.phase == 'end':
                    self.state = 'menu'; return
                if self.winner:
                    continue

                if self.phase == 'move':
                    if e.key == pygame.K_LEFT:
                        self.steering = max(-90.0, self.steering - 15)
                        self._refresh_ghost()
                    elif e.key == pygame.K_RIGHT:
                        self.steering = min(90.0, self.steering + 15)
                        self._refresh_ghost()
                    elif e.key == pygame.K_UP:
                        self.speed = min(self.ships[self.turn].max_speed, self.speed + 1)
                        self._refresh_ghost()
                    elif e.key == pygame.K_DOWN:
                        self.speed = max(1, self.speed - 1)
                        self._refresh_ghost()
                    elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        self._execute_move()
                    elif e.key == pygame.K_z:
                        self._set_zoom(self.zoom + 0.15)
                    elif e.key == pygame.K_x:
                        self._set_zoom(self.zoom - 0.15)

                elif self.phase == 'action':
                    if e.key in (pygame.K_SPACE, pygame.K_RETURN):
                        self._log("Ataque pulado.")
                        self._open_shop()
                    elif e.key == pygame.K_z:
                        self._set_zoom(self.zoom + 0.15)
                    elif e.key == pygame.K_x:
                        self._set_zoom(self.zoom - 0.15)

                elif self.phase == 'shop':
                    if e.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self._end_turn()

                elif self.phase == 'build':
                    if e.key == pygame.K_r and self.pending_mod:
                        self.pending_mod.rotated = not self.pending_mod.rotated
                    elif e.key in (pygame.K_ESCAPE,):
                        self.phase = 'shop'
                        self._log("Construção cancelada.")

            # ── MOUSE ─────────────────────────────────────────────────────────
            if e.type == pygame.MOUSEBUTTONDOWN and not self.winner:
                mx, my = e.pos

                if self.phase == 'action' and self._in_vp(mx, my) and e.button == 1:
                    tx, ty = self.s2w(mx, my)
                    self._fire_mortar(int(tx), int(ty))

                elif self.phase == 'shop':
                    for (rect, action, mod_type) in self._shop_rects:
                        if rect.collidepoint(mx, my):
                            if action == 'skip':
                                self._end_turn()
                                return
                            ship = self.ships[self.turn]
                            if action == 'hull_expand':
                                if ship.can_afford('hull_expand', 'hull'):
                                    ship.apply_purchase('hull_expand', 'hull')
                                    self._log(f"Casco expandido para {ship.hull.w}×{ship.hull.h}!")
                                else:
                                    self._log("Dinheiro insuficiente!")
                                return
                            if ship.can_afford(action, mod_type):
                                if action == 'buy':
                                    self.pending_mod = Module(mod_type)
                                    self.phase = 'build'
                                    self._log(f"Posicionando {MODULE_DEFS[mod_type]['name']} (R rotaciona)")
                                else:
                                    ship.apply_purchase(action, mod_type)
                                    self._log("Transação concluída.")
                            else:
                                self._log("Dinheiro insuficiente!")
                            return

                elif self.phase == 'build' and self._in_vp(mx, my):
                    if e.button == 1:
                        tx, ty = self.s2w(mx, my)
                        ship   = self.ships[self.turn]
                        rx, ry = int(tx - ship.gx), int(ty - ship.gy)
                        if self._is_valid_placement(ship, self.pending_mod, rx, ry):
                            ship.apply_purchase('buy', self.pending_mod.type, self.pending_mod)
                            self.pending_mod = None
                            self.phase = 'shop'
                            self._log("Módulo construído!")
                        else:
                            self._log("Posição inválida! (dentro do casco, sem sobreposição)")
                    elif e.button == 3:
                        self.phase = 'shop'
                        self._log("Construção cancelada.")

    # ─────────────────────── Render ───────────────────────────────────────────
    def draw(self):
        if self.state == 'menu':
            self.renderer.draw_menu()
            return

        r = self.renderer

        # Área do mundo (recebe zoom)
        visible = self._visible_tiles()
        r.draw_water()
        r.draw_npcs(visible)
        r.draw_ship(self.ships[1 - self.turn], visible)
        if self.phase == 'move':
            r.draw_ghost(self._ghost, self.ships[self.turn])
        r.draw_ship(self.ships[self.turn], visible)
        if self.phase == 'action':
            r.draw_mortar_range(self.ships[self.turn])
            r.draw_crosshair()
        if self.phase == 'build':
            r.draw_build_overlay(self.ships[self.turn], self.pending_mod)
        r.draw_fog(visible)

        # Partículas (posição em pixels — não escala com zoom aqui)
        self.particles = [p for p in self.particles if p.life > 0]
        r.draw_particles(self.particles)

        # HUD fixa (nunca sofre zoom)
        r.draw_sidebar()
        r.draw_bottom()

    # ─────────────────────── Loop principal ───────────────────────────────────
    def run(self):
        while True:
            if self.state == 'play':
                self._update_npcs()
                self.radar.update(self.ships, self.npcs, self.turn)

            self.handle_events()
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)
