import bpy
import bmesh
import mathutils
import numpy as np

EncodedVertsKey = 'verts'
EncodedNormalsKey = 'normals'
EncodedUVsKey = 'uvs'
EncodedIndicesKey = 'indices'
EncodedVertsLengthKey = 'length'
EncodedTrianglesCount = 'number_triangles'
Epsilon = 0.0001

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

    export_verts = True
    export_uvs = False
    export_norms = True

    # Validate mesh options
    uv_layer = bmesh_obj.loops.layers.uv.active
    if export_uvs and uv_layer is None:
        bmesh_obj.free()
        del bmesh_obj
        raise RuntimeError('Cannot encode mesh without UV when export_opt specifies to export UVs')

    index_trans, norms, uvs, verts = _convert_bmesh(bmesh_obj, export_uvs, uv_layer)

    # Create dict to store all of the data to encode
    data = {
        EncodedVertsLengthKey: int(len(verts)/3),
        EncodedTrianglesCount: int(len(index_trans)/3),
        EncodedVertsKey: [v.co for v in bmesh_obj.verts],
        EncodedNormalsKey: [v.normal for v in bmesh_obj.verts]
    }

    bmesh_obj.free()
    del bmesh_obj


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
                        match_ind = None
                        common_uvs = [(i, uvs[i]) for i in trans_lists[vert.index]]
                        diffs = [(other[0], np.sum(np.absolute(uv - other[1]))) for other in common_uvs]
                        matching = filter(lambda x: x[1] < Epsilon, diffs)
                        if len(matching > 0):
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


if __name__ == "__main__":
    obj = bpy.context.scene.objects.active.data
    encode_mesh_data(obj, 'All')
