from __future__ import annotations

from pathlib import Path

import bpy

from bpy.types import Operator
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper

from .obj_parser import read_obj
from .json_parser import (
    json_from_obj,
    read_json,
    validate,
)
from .hair_builder import build_hair
from .asset_loader import setup_hair


class IMPORT_OT_unreal_groom(
    Operator,
    ImportHelper,
):
    """Import Unreal Groom"""

    bl_idname = "import_scene.unreal_groom"
    bl_label = "Import Unreal Groom"
    bl_options = {"REGISTER", "UNDO"}

    filename_ext = ".obj"

    filter_glob: StringProperty(
        default="*.obj",
        options={"HIDDEN"},
    )

    # ----------------------------------------------------------
    # Execute
    # ----------------------------------------------------------

    def execute(self, context):

        try:

            obj_path = Path(self.filepath)

            if not obj_path.exists():
                self.report(
                    {"ERROR"},
                    "OBJ file not found."
                )
                return {"CANCELLED"}

            json_path = json_from_obj(obj_path)

            if not json_path.exists():
                self.report(
                    {"ERROR"},
                    f"Missing JSON:\n{json_path.name}"
                )
                return {"CANCELLED"}

            #
            # Read files
            #

            vertices = read_obj(obj_path)

            curves = read_json(json_path)

            validate(curves)
            
            name = obj_path.stem

            #
            # Build hair
            #

            hair_object = build_hair(
                vertices,
                curves,
               name=name,
            )

            #
            # Find selected mesh
            #

            surface = None

            for obj in context.selected_objects:

                if obj == hair_object:
                    continue

                if obj.type == 'MESH':
                    surface = obj
                    break

            #
            # Setup assets
            #

            setup_hair(
                hair_object,
                surface=surface,
                uv_map="UVMap",
            )

            #
            # Done
            #

            self.report(
                {"INFO"},
                f"Imported {len(curves):,} curves"
            )

            return {"FINISHED"}

        except Exception as e:

            self.report(
                {"ERROR"},
                str(e),
            )

            import traceback

            traceback.print_exc()

            return {"CANCELLED"}