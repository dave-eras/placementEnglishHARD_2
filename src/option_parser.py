import re

from src.models import OptionSet

OPTION_RE = re.compile(r"^([A-Z])\)\s*(.+)$")
ANSWER_RE = re.compile(r"^Answer:\s*([A-Z])\s*$", re.IGNORECASE)


def parse_option_cell(cell: str) -> tuple[str, OptionSet]:
    prompt_lines: list[str] = []
    options: list[tuple[str, str]] = []
    correct_letter = ""

    for raw_line in cell.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        answer_match = ANSWER_RE.match(line)
        if answer_match:
            correct_letter = answer_match.group(1).upper()
            continue

        option_match = OPTION_RE.match(line)
        if option_match:
            options.append((option_match.group(1), option_match.group(2).strip()))
            continue

        prompt_lines.append(raw_line.rstrip())

    if not prompt_lines:
        raise ValueError("Question cell is missing prompt text.")
    if not options:
        raise ValueError(f"Question is missing options: {prompt_lines[0]}")
    if not correct_letter:
        raise ValueError(f"Question is missing an answer key: {prompt_lines[0]}")
    if correct_letter not in {letter for letter, _ in options}:
        raise ValueError(f"Answer key {correct_letter} is not one of the options.")

    return "\n".join(prompt_lines), OptionSet(options=options, correct_letter=correct_letter)
