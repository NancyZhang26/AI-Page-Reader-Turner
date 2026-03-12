from narratron.models import CommandType
from narratron.services.stt import CommandParser


def test_parse_start_command() -> None:
    parser = CommandParser()
    assert parser.parse("please start reading") == CommandType.START


def test_parse_turn_command() -> None:
    parser = CommandParser()
    assert parser.parse("next page please") == CommandType.TURN


def test_parse_back_command() -> None:
    parser = CommandParser()
    assert parser.parse("go back one page") == CommandType.BACK


def test_parse_unknown_command() -> None:
    parser = CommandParser()
    assert parser.parse("what is the weather") == CommandType.UNKNOWN
