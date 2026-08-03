# Unreal Groom Importer Blender Extension

The Unreal Groom Importer  Blender Extension imports Groom Assets exported from Unreal Engine as native Blender Hair Curves.

The importer automatically reconstructs the original curve layout, creates the required attributes, applies coordinate conversion, and configures the hair object for use inside Blender.

---

## Features

- Import Unreal Groom OBJ files
- Automatically reads the matching JSON metadata
- Creates native Blender Hair Curves
- Preserves strand topology
- Preserves root UV coordinates
- Creates `surface_uv_coordinate` attribute
- Creates `group` attribute
- Automatically applies scale and orientation correction
- Automatically loads the Geometry Nodes asset
- Automatically assigns the hair material
- Automatically disables the default Hair Dynamics modifier

---

## Requirements

- Blender 5.2 or later
- Unreal Groom Assets library included with the extension
- Groom exported using the Unreal Groom Exporter plugin

---

## Installation

1. Open **Edit → Preferences → Get Extensions**.

2. Install the Unreal Groom Blender Extension.

3. Ensure the included asset library remains inside the extension folder.

---

## Quick Start

1. Select the character mesh that the groom should be attached to.

2. Choose **File → Import → Unreal Groom (.obj)**.

3. Select the exported OBJ file.

The importer automatically:

- Reads the accompanying JSON file
- Creates the Hair Curves object
- Imports root UV data
- Applies coordinate conversion
- Loads the Geometry Nodes modifier
- Assigns the hair material

The imported Hair Curves object is named after the imported file.

### Note

The `.json` file must have the same filename as the `.obj` file and be located in the same folder.

Example:

```
Hair_S_Pixie.obj
Hair_S_Pixie.json
```
