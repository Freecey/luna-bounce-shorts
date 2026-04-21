# 🌙 Luna Bounce Shorts

ASMR satisfying vertical shorts generator — 100% procedural, no AI video models.

Generate hypnotic bouncing ball videos in Luna's visual style. Vertical 9:16 format, ready for YouTube Shorts / TikTok / Reels.

![Luna Cosmic Style](.github/preview-cosmic.gif)
![Luna Threshold Style](.github/preview-threshold.gif)

## Features

- **Procedural physics** — pure Python, no external physics engine
- **Luna visual styles** — Cosmic, Threshold, Aurora
- **ASMR audio** — generated bounce sounds synced to collisions
- **100% reproducible** — seed-based, same seed = same video
- **Batch generation** — produce many variants automatically
- **No AI** — no AI video models, no API calls

## Quick Start

```bash
# One video
python main.py --style cosmic --seed 42

# Batch of 5 variants
python main.py --batch 5 --style threshold

# Full HD vertical
python main.py --width 1080 --height 1920 --duration 15
```

## Styles

| Style | Description |
|-------|-------------|
| `cosmic` | Stardust gold ball through deep space purple |
| `threshold` | Warm white light on the edge between two worlds |
| `aurora` | Arctic teal, silence and ice |

## Requirements

- Python 3.10+
- Pillow
- FFmpeg (for video assembly)

```bash
pip install Pillow
# FFmpeg must be installed on system
```

## Architecture

```
src/
  ball.py       — Physics (velocity, gravity, bounce, collision)
  renderer.py   — PIL rendering (glow, trails, particles, vignette)
  audio.py      — Waveform audio generation (bounce sounds)
  simulator.py  — Main loop orchestrator + FFmpeg assembly
styles/
  luna.py       — Visual style presets
main.py         — CLI entry point
```

## License

Created by Luna for Luna Creative Archive.
