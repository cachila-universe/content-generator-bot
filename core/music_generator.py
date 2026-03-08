"""
Ambient background music generator — royalty-free, zero copyright.

Generates warm lo-fi ambient pads using pure numpy synthesis.
No external files, APIs, or licenses needed — the code IS the composer.

Features:
  • Pentatonic chord progressions (always pleasant, no dissonance)
  • Layered sine waves with slight detuning for warmth
  • Gentle fade-ins/outs between chords for smooth transitions
  • 6 mood presets matched to niche categories
  • Generated once → cached to data/music/ for reuse
  • Exported as WAV (moviepy-compatible)
"""

import hashlib
import logging
import struct
import wave
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

SAMPLE_RATE = 44100
_PROJECT_ROOT = Path(__file__).parent.parent
_MUSIC_DIR = _PROJECT_ROOT / "data" / "music"

# ── Musical scales (Hz) ──────────────────────────────────────────────────
# Pentatonic scale notes across octaves — always sounds pleasant
_PENTATONIC = {
    "C3": 130.81, "D3": 146.83, "E3": 164.81, "G3": 196.00, "A3": 220.00,
    "C4": 261.63, "D4": 293.66, "E4": 329.63, "G4": 392.00, "A4": 440.00,
    "C5": 523.25, "D5": 587.33, "E5": 659.25, "G5": 783.99, "A5": 880.00,
}

# ── Mood presets (chord progressions as frequency groups) ─────────────────
MOODS = {
    "calm": {
        "name": "Calm Ambient",
        "tempo": 0.25,        # chords per second (very slow)
        "chords": [
            [130.81, 196.00, 329.63],   # C  - G  - E4
            [146.83, 220.00, 329.63],   # D  - A  - E4
            [164.81, 261.63, 392.00],   # E  - C4 - G4
            [130.81, 196.00, 261.63],   # C  - G  - C4
        ],
        "pad_harmonics": [1.0, 0.5, 0.25, 0.12],
        "detune_cents": 8,
    },
    "upbeat": {
        "name": "Upbeat Lo-Fi",
        "tempo": 0.4,
        "chords": [
            [196.00, 329.63, 523.25],   # G  - E4 - C5
            [220.00, 329.63, 523.25],   # A  - E4 - C5
            [261.63, 392.00, 659.25],   # C4 - G4 - E5
            [196.00, 293.66, 523.25],   # G  - D4 - C5
        ],
        "pad_harmonics": [1.0, 0.6, 0.2, 0.08],
        "detune_cents": 6,
    },
    "techy": {
        "name": "Tech Ambient",
        "tempo": 0.3,
        "chords": [
            [164.81, 261.63, 440.00],   # E  - C4 - A4
            [196.00, 293.66, 440.00],   # G  - D4 - A4
            [130.81, 261.63, 392.00],   # C  - C4 - G4
            [146.83, 220.00, 392.00],   # D  - A  - G4
        ],
        "pad_harmonics": [1.0, 0.4, 0.3, 0.15],
        "detune_cents": 10,
    },
    "warm": {
        "name": "Warm Pads",
        "tempo": 0.2,
        "chords": [
            [130.81, 164.81, 261.63],   # C  - E  - C4
            [146.83, 196.00, 293.66],   # D  - G  - D4
            [130.81, 196.00, 329.63],   # C  - G  - E4
            [164.81, 220.00, 261.63],   # E  - A  - C4
        ],
        "pad_harmonics": [1.0, 0.55, 0.3, 0.18],
        "detune_cents": 12,
    },
    "chill": {
        "name": "Chill Vibes",
        "tempo": 0.28,
        "chords": [
            [220.00, 329.63, 523.25],   # A  - E4 - C5
            [196.00, 293.66, 440.00],   # G  - D4 - A4
            [164.81, 261.63, 392.00],   # E  - C4 - G4
            [196.00, 329.63, 440.00],   # G  - E4 - A4
        ],
        "pad_harmonics": [1.0, 0.45, 0.22, 0.1],
        "detune_cents": 7,
    },
    "focus": {
        "name": "Focus Flow",
        "tempo": 0.22,
        "chords": [
            [130.81, 261.63, 392.00],   # C  - C4 - G4
            [146.83, 293.66, 440.00],   # D  - D4 - A4
            [164.81, 329.63, 523.25],   # E  - E4 - C5
            [130.81, 196.00, 329.63],   # C  - G  - E4
        ],
        "pad_harmonics": [1.0, 0.5, 0.28, 0.14],
        "detune_cents": 9,
    },
}

# ── Niche → mood mapping ─────────────────────────────────────────────────
NICHE_MOODS = {
    "ai_tools":           "techy",
    "personal_finance":   "focus",
    "health_biohacking":  "calm",
    "home_tech":          "techy",
    "travel":             "chill",
    "pet_care":           "warm",
    "fitness_wellness":   "upbeat",
    "remote_work":        "focus",
}


def _get_mood(niche_id: str, slug: str = "") -> dict:
    """Pick a mood based on niche, with slug-based variation for diversity."""
    # Primary mood from niche
    mood_name = NICHE_MOODS.get(niche_id, "calm")

    # Use slug hash to occasionally pick a different compatible mood
    # This prevents the same niche always getting the exact same music
    if slug:
        h = int(hashlib.md5(slug.encode()).hexdigest(), 16)
        # 30% chance of picking a different mood for variety
        if h % 10 < 3:
            all_moods = list(MOODS.keys())
            mood_name = all_moods[h % len(all_moods)]

    return MOODS[mood_name]


def _generate_pad_tone(freq: float, duration: float, harmonics: list,
                       detune_cents: int) -> np.ndarray:
    """
    Generate a warm pad tone at the given frequency.

    Layers multiple sine waves with slight detuning for a rich, warm sound.
    Each harmonic is added at decreasing amplitude.
    """
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    signal = np.zeros_like(t)

    # Detune factor (cents → ratio)
    detune_ratio = 2 ** (detune_cents / 1200.0)

    for i, amp in enumerate(harmonics):
        harmonic_freq = freq * (i + 1)
        # Main tone
        signal += amp * np.sin(2 * np.pi * harmonic_freq * t)
        # Detuned copy (slightly sharp) for warmth
        signal += amp * 0.5 * np.sin(2 * np.pi * harmonic_freq * detune_ratio * t)
        # Detuned copy (slightly flat) for width
        signal += amp * 0.5 * np.sin(2 * np.pi * harmonic_freq / detune_ratio * t)

    return signal


def _apply_envelope(signal: np.ndarray, attack: float = 0.8,
                    release: float = 0.8) -> np.ndarray:
    """Apply smooth attack/release envelope to avoid clicks."""
    n = len(signal)
    attack_samples = int(SAMPLE_RATE * attack)
    release_samples = int(SAMPLE_RATE * release)

    env = np.ones(n)
    if attack_samples > 0 and attack_samples < n:
        env[:attack_samples] = np.linspace(0, 1, attack_samples)
    if release_samples > 0 and release_samples < n:
        env[-release_samples:] = np.linspace(1, 0, release_samples)

    return signal * env


def _simple_lowpass(signal: np.ndarray, cutoff_hz: float = 2000.0) -> np.ndarray:
    """
    Simple first-order IIR lowpass filter using numpy only (no scipy).
    Softens the sound for a warm, ambient feel.
    """
    rc = 1.0 / (2.0 * np.pi * cutoff_hz)
    dt = 1.0 / SAMPLE_RATE
    alpha = dt / (rc + dt)

    output = np.zeros_like(signal)
    output[0] = alpha * signal[0]
    for i in range(1, len(signal)):
        output[i] = alpha * signal[i] + (1 - alpha) * output[i - 1]

    return output


def generate_ambient_track(
    duration_seconds: float,
    niche_id: str = "",
    slug: str = "",
    variant: int = 0,
) -> Path:
    """
    Generate an ambient background music WAV file.

    Uses pentatonic chord progressions with warm pad synthesis.
    Tracks are cached to data/music/ so they're only generated once.

    Args:
        duration_seconds: Target track length (will be exact)
        niche_id: Niche ID for mood selection
        slug: Article slug for deterministic variation
        variant: Extra variation seed (0=shorts, 1=landscape, 2=roundup)

    Returns:
        Path to the generated WAV file
    """
    mood = _get_mood(niche_id, slug)

    # Cache key includes slug so each article gets its own unique track
    cache_key = hashlib.md5(
        f"{mood['name']}_{int(duration_seconds)}_{variant}_{slug}".encode()
    ).hexdigest()[:12]
    cache_path = _MUSIC_DIR / f"ambient_{cache_key}.wav"

    if cache_path.exists():
        logger.debug("Using cached ambient track: %s", cache_path.name)
        return cache_path

    logger.info(
        "Generating ambient track: %s (%.0fs, mood=%s)",
        cache_path.name, duration_seconds, mood["name"],
    )

    # Use slug hash to create per-article musical variation
    slug_hash = int(hashlib.md5((slug or "default").encode()).hexdigest(), 16)

    chords = list(mood["chords"])  # copy so we can shuffle
    # Rotate chord progression start point based on slug
    rotation = slug_hash % len(chords)
    chords = chords[rotation:] + chords[:rotation]

    harmonics = mood["pad_harmonics"]
    # Subtle detune variation: ±3 cents per article
    base_detune = mood["detune_cents"]
    detune = base_detune + (slug_hash % 7) - 3  # range: -3 to +3

    # Subtle tempo variation: ±10% per article
    base_tempo = mood["tempo"]
    tempo_factor = 0.9 + (slug_hash % 21) / 100  # 0.90 to 1.10
    chord_duration = 1.0 / (base_tempo * tempo_factor)

    total_samples = int(SAMPLE_RATE * duration_seconds)
    track = np.zeros(total_samples, dtype=np.float64)

    # Layer chords in sequence, looping the progression
    t = 0.0
    chord_idx = 0
    while t < duration_seconds:
        chord = chords[chord_idx % len(chords)]
        seg_duration = min(chord_duration, duration_seconds - t)

        if seg_duration < 0.5:
            break

        # Generate pad for each note in the chord
        chord_signal = np.zeros(int(SAMPLE_RATE * seg_duration))
        for freq in chord:
            tone = _generate_pad_tone(freq, seg_duration, harmonics, detune)
            chord_signal += tone

        # Smooth envelope (long attack/release for pad feel)
        chord_signal = _apply_envelope(
            chord_signal,
            attack=min(1.5, seg_duration * 0.3),
            release=min(1.5, seg_duration * 0.3),
        )

        # Place into track
        start_sample = int(t * SAMPLE_RATE)
        end_sample = start_sample + len(chord_signal)
        if end_sample > total_samples:
            chord_signal = chord_signal[:total_samples - start_sample]
            end_sample = total_samples
        track[start_sample:end_sample] += chord_signal

        t += seg_duration
        chord_idx += 1

    # Normalize to prevent clipping
    peak = np.max(np.abs(track))
    if peak > 0:
        track = track / peak * 0.7

    # Lowpass filter for warm, soft sound
    track = _simple_lowpass(track, cutoff_hz=1800.0)

    # Final fade-in / fade-out for the whole track
    fade_samples = int(SAMPLE_RATE * 2.0)  # 2-second fade
    if fade_samples < len(track) // 2:
        track[:fade_samples] *= np.linspace(0, 1, fade_samples)
        track[-fade_samples:] *= np.linspace(1, 0, fade_samples)

    # Convert to 16-bit PCM
    track_int16 = (track * 32767).astype(np.int16)

    # Write WAV
    _MUSIC_DIR.mkdir(parents=True, exist_ok=True)
    with wave.open(str(cache_path), "w") as wf:
        wf.setnchannels(1)       # mono
        wf.setsampwidth(2)       # 16-bit
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(track_int16.tobytes())

    size_mb = cache_path.stat().st_size / 1048576
    logger.info("Ambient track saved: %s (%.1f MB)", cache_path.name, size_mb)
    return cache_path


def mix_music_into_video(video_clip, niche_id: str = "", slug: str = "",
                         variant: int = 0, music_volume: float = 0.08):
    """
    Layer ambient background music under an existing video clip.

    The music plays at low volume (default 8% of peak) so it doesn't
    compete with TTS narration — just fills silence and adds polish.

    Args:
        video_clip: moviepy VideoClip with existing audio (TTS narration)
        niche_id: For mood selection
        slug: For deterministic variation
        variant: 0=shorts, 1=landscape, 2=roundup
        music_volume: Volume multiplier for music (0.0-1.0). Default 0.08
                      keeps it very subtle under narration.

    Returns:
        New VideoClip with music mixed under the original audio
    """
    try:
        from moviepy import AudioFileClip, CompositeAudioClip
    except ImportError:
        logger.warning("moviepy not available — skipping background music")
        return video_clip

    try:
        duration = video_clip.duration
        if not duration or duration < 3:
            return video_clip

        # Generate ambient track matching video duration
        music_path = generate_ambient_track(
            duration_seconds=duration,
            niche_id=niche_id,
            slug=slug,
            variant=variant,
        )

        if not music_path.exists():
            logger.warning("Music track not found, skipping")
            return video_clip

        # Load music and set low volume
        music_clip = AudioFileClip(str(music_path))

        # Trim music to exact video duration
        if music_clip.duration > duration:
            music_clip = music_clip.subclipped(0, duration)

        music_clip = music_clip.with_volume_scaled(music_volume)

        # Mix: original audio (narration) + background music
        if video_clip.audio is not None:
            mixed_audio = CompositeAudioClip([video_clip.audio, music_clip])
        else:
            mixed_audio = music_clip

        return video_clip.with_audio(mixed_audio)

    except Exception as exc:
        logger.warning("Could not add background music: %s", exc)
        return video_clip
