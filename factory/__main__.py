"""Run one example or a checkpointed batch of independent inputs."""
import argparse
import json
from pathlib import Path

from factory.core import Checkpoints, encode
from factory.pipelines import educational_data, social_dry_run, subtitle_and_dub


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", default=".factory/jobs.sqlite")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("education", "social"):
        command = commands.add_parser(name)
        command.add_argument("inputs", nargs="+", type=Path)
    speech = commands.add_parser("speech")
    speech.add_argument("audio", type=Path)
    speech.add_argument("destination", type=Path)
    args = parser.parse_args()
    if args.command == "speech":
        subtitle_and_dub(args.audio, args.destination)
        return 0
    state = Checkpoints(args.state)
    failed = False
    for path in args.inputs:
        try:
            if args.command == "education":
                result, cached = educational_data(path, state)
            else:
                result, cached = social_dry_run(json.loads(path.read_text(encoding="utf-8")), state)
            print(encode({"input": str(path), "cached": cached, "result": result}))
        except (ValueError, OSError, RuntimeError) as exc:
            failed = True
            print(encode({"input": str(path), "error": str(exc)}))
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
