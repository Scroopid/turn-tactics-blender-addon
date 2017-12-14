import struct

import bmesh
import numpy as np

from . import ExportOptions

EncodedVertsKey = 'verts'
EncodedNormalsKey = 'normals'
EncodedUVsKey = 'uvs'
EncodedIndicesKey = 'indices'
EncodedVertsLengthKey = 'length'
EncodedTrianglesCount = 'number_triangles'
Epsilon = 0.0001
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


def _convert_bmesh(bmesh_obj, export_uvs, uv_layer):
    """
    Converts the bmesh to an intermediate format for conversion into engine format
    :param bmesh_obj: The bmesh object to convert
    :param export_uvs: If we should export UVs from this object
    :param uv_layer: The UV layer to export.
    :return:
    """
    # Initialize intermediate format
    index_trans = []
    norms = []
    verts = []
    uvs = [None for _ in range(len(bmesh_obj.verts))]
    trans_lists = [[] for _ in range(len(bmesh_obj.verts))]

    # Initialize norms and verts to vertices in the model
    for vert in bmesh_obj.verts:
        norm = np.array([vert.normal.x, vert.normal.y, vert.normal.z])
        v = np.array([vert.co.x, vert.co.y, vert.co.z])
        verts.append(v)
        norms.append(norm)

    for face in bmesh_obj.faces:
        for loop, vert in zip(face.loops, face.verts):
            # If we are exporting UV's
            if export_uvs:
                # See if the uv doesnt exist
                uv = np.array([loop[uv_layer].uv.x, loop[uv_layer].uv.y])

                # If there is no UV recorded yet, just set the current index to this one
                if uvs[vert.index] is None:
                    uvs[vert.index] = uv
                else:
                    exst = uvs[vert.index]
                    s = sum([abs(x - y) for (x, y) in zip(exst, uv)])
                    if s > Epsilon:
                        # We need to check the trans_list for a possible similar UV
                        common_uvs = [(i, uvs[i]) for i in trans_lists[vert.index]]
                        diffs = [(other[0], np.sum(np.absolute(uv - other[1]))) for other in common_uvs]
                        matching = list(filter(lambda x: x[1] < Epsilon, diffs))

                        if len(matching) > 0:
                            ind, _ = matching[0]
                            index_trans.append(ind)
                        else:
                            # Copy UV, vert, norm into new index
                            newTrans = len(verts)
                            verts.append(verts[vert.index])
                            norms.append(norms[vert.index])
                            uvs.append(uv)
                            trans_lists[vert.index].append(newTrans)
            else:
                # Just add to index_trans list
                index_trans.append(vert.index)

    return index_trans, norms, uvs, verts


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
    bmesh_obj = _prepare_mesh_for_export(bl_obj.data)

    export_verts = _export_verts_lu[export_opt]
    export_uvs = _export_uvs_lu[export_opt]
    export_norms = _export_norms_lu[export_opt]

    # Validate mesh options
    uv_layer = bmesh_obj.loops.layers.uv.active
    if export_uvs and uv_layer is None:
        bmesh_obj.free()
        del bmesh_obj
        raise RuntimeError('Cannot encode mesh without UV when export_opt specifies to export UVs')

    index_trans, norms, uvs, verts = _convert_bmesh(bmesh_obj, export_uvs, uv_layer)

    bmesh_obj.free()
    del bmesh_obj

    # Encode all of the mesh data into LE binary format
    enc_vert = bytearray(len(verts) * 12) if export_verts else None
    enc_norm = bytearray(len(norms) * 12) if export_norms else None
    enc_uv = bytearray(len(uvs) * 8) if export_uvs else None
    enc_ind = bytearray(len(index_trans) * 4)

    for i in range(len(verts)):
        if export_verts:
            struct.pack_into("<fff", enc_vert, i * 12, verts[i][0], verts[i][1], verts[i][2])
        if export_norms:
            struct.pack_into("<fff", enc_norm, i * 12, norms[i][0], verts[i][1], verts[i][2])
        if export_uvs:
            struct.pack_into("<ff", enc_uv, i * 8, uvs[i][0], uvs[i][1])

    for i in range(len(index_trans)):
        struct.pack_into("<I", enc_ind, i * 4, index_trans[i])

    # Create dict to store all of the data to encode
    return {
        EncodedVertsLengthKey: int(len(verts) / 3),
        EncodedTrianglesCount: int(len(index_trans) / 3),
        EncodedVertsKey: enc_vert,
        EncodedNormalsKey: enc_norm,
        EncodedUVsKey: enc_uv,
        EncodedIndicesKey: enc_ind
    }
