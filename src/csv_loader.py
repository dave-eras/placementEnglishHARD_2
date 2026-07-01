import csv
from pathlib import Path

from src.models import TestPage
from src.option_parser import parse_option_cell


def _item_id(row_index: int, sub_index: int, item_type: str) -> str:
    normalized_type = item_type.lower().replace("/", "_").replace(" ", "_")
    return f"row_{row_index:02d}_{normalized_type}_q_{sub_index}"


def load_pages(csv_path: Path) -> list[TestPage]:
    pages: list[TestPage] = []
    test_id = csv_path.stem

    with csv_path.open(encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.reader(csv_file)
        for row_index, row in enumerate(reader, start=1):
            if not row or not any(cell.strip() for cell in row):
                continue

            item_type = row[0].strip()
            input_text = row[1].strip() if len(row) > 1 else ""

            if not item_type:
                continue

            sub_index = 0
            for cell in row[2:]:
                if not cell.strip():
                    continue

                sub_index += 1
                question_text, option_set = parse_option_cell(cell)
                pages.append(
                    TestPage(
                        item_id=_item_id(row_index, sub_index, item_type),
                        test_id=test_id,
                        row_index=row_index,
                        sub_index=sub_index,
                        item_type=item_type,
                        skill=item_type,
                        input_text=input_text,
                        question_text=question_text,
                        option_set=option_set,
                    )
                )

    return pages
