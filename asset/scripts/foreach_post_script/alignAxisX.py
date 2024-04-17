import bpy

index = globals().get('index')

for obj in bpy.context.selected_objects:
    obj.location.x += index * 2
