from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class CommandType(str, Enum):
    START = "start"
    STOP = "stop"
    TURN = "turn_page"
    BACK = "go_back"
    UNKNOWN = "unknown"


class OCRResult(BaseModel):
    text: str = Field(default="")


class STTResult(BaseModel):
    transcript: str = Field(default="")


class CommandResult(BaseModel):
    command: CommandType
    transcript: str


class PageProcessRequest(BaseModel):
    image_path: str
    output_audio_path: str = "output.wav"


class PageProcessResult(BaseModel):
    extracted_text: str
    audio_path: str
    page_turn_signal: str


class TranscribeRequest(BaseModel):
    audio_path: str


class ParseTranscriptRequest(BaseModel):
    transcript: str
