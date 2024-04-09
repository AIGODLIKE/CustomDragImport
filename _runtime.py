import json
import bpy
from pathlib import Path

from .public_path import AssetDir, get_AssetDir_path
from .wrap_handle import gen_import_op, gen_import_handle
from . import clipboard

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


class CDI_OT_popup_operator(bpy.types.Operator):
    bl_label = "CDI Popup Operator"
    bl_idname = "cdi.popup_operator"

    def filter_files(self, files) -> list[Path]:
        # get the most common extension
        exts = [file.suffix for file in files]
        ext = max(set(exts), key=exts.count)
        return [file for file in files if file.suffix == ext]

    def filter_operator(self, context, bl_file_extensions) -> list[str]:
        split_exts = lambda exts: exts.split(';')
        ops = []
        for handle in G_handles.values():
            if not handle.poll_drop(context): continue
            if bl_file_extensions in split_exts(handle.bl_file_extensions):
                ops.append(handle.bl_import_operator)
        return ops

    def execute(self, context):
        wm = context.window_manager
        with clipboard.clipboard():
            try:
                files = clipboard.get_FILEPATHS()
            except clipboard.ClipetteWin32ClipboardError:
                self.report({'ERROR'}, 'Clipboard is empty!')
                return {'CANCELLED'}

        files = [Path(file) for file in files]
        files = self.filter_files(files)

        if not files:
            return {'CANCELLED'}

        directory = files[0].parent
        bl_file_extensions = files[0].suffix
        clipboard_files = ';'.join([file.name for file in files])

        def draw(_self, _context):
            for bl_idname in self.filter_operator(context, bl_file_extensions):
                op = _self.layout.operator(bl_idname)
                op.directory = str(directory)
                op.clipboard_files = clipboard_files

        wm.popup_menu(draw)

        return {'FINISHED'}


def register():
    try:
        unregister()
    except:
        pass

    ensure_op_handles()

    import bpy
    for op in G_ops.values():
        bpy.utils.register_class(op)
    for handle in G_handles.values():
        bpy.utils.register_class(handle)

    bpy.utils.register_class(CDI_OT_popup_operator)


def unregister():
    import bpy
    for op in G_ops.values():
        bpy.utils.unregister_class(op)
    for handle in G_handles.values():
        bpy.utils.unregister_class(handle)

    bpy.utils.unregister_class(CDI_OT_popup_operator)

    G_ops.clear()
    G_handles.clear()
