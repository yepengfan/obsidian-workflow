#!/usr/bin/env python3
"""Step 1: Local Whisper transcription (mlx-whisper).

Reads enriched episode JSON from stdin (output of fetch.py), transcribes
each audio file that doesn't already have a .srt, writes an SRT subtitle
file alongside the .mp3, and emits enriched JSON to stdout.

Input:  stdin JSON  {"episodes": [...], "stats": {...}}
        Each episode must have an "audio_path" field.
Output: stdout JSON  same structure, episodes augmented with:
            transcript_segments: list of {"start": float, "end": float, "text": str}
            transcript_text:     full concatenated transcript string
            language:            detected language code (e.g. "en", "zh")
        Episodes that fail transcription keep their other fields intact;
        transcript_segments is set to null, transcript_text to null.

SRT files are written to the same directory as the .mp3, with the same
stem and .srt extension.

Usage (as part of pipeline):
    python fetch.py | python transcribe.py | python enrich.py
"""

import json
import sys
from pathlib import Path

# ── Whisper configuration ─────────────────────────────────────────────

MODEL_NAME = "mlx-community/whisper-large-v3"
WORD_TIMESTAMPS = True


# ── SRT helpers ───────────────────────────────────────────────────────

def seconds_to_srt_time(seconds: float) -> str:
    """Convert float seconds to SRT timestamp format HH:MM:SS,mmm."""
    total_ms = int(round(seconds * 1000))
    ms = total_ms % 1000
    total_s = total_ms // 1000
    s = total_s % 60
    total_m = total_s // 60
    m = total_m % 60
    h = total_m // 60
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def segments_to_srt(segments: list[dict]) -> str:
    """Convert a list of segment dicts to SRT-format string."""
    lines: list[str] = []
    for i, seg in enumerate(segments, start=1):
        start = seconds_to_srt_time(seg["start"])
        end = seconds_to_srt_time(seg["end"])
        text = seg["text"].strip()
        lines.append(f"{i}\n{start} --> {end}\n{text}\n")
    return "\n".join(lines)


def write_srt(srt_path: Path, segments: list[dict]) -> None:
    """Write SRT file from segment list."""
    srt_content = segments_to_srt(segments)
    srt_path.write_text(srt_content, encoding="utf-8")


# ── Existing SRT loader ───────────────────────────────────────────────

def load_existing_srt(srt_path: Path) -> list[dict] | None:
    """Parse an existing .srt file into segment dicts, or return None on failure."""
    try:
        content = srt_path.read_text(encoding="utf-8")
    except OSError:
        return None

    segments: list[dict] = []
    blocks = content.strip().split("\n\n")
    for block in blocks:
        block_lines = block.strip().splitlines()
        if len(block_lines) < 3:
            continue
        # Line 0: sequence number (skip)
        # Line 1: "HH:MM:SS,mmm --> HH:MM:SS,mmm"
        # Line 2+: text
        timecode_line = block_lines[1]
        parts = timecode_line.split(" --> ")
        if len(parts) != 2:
            continue
        try:
            start = _srt_time_to_seconds(parts[0].strip())
            end = _srt_time_to_seconds(parts[1].strip())
        except ValueError:
            continue
        text = " ".join(line.strip() for line in block_lines[2:])
        segments.append({"start": start, "end": end, "text": text})

    return segments if segments else None


def _srt_time_to_seconds(ts: str) -> float:
    """Parse 'HH:MM:SS,mmm' to float seconds."""
    ts = ts.replace(",", ".")
    h, m, rest = ts.split(":")
    return int(h) * 3600 + int(m) * 60 + float(rest)


# ── Duration helper ───────────────────────────────────────────────────

def _duration_minutes(audio_path: str) -> str:
    """Best-effort estimate of audio duration in minutes for progress display."""
    p = Path(audio_path)
    try:
        size_mb = p.stat().st_size / (1024 * 1024)
        # Rough: ~1 MB/min for 128kbps MP3
        return f"~{int(size_mb)}"
    except OSError:
        return "?"


# ── Transcription ─────────────────────────────────────────────────────

def transcribe_episode(episode: dict) -> dict:
    """
    Transcribe audio for one episode. Mutates episode in place to add:
        transcript_segments, transcript_text, language
    Returns the (mutated) episode dict.
    """
    audio_path = Path(episode.get("audio_path", ""))
    slug = episode.get("slug", audio_path.stem)

    if not audio_path or not audio_path.exists():
        print(
            f"[transcribe] WARNING: audio file not found for '{slug}', skipping.",
            file=sys.stderr,
        )
        episode["transcript_segments"] = None
        episode["transcript_text"] = None
        episode["language"] = None
        return episode

    srt_path = audio_path.with_suffix(".srt")

    # ── Fast path: .srt already exists ───────────────────────────────
    if srt_path.exists():
        print(f"[transcribe] SRT exists, loading: {srt_path.name}", file=sys.stderr)
        existing_segs = load_existing_srt(srt_path)
        if existing_segs is not None:
            episode["transcript_segments"] = existing_segs
            episode["transcript_text"] = " ".join(s["text"] for s in existing_segs)
            episode["language"] = episode.get("language", "unknown")
            return episode
        else:
            print(
                f"[transcribe] WARNING: could not parse existing SRT {srt_path.name}, "
                "re-transcribing.",
                file=sys.stderr,
            )

    # ── Transcribe with mlx_whisper ───────────────────────────────────
    dur_min = _duration_minutes(str(audio_path))
    print(
        f"[transcribe] Transcribing: {audio_path.name} ({dur_min} min)...",
        file=sys.stderr,
    )

    try:
        import mlx_whisper  # type: ignore[import]
    except ImportError:
        print(
            "[transcribe] FATAL: mlx_whisper not installed. "
            "Run: pip install mlx-whisper",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        result = mlx_whisper.transcribe(
            str(audio_path),
            path_or_hf_repo=MODEL_NAME,
            word_timestamps=WORD_TIMESTAMPS,
        )
    except Exception as exc:
        print(
            f"[transcribe] ERROR transcribing {audio_path.name}: {exc}",
            file=sys.stderr,
        )
        episode["transcript_segments"] = None
        episode["transcript_text"] = None
        episode["language"] = None
        return episode

    # ── Extract segments ──────────────────────────────────────────────
    raw_segments = result.get("segments", [])
    segments: list[dict] = []
    for seg in raw_segments:
        text = seg.get("text", "").strip()
        if not text:
            continue
        segments.append({
            "start": float(seg.get("start", 0.0)),
            "end": float(seg.get("end", 0.0)),
            "text": text,
        })

    language = result.get("language", "unknown")

    # ── Write SRT file ────────────────────────────────────────────────
    try:
        write_srt(srt_path, segments)
        print(f"[transcribe] SRT written: {srt_path.name}", file=sys.stderr)
    except OSError as exc:
        print(
            f"[transcribe] WARNING: could not write SRT {srt_path.name}: {exc}",
            file=sys.stderr,
        )

    episode["transcript_segments"] = segments
    episode["transcript_text"] = " ".join(s["text"] for s in segments)
    episode["language"] = language
    return episode


# ── Main ──────────────────────────────────────────────────────────────

def main() -> None:
    raw = json.load(sys.stdin)
    episodes: list[dict] = raw.get("episodes", [])
    stats: dict = raw.get("stats", {})

    audio_episodes = [ep for ep in episodes if ep.get("audio_path")]
    no_audio = len(episodes) - len(audio_episodes)

    if not audio_episodes:
        print("[transcribe] No episodes with audio paths; passing through.", file=sys.stderr)
    else:
        print(
            f"[transcribe] Processing {len(audio_episodes)} episodes"
            + (f" ({no_audio} without audio skipped)" if no_audio else "")
            + "...",
            file=sys.stderr,
        )

    enriched_episodes: list[dict] = []

    for ep in episodes:
        if ep.get("audio_path"):
            ep = transcribe_episode(ep)
        else:
            ep.setdefault("transcript_segments", None)
            ep.setdefault("transcript_text", None)
            ep.setdefault("language", None)
        enriched_episodes.append(ep)

    successful = sum(
        1 for ep in enriched_episodes if ep.get("transcript_segments") is not None
    )
    print(
        f"[transcribe] Done: {successful}/{len(audio_episodes)} transcribed successfully.",
        file=sys.stderr,
    )

    result = {"episodes": enriched_episodes, "stats": stats}
    json.dump(result, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
