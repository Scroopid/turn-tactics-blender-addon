import bpy

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
        ('All', 'All', 'Exports all of the visible meshes data (position, normals, uv)'),
        ('Vertices', 'Vertices', 'Exports only the vertex coordinates of the meshes visible'),
        ('Vertices_Normals', 'Vertices/Normals',
         'Exports only the vertex coordinates and normals of the meshes visible'),
        ('Vertices_UV', 'Vertices/UV', 'Exports only the vertex coordinates and uv coordinates of the meshes visible'),
        ('Normals', 'Normals', 'Exports only the normals of the meshes visible'),
        ('Normals_UV', 'Normals/UV', 'Exports only the normals and uv coordinates of the meshes visible'),
        ('UV', 'UV', 'Exports only the uv coordinates of the meshes visible'),
        ('No_Export', 'None', "Doesn't export any mesh data into .model archive")
    )

    material_exportOpts = (
        ('All', 'All', 'Exports all of the materials used in the scene'),
        ('Link_Only', 'Link', 'Only links the name of the material to the meshes, does not save material in '
                                   'archive. Useful for using existing materials.'),
        ('Save_Only', 'Save', 'Only saves the materials used by the various meshes. Useful for exporting materials.'),
        ('No_Export', 'None',
         'Does not export any material data, sets meshes material property to default (Lambert gray).')
    )

    animation_exportOpts = (
        ('No_Export', 'None', 'WIP. Animation data is not supported yet...'),
        ('All', 'All', 'Does not affect export yet. WIP')
    )

    # -- Controls --
    exportMetadata = BoolProperty(name='Export Metadata', default=True, description='Exports the metadata needed to '
                                                                                    'link Meshes/Material/Animations '
                                                                                    ' to a model in-engine.')

    exportMeshData = EnumProperty(name='Export Mesh Data', default='All', description='What mesh data to export.', items=mesh_exportOpts)
    exportMaterialData = EnumProperty(name='Export Material Data', default='All', description='What materials and '
                                                                                              'material metadata to '
                                                                                              'export.', items=material_exportOpts)
    exportAnimationData = EnumProperty(name='Export Animation Data', default='No_Export', description='What '
                                                                                                      'animations and'
                                                                                                      ' animation '
                                                                                                      'metadata to '
                                                                                                      'export.', items=animation_exportOpts)

    def _parseOpt(self, val):
        if val == 'No_Export':
            return None
        return val

    def execute(self, context):
        filePath = bpy.path.ensure_ext(self.filepath, '.model')
        config = {
            'file_path': filePath,
            'mesh_export': self._parseOpt(self.exportMeshData),
            'material_export': self._parseOpt(self.exportMaterialData),
            'animation_export': self._parseOpt(self.exportAnimationData),
            'emit_metadata': self.exportMetadata
        }

        from .ModelExporter import exportModel
        exportModel(context, config)
        return {'FINISHED'}

    def invoke(self, context, event):
        if not self.filepath:
            self.filepath = bpy.path.ensure_ext(bpy.data.filepath, '.model')
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {'RUNNING_MODAL'}
