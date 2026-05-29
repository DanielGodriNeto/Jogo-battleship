# radar.py — Sistema de radar/sonar

import pygame
import math
import random
from constants import C, SIDEBAR_W


class Radar:
    """Radar estilo sonar: linha giratória verde, pings coloridos por tipo."""

    # Duração dos pings em frames
    PING_LIFE_NPC    = 200   # NPCShip: amarelo
    PING_LIFE_FISH   = 160   # Peixe: azul
    PING_LIFE_ENEMY  = 220   # Jogador inimigo: vermelho
    PING_LIFE_ISLAND = 300   # Ilha: bege/terra — dura mais, pois não se move

    def __init__(self):
        self.angle     = 0.0    # graus, avança por frame
        self.speed     = 1.5    # graus/frame
        self.pings     : list[dict] = []
        # Cache de ilhas detectadas para não repetir pings estáticos
        self._island_pings : dict = {}  # (gx,gy) -> frames_restantes

    # ─────────────────────── Update ───────────────────────────────────────────
    def update(self, ships, npcs, current_turn, map_grid, grid_size):
        self.angle = (self.angle + self.speed) % 360

        player = ships[current_turn]
        enemy  = ships[1 - current_turn]
        px, py = player.center()

        # Raio de detecção proporcional ao ruído do motor do jogador atual
        noise_radius = player.noise_level * 20 + 5   # 5–25 tiles

        def _sweep_hit(tx, ty):
            """True se a linha de sweep passou por cima deste alvo neste frame."""
            dist = math.hypot(tx - px, ty - py)
            if dist > noise_radius:
                return False
            ang = math.degrees(math.atan2(ty - py, tx - px)) % 360
            diff = (ang - self.angle + 360) % 360
            return diff < self.speed * 2 or diff > 360 - self.speed * 2

        # ── Inimigo jogador ────────────────────────────────────────────────────
        if not enemy.is_silent:
            ex, ey = enemy.center()
            if _sweep_hit(ex, ey):
                self.pings.append({
                    'wx': ex, 'wy': ey,
                    'life': self.PING_LIFE_ENEMY,
                    'max_life': self.PING_LIFE_ENEMY,
                    'kind': 'enemy',
                })

        # ── NPCs ───────────────────────────────────────────────────────────────
        from entities import NPCShip, Fish
        for npc in npcs:
            if not npc.alive:
                continue
            nx, ny = npc.gx, npc.gy
            if not _sweep_hit(nx, ny):
                continue
            if isinstance(npc, Fish):
                self.pings.append({
                    'wx': nx, 'wy': ny,
                    'life': self.PING_LIFE_FISH,
                    'max_life': self.PING_LIFE_FISH,
                    'kind': 'fish',
                })
            elif isinstance(npc, NPCShip):
                self.pings.append({
                    'wx': nx, 'wy': ny,
                    'life': self.PING_LIFE_NPC,
                    'max_life': self.PING_LIFE_NPC,
                    'kind': 'npc',
                })

        # ── Ilhas (tiles de terra na área de varredura) ────────────────────────
        # Amostra tiles em torno do jogador dentro do noise_radius
        sample_step = max(1, int(noise_radius / 8))  # não escaneia todo tile (performance)
        sweep_rad   = math.radians(self.angle)
        # Varre uma "fatia" em torno do ângulo atual — só os tiles que a linha tocou
        for dist_step in range(1, int(noise_radius) + 1, sample_step):
            tx = px + math.cos(sweep_rad) * dist_step
            ty = py + math.sin(sweep_rad) * dist_step
            igx, igy = int(tx), int(ty)
            if 0 <= igx < grid_size and 0 <= igy < grid_size:
                if map_grid[igy][igx] != 'water':
                    key = (igx, igy)
                    if key not in self._island_pings or self._island_pings[key] <= 0:
                        self.pings.append({
                            'wx': igx + 0.5, 'wy': igy + 0.5,
                            'life': self.PING_LIFE_ISLAND,
                            'max_life': self.PING_LIFE_ISLAND,
                            'kind': 'island',
                        })
                        self._island_pings[key] = self.PING_LIFE_ISLAND

        # Decai timers do cache de ilhas
        for k in list(self._island_pings):
            self._island_pings[k] -= 1
            if self._island_pings[k] <= 0:
                del self._island_pings[k]

        # Decai pings normais
        for p in self.pings:
            p['life'] -= 1
        self.pings = [p for p in self.pings if p['life'] > 0]

    # ─────────────────────── Draw ─────────────────────────────────────────────
    def draw(self, surf, x0, y, mm_w, mm_sc, ships, npcs, current_turn, grid_size):
        cx = x0 + 12 + mm_w // 2
        cy = y  + mm_w // 2
        r  = mm_w // 2

        # Fundo e círculo base
        pygame.draw.rect(surf, C['radar_bg'], (x0 + 12, y, mm_w, mm_w))
        pygame.draw.circle(surf, C['radar_bg'], (cx, cy), r)

        # Grade
        for frac in (0.25, 0.5, 0.75, 1.0):
            pygame.draw.circle(surf, C['radar_grid'], (cx, cy), int(r * frac), 1)
        pygame.draw.line(surf, C['radar_grid'], (cx - r, cy), (cx + r, cy), 1)
        pygame.draw.line(surf, C['radar_grid'], (cx, cy - r), (cx, cy + r), 1)
        # Diagonais 45° para deixar mais parecido com sonar real
        d = int(r * 0.707)
        pygame.draw.line(surf, C['radar_grid'], (cx - d, cy - d), (cx + d, cy + d), 1)
        pygame.draw.line(surf, C['radar_grid'], (cx + d, cy - d), (cx - d, cy + d), 1)

        # Sweep — linha verde
        rad = math.radians(self.angle)
        ex  = cx + int(math.cos(rad) * r)
        ey  = cy + int(math.sin(rad) * r)
        pygame.draw.line(surf, C['radar_line'], (cx, cy), (ex, ey), 2)

        # Rastro do sweep (cone de brilho decrescente)
        for fade in range(1, 10):
            frad  = math.radians(self.angle - fade * 6)
            fx    = cx + int(math.cos(frad) * r)
            fy    = cy + int(math.sin(frad) * r)
            ratio = 1 - fade / 10
            trail = tuple(int(c * ratio) for c in C['radar_line'])
            pygame.draw.line(surf, trail, (cx, cy), (fx, fy), 1)

        # Cores por tipo de ping
        KIND_COLORS = {
            'enemy' : (220,  55,  55),   # vermelho
            'npc'   : (210, 180,  40),   # amarelo
            'fish'  : ( 60, 160, 230),   # azul
            'island': (180, 155, 100),   # bege/terra
        }
        KIND_RADIUS = {
            'enemy' : 4,
            'npc'   : 3,
            'fish'  : 2,
            'island': 2,
        }

        player_cx, player_cy = ships[current_turn].center()
        noise_r = ships[current_turn].noise_level * 20 + 5

        for ping in self.pings:
            life_ratio = ping['life'] / ping['max_life']
            kind = ping['kind']
            wx, wy = ping['wx'], ping['wy']

            # Posição no radar (relativa ao centro do jogador, escalada)
            dx = (wx - player_cx) / noise_r
            dy = (wy - player_cy) / noise_r
            px_ = cx + int(dx * r)
            py_ = cy + int(dy * r)

            # Só desenha se estiver dentro do círculo do radar
            if math.hypot(px_ - cx, py_ - cy) > r:
                continue

            base_col  = KIND_COLORS.get(kind, (200, 200, 200))
            dot_r     = KIND_RADIUS.get(kind, 3)
            col_faded = tuple(int(c * life_ratio) for c in base_col)

            # Ilhas: quadrado pequeno (referência visual de obstáculo)
            if kind == 'island':
                s = max(1, int(dot_r * life_ratio))
                pygame.draw.rect(surf, col_faded, (px_ - s, py_ - s, s * 2, s * 2))
            else:
                pygame.draw.circle(surf, col_faded, (px_, py_), max(1, int(dot_r * life_ratio)))

        # Ponto branco central = jogador atual
        pygame.draw.circle(surf, C['radar_ping'], (cx, cy), 3)

        # Borda
        pygame.draw.circle(surf, C['ui_border'], (cx, cy), r, 1)

        # ── Legenda de coordenadas ─────────────────────────────────────────────
        y_ll  = y + mm_w + 4
        font  = pygame.font.SysFont('consolas', 11)
        for i, s in enumerate(ships):
            sx_, sy_ = s.center()
            lat =  90.0 - (sy_ / grid_size) * 180.0
            lon = -180.0 + (sx_ / grid_size) * 360.0
            la  = f"{'N' if lat >= 0 else 'S'}{abs(lat):05.1f}°"
            lo  = f"{'E' if lon >= 0 else 'W'}{abs(lon):06.1f}°"

            if i == current_turn:
                txt = font.render(f"J{i+1} {la} {lo}", True, s.player_color)
            elif s.is_silent:
                txt = font.render(f"J{i+1} — SILENCIOSO —", True, C['text_dim'])
            else:
                lat += random.uniform(-8, 8)
                lon += random.uniform(-8, 8)
                la2 = f"{'N' if lat >= 0 else 'S'}{abs(lat):05.1f}°"
                lo2 = f"{'E' if lon >= 0 else 'W'}{abs(lon):06.1f}°"
                txt = font.render(f"J{i+1} ~{la2} ~{lo2}", True, C['text_dim'])
            surf.blit(txt, (x0 + 10, y_ll))
            y_ll += 14

        # ── Legenda de cores ───────────────────────────────────────────────────
        y_ll += 2
        legend = [
            ((220,  55,  55), "● Inimigo"),
            ((210, 180,  40), "● NPC"),
            ((60,  160, 230), "● Peixe"),
            ((180, 155, 100), "■ Ilha"),
        ]
        for col, label in legend:
            ls = font.render(label, True, col)
            surf.blit(ls, (x0 + 10, y_ll))
            y_ll += 13