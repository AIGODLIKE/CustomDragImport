import bpy
import os
import addon_utils

files = globals().get('files')
directory = globals().get('directory') + '\\'

if addon_utils.check('node_wrangler')[1] is False:
    addon_utils.enable('node_wrangler')

tree = bpy.context.space_data.edit_tree
if tree:
    if bpy.context.area.ui_type == 'ShaderNodeTree':
        fs = [{'name': file} for file in files]
        fp = directory + files[0]
        bpy.ops.node.nw_add_textures_for_principled(filepath=fp,
                                                    directory=directory,
                                                    files=fs, relative_path=True)
