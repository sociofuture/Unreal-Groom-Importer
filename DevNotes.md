# Unreal Groom Importer
## Developer Notes

This document describes the internal architecture of the Unreal Groom Importer Blender Extension. It is intended for developers who wish to understand, maintain, or extend the importer.

---

# Project Structure

```
unreal_groom_importer/
│
├── blender_manifest.toml
├── __init__.py
│
├── importer.py
├── obj_parser.py
├── json_parser.py
├── hair_builder.py
├── asset_loader.py
│
└── assets/
    └── Unreal Groom Assets.blend
```

---

# Overview

The importer reconstructs native Blender Hair Curves from the OBJ and JSON files exported by the Unreal Groom Exporter plugin.

The import pipeline is intentionally split into small modules, with each module responsible for a single task.

```
OBJ
   │
   ▼
OBJ Parser
   │
   ▼
Vertex Positions
   │
   ▼

JSON
   │
   ▼
JSON Parser
   │
   ▼
Curve Metadata
   │
   ▼

Hair Builder
   │
   ▼
Native Hair Curves
   │
   ▼
Asset Loader
   │
   ▼
Finished Groom
```

---

# Module Overview

## __init__.py

Addon entry point.

Responsibilities

- Register operators
- Register import menu
- Unregister classes
- Register Blender Extension metadata

No import logic should be placed here.

---

## importer.py

Main import operator.

Responsibilities

- Display File > Import menu entry
- Read selected OBJ path
- Locate matching JSON file
- Call parsers
- Build Hair Curves
- Assign Geometry Nodes
- Assign material
- Report errors

This module acts as the controller for the entire import process.

---

## obj_parser.py

Reads the exported OBJ.

Responsibilities

- Read vertex positions
- Ignore unsupported OBJ records
- Return a flat float array

The parser intentionally ignores

- Faces
- Normals
- UVs
- Materials

Only vertex positions are required.

---

## json_parser.py

Reads Groom metadata.

Responsibilities

- Load JSON
- Validate schema
- Return curve metadata

Each JSON entry describes one strand.

```
{
    "first": 108,
    "count": 46,
    "group": 0,
    "uv": [0.60, 0.95]
}
```

---

## hair_builder.py

Creates the native Blender Hair Curves object.

Responsibilities

- Create Hair Curves object
- Allocate curves
- Allocate points
- Copy positions
- Create attributes
- Apply transforms
- Disable Hair Dynamics

This module contains all Blender Hair Curves API interaction.

---

## asset_loader.py

Configures the imported groom.

Responsibilities

- Load Geometry Node asset
- Load material asset
- Assign Geometry Nodes modifier
- Assign material
- Bind selected mesh
- Set Surface UV attribute

This module contains all Asset Library interactions.

---

# Import Pipeline

```
User selects OBJ
        │
        ▼
Locate JSON
        │
        ▼
Read OBJ
        │
        ▼
Read JSON
        │
        ▼
Validate JSON
        │
        ▼
Create Hair Curves
        │
        ▼
Copy Point Positions
        │
        ▼
Create Attributes
        │
        ▼
Apply Transform Correction
        │
        ▼
Load Geometry Nodes
        │
        ▼
Assign Material
        │
        ▼
Import Complete
```

---

# OBJ Format

The importer only reads

```
v x y z
```

All other OBJ records are ignored.

Vertex positions are stored as a flat float list.

Example

```
[
x,
y,
z,

x,
y,
z,

...
]
```

This layout is compatible with

```
hair.position_data.foreach_set()
```

which provides significantly better performance than assigning points individually.

---

# JSON Format

The importer expects

```json
{
    "curves":
    [
        {
            "first": 0,
            "count": 51,
            "group": 0,
            "uv": [0.70, 0.88]
        }
    ]
}
```

Fields

| Field | Description |
|--------|-------------|
| first | First vertex index inside OBJ |
| count | Number of vertices in strand |
| group | Unreal Hair Group |
| uv | Root surface UV |

The importer validates the JSON before any Blender objects are created.

---

# Hair Curves

A native Blender Hair Curves object is created using

```
bpy.ops.object.curves_empty_hair_add()
```

Blender requires an active mesh object before this operator can execute.

If no mesh is selected, the importer displays a user-friendly error instead of Blender's internal operator error.

---

# Curve Allocation

Curve sizes are collected from the JSON.

Example

```
51
11
46
...
```

They are allocated using

```
hair.add_curves(sizes)
```

Blender automatically creates all required point storage.

---

# Position Copy

Point positions are copied using

```
hair.position_data.foreach_set(
    "vector",
    vertices
)
```

Using `foreach_set()` is substantially faster than assigning positions one point at a time, making it suitable for very large grooms containing millions of points.

---

# Attributes

The importer creates two custom attributes.

## surface_uv_coordinate

```
Type

FLOAT2

Domain

CURVE
```

Stores Unreal Groom root UV coordinates.

This attribute is required by the supplied Geometry Nodes setup.

---

## group

```
Type

INT

Domain

CURVE
```

Stores the Unreal Hair Group index.

This can be used to isolate or process individual Groom groups inside Geometry Nodes.

---

# Coordinate Conversion

Unreal Engine and Blender use different coordinate systems.

The importer performs the required conversion by applying

```
Scale

0.01

Rotation

180°
around Z
```

Transforms are applied immediately after import so the object retains clean transforms.

The Unreal exporter intentionally performs no coordinate conversion.

---

# Object Naming

The imported Hair Curves object and its data block are automatically named using the imported filename.

Example

```
Hair_S_Pixie.obj
```

creates

```
Hair_S_Pixie
```

This makes imported grooms easier to identify in larger scenes.

---

# Asset Loading

The importer loads assets from

```
assets/
    Unreal Groom Assets.blend
```

Currently imported assets

- Geometry Nodes setup
- Hair material

The asset library can be updated independently of the Python code, allowing improvements to shaders or Geometry Nodes without modifying the importer.

---

# Geometry Nodes Setup

After import

The importer

- disables the default Hair Dynamics modifier
- adds the supplied Geometry Nodes modifier
- assigns the selected mesh as the surface object
- sets the Surface UV Attribute to

```
surface_uv_coordinate
```

This immediately enables Blender's **Deform Curves on Surface** workflow.

---

# Error Handling

The importer validates

- OBJ exists
- JSON exists
- JSON schema
- Active mesh selection
- Asset library availability

Errors are presented using Blender's operator reports to provide clear feedback without exposing internal Python exceptions.

---

# Performance Notes

The importer is designed for production Groom assets.

Performance is achieved by

- bulk curve allocation
- bulk point assignment using `foreach_set()`
- avoiding per-point Python loops whenever possible
- separating parsing from Blender API calls

The importer has been tested with Groom assets containing

- 54,394 curves
- 1,492,941 points

---

# Design Philosophy

Each module has a single responsibility.

```
importer.py

Coordinates the import.
```

```
obj_parser.py

Reads OBJ.
```

```
json_parser.py

Reads metadata.
```

```
hair_builder.py

Creates Hair Curves.
```

```
asset_loader.py

Assigns assets.
```

Keeping responsibilities isolated makes the importer easier to maintain, test, and extend.

---

# Future Improvements

Potential future additions

- Progress bar during import
- Batch Groom import
- Multiple Geometry Nodes presets
- Optional material assignment
- Width attribute import
- Vertex color import
- Curve ID attribute
- Automatic asset library registration
- Import options dialog
- Support for future Unreal Groom metadata

---
