"""
Ball physics simulation.
Pure Python + math, no dependencies.
"""

import math
import random
from dataclasses import dataclass, field
from typing import List, Tuple

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from arena import ArenaMechanic


@dataclass
class Vector2:
    x: float
    y: float

    def __add__(self, other: "Vector2") -> "Vector2":
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector2") -> "Vector2":
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Vector2":
        return Vector2(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> "Vector2":
        return self.__mul__(scalar)

    def magnitude(self) -> float:
        return math.sqrt(self.x**2 + self.y**2)

    def normalize(self) -> "Vector2":
        mag = self.magnitude()
        if mag == 0:
            return Vector2(0, 0)
        return Vector2(self.x / mag, self.y / mag)

    def dot(self, other: "Vector2") -> float:
        return self.x * other.x + self.y * other.y

    def rotate(self, angle: float) -> "Vector2":
        """Rotate vector by angle in radians."""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return Vector2(self.x * cos_a - self.y * sin_a, self.x * sin_a + self.y * cos_a)

    def reflect(self, normal: "Vector2", bounce: float = 0.85) -> "Vector2":
        """Reflect velocity vector off a normal, apply bounce factor."""
        d = self.dot(normal)
        return self - normal * (2 * d * bounce)


@dataclass
class Collision:
    """Record of a collision event for audio sync."""
    frame: int
    position: Vector2
    velocity_before: Vector2
    speed: float
    surface_normal: Vector2


@dataclass
class Ball:
    """Ball with physics state and trail history."""

    pos: Vector2
    vel: Vector2
    radius: float
    color: Tuple[int, int, int]
    glow_color: Tuple[int, int, int]
    bounce: float = 0.85
    gravity: float = 0.3
    trail: List[Vector2] = field(default_factory=list)
    trail_max: int = 40
    collisions: List[Collision] = field(default_factory=list)
    mass: float = 1.0

    def update(self, width: int, height: int, dt: float = 1.0,
               arena=None) -> List[Collision]:
        """
        Update ball physics for one frame. Returns list of new collisions.

        Args:
            width, height: Frame dimensions (used when arena=None).
            dt: Time step multiplier.
            arena: Optional Arena instance for dynamic bounds and obstacles.
        """
        new_collisions = []

        # Apply gravity
        self.vel = self.vel + Vector2(0, self.gravity * dt)

        # Update position
        self.pos = self.pos + self.vel * dt

        # Trail
        self.trail.append(Vector2(self.pos.x, self.pos.y))
        if len(self.trail) > self.trail_max:
            self.trail.pop(0)

        frame = len(self.collisions)  # approximate

        # ── Arena-based collision ─────────────────────────────────────────────
        if arena is not None:
            bounds = arena.get_bounds()

            if arena.mechanic == ArenaMechanic.CIRCULAR:
                new_collisions = self._collide_circular(arena, frame)

            else:
                if arena.mechanic == ArenaMechanic.ROTATING:
                    cx, cy = bounds.center()
                    angle = arena.get_rotation()
                    local_pos = self.pos.rotate(-angle)
                    local_pos = Vector2(local_pos.x + cx, local_pos.y + cy)
                else:
                    local_pos = self.pos

                speed = self.vel.magnitude()

                # Wall collisions
                # Left
                if local_pos.x - self.radius < bounds.left:
                    self.pos.x = bounds.left + self.radius
                    if arena.mechanic == ArenaMechanic.ROTATING:
                        angle = arena.get_rotation()
                        normal = Vector2(1, 0).rotate(angle)
                    else:
                        normal = Vector2(1, 0)
                    if speed > 0.5:
                        new_collisions.append(Collision(frame, Vector2(self.pos.x, self.pos.y),
                                                         Vector2(self.vel.x, self.vel.y), speed, normal))
                    self.vel = self.vel.reflect(normal, self.bounce)

                # Right
                if local_pos.x + self.radius > bounds.right:
                    self.pos.x = bounds.right - self.radius
                    if arena.mechanic == ArenaMechanic.ROTATING:
                        angle = arena.get_rotation()
                        normal = Vector2(-1, 0).rotate(angle)
                    else:
                        normal = Vector2(-1, 0)
                    if speed > 0.5:
                        new_collisions.append(Collision(frame, Vector2(self.pos.x, self.pos.y),
                                                         Vector2(self.vel.x, self.vel.y), speed, normal))
                    self.vel = self.vel.reflect(normal, self.bounce)

                # Top
                if local_pos.y - self.radius < bounds.top:
                    self.pos.y = bounds.top + self.radius
                    if arena.mechanic == ArenaMechanic.ROTATING:
                        angle = arena.get_rotation()
                        normal = Vector2(0, 1).rotate(angle)
                    else:
                        normal = Vector2(0, 1)
                    if speed > 0.5:
                        new_collisions.append(Collision(frame, Vector2(self.pos.x, self.pos.y),
                                                         Vector2(self.vel.x, self.vel.y), speed, normal))
                    self.vel = self.vel.reflect(normal, self.bounce)

                # Bottom
                if local_pos.y + self.radius > bounds.bottom:
                    self.pos.y = bounds.bottom - self.radius
                    if arena.mechanic == ArenaMechanic.ROTATING:
                        angle = arena.get_rotation()
                        normal = Vector2(0, -1).rotate(angle)
                    else:
                        normal = Vector2(0, -1)
                    if speed > 0.5:
                        new_collisions.append(Collision(frame, Vector2(self.pos.x, self.pos.y),
                                                         Vector2(self.vel.x, self.vel.y), speed, normal))
                    self.vel = self.vel.reflect(normal, self.bounce)

                # Obstacle collisions
                for obs in arena.obstacles:
                    result = obs.collision_test(self.pos, self.radius)
                    if result is not None:
                        normal, depth = result
                        self.pos = self.pos + normal * depth
                        speed = self.vel.magnitude()
                        if speed > 0.5:
                            new_collisions.append(Collision(frame, Vector2(self.pos.x, self.pos.y),
                                                             Vector2(self.vel.x, self.vel.y), speed, normal))
                        self.vel = self.vel.reflect(normal, self.bounce)

        else:
            # ── Legacy static boundary collision ───────────────────────────────
            # Left wall
            if self.pos.x - self.radius < 0:
                self.pos.x = self.radius
                speed = self.vel.magnitude()
                if speed > 0.5:
                    normal = Vector2(1, 0)
                    new_collisions.append(Collision(frame, Vector2(self.pos.x, self.pos.y), Vector2(self.vel.x, self.vel.y), speed, normal))
                self.vel = self.vel.reflect(Vector2(1, 0), self.bounce)

            # Right wall
            if self.pos.x + self.radius > width:
                self.pos.x = width - self.radius
                speed = self.vel.magnitude()
                if speed > 0.5:
                    normal = Vector2(-1, 0)
                    new_collisions.append(Collision(frame, Vector2(self.pos.x, self.pos.y), Vector2(self.vel.x, self.vel.y), speed, normal))
                self.vel = self.vel.reflect(Vector2(-1, 0), self.bounce)

            # Top wall
            if self.pos.y - self.radius < 0:
                self.pos.y = self.radius
                speed = self.vel.magnitude()
                if speed > 0.5:
                    normal = Vector2(0, 1)
                    new_collisions.append(Collision(frame, Vector2(self.pos.x, self.pos.y), Vector2(self.vel.x, self.vel.y), speed, normal))
                self.vel = self.vel.reflect(Vector2(0, 1), self.bounce)

            # Bottom wall
            if self.pos.y + self.radius > height:
                self.pos.y = height - self.radius
                speed = self.vel.magnitude()
                if speed > 0.5:
                    normal = Vector2(0, -1)
                    new_collisions.append(Collision(frame, Vector2(self.pos.x, self.pos.y), Vector2(self.vel.x, self.vel.y), speed, normal))
                self.vel = self.vel.reflect(Vector2(0, -1), self.bounce)

        self.collisions.extend(new_collisions)
        return new_collisions

    def _collide_circular(self, arena, frame: int) -> List[Collision]:
        """Handle collision with circular arena boundary."""
        collisions = []
        cx, cy = arena.get_circle_center()
        arena_r = arena.get_circle_radius()
        dx = self.pos.x - cx
        dy = self.pos.y - cy
        dist = math.sqrt(dx * dx + dy * dy)

        if dist + self.radius > arena_r and dist > 0:
            # Check if ball is in a gap — if so, let it pass through
            if arena.is_in_gap(self.pos):
                return collisions

            normal = Vector2(dx / dist, dy / dist)
            self.pos.x = cx + normal.x * (arena_r - self.radius - 0.5)
            self.pos.y = cy + normal.y * (arena_r - self.radius - 0.5)
            speed = self.vel.magnitude()
            vel_dot_normal = self.vel.x * normal.x + self.vel.y * normal.y
            if vel_dot_normal > 0.5:
                collisions.append(Collision(
                    frame, Vector2(self.pos.x, self.pos.y),
                    Vector2(self.vel.x, self.vel.y), speed, normal
                ))
            self.vel = self.vel.reflect(normal, self.bounce)

        return collisions


def create_ball(seed: int, width: int, height: int, style: dict,
                center_start: bool = False) -> Ball:
    """Create a ball from a seed for reproducible randomness."""
    rng = random.Random(seed)

    radius = rng.uniform(style.get("ball_radius_min", 15), style.get("ball_radius_max", 30))

    if center_start:
        start_x = width * 0.5
        start_y = height * 0.5
    else:
        start_x = rng.uniform(width * 0.2, width * 0.8)
        start_y = rng.uniform(height * 0.2, height * 0.5)

    speed = rng.uniform(style.get("speed_min", 5), style.get("speed_max", 12))
    angle = rng.uniform(0, 2 * math.pi)

    color = rng.choice(style.get("colors", [(255, 255, 255)]))
    glow_color = style.get("glow_color", color)

    ball = Ball(
        pos=Vector2(start_x, start_y),
        vel=Vector2(math.cos(angle) * speed, math.sin(angle) * speed - 3),
        radius=radius,
        color=color,
        glow_color=glow_color,
        bounce=style.get("bounce", 0.85),
        gravity=style.get("gravity", 0.3),
    )
    return ball


def spawn_ball_at_center(width: int, height: int, style: dict,
                         rng: random.Random = None) -> Ball:
    """Spawn a ball at the center with a random color."""
    if rng is None:
        rng = random.Random()

    radius = rng.uniform(style.get("ball_radius_min", 15), style.get("ball_radius_max", 30))
    speed = rng.uniform(style.get("speed_min", 5), style.get("speed_max", 12))
    angle = rng.uniform(0, 2 * math.pi)

    hue = rng.uniform(0, 360)
    color = _hsv_to_rgb(hue, 0.7, 1.0)
    glow_color = _hsv_to_rgb(hue, 0.5, 1.0)

    return Ball(
        pos=Vector2(width * 0.5, height * 0.5),
        vel=Vector2(math.cos(angle) * speed, math.sin(angle) * speed - 2),
        radius=radius,
        color=color,
        glow_color=glow_color,
        bounce=style.get("bounce", 0.85),
        gravity=style.get("gravity", 0.3),
    )


def _hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
    """Convert HSV (h: 0-360, s: 0-1, v: 0-1) to RGB tuple."""
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))


@dataclass
class BallBallCollision:
    """Record of a ball-to-ball collision event."""
    frame: int
    position: Vector2
    ball1_velocity_before: Vector2
    ball2_velocity_before: Vector2
    impact_speed: float
    surface_normal: Vector2


class MultiBall:
    """Manages multiple balls with inter-ball elastic collision physics."""

    def __init__(self, balls: List[Ball] = None):
        self.balls: List[Ball] = balls or []
        self.collisions: List[BallBallCollision] = []

    def add_ball(self, ball: Ball) -> None:
        self.balls.append(ball)

    def update(self, width: int, height: int, dt: float = 1.0) -> List[BallBallCollision]:
        """Update all balls and resolve inter-ball collisions. Returns list of ball-ball collisions."""
        all_collisions = []

        # Update each ball (gravity, position, boundary collisions)
        for ball in self.balls:
            new_cols = ball.update(width, height, dt)
            all_collisions.extend(new_cols)

        # Resolve ball-to-ball collisions
        ball_collisions = self._resolve_ball_collisions()
        all_collisions.extend(ball_collisions)

        self.collisions.extend(all_collisions)
        return all_collisions

    def _resolve_ball_collisions(self) -> List[BallBallCollision]:
        """Detect and resolve elastic collisions between all pairs of balls."""
        new_collisions = []

        for i in range(len(self.balls)):
            for j in range(i + 1, len(self.balls)):
                b1 = self.balls[i]
                b2 = self.balls[j]

                collision = self._check_collision(b1, b2)
                if collision is not None:
                    new_collisions.append(collision)
                    self._apply_elastic_collision(b1, b2, collision.surface_normal)

        return new_collisions

    def _check_collision(self, b1: Ball, b2: Ball) -> BallBallCollision | None:
        """Check if two balls are colliding. Returns collision info or None."""
        diff = b2.pos - b1.pos
        dist = diff.magnitude()
        min_dist = b1.radius + b2.radius

        if dist < min_dist and dist > 0:
            # Collision detected
            normal = diff.normalize()
            impact_speed = abs(b1.vel.dot(normal) - b2.vel.dot(normal))

            # Separate balls to prevent overlap
            overlap = min_dist - dist
            separation = normal * (overlap / 2 + 1)
            b1.pos = b1.pos - separation
            b2.pos = b2.pos + separation

            frame = len(self.collisions)
            return BallBallCollision(
                frame=frame,
                position=Vector2((b1.pos.x + b2.pos.x) / 2, (b1.pos.y + b2.pos.y) / 2),
                ball1_velocity_before=Vector2(b1.vel.x, b1.vel.y),
                ball2_velocity_before=Vector2(b2.vel.x, b2.vel.y),
                impact_speed=impact_speed,
                surface_normal=normal,
            )

        return None

    def _apply_elastic_collision(self, b1: Ball, b2: Ball, normal: Vector2) -> None:
        """Apply 2D elastic collision response using proper physics formula."""
        # Relative velocity
        rel_vel = b1.vel - b2.vel

        # Relative velocity along collision normal
        rel_vel_normal = rel_vel.dot(normal)

        # Only resolve if balls are approaching
        if rel_vel_normal > 0:
            return

        # Elastic collision with restitution (use average bounce)
        restitution = (b1.bounce + b2.bounce) / 2

        # Impulse scalar: j = -(1 + e) * v_rel_n / (1/m1 + 1/m2)
        inv_m1 = 1.0 / b1.mass
        inv_m2 = 1.0 / b2.mass
        impulse = -(1 + restitution) * rel_vel_normal / (inv_m1 + inv_m2)

        # Apply impulse to velocities
        b1.vel = b1.vel + normal * (impulse * inv_m1)
        b2.vel = b2.vel - normal * (impulse * inv_m2)
