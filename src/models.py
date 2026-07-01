from dataclasses import dataclass, field


@dataclass(frozen=True)
class OptionSet:
    options: list[tuple[str, str]]
    correct_letter: str

    @property
    def correct_text(self) -> str:
        for letter, text in self.options:
            if letter == self.correct_letter:
                return text
        return ""


@dataclass(frozen=True)
class GapOptionSet:
    gap_number: int
    options: list[tuple[str, str]]
    correct_letter: str


@dataclass(frozen=True)
class TestPage:
    item_id: str
    test_id: str
    row_index: int
    sub_index: int
    item_type: str
    skill: str
    input_text: str
    question_text: str
    option_set: OptionSet | None = None
    gap_option_sets: list[GapOptionSet] = field(default_factory=list)
