"""General helper functions, helper classes, and decorators."""

from __future__ import annotations

import datetime
import json
from pathlib import Path, PurePath
from typing import Any, cast


def read_json_file(path: PurePath | str) -> dict[str, Any]:
    """Read json file, thowing an error if missing."""
    if not path:
        raise RuntimeError("Could not open file. Filepath not provided.")

    if not Path(path).exists():
        msg = f"File at '{path}' was not found."
        for template in [f"{path}.template"]:
            if Path(template).exists():
                msg += f"\nFor more info, please see the sample template at: {template}"
        raise FileExistsError(msg)

    return cast(dict, json.loads(Path(path).read_text()))


def utc_now() -> datetime.datetime:
    """Return current time in UTC."""
    return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
