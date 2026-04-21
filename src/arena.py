"""
Arena mechanics: moving walls, shrinking arena, rotating frame, obstacles.
Supports four mechanic types:
- "none"          : static rectangular arena (default)
- "shrinking"     : walls move inward over time
- "moving_walls"  : walls oscillate with sinusoidal motion
- "rotating"      : entire frame rotates, ball bounces off rotated walls
Obstacles: static circles and line segments inside the arena.
"""

import math
import random
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from enum import Enum


class ArenaMechanic(Enum):
    NONE = "none"
    SHRINKING = "shrinking"
    MOVING_WALLS = "moving_walls"
    ROTATING = "rotating"


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

    def dot(self, other: "Vector2") -> float:
        return self.x * other.x + self.y * other.y

    def magnitude(self) -> float:
        return math.sqrt(self.x**2 + self.y**2)

    def normalize(self) -> "Vector2":
        mag = self.magnitude()
        if mag == 0:
            return Vector2(0, 0)
        return Vector2(self.x / mag, self.y / mag)

    def rotate(self, angle: float) -> "Vector2":
        """Rotate vector by angle in radians."""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return Vector2(
            self.x * cos_a - self.y * sin_a,
            self.x * sin_a + self.y * cos_a
        )

    def perpendicular(self) -> "Vector2":
        """Return a perpendicular vector (90° counterclockwise)."""
        return Vector2(-self.y, self.x)


# ─── Obstacles ─────────────────────────────────────────────────────────────────

@dataclass
class Obstacle:
    """Base obstacle — override collision_test()."""
    color: Tuple[int, int, int] = (80, 80, 120)



@dataclass
class CircleObstacle:
    """Static circle obstacle."""
    cx: float = 0.0
    cy: float = 0.0
    radius: float = 20.0
    color: Tuple[int, int, int] = (100, 120, 180)

    def collision_test(self, pos: Vector2, radius: float):
        dx = pos.x - self.cx
        dy = pos.y - self.cy
        dist = math.sqrt(dx*dx + dy*dy)
        min_dist = self.radius + radius
        if dist < min_dist and dist > 0:
            normal = Vector2(dx / dist, dy / dist)
            depth = min_dist - dist
            return (normal, depth)
        return None

    def draw(self, draw, frame: int):
        import PIL.ImageDraw
        if isinstance(draw, PIL.ImageDraw.ImageDraw):
            draw.ellipse(
                [self.cx - self.radius, self.cy - self.radius,
                 self.cx + self.radius, self.cy + self.radius],
                outline=self.color, width=2
            )


@dataclass
class LineObstacle:
    """Static line segment obstacle defined by two endpoints."""
    x1: float = 0.0
    y1: float = 0.0
    x2: float = 0.0
    y2: float = 0.0
    color: Tuple[int, int, int] = (120, 100, 160)

    def _closest_point_on_segment(self, px: float, py: float):
        dx = self.x2 - self.x1
        dy = self.y2 - self.y1
        length_sq = dx*dx + dy*dy
        if length_sq == 0:
            return (self.x1, self.y1, 0.0)
        t = max(0.0, min(1.0, ((px - self.x1) * dx + (py - self.y1) * dy) / length_sq))
        return (self.x1 + t * dx, self.y1 + t * dy, t)

    def collision_test(self, pos: Vector2, radius: float):
        cx, cy, _ = self._closest_point_on_segment(pos.x, pos.y)
        dx = pos.x - cx
        dy = pos.y - cy
        dist = math.sqrt(dx*dx + dy*dy)
        if dist < radius and dist > 0:
            normal = Vector2(dx / dist, dy / dist)
            depth = radius - dist
            return (normal, depth)
        return None

    def draw(self, draw, frame: int):
        draw.line([self.x1, self.y1, self.x2, self.y2], self.color, width=3)


@dataclass
class MovingCircleObstacle(CircleObstacle):
    """Circle obstacle that moves sinusoidally."""
    base_cx: float = 0.0
    base_cy: float = 0.0
    amplitude_x: float = 0.0
    amplitude_y: float = 0.0
    speed_x: float = 1.0
    speed_y: float = 1.0

    def update_position(self, frame: int):
        self.cx = self.base_cx + math.sin(frame * self.speed_x) * self.amplitude_x
        self.cy = self.base_cy + math.sin(frame * self.speed_y) * self.amplitude_y


# ─── Arena Bounds ──────────────────────────────────────────────────────────────

@dataclass
class ArenaBounds:
    """Dynamic arena boundaries driven by the current mechanic."""
    left: float
    right: float   # exclusive right edge
    top: float
    bottom: float   # exclusive bottom edge

    def width(self) -> float:
        return self.right - self.left

    def height(self) -> float:
        return self.bottom - self.top

    def contains(self, x: float, y: float) -> bool:
        return self.left <= x <= self.right and self.top <= y <= self.bottom

    def center(self) -> Tuple[float, float]:
        return ((self.left + self.right) * 0.5, (self.top + self.bottom) * 0.5)


# ─── Arena ─────────────────────────────────────────────────────────────────────

@dataclass
class Arena:
    """
    Arena state including bounds and obstacles.
    """
    width: int
    height: int
    mechanic: ArenaMechanic = ArenaMechanic.NONE
    obstacles: List[Obstacle] = field(default_factory=list)
    frame: int = 0

    # Shrinking params
    shrink_duration_frames: int = 300
    shrink_min_margin: float = 80.0

    # Moving walls params
    wall_amplitude: float = 60.0
    wall_speed: float = 0.02

    # Rotating params
    rotation_angle: float = 0.0
    rotation_speed: float = 0.008  # radians per frame
    max_rotation: float = math.pi / 6  # ±30°

    def _static_bounds(self) -> ArenaBounds:
        return ArenaBounds(left=0.0, right=float(self.width),
                           top=0.0, bottom=float(self.height))

    def _shrinking_bounds(self) -> ArenaBounds:
        progress = min(1.0, self.frame / self.shrink_duration_frames)
        margin = self.shrink_min_margin + (min(self.width, self.height) * 0.5 - self.shrink_min_margin) * (1.0 - progress)
        return ArenaBounds(
            left=margin,
            right=float(self.width) - margin,
            top=margin,
            bottom=float(self.height) - margin
        )

    def _moving_walls_bounds(self) -> ArenaBounds:
        cx = self.width * 0.5
        cy = self.height * 0.5
        base_margin = 40.0

        offset_x = math.sin(self.frame * self.wall_speed) * self.wall_amplitude
        offset_y = math.cos(self.frame * self.wall_speed * 0.7) * self.wall_amplitude

        half_w = (self.width * 0.5 - base_margin - abs(offset_x))
        half_h = (self.height * 0.5 - base_margin - abs(offset_y))
        half_w = max(half_w, self.shrink_min_margin)
        half_h = max(half_h, self.shrink_min_margin)

        return ArenaBounds(
            left=cx - half_w,
            right=cx + half_w,
            top=cy - half_h,
            bottom=cy + half_h
        )

    def _rotating_bounds(self) -> ArenaBounds:
        # In rotating mode, bounds are static but the ball is in a rotated space.
        # We keep the full static bounds so the ball can move anywhere,
        # and handle wall collisions in rotated space.
        return self._static_bounds()

    def get_bounds(self) -> ArenaBounds:
        if self.mechanic == ArenaMechanic.SHRINKING:
            return self._shrinking_bounds()
        elif self.mechanic == ArenaMechanic.MOVING_WALLS:
            return self._moving_walls_bounds()
        elif self.mechanic == ArenaMechanic.ROTATING:
            return self._rotating_bounds()
        return self._static_bounds()

    def get_rotation(self) -> float:
        if self.mechanic == ArenaMechanic.ROTATING:
            progress = min(1.0, self.frame / (self.shrink_duration_frames * 2))
            self.rotation_angle = math.sin(progress * math.pi) * self.max_rotation * math.sin(self.frame * self.rotation_speed)
        return self.rotation_angle

    def advance(self):
        """Advance the arena by one frame."""
        self.frame += 1
        # Update any moving obstacles
        for obs in self.obstacles:
            if isinstance(obs, MovingCircleObstacle):
                obs.update_position(self.frame)

    def ball_inside_arena(self, x: float, y: float, radius: float) -> bool:
        """Check if ball circle is fully inside the non-rotated arena bounds."""
        return (radius <= x <= self.width - radius and
                radius <= y <= self.height - radius)

    def transform_ball_to_arena_space(self, pos: Vector2, bounds: ArenaBounds) -> Vector2:
        """
        Transform ball position into the rotating arena's local coordinate space.
        For rotating mechanic, we apply the inverse rotation to the ball's position
        relative to the arena center.
        """
        if self.mechanic != ArenaMechanic.ROTATING:
            return pos

        cx, cy = bounds.center()
        angle = self.get_rotation()
        # Inverse rotate to get position in non-rotated space
        relative = Vector2(pos.x - cx, pos.y - cy)
        rotated = relative.rotate(-angle)
        return Vector2(rotated.x + cx, rotated.y + cy)

    def ball_collision_with_rotated_walls(self, pos: Vector2, vel: Vector2,
                                           radius: float, bounds: ArenaBounds):
        """
        Handle ball collisions with walls when the arena is rotated.
        Returns a list of (normal, speed) tuples for collisions.
        """
        cx, cy = bounds.center()
        angle = self.get_rotation()

        # Transform ball position to arena space
        local_pos = self.transform_ball_to_arena_space(pos, bounds)

        collisions = []
        speed = vel.magnitude()

        # Left wall
        if local_pos.x - radius < bounds.left:
            normal_global = Vector2(1, 0).rotate(angle)
            normal_local = Vector2(1, 0)
            if speed > 0.5:
                collisions.append((normal_global, speed))
        # Right wall
        if local_pos.x + radius > bounds.right:
            normal_global = Vector2(-1, 0).rotate(angle)
            if speed > 0.5:
                collisions.append((normal_global, speed))
        # Top wall
        if local_pos.y - radius < bounds.top:
            normal_global = Vector2(0, 1).rotate(angle)
            if speed > 0.5:
                collisions.append((normal_global, speed))
        # Bottom wall
        if local_pos.y + radius > bounds.bottom:
            normal_global = Vector2(0, -1).rotate(angle)
            if speed > 0.5:
                collisions.append((normal_global, speed))

        return collisions


# ─── Arena Creation ────────────────────────────────────────────────────────────

def create_arena(width: int, height: int, mechanic: ArenaMechanic,
                 seed: int, style: dict) -> Arena:
    """
    Factory: build an Arena from a seed for reproducible obstacle placement.
    """
    rng = random.Random(seed)

    obstacle_count = style.get("obstacle_count", 0)
    obstacles: List[Obstacle] = []

    for _ in range(obstacle_count):
        obstacle_type = rng.choice(["circle", "line"])

        if obstacle_type == "circle":
            margin = 100
            cx = rng.uniform(margin, width - margin)
            cy = rng.uniform(margin, height - margin)
            r = rng.uniform(20, 60)
            color = tuple(rng.randint(80, 140) for _ in range(3))
            circle = CircleObstacle(cx=cx, cy=cy, radius=r, color=color)

            # Some circles move
            if rng.random() < 0.3:
                circle = MovingCircleObstacle(
                    cx=cx, cy=cy, radius=r, color=color,
                    base_cx=cx, base_cy=cy,
                    amplitude_x=rng.uniform(20, 50),
                    amplitude_y=rng.uniform(20, 50),
                    speed_x=rng.uniform(0.01, 0.03),
                    speed_y=rng.uniform(0.01, 0.03),
                )
            obstacles.append(circle)

        elif obstacle_type == "line":
            margin = 80
            x1 = rng.uniform(margin, width - margin)
            y1 = rng.uniform(margin, height - margin)
            length = rng.uniform(60, 150)
            angle = rng.uniform(0, math.pi)
            x2 = x1 + math.cos(angle) * length
            y2 = y1 + math.sin(angle) * length
            color = tuple(rng.randint(90, 150) for _ in range(3))
            obstacles.append(LineObstacle(x1=x1, y1=y1, x2=x2, y2=y2, color=color))

    arena = Arena(
        width=width,
        height=height,
        mechanic=mechanic,
        obstacles=obstacles,
    )

    # Mechanic-specific overrides from style
    if mechanic == ArenaMechanic.SHRINKING:
        arena.shrink_duration_frames = style.get("shrink_duration_frames", 300)
        arena.shrink_min_margin = style.get("shrink_min_margin", 80.0)
    elif mechanic == ArenaMechanic.MOVING_WALLS:
        arena.wall_amplitude = style.get("wall_amplitude", 60.0)
        arena.wall_speed = style.get("wall_speed", 0.02)
    elif mechanic == ArenaMechanic.ROTATING:
        arena.rotation_speed = style.get("rotation_speed", 0.008)
        arena.max_rotation = style.get("max_rotation", math.pi / 6)

    return arena
