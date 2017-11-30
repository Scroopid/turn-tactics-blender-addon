import bpy
import bmesh
from . import ExportOptions

MeshDataKey = 'mesh_data'
MaterialDataKey = 'material_data'
AnimationDataKey = 'animation_data'
MetadataKey = 'metadata'

# Metadata keys
MeshTransformsKey = 'mesh_transforms' # This stores what each of the local transformations for each of the meshes should be
MaterialLinksKey = 'material_links'   # This stores each of the links to materials of the meshes in the engine
AnimationsLinkKey = 'animation_links' # This stores links for each of the different meshes animations

# Lookup tables for export options
_export_verts_lu = {
    ExportOptions.MeshAll: True,
    ExportOptions.MeshNoExport: False,
    ExportOptions.MeshNormalsAndUVs: False,
    ExportOptions.MeshNormals: False,
    ExportOptions.MeshUVs: False,
    ExportOptions.MeshVertsAndUVs: True,
    ExportOptions.MeshVerts: True,
    ExportOptions.MeshVertsAndNormals: True
}
_export_norms_lu = {
    ExportOptions.MeshAll: True,
    ExportOptions.MeshNoExport: False,
    ExportOptions.MeshNormalsAndUVs: True,
    ExportOptions.MeshNormals: True,
    ExportOptions.MeshUVs: False,
    ExportOptions.MeshVertsAndUVs: False,
    ExportOptions.MeshVerts: False,
    ExportOptions.MeshVertsAndNormals: True
}
_export_uvs_lu = {
    ExportOptions.MeshAll: True,
    ExportOptions.MeshNoExport: False,
    ExportOptions.MeshNormalsAndUVs: True,
    ExportOptions.MeshNormals: False,
    ExportOptions.MeshUVs: True,
    ExportOptions.MeshVertsAndUVs: True,
    ExportOptions.MeshVerts: False,
    ExportOptions.MeshVertsAndNormals: False
}

def _is_supported_export(obj):
    """
    This determines if the obj passed in can be exported into the engine.

    For now, it just checks to see if the object is a mesh...

    :param obj:  The object to export
    :return: If the object can be exported
    """
    return obj.type == 'MESH'


def _is_mesh_animation_supported(bl_obj, context):
    """
    Checks over objects animations and ensures that they are correctly rigged and animated for the engine.

    This is just a placeholder til animation features are integrated and researched
    :param bl_obj: The blender object to validate for exporting animations
    :param context: The blender context
    :return: If the mesh's animations are supported
    """
    return True


def _prepare_mesh_for_export(mesh_obj):
    """
    Prepare the mesh for export, which is: convert mesh to bmesh, triangulate the bmesh, and return new mesh.

    :param mesh_obj: The mesh to prepare for export
    :return: The triangulated bmesh of given mesh_obj
    """
    # Copy the mesh given and give it a new name with a _prepared postfix
    bmesh_obj = bmesh.new()
    bmesh_obj.from_mesh(mesh_obj)
    bmesh.ops.triangulate(bmesh_obj, faces=bmesh_obj.faces)
    return bmesh_obj


def save_data(encoded_data, file_path, context):
    """
    Saves the encoded_data into a compressed format for the engine.

    :param encoded_data: The encoded model data
    :param file_path: Where to save the compressed model
    :param context: The blender context
    :return: Bytes written to disk
    """
    pass


def encode_mesh_data(bl_obj, export_opt):
    """
    Encodes the various mesh data elements (Verts/Normals/UVs) into bytearray structures. Will also return list of
    indices to be used in engine

    :param bl_obj: The blender object to
    :param export_opt: The export option chosen
    :return: Dictionary with all of the data encoded for the given export_opt
    """
    print('Exporting %s mesh data' % bl_obj.name)

    # Prep mesh for export
    bmesh_obj = _prepare_mesh_for_export(bl_obj)

    export_verts = _export_verts_lu[export_opt]
    export_uvs = _export_uvs_lu[export_opt]
    export_norms = _export_norms_lu[export_opt]

    # Validate mesh options
    uv_layer = bmesh_obj.loops.layers.uv.active
    if uv_layer is None:
        raise RuntimeError('Cannot encode mesh without UV when export_opt specifies to export UVs')

    for face in bmesh_obj.faces:
        print('Face %i' % face.index)

        for loop, vert in zip(face.loops, face.verts):
            print(' - Loop for Vertex %i, UV = %r' % (face.index, loop[uv_layer].uv))


def encode_material_data(bl_mat):
    """
    Encodes the blender material into engine-optimized format

    :param bl_mat: The blender material to encode
    :return: A JSON description of the material for the engine
    """
    pass


def create_link_definition(bl_obj, context):
    """
    Creates a link definition for the engine, to link the material to the mesh. This will simply use the name of the
    material in blender to link to a material definition created locally in blender, or a built-in material of the
    engine

    If link_only is specified for material export options and there is no engine material with existing name, the
    default material will be used, with the engine producing a material link error of material not found.

    :param bl_obj: The blender object to create link definition for.
    :param context:
    :return:
    """


def encode_animation_data(bl_obj):
    """
    This encodes all of the animation data in the model

    This method is a placeholder for now, doesn't do anything until animations are in engine

    :param bl_obj: The blender object to pull animation data from
    :return: The encoded animation data
    """
    pass


def export_model(context, config):
    """
    Exports the models in the blender scene with the config given. See the different config
    options to see how to customize an export

    :param context: Blender context
    :param config: The configuration of the export
    :return: Filepath to exported model
    """
    encoded_data = {}

    if config[ExportOptions.SelectedOnlyKey]:
        scene_objs = [obj for obj in context.scene.objects if obj.selected and _is_supported_export(obj)]
    else:
        scene_objs = [obj for obj in context.scene.objects if _is_supported_export(obj)]

    # Encode all of the mesh data if we need to
    if config[ExportOptions.MeshKey] == ExportOptions.MeshNoExport:
        encoded_data[MeshDataKey] = None
    else:
        objs = [obj for obj in scene_objs if obj.type == 'MESH']
        export_opt = config[ExportOptions.MeshKey]
        encoded_data[MeshDataKey] = dict([(obj.name, encode_mesh_data(obj, export_opt)) for obj in objs])

    # Encode the material data
    if config[ExportOptions.MaterialKey] == ExportOptions.MaterialNoExport:
        encoded_data[MaterialDataKey] = None
    else:
        # TODO: Encode Material data
        pass

    # Encode animation data
    if config[ExportOptions.AnimationKey] == ExportOptions.AnimationNoExport:
        encoded_data[AnimationDataKey] = None
    else:
        animated_objs = [obj for obj in scene_objs if _is_mesh_animation_supported(obj, context)]
        encoded_data[AnimationDataKey] = dict([(obj.name, encode_animation_data(obj)) for obj in animated_objs])

    if not config[ExportOptions.EmitMetadataKey]:
        encoded_data[MetadataKey] = None
    else:
        pass

if __name__ == "__main__":
    config = {
        ExportOptions.MeshKey: ExportOptions.MeshAll,
        ExportOptions.MaterialKey: ExportOptions.MaterialAll,
        ExportOptions.AnimationKey: ExportOptions.AnimationKey,
        ExportOptions.FilePathKey: "D:\\Code\\game-dev\\turn-tactics\\Test\\Shaded_Model\\Resource\\Models\\test.model",
        ExportOptions.SelectedOnlyKey: False
    }

    export_model(bpy.context, config)
