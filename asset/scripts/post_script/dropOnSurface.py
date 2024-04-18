import bpy
from mathutils import Vector
from cdi_tool.boundingBox import ObjectBoundingBox, ObjectsBoundingBox, C_OBJECT_TYPE_HAS_BBOX
from cdi_tool.raycast import ray_cast, exclude_ray_cast

event = globals().get('event')

selected_objs = [obj for obj in bpy.context.selected_objects if obj.type in C_OBJECT_TYPE_HAS_BBOX]
bboxs = [ObjectBoundingBox(obj, is_local=False) for obj in selected_objs]

if len(bboxs) != 0:
    objs_A = ObjectsBoundingBox(bboxs)
    bottom = objs_A.get_bottom_center()
    normal = Vector((0, 0, 1))

    with exclude_ray_cast(selected_objs):
        result, target_obj, view_point, world_loc, normal, location, matrix = ray_cast(bpy.context, event)
        if result:
            normal = normal.normalized()
            world_loc = location

    # move
    vec = world_loc - bottom
    for obj in  selected_objs:
        obj.location += vec
