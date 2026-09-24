"""
Asset loader for Unreal Groom Importer.

Loads bundled assets from GroomAssets.blend.

Responsibilities
----------------
* Append Geometry Node group
* Append Material
* Assign Geometry Nodes modifier
* Assign Material
"""

from __future__ import annotations

from pathlib import Path

import bpy


# ----------------------------------------------------------
# Constants
# ----------------------------------------------------------

ASSET_BLEND = "GroomAssets.blend"

NODE_GROUP_NAME = "UE_HairCurve"
MATERIAL_NAME = "UE_HairCurve"

ATTACH_NODE_NAME = "Attach Hair Curves to Surface"

ASSET_FOLDER = Path(__file__).parent / "assets"
ASSET_FILE = ASSET_FOLDER / ASSET_BLEND


# ----------------------------------------------------------
# Public API
# ----------------------------------------------------------

def load_assets():
    """
    Append bundled assets if they are not already loaded.
    """

    if not ASSET_FILE.exists():
        raise FileNotFoundError(
            f"Asset library not found:\n{ASSET_FILE}"
        )

    node_groups = []
    materials = []

    if NODE_GROUP_NAME not in bpy.data.node_groups:
        node_groups.append(NODE_GROUP_NAME)

    if MATERIAL_NAME not in bpy.data.materials:
        materials.append(MATERIAL_NAME)

    if not node_groups and not materials:
        return

    with bpy.data.libraries.load(
        str(ASSET_FILE),
        link=False,
    ) as (source, destination):

        destination.node_groups = node_groups
        destination.materials = materials


def configure_node_group():
    """
    Fix up the bundled node group for imported grooms.

    'Attach Hair Curves to Surface' ships with 'Snap to Surface' enabled, which
    re-anchors every curve root onto the surface. The lookup it uses has no
    surface configured here, so the snap sends the whole groom to the origin -
    measured at 98.8% of points collapsed. The OBJ already holds absolute root
    positions and the JSON already holds exact root UVs, so neither the snap nor
    the re-projection is wanted.
    """

    node_group = bpy.data.node_groups.get(NODE_GROUP_NAME)

    if node_group is None:
        return

    node = node_group.nodes.get(ATTACH_NODE_NAME)

    if node is None:
        return

    for socket_name, value in (
        ("Use Existing Attachment", True),
        ("Snap to Surface", False),
    ):

        socket = node.inputs.get(socket_name)

        if socket is not None:
            socket.default_value = value


# ----------------------------------------------------------
# Geometry Nodes
# ----------------------------------------------------------

def assign_geometry_nodes(obj):
    """
    Add the bundled Geometry Nodes modifier.
    """

    load_assets()

    configure_node_group()

    modifier = obj.modifiers.new(
        name="UE Groom",
        type='NODES',
    )

    modifier.node_group = bpy.data.node_groups[
        NODE_GROUP_NAME
    ]

    return modifier


# ----------------------------------------------------------
# Material
# ----------------------------------------------------------

def assign_material(obj):
    """
    Assign bundled material.
    """

    load_assets()

    material = bpy.data.materials[MATERIAL_NAME]

    curves = obj.data

    if len(curves.materials) == 0:
        curves.materials.append(material)
    else:
        curves.materials[0] = material


# ----------------------------------------------------------
# Surface
# ----------------------------------------------------------

def assign_surface(
    obj,
    surface,
    uv_map="UVMap",
):
    """
    Bind curves to a surface mesh.
    """

    if surface is None:
        return

    obj.data.surface = surface
    obj.data.surface_uv_map = uv_map


# ----------------------------------------------------------
# Convenience
# ----------------------------------------------------------

def setup_hair(
    obj,
    surface=None,
    uv_map="UVMap",
):
    """
    Complete setup.

    * Append assets
    * Assign Geometry Nodes
    * Assign Material
    * Bind surface
    """

    load_assets()

    assign_geometry_nodes(obj)

    assign_material(obj)

    assign_surface(
        obj,
        surface,
        uv_map,
    )