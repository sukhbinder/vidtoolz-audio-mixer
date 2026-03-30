import os

import vidtoolz

from vidtoolz_audio_mixer.amixer import (
    mix_video_and_music,
    parse_segments,
    write_clip,
)


def create_parser(subparser):
    parser = subparser.add_parser(
        "amixer", description="Mix video with music audio track"
    )
    parser.add_argument("video", type=str, help="Input video file")
    parser.add_argument("music", type=str, help="Music/audio file to mix with video")
    parser.add_argument(
        "-s",
        "--segments",
        type=str,
        default=None,
        help="Time segments for original audio boost. Format: '10-25:1.0;40-60:0.3'",
    )
    parser.add_argument(
        "-ov",
        "--org-volume",
        type=float,
        default=0.1,
        help="Default volume for original video audio (0.0-1.0). Default: %(default)s",
    )
    parser.add_argument(
        "-f",
        "--fade",
        type=float,
        default=2.0,
        help="Fade duration in seconds for transitions. Default: %(default)s",
    )
    parser.add_argument(
        "-mv",
        "--music-volume",
        type=float,
        default=1.0,
        help="Volume multiplier for music track (0.0-1.0). Default: %(default)s",
    )
    parser.add_argument(
        "-o", "--output", type=str, default=None, help="Output video file path"
    )
    return parser


def determine_output_path(input_file, output_file):
    """Determine the output file path."""
    input_dir, input_filename = os.path.split(input_file)
    name, _ = os.path.splitext(input_filename)

    if output_file:
        output_dir, output_filename = os.path.split(output_file)
        if not output_dir:
            return os.path.join(input_dir, output_filename)
        return output_file
    else:
        return os.path.join(input_dir, f"{name}_mixed.mp4")


class ViztoolzPlugin:
    """Music mixer for a video"""

    __name__ = "amixer"

    @vidtoolz.hookimpl
    def register_commands(self, subparser):
        self.parser = create_parser(subparser)
        self.parser.set_defaults(func=self.run)

    def run(self, args):
        output = determine_output_path(args.video, args.output)

        # Parse segments if provided
        segments = parse_segments(args.segments) if args.segments else []

        # Mix video and music
        clip = mix_video_and_music(
            args.video,
            args.music,
            segments=segments,
            org_volume=args.org_volume,
            fade_duration=args.fade,
            music_volume=args.music_volume,
        )

        # Write output
        write_clip(clip, output)
        print(f"{output} written.")

    def hello(self, args):
        print("Hello! This is the vidtoolz amixer plugin.")


amixer_plugin = ViztoolzPlugin()
