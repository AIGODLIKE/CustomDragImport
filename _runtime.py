import json
from .public_path import AssetDir, get_AssetDir_path
from .wrap_handle import gen_import_op, gen_import_handle

G_ops = {}
G_handles = {}


def ensure_op_handles():
    datas = {}
    # get configs dict from path
    for file in get_AssetDir_path(AssetDir.CONFIG).iterdir():
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            datas.update(data)
    # register in op
    for label, values in datas.items():
        op = gen_import_op(
            bl_label=label,
            bl_idname=values['bl_idname'],
            bl_import_operator=values['bl_import_operator'],
            bl_file_extensions=values['bl_file_extensions']
        )
        if 'pre_script' in values:
            op.pre_script = values['pre_script']
        if 'post_script' in values:
            op.post_script = values['post_script']

        handle = gen_import_handle(
            bl_label=label,
            bl_import_operator=values['bl_idname'],
            bl_idname=values['bl_idname'] + '_handle',
            bl_file_extensions=values['bl_file_extensions'],
            poll_area=values['poll_area']
        )

        G_ops.update({label: op})
        G_handles.update({label: handle})

    # print(G_ops, G_handles)


def register():
    ensure_op_handles()

    import bpy
    for op in G_ops.values():
        bpy.utils.register_class(op)
    for handle in G_handles.values():
        bpy.utils.register_class(handle)


def unregister():
    import bpy
    for op in G_ops.values():
        bpy.utils.unregister_class(op)
    for handle in G_handles.values():
        bpy.utils.unregister_class(handle)

    G_ops.clear()
    G_handles.clear()
