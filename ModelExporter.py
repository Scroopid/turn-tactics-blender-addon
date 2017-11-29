import bpy
import ExportOptions

MeshDataKey = 'mesh_data'
MaterialDataKey = 'material_data'
AnimationDataKey = 'animation_data'
MetadataKey = 'metadata'

def _is_supported_export(obj):
    """
    This determines if the obj passed in can be exported into the engine.

    For now, it just checks to see if the object is a mesh...

    :param obj:  The object to export
    :return: If the object can be exported
    """
    return obj.type == 'MESH'


def _prepare_mesh_for_export(mesh_obj):
    """
    Will prepare the mesh for export, which is: copy the mesh given, rename it, triangulate the mesh, and return new name.

    :param mesh_obj: The mesh to prepare for export
    :return: The name of the triangulated mesh in the scene
    """


def encode_mesh_data(bl_obj, export_opt):
    """
    Encodes the various mesh data elements (Verts/Normals/UVs) into bytearray structures. Will also return list of
    indices to be used in engine

    :param bl_obj: The blender object to
    :param export_opt: The export option chosen
    :return: Dictionary with all of the data encoded for the given export_opt
    """
    pass


def encode_material_data(bl_mat):
    """
    Encodes the blender material into engine-optimized format

    :param bl_mat: The blender material to encode
    :return: A JSON description of the material for the engine
    """
    pass


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

if __name__ == "__main__":
    config = {
        ExportOptions.MeshKey: ExportOptions.MeshAll,
        ExportOptions.MaterialKey: ExportOptions.MaterialAll,
        ExportOptions.AnimationKey: ExportOptions.AnimationKey,
        ExportOptions.FilePathKey: "D:\\Code\\game-dev\\turn-tactics\\Test\\Shaded_Model\\Resource\\Models\\test.model",
        ExportOptions.SelectedOnlyKey: False
    }

    export_model(bpy.context, config)
