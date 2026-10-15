from __future__ import annotations

import csv
import json
from typing import Any, Iterator


class DataGeneratorStorage:

    @staticmethod
    def read_csv_generator(file_path: str) -> Iterator[dict[str, str]]:
        with open(file_path, "r", encoding="utf-8", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                yield row

    @staticmethod
    def save_report(file_path: str, data: dict[str, Any]) -> None:
        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=2)
            json_file.write("\n")