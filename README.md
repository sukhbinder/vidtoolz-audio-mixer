# vidtoolz-audio-mixer

[![PyPI](https://img.shields.io/pypi/v/vidtoolz-audio-mixer.svg)](https://pypi.org/project/vidtoolz-audio-mixer/)
[![Changelog](https://img.shields.io/github/v/release/sukhbinder/vidtoolz-audio-mixer?include_prereleases&label=changelog)](https://github.com/sukhbinder/vidtoolz-audio-mixer/releases)
[![Tests](https://github.com/sukhbinder/vidtoolz-audio-mixer/workflows/Test/badge.svg)](https://github.com/sukhbinder/vidtoolz-audio-mixer/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/sukhbinder/vidtoolz-audio-mixer/blob/main/LICENSE)

Music mixer for a video

## Installation

First install [vidtoolz](https://github.com/sukhbinder/vidtoolz).

```bash
pip install vidtoolz
```

Then install this plugin in the same environment as your vidtoolz application.

```bash
vidtoolz install vidtoolz-audio-mixer
```
## Usage

type ``vid amixer --help`` to get help



## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:
```bash
cd vidtoolz-audio-mixer
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
pip install -e '.[test]'
```
To run the tests:
```bash
python -m pytest
```
