import bpy
from pathlib import Path

cdi_tool = globals().get('cdi_tool')
filepath = globals().get('filepath')

# get file name
fp = Path(filepath)
name = fp.stem
# create coll
old_coll = bpy.context.collection
coll = bpy.data.collections.new(name)
bpy.context.scene.collection.children.link(coll)
# link selected objects to collection
for obj in bpy.context.selected_objects:
    old_coll.objects.unlink(obj)
    coll.objects.link(obj)
