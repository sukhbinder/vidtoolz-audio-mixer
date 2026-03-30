import os
from argparse import ArgumentParser
from pathlib import Path

import pytest
from moviepy import VideoFileClip

import vidtoolz_audio_mixer as w
from vidtoolz_audio_mixer.amixer import (
    mix_video_and_music,
    parse_segments,
    write_clip,
)

HERE = Path(__file__).parent
TEST_OUTPUT_PATH = HERE / "output_test_video.mp4"
IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"


def test_parse_segments():
    # Test basic segment parsing
    result = parse_segments("10-25:1.0;40-60:0.3")
    assert result == [(10, 25, 1.0), (40, 60, 0.3)]

    # Test single segment
    result = parse_segments("5-10:0.5")
    assert result == [(5, 10, 0.5)]

    # Test empty string
    result = parse_segments("")
    assert result == []

    # Test None
    result = parse_segments(None)
    assert result == []

    # Test with decimal values
    result = parse_segments("1.5-2.5:0.75")
    assert result == [(1.5, 2.5, 0.75)]


def test_create_parser():
    subparser = ArgumentParser().add_subparsers()
    parser = w.create_parser(subparser)

    assert parser is not None

    result = parser.parse_args(
        [
            "video.mp4",
            "music.mp3",
            "--segments",
            "10-25:1.0;40-60:0.3",
            "--org-volume",
            "0.1",
            "--fade",
            "2",
            "-o",
            "output.mp4",
        ]
    )
    assert result.video == "video.mp4"
    assert result.music == "music.mp3"
    assert result.segments == "10-25:1.0;40-60:0.3"
    assert result.org_volume == 0.1
    assert result.fade == 2.0
    assert result.output == "output.mp4"


def test_create_parser_defaults():
    subparser = ArgumentParser().add_subparsers()
    parser = w.create_parser(subparser)

    result = parser.parse_args(["video.mp4", "music.mp3"])
    assert result.video == "video.mp4"
    assert result.music == "music.mp3"
    assert result.segments is None
    assert result.org_volume == 0.1
    assert result.fade == 2.0
    assert result.output is None
    assert result.music_volume == 1.0


def test_plugin_hello(capsys):
    w.amixer_plugin.hello(None)
    captured = capsys.readouterr()
    assert "Hello! This is the vidtoolz amixer plugin." in captured.out


def test_determine_output_path():
    # Test with explicit output
    result = w.determine_output_path("/path/to/video.mp4", "/path/to/output.mp4")
    assert result == "/path/to/output.mp4"

    # Test with just filename
    result = w.determine_output_path("/path/to/video.mp4", "output.mp4")
    assert result == "/path/to/output.mp4"

    # Test with no output (should use input dir + _mixed suffix)
    result = w.determine_output_path("/path/to/video.mp4", None)
    assert result == "/path/to/video_mixed.mp4"


@pytest.mark.skipif(IN_GITHUB_ACTIONS, reason="Test doesn't work in Github Actions.")
def test_realcase_amixer(tmpdir):
    """Test the full amixer workflow with real files."""
    outfile = Path(tmpdir) / "output.mp4"
    testdata = HERE / "test_data"
    video = testdata / "IMG_3262.MOV"
    audio = testdata / "MalgudiDays.mp3"

    subparser = ArgumentParser().add_subparsers()
    parser = w.create_parser(subparser)

    argv = [
        str(video),
        str(audio),
        "-o",
        str(outfile),
        "--segments",
        "1-2:1.0",
        "--org-volume",
        "0.1",
        "--fade",
        "0.5",
    ]
    args = parser.parse_args(argv)
    w.amixer_plugin.run(args)
    assert outfile.exists()


@pytest.fixture(scope="module")
def test_files():
    testdata = HERE / "test_data"
    TEST_VIDEO_PATH = testdata / "IMG_3262.MOV"
    TEST_AUDIO_PATH = testdata / "MalgudiDays.mp3"
    return str(TEST_VIDEO_PATH), str(TEST_AUDIO_PATH)


def cleanup_test_files():
    if TEST_OUTPUT_PATH.exists():
        TEST_OUTPUT_PATH.unlink()


@pytest.mark.skipif(IN_GITHUB_ACTIONS, reason="Test doesn't work in Github Actions.")
def test_mix_video_and_music(test_files):
    """Test mixing video with music."""
    TEST_VIDEO_PATH, TEST_AUDIO_PATH = test_files

    clip = mix_video_and_music(
        TEST_VIDEO_PATH,
        TEST_AUDIO_PATH,
        segments=[],
        org_volume=0.1,
        fade_duration=0.5,
    )
    write_clip(clip, TEST_OUTPUT_PATH)

    assert TEST_OUTPUT_PATH.exists()

    # Verify output has audio
    output_video = VideoFileClip(TEST_OUTPUT_PATH)
    assert output_video.audio is not None
    output_video.close()
    cleanup_test_files()


@pytest.mark.skipif(IN_GITHUB_ACTIONS, reason="Test doesn't work in Github Actions.")
def test_mix_video_and_music_with_segments(test_files):
    """Test mixing with volume boost segments."""
    TEST_VIDEO_PATH, TEST_AUDIO_PATH = test_files

    clip = mix_video_and_music(
        TEST_VIDEO_PATH,
        TEST_AUDIO_PATH,
        segments=[(1, 2, 1.0)],  # Boost original audio from 1-2 seconds
        org_volume=0.1,
        fade_duration=0.5,
    )
    write_clip(clip, TEST_OUTPUT_PATH)

    assert TEST_OUTPUT_PATH.exists()

    output_video = VideoFileClip(TEST_OUTPUT_PATH)
    assert output_video.audio is not None
    output_video.close()
    cleanup_test_files()


@pytest.mark.skipif(IN_GITHUB_ACTIONS, reason="Test doesn't work in Github Actions.")
def test_mix_video_and_music_with_music_volume(test_files):
    """Test mixing with custom music volume."""
    TEST_VIDEO_PATH, TEST_AUDIO_PATH = test_files

    clip = mix_video_and_music(
        TEST_VIDEO_PATH,
        TEST_AUDIO_PATH,
        segments=[],
        org_volume=0.1,
        fade_duration=0.5,
        music_volume=0.5,
    )
    write_clip(clip, TEST_OUTPUT_PATH)

    assert TEST_OUTPUT_PATH.exists()

    output_video = VideoFileClip(TEST_OUTPUT_PATH)
    assert output_video.audio is not None
    output_video.close()
    cleanup_test_files()


@pytest.mark.skipif(IN_GITHUB_ACTIONS, reason="Test doesn't work in Github Actions.")
def test_realcase_mixer(tmpdir):
    outfile = tmpdir / "test_mixer.mp4"
    testdata = Path(__file__).parent / "test_data"
    vidfile = testdata / "IMG_3262.MOV"
    audfile = testdata / "MalgudiDays.mp3"
    argv = [
        str(vidfile),
        str(audfile),
        "-s",
        "1-4:1.0;6-8:0.9;10-11:0.5",
        "-o",
        str(outfile),
    ]
    subparser = ArgumentParser().add_subparsers()
    parser = w.create_parser(subparser)
    args = parser.parse_args(argv)
    args.func = None
    w.amixer_plugin.run(args)
    assert outfile.exists()
