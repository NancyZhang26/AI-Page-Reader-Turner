from __future__ import annotations

from pathlib import Path


_SAMPLE_DOSTOYEVSKY_PASSAGE = (
    "I am a sick man... I am a spiteful man. I am an unattractive man. "
    "I think there is something wrong with my liver."
)


class OCRService:
    def __init__(self, use_mock: bool = True) -> None:
        self.use_mock = use_mock
        self._engine = None

    def _ensure_engine(self) -> None:
        if self.use_mock or self._engine is not None:
            return

        try:
            from paddleocr import PaddleOCR
        except ImportError as exc:
            raise RuntimeError(
                "PaddleOCR is not installed. Install requirements-ml.txt or set NARRATRON_USE_MOCK_SERVICES=true."
            ) from exc

        self._engine = PaddleOCR(use_angle_cls=True, lang="en")

    def extract_text(self, image_path: str) -> str:
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        if self.use_mock:
            return f"[MOCK OCR] {_SAMPLE_DOSTOYEVSKY_PASSAGE}"

        self._ensure_engine()
        assert self._engine is not None

        result = self._engine.ocr(str(path), cls=True)
        lines: list[str] = []

        for block in result:
            for entry in block:
                text = entry[1][0]
                if text:
                    lines.append(text.strip())

        return "\n".join(lines)
