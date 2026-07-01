from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ItemResult:
    correct_count: int
    incorrect_count: int

    @property
    def total_count(self) -> int:
        return self.correct_count + self.incorrect_count

    @property
    def correct_percent(self) -> float:
        if self.total_count == 0:
            return 0.0
        return self.correct_count / self.total_count * 100

    @property
    def incorrect_percent(self) -> float:
        return 100 - self.correct_percent if self.total_count else 0.0


def _cell(row: dict[str, Any], *names: str) -> Any:
    normalized = {str(key).strip().lower(): value for key, value in row.items()}
    for name in names:
        value = normalized.get(name.lower())
        if value is not None:
            return value
    return None


def load_result_stats(results_path: Path) -> dict[str, ItemResult]:
    try:
        import pandas as pd
    except ImportError as exc:
        raise RuntimeError("pandas and openpyxl are required to read results.xlsx.") from exc

    frame = pd.read_excel(results_path)
    counts: dict[str, list[int]] = {}

    for row in frame.to_dict(orient="records"):
        item_id = _cell(row, "item_id", "Item ID")
        if not item_id:
            continue

        response = _cell(row, "response", "Response")
        correct = _cell(row, "correct", "Correct")
        is_correct = response == correct
        bucket = counts.setdefault(str(item_id), [0, 0])
        bucket[0 if is_correct else 1] += 1

    return {
        item_id: ItemResult(correct_count=correct, incorrect_count=incorrect)
        for item_id, (correct, incorrect) in counts.items()
    }
