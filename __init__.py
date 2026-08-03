bl_info = {
    "name": "Unreal Groom Importer",
    "author": "Vignesh Narayan S",
    "version": (1, 0, 0),
    "blender": (5, 2, 0),
    "location": "File > Import",
    "description": "Import Unreal Engine Groom assets as native Blender Hair Curves",
    "category": "Import-Export",
}

import bpy

from .importer import IMPORT_OT_unreal_groom


# ----------------------------------------------------------
# File > Import Menu
# ----------------------------------------------------------

def menu_import(self, context):
    self.layout.operator(
        IMPORT_OT_unreal_groom.bl_idname,
        text="Unreal Groom (.obj)"
    )


# ----------------------------------------------------------
# Registration
# ----------------------------------------------------------

classes = (
    IMPORT_OT_unreal_groom,
)


def register():

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_import.append(menu_import)


def unregister():

    bpy.types.TOPBAR_MT_file_import.remove(menu_import)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()