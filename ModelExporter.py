import bpy

from . import ExportOptions
from .AnimationExporter import _is_mesh_animation_supported, encode_animation_data
from .MaterialExporter import encode_material_data
from .MeshExporter import encode_mesh_data

MeshDataKey = 'mesh_data'
MaterialDataKey = 'material_data'
AnimationDataKey = 'animation_data'
MetadataKey = 'metadata'
ExportedMeshesKey = 'meshes_exported'

# Metadata keys
MeshTransformsKey = 'mesh_transforms'  # This stores what each of the local transformations for each of the meshes should be

def _is_supported_export(obj):
    """
    This determines if the obj passed in can be exported into the engine.

    For now, it just checks to see if the object is a mesh...

    :param obj:  The object to export
    :return: If the object can be exported
    """
    return obj.type == 'MESH'


def save_data(encoded_data, file_path, context):
    """
    Saves the encoded_data into a compressed format for the engine.

    :param encoded_data: The encoded model data
    :param file_path: Where to save the compressed model
    :param context: The blender context
    :return: Bytes written to disk
    """
    pass


def encode_transform_data(obj):
    """
    Encodes the translation data into an engine readable format.

    :param obj: The object to pull the translation data from
    :return: dict with translation data in it
    """
    trans_mat = {}
    trans_mat['position'] = [float(obj.location[0]), float(obj.location[1]), float(obj.location[2])]
    trans_mat['scale'] = [float(obj.scale[0]), float(obj.scale[1]), float(obj.scale[2])]

    # Encode the rotation data now... check for quaternion
    if obj.rotation_mode == 'QUATERNION':
        trans_mat['mode'] = 'quaternion'
        trans_mat['rotation'] = [float(obj.rotation_quaternion[0]), float(obj.rotation_quaternion[1]),
                                 float(obj.rotation_quaternion[2]), float(obj.rotation_quaternion[3])]
    elif obj.rotation_mode == 'AXIS_ANGLE':
        print('No support for AXIS_ANGLE rotation... %s' % str(obj.name))
        raise RuntimeError('AXIS_ANGLE not supported...')
    else:
        trans_mat['mode'] = obj.rotation_mode.lower()
        trans_mat['rotation'] = [float(obj.rotation_euler[0]), float(obj.rotation_euler[1]),
                                 float(obj.rotation_euler[2])]

    return trans_mat


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
        objs = [obj for obj in scene_objs if obj.type == 'MESH']
        export_opt = config[ExportOptions.MaterialKey]
        encoded_data[MaterialDataKey] = dict(
            [(obj.name, encode_material_data(obj, context, export_opt)) for obj in objs])

    # Encode animation data
    if config[ExportOptions.AnimationKey] == ExportOptions.AnimationNoExport:
        encoded_data[AnimationDataKey] = None
    else:
        animated_objs = [obj for obj in scene_objs if _is_mesh_animation_supported(obj, context)]
        encoded_data[AnimationDataKey] = dict([(obj.name, encode_animation_data(obj)) for obj in animated_objs])

    # No needed metadata to export yet...
    if not config[ExportOptions.EmitMetadataKey]:
        encoded_data[MetadataKey] = None
    else:
        encoded_data[MetadataKey] = None

    # Export translation data for each object
    encoded_data[MeshTransformsKey] = dict(
        [(obj.name, encode_transform_data(obj)) for obj in scene_objs if obj.type == 'MESH'])
    encoded_data[ExportedMeshesKey] = [obj.name for obj in scene_objs if obj.type == 'MESH']

    return encoded_data


if __name__ == "__main__":
    config = {
        ExportOptions.MeshKey: ExportOptions.MeshAll,
        ExportOptions.MaterialKey: ExportOptions.MaterialAll,
        ExportOptions.AnimationKey: ExportOptions.AnimationKey,
        ExportOptions.FilePathKey: "D:\\Code\\game-dev\\turn-tactics\\Test\\Shaded_Model\\Resource\\Models\\test.model",
        ExportOptions.SelectedOnlyKey: False
    }

    export_model(bpy.context, config)
