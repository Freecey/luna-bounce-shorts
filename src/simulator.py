"""
Scene simulator — orchestrates physics, rendering, audio.
The main loop that ties everything together.
"""

import os
import random
import math
import uuid
from dataclasses import dataclass
from PIL import Image

from ball import Ball, create_ball
from renderer import Renderer
from audio import BounceAudioTrack
from arena import Arena, ArenaMechanic, create_arena


# 9:16 vertical format for Shorts
SHORT_WIDTH = 720
SHORT_HEIGHT = 1280
FPS = 30
DURATION_SECONDS = 15


@dataclass
class SceneConfig:
    """Configuration for a scene render."""
    seed: int
    style: dict
    width: int = SHORT_WIDTH
    height: int = SHORT_HEIGHT
    fps: int = FPS
    duration: int = DURATION_SECONDS
    output_dir: str = "./exports"
    output_name: str = None
    # Arena mechanic: "none", "shrinking", "moving_walls", "rotating"
    arena_mechanic: str = "none"
    # Whether to spawn obstacles inside the arena
    obstacle_count: int = 0
    # Number of final frames that fade to black (loop-friendly ending)
    fade_out_frames: int = 45

    def __post_init__(self):
        if self.output_name is None:
            self.output_name = f"luna_bounce_{self.seed}"

    @property
    def mechanic_enum(self) -> ArenaMechanic:
        try:
            return ArenaMechanic(self.arena_mechanic)
        except ValueError:
            return ArenaMechanic.NONE


class Simulator:
    """
    Main simulator class.
    Runs the physics, renders frames, builds audio track.
    """

    def __init__(self, config: SceneConfig):
        self.config = config
        self.rng = random.Random(config.seed)

        # Initialize arena
        style_with_obstacles = dict(config.style, obstacle_count=config.obstacle_count)
        self.arena = create_arena(
            width=config.width,
            height=config.height,
            mechanic=config.mechanic_enum,
            seed=config.seed,
            style=style_with_obstacles,
        )

        # Initialize ball
        self.ball = create_ball(config.seed, config.width, config.height, config.style)
        self.renderer = Renderer(config.width, config.height, config.style)
        self.audio = BounceAudioTrack()

        self.frames: list[Image.Image] = []
        self.total_frames = config.fps * config.duration
        self.frame_time_ms = 1000 / config.fps

        self.current_frame = 0

    def run(self) -> str:
        """Run the simulation and return path to output video."""
        print(f"  🎬 Simulating {self.total_frames} frames @ {self.config.fps}fps...")
        print(f"  🌌 Style: {self.config.style.get('name', 'unknown')}")
        print(f"  🎲 Seed: {self.config.seed}")

        for frame_idx in range(self.total_frames):
            # Advance arena (moves obstacles, updates mechanic state)
            self.arena.advance()

            # Physics step
            collisions = self.ball.update(self.config.width, self.config.height,
                                          arena=self.arena)

            # Handle collisions
            flash = 0.0
            for col in collisions:
                self.audio.add_bounce(
                    time_ms=int(self.frame_time_ms * frame_idx),
                    speed=col.speed
                )
                # Spawn particles
                self.renderer.particles.spawn(
                    col.position.x, col.position.y,
                    col.speed, col.surface_normal,
                    col.velocity_before and (200, 200, 255) or (255, 200, 200),
                    count=self.config.style.get("particle_count", 8)
                )
                flash = min(1.0, col.speed / 15)

            # Render frame
            img = self.renderer.render_frame(self.ball, flash_intensity=flash,
                                            arena=self.arena)
            self.frames.append(img)

            if frame_idx % (self.total_frames // 4) == 0:
                pct = (frame_idx / self.total_frames) * 100
                print(f"    {pct:.0f}%")

        print("    100%")
        return self._export_video()

    def _export_video(self) -> str:
        """Export frames + audio to MP4 using FFmpeg."""
        import subprocess

        output_dir = self.config.output_dir
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{self.config.output_name}.mp4")

        # Save frames to temp dir
        frames_dir = os.path.join(output_dir, f"_frames_{self.config.seed}")
        os.makedirs(frames_dir, exist_ok=True)

        print(f"  📁 Saving {len(self.frames)} frames...")
        # Apply fade-out to final frames (loop-friendly ending)
        fade_frames = self.config.fade_out_frames
        total = len(self.frames)
        for i, frame in enumerate(self.frames):
            # Compute fade alpha for last fade_frames
            fade_idx = i - (total - fade_frames)
            if fade_idx >= 0:
                # fade_idx goes 0 → fade_frames-1 (0 = start of fade, last = full black)
                alpha = fade_idx / fade_frames  # 0.0 → 1.0
                # Blend with pure black
                black = Image.new("RGB", frame.size, (0, 0, 0))
                frame = Image.blend(frame, black, alpha)
            frame.save(os.path.join(frames_dir, f"frame_{i:05d}.png"))

        # Generate audio
        audio_path = os.path.join(frames_dir, "audio.wav")
        print(f"  🎵 Generating audio...")
        track = self.audio.generate_track(
            duration_ms=self.total_frames * self.frame_time_ms
        )
        from audio import write_wav
        write_wav(audio_path, track)
        print(f"  ✓ Audio track saved")

        # FFmpeg assembly
        print(f"  🎞️  Assembling video with FFmpeg...")
        frame_pattern = os.path.join(frames_dir, "frame_%05d.png")

        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(self.config.fps),
            "-i", frame_pattern,
            "-i", audio_path,
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-vf", f"scale={self.config.width}:{self.config.height}:force_original_aspect_ratio=decrease,pad={self.config.width}:{self.config.height}:(ow-iw)/2:(oh-ih)/2",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            output_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  ⚠️  FFmpeg error: {result.stderr[:500]}")
            # Try without audio as fallback
            cmd_audio = [x for x in cmd if x != "-i" and x != audio_path]
            cmd_audio.remove("-c:a")
            cmd_audio.remove("aac")
            cmd_audio.remove("-b:a")
            cmd_audio.remove("192k")
            cmd_audio.remove("-shortest")
            subprocess.run(cmd_audio, capture_output=True, text=True)

        # Cleanup frames
        import shutil
        shutil.rmtree(frames_dir)

        print(f"  ✅ Output: {output_path}")
        return output_path


def render_scene(seed: int = None, style_name: str = "cosmic",
                 width: int = SHORT_WIDTH, height: int = SHORT_HEIGHT,
                 duration: int = DURATION_SECONDS, fps: int = FPS,
                 arena_mechanic: str = "none",
                 obstacle_count: int = 0) -> str:
    """
    Main entry point: render a single scene.
    Returns path to the output MP4.
    """
    from styles.luna import get_style
    from styles.luna_dot import get_dot_style
    from styles.microcosm import get_micro_style

    if seed is None:
        seed = random.randint(0, 999999)

    style = {}

    # Resolve style: microcosm > dot > ball
    if style_name.startswith("micro_"):
        style = get_micro_style(style_name.replace("micro_", ""))
    elif style_name.startswith("dot_"):
        style = get_dot_style(style_name.replace("dot_", ""))
    else:
        style = get_dot_style(style_name)
        if style is None or style == {}:
            style = get_style(style_name)

    if style is None or style == {}:
        print(f"  ⚠️  Unknown style '{style_name}', using cosmic")
        style = get_style("cosmic")

    # Ball radius adapts to dot mode
    if style.get("dot_mode", False):
        style["ball_radius_min"] = style.get("ball_radius_min", 8)
        style["ball_radius_max"] = style.get("ball_radius_max", 15)

    # Obstacle count from style, overridable via parameter
    style_obstacle_count = style.get("obstacle_count", obstacle_count)
    # Arena mechanic from style
    if arena_mechanic == "none":
        arena_mechanic = style.get("arena_mechanic", "none")

    config = SceneConfig(
        seed=seed,
        style=style,
        width=width,
        height=height,
        fps=fps,
        duration=duration,
        arena_mechanic=arena_mechanic,
        obstacle_count=style_obstacle_count,
    )

    sim = Simulator(config)
    return sim.run()


def render_batch(count: int = 3, style_name: str = "cosmic",
                 width: int = SHORT_WIDTH, height: int = SHORT_HEIGHT,
                 arena_mechanic: str = "none",
                 obstacle_count: int = 0) -> list[str]:
    """Render multiple variants."""
    from styles.luna import get_style
    from styles.luna_dot import get_dot_style
    from styles.microcosm import get_micro_style

    style = {}

    # Resolve style: microcosm > dot > ball
    if style_name.startswith("micro_"):
        style = get_micro_style(style_name.replace("micro_", ""))
    elif style_name.startswith("dot_"):
        style = get_dot_style(style_name.replace("dot_", ""))
    else:
        style = get_dot_style(style_name)
        if style is None or style == {}:
            style = get_style(style_name)

    if style is None or style == {}:
        style = get_style("cosmic")

    if style.get("dot_mode", False):
        style["ball_radius_min"] = style.get("ball_radius_min", 8)
        style["ball_radius_max"] = style.get("ball_radius_max", 15)

    outputs = []

    print(f"\n🎬 BATCH RENDER: {count} videos in {style.get('name', style_name)}\n")

    for i in range(count):
        print(f"\n--- Video {i+1}/{count} ---")
        seed = random.randint(0, 999999)
        config = SceneConfig(
            seed=seed,
            style=style,
            width=width,
            height=height,
            arena_mechanic=arena_mechanic,
            obstacle_count=obstacle_count,
        )
        sim = Simulator(config)
        out = sim.run()
        outputs.append(out)

    return outputs
