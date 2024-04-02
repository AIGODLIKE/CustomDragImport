import bpy
import os
from pathlib import Path
from contextlib import contextmanager

from .public_path import get_ScriptFile


class DynamicImport():
    # must have
    directory: bpy.props.StringProperty(subtype='FILE_PATH', options={'SKIP_SAVE'})
    files: bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement, options={'SKIP_SAVE'})

    # pass in
    bl_file_extensions: str
    bl_import_operator: str
    operator_context:str
    # custom
    kwargs: dict
    pre_script: str
    post_script: str
    foreach_pre_script: str
    foreach_post_script: str

    def execute(self, context):
        if not self.directory:
            return {'CANCELLED'}

        with self._process_scripts(self.pre_script, self.post_script,
                                   {'directory': self.directory, 'files': self.files}):
            select_objs = []
            select_nodes = []

            for file in self.files:
                if not file.name.endswith(self.bl_file_extensions): continue

                filepath = os.path.join(self.directory, file.name)
                cat, name = self.bl_import_operator.split('.')
                op_callable = getattr(getattr(bpy.ops, cat), name)

                with self._process_scripts(self.foreach_pre_script, self.foreach_post_script, {'filepath': filepath}):
                    if self.kwargs:
                        op_callable(self.operator_context,filepath=filepath, **self.kwargs)
                    else:
                        op_callable(self.operator_context,filepath=filepath)

                    self.report({'INFO'}, 'Imported: ' + file.name)

                # restore select
                if hasattr(context, 'selected_objects'):
                    select_objs += list(context.selected_objects)
                if hasattr(context, 'selected_nodes'):
                    select_nodes += list(context.selected_nodes)
            # just make it behavior like blender's default drag
            for obj in select_objs:
                obj.select_set(True)
            if hasattr(context, 'selected_nodes'):
                tree = context.space_data.node_tree
                for node in select_nodes:
                    node.select = True
                if select_nodes:
                    tree.nodes.active = select_nodes[0]

        return {'FINISHED'}

    def invoke(self, context, event):
        if self.directory:
            return self.execute(context)
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    @contextmanager
    def _process_scripts(self, pre: str | None, post: str | None, kwargs: dict | None = None):
        if pre is not None:
            self._exec_script(pre, kwargs)
        yield
        if post is not None:
            self._exec_script(post, kwargs)

    def _exec_script(self, script: str, kwargs: dict):
        file = get_ScriptFile(script)
        if not file.exists(): return
        with open(file, 'r', encoding='utf-8') as f:
            data = f.read()
            # pass in kwargs
            kwargs = kwargs if kwargs else {}
            exec(data, globals(), locals())


class DynamicPollDrop():
    poll_region: str = 'WINDOW'
    poll_area: str = 'VIEW_3D'

    @classmethod
    def poll_drop(self, context):
        return (context.region and context.region.type == self.poll_region
                and context.area and context.area.type == self.poll_area)


def gen_import_op(bl_idname, bl_label, bl_import_operator: str, bl_file_extensions,operator_context: str = 'INVOKE_DEFAULT',
                  kwargs: dict = None,
                  pre_script: str = None,
                  post_script: str = None,
                  foreach_pre_script: str = None,
                  foreach_post_script: str = None):
    op = type(bl_idname,
              (bpy.types.Operator, DynamicImport),
              {
                  "bl_idname": bl_idname,
                  "bl_label": bl_label,
                  "bl_import_operator": bl_import_operator,
                  "bl_file_extensions": bl_file_extensions,
                  "operator_context":operator_context,
                  # custom
                  "kwargs": kwargs,
                  "invoke": DynamicImport.invoke,
                  "execute": DynamicImport.execute,
                  "pre_script": pre_script,
                  "post_script": post_script,
                  "foreach_pre_script": foreach_pre_script,
                  "foreach_post_script": foreach_post_script
              }
              )

    return op


def gen_import_handle(bl_idname: str, bl_label: str, bl_import_operator: str, bl_file_extensions: str,
                      poll_region: str = 'WINDOW', poll_area='VIEW_3D'):
    handle = type(bl_idname,
                  (bpy.types.FileHandler, DynamicPollDrop),
                  {
                      "bl_idname": bl_idname,
                      "bl_label": bl_label,
                      "bl_import_operator": bl_import_operator,
                      "bl_file_extensions": bl_file_extensions,
                      # custom
                      "poll_region": poll_region,
                      "poll_area": poll_area,
                      "poll_drop": DynamicPollDrop.poll_drop
                  }
                  )

    return handle
