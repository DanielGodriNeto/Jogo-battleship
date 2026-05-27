# radar.py — Sistema de radar/sonar estilo sonar verde

import pygame
import math
from constants import C, SIDEBAR_W


class Radar:
    """Radar estilo sonar: linha giratória verde, pings de inimigos detectados."""

    def __init__(self):
        self.angle    = 0.0       # ângulo atual da linha do radar (graus)
        self.speed    = 1.5       # graus/frame
        self.pings    : list[dict] = []   # {x, y, life, max_life, hit}
        self.ping_life = 180      # frames que o ping dura

    def update(self, ships, npcs, current_turn):
        """Gira o radar e detecta inimigos dentro do raio de ruído."""
        self.angle = (self.angle + self.speed) % 360

        player = ships[current_turn]
        enemy  = ships[1 - current_turn]

        px, py = player.center()
        noise_radius = player.noise_level * 20 + 5   # 5–25 tiles baseado no motor

        # Varre NPCShips e inimigo
        targets = []
        for npc in npcs:
            from entities import NPCShip
            if isinstance(npc, NPCShip) and npc.alive:
                targets.append(npc.center())
        if not enemy.is_silent:
            targets.append(enemy.center())

        for tx, ty in targets:
            dist = math.hypot(tx - px, ty - py)
            if dist <= noise_radius:
                target_angle = math.degrees(math.atan2(ty - py, tx - px)) % 360
                diff = abs((target_angle - self.angle + 360) % 360)
                if diff < self.speed * 2 or diff > 360 - self.speed * 2:
                    # Ping!
                    self.pings.append({
                        'wx': tx, 'wy': ty,
                        'life': self.ping_life,
                        'max_life': self.ping_life,
                        'is_enemy': True,
                    })

        # Decai pings
        self.pings = [p for p in self.pings if p['life'] > 0]
        for p in self.pings:
            p['life'] -= 1

    def draw(self, surf, x0, y, mm_w, mm_sc, ships, npcs, current_turn, grid_size):
        """Desenha o radar estilo sonar no espaço do minimapa."""
        cx = x0 + 12 + mm_w // 2
        cy = y + mm_w // 2
        r  = mm_w // 2

        # Fundo escuro
        pygame.draw.rect(surf, C['radar_bg'], (x0 + 12, y, mm_w, mm_w))
        pygame.draw.circle(surf, C['radar_bg'], (cx, cy), r)

        # Grade de círculos e linhas
        for frac in (0.25, 0.5, 0.75, 1.0):
            pygame.draw.circle(surf, C['radar_grid'], (cx, cy), int(r * frac), 1)
        pygame.draw.line(surf, C['radar_grid'], (cx - r, cy), (cx + r, cy), 1)
        pygame.draw.line(surf, C['radar_grid'], (cx, cy - r), (cx, cy + r), 1)

        # Sweep — linha verde girando
        rad = math.radians(self.angle)
        ex  = cx + int(math.cos(rad) * r)
        ey  = cy + int(math.sin(rad) * r)
        pygame.draw.line(surf, C['radar_line'], (cx, cy), (ex, ey), 2)

        # Rastro suave do sweep (últimos ~60°)
        for fade in range(1, 8):
            frad = math.radians(self.angle - fade * 8)
            fx   = cx + int(math.cos(frad) * r)
            fy   = cy + int(math.sin(frad) * r)
            alpha_col = tuple(int(c * (1 - fade / 9)) for c in C['radar_line'])
            pygame.draw.line(surf, alpha_col, (cx, cy), (fx, fy), 1)

        # Pings detectados
        player_cx, player_cy = ships[current_turn].center()
        noise_r = (ships[current_turn].noise_level * 20 + 5)

        for ping in self.pings:
            life_ratio = ping['life'] / ping['max_life']
            wx, wy     = ping['wx'], ping['wy']
            # Converte pos do mundo para pos no radar
            dx = (wx - player_cx) / noise_r
            dy = (wy - player_cy) / noise_r
            px_ = cx + int(dx * r)
            py_ = cy + int(dy * r)
            alpha = int(200 * life_ratio)
            col   = C['radar_enemy'] if ping['is_enemy'] else C['radar_ping']
            col_a = tuple(int(c * life_ratio) for c in col)
            pygame.draw.circle(surf, col_a, (px_, py_), max(2, int(4 * life_ratio)))

        # Posição do jogador atual — ponto branco no centro
        pygame.draw.circle(surf, C['radar_ping'], (cx, cy), 3)

        # Borda circular
        pygame.draw.circle(surf, C['ui_border'], (cx, cy), r, 1)

        # Legenda de lat/lon abaixo do radar
        y_ll = y + mm_w + 4
        for i, s in enumerate(ships):
            sx_, sy_ = s.center()
            lat =  90.0 - (sy_ / grid_size) * 180.0
            lon = -180.0 + (sx_ / grid_size) * 360.0
            la = f"{'N' if lat >= 0 else 'S'}{abs(lat):05.1f}°"
            lo = f"{'E' if lon >= 0 else 'W'}{abs(lon):06.1f}°"

            font = pygame.font.SysFont('consolas', 11)
            if i == current_turn:
                txt = font.render(f"J{i+1} {la} {lo}", True, s.player_color)
            elif s.is_silent:
                txt = font.render(f"J{i+1} — SILENCIOSO —", True, C['text_dim'])
            else:
                import random
                lat += random.uniform(-8, 8)
                lon += random.uniform(-8, 8)
                la2 = f"{'N' if lat >= 0 else 'S'}{abs(lat):05.1f}°"
                lo2 = f"{'E' if lon >= 0 else 'W'}{abs(lon):06.1f}°"
                txt = font.render(f"J{i+1} ~{la2} ~{lo2}", True, C['text_dim'])
            surf.blit(txt, (x0 + 10, y_ll))
            y_ll += 14
