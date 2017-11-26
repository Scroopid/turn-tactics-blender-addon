bl_info = {
    "name": "Turn Engine Exporter Tools",
    "author": "Scroopid",
    "version": (1, 0, 0),
    "blender": (2, 79, 0),
    "location": "File > Export > Turn Engine (.model)",
    "description": "Tools for exporting meshes into Turn Engine .model archives with engine-optimized format.",
    "warning": "WIP, when the export tools are finished and integrated into the engine, this will be removed",
    "category": "Import-Export"
}

import bpy
from . import operator


def menu_opt(self, context):
    self.layout.operator(operator.TTModelExporter.bl_idname, text="Turn Tactics (.model)")

classes = (
    operator.TTModelExporter,
)


def register():
    bpy.types.INFO_MT_file_export.append(menu_opt)

    from bpy.utils import register_class
    for klass in classes:
        register_class(klass)


def unregister():
    bpy.types.INFO_MT_file_export.remove(menu_opt)

    from bpy.utils import unregister_class
    for klass in reversed(classes):
        unregister_class(klass)


if __name__ == "__main__":
    register()