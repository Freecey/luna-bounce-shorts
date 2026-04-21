"""
Renderer with glow, trails, particles and post-effects.
Pure Pillow, no pygame needed for static frame generation.
"""

import math
import random
from dataclasses import dataclass
from typing import List, Tuple, Optional
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from ball import Ball, Vector2, Collision


@dataclass
class Particle:
    """Small particle for collision effects."""
    x: float
    y: float
    vx: float
    vy: float
    life: float
    max_life: float
    color: Tuple[int, int, int]
    size: float


class ParticleSystem:
    """Manages particles spawned on collisions."""

    def __init__(self, max_particles: int = 200):
        self.particles: List[Particle] = []
        self.max_particles = max_particles

    def spawn(self, x: float, y: float, speed: float, normal: Vector2, color: Tuple[int, int, int], count: int = 8):
        """Spawn particles at collision point."""
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
        """Update all particles."""
        for p in self.particles:
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.vy += 0.05 * dt  # slight gravity
            p.life -= (1.0 / p.max_life) * dt
        self.particles = [p for p in self.particles if p.life > 0]

    def clear(self):
        self.particles = []


class Renderer:
    """Renders a ball scene with effects to a PIL Image."""

    def __init__(self, width: int, height: int, style: dict):
        self.width = width
        self.height = height
        self.style = style
        self.particles = ParticleSystem()
        self.frame = 0

        # Pre-build background
        self._build_background()

    def _build_background(self):
        """Create the static background layer."""
        bg = self.style.get("background", (10, 6, 18))
        self.background = Image.new("RGB", (self.width, self.height), bg)

        draw = ImageDraw.Draw(self.background)

        # Grid lines (subtle)
        if self.style.get("grid_enabled", False):
            grid_color = tuple(max(0, c - 15) for c in bg)
            step = self.style.get("grid_step", 80)
            for x in range(0, self.width, step):
                draw.line([(x, 0), (x, self.height)], grid_color, width=1)
            for y in range(0, self.height, step):
                draw.line([(0, y), (self.width, y)], grid_color, width=1)

        # Central guide circle (threshold aesthetic)
        if self.style.get("center_ring", False):
            cx, cy = self.width // 2, self.height // 2
            r = min(self.width, self.height) // 3
            ring_color = tuple(min(255, c + 20) for c in bg)
            draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=ring_color, width=2)

    def render_frame(self, ball: Ball, flash_intensity: float = 0.0) -> Image:
        """Render one frame to an Image."""
        self.frame += 1

        # Render order: background → trails → particles → ball → glow → flash
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

        # Ball body
        cx, cy = ball.pos.x, ball.pos.y
        r = ball.radius
        ball_color = ball.color

        # Outer glow
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

        # Ball fill with gradient effect (simple radial)
        r_int = int(r)
        for i in range(r_int, 0, -1):
            ratio = i / r_int
            color = tuple(int(c * (0.4 + 0.6 * ratio)) for c in ball_color)
            draw.ellipse([cx - i, cy - i, cx + i, cy + i], fill=color)

        # Specular highlight
        hl_x = cx - int(r * 0.3)
        hl_y = cy - int(r * 0.3)
        hl_r = max(2, int(r * 0.25))
        draw.ellipse([hl_x - hl_r, hl_y - hl_r, hl_x + hl_r, hl_y + hl_r],
                     fill=(255, 255, 255, 180))

        # Collision flash
        if flash_intensity > 0:
            flash = Image.new("RGB", (self.width, self.height), (255, 255, 255))
            img = Image.blend(img, flash, flash_intensity * 0.4)

        # Vignette
        if self.style.get("vignette", True):
            vig = self._vignette(self.width, self.height, self.style.get("vignette_strength", 0.4))
            img = Image.blend(img, vig, 0.5)

        return img

    def _vignette(self, w: int, h: int, strength: float) -> Image:
        """Create a vignette overlay."""
        img = Image.new("RGB", (w, h), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        steps = 20
        for i in range(steps, 0, -1):
            alpha = (1 - i / steps) * strength
            r_inner = 0
            r_outer = int(math.sqrt(w**2 + h**2) * (i / steps))
            overlay = Image.new("RGB", (w, h), (0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.ellipse([w//2 - r_outer, h//2 - r_outer,
                                   w//2 + r_outer, h//2 + r_outer], fill=(255, 255, 255))
            img = Image.blend(img, overlay, alpha)
        return img

    def handle_collision(self, collision: Collision):
        """React to a collision: spawn particles + flash."""
        color = self.particles.max_particles > 0 and collision.position or collision.position
        self.particles.spawn(
            collision.position.x,
            collision.position.y,
            collision.speed,
            collision.surface_normal,
            collision.velocity_before and (200, 200, 255) or (255, 200, 200),
            count=self.style.get("particle_count", 8)
        )
