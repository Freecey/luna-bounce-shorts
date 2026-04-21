"""
Audio generation for bounce sounds.
Pure Python wave module, no external audio deps needed.
Generates soft ASMR-style bounce sounds.
"""

import math
import struct
import wave
import random
import os
from dataclasses import dataclass


@dataclass
class BounceSound:
    """A generated bounce sound."""
    samples: list
    sample_rate: int
    duration_ms: int


def generate_bounce_wave(frequency: float, duration_ms: int, sample_rate: int = 44100,
                          volume: float = 0.6, decay: float = 0.15) -> list:
    """
    Generate a sine wave with exponential decay for a soft bounce sound.
    This is basically a decaying sine wave — very ASMR.
    """
    n_samples = int(sample_rate * duration_ms / 1000)
    samples = []

    for i in range(n_samples):
        t = i / sample_rate
        # Exponential decay envelope
        envelope = math.exp(-t * decay)
        # Sine wave
        wave_val = math.sin(2 * math.pi * frequency * t)
        # Add slight harmonics for richer sound
        wave_val += 0.3 * math.sin(2 * math.pi * frequency * 2 * t)
        wave_val += 0.1 * math.sin(2 * math.pi * frequency * 3 * t)
        # Apply envelope
        sample = wave_val * envelope * volume
        samples.append(sample)

    return samples


def generate_soft_bounce(duration_ms: int = 80, sample_rate: int = 44100) -> list:
    """Soft gentle bounce — for slow impacts."""
    freq = random.uniform(280, 380)
    return generate_bounce_wave(freq, duration_ms, sample_rate, volume=0.4, decay=0.18)


def generate_medium_bounce(duration_ms: int = 60, sample_rate: int = 44100) -> list:
    """Medium impact bounce."""
    freq = random.uniform(400, 520)
    return generate_bounce_wave(freq, duration_ms, sample_rate, volume=0.5, decay=0.22)


def generate_strong_bounce(duration_ms: int = 50, sample_rate: int = 44100) -> list:
    """Harder impact — for fast collisions."""
    freq = random.uniform(550, 700)
    return generate_bounce_wave(freq, duration_ms, sample_rate, volume=0.6, decay=0.28)


def generate_click(duration_ms: int = 20, sample_rate: int = 44100) -> list:
    """Very short click sound for tiny taps."""
    freq = random.uniform(800, 1200)
    return generate_bounce_wave(freq, duration_ms, sample_rate, volume=0.3, decay=0.5)


def mix_samples(sample_lists: list, volumes: list = None) -> list:
    """Mix multiple samples together."""
    if volumes is None:
        volumes = [1.0] * len(sample_lists)

    max_len = max(len(s) for s in sample_lists)
    mixed = [0.0] * max_len

    for samples, vol in zip(sample_lists, volumes):
        for i, s in enumerate(samples):
            mixed[i] += s * vol

    # Normalize to prevent clipping
    max_val = max(abs(s) for s in mixed) if mixed else 1.0
    if max_val > 1.0:
        mixed = [s / max_val for s in mixed]

    return mixed


def samples_to_bytes(samples: list, sample_rate: int = 44100) -> bytes:
    """Convert float samples to 16-bit PCM bytes."""
    fmt = "<h"  # little-endian signed short
    byte_data = b""
    for s in samples:
        clamped = max(-1.0, min(1.0, s))
        packed = struct.pack(fmt, int(clamped * 32767))
        byte_data += packed
    return byte_data


def write_wav(filepath: str, samples: list, sample_rate: int = 44100):
    """Write samples to a WAV file."""
    with wave.open(filepath, 'w') as wav:
        wav.setnchannels(1)  # mono
        wav.setsampwidth(2)  # 16-bit
        wav.setframerate(sample_rate)
        byte_data = samples_to_bytes(samples, sample_rate)
        wav.writeframes(byte_data)


class BounceAudioTrack:
    """
    Builds a complete audio track from collision events.
    Combines bounce sounds with ambient noise.
    """

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.track: list[float] = []
        self.collision_times: list[tuple] = []  # (time_ms, strength, type)

    def add_bounce(self, time_ms: int, speed: float):
        """Schedule a bounce sound at a given time (ms)."""
        # Classify impact strength
        if speed < 3:
            btype = "soft"
        elif speed < 7:
            btype = "medium"
        else:
            btype = "strong"

        self.collision_times.append((time_ms, speed, btype))

    def generate_track(self, duration_ms: int, ambient: bool = True) -> list:
        """Generate the complete audio track."""
        total_samples = int(self.sample_rate * duration_ms / 1000)
        self.track = [0.0] * total_samples

        # Add bounce sounds
        for time_ms, speed, btype in self.collision_times:
            if btype == "soft":
                samples = generate_soft_bounce(sample_rate=self.sample_rate)
            elif btype == "medium":
                samples = generate_medium_bounce(sample_rate=self.sample_rate)
            else:
                samples = generate_strong_bounce(sample_rate=self.sample_rate)

            # Pitch variation
            if random.random() > 0.7:
                pitch_shift = random.uniform(0.9, 1.1)
                # Simple pitch shift by resampling would go here
                # For now we just use the original

            # Place in track
            start_sample = int(self.sample_rate * time_ms / 1000)
            for i, s in enumerate(samples):
                if start_sample + i < total_samples:
                    self.track[start_sample + i] += s * (speed / 10)

        # Normalize
        max_val = max(abs(s) for s in self.track) if self.track else 1.0
        if max_val > 0.95:
            self.track = [s / max_val * 0.95 for s in self.track]

        return self.track

    def save(self, filepath: str):
        """Write track to WAV file."""
        if not self.track:
            return
        write_wav(filepath, self.track, self.sample_rate)


def generate_ambient_loop(duration_ms: int = 3000, sample_rate: int = 44100) -> list:
    """Generate a soft ambient noise loop (like white noise but softer)."""
    n = int(sample_rate * duration_ms / 1000)
    noise = []

    # Pink-ish noise (filtered white noise)
    prev = 0.0
    for i in range(n):
        white = random.uniform(-1, 1)
        # Simple low-pass filter
        val = prev * 0.9 + white * 0.1
        prev = val
        noise.append(val * 0.03)  # very quiet

    return noise


def create_test_sounds(sounds_dir: str):
    """Generate test sound files."""
    os.makedirs(sounds_dir, exist_ok=True)

    for name, gen_fn in [
        ("bounce_soft.wav", lambda: generate_soft_bounce()),
        ("bounce_medium.wav", lambda: generate_medium_bounce()),
        ("bounce_strong.wav", lambda: generate_strong_bounce()),
        ("click.wav", lambda: generate_click()),
    ]:
        samples = gen_fn()
        write_wav(os.path.join(sounds_dir, name), samples)
        print(f"  ✓ {name}")
