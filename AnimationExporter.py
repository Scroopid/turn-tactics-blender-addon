def _is_mesh_animation_supported(bl_obj, context):
    """
    Checks over objects animations and ensures that they are correctly rigged and animated for the engine.

    This is just a placeholder til animation features are integrated and researched
    :param bl_obj: The blender object to validate for exporting animations
    :param context: The blender context
    :return: If the mesh's animations are supported
    """
    return True


def encode_animation_data(bl_obj):
    """
    This encodes all of the animation data in the model

    This method is a placeholder for now, doesn't do anything until animations are in engine

    :param bl_obj: The blender object to pull animation data from
    :return: The encoded animation data
    """
    pass
