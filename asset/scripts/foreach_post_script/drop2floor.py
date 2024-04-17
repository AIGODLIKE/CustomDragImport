import bpy
from cdi_tool.boundingBox import ObjectBoundingBox, ObjectsBoundingBox, C_OBJECT_TYPE_HAS_BBOX
from cdi_tool.debugLog import DebugLog

logger = DebugLog()

selected_objs = [obj for obj in bpy.context.selected_objects if obj.type in C_OBJECT_TYPE_HAS_BBOX]
bboxs = [ObjectBoundingBox(obj, is_local=False) for obj in selected_objs]

if len(bboxs) != 0:
    objs_A = ObjectsBoundingBox(bboxs)
    bottom = objs_A.get_bottom_center()

    for obj in selected_objs:
        obj.location.z -= bottom[2]
