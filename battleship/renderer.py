# renderer.py — Toda a lógica de desenho

import pygame
import math
from constants import (C, MODULE_DEFS, SIDEBAR_W, BOTTOM_H,
                        VP_PIXELS_W, VP_PIXELS_H)
from entities import Ship, Fish, NPCShip, lerp_color


def draw_text(surf, text, font, color, pos):
    s = font.render(text, True, color)
    surf.blit(s, pos)


class Renderer:
    """Cuida de todo o desenho do jogo. Recebe referência ao Game."""

    def __init__(self, game):
        self.g = game   # referência ao Game

    # ── Atalhos ───────────────────────────────────────────────────────────────
    @property
    def tile(self):   return self.g.tile
    @property
    def screen(self): return self.g.screen
    @property
    def cam_x(self):  return self.g.cam_x
    @property
    def cam_y(self):  return self.g.cam_y

    def w2s(self, gx, gy): return self.g.w2s(gx, gy)
    def _in_vp(self, sx, sy): return self.g._in_vp(sx, sy)
    def _vp_w(self): return VP_PIXELS_W
    def _vp_h(self): return VP_PIXELS_H

    # ═══════════════════════════════════════════════════════════════════════════
    # Menu
    # ═══════════════════════════════════════════════════════════════════════════
    def draw_menu(self):
        from constants import MAP_SIZES
        g = self.g
        surf = self.screen
        surf.fill((30, 40, 60))  # cor de fundo mais escura e simples

        # Título simples
        title = g.font_lg.render("BATALHA NAVAL", True, (255, 255, 255))
        surf.blit(title, (g.SCREEN_W // 2 - title.get_width() // 2, 60))

        y = 130
        g._menu_buttons = []

        # Escolha de tamanho do mapa
        ms = g.font_md.render("Tamanho do mapa:", True, (220, 220, 220))
        surf.blit(ms, (g.SCREEN_W // 2 - ms.get_width() // 2, y))
        y += 30

        bw, bh = 90, 30
        total_w = len(MAP_SIZES) * (bw + 10) - 10
        bx_start = g.SCREEN_W // 2 - total_w // 2
        for i, key in enumerate(MAP_SIZES):
            bx = bx_start + i * (bw + 10)
            rect = pygame.Rect(bx, y, bw, bh)
            sel = key == g.map_choice
            col = (80, 120, 180) if sel else (60, 80, 120)
            pygame.draw.rect(surf, col, rect)
            pygame.draw.rect(surf, (200, 200, 200), rect, 1)
            lbl = g.font_sm.render(key, True, (255, 255, 255) if sel else (200, 200, 200))
            surf.blit(lbl, (bx + bw // 2 - lbl.get_width() // 2, y + 4))
            g._menu_buttons.append((rect, key))
        y += bh + 20

        # Botão iniciar
        sw, sh = 160, 38
        sx = g.SCREEN_W // 2 - sw // 2
        rect_start = pygame.Rect(sx, y, sw, sh)
        pygame.draw.rect(surf, (60, 180, 80), rect_start)
        pygame.draw.rect(surf, (200, 200, 200), rect_start, 1)
        ts = g.font_md.render("INICIAR", True, (255, 255, 255))
        surf.blit(ts, (sx + sw // 2 - ts.get_width() // 2, y + sh // 2 - ts.get_height() // 2))
        g._menu_buttons.append((rect_start, 'start'))
        y += sh + 30

        # Não exibe instruções de teclas no menu

    # ═══════════════════════════════════════════════════════════════════════════
    # Mundo
    # ═══════════════════════════════════════════════════════════════════════════
    def draw_water(self):
        """Desenha água e grade. Respeita tile atual (com zoom)."""
        t = self.tile
        vis_cols = int(self._vp_w() / t) + 2
        vis_rows = int(self._vp_h() / t) + 2
        for row in range(vis_rows):
            for col in range(vis_cols):
                wx = int(self.cam_x) + col
                wy = int(self.cam_y) + row
                sx, sy = self.w2s(wx, wy)
                col_c = C['water_a'] if (wx + wy) % 2 == 0 else C['water_b']
                pygame.draw.rect(self.screen, col_c, (sx, sy, t + 1, t + 1))
                pygame.draw.rect(self.screen, C['grid_line'], (sx, sy, t, t), 1)
                if wx % 10 == 0 and wy % 10 == 0:
                    lbl = self.g.font_xs.render(f"{wx},{wy}", True, C['grid_line'])
                    self.screen.blit(lbl, (sx + 2, sy + 2))

    def draw_fog(self, visible):
        t  = self.tile
        ft = pygame.Surface((t + 1, t + 1), pygame.SRCALPHA)
        ft.fill((8, 12, 24, 210))
        vis_cols = int(self._vp_w() / t) + 2
        vis_rows = int(self._vp_h() / t) + 2
        for row in range(vis_rows):
            for col in range(vis_cols):
                wx = int(self.cam_x) + col
                wy = int(self.cam_y) + row
                if (wx, wy) not in visible:
                    sx, sy = self.w2s(wx, wy)
                    self.screen.blit(ft, (sx, sy))

    def draw_npcs(self, visible):
        t = self.tile
        for npc in self.g.npcs:
            wx, wy = int(npc.gx), int(npc.gy)
            if (wx, wy) not in visible:
                continue
            sx, sy = self.w2s(npc.gx, npc.gy)
            if not self._in_vp(sx, sy):
                continue
            if isinstance(npc, Fish):
                rad = math.radians(npc.angle)
                cx, cy = sx + t / 2, sy + t / 2
                pts = [
                    (cx + math.cos(rad) * t * 0.4,    cy + math.sin(rad) * t * 0.4),
                    (cx + math.cos(rad + 2.4) * t * 0.2, cy + math.sin(rad + 2.4) * t * 0.2),
                    (cx + math.cos(rad - 2.4) * t * 0.2, cy + math.sin(rad - 2.4) * t * 0.2),
                ]
                pygame.draw.polygon(self.screen, C['fish_col'], pts)
            elif isinstance(npc, NPCShip):
                col = lerp_color(C['damaged'], C['npc_ship'], npc.hp / npc.max_hp)
                pygame.draw.rect(self.screen, col, (sx + 3, sy + 3, t - 6, t - 6))
                pygame.draw.rect(self.screen, C['npc_ship'], (sx + 3, sy + 3, t - 6, t - 6), 1)

    def draw_ship(self, ship: Ship, visible: set):
        t  = self.tile
        ox, oy = int(ship.gx), int(ship.gy)

        for m in ship.modules:
            for (rx, ry) in m.local_tiles():
                wx, wy = ox + rx, oy + ry
                if (wx, wy) not in visible:
                    continue
                sx, sy = self.w2s(wx, wy)
                if not self._in_vp(sx, sy):
                    continue

                if m.type == 'hull':
                    # Casco fica mais escuro se tiver módulo em cima
                    has_top = any(
                        other.type != 'hull' and not other.destroyed
                        and (rx, ry) in other.local_tiles()
                        for other in ship.modules
                    )
                    col = tuple(int(c * 0.55) for c in m.color) if has_top else m.color
                    pad = 1
                else:
                    col = m.color
                    pad = 4

                pygame.draw.rect(self.screen, col, (sx + pad, sy + pad, t - pad * 2, t - pad * 2))
                pygame.draw.rect(self.screen, ship.player_color,
                                 (sx + pad, sy + pad, t - pad * 2, t - pad * 2), 1)

                if m.destroyed:
                    pygame.draw.line(self.screen, C['destroyed'],
                                     (sx + 4, sy + 4), (sx + t - 4, sy + t - 4), 2)
                    pygame.draw.line(self.screen, C['destroyed'],
                                     (sx + t - 4, sy + 4), (sx + 4, sy + t - 4), 2)
                elif m.type != 'hull':
                    cx_, cy_ = sx + t // 2, sy + t // 2
                    if 'mortar' in m.type:
                        pygame.draw.circle(self.screen, (20, 12, 4), (cx_, cy_), t // 5)
                        pygame.draw.circle(self.screen, (70, 50, 8), (cx_, cy_), t // 8)
                    elif m.type == 'armor':
                        pygame.draw.rect(self.screen, (40, 80, 120),
                                         (sx + pad + 2, sy + pad + 2, t - pad * 2 - 4, t - pad * 2 - 4), 2)
                    elif 'engine' in m.type:
                        for i in range(3):
                            ey = sy + pad + 2 + i * (t - pad * 2 - 4) // 3
                            pygame.draw.line(self.screen, (100, 40, 120),
                                             (sx + pad, ey), (sx + t - pad, ey), 2)
                    elif m.type in ('research', 'radar'):
                        pygame.draw.circle(self.screen, (30, 100, 50), (cx_, cy_), t // 5, 2)

                    # HP dots
                    dot_r = max(1, t // 12)
                    for i in range(m.max_hp):
                        dc = (50, 200, 80) if i < m.hp else (80, 30, 30)
                        pygame.draw.circle(self.screen, dc,
                                           (sx + pad + 2 + i * (dot_r * 2 + 1), sy + pad + 2), dot_r)

        # Seta de heading
        if ship.hull and not ship.hull.destroyed:
            cx, cy = ship.center()
            scx, scy = self.w2s(cx, cy)
            if self._in_vp(scx, scy):
                rad = math.radians(ship.angle)
                ex  = scx + int(math.cos(rad) * t * 1.8)
                ey  = scy + int(math.sin(rad) * t * 1.8)
                pygame.draw.line(self.screen, ship.player_color, (scx, scy), (ex, ey), 2)
                pygame.draw.polygon(self.screen, ship.player_color, [
                    (ex, ey),
                    (ex + int(math.cos(rad + 2.5) * 5), ey + int(math.sin(rad + 2.5) * 5)),
                    (ex + int(math.cos(rad - 2.5) * 5), ey + int(math.sin(rad - 2.5) * 5)),
                ])

        # Barra de HP
        h = ship.hull
        if h and not h.destroyed:
            ox_, oy_ = int(ship.gx), int(ship.gy)
            bx, by = self.w2s(ox_, oy_)
            by += t * h.h + 2
            bw  = t * h.w - 4
            ratio = h.hp / h.max_hp
            pygame.draw.rect(self.screen, (40, 20, 20), (bx, by, bw, 4))
            hpc = (int(200 * (1 - ratio) + 40 * ratio), int(40 * (1 - ratio) + 200 * ratio), 40)
            pygame.draw.rect(self.screen, hpc, (bx, by, int(bw * ratio), 4))

    def draw_ghost(self, ghost, ship: Ship):
        if not ghost:
            return
        nx, ny, na, path = ghost
        t = self.tile
        for i, (px, py) in enumerate(path):
            scx, scy = self.w2s(px + 1.5, py + 1.0)
            r = 3 if i < len(path) - 1 else 5
            pygame.draw.circle(self.screen, C['ghost_path'], (scx, scy), r)

        h = ship.hull
        if h:
            for (rx, ry) in h.local_tiles():
                sx, sy = self.w2s(int(nx) + rx, int(ny) + ry)
                pygame.draw.rect(self.screen, C['ghost_fill'], (sx + 3, sy + 3, t - 6, t - 6))
                pygame.draw.rect(self.screen, C['ghost'],      (sx + 3, sy + 3, t - 6, t - 6), 1)
            gcx, gcy = nx + h.w / 2, ny + h.h / 2
            gsx, gsy = self.w2s(gcx, gcy)
            grad = math.radians(na)
            gex  = gsx + int(math.cos(grad) * t * 1.5)
            gey  = gsy + int(math.sin(grad) * t * 1.5)
            pygame.draw.line(self.screen, C['ghost'], (gsx, gsy), (gex, gey), 1)

    def draw_mortar_range(self, ship: Ship):
        if not ship.has_mortar():
            return
        cx, cy   = ship.center()
        scx, scy = self.w2s(cx, cy)
        r_pix    = ship.mortar_range() * self.tile
        overlay  = pygame.Surface((self._vp_w(), self._vp_h()), pygame.SRCALPHA)
        pygame.draw.circle(overlay, (255, 200, 50, 22), (scx, scy), r_pix)
        pygame.draw.circle(overlay, (255, 200, 50, 90), (scx, scy), r_pix, 2)
        self.screen.blit(overlay, (0, 0))

    def draw_crosshair(self):
        mx, my = pygame.mouse.get_pos()
        if not self._in_vp(mx, my):
            return
        tx, ty = self.g.s2w(mx, my)
        sx, sy = self.w2s(int(tx), int(ty))
        t = self.tile
        ov = pygame.Surface((t, t), pygame.SRCALPHA)
        ov.fill((255, 60, 60, 55))
        pygame.draw.rect(ov, (255, 60, 60, 200), (0, 0, t, t), 2)
        self.screen.blit(ov, (sx, sy))
        half = t // 2
        pygame.draw.line(self.screen, (255, 60, 60), (sx, sy + half), (sx + t, sy + half), 1)
        pygame.draw.line(self.screen, (255, 60, 60), (sx + half, sy), (sx + half, sy + t), 1)

    def draw_build_overlay(self, ship: Ship, pending_mod):
        if not pending_mod:
            return
        mx, my = pygame.mouse.get_pos()
        if not self._in_vp(mx, my):
            return
        tx, ty = self.g.s2w(mx, my)
        rx, ry = int(tx - ship.gx), int(ty - ship.gy)

        valid = self.g._is_valid_placement(ship, pending_mod, rx, ry)
        color = (50, 255, 50, 120) if valid else (255, 50, 50, 120)

        for dx in range(pending_mod.current_w):
            for dy in range(pending_mod.current_h):
                sx, sy = self.w2s(ship.gx + rx + dx, ship.gy + ry + dy)
                s = pygame.Surface((self.tile, self.tile), pygame.SRCALPHA)
                s.fill(color)
                self.screen.blit(s, (sx, sy))

    def draw_particles(self, particles):
        for p in particles:
            p.update()
            p.draw(self.screen)

    # ═══════════════════════════════════════════════════════════════════════════
    # HUD fixa (sidebar + bottom)
    # ═══════════════════════════════════════════════════════════════════════════
    def draw_sidebar(self):
        g    = self.g
        x0   = self._vp_w()
        surf = self.screen

        pygame.draw.rect(surf, C['ui_bg'], (x0, 0, SIDEBAR_W, g.SCREEN_H))
        pygame.draw.line(surf, C['ui_border'], (x0, 0), (x0, g.SCREEN_H), 2)

        y = 10

        def line(text, color=None, font=None, indent=0):
            nonlocal y
            col = color or C['text']
            f   = font  or g.font_sm
            s   = f.render(text, True, col)
            surf.blit(s, (x0 + 12 + indent, y))
            y  += s.get_height() + 2

        def sep():
            nonlocal y
            pygame.draw.line(surf, C['ui_border'],
                             (x0 + 6, y + 3), (x0 + SIDEBAR_W - 6, y + 3))
            y += 9

        ship = g.ships[g.turn]
        pc   = C['p1'] if g.turn == 0 else C['p2']
        line(f"JOGADOR {g.turn+1}", pc, g.font_lg)

        money_surf = g.font_md.render(f"${ship.money}", True, C['money'])
        surf.blit(money_surf, (x0 + SIDEBAR_W - money_surf.get_width() - 10, 10))

        if g.phase == 'end' and g.winner is not None:
            wc = C['p1'] if g.winner == 0 else C['p2']
            line(f"J{g.winner+1} VENCEU!", wc, g.font_md)
            line("R = Menu", C['highlight'])
        else:
            labels = {'move': 'NAVEGAÇÃO', 'action': 'ATAQUE', 'shop': 'LOJA',
                      'build': 'CONSTRUÇÃO', 'end': 'FIM'}
            line(f"Fase: {labels.get(g.phase, g.phase)}", C['highlight'], g.font_md)

        sep()

        if g.phase == 'move':
            line("CONTROLES", C['text_dim'])
            line(f"← →  Leme: {g.steering:+.0f}°",         indent=6)
            line(f"↑ ↓  Vel: {g.speed}/{ship.max_speed}",   indent=6)
            line(f"     Rumo: {ship.angle:.0f}°",            indent=6)
            line("ENTER Confirmar", C['highlight'], indent=6)
            line("Scroll/Z/X Zoom", C['text_dim'], indent=6)

        elif g.phase == 'action':
            line("MORTEIRO", C['text_dim'])
            if ship.has_mortar():
                line(f"Alcance: {ship.mortar_range()} tiles", indent=6)
                line(f"Dano:    {ship.mortar_damage()}×",      indent=6)
            line("SPACE = Pular", C['highlight'], indent=6)

        elif g.phase == 'build':
            line("CONSTRUÇÃO", C['highlight'], g.font_md)
            if g.pending_mod:
                line(f"Alocando: {g.pending_mod.name}", indent=6)
                line(f"Tamanho: {g.pending_mod.current_w}×{g.pending_mod.current_h}", indent=6)
            line("R = Rotacionar", C['highlight'], indent=6)
            line("Click = Colocar", indent=6)
            line("Dir / ESC = Cancelar", C['text_dim'], indent=6)

        elif g.phase == 'shop':
            self._draw_shop(x0, y)
            return

        sep()

        # Módulos
        line("MÓDULOS", C['text_dim'])
        for m in ship.modules:
            if m.type == 'hull':
                h = ship.hull
                line(f"  Casco {h.w}×{h.h}  {h.hp}/{h.max_hp}HP", C[h.color_key], g.font_xs)
                continue
            hp_str = "✕ DESTRUÍDO" if m.destroyed else f"{m.hp}/{m.max_hp}HP"
            mc = m.color if not m.destroyed else C['damaged']
            line(f"  {m.name[:14]:14s}{hp_str}", mc, g.font_xs)

        sep()

        # Radar (substitui minimapa simples)
        mm_w  = SIDEBAR_W - 24
        g.radar.draw(surf, x0, y, mm_w, mm_w / g.grid_size,
                     g.ships, g.npcs, g.turn, g.grid_size)
        y += mm_w + 30   # pula radar + lat/lon

        sep()
        line("LOG", C['text_dim'])
        for msg in g.messages[-5:]:
            c = C['highlight'] if ('══' in msg or '╔' in msg) else C['text_dim']
            s = g.font_xs.render(msg[:34], True, c)
            surf.blit(s, (x0 + 10, y))
            y += s.get_height() + 1

    def _draw_shop(self, x0, y):
        g = self.g
        ship = g.ships[g.turn]
        g._shop_rects = []
        surf = self.screen
        mouse = pygame.mouse.get_pos()

        def line(text, color=None, font=None):
            nonlocal y
            s = (font or g.font_sm).render(text, True, color or C['text'])
            surf.blit(s, (x0 + 12, y))
            y += s.get_height() + 2

        def sep():
            nonlocal y
            pygame.draw.line(surf, C['ui_border'],
                             (x0 + 6, y + 3), (x0 + SIDEBAR_W - 6, y + 3))
            y += 8

        sep()
        line(f"LOJA  Saldo: ${ship.money}", C['money'], g.font_md)
        sep()

        items = ship.available_purchases()
        BW, BH = SIDEBAR_W - 24, 38

        for (action, mod_type, name, cost, can, desc) in items[:6]:
            rect = pygame.Rect(x0 + 12, y, BW, BH)
            hov  = rect.collidepoint(mouse)
            if not can:
                bg = C['btn_dis']
            elif action == 'hull_expand':
                bg = (0, 80, 120) if not hov else (0, 110, 160)
            elif hov:
                bg = C['btn_buy_h']
            else:
                bg = C['btn_buy']
            pygame.draw.rect(surf, bg, rect, border_radius=4)
            pygame.draw.rect(surf, C['ui_border'], rect, 1, border_radius=4)

            tc = C['text'] if can else C['text_dim']
            label = g.font_sm.render(f"{name[:18]} ${cost}", True, tc)
            desc_s = g.font_xs.render(desc[:32], True, C['text_dim'])
            surf.blit(label, (x0 + 16, y + 4))
            surf.blit(desc_s, (x0 + 16, y + 20))

            g._shop_rects.append((rect, action, mod_type))
            y += BH + 4

        sep()
        rect_skip = pygame.Rect(x0 + 12, y, BW, 28)
        hov = rect_skip.collidepoint(mouse)
        pygame.draw.rect(surf, C['btn_hover'] if hov else C['btn'], rect_skip, border_radius=4)
        ts = g.font_sm.render("ENTER / Pular turno", True, C['highlight'])
        surf.blit(ts, (x0 + 16, y + 5))
        g._shop_rects.append((rect_skip, 'skip', ''))
        y += 36

        sep()
        mm_w = SIDEBAR_W - 24
        g.radar.draw(surf, x0, y, mm_w, mm_w / g.grid_size,
                     g.ships, g.npcs, g.turn, g.grid_size)

    def draw_bottom(self):
        g    = self.g
        surf = self.screen
        y0   = self._vp_h()

        pygame.draw.rect(surf, C['ui_bg'], (0, y0, self._vp_w(), BOTTOM_H))
        pygame.draw.line(surf, C['ui_border'], (0, y0), (self._vp_w(), y0), 2)

        for i, ship in enumerate(g.ships):
            c = C['p1'] if i == 0 else C['p2']
            h = ship.hull
            hp_r = h.hp / h.max_hp if (h and h.max_hp > 0) else 0
            lbl  = f"J{i+1} Casco {h.hp}/{h.max_hp}" if (h and not h.destroyed) else f"J{i+1} AFUNDOU"
            surf.blit(g.font_md.render(lbl, True, c), (12 + i * 250, y0 + 6))

            bx, by, bw, bh = 12 + i * 250, y0 + 28, 210, 8
            pygame.draw.rect(surf, (40, 20, 20), (bx, by, bw, bh))
            if hp_r > 0:
                bar_c = (int(200 * (1 - hp_r) + 40 * hp_r), int(40 * (1 - hp_r) + 200 * hp_r), 40)
                pygame.draw.rect(surf, bar_c, (bx, by, int(bw * hp_r), bh))
            pygame.draw.rect(surf, c, (bx, by, bw, bh), 1)

            ms = g.font_xs.render(f"${ship.money}", True, C['money'])
            surf.blit(ms, (bx, y0 + 42))

            if i == g.turn and g.phase != 'end':
                pygame.draw.polygon(surf, C['highlight'], [
                    (bx - 14, y0 + 14), (bx - 6, y0 + 20), (bx - 14, y0 + 26)
                ])

        hint = {
            'move'  : "← → Leme   ↑ ↓ Vel   ENTER Mover   Scroll/Z/X Zoom",
            'action': "Mouse = Mirar   Click = Fogo   SPACE = Pular",
            'shop'  : "Clique = Comprar/Expandir   ENTER = Pular loja",
            'build' : "Click = Colocar   R = Rotacionar   Dir/ESC = Cancelar",
            'end'   : "R = Menu",
        }.get(g.phase, "")
        hs = g.font_sm.render(hint, True, C['text_dim'])
        surf.blit(hs, (self._vp_w() // 2 - hs.get_width() // 2, y0 + 62))
