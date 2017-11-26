import bpy

def exportModel(context, config):
    print('This will run an export to %s with a config of %s' % (config['file_path'], repr(config)))
