from __future__ import annotations

import math
import shutil
from pathlib import Path
import subprocess
import tempfile
import wave


class PiperTTSConfigError(RuntimeError):
    """Raised when Piper is not configured correctly."""


class TTSService:
    def __init__(
        self,
        use_mock: bool = True,
        piper_bin: str = "piper",
        piper_model_path: str = "",
        piper_speaker_id: str = "",
    ) -> None:
        self.use_mock = use_mock
        self.piper_bin = piper_bin
        self.piper_model_path = piper_model_path
        self.piper_speaker_id = piper_speaker_id

    def _build_cmd(self, output_audio_path: str) -> list[str]:
        if not self.piper_model_path:
            raise PiperTTSConfigError(
                "NARRATRON_PIPER_MODEL_PATH is empty. Set it to a local Piper .onnx model path."
            )

        cmd = [
            self.piper_bin,
            "--model",
            self.piper_model_path,
            "--output_file",
            output_audio_path,
        ]

        if self.piper_speaker_id:
            cmd.extend(["--speaker", self.piper_speaker_id])

        return cmd

    def _synthesize_with_piper(self, text: str, output_audio_path: str) -> None:
        cmd = self._build_cmd(output_audio_path)

        try:
            subprocess.run(
                cmd,
                input=text,
                text=True,
                check=True,
                capture_output=True,
            )
        except FileNotFoundError as exc:
            raise PiperTTSConfigError(
                "Piper binary not found. Install Piper and/or set NARRATRON_PIPER_BIN to its executable path."
            ) from exc
        except subprocess.CalledProcessError as exc:
            stderr = (exc.stderr or "").strip()
            raise RuntimeError(f"Piper synthesis failed: {stderr}") from exc

    def _write_mock_output(self, text: str, path: Path) -> None:
        # Try real spoken audio first for mock mode; keep tone fallback for environments without TTS tools.
        if self._try_system_tts(text=text, path=path):
            return

        self._write_tone_fallback(text=text, path=path)

    def _try_system_tts(self, text: str, path: Path) -> bool:
        say_bin = shutil.which("say")
        if not say_bin:
            return False

        try:
            with tempfile.TemporaryDirectory(prefix="narra-tron-tts-") as tmp_dir:
                tmp_aiff = Path(tmp_dir) / "speech.aiff"

                subprocess.run(
                    [say_bin, "-o", str(tmp_aiff), text],
                    check=True,
                    capture_output=True,
                    text=True,
                )

                # Prefer WAV output for consistency with downstream components.
                afconvert_bin = shutil.which("afconvert")
                if path.suffix.lower() == ".wav" and afconvert_bin:
                    subprocess.run(
                        [
                            afconvert_bin,
                            "-f",
                            "WAVE",
                            "-d",
                            "LEI16@22050",
                            str(tmp_aiff),
                            str(path),
                        ],
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                else:
                    path.write_bytes(tmp_aiff.read_bytes())

            return path.exists() and path.stat().st_size > 0
        except subprocess.CalledProcessError:
            return False

    def _write_tone_fallback(self, text: str, path: Path) -> None:
        # Final fallback when system TTS is unavailable.
        sample_rate = 22050
        duration_seconds = max(1.0, min(4.0, len(text) / 120.0))
        total_samples = int(sample_rate * duration_seconds)
        frequency = 220.0
        amplitude = 0.2

        with wave.open(str(path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)

            for i in range(total_samples):
                value = int(
                    32767
                    * amplitude
                    * math.sin(2 * math.pi * frequency * i / sample_rate)
                )
                wav_file.writeframesraw(
                    value.to_bytes(2, byteorder="little", signed=True)
                )

    def synthesize(self, text: str, output_audio_path: str) -> str:
        path = Path(output_audio_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        if self.use_mock:
            self._write_mock_output(text=text, path=path)
            return str(path)

        self._synthesize_with_piper(text=text, output_audio_path=str(path))

        if not path.exists():
            raise RuntimeError(
                "Piper reported success but output file was not created."
            )

        return str(path)
