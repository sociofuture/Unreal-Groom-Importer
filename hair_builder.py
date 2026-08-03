"""
Hair Curves builder.

Creates a native Blender Hair Curves object from the data exported
from Unreal Engine Groom.

Responsibilities
----------------
* Create Hair Curves
* Copy point positions
* Create curve attributes
* Apply transforms
* Disable Hair Dynamics
"""

from __future__ import annotations

import math
from os import name

import bpy


# ----------------------------------------------------------
# Constants
# ----------------------------------------------------------

OBJECT_NAME = "UE Groom"

ROOT_UV_ATTRIBUTE = "surface_uv_coordinate"
GROUP_ATTRIBUTE = "group"


# ----------------------------------------------------------
# Public API
# ----------------------------------------------------------

def build_hair(
    vertices: list[float],
    curves: list[dict],
    name="Hair"
) -> bpy.types.Object:
    """
    Create a Blender Hair Curves object.

    Parameters
    ----------
    vertices
        Flat XYZ vertex array.

    curves
        JSON curve metadata.

    Returns
    -------
    bpy.types.Object
    """

    obj = _create_empty_hair(name)

    hair = obj.data

    _create_curves(hair, curves)

    _write_positions(hair, vertices)

    _create_root_uv_attribute(hair, curves)

    _create_group_attribute(hair, curves)

    _disable_hair_dynamics(obj)

    return obj


# ----------------------------------------------------------
# Hair Object
# ----------------------------------------------------------

def _create_empty_hair(name):

    surface = None

    for obj in bpy.context.selected_objects:
        if obj.type == 'MESH':
            surface = obj
            break

    if surface is None:
        raise RuntimeError(
            "No mesh object selected.\n\n"
            "Select the character mesh before importing the Unreal Groom."
        )

    bpy.context.view_layer.objects.active = surface

    bpy.ops.object.curves_empty_hair_add()

    obj = bpy.context.active_object

    obj.name = name
    obj.data.name = name

    return obj


# ----------------------------------------------------------
# Curves
# ----------------------------------------------------------

def _create_curves(hair, curves):

    sizes = [curve["count"] for curve in curves]

    hair.add_curves(sizes)


# ----------------------------------------------------------
# Positions
# ----------------------------------------------------------

def _write_positions(hair, vertices):

    hair.position_data.foreach_set(
        "vector",
        vertices,
    )

    hair.update_tag()


# ----------------------------------------------------------
# Attributes
# ----------------------------------------------------------

def _create_root_uv_attribute(hair, curves):

    attribute = hair.attributes.new(
        ROOT_UV_ATTRIBUTE,
        type='FLOAT2',
        domain='CURVE',
    )

    values = []

    for curve in curves:

        values.extend(curve["uv"])

    attribute.data.foreach_set(
        "vector",
        values,
    )


def _create_group_attribute(hair, curves):

    attribute = hair.attributes.new(
        GROUP_ATTRIBUTE,
        type='INT',
        domain='CURVE',
    )

    values = [
        curve["group"]
        for curve in curves
    ]

    attribute.data.foreach_set(
        "value",
        values,
    )



# ----------------------------------------------------------
# Hair Dynamics
# ----------------------------------------------------------

def _disable_hair_dynamics(obj):

    modifier = obj.modifiers.get(
        "Hair Dynamics"
    )

    if modifier is None:
        return

    modifier.show_viewport = False
    modifier.show_render = False