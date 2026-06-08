# renderer.py

import pygame
import math
import os
from constants import C, MODULE_DEFS, UPGRADE_TREE, SIDEBAR_W, BOTTOM_H, VP_PIXELS_W, VP_PIXELS_H
from entities import Ship, Fish, NPCShip, lerp_color

class Renderer:
    def __init__(self, game):
        self.g = game
        self.sprite_cache = {}
        self.last_tile = -1
        self.assets_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Sprites battleship")

    @property
    def tile(self):   return self.g.tile
    @property
    def screen(self): return self.g.screen
    @property
    def cam_x(self):  return self.g.cam_x
    @property
    def cam_y(self):  return self.g.cam_y

    def w2s(self, gx, gy):       return self.g.w2s(gx, gy)
    def _in_vp(self, sx, sy):    return self.g._in_vp(sx, sy)
    def _vp_w(self):             return VP_PIXELS_W
    def _vp_h(self):             return VP_PIXELS_H

    def _get_sprite(self, category, name, size=None):
        """Carrega, redimensiona e armazena sprites em cache. Se não encontrar, cria um fallback visual."""
        if self.tile != self.last_tile:
            self.sprite_cache.clear()
            self.last_tile = self.tile

        key = (category, name, size)
        if key in self.sprite_cache:
            return self.sprite_cache[key]

        # Mapeamento para os nomes de arquivos em português da sua pasta
        mapping = {
            "water": "Agua",
            "sand": "Areia",
            "grass": "Grama",
            "stone": "Montanha",
            "hull": "Navio",
            "mortar": "Missel 1.0",
            "mortar_heavy": "Missel 2.0",
            "radar": "Radar",
            "pirate": "Navio"
        }
        filename = mapping.get(name, name)

        # Procura o arquivo .png diretamente na pasta "Sprites battleship"
        path = os.path.join(self.assets_path, f"{filename}.png")

        img = None
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
            except:
                pass

        try:
            # Adicionamos 1px extra em tiles de terreno (size is None) para evitar vãos de arredondamento
            extra = 1 if not size else 0
            w = int((size[0] if size else 1) * self.tile) + extra
            h = int((size[1] if size else 1) * self.tile) + extra
            img = pygame.transform.scale(img, (w, h))
            self.sprite_cache[key] = img
            return img
        except:
            # Fallback sólido sem cantos arredondados para as peças encostarem perfeitamente
            w = (size[0] if size else 1) * self.tile
            h = (size[1] if size else 1) * self.tile
            fallback = pygame.Surface((int(w), int(h)), pygame.SRCALPHA)
            color = C.get(name, (100, 100, 100))
            fallback.fill(color)
            pygame.draw.rect(fallback, (255, 255, 255, 40), (0, 0, w, h), 1)
            self.sprite_cache[key] = fallback
            return fallback

    def _draw_rotated_sprite(self, sprite, center_pos, angle):
        """Desenha um sprite rotacionado, ajustando para o sistema de coordenadas do jogo."""
        # Ajuste para o sistema de coordenadas do jogo (0 graus = Leste)
        rotated = pygame.transform.rotate(sprite, -angle)
        rect = rotated.get_rect(center=center_pos)
        self.screen.blit(rotated, rect.topleft)

    def _draw_hp_bar(self, x, y, w, ratio):
        """Helper para desenhar barras de vida consistentes."""
        if ratio <= 0: return
        pygame.draw.rect(self.screen, (40, 20, 20), (x, y, w, 4))
        # Cor transiciona de Verde para Vermelho baseado no ratio
        hpc = (int(200 * (1 - ratio) + 40 * ratio), int(40 * (1 - ratio) + 200 * ratio), 40)
        pygame.draw.rect(self.screen, hpc, (x, y, int(w * ratio), 4))

    # ═══════════════════════════════════════════════════════════════════════════
    # Menu
    # ═══════════════════════════════════════════════════════════════════════════
    def draw_menu(self):
        from constants import MAP_SIZES
        g    = self.g
        surf = self.screen
        surf.fill((30, 40, 60))

        title = g.font_lg.render("BATALHA NAVAL 2", True, (255, 255, 255))
        surf.blit(title, (g.SCREEN_W // 2 - title.get_width() // 2, 60))

        y = 150
        g._menu_buttons = []

        ms = g.font_md.render("Tamanho do mapa:", True, (220, 220, 220))
        surf.blit(ms, (g.SCREEN_W // 2 - ms.get_width() // 2, y))
        y += 30

        bw, bh = 90, 30
        total_w  = len(MAP_SIZES) * (bw + 10) - 10
        bx_start = g.SCREEN_W // 2 - total_w // 2
        for i, key in enumerate(MAP_SIZES):
            bx   = bx_start + i * (bw + 10)
            rect = pygame.Rect(bx, y, bw, bh)
            sel  = key == g.map_choice
            col  = (80, 120, 180) if sel else (60, 80, 120)
            pygame.draw.rect(surf, col, rect)
            pygame.draw.rect(surf, (200, 200, 200), rect, 1)
            lbl = g.font_sm.render(key, True, (255, 255, 255) if sel else (200, 200, 200))
            surf.blit(lbl, (bx + bw // 2 - lbl.get_width() // 2, y + 4))
            g._menu_buttons.append((rect, key))
        y += bh + 20

        sw, sh = 160, 38
        sx = g.SCREEN_W // 2 - sw // 2
        rect_start = pygame.Rect(sx, y, sw, sh)
        pygame.draw.rect(surf, C['btn_buy'], rect_start)
        pygame.draw.rect(surf, (200, 200, 200), rect_start, 1)
        ts = g.font_md.render("INICIAR", True, (255, 255, 255))
        surf.blit(ts, (sx + sw // 2 - ts.get_width() // 2, y + sh // 2 - ts.get_height() // 2))
        g._menu_buttons.append((rect_start, 'start'))

    # ═══════════════════════════════════════════════════════════════════════════
    # Mundo / tiles
    # ═══════════════════════════════════════════════════════════════════════════
    def draw_world(self, visible: set):
        g  = self.g
        t  = self.tile
        gs = g.grid_size
        self.screen.fill(C['ui_bg'])

        col0 = max(0, int(self.cam_x) - 1)
        row0 = max(0, int(self.cam_y) - 1)
        col1 = min(gs, col0 + int(self._vp_w() / t) + 3)
        row1 = min(gs, row0 + int(self._vp_h() / t) + 3)

        for gy in range(row0, row1):
            for gx in range(col0, col1):
                sx, sy  = self.w2s(gx, gy)
                terrain = g.map_grid[gy][gx]
                
                # Desenha sprite do terreno (água, areia, etc)
                tile_sprite = self._get_sprite("tiles", terrain)
                self.screen.blit(tile_sprite, (sx, sy))

        self.draw_npcs(visible)

    def draw_fog(self, visible):
        t  = self.tile
        ft = pygame.Surface((t + 1, t + 1), pygame.SRCALPHA)
        ft.fill((8, 12, 24, 210))
        for row in range(int(self._vp_h() / t) + 2):
            for col in range(int(self._vp_w() / t) + 2):
                wx, wy = int(self.cam_x) + col, int(self.cam_y) + row
                if (wx, wy) not in visible:
                    sx, sy = self.w2s(wx, wy)
                    self.screen.blit(ft, (sx, sy))

    def draw_npcs(self, visible):
        t = self.tile
        for npc in self.g.npcs:
            wx, wy = int(npc.gx), int(npc.gy)
            if (wx, wy) not in visible: continue
            sx, sy = self.w2s(wx, wy)
            if not self._in_vp(sx, sy): continue

            if isinstance(npc, Fish):
                fish_sprite = self._get_sprite("npcs", "fish")
                self._draw_rotated_sprite(fish_sprite, (sx + t/2, sy + t/2), npc.angle)

            elif isinstance(npc, NPCShip):
                npc_sprite = self._get_sprite("npcs", "pirate")
                self.screen.blit(npc_sprite, (sx, sy))
                self._draw_hp_bar(sx + 3, sy - 7, t - 6, npc.hp / npc.max_hp)

    # ═══════════════════════════════════════════════════════════════════════════
    # Navio
    # ═══════════════════════════════════════════════════════════════════════════
    def draw_ship(self, ship: Ship, visible: set):
        t  = self.tile
        ox, oy = round(ship.gx), round(ship.gy)
        # Ordenar módulos: Desenhar o 'hull' (casco) primeiro, depois o resto
        sorted_mods = sorted(ship.modules, key=lambda m: 0 if m.type == 'hull' else 1)

        for m in sorted_mods:
            rx_first, ry_first = m.local_tiles()[0]
            wx, wy = ox + rx_first, oy + ry_first
            
            if (wx, wy) not in visible: continue
            sx, sy = self.w2s(wx, wy)
            if not self._in_vp(sx, sy): continue

            # Desenha o sprite do módulo (Hull, Mortar, etc)
            mod_sprite = self._get_sprite("modules", m.type, (m.current_w, m.current_h))
            if m.rotated:
                mod_sprite = pygame.transform.rotate(mod_sprite, 90)
            
            self.screen.blit(mod_sprite, (sx, sy))
            
            # Feedback de destruição
            if m.destroyed:
                overlay = pygame.Surface((m.current_w * t, m.current_h * t), pygame.SRCALPHA)
                overlay.fill((20, 0, 0, 160))
                self.screen.blit(overlay, (sx, sy))
                pygame.draw.line(self.screen, C['destroyed'], (sx, sy), (sx + m.current_w*t, sy + m.current_h*t), 3)
            
            # Pontos de vida (HP) pequenos em cima do módulo
            if not m.destroyed and m.type != 'hull':
                dot_r = max(2, t // 10)
                for i in range(m.max_hp):
                    col = (50, 255, 100) if i < m.hp else (255, 50, 50)
                    pygame.draw.circle(self.screen, col, (sx + 8 + i*(dot_r*2 + 2), sy + 8), dot_r)

        h = ship.hull
        if h and not h.destroyed:
            cx, cy = ship.center()
            if (int(cx), int(cy)) in visible:
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
                    bx, by = self.w2s(round(ship.gx), round(ship.gy))
                    by += t * h.h + 2
                    self._draw_hp_bar(bx, by, t * h.w - 4, h.hp / h.max_hp)

    def draw_ghost(self, ghost, ship: Ship):
        if not ghost: return
        nx, ny, na, path = ghost
        t = self.tile
        for i, (px, py) in enumerate(path):
            scx, scy = self.w2s(px + 1.5, py + 1.0)
            pygame.draw.circle(self.screen, C['ghost_path'], (scx, scy), 3 if i < len(path) - 1 else 5)
        h = ship.hull
        if h:
            for rx, ry in h.local_tiles():
                sx, sy = self.w2s(round(nx) + rx, round(ny) + ry)
                pygame.draw.rect(self.screen, C['ghost_fill'], (sx + 3, sy + 3, t - 6, t - 6))
                pygame.draw.rect(self.screen, C['ghost'],      (sx + 3, sy + 3, t - 6, t - 6), 1)
            gsx, gsy = self.w2s(nx + h.w / 2, ny + h.h / 2)
            grad = math.radians(na)
            gex  = gsx + int(math.cos(grad) * t * 1.5)
            gey  = gsy + int(math.sin(grad) * t * 1.5)
            pygame.draw.line(self.screen, C['ghost'], (gsx, gsy), (gex, gey), 1)

    def draw_mortar_range(self, ship: Ship):
        if not ship.has_mortar(): return
        cx, cy   = ship.center()
        scx, scy = self.w2s(cx, cy)
        r_pix    = ship.mortar_range() * self.tile
        overlay  = pygame.Surface((self._vp_w(), self._vp_h()), pygame.SRCALPHA)
        pygame.draw.circle(overlay, (255, 200, 50, 22), (scx, scy), r_pix)
        pygame.draw.circle(overlay, (255, 200, 50, 90), (scx, scy), r_pix, 2)
        self.screen.blit(overlay, (0, 0))

    def draw_crosshair(self):
        mx, my = pygame.mouse.get_pos()
        if not self._in_vp(mx, my): return
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

    def draw_particles(self, particles):
        for p in particles:
            p.draw(self.screen)

    # ═══════════════════════════════════════════════════════════════════════════
    # HUD — sidebar e bottom
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
        line(f"Dinheiro: ${ship.money}", C['money'], g.font_md)

        sep()
        
        if g.phase == 'end' and g.winner is not None:
            wc = C['p1'] if g.winner == 0 else C['p2']
            line(f"J{g.winner+1} VENCEU!", wc, g.font_md)
            line("R = Menu", C['highlight'])
        else:
            labels = {'move': 'NAVEGAÇÃO', 'action': 'ATAQUE', 'shop': 'LOJA', 'end': 'FIM'}
            line(f"Fase: {labels.get(g.phase, g.phase)}", C['highlight'], g.font_md)

        sep()

        line("CONTROLES", C['text_dim'])
        if g.phase == 'move':
            line(f"← → Leme: {g.steering:+.0f}°", indent=6)
            line(f"↑ ↓ Vel: {g.speed}/{ship.max_speed}", indent=6)
            line(f"Rumo: {ship.angle:.0f}°", indent=6)
            line("ENTER: Confirmar", C['highlight'], indent=6)
        elif g.phase == 'action':
            line("Mira: Mouse", indent=6)
            line("Atirar: Clique", indent=6)
            line("Pular: ESPAÇO", C['highlight'], indent=6)
            if ship.has_mortar():
                line(f"Alcance: {ship.mortar_range()} tiles", C['text_dim'], indent=6)
                line(f"Dano: {ship.mortar_damage()}x", C['text_dim'], indent=6)

        elif g.phase == 'shop':
            self._draw_shop(x0, y)
            return

        sep()
        line("MÓDULOS", C['text_dim'])
        for m in ship.modules:
            if m.type == 'hull': # Casco está sempre presente e não é destruído
                line(f"  Casco: {m.hp}/{m.max_hp} HP", C[m.color_key], g.font_xs)
            else:
                hp_str = "DESTRUÍDO" if m.destroyed else f"{m.hp}/{m.max_hp} HP"
                mc = C['damaged'] if m.destroyed else m.color # Usa a cor do módulo se não estiver destruído
                line(f"  {m.name}: {hp_str}", mc, g.font_xs)

        line("Zoom: Z/X ou Scroll", C['text_dim'], indent=6)
        sep()

        mm_w = SIDEBAR_W - 24
        g.radar.draw(surf, x0, y, mm_w, mm_w / g.grid_size,
                     g.ships, g.npcs, g.turn, g.grid_size)
        y += mm_w + 30

        sep()
        line("LOG", C['text_dim'])
        for msg in g.messages[-5:]:
            c = C['highlight'] if ('══' in msg or '╔' in msg) else C['text_dim']
            surf.blit(g.font_xs.render(msg[:34], True, c), (x0 + 10, y))
            y += g.font_xs.get_height() + 1

    def _draw_shop(self, x0, y):
        g    = self.g
        ship = g.ships[g.turn]
        g._shop_rects = []
        surf  = self.screen
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
        BW, BH = SIDEBAR_W - 24, 30 # Altura do botão reduzida para visual mais compacto

        for action, mod_type, name, cost, can, desc in items: # Iterar todos os itens
            rect = pygame.Rect(x0 + 12, y, BW, BH)
            hov  = rect.collidepoint(mouse)
            if not can:          bg = C['btn_dis']
            elif hov:            bg = C['btn_buy_h']
            else:                bg = C['btn_buy']
            pygame.draw.rect(surf, bg, rect, border_radius=4)
            pygame.draw.rect(surf, C['ui_border'], rect, 1, border_radius=4)
            tc = C['text'] if can else C['text_dim']
            surf.blit(g.font_sm.render(f"{name} (${cost})", True, tc), (x0 + 16, y + (BH // 2) - (g.font_sm.get_height() // 2))) # Centraliza texto verticalmente
            g._shop_rects.append((rect, action, mod_type))
            y += BH + 4

        sep()
        rect_skip = pygame.Rect(x0 + 12, y, BW, 28)
        hov = rect_skip.collidepoint(mouse)
        pygame.draw.rect(surf, C['btn_hover'] if hov else C['btn'], rect_skip, border_radius=4)
        surf.blit(g.font_sm.render("ENTER / Pular turno", True, C['highlight']), (x0 + 16, y + 5))
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
            c   = C['p1'] if i == 0 else C['p2']
            h   = ship.hull
            lbl  = f"J{i+1} Casco {h.hp}/{h.max_hp}" if (h and not h.destroyed) else f"J{i+1} AFUNDOU"
            surf.blit(g.font_md.render(lbl, True, c), (12 + i * 250, y0 + 6))

            bx, by, bw = 12 + i * 250, y0 + 28, 210
            self._draw_hp_bar(bx, by, bw, h.hp / h.max_hp if h else 0)
            surf.blit(g.font_xs.render(f"${ship.money}", True, C['money']), (bx, y0 + 42))

            if i == g.turn and g.phase != 'end':
                pygame.draw.polygon(surf, C['highlight'], [
                    (bx - 14, y0 + 14), (bx - 6, y0 + 20), (bx - 14, y0 + 26)
                ])

        hint = {
            'move'  : "← → Leme   ↑ ↓ Vel   ENTER Mover   Scroll/Z/X Zoom",
            'action': "Mouse = Mirar   Click = Fogo   SPACE = Pular",
            'shop'  : "Clique = Comprar/Upgrade   ENTER = Pular loja",
            'end'   : "R = Menu",
        }.get(g.phase, "")
        hs = g.font_sm.render(hint, True, C['text_dim'])
        surf.blit(hs, (self._vp_w() // 2 - hs.get_width() // 2, y0 + 62))
