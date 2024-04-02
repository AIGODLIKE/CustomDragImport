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
    for index, (label, values) in enumerate(datas.items()):
        new_idname = f'cdi.import_{index}'
        op = gen_import_op(
            bl_label=label,
            bl_idname=new_idname,
            bl_import_operator=values['bl_import_operator'],
            bl_file_extensions=values['bl_file_extensions'],
            operator_context=values.get('operator_context', 'INVOKE_DEFAULT'),
        )
        # external scripts
        op.pre_script = values.get('pre_script')
        op.post_script = values.get('post_script')
        op.foreach_pre_script = values.get('foreach_pre_script')
        op.foreach_post_script = values.get('foreach_post_script')

        # handle
        handle = gen_import_handle(
            bl_label=label,
            bl_import_operator=new_idname,
            bl_idname=f"CDI_FH_handle{index}",
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
