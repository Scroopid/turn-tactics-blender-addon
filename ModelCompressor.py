import json
import zipfile

from .MeshExporter import EncodedIndicesKey, EncodedUVsKey, EncodedNormalsKey, EncodedVertsKey
from .ModelExporter import MeshTransformsKey, MetadataKey, AnimationDataKey, MaterialDataKey, MeshDataKey, \
    ExportedMeshesKey


def _generate_mesh_link(encoded_mesh_data, model_name, type):
    link = {'location': '%s.%s.bin' % (model_name, type), 'bytes_length': len(encoded_mesh_data), 'type': type}

    return link


def _save_bytes(bytes, name, zfile):
    """
    Save the bytes given into the zfile with the name given
    :param bytes: The bytes to compress and save
    :param name: The name of the file inside of the archive
    :param zfile: The zipfile
    """
    zfile.writestr(name, bytes)


def _save_dict_as_json(d, name, zfile):
    """
    Saves the given dict as a json file with the name given
    :param d: The dictionary to save
    :param name: The name of the file to save it as
    :param zfile: The archive to compress to
    """
    zfile.writestr(name, str.encode(json.dumps(d, sort_keys=True, indent=2), 'utf-8'))


def _save_model_and_generate_manifest(model_name, transform_data, zfile, material_data=None, mesh_data=None,
                                      animation_data=None, metadata=None):
    """
    Generates a manifest for a model and saves the data for the model into the zipfile given
    :param model_name: The name of the model given
    :param transform_data: The local transformations made in the scene for the given model
    :param zfile: the zipfile to save encoded data to
    :param material_data: The material data of the model
    :param mesh_data: The mesh data of the model
    :param animation_data: The animation data of the model
    :return: Manifest generated from saving the model into the zipfile
    """
    mod_manifest = {'name': model_name}

    # This will cause the engine to load a default material set for the game.
    # TODO: Check for duplicates in the zip archive... (materials)
    if material_data is None:
        mod_manifest['material'] = None
    else:
        mod_manifest['material'] = {}
        mod_manifest['material']['name'] = material_data['name']

        # If use_engine_mat is set, it will load whatever material in-engine is identified by the 'name' key, or warn
        # the user and load the default material if no material of name exists in engine
        if material_data['use_engine_mat']:
            mod_manifest['material']['location'] = None
        else:
            _save_dict_as_json(material_data, '%s.mat.json' % material_data['name'], zfile)
            mod_manifest['material']['location'] = '%s.mat.json' % material_data['name']

    # Export Mesh data
    if MeshDataKey is None:
        mod_manifest['mesh'] = None
    else:
        # Only set lengths and locations to mesh data that got exported (i.e if only vertices are exported,
        # only set the vertices link up)
        mod_manifest['mesh'] = {}

        if mesh_data[EncodedVertsKey] is None:
            mod_manifest['mesh']['verts'] = None
        else:
            _save_bytes(mesh_data[EncodedVertsKey], '%s.vert.bin' % model_name, zfile)
            mod_manifest['mesh']['verts'] = _generate_mesh_link(mesh_data[EncodedVertsKey], model_name, 'vert')

        if mesh_data[EncodedNormalsKey] is None:
            mod_manifest['mesh']['normals'] = None
        else:
            _save_bytes(mesh_data[EncodedVertsKey], '%s.norm.bin' % model_name, zfile)
            mod_manifest['mesh']['normals'] = _generate_mesh_link(mesh_data[EncodedNormalsKey], model_name, 'norm')

        if mesh_data[EncodedUVsKey] is None:
            mod_manifest['mesh']['uvs'] = None
        else:
            _save_bytes(mesh_data[EncodedVertsKey], '%s.uv.bin' % model_name, zfile)
            mod_manifest['mesh']['uvs'] = _generate_mesh_link(mesh_data[EncodedUVsKey], model_name, 'uv')

        if mesh_data[EncodedIndicesKey] is None:
            mod_manifest['mesh']['ind'] = None
        else:
            _save_bytes(mesh_data[EncodedVertsKey], '%s.ind.bin' % model_name, zfile)
            mod_manifest['mesh']['ind'] = _generate_mesh_link(mesh_data[EncodedIndicesKey], model_name, 'ind')

    # Export animation data
    if animation_data is None:
        mod_manifest['animation'] = None
    else:
        # TODO: Save manifest for animation data once it is done being implemented
        pass

    if metadata is None:
        mod_manifest['metadata'] = None
    else:
        mod_manifest['metadata'] = metadata

    # Export transform data
    mod_manifest['transform'] = {}
    _save_dict_as_json(transform_data, '%s.trans.json' % model_name, zfile)
    mod_manifest['location'] = '%s.trans.json' % model_name

    return mod_manifest


def _save_scene_and_generate_manifest(encoded_data, zfile):
    """
    Saves all encoded data into the zipfile given and generates a manifest json file

    :param encoded_data: The encoded data to generate a manifest from
    :param zfile: The zipfile to save into
    :return: The manifest dict
    """
    # Set what the model data is exported in this archive
    manifest = {}
    manifest['contains_mesh_data'] = encoded_data[MeshDataKey] is not None
    manifest['contains_material_data'] = encoded_data[MaterialDataKey] is not None
    manifest['contains_animation_data'] = encoded_data[AnimationDataKey] is not None
    manifest['contains_metadata'] = encoded_data[MetadataKey] is not None
    manifest['meshes'] = encoded_data[ExportedMeshesKey]

    # TODO: Add CRC checksums and expected lengths for security/integrity (just in case...)

    # Set what models have been exported, and their transformation data, with material/mesh links
    for model in encoded_data[ExportedMeshesKey]:
        mesh = encoded_data[MeshDataKey][model] if encoded_data[MeshDataKey] is not None else None
        mat = encoded_data[MaterialDataKey][model] if encoded_data[MaterialDataKey] is not None else None
        ani = encoded_data[AnimationDataKey][model] if encoded_data[AnimationDataKey] is not None else None
        trans = encoded_data[MeshTransformsKey][model]
        metadata = encoded_data[MetadataKey][model] if encoded_data[MetadataKey] is not None else None

        manifest['%s_data' % model] = _save_model_and_generate_manifest(model, trans, zfile, mat, mesh, ani, metadata)

    # Now save the manifest
    _save_dict_as_json(manifest, 'manifest.json', zfile)


def save_model(encoded_data, filepath):
    """
    Will compress the encoded data, and save to the given filepath
    :param encoded_data: The encoded scene data to save
    :param filepath: The path to save the LZMA compressed .model file

    """
    with zipfile.ZipFile(filepath, 'w', compression=zipfile.ZIP_LZMA) as z:
        _save_scene_and_generate_manifest(encoded_data, z)
