from __future__ import annotations

import argparse
import json

import uvicorn

from narratron.config import settings
from narratron.pipeline import NarraTronPipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="narra-tron", description="Narra-Tron software stack")
    subparsers = parser.add_subparsers(dest="command", required=True)

    serve = subparsers.add_parser("serve", help="Run FastAPI server")
    serve.add_argument("--host", default=settings.host)
    serve.add_argument("--port", type=int, default=settings.port)

    process_page = subparsers.add_parser("process-page", help="OCR + TTS for one page image")
    process_page.add_argument("image_path")
    process_page.add_argument("output_audio_path")

    parse_transcript = subparsers.add_parser("parse-transcript", help="Parse spoken command text")
    parse_transcript.add_argument("transcript")

    transcribe_cmd = subparsers.add_parser("transcribe-command", help="STT audio then command parse")
    transcribe_cmd.add_argument("audio_path")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "serve":
        uvicorn.run("narratron.api:app", host=args.host, port=args.port, reload=False)
        return

    pipeline = NarraTronPipeline.build_default()

    if args.command == "process-page":
        result = pipeline.process_page(args.image_path, args.output_audio_path)
        print(json.dumps(result.model_dump(), indent=2))
        return

    if args.command == "parse-transcript":
        result = pipeline.parse_transcript(args.transcript)
        print(json.dumps(result.model_dump(), indent=2))
        return

    if args.command == "transcribe-command":
        result = pipeline.transcribe_command(args.audio_path)
        print(json.dumps(result.model_dump(), indent=2))
        return

    parser.error("Unknown command")


if __name__ == "__main__":
    main()
