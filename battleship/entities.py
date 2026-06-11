# entities.py

import math
import random
from constants import C, MODULE_DEFS, UPGRADE_TREE, FOG_RADIUS_BASE


def lerp_color(a, b, t):
    return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))


class Module:
    def __init__(self, mod_type: str, rx=None, ry=None):
        d = MODULE_DEFS[mod_type]
        self.type      = mod_type
        self.name      = d['name']
        self.w         = d['w']
        self.h         = d['h']
        self.hp        = d['hp']
        self.max_hp    = d['hp']
        self.color_key = d['color']
        self.rx        = d['rx'] if rx is None else rx
        self.ry        = d['ry'] if ry is None else ry
        self.rotated   = False

    @property
    def current_w(self): return self.h if self.rotated else self.w
    @property
    def current_h(self): return self.w if self.rotated else self.h
    @property
    def destroyed(self): return self.hp <= 0

    @property
    def color(self):
        if self.destroyed:
            return C['destroyed']
        return lerp_color(C['damaged'], C[self.color_key], self.hp / self.max_hp)

    def damage(self, amount=1):
        self.hp = max(0, self.hp - amount)

    def local_tiles(self):
        return [(self.rx + dx, self.ry + dy)
                for dx in range(self.current_w)
                for dy in range(self.current_h)]


class Ship:
    def __init__(self, gx, gy, angle, pid):
        self.gx         = float(gx)
        self.gy         = float(gy)
        self.angle      = float(angle)
        self.pid        = pid
        self.modules    : list[Module] = []
        self.pending_shot = None # Armazena (tx, ty) para disparar após o movimento
        self.pending_move = (0.0, 0) # Armazena (steering, speed) planejado
        self.money      = 200
        self._base_fog  = FOG_RADIUS_BASE # Raio base da névoa
        self.modules.append(Module('hull')) # Inicializa com um casco

    def _mod(self, t):
        return next((m for m in self.modules if m.type == t and not m.destroyed), None)

    @property
    def hull(self):
        return next((m for m in self.modules if m.type == 'hull'), None)

    @property
    def alive(self):
        # O navio está vivo enquanto houver qualquer módulo funcional (incluindo o casco)
        return any(not m.destroyed for m in self.modules)

    @property
    def player_color(self):
        return C['p1'] if self.pid == 0 else C['p2']

    def has_engine(self):
        for t in ('engine_thermo', 'engine_nuclear', 'engine'):
            m = self._mod(t)
            if m: return m
        return None

    @property
    def max_speed(self):
        e = self.has_engine()
        if e is None:             return 2
        if e.type == 'engine_thermo':  return 8
        if e.type == 'engine_nuclear': return 6
        return 4

    @property
    def noise_level(self):
        e = self.has_engine()
        if e is None:              return 0.3
        if e.type == 'engine_thermo':  return 0.0
        if e.type == 'engine_nuclear': return 0.4
        return 0.7

    @property
    def is_silent(self):
        e = self.has_engine()
        return e is not None and e.type == 'engine_thermo'

    def fog_radius(self):
        return self._base_fog + (2 if self._mod('radar') else 0)

    def has_mortar(self):
        for t in ('mortar_heavy', 'mortar'):
            m = self._mod(t)
            if m: return m
        return None

    def mortar_range(self):
        m = self.has_mortar()
        if m is None:              return 0
        if m.type == 'mortar_heavy': return 20
        return 14

    def mortar_damage(self):
        m = self.has_mortar()
        return 2 if m and m.type == 'mortar_heavy' else 1

    def has_research(self):
        return self._mod('research') is not None

    def center(self):
        h = self.hull
        if h: return self.gx + h.w / 2, self.gy + h.h / 2
        return self.gx + 1.5, self.gy + 1.0

    def world_tiles(self):
        ox, oy = round(self.gx), round(self.gy)
        result = []
        for m in self.modules:
            # Agora retorna todos os tiles, permitindo colisões mesmo em partes destruídas
            for (rx, ry) in m.local_tiles():
                result.append((ox + rx, oy + ry))
        return list(set(result))

    def take_damage_at(self, wx, wy, amount=1):
        ox, oy = round(self.gx), round(self.gy)
        
        # Encontra todos os módulos que ocupam esta coordenada específica
        potential_targets = []
        for m in self.modules:
            if any(ox + lrx == wx and oy + lry == wy for lrx, lry in m.local_tiles()):
                potential_targets.append(m)
        
        if not potential_targets:
            return False

        # Prioridade 1: Módulos funcionais que NÃO são o casco (armas, motores, etc.)
        active_parts = [m for m in potential_targets if not m.destroyed and m.type != 'hull']
        
        if active_parts:
            target = random.choice(active_parts)
        else:
            # Prioridade 2: O casco, se ainda estiver inteiro
            active_hull = [m for m in potential_targets if not m.destroyed and m.type == 'hull']
            if active_hull:
                target = active_hull[0]
            else:
                # Prioridade 3: Se o local atingido já está destruído, dano de "overflow" em qualquer parte viva
                living = [m for m in self.modules if not m.destroyed]
                if not living: return True
                target = random.choice(living)

        target.damage(amount)
        return True # Impacto confirmado
        return False

    def preview_move(self, steering, speed, grid_w, grid_h):
        path = []
        x, y = self.gx, self.gy
        steering = max(-45, min(45, steering))
        for step in range(speed):
            t = step / max(speed - 1, 1) if speed > 1 else 1.0
            rad = math.radians(self.angle + steering * t)
            x += math.cos(rad)
            y += math.sin(rad)
            path.append((x, y))
        h = self.hull
        bw, bh = (h.w, h.h) if h else (3, 2)
        nx = max(0.0, min(float(grid_w - bw), x))
        ny = max(0.0, min(float(grid_h - bh), y))
        return nx, ny, (self.angle + steering) % 360, path

    def apply_move(self, steering, speed, grid_w, grid_h):
        self.gx, self.gy, self.angle, _ = self.preview_move(steering, speed, grid_w, grid_h)

    def available_purchases(self):
        owned = {m.type for m in self.modules}
        items = []

        for t, d in MODULE_DEFS.items():
            if t in ('hull', 'engine', 'engine_nuclear', 'engine_thermo', 'mortar_heavy'):
                continue
            if t in owned:
                continue
            items.append(('buy', t, d['name'], d['cost'], self.money >= d['cost'], d['desc']))

        for t, up in UPGRADE_TREE.items():
            if t in owned and up not in owned:
                ud = MODULE_DEFS[up]
                items.append(('upgrade', t, ud['name'], ud['cost'], self.money >= ud['cost'], ud['desc']))

        for m in self.modules:
            if 0 < m.hp < m.max_hp:
                items.append(('repair', m.type, f'Reparar {m.name}', 30, self.money >= 30, 'Restaura 1HP'))

        return items

    def apply_purchase(self, action, mod_type):
        if action == 'upgrade':
            up = UPGRADE_TREE.get(mod_type)
            if not up: return
            old_m = next((x for x in self.modules if x.type == mod_type), None)
            if old_m:
                new_m = Module(up, rx=old_m.rx, ry=old_m.ry)
                new_m.rotated = old_m.rotated
                self.money -= MODULE_DEFS[up]['cost']
                self.modules.remove(old_m)
                self.modules.append(new_m)

        elif action == 'repair':
            m = next((x for x in self.modules if x.type == mod_type), None)
            if m:
                self.money -= 30
                m.hp = min(m.max_hp, m.hp + 1)

        elif action == 'buy':
            if mod_type in [m.type for m in self.modules]: return
            d = MODULE_DEFS[mod_type]
            if self.money >= d['cost']:
                self.money -= d['cost']
                self.modules.append(Module(mod_type))


# ─────────────────────── NPCs ──────────────────────────────────────────────────

class NPC:
    def __init__(self, gx, gy):
        self.gx    = float(gx)
        self.gy    = float(gy)
        self.alive = True
        self.hp    = 1
        self.angle = random.uniform(0, 360)

    def center(self):      return self.gx, self.gy
    def world_tiles(self): return [(int(self.gx), int(self.gy))]
    def money_reward(self): return 50
    def update(self): pass

    def take_damage_at(self, wx, wy, amount=1):
        if int(self.gx) == wx and int(self.gy) == wy:
            self.hp -= amount
            if self.hp <= 0: self.alive = False
            return True
        return False


class Fish(NPC):
    SWIM_SPEED   = 0.04
    PAUSE_FRAMES = (60, 180)

    def __init__(self, gx, gy):
        super().__init__(int(gx) + 0.5, int(gy) + 0.5)
        self.target_x = self.gx
        self.target_y = self.gy
        self.pause_t  = random.randint(*self.PAUSE_FRAMES)
        self.timer    = 0
        self.moving   = False
        self._pick_target()

    def _pick_target(self, grid_w=32, grid_h=18):
        # Tenta pegar o tamanho atual se possível, senão usa padrão Pequeno
        radius = random.randint(2, 5)
        for _ in range(10):
            nx = self.gx + random.randint(-radius, radius)
            ny = self.gy + random.randint(-radius, radius)
            if 0.5 <= nx <= grid_w - 1.5 and 0.5 <= ny <= grid_h - 1.5:
                self.target_x = float(int(nx)) + 0.5
                self.target_y = float(int(ny)) + 0.5
                dist = math.hypot(self.target_x - self.gx, self.target_y - self.gy)
                if dist > 0.5:
                    self.angle = math.degrees(math.atan2(self.target_y - self.gy, self.target_x - self.gx))
                    self.moving = True
                    return
        self.moving  = False
        self.timer   = 0
        self.pause_t = random.randint(*self.PAUSE_FRAMES)

    def update(self):
        if not self.alive: return
        if self.moving:
            dx = self.target_x - self.gx
            dy = self.target_y - self.gy
            dist = math.hypot(dx, dy)
            if dist < self.SWIM_SPEED + 0.01:
                self.gx, self.gy = self.target_x, self.target_y
                self.moving  = False
                self.timer   = 0
                self.pause_t = random.randint(*self.PAUSE_FRAMES)
            else:
                self.gx += (dx / dist) * self.SWIM_SPEED
                self.gy += (dy / dist) * self.SWIM_SPEED
        else:
            self.timer += 1
            if self.timer >= self.pause_t:
                self._pick_target()

    def world_tiles(self):
        return [(round(self.gx - 0.5), round(self.gy - 0.5))]

    def take_damage_at(self, wx, wy, amount=1):
        tx, ty = round(self.gx - 0.5), round(self.gy - 0.5)
        if tx == wx and ty == wy:
            self.hp -= amount
            if self.hp <= 0: self.alive = False
            return True
        return False


class NPCShip(NPC):
    def __init__(self, gx, gy):
        super().__init__(gx, gy)
        self.max_hp = 1
        self.speed  = random.uniform(0.03, 0.10)
        self.timer  = 0

    def update(self, map_grid):
        if not self.alive: return
        GH = len(map_grid)
        GW = len(map_grid[0]) if GH > 0 else 0
        self.timer += 1
        if self.timer % 90 == 0:
            self.angle += random.uniform(-45, 45)
        rad = math.radians(self.angle)
        for d in range(1, 5):
            fx, fy = int(self.gx + math.cos(rad) * d), int(self.gy + math.sin(rad) * d)
            if 0 <= fx < GW and 0 <= fy < GH:
                if map_grid[fy][fx] != 'water':
                    self.angle += random.choice([25, -25, 40, -40])
                    break
            else:
                self.angle += random.choice([30, -30])
                break
        rad = math.radians(self.angle)
        self.gx = max(1.0, min(GW - 2.0, self.gx + math.cos(rad) * self.speed))
        self.gy = max(1.0, min(GH - 2.0, self.gy + math.sin(rad) * self.speed))

    def money_reward(self): return 150


# ─────────────────────── Partículas ────────────────────────────────────────────

class Particle:
    def __init__(self, sx, sy):
        a   = random.uniform(0, math.tau)
        spd = random.uniform(1.5, 5.0)
        self.x,  self.y  = float(sx), float(sy)
        self.vx, self.vy = math.cos(a) * spd, math.sin(a) * spd
        self.life = random.randint(18, 40)
        self.col  = random.choice([C['exp_a'], C['exp_b'], C['exp_c']])

    def update(self):
        self.x  += self.vx;  self.y  += self.vy
        self.vx *= 0.90;     self.vy *= 0.90
        self.life -= 1

    def draw(self, surf):
        import pygame
        pygame.draw.circle(surf, self.col, (int(self.x), int(self.y)), max(1, self.life // 9))
