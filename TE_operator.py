import bpy

from bpy.props import (
    BoolProperty,
    EnumProperty,
    StringProperty
)

class TEModelExporter(bpy.types.Operator):
    """
    Export and convert visible models to engine-optimized meshes inside a .model archive
    """
    bl_idname = "te.export.model"
    bl_label = "Export Turn Engine .model"
    filepath = StringProperty(subtype='FILE_PATH')

    mesh_exportOpts = (
        ('All', 'All', 'Exports all of the visible meshes data (position, normals, uv)'),
        ('Vertices', '', 'Exports only the vertex coordinates of the meshes visible'),
        ('Vertices_Normals', 'Vertices/Normals', 'Exports only the vertex coordinates and normals of the meshes visible'),
        ('Vertices_UV', 'Vertices/UV', 'Exports only the vertex coordinates and uv coordinates of the meshes visible'),
        ('Normals', 'Normals', 'Exports only the normals of the meshes visible'),
        ('Normals_UV', 'Normals/UV', 'Exports only the normals and uv coordinates of the meshes visible'),
        ('UV', 'UV', 'Exports only the uv coordinates of the meshes visible'),
        ('No_Export', 'None', "Doesn't export any mesh data into .model archive")
    )

    material_exportOpts = (
        ('All', 'All', 'Exports all of the materials used in the scene')
    )