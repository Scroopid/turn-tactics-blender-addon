import bpy
import bmesh
import mathutils
import numpy as np

EncodedVertsKey = 'verts'
EncodedNormalsKey = 'normals'
EncodedUVsKey = 'uvs'
EncodedIndicesKey = 'indices'
Epsilon = 0.0001

class TTVertex(object):
    def __init__(self, co, norm, uv=None):
        self.loc = np.array(co, dtype=np.float32)
        self.norm = np.array(norm, dtype=np.float32)
        self.uv = np.array(uv, dtype=np.float32) if uv is not None else np.zeros(2, dtype=np.float32)

    def __eq__(self, other):
        if isinstance(other, TTVertex):
            abs_loc = np.sum(np.absolute(self.loc - other.loc))
            abs_norm = np.sum(np.absolute(self.norm - other.norm))
            abs_uv = np.sum(np.absolute(self.uv - other.uv))

            return abs_loc < Epsilon and abs_norm < Epsilon and abs_uv < Epsilon

        return False

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
    export_uvs = True
    export_norms = True

    # Validate mesh options
    uv_layer = bmesh_obj.loops.layers.uv.active
    if uv_layer is None:
        bmesh_obj.free()
        del bmesh_obj
        raise RuntimeError('Cannot encode mesh without UV when export_opt specifies to export UVs')

    # Create kd-tree and store all of the vertices in it, and flatten out coordinates
    kd = mathutils.kdtree.KDTree(len(bmesh_obj.verts))
    index_trans = []
    for face in bmesh_obj.faces:
        for loop, vert in zip(face.loops, face.verts):
            index_trans.append(vert.index)
    kd.balance()

    # Create dict to store all of the data to encode
    data = {
        EncodedVertsKey: [v.co for v in bmesh_obj.verts],
        EncodedNormalsKey: [v.normal for v in bmesh_obj.verts]
    }

    bmesh_obj.free()
    del bmesh_obj

if __name__ == "__main__":
    obj = [obj.data for obj in bpy.context.scene.objects if obj.type == 'MESH'][0]
    encode_mesh_data(obj, 'All')