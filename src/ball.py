"""
Ball physics simulation.
Pure Python + math, no dependencies.
"""

import math
import random
from dataclasses import dataclass, field
from typing import List, Tuple


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

    def update(self, width: int, height: int, dt: float = 1.0) -> List[Collision]:
        """Update ball physics for one frame. Returns list of new collisions."""
        new_collisions = []

        # Apply gravity
        self.vel = self.vel + Vector2(0, self.gravity * dt)

        # Update position
        self.pos = self.pos + self.vel * dt

        # Trail
        self.trail.append(Vector2(self.pos.x, self.pos.y))
        if len(self.trail) > self.trail_max:
            self.trail.pop(0)

        # Boundary collisions
        frame = len(self.collisions)  # approximate

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


def create_ball(seed: int, width: int, height: int, style: dict) -> Ball:
    """Create a ball from a seed for reproducible randomness."""
    rng = random.Random(seed)

    radius = rng.uniform(style.get("ball_radius_min", 15), style.get("ball_radius_max", 30))
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
