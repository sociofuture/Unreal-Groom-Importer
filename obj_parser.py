"""
OBJ parser for Unreal Groom Importer.

Reads only vertex positions from an OBJ file and returns a flat list
ready for Blender's foreach_set().
"""

from __future__ import annotations

from pathlib import Path


# Unreal -> Blender scale
SCALE = 0.01


def read_obj(filepath: str | Path) -> list[float]:
    """
    Read vertex positions from an OBJ file.

    Parameters
    ----------
    filepath
        Path to the OBJ file.

    Returns
    -------
    list[float]

        Flat float list:

        [
            x0, y0, z0,
            x1, y1, z1,
            ...
        ]
    """

    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(filepath)

    vertices: list[float] = []

    with filepath.open("r", encoding="utf8") as obj:

        for line in obj:

            if not line.startswith("v "):
                continue

            try:
                _, x, y, z = line.split(maxsplit=3)
            except ValueError:
                continue

            x = float(x)
            y = float(y)
            z = float(z)

            #
            # Unreal → Blender
            #
            # Scale only.
            # Rotation is applied to the object later so that
            # transforms can be applied cleanly.
            #
            vertices.extend((
                 x * SCALE,
                -y * SCALE,
                 z * SCALE,
            ))

    return vertices


def vertex_count(vertices: list[float]) -> int:
    """
    Return the number of vertices in a flat vertex array.
    """

    return len(vertices) // 3