from __future__ import annotations

from pathlib import Path

from narratron.models import CommandType


class STTService:
    def __init__(self, model_size: str = "tiny", use_mock: bool = True) -> None:
        self.model_size = model_size
        self.use_mock = use_mock
        self._model = None

    def _ensure_model(self) -> None:
        if self.use_mock or self._model is not None:
            return

        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise RuntimeError(
                "faster-whisper is not installed. Install requirements-ml.txt or set NARRATRON_USE_MOCK_SERVICES=true."
            ) from exc

        self._model = WhisperModel(self.model_size)

    def transcribe(self, audio_path: str) -> str:
        path = Path(audio_path)
        if not path.exists():
            raise FileNotFoundError(f"Audio not found: {audio_path}")

        if self.use_mock:
            return "start"

        self._ensure_model()
        assert self._model is not None

        segments, _ = self._model.transcribe(str(path))
        return " ".join(segment.text.strip() for segment in segments).strip()


class CommandParser:
    _rules: dict[CommandType, tuple[str, ...]] = {
        CommandType.BACK: ("go back", "back", "previous"),
        CommandType.STOP: ("stop", "pause", "halt"),
        CommandType.TURN: ("turn", "next", "forward"),
        CommandType.START: ("start", "resume", "begin", "go"),
    }

    def parse(self, transcript: str) -> CommandType:
        text = " ".join(transcript.lower().strip().split())

        for command, keywords in self._rules.items():
            if any(keyword in text for keyword in keywords):
                return command

        return CommandType.UNKNOWN
