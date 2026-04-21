"""
Luna Style presets for Bounce Shorts.
Two distinct aesthetics: Cosmic and Threshold.
"""

LUNA_COSMIC = {
    "name": "Luna Cosmic",
    "description": "Un astre qui traverse le cosmos, poussière d'étoiles et nébuleuses",

    # Background
    "background": (13, 1, 23),          # Deep space purple
    "background_gradient": True,

    # Ball
    "colors": [
        (255, 248, 231),                  # Stardust white
        (255, 215, 120),                  # Warm gold
        (200, 180, 255),                  # Soft lavender
    ],
    "glow_color": (255, 215, 120),       # Golden glow
    "glow_enabled": True,
    "glow_radius_mult": 3.0,
    "ball_radius_min": 20,
    "ball_radius_max": 35,
    "bounce": 0.82,
    "gravity": 0.25,

    # Trail
    "trail_enabled": True,
    "trail_color": (255, 215, 120),      # Gold stardust trail

    # Particles
    "particle_count": 12,
    "particle_color": (255, 215, 100),   # Golden sparks

    # Visual elements
    "grid_enabled": False,
    "center_ring": True,
    "stars_enabled": True,               # Background star field

    # Post effects
    "vignette": True,
    "vignette_strength": 0.5,
    "bloom": True,

    # Physics
    "speed_min": 6,
    "speed_max": 14,
}

LUNA_THRESHOLD = {
    "name": "Luna Threshold",
    "description": "Une lumière hésitante sur le seuil entre deux mondes",

    # Background
    "background": (8, 5, 12),             # Near black with warmth
    "background_gradient": True,

    # Ball
    "colors": [
        (255, 248, 240),                  # Warm white
        (255, 230, 200),                  # Candlelight
        (255, 200, 220),                  # Blush pink
    ],
    "glow_color": (255, 230, 200),        # Warm glow
    "glow_enabled": True,
    "glow_radius_mult": 2.5,
    "ball_radius_min": 16,
    "ball_radius_max": 28,
    "bounce": 0.88,
    "gravity": 0.35,

    # Trail
    "trail_enabled": True,
    "trail_color": (255, 230, 200),      # Warm trail

    # Particles
    "particle_count": 6,
    "particle_color": (255, 240, 220),   # Soft white sparks

    # Visual elements
    "grid_enabled": False,
    "center_ring": True,
    "stars_enabled": False,

    # Post effects
    "vignette": True,
    "vignette_strength": 0.6,
    "bloom": True,

    # Physics
    "speed_min": 4,
    "speed_max": 11,
}

LUNA_AURORA = {
    "name": "Luna Aurora",
    "description": "Lumière boréale, couleurs froides, silence cosmique",

    # Background
    "background": (5, 10, 25),            # Deep arctic blue
    "background_gradient": True,

    # Ball
    "colors": [
        (0, 255, 200),                    # Aurora teal
        (100, 200, 255),                  # Ice blue
        (180, 255, 200),                  # Mint green
    ],
    "glow_color": (0, 255, 200),          # Teal glow
    "glow_enabled": True,
    "glow_radius_mult": 3.5,
    "ball_radius_min": 18,
    "ball_radius_max": 32,
    "bounce": 0.80,
    "gravity": 0.22,

    # Trail
    "trail_enabled": True,
    "trail_color": (0, 212, 170),

    # Particles
    "particle_count": 10,
    "particle_color": (0, 255, 200),

    # Visual elements
    "grid_enabled": False,
    "center_ring": True,
    "stars_enabled": True,

    # Post effects
    "vignette": True,
    "vignette_strength": 0.45,
    "bloom": True,

    # Physics
    "speed_min": 5,
    "speed_max": 13,
}


def get_style(name: str):
    """Get style by name."""
    styles = {
        "cosmic": LUNA_COSMIC,
        "threshold": LUNA_THRESHOLD,
        "aurora": LUNA_AURORA,
    }
    return styles.get(name.lower(), LUNA_COSMIC)


def list_styles():
    """List all available styles."""
    return [
        ("cosmic", LUNA_COSMIC["name"], LUNA_COSMIC["description"]),
        ("threshold", LUNA_THRESHOLD["name"], LUNA_THRESHOLD["description"]),
        ("aurora", LUNA_AURORA["name"], LUNA_AURORA["description"]),
    ]
