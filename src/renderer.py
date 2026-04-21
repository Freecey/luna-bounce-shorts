"""
Renderer with multiple modes:
- BALL mode: full glowing orb with particles
- DOT mode: minimal point/line, ultra-thin abstract
All rendered with pure PIL.
"""

import math
import random
from dataclasses import dataclass
from typing import List, Tuple
from PIL import Image, ImageDraw, ImageFilter

from ball import Ball, Vector2, Collision


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float
    max_life: float
    color: Tuple[int, int, int]
    size: float


class ParticleSystem:
    def __init__(self, max_particles: int = 200):
        self.particles: List[Particle] = []
        self.max_particles = max_particles

    def spawn(self, x: float, y: float, speed: float, normal: Vector2,
              color: Tuple[int, int, int], count: int = 8):
        for _ in range(count):
            angle = math.atan2(normal.y, normal.x) + random.uniform(-math.pi/2, math.pi/2)
            vel = random.uniform(0.5, 2.5) * (speed / 10)
            self.particles.append(Particle(
                x=x, y=y,
                vx=math.cos(angle) * vel,
                vy=math.sin(angle) * vel,
                life=1.0,
                max_life=random.uniform(0.5, 1.0),
                color=color,
                size=random.uniform(1, 3)
            ))

    def update(self, dt: float = 1.0):
        for p in self.particles:
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.vy += 0.05 * dt
            p.life -= (1.0 / p.max_life) * dt
        self.particles = [p for p in self.particles if p.life > 0]

    def clear(self):
        self.particles = []


class Renderer:
    """Main renderer supporting BALL and DOT modes."""

    def __init__(self, width: int, height: int, style: dict):
        self.width = width
        self.height = height
        self.style = style
        self.particles = ParticleSystem()
        self.frame = 0
        self._build_background()

    def _build_background(self):
        bg = self.style.get("background", (10, 6, 18))
        self.background = Image.new("RGB", (self.width, self.height), bg)
        draw = ImageDraw.Draw(self.background)

        if self.style.get("grid_enabled", False):
            grid_color = tuple(max(0, c - 15) for c in bg)
            step = self.style.get("grid_step", 80)
            for x in range(0, self.width, step):
                draw.line([(x, 0), (x, self.height)], grid_color, width=1)
            for y in range(0, self.height, step):
                draw.line([(0, y), (self.width, y)], grid_color, width=1)

        if self.style.get("center_ring", False):
            cx, cy = self.width // 2, self.height // 2
            r = min(self.width, self.height) // 3
            ring_color = tuple(min(255, c + 20) for c in bg)
            draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=ring_color, width=2)

    def render_frame(self, ball: Ball, flash_intensity: float = 0.0) -> Image:
        """Route to the appropriate renderer based on mode."""
        self.frame += 1
        dot_mode = self.style.get("dot_mode", False)

        if dot_mode:
            return self._render_dot_frame(ball, flash_intensity)
        else:
            return self._render_ball_frame(ball, flash_intensity)

    # ─── BALL MODE ───────────────────────────────────────────────────────────

    def _render_ball_frame(self, ball: Ball, flash_intensity: float = 0.0) -> Image:
        """Full glowing orb with particles."""
        img = self.background.copy()
        draw = ImageDraw.Draw(img)

        # Trails
        if len(ball.trail) > 1 and self.style.get("trail_enabled", True):
            trail_color = ball.glow_color
            for i in range(len(ball.trail) - 1):
                alpha = (i / len(ball.trail)) * 0.6
                r = int(trail_color[0] * alpha)
                g = int(trail_color[1] * alpha)
                b = int(trail_color[2] * alpha)
                width = max(1, int(ball.radius * 0.3 * alpha))
                p1 = (ball.trail[i].x, ball.trail[i].y)
                p2 = (ball.trail[i+1].x, ball.trail[i+1].y)
                draw.line([p1, p2], (r, g, b), width=width)

        # Particles
        self.particles.update()
        for p in self.particles.particles:
            alpha = p.life
            size = max(1, int(p.size * alpha))
            color = tuple(int(c * alpha) for c in p.color)
            draw.ellipse([p.x - size, p.y - size, p.x + size, p.y + size], fill=color)

        cx, cy = int(ball.pos.x), int(ball.pos.y)
        r = int(ball.radius)

        # Glow
        if self.style.get("glow_enabled", True):
            glow_radius = int(r * self.style.get("glow_radius_mult", 2.5))
            glow_img = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
            glow_draw = ImageDraw.Draw(glow_img)
            for i in range(3):
                g_alpha = int(80 - i * 20)
                g_r = int(glow_radius + i * r * 0.5)
                glow_color = (*ball.glow_color[:3], g_alpha)
                glow_draw.ellipse([cx - g_r, cy - g_r, cx + g_r, cy + g_r], fill=glow_color)
            glow_img = glow_img.filter(ImageFilter.GaussianBlur(radius=int(glow_radius * 0.3)))
            img = Image.alpha_composite(img.convert("RGBA"), glow_img).convert("RGB")

        # Ball body
        for i in range(r, 0, -1):
            ratio = i / r
            color = tuple(int(c * (0.4 + 0.6 * ratio)) for c in ball.color)
            draw.ellipse([cx - i, cy - i, cx + i, cy + i], fill=color)

        # Specular highlight
        hl_x = cx - int(r * 0.3)
        hl_y = cy - int(r * 0.3)
        hl_r = max(2, int(r * 0.25))
        draw.ellipse([hl_x - hl_r, hl_y - hl_r, hl_x + hl_r, hl_y + hl_r],
                     fill=(255, 255, 255, 180))

        # Flash
        if flash_intensity > 0:
            flash = Image.new("RGB", (self.width, self.height), (255, 255, 255))
            img = Image.blend(img, flash, flash_intensity * 0.4)

        if self.style.get("vignette", True):
            img = self._apply_vignette(img)

        return img

    # ─── DOT MODE ────────────────────────────────────────────────────────────

    def _render_dot_frame(self, ball: Ball, flash_intensity: float = 0.0) -> Image:
        """Ultra-minimal dot/line with fading trail."""
        img = self.background.copy()
        draw = ImageDraw.Draw(img)

        dot_mode = self.style.get("dot_mode", True)
        trail_color = self.style.get("dot_glow_color", (255, 255, 255))

        # Fading trail
        if len(ball.trail) > 1 and self.style.get("dot_trail", True):
            for i in range(len(ball.trail) - 1):
                alpha = i / len(ball.trail)
                fade = self.style.get("dot_trail_fade", True)
                if fade:
                    r = int(trail_color[0] * alpha)
                    g = int(trail_color[1] * alpha)
                    b = int(trail_color[2] * alpha)
                else:
                    r, g, b = trail_color[:3]
                width = max(1, int(alpha * 2))
                p1 = (ball.trail[i].x, ball.trail[i].y)
                p2 = (ball.trail[i+1].x, ball.trail[i+1].y)
                draw.line([p1, p2], (r, g, b), width=width)

        cx, cy = int(ball.pos.x), int(ball.pos.y)

        if dot_mode == "line":
            # Short line in velocity direction
            line_len = self.style.get("line_length", 12)
            angle = math.atan2(ball.vel.y, ball.vel.x)
            mag = ball.vel.magnitude()
            dx = math.cos(angle) * min(line_len, mag * 1.5)
            dy = math.sin(angle) * min(line_len, mag * 1.5)

            x1, y1 = cx - dx * 0.5, cy - dy * 0.5
            x2, y2 = cx + dx * 0.5, cy + dy * 0.5
            line_color = self.style.get("line_color", (255, 255, 255))

            if self.style.get("line_glow", True):
                glow_r = self.style.get("line_glow_radius", 6)
                glow_color = self.style.get("line_glow_color", line_color)
                for gr in range(glow_r, 0, -1):
                    draw.line([x1, y1, x2, y2], glow_color[:3], width=gr + 1)

            draw.line([x1, y1, x2, y2], line_color, width=2)

        elif dot_mode == "stardust":
            # Cluster of tiny dots
            dot_color = self.style.get("dot_color", (255, 255, 255))
            glow_color = self.style.get("dot_glow_color", dot_color)
            count = self.style.get("dot_count", 3)
            sizes = self.style.get("dot_size_range", [1, 3])

            for i in range(count):
                ox = math.cos(i * 2.1 + self.frame * 0.1) * ball.radius * 0.5
                oy = math.sin(i * 2.1 + self.frame * 0.1) * ball.radius * 0.5
                px, py = cx + ox, cy + oy
                sz = sizes[0] + (sizes[1] - sizes[0]) * (i / count)

                if self.style.get("dot_glow", True):
                    for gr in range(self.style.get("dot_glow_radius", 5), 1, -1):
                        draw.ellipse([px-gr, py-gr, px+gr, py+gr], fill=glow_color[:3])
                draw.ellipse([px-sz, py-sz, px+sz, py+sz], fill=dot_color[:3])

        else:
            # Simple dot with glow
            dot_size = self.style.get("dot_size", 2)
            dot_color = self.style.get("dot_color", (255, 255, 255))
            glow_color = self.style.get("dot_glow_color", dot_color)
            glow_r = self.style.get("dot_glow_radius", 8)

            if self.style.get("dot_glow", True):
                for gr in range(glow_r, 1, -1):
                    alpha = 1 - gr / glow_r
                    gc = tuple(int(c * alpha) for c in glow_color[:3])
                    draw.ellipse([cx-gr, cy-gr, cx+gr, cy+gr], fill=gc)

            draw.ellipse([cx-dot_size, cy-dot_size, cx+dot_size, cy+dot_size],
                         fill=dot_color[:3])

        # Collision flash
        if flash_intensity > 0 and self.style.get("flash_on_hit", True):
            flash = Image.new("RGB", (self.width, self.height), (255, 255, 255))
            img = Image.blend(img, flash, flash_intensity * 0.3)

        if self.style.get("vignette", True):
            img = self._apply_vignette(img)

        return img

    # ─── SHARED ─────────────────────────────────────────────────────────────

    def _apply_vignette(self, img: Image) -> Image:
        """Apply subtle vignette overlay."""
        w, h = self.width, self.height
        strength = self.style.get("vignette_strength", 0.5)
        bg = self.style.get("background", (10, 6, 18))

        # Build radial gradient manually
        vignette = Image.new("RGB", (w, h), bg)
        vd = ImageDraw.Draw(vignette)
        cx, cy = w // 2, h // 2
        max_r = int(math.sqrt(w**2 + h**2))

        for i in range(max_r, 0, -10):
            alpha = (1 - i / max_r) * strength
            color = tuple(int(c * alpha) for c in bg)
            vd.ellipse([cx-i, cy-i, cx+i, cy+i], fill=color)

        return Image.blend(img, vignette, 0.4)

    def handle_collision(self, collision: Collision):
        if self.style.get("particles_on_hit", True):
            self.particles.spawn(
                collision.position.x, collision.position.y,
                collision.speed, collision.surface_normal,
                (200, 200, 255),
                count=self.style.get("particle_count", 8)
            )
