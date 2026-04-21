"""
Microcosm Style presets for Bounce Shorts.
Enhanced arena behaviors and physics modes for the Microcosm series.
Each style configures physics, arena behavior, and visual theme.
"""

# =============================================================================
# ESCAPE — The ball fights to break free from a collapsing arena
# =============================================================================
MICRO_ESCAPE = {
    "name": "Micro Escape",
    "description": "Une lumière piégée qui lutte pour s'échapper d'un espace qui se rétrécit",

    # Background
    "background": (15, 3, 25),              # Dark violet void
    "background_gradient": True,

    # Arena behavior
    "arena_mode": "shrink",                  # Walls slowly close in
    "arena_shrink_rate": 0.02,              # Shrink per second
    "arena_min_radius": 0.25,                # Minimum arena size (% of screen)

    # Ball
    "colors": [
        (255, 100, 150),                     # Desperate pink
        (255, 180, 100),                     # Warning orange
        (255, 80, 120),                      # Urgent red-pink
    ],
    "glow_color": (255, 120, 150),          # Pink urgency glow
    "glow_enabled": True,
    "glow_radius_mult": 3.5,
    "ball_radius_min": 18,
    "ball_radius_max": 30,
    "bounce": 0.92,                          # High bounce — fighting hard
    "gravity": 0.35,                         # Strong pull for drama

    # Trail
    "trail_enabled": True,
    "trail_color": (255, 120, 150),          # Pink trail of desperation

    # Particles
    "particle_count": 15,
    "particle_color": (255, 150, 180),       # Soft pink sparks

    # Visual elements
    "grid_enabled": True,
    "grid_color": (60, 20, 80),              # Faint violet grid
    "center_ring": True,
    "stars_enabled": True,
    "arena_border": True,
    "arena_border_color": (255, 80, 120),    # Red warning border

    # Post effects
    "vignette": True,
    "vignette_strength": 0.5,
    "bloom": True,
    "shake_on_escape": True,                 # Screen shake when ball hits shrinking wall

    # Physics
    "speed_min": 7,
    "speed_max": 16,
}


# =============================================================================
# TRAP — Sticky zones and momentum-draining walls
# =============================================================================
MICRO_TRAP = {
    "name": "Micro Trap",
    "description": "Labyrinthe de zones gluantes où la lumière se fait piéger",

    # Background
    "background": (5, 12, 8),                 # Dark swamp green
    "background_gradient": True,

    # Arena behavior
    "arena_mode": "trap",                    # Sticky zones active
    "trap_zones": [                          # Defined sticky zones
        {"pos": (0.5, 0.5), "radius": 0.15, "strength": 0.7},
        {"pos": (0.25, 0.25), "radius": 0.10, "strength": 0.5},
        {"pos": (0.75, 0.75), "radius": 0.10, "strength": 0.5},
    ],

    # Ball
    "colors": [
        (100, 255, 180),                     # Trapped teal
        (80, 200, 160),                      # Muted green
        (120, 240, 200),                     # Lighter teal
    ],
    "glow_color": (100, 255, 180),           # Teal glow
    "glow_enabled": True,
    "glow_radius_mult": 2.8,
    "ball_radius_min": 16,
    "ball_radius_max": 26,
    "bounce": 0.65,                          # Low bounce — losing momentum
    "gravity": 0.20,

    # Trail
    "trail_enabled": True,
    "trail_color": (100, 220, 160),           # Greenish trail

    # Particles
    "particle_count": 8,
    "particle_color": (100, 255, 180),       # Teal sparks
    "particles_on_trap": True,               # Extra particles in trap zones

    # Visual elements
    "grid_enabled": False,
    "center_ring": True,
    "stars_enabled": False,
    "trap_zone_visual": True,                # Show trap zones
    "trap_zone_color": (80, 180, 140),       # Translucent green zones

    # Post effects
    "vignette": True,
    "vignette_strength": 0.55,
    "bloom": True,
    "slowdown_effect": True,                 # Visual slowmo in trap zones

    # Physics
    "speed_min": 4,
    "speed_max": 10,
}


# =============================================================================
# ROTATE — The entire arena spins, creating artificial gravity
# =============================================================================
MICRO_ROTATE = {
    "name": "Micro Rotate",
    "description": "L'arène tourne sur elle-même, la gravité devient un choix",

    # Background
    "background": (8, 5, 18),                 # Deep cosmic purple
    "background_gradient": True,

    # Arena behavior
    "arena_mode": "rotate",                   # Rotating arena
    "rotation_speed": 0.8,                   # Radians per second
    "rotation_direction": 1,                 # 1 = clockwise, -1 = counter-clockwise

    # Ball
    "colors": [
        (200, 150, 255),                     # Spinning violet
        (150, 200, 255),                     # Ice violet
        (180, 130, 255),                     # Lavender
    ],
    "glow_color": (180, 150, 255),           # Violet glow
    "glow_enabled": True,
    "glow_radius_mult": 3.2,
    "ball_radius_min": 18,
    "ball_radius_max": 32,
    "bounce": 0.85,
    "gravity": 0.25,
    "gravity_rotation_offset": 0.5,          # Gravity direction offset from rotation

    # Trail
    "trail_enabled": True,
    "trail_color": (170, 130, 255),           # Purple swirl trail

    # Particles
    "particle_count": 12,
    "particle_color": (180, 150, 255),       # Violet sparks

    # Visual elements
    "grid_enabled": True,
    "grid_color": (40, 25, 70),              # Faint rotating grid
    "center_ring": True,
    "stars_enabled": True,
    "rotation_trails": True,                 # Show arena rotation direction

    # Post effects
    "vignette": True,
    "vignette_strength": 0.45,
    "bloom": True,
    "coriolis_effect": True,                 # Visual effect for rotation

    # Physics
    "speed_min": 6,
    "speed_max": 14,
}


# =============================================================================
# SPIRAL — Curved gravity wells creating spiral trajectories
# =============================================================================
MICRO_SPIRAL = {
    "name": "Micro Spiral",
    "description": "Des puits de gravité courbent la lumière en spirales infinies",

    # Background
    "background": (3, 8, 20),                # Deep ocean blue
    "background_gradient": True,

    # Arena behavior
    "arena_mode": "spiral",                  # Spiral gravity wells
    "spiral_centers": [
        {"pos": (0.5, 0.5), "strength": 0.4, "direction": 1},
    ],
    "spiral_strength": 0.6,                  # How much gravity wells pull

    # Ball
    "colors": [
        (0, 200, 255),                       # Deep spiral blue
        (0, 180, 220),                       # Ocean blue
        (100, 220, 255),                     # Sky blue
    ],
    "glow_color": (0, 200, 255),             # Blue glow
    "glow_enabled": True,
    "glow_radius_mult": 3.0,
    "ball_radius_min": 16,
    "ball_radius_max": 28,
    "bounce": 0.80,
    "gravity": 0.30,

    # Trail
    "trail_enabled": True,
    "trail_color": (0, 190, 240),             # Blue spiral trail
    "trail_spiral": True,                     # Trail follows spiral curve

    # Particles
    "particle_count": 10,
    "particle_color": (0, 200, 255),         # Blue sparks

    # Visual elements
    "grid_enabled": False,
    "center_ring": True,
    "stars_enabled": True,
    "spiral_lines": True,                     # Show spiral gravity field
    "spiral_line_color": (0, 100, 150),      # Faint spiral guides

    # Post effects
    "vignette": True,
    "vignette_strength": 0.50,
    "bloom": True,
    "wave_distortion": True,                 # Slight wave effect

    # Physics
    "speed_min": 5,
    "speed_max": 13,
}


# =============================================================================
# OBSTACLE — Navigate through a field of barriers and walls
# =============================================================================
MICRO_OBSTACLE = {
    "name": "Micro Obstacle",
    "description": "Forêt de barrières lumineuses à traverser",

    # Background
    "background": (10, 8, 5),                # Dark amber
    "background_gradient": True,

    # Arena behavior
    "arena_mode": "obstacle",               # Obstacle field
    "obstacles": [                           # Define obstacle walls
        {"type": "h", "y": 0.3, "x_start": 0.2, "x_end": 0.8},
        {"type": "v", "x": 0.6, "y_start": 0.4, "y_end": 0.9},
        {"type": "h", "y": 0.7, "x_start": 0.1, "x_end": 0.5},
        {"type": "v", "x": 0.3, "y_start": 0.1, "y_end": 0.6},
    ],
    "obstacle_thickness": 8,                # Pixel thickness of obstacles

    # Ball
    "colors": [
        (255, 200, 100),                    # Golden light
        (255, 180, 80),                      # Warm amber
        (255, 220, 120),                    # Bright gold
    ],
    "glow_color": (255, 200, 100),           # Golden glow
    "glow_enabled": True,
    "glow_radius_mult": 3.0,
    "ball_radius_min": 14,
    "ball_radius_max": 22,
    "bounce": 0.78,
    "gravity": 0.28,

    # Trail
    "trail_enabled": True,
    "trail_color": (255, 190, 100),          # Golden trail

    # Particles
    "particle_count": 10,
    "particle_color": (255, 200, 120),       # Golden sparks
    "particles_on_hit": True,                # Particles when hitting obstacles

    # Visual elements
    "grid_enabled": False,
    "center_ring": False,
    "stars_enabled": False,
    "obstacle_color": (200, 150, 80),        # Amber barriers
    "obstacle_glow": True,

    # Post effects
    "vignette": True,
    "vignette_strength": 0.45,
    "bloom": True,
    "flash_on_obstacle_hit": True,           # Flash effect on collision

    # Physics
    "speed_min": 6,
    "speed_max": 14,
}


# =============================================================================
# MULTI — Multiple balls with inter-ball physics
# =============================================================================
MICRO_MULTI = {
    "name": "Micro Multi",
    "description": "Plusieurs lumières interagissent en parfaite harmonie",

    # Background
    "background": (5, 10, 25),                # Deep space blue
    "background_gradient": True,

    # Arena behavior
    "arena_mode": "multi",                   # Multiple balls
    "ball_count": 3,                         # Number of balls
    "ball_interaction": True,                # Balls interact with each other
    "collision_strength": 0.9,              # How much they bounce off each other

    # Ball
    "colors": [
        (255, 150, 100),                     # Warm coral
        (100, 200, 255),                     # Cool sky
        (200, 255, 150),                     # Fresh mint
    ],
    "glow_color": (200, 200, 255),           # Combined soft glow
    "glow_enabled": True,
    "glow_radius_mult": 2.5,
    "ball_radius_min": 14,
    "ball_radius_max": 24,
    "bounce": 0.85,
    "gravity": 0.22,

    # Trail
    "trail_enabled": True,
    "trail_color": (180, 180, 220),          # Soft combined trail
    "trail_per_ball": True,                  # Each ball has own trail color

    # Particles
    "particle_count": 8,
    "particle_color": (200, 200, 255),      # Soft white sparks
    "particles_on_collision": True,         # Sparks when balls collide

    # Visual elements
    "grid_enabled": False,
    "center_ring": True,
    "stars_enabled": True,
    "connection_lines": True,                 # Draw lines between nearby balls
    "connection_distance": 150,              # Max distance for connections

    # Post effects
    "vignette": True,
    "vignette_strength": 0.45,
    "bloom": True,
    "color_blend": True,                     # Balls blend colors on collision

    # Physics
    "speed_min": 5,
    "speed_max": 12,
}


# =============================================================================
# Style lookup functions
# =============================================================================

def get_micro_style(name: str):
    """Get microcosm style by name."""
    styles = {
        "escape": MICRO_ESCAPE,
        "trap": MICRO_TRAP,
        "rotate": MICRO_ROTATE,
        "spiral": MICRO_SPIRAL,
        "obstacle": MICRO_OBSTACLE,
        "multi": MICRO_MULTI,
    }
    return styles.get(name.lower(), MICRO_ESCAPE)


def list_micro_styles():
    """List all available microcosm styles."""
    return [
        ("escape", MICRO_ESCAPE["name"], MICRO_ESCAPE["description"]),
        ("trap", MICRO_TRAP["name"], MICRO_TRAP["description"]),
        ("rotate", MICRO_ROTATE["name"], MICRO_ROTATE["description"]),
        ("spiral", MICRO_SPIRAL["name"], MICRO_SPIRAL["description"]),
        ("obstacle", MICRO_OBSTACLE["name"], MICRO_OBSTACLE["description"]),
        ("multi", MICRO_MULTI["name"], MICRO_MULTI["description"]),
    ]
