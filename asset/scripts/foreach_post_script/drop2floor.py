import bpy

cdi_tool = globals().get('cdi_obj_measure')

if bpy.context.selected_objects:
    obj = bpy.context.selected_objects[0]

    bound_box = cdi_tool.ObjectBoundingBox(obj)
    print(bound_box.size)
