import colorsys

import bpy

DiffusePassKey = 'diffuse'
SpecularPassKey = 'specular'
AmbientPassKey = 'ambient'
ShadowPassKey = 'shadow'
_diffuse_shader_lu = {
    'LAMBERT': 'lambert',
    'OREN_NAYAR': 'oren_nayar',
    'TOON': 'toon',
    'MINNAERT': 'minnaert',
    'FRESNEL': 'fresnel'
}

_specular_shader_lu = {
    'COOKTORR': 'cook_torr',
    'PHONG': 'phong',
    'BLINN': 'blinn',
    'TOON': 'toon',
    'WARDISO': 'ward_anisotropic'
}

_engine_blend_op = {
    'MIX': 'mix',  # Blends elements by dst = src*srcFactor + dst*(1-srcFactor),
    'ADD': 'add',  # dst = src*srcFactor + dst
    'MULTIPLY': 'mult',  # dst = src*srcFactor*dst
    'SUBTRACT': 'sub',  # dst = dst - src*srcFactor
    'SCREEN': 'screen',  # dst = 1 - (1 - dst)*(1 - src*srcFactor),
    'DIVIDE': 'div',  # dst = dst/src,
    'DIFFERENCE': 'diff',  # dst = src*srcFactor - dst
    'DARKEN': 'min',  # dst = { min(dst_comp, src_comp) | (dst_comp, src_comp) in (dst, src) }
    'LIGHTEN': 'max',  # dst = { max(dst_comp, src_comp) | (dst_comp, src_comp) in (dst, src) }
    'OVERLAY': 'overlay',  # dst = if src_comp < .5 then 2*src*dst else 1 - 2(1-src)(1-dst)
    'DODGE': 'color_dodge',  # dst = dst/(src^0xff <- Inverting color component)
    'BURN': 'burn',  # dst = ((dst^0xff)/src)^0xff
    'HUE': 'hue',  # This is dependant on color spaces used for textures....
    'SATURATION': 'sat',  # This is dependant on color spaces used....
    'VALUE': 'lum',  # Luminance style, dependant on color spaces used....
    'COLOR': 'color',  # Color blend, dependant on color space used...
    'SOFT_LIGHT': 'soft',  # uses w3c method of soft_light blend op
    'LINEAR_LIGHT': 'linear_light'  # inverse of layers on overlay
}


def _get_diffuse_shader_config(mat):
    """
    Gets the parameter specific for diffuse shader type like roughness for oren-nayar and intensity of a lambert shader.

    :param mat: The material in blender to translate to engine format config
    :return: dict containning engine-type parameters for the diffuse shader for the material given.
    """
    try:
        diff_shader_type = _diffuse_shader_lu[mat.diffuse_shader]
    except:
        raise RuntimeError("Shader '%s' not supported yet..." % mat.diffuse_shader)

    if diff_shader_type == 'lambert':
        return {
            'intensity': mat.diffuse_intensity
        }
    elif diff_shader_type == 'oren_nayar':
        return {
            'intensity': mat.diffuse_intensity,
            'roughness': mat.roughness
        }
    elif diff_shader_type == 'toon':
        return {
            'intensity': mat.diffuse_intensity,
            'size': mat.diffuse_toon_size,
            'smooth': mat.diffuse_toon_smooth
        }
    elif diff_shader_type == 'minnaert':
        return {
            'intensity': mat.diffuse_intensity,
            'darkness': mat.darkness
        }
    elif diff_shader_type == 'fresnel':
        return {
            'intensity': mat.diffuse_intensity,
            'fresnel': mat.diffuse_fresnel,
            'fresnel_factor': mat.diffuse_fresnel_factor
        }


def _get_specular_shader_config(mat):
    """
    Gets the parameter specific for specular shader type like roughness for oren-nayar and intensity of a lambert shader.

    :param mat: The material in blender to translate to engine format config
    :return: dict containning engine-type parameters for the diffuse shader for the material given.
    """
    try:
        spec_shader_type = _specular_shader_lu[mat.specular_shader]
    except:
        raise RuntimeError("Shader '%s' not supported yet..." % mat.specular_shader)

    if spec_shader_type == 'cook_torr' or spec_shader_type == 'phong':
        return {
            'intensity': mat.specular_intensity,
            'hardness': mat.specular_hardness
        }
    elif spec_shader_type == 'blinn':
        return {
            'intensity': mat.specular_intensity,
            'hardness': mat.specular_hardness,
            'ior': mat.specular_ior
        }
    elif spec_shader_type == 'toon':
        return {
            'intensity': mat.specular_intensity,
            'size': mat.specular_toon_size,
            'smooth': mat.specular_toon_smooth
        }
    elif spec_shader_type == 'ward_anisotropic':
        return {
            'intensity': mat.diffuse_intensity,
            'slope': mat.specular_slope
        }


def _get_color_type(mat, for_stage):
    """
    Gets the type of color specified in color parameter for the stage given. This will be ramp or static

    :param mat: The material to get the color type for
    :param for_stage: For which stage (diffuse, specular)
    :return: ramp if using ramp option in blender, static if not. If invalid for_stage is provided, None is returned
    """
    if for_stage == DiffusePassKey:
        return 'ramp' if mat.use_diffuse_ramp else 'static'
    elif for_stage == SpecularPassKey:
        return 'ramp' if mat.use_specular_ramp else 'static'

    print('No stage %s in material, assuming static color' % str(for_stage))
    return None


def _get_color_ramp_elements(ramp, resolution):
    """
    Converts the blender ramp elements to a game-engine format. This will sample the color ramp *resolution* times evenly,
    then in engine, it will use linear interpolation across the evaluated points.

    :param ramp: The color ramp to extract elements from
    :param resolution: Amount of samples to get. int
    :return: Engine formatted color ramp
    """
    points = []
    for step in range(resolution):
        pos = float(step) / float(resolution)
        color = ramp.evaluate(pos)
        points.append([color[0], color[1], color[2], color[3]])

    # Convert all points to RGB if they aren't already
    if ramp.color_mode == 'HSV' or ramp.color_mode == 'HSL':
        rgb_points = []
        for point in points:
            if ramp.color_mode == 'HSV':
                conv = colorsys.hsv_to_rgb(point[0], point[1], point[2])
            else:
                conv = colorsys.hls_to_rgb(point[0], point[2], point[1])

            rgb_point = [conv[0], conv[1], conv[2], point[3]]  # Pick up Alpha from original point
            rgb_points.append(rgb_point)
        return rgb_points
    if ramp.color_mode == 'RGB':
        return points

    raise RuntimeError("Invalid color mode %s for ramp" % str(ramp.color_mode))


def _get_color_prop(mat, for_stage):
    """
    Returns the color property for the stage given. This will either be an engine-formatted ramp color scheme
    or just a static color. If an improper stage is given, an exception will be raised

    :param mat: The material to process
    :param for_stage: For which stage to process it.
    :return: dict containing engine configuration of the color type.
    """
    color_type = _get_color_type(mat, for_stage)
    if color_type is None:
        raise RuntimeError("Invalid stage '%s' given" % str(for_stage))
    elif color_type == 'static':
        return {
            'color': [mat.diffuse_color[0], mat.diffuse_color[1], mat.diffuse_color[2]]
        }
    elif color_type == 'ramp':
        return {
            'ramp_blend_op': _engine_blend_op[mat.diffuse_ramp_blend],
            'blend_factor': mat.diffuse_ramp_factor,
            'colors': _get_color_ramp_elements(mat.diffuse_ramp, 100)
        }


def encode_material_data(obj, context):
    """
    Encodes the active material on the object into a game-engine format

    :param obj: Object to pull active material from
    :param context: Blender context that the object came from
    :return: dict with material encoded in engine format
    """
    # TODO: Export textures us
    print(obj.name)

    mat = obj.materials[0]
    eng_mat = {}
    eng_mat['name'] = mat.name
    eng_mat['type'] = mat.type
    print(mat.name)
    print(mat.type)

    # Diffuse props
    eng_mat['diffuse'] = {}
    eng_mat['diffuse']['type'] = _diffuse_shader_lu[mat.diffuse_shader]
    eng_mat['diffuse']['color_type'] = _get_color_type(mat, DiffusePassKey)
    eng_mat['diffuse']['color_props'] = _get_color_prop(mat, DiffusePassKey)
    eng_mat['diffuse']['shader_config'] = _get_diffuse_shader_config(mat)

    # Specular props
    eng_mat['specular'] = {}
    eng_mat['specular']['type'] = _specular_shader_lu[mat.specular_shader]
    eng_mat['specular']['color_type'] = _get_color_type(mat, SpecularPassKey)
    eng_mat['specular']['color_props'] = _get_color_prop(mat, SpecularPassKey)
    eng_mat['specular']['shader_config'] = _get_specular_shader_config(mat)

    # Shadow Props
    eng_mat['shadow'] = {}
    eng_mat['shadow']['cast_shadows'] = mat.use_cast_shadows or mat.use_cast_shadows_only or mat.use_cast_buffer_shadows
    eng_mat['shadow']['receive_shadows'] = mat.use_shadows or mat.use_transparent_shadows or mat.use_only_shadow
    eng_mat['shadow']['buffer_bias'] = mat.shadow_buffer_bias

    return eng_mat


if __name__ == "__main__":
    obj = bpy.context.scene.objects.active.data
    encode_material_data(obj, bpy.context)
