import bpy
from mathutils import Vector


def create_tmp_parent(bottom_loc: Vector, selected_objs: list[bpy.types.Object], axis='Z',
                         invert_axis: bool = False)->bpy.types.Object:
    offset = 0.001
    if invert_axis: offset = -offset

    empty = bpy.data.objects.new('Empty', None)
    empty.name = 'TMP_PARENT'
    empty.empty_display_type = 'PLAIN_AXES'
    empty.empty_display_size = 0
    empty.location = bottom_loc
    z = getattr(empty.location, axis.lower())
    setattr(empty.location, axis.lower(), z - offset)

    rot_obj = bpy.context.object
    empty.rotation_euler = rot_obj.rotation_euler

    def create_parent_const(obj):
        con = obj.constraints.new('CHILD_OF')
        con.name = 'TMP_PARENT'
        con.use_rotation_x = True
        con.use_rotation_y = True
        con.use_rotation_z = True
        con.target = empty
        obj.select_set(False)

    for obj in selected_objs:
        if obj.parent and obj.parent in selected_objs:
            obj.select_set(False)
            continue
        # loop over the constraints in each object
        create_parent_const(obj)
    # if obj is not mesh
    if rot_obj not in selected_objs:
        create_parent_const(rot_obj)
        rot_obj.select_set(True)

    bpy.context.collection.objects.link(empty)
    bpy.context.view_layer.objects.active = rot_obj
    return empty


def apply_tmp_parent(tmp_parent: bpy.types.Object, selected_objs: list[bpy.types.Object]):
    if not tmp_parent: return

    # apply constraints
    def apply_const(obj):
        obj.select_set(True)
        tmp_mx = obj.matrix_world.copy()
        for con in obj.constraints:
            if con.name == 'TMP_PARENT' and con.type == 'CHILD_OF':
                obj.constraints.remove(con)

        obj.matrix_world = tmp_mx

    for obj in selected_objs:
        apply_const(obj)

    if bpy.context.object not in selected_objs:
        apply_const(bpy.context.object)

    # remove empty
    bpy.data.objects.remove(tmp_parent)


def align_obj2normal(normal: Vector, obj: bpy.types.Object, axis: str = 'Z', invert_axis=False):
    """清除除了local z以外轴向的旋转"""
    v = -1 if invert_axis else 1
    if axis == 'Z':
        z = Vector((0, 0, v))
    elif axis == 'Y':
        z = Vector((0, v, 0))
    else:
        z = Vector((v, 0, 0))

    rotate_clear = obj.matrix_local.to_quaternion()

    for a in ['x', 'y', 'z']:
        if a == axis.lower(): continue
        # clear
        setattr(rotate_clear, a, 0)

    rotate_clear = rotate_clear.to_matrix()
    try:
        offset_q = z.rotation_difference(normal)
    except:
        offset_q = Vector((0, 0, 1)).rotation_difference(z)

    obj.rotation_euler = (offset_q.to_matrix() @ rotate_clear).to_euler()
