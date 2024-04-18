import bpy
import os

files = globals().get('files')
directory = globals().get('directory')
event = globals().get('event')

mouse_x, mouse_y = bpy.context.space_data.cursor_location

if tree := bpy.context.space_data.edit_tree:
    if bpy.context.area.ui_type == 'ShaderNodeTree':
        idname = 'ShaderNodeTexImage'
    elif bpy.context.area.ui_type == 'GeometryNodeTree':
        idname = 'GeometryNodeImageTexture'
    else:
        idname = None

    if idname:
        for i, file in enumerate(files):
            filepath = os.path.join(directory, file)
            img = bpy.data.images.load(filepath)
            node = tree.nodes.new(idname)
            node.image = img
            node.location = mouse_x + i * 50, mouse_y + i * 10
