# vidtoolz-audio-mixer

[![PyPI](https://img.shields.io/pypi/v/vidtoolz-audio-mixer.svg)](https://pypi.org/project/vidtoolz-audio-mixer/)
[![Changelog](https://img.shields.io/github/v/release/sukhbinder/vidtoolz-audio-mixer?include_prereleases&label=changelog)](https://github.com/sukhbinder/vidtoolz-audio-mixer/releases)
[![Tests](https://github.com/sukhbinder/vidtoolz-audio-mixer/workflows/Test/badge.svg)](https://github.com/sukhbinder/vidtoolz-audio-mixer/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/sukhbinder/vidtoolz-audio-mixer/blob/main/LICENSE)

Music mixer for videos. Mix video audio with music tracks and apply fade transitions.

## Installation

1. Install [vidtoolz](https://github.com/sukhbinder/vidtoolz)

```bash
pip install vidtoolz
```

2. Install this plugin in the same environment as your vidtoolz application:

```bash
vidtoolz install vidtoolz-audio-mixer
```

## Usage

Type `vid amixer --help` to see usage information.

Basic usage:

```bash
vid amixer --help
```

Mix video and music with fade transitions:

```bash
vid amixer input.mp4 music.mp3
```

## Options

- `video` - Input video file (required)
- `music` - Music/audio file to mix with video (required)
- `-s, --segments` - Time segments for original audio boost. Format: `10-25:1.0;40-60:0.3`
- `-ov, --org-volume` - Default volume for original video audio (0.0-1.0). Default: 0.1
- `-f, --fade` - Fade duration in seconds for transitions. Default: 2.0
- `-mv, --music-volume` - Volume multiplier for music track (0.0-1.0). Default: 1.0
- `-o, --output` - Output video file path

## Examples

Basic mix:

```bash
vid amixer input.mp4 music.mp3 -o output.mp4
```

Mix with fade and custom volumes:

```bash
vid amixer input.mp4 music.mp3 -f 3.0 -ov 0.5 -mv 1.2 -o output.mp4
```

Apply fade to specific time segments (boost original audio during certain ranges):

```bash
vid amixer input.mp4 music.mp3 -s "0-10:1.0;20-30:0.5;40-50:0.8" -o output.mp4
```

## Development

To set up this plugin locally:

```bash
cd vidtoolz-audio-mixer
python -m venv venv
source venv/bin/activate
```

Install dependencies and test dependencies:

```bash
pip install -e '.[test]'
```

Run the tests:

```bash
python -m pytest
```

## License

Apache-2.0
