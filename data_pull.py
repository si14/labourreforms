import json
import os
import tomllib
from pathlib import Path
from typing import Optional

import requests
from pydantic import BaseModel


class Group(BaseModel):
    id: str
    short: str
    title: str


class Bill(BaseModel):
    group: str
    title: str
    parliament_id: Optional[int] = None
    context_url: Optional[str] = None
    theguardian: Optional[str] = None
    ft: Optional[str] = None


def read_bills() -> tuple[dict[str, Group], list[Bill]]:
    with open("kings_speech_2024.toml", "rb") as f:
        raw_data = tomllib.load(f)

    groups = {g["id"]: Group.model_validate(g) for g in raw_data["group"]}
    bills = [Bill.model_validate(b) for b in raw_data["bill"]]

    return groups, bills


CACHE_DIR = Path("./data_cache")


def main() -> None:
    groups, bills = read_bills()

    for bill in bills:
        if bill.parliament_id is None:
            continue

        response = requests.get(
            f"https://bills-api.parliament.uk/api/v1/Bills/{bill.parliament_id}",
        )
        response.raise_for_status()

        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(CACHE_DIR / f"bill_{bill.parliament_id}.json", "w") as f:
            s = json.dumps(response.json(), indent=2)
            f.write(s)


if __name__ == "__main__":
    main()
