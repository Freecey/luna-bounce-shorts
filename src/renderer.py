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

    def render_frame(self, ball, flash_intensity: float = 0.0,
                     arena=None, extra_balls: list = None) -> Image:
        """Route to the appropriate renderer based on mode."""
        self.frame += 1
        dot_mode = self.style.get("dot_mode", False)

        if dot_mode:
            return self._render_dot_frame(ball, flash_intensity, arena)
        else:
            return self._render_ball_frame(ball, flash_intensity, arena,
                                           extra_balls=extra_balls)

    # ─── BALL MODE ───────────────────────────────────────────────────────────

    def _render_ball_frame(self, ball: Ball, flash_intensity: float = 0.0,
                          arena=None, extra_balls: list = None) -> Image:
        """Full glowing orb with particles. Supports multiple balls."""
        img = self.background.copy()
        draw = ImageDraw.Draw(img)

        # Arena boundaries and obstacles
        if arena is not None:
            img, draw = self._draw_arena(img, draw, arena)

        # Collect all balls to render
        all_balls = [ball]
        if extra_balls:
            all_balls.extend(extra_balls)

        for b in all_balls:
            # Trails
            if len(b.trail) > 1 and self.style.get("trail_enabled", True):
                trail_color = b.glow_color
                for i in range(len(b.trail) - 1):
                    alpha = (i / len(b.trail)) * 0.6
                    r = int(trail_color[0] * alpha)
                    g = int(trail_color[1] * alpha)
                    bl = int(trail_color[2] * alpha)
                    width = max(1, int(b.radius * 0.3 * alpha))
                    p1 = (b.trail[i].x, b.trail[i].y)
                    p2 = (b.trail[i+1].x, b.trail[i+1].y)
                    draw.line([p1, p2], (r, g, bl), width=width)

        # Particles
        self.particles.update()
        for p in self.particles.particles:
            alpha = p.life
            size = max(1, int(p.size * alpha))
            color = tuple(int(c * alpha) for c in p.color)
            draw.ellipse([p.x - size, p.y - size, p.x + size, p.y + size], fill=color)

        for b in all_balls:
            cx, cy = int(b.pos.x), int(b.pos.y)
            r = int(b.radius)

            # Glow
            if self.style.get("glow_enabled", True):
                glow_radius = int(r * self.style.get("glow_radius_mult", 2.5))
                glow_img = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
                glow_draw = ImageDraw.Draw(glow_img)
                for i in range(3):
                    g_alpha = int(80 - i * 20)
                    g_r = int(glow_radius + i * r * 0.5)
                    glow_color = (*b.glow_color[:3], g_alpha)
                    glow_draw.ellipse([cx - g_r, cy - g_r, cx + g_r, cy + g_r], fill=glow_color)
                glow_img = glow_img.filter(ImageFilter.GaussianBlur(radius=int(glow_radius * 0.3)))
                img = Image.alpha_composite(img.convert("RGBA"), glow_img).convert("RGB")
                draw = ImageDraw.Draw(img)

            # Ball body
            for i in range(r, 0, -1):
                ratio = i / r
                color = tuple(int(c * (0.4 + 0.6 * ratio)) for c in b.color)
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
            img = Image.blend(img, flash, flash_intensity * 0.15)

        if self.style.get("vignette", True):
            img = self._apply_vignette(img)

        return img

    # ─── DOT MODE ────────────────────────────────────────────────────────────

    def _render_dot_frame(self, ball: Ball, flash_intensity: float = 0.0,
                         arena=None) -> Image:
        """Ultra-minimal dot/line with fading trail."""
        img = self.background.copy()
        draw = ImageDraw.Draw(img)

        dot_mode = self.style.get("dot_mode", True)
        trail_color = self.style.get("dot_glow_color", (255, 255, 255))

        # Arena boundaries and obstacles
        if arena is not None:
            img, draw = self._draw_arena(img, draw, arena)

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

    def _draw_arena(self, img, draw, arena):
        """
        Draw arena boundaries and obstacles onto the image.
        Returns updated (img, draw) tuple since rotating the canvas modifies them.
        """
        from arena import ArenaMechanic
        bounds = arena.get_bounds()
        bg = self.style.get("background", (10, 6, 18))

        if arena.mechanic == ArenaMechanic.ROTATING:
            # Rotate the canvas for the rotating frame effect
            cx, cy = bounds.center()
            angle = arena.get_rotation()
            if abs(angle) > 0.001:
                img = img.rotate(math.degrees(angle), center=(cx, cy), resample=Image.BICUBIC)
                draw = ImageDraw.Draw(img)

        if arena.mechanic == ArenaMechanic.CIRCULAR:
            # Draw circular arena
            cx, cy = arena.get_circle_center()
            r = arena.get_circle_radius()
            circle_color = arena.circle_color
            circle_rotation = arena.get_circle_rotation()
            circle_width = self.style.get("circle_line_width", 3)

            # Glow ring
            glow_mult = self.style.get("circle_glow_mult", 3)
            glow_color = self.style.get("circle_glow_color", circle_color)
            for gr in range(int(r + 15 * glow_mult), int(r), -2):
                alpha = max(0, 1 - (gr - r) / (15 * glow_mult))
                gc = tuple(int(c * alpha * 0.3) for c in glow_color[:3])
                draw.ellipse([cx - gr, cy - gr, cx + gr, cy + gr], outline=gc, width=2)

            # Draw circle as arcs with gaps
            gap_count = arena.circle_gap_count
            gap_size = arena.circle_gap_size  # radians

            if gap_count > 0:
                gap_spacing = 2 * math.pi / gap_count
                # Draw arcs between gaps
                for i in range(gap_count):
                    arc_start = circle_rotation + i * gap_spacing + gap_size / 2
                    arc_end = circle_rotation + (i + 1) * gap_spacing - gap_size / 2
                    # Convert to degrees (PIL uses degrees, 0=3 o'clock, counter-clockwise)
                    start_deg = -math.degrees(arc_start)
                    end_deg = -math.degrees(arc_end)
                    # Draw arc as series of small lines for precision
                    steps = max(10, int(abs(arc_end - arc_start) * r / 5))
                    points = []
                    for s in range(steps + 1):
                        a = arc_start + (arc_end - arc_start) * s / steps
                        px = cx + math.cos(a) * r
                        py = cy + math.sin(a) * r
                        points.append((px, py))
                    if len(points) > 1:
                        draw.line(points, fill=circle_color, width=circle_width)
            else:
                # Full circle (no gaps)
                draw.ellipse(
                    [cx - r, cy - r, cx + r, cy + r],
                    outline=circle_color, width=circle_width
                )

            # Rotating tick marks for visual spin effect
            tick_count = self.style.get("circle_tick_count", 8)
            tick_length = self.style.get("circle_tick_length", 15)
            tick_color = self.style.get("circle_tick_color", circle_color)
            for i in range(tick_count):
                a = circle_rotation + (2 * math.pi * i / tick_count)
                x1 = cx + math.cos(a) * (r - tick_length)
                y1 = cy + math.sin(a) * (r - tick_length)
                x2 = cx + math.cos(a) * r
                y2 = cy + math.sin(a) * r
                draw.line([x1, y1, x2, y2], tick_color, width=2)

            return img, draw

        # Draw arena boundary box
        boundary_color = tuple(max(0, c - 20) for c in bg)
        boundary_width = self.style.get("arena_boundary_width", 2)
        draw.rectangle(
            [bounds.left, bounds.top, bounds.right, bounds.bottom],
            outline=boundary_color, width=boundary_width
        )

        # Draw corner brackets for a stylish arena frame
        bracket_size = 30
        bracket_color = tuple(min(255, c + 15) for c in boundary_color)
        bw = boundary_width + 2

        # Top-left
        draw.line([(bounds.left, bounds.top + bracket_size), (bounds.left, bounds.top)], bracket_color, width=bw)
        draw.line([(bounds.left, bounds.top), (bounds.left + bracket_size, bounds.top)], bracket_color, width=bw)
        # Top-right
        draw.line([(bounds.right - bracket_size, bounds.top), (bounds.right, bounds.top)], bracket_color, width=bw)
        draw.line([(bounds.right, bounds.top), (bounds.right, bounds.top + bracket_size)], bracket_color, width=bw)
        # Bottom-left
        draw.line([(bounds.left, bounds.bottom - bracket_size), (bounds.left, bounds.bottom)], bracket_color, width=bw)
        draw.line([(bounds.left, bounds.bottom), (bounds.left + bracket_size, bounds.bottom)], bracket_color, width=bw)
        # Bottom-right
        draw.line([(bounds.right - bracket_size, bounds.bottom), (bounds.right, bounds.bottom)], bracket_color, width=bw)
        draw.line([(bounds.right, bounds.bottom), (bounds.right, bounds.bottom - bracket_size)], bracket_color, width=bw)

        # Draw obstacles
        for obs in arena.obstacles:
            obs.draw(draw, arena.frame)

        return img, draw

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
