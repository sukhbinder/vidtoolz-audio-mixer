"""
Audio mixing functionality for vidtoolz amixer plugin.

Mixes a video file with a music track, allowing fine-grained control
over original video audio volume at specific time segments.
"""

import re

from moviepy import (
    AudioFileClip,
    CompositeAudioClip,
    VideoFileClip,
    afx,
    vfx,
)


def parse_segments(segments_str):
    """
    Parse segments string into a list of (start, end, volume) tuples.

    Format: "10-25:1.0;40-60:0.3"
    Returns: [(10, 25, 1.0), (40, 60, 0.3)]
    """
    if not segments_str:
        return []

    segments = []
    for segment in segments_str.split(";"):
        segment = segment.strip()
        if not segment:
            continue
        # Match pattern: start-end:volume
        match = re.match(r"(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?):(\d+(?:\.\d+)?)", segment)
        if match:
            start = float(match.group(1))
            end = float(match.group(2))
            volume = float(match.group(3))
            segments.append((start, end, volume))

    return segments


def apply_volume_envelope(
    audio_clip, segments, default_volume, fade_duration, total_duration
):
    """
    Apply volume changes to audio clip based on segments.

    Creates a volume envelope where:
    - default_volume is used outside of segments
    - segment volume is used within segment time ranges
    - fades are applied at transitions

    Returns the processed audio clip.
    """
    if not segments:
        # No segments, just apply default volume
        return audio_clip.with_effects([afx.MultiplyVolume(default_volume)])

    # Sort segments by start time
    segments = sorted(segments, key=lambda x: x[0])

    # Build list of audio clips to composite
    audio_clips = []

    for start, end, volume in segments:
        # Extract the segment from the original audio
        segment_clip = audio_clip.subclipped(start, end)

        # Apply the segment volume
        segment_clip = segment_clip.with_effects([afx.MultiplyVolume(volume)])

        # Apply fade in/out at segment boundaries if fade_duration > 0
        if fade_duration > 0:
            # Limit fade duration to segment duration
            actual_fade = min(fade_duration, (end - start) / 2)
            if actual_fade > 0:
                segment_clip = segment_clip.with_effects([
                    afx.AudioFadeIn(actual_fade),
                    afx.AudioFadeOut(actual_fade),
                ])

        # Position the segment at the correct start time
        segment_clip = segment_clip.with_start(start)
        audio_clips.append(segment_clip)

    # Create default volume clips for the gaps between segments
    gap_clips = []
    prev_end = 0.0

    for start, end, volume in segments:
        if start > prev_end:
            # There's a gap before this segment
            gap_duration = start - prev_end
            gap_clip = audio_clip.subclipped(prev_end, start)
            gap_clip = gap_clip.with_effects([afx.MultiplyVolume(default_volume)])
            gap_clip = gap_clip.with_start(prev_end)
            gap_clips.append(gap_clip)
        prev_end = end

    # Add final gap after last segment if needed
    if prev_end < total_duration:
        gap_duration = total_duration - prev_end
        if gap_duration > 0:
            gap_clip = audio_clip.subclipped(prev_end, total_duration)
            gap_clip = gap_clip.with_effects([afx.MultiplyVolume(default_volume)])
            gap_clip = gap_clip.with_start(prev_end)
            gap_clips.append(gap_clip)

    # Composite all clips together
    all_clips = audio_clips + gap_clips
    return CompositeAudioClip(all_clips)


def mix_video_and_music(
    video_path,
    music_path,
    segments=None,
    org_volume=0.1,
    fade_duration=2.0,
    music_volume=1.0,
):
    """
    Mix a video file with a music track.

    Args:
        video_path: Path to the input video file
        music_path: Path to the music/audio file
        segments: List of (start, end, volume) tuples for volume boosts
        org_volume: Default volume for original video audio (0.0-1.0)
        fade_duration: Duration of fade transitions in seconds
        music_volume: Volume multiplier for music track (0.0-1.0)

    Returns:
        VideoFileClip with mixed audio
    """
    # Load video and music
    video = VideoFileClip(video_path)
    music = AudioFileClip(music_path)

    video_duration = video.duration

    # Loop music to match video duration if needed
    if music.duration < video_duration:
        music = music.with_effects([afx.AudioLoop(duration=video_duration)])

    # Trim music to video duration
    music = music.with_duration(video_duration)

    # Process original video audio
    if video.audio is not None:
        # Apply volume envelope to original audio
        original_audio = apply_volume_envelope(
            video.audio, segments, org_volume, fade_duration, video_duration
        )

        # Apply ducking to music during segments where original audio is boosted
        if segments:
            music = apply_music_ducking(
                music, segments, music_volume, org_volume, fade_duration, video_duration
            )
        else:
            # No segments, just apply music volume
            if music_volume != 1.0:
                music = music.with_effects([afx.MultiplyVolume(music_volume)])

        # Mix original audio with music
        final_audio = CompositeAudioClip([music, original_audio])
    else:
        # No original audio, just use music
        final_audio = music
        if music_volume != 1.0:
            final_audio = final_audio.with_effects([afx.MultiplyVolume(music_volume)])

    # Set final audio duration
    final_audio = final_audio.with_duration(video_duration)

    # Apply final fade out
    if fade_duration > 0:
        final_audio = final_audio.with_effects([afx.AudioFadeOut(fade_duration)])

    # Set video audio
    video = video.with_audio(final_audio)

    return video


def apply_music_ducking(
    music_clip, segments, music_volume, org_volume, fade_duration, total_duration
):
    """
    Apply ducking to music during segments where original audio is boosted.

    During segments, music is reduced to allow original audio to dominate.
    Outside segments, music plays at the specified music_volume.
    """
    # Sort segments by start time
    segments = sorted(segments, key=lambda x: x[0])

    # Build list of audio clips to composite
    audio_clips = []

    # Calculate ducked volume - reduce music significantly during segments
    # The ducked volume should be low enough that original audio dominates
    ducked_volume = music_volume * 0.1  # Reduce to 10% during segments

    for start, end, volume in segments:
        # Extract the segment from the music
        segment_clip = music_clip.subclipped(start, end)

        # Apply ducked volume during segment
        segment_clip = segment_clip.with_effects([afx.MultiplyVolume(ducked_volume)])

        # Apply fade in/out at segment boundaries
        if fade_duration > 0:
            actual_fade = min(fade_duration, (end - start) / 2)
            if actual_fade > 0:
                segment_clip = segment_clip.with_effects([
                    afx.AudioFadeIn(actual_fade),
                    afx.AudioFadeOut(actual_fade),
                ])

        # Position the segment at the correct start time
        segment_clip = segment_clip.with_start(start)
        audio_clips.append(segment_clip)

    # Create normal volume clips for the gaps between segments
    gap_clips = []
    prev_end = 0.0

    for start, end, volume in segments:
        if start > prev_end:
            # There's a gap before this segment - music at normal volume
            gap_clip = music_clip.subclipped(prev_end, start)
            gap_clip = gap_clip.with_effects([afx.MultiplyVolume(music_volume)])
            gap_clip = gap_clip.with_start(prev_end)
            gap_clips.append(gap_clip)
        prev_end = end

    # Add final gap after last segment if needed
    if prev_end < total_duration:
        gap_duration = total_duration - prev_end
        if gap_duration > 0:
            gap_clip = music_clip.subclipped(prev_end, total_duration)
            gap_clip = gap_clip.with_effects([afx.MultiplyVolume(music_volume)])
            gap_clip = gap_clip.with_start(prev_end)
            gap_clips.append(gap_clip)

    # Composite all clips together
    all_clips = audio_clips + gap_clips
    return CompositeAudioClip(all_clips)


def write_clip(video_clip, output_path):
    """
    Write the video clip to a file.

    Args:
        video_clip: VideoFileClip to write
        output_path: Path to output file
    """
    video_clip.write_videofile(
        output_path,
        codec="libx264",
        temp_audiofile="temp_audio.m4a",
        remove_temp=True,
        audio_codec="aac",
    )
    video_clip.close()
