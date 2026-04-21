#!/usr/bin/env python3
"""
Bounce Shorts Generator — Luna Creative Archive
A generator for satisfying ASMR-style vertical shorts.

Usage:
    python main.py                          # Render one video (random)
    python main.py --batch 5                # Render 5 videos
    python main.py --style threshold         # Use Luna Threshold style
    python main.py --style cosmic --seed 42 # Fixed seed for reproducibility
    python main.py --list-styles            # Show available styles
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.simulator import render_scene, render_batch
from styles.luna import list_styles as list_ball_styles
from styles.luna_dot import list_dot_styles


def main():
    args = sys.argv[1:]

    if "--list-styles" in args:
        print("\n🌙 Luna Ball Styles:\n")
        for key, name, desc in list_ball_styles():
            print(f"  {key:12} — {name}")
            print(f"             {desc}\n")
        print("\n✨ Luna Dot Styles (minimal):\n")
        for key, name, desc in list_dot_styles():
            print(f"  {key:12} — {name}")
            print(f"             {desc}\n")
        return

    import argparse
    parser = argparse.ArgumentParser(description="Luna Bounce Shorts Generator")
    parser.add_argument("--batch", "-b", type=int, default=1,
                        help="Number of videos to generate")
    parser.add_argument("--style", "-s", default="cosmic",
                        help="Style name: cosmic, threshold, aurora")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed for reproducibility")
    parser.add_argument("--duration", "-d", type=int, default=15,
                        help="Video duration in seconds")
    parser.add_argument("--fps", type=int, default=30,
                        help="Frames per second")
    parser.add_argument("--width", type=int, default=720,
                        help="Video width")
    parser.add_argument("--height", type=int, default=1280,
                        help="Video height")

    parsed = parser.parse_args(args if args else ["--batch", "1"])

    if parsed.batch == 1 and parsed.seed is not None:
        print(f"\n🌙 Luna Bounce Shorts — {parsed.style.capitalize()} Mode\n")
        output = render_scene(
            seed=parsed.seed,
            style_name=parsed.style,
            duration=parsed.duration,
            fps=parsed.fps,
            width=parsed.width,
            height=parsed.height,
        )
        print(f"\n✨ Done: {output}")
    else:
        outputs = render_batch(
            count=parsed.batch,
            style_name=parsed.style,
            width=parsed.width,
            height=parsed.height,
        )
        print(f"\n✨ Batch complete: {len(outputs)} videos generated")


if __name__ == "__main__":
    main()
