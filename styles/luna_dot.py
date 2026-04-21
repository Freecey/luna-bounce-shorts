"""
Luna Dot Style — ultra-minimal, line-only aesthetic.
The ball is rendered as a thin dot or short line segment.
Perfect for "satisfying line" ASMR visuals.
"""

DOT_COSMIC = {
    "name": "Dot Cosmic",
    "description": "Un point de lumière traverse le cosmos",

    # Background
    "background": (5, 3, 15),

    # Dot rendering
    "dot_mode": True,           # Use dot/line instead of ball
    "dot_size": 2,              # Pixel size of dot
    "dot_color": (255, 248, 200),  # Warm white dot
    "dot_glow": True,
    "dot_glow_radius": 8,
    "dot_glow_color": (255, 215, 100),
    "dot_trail": True,         # Trail follows dot
    "dot_trail_fade": True,
    "dot_trail_max": 60,       # More trail points for thinner look

    # Physics
    "bounce": 0.82,
    "gravity": 0.28,
    "speed_min": 5,
    "speed_max": 12,

    # Particles (minimal)
    "particles_on_hit": False,  # No particles — pure line
    "flash_on_hit": True,
    "flash_decay": 0.08,

    # Post
    "vignette": True,
    "vignette_strength": 0.7,
}

DOT_THRESHOLD = {
    "name": "Dot Threshold",
    "description": "Une ligne fine hésite sur le seuil",

    "background": (8, 5, 10),

    "dot_mode": True,
    "dot_size": 2,
    "dot_color": (255, 245, 230),
    "dot_glow": True,
    "dot_glow_radius": 6,
    "dot_glow_color": (255, 230, 200),
    "dot_trail": True,
    "dot_trail_fade": True,
    "dot_trail_max": 50,

    "bounce": 0.88,
    "gravity": 0.32,
    "speed_min": 4,
    "speed_max": 10,

    "particles_on_hit": False,
    "flash_on_hit": True,
    "flash_decay": 0.06,

    "vignette": True,
    "vignette_strength": 0.75,
}

DOT_AURORA = {
    "name": "Dot Aurora",
    "description": "Un fil de lumière boréale",

    "background": (3, 8, 20),

    "dot_mode": True,
    "dot_size": 2,
    "dot_color": (0, 255, 200),
    "dot_glow": True,
    "dot_glow_radius": 10,
    "dot_glow_color": (0, 212, 170),
    "dot_trail": True,
    "dot_trail_fade": True,
    "dot_trail_max": 70,

    "bounce": 0.80,
    "gravity": 0.22,
    "speed_min": 5,
    "speed_max": 13,

    "particles_on_hit": False,
    "flash_on_hit": True,
    "flash_decay": 0.10,

    "vignette": True,
    "vignette_strength": 0.6,
}

DOT_COSMIC_LINE = {
    "name": "Dot Cosmic Line",
    "description": "Un trait doré fend l'espace",

    "background": (10, 5, 20),

    "dot_mode": "line",         # Short line showing velocity direction
    "dot_size": 2,
    "line_length": 12,          # Length of velocity line
    "line_color": (255, 215, 100),
    "line_glow": True,
    "line_glow_radius": 6,
    "dot_trail": True,
    "dot_trail_fade": True,
    "dot_trail_max": 80,

    "bounce": 0.82,
    "gravity": 0.25,
    "speed_min": 6,
    "speed_max": 14,

    "particles_on_hit": False,
    "flash_on_hit": True,
    "flash_decay": 0.07,

    "vignette": True,
    "vignette_strength": 0.65,
}

DOT_STARDUST = {
    "name": "Dot Stardust",
    "description": "Poussière d'étoiles en chute",

    "background": (2, 1, 8),

    "dot_mode": "stardust",     # Multiple tiny dots like star field
    "dot_count": 3,             # Number of tiny balls
    "dot_size_range": [1, 3],   # Random sizes
    "dot_color": (255, 248, 220),
    "dot_glow": True,
    "dot_glow_radius": 5,
    "dot_trail": True,
    "dot_trail_fade": True,
    "dot_trail_max": 40,

    "bounce": 0.78,
    "gravity": 0.20,
    "speed_min": 4,
    "speed_max": 11,

    "particles_on_hit": False,
    "flash_on_hit": True,
    "flash_decay": 0.05,

    "vignette": True,
    "vignette_strength": 0.8,
}

DOT_THRESHOLD_VIOLET = {
    "name": "Dot Threshold Violet",
    "description": "Un fil violet entre deux mondes",

    "background": (6, 3, 12),

    "dot_mode": "line",
    "dot_size": 2,
    "line_length": 10,
    "line_color": (180, 130, 255),
    "line_glow": True,
    "line_glow_radius": 8,
    "line_glow_color": (140, 80, 255),
    "dot_trail": True,
    "dot_trail_fade": True,
    "dot_trail_max": 65,

    "bounce": 0.85,
    "gravity": 0.30,
    "speed_min": 5,
    "speed_max": 12,

    "particles_on_hit": False,
    "flash_on_hit": True,
    "flash_decay": 0.08,

    "vignette": True,
    "vignette_strength": 0.7,
}


def get_dot_style(name: str):
    styles = {
        "cosmic": DOT_COSMIC,
        "threshold": DOT_THRESHOLD,
        "aurora": DOT_AURORA,
        "line": DOT_COSMIC_LINE,
        "stardust": DOT_STARDUST,
        "violet": DOT_THRESHOLD_VIOLET,
    }
    return styles.get(name.lower(), DOT_COSMIC)


def list_dot_styles():
    return [
        ("cosmic", DOT_COSMIC["name"], DOT_COSMIC["description"]),
        ("threshold", DOT_THRESHOLD["name"], DOT_THRESHOLD["description"]),
        ("aurora", DOT_AURORA["name"], DOT_AURORA["description"]),
        ("line", DOT_COSMIC_LINE["name"], DOT_COSMIC_LINE["description"]),
        ("stardust", DOT_STARDUST["name"], DOT_STARDUST["description"]),
        ("violet", DOT_THRESHOLD_VIOLET["name"], DOT_THRESHOLD_VIOLET["description"]),
    ]
