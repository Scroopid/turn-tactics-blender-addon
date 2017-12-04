import bpy
import time
from . import ExportOptions

from bpy.props import (
    BoolProperty,
    EnumProperty,
    StringProperty
)


class TTModelExporter(bpy.types.Operator):
    """
    Export and convert visible models to engine-optimized meshes inside a .model archive
    """
    bl_idname = 'export.tt_model'
    bl_label = 'Export Turn Tactics .model'
    filepath = StringProperty(subtype='FILE_PATH')

    # -- Export Options --
    mesh_exportOpts = (
        (ExportOptions.MeshAll, 'All', 'Exports all of the visible meshes data (position, normals, uv)'),
        (ExportOptions.MeshVerts, 'Vertices', 'Exports only the vertex coordinates of the meshes visible'),
        (ExportOptions.MeshVertsAndNormals, 'Vertices/Normals',
         'Exports only the vertex coordinates and normals of the meshes visible'),
        (ExportOptions.MeshVertsAndUVs, 'Vertices/UV',
         'Exports only the vertex coordinates and uv coordinates of the meshes visible'),
        (ExportOptions.MeshNormals, 'Normals', 'Exports only the normals of the meshes visible'),
        (ExportOptions.MeshNormalsAndUVs, 'Normals/UV',
         'Exports only the normals and uv coordinates of the meshes visible'),
        (ExportOptions.MeshUVs, 'UV', 'Exports only the uv coordinates of the meshes visible'),
        (ExportOptions.MeshNoExport, 'None', "Doesn't export any mesh data into .model archive")
    )

    material_exportOpts = (
        (ExportOptions.MaterialAll, 'All', 'Exports all of the materials used in the scene'),
        (ExportOptions.MaterialLink, 'Link',
         'Only links the name of the material to the meshes, does not save material in '
         'archive. Useful for using existing materials. This is apart of the metadata and will not be linked if no '
         'metadata is exported'),
        (ExportOptions.MaterialSave, 'Save',
         'Only saves the materials used by the various meshes. Useful for exporting materials.'),
        (ExportOptions.MaterialNoExport, 'None',
         'Does not export any material data, sets meshes material property to default (Lambert gray).')
    )

    animation_exportOpts = (
        (ExportOptions.AnimationNoExport, 'None', 'WIP. Animation data is not supported yet...'),
        (ExportOptions.AnimationAll, 'All', 'Does not affect export yet. WIP')
    )

    # -- Controls --
    exportMetadata = BoolProperty(name='Export Metadata', default=True, description='Exports the metadata needed to '
                                                                                    'link Meshes/Material/Animations '
                                                                                    ' to a model in-engine.')
    exportSelectedOnly = BoolProperty(name='Only Export Selected', default=False,
                                      description='Exports only the selected objects in the scene.')

    exportMeshData = EnumProperty(name='Export Mesh Data', default='All', description='What mesh data to export.',
                                  items=mesh_exportOpts)
    exportMaterialData = EnumProperty(name='Export Material Data', default='All', description='What materials and '
                                                                                              'material metadata to '
                                                                                              'export.',
                                      items=material_exportOpts)
    exportAnimationData = EnumProperty(name='Export Animation Data', default='No_Export', description='What '
                                                                                                      'animations and'
                                                                                                      ' animation '
                                                                                                      'metadata to '
                                                                                                      'export.',
                                       items=animation_exportOpts)

    def execute(self, context):
        start = time.time()
        filePath = bpy.path.ensure_ext(self.filepath, '.model')
        config = {
            ExportOptions.FilePathKey: filePath,
            ExportOptions.MeshKey: self.exportMeshData,
            ExportOptions.MaterialKey: self.exportMaterialData,
            ExportOptions.AnimationKey: self.exportAnimationData,
            ExportOptions.EmitMetadataKey: self.exportMetadata,
            ExportOptions.SelectedOnlyKey: self.exportSelectedOnly
        }

        from .ModelExporter import export_model
        export_model(context, config)

        print("Export finished in %.4f seconds" % (time.time() - start))
        return {'FINISHED'}

    def invoke(self, context, event):
        if not self.filepath:
            self.filepath = bpy.path.ensure_ext(bpy.data.filepath, '.model')
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {'RUNNING_MODAL'}
