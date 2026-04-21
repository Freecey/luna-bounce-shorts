#!/usr/bin/env python3
"""
Bounce Shorts Generator — Luna Creative Archive
A generator for satisfying ASMR-style vertical shorts.
Microcosm series: physics-based procedural animations.

Usage:
    python main.py                          # One video (random)
    python main.py --batch 5                # 5 variants
    python main.py --style cosmic            # Luna ball styles
    python main.py --style dot_cosmic        # Dot (minimal) styles
    python main.py --style micro_escape      # Microcosm series
    python main.py --style micro_multi        # Multi-ball physics
    python main.py --style micro_rotate      # Rotating arena
    python main.py --list-styles            # Show all styles
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
sys.path.insert(0, os.path.dirname(__file__))

from src.simulator import render_scene, render_batch
from styles.luna import list_styles as list_ball_styles
from styles.luna_dot import list_dot_styles
from styles.microcosm import list_micro_styles, get_micro_style


def main():
    args = sys.argv[1:]

    if "--list-styles" in args:
        print("\n🌙 Luna Ball Styles:\n")
        for key, name, desc in list_ball_styles():
            print(f"  ball_{key:10} — {name}")
            print(f"                {desc}\n")
        print("\n✨ Luna Dot Styles (minimal):\n")
        for key, name, desc in list_dot_styles():
            print(f"  dot_{key:9} — {name}")
            print(f"                {desc}\n")
        print("\n🌀 Microcosm Series:\n")
        for key, name, desc in list_micro_styles():
            print(f"  micro_{key:7} — {name}")
            print(f"                {desc}\n")
        return

    import argparse
    parser = argparse.ArgumentParser(description="Luna Bounce Shorts Generator")
    parser.add_argument("--batch", "-b", type=int, default=1,
                        help="Number of videos to generate")
    parser.add_argument("--style", "-s", default="cosmic",
                        help="Style name (see --list-styles)")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed for reproducibility")
    parser.add_argument("--duration", "-d", type=int, default=15,
                        help="Video duration in seconds (15-60)")
    parser.add_argument("--fps", type=int, default=30,
                        help="Frames per second")
    parser.add_argument("--width", type=int, default=720,
                        help="Video width")
    parser.add_argument("--height", type=int, default=1280,
                        help="Video height")
    parser.add_argument("--arena", default=None,
                        help="Arena mechanic: shrinking, moving, rotating (auto from style)")

    parsed = parser.parse_args(args if args else ["--batch", "1"])

    # Resolve style
    style_name = parsed.style

    # Check microcosm styles
    micro_styles = {k: (n, d) for k, n, d in list_micro_styles()}
    if style_name in micro_styles or style_name.startswith("micro_"):
        # Already a micro_ style
        pass

    # Resolve seed
    if parsed.seed is None:
        import random
        parsed.seed = random.randint(0, 999999)

    print(f"\n🌙 Luna Bounce Shorts — {style_name} Mode\n")
    output = render_scene(
        seed=parsed.seed,
        style_name=style_name,
        duration=parsed.duration,
        fps=parsed.fps,
        width=parsed.width,
        height=parsed.height,
    )
    print(f"\n✨ Done: {output}")


if __name__ == "__main__":
    main()
