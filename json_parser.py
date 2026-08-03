"""
JSON parser for Unreal Groom Importer.

Reads the JSON metadata exported from Unreal Engine and returns the
curve information required to build Blender Hair Curves.
"""

from __future__ import annotations

from pathlib import Path
import json


def read_json(filepath: str | Path) -> list[dict]:
    """
    Read Unreal Groom JSON metadata.

    Parameters
    ----------
    filepath
        Path to the JSON file.

    Returns
    -------
    list[dict]

        List of curve dictionaries.

        Example:

        [
            {
                "first": 0,
                "count": 51,
                "group": 0,
                "uv": [0.70, 0.88],
            },
            ...
        ]
    """

    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(filepath)

    with filepath.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if "curves" not in data:
        raise ValueError("JSON does not contain a 'curves' array.")

    curves = data["curves"]

    if not isinstance(curves, list):
        raise ValueError("'curves' must be a list.")

    return curves


def json_from_obj(obj_filepath: str | Path) -> Path:
    """
    Return the JSON path corresponding to an OBJ file.

    Example
    -------
        Hair.obj
            ->
        Hair.json
    """

    return Path(obj_filepath).with_suffix(".json")


def curve_count(curves: list[dict]) -> int:
    """
    Return the number of curves.
    """

    return len(curves)


def point_count(curves: list[dict]) -> int:
    """
    Return the total number of points.
    """

    return sum(curve["count"] for curve in curves)


def validate(curves: list[dict]) -> None:
    """
    Validate curve metadata.

    Raises
    ------
    ValueError
        If the JSON format is invalid.
    """

    required = {
        "first",
        "count",
        "group",
        "uv",
    }

    for index, curve in enumerate(curves):

        missing = required - curve.keys()

        if missing:
            raise ValueError(
                f"Curve {index} is missing keys: "
                f"{', '.join(sorted(missing))}"
            )

        if len(curve["uv"]) != 2:
            raise ValueError(
                f"Curve {index} has an invalid UV."
            )