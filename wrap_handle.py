import bpy
import os
from pathlib import Path
from contextlib import contextmanager

from .public_path import get_ScriptFile


def empty_op(operator_context: str, filepath, kwargs=None):
    print('Invalid/Empty Operator: ', operator_context, filepath, kwargs)


class DynamicImport():
    # must have
    directory: bpy.props.StringProperty(subtype='FILE_PATH', options={'SKIP_SAVE'})
    files: bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement, options={'SKIP_SAVE'})
    clipboard_files: bpy.props.StringProperty(options={'SKIP_SAVE'})  # file names join with ;
    # pass in
    bl_file_extensions: str
    bl_import_operator: str
    operator_context: str
    # custom
    kwargs: dict
    pre_script: str
    post_script: str
    foreach_pre_script: str
    foreach_post_script: str

    def execute(self, context):
        if not self.directory:
            return {'CANCELLED'}
        if len(self.files) == 0:
            files = self.clipboard_files.split(';')
        else:
            files = [file.name for file in self.files]

        with self._process_scripts(self.pre_script, self.post_script,
                                   {'directory': self.directory, 'files': files,'event':self.event}):
            select_objs = []
            select_nodes = []

            for index, file in enumerate(files):
                has_ext = self._check_extension(file, self.bl_file_extensions)
                if not has_ext: continue

                filepath = os.path.join(self.directory, file)
                try:
                    cat, name = self.bl_import_operator.split('.')
                    op_callable = getattr(getattr(bpy.ops, cat), name)
                except (ValueError, AttributeError):  # user can empty the operator
                    self.report({'WARNING'}, 'Invalid/Empty Operator: ' + self.bl_import_operator)
                    op_callable = empty_op

                with self._process_scripts(self.foreach_pre_script, self.foreach_post_script,
                                           {'filepath': filepath, 'index': index,'event':self.event,
                                            'selected_objects': select_objs,
                                            'selected_nodes': select_nodes
                                            }):
                    if self.kwargs:
                        op_callable(self.operator_context, filepath=filepath, **self.kwargs)
                    else:
                        op_callable(self.operator_context, filepath=filepath)

                    self.report({'INFO'}, 'Imported: ' + file)

                # restore select
                if hasattr(context, 'selected_objects'):
                    select_objs.append(list(context.selected_objects))
                if hasattr(context, 'selected_nodes'):
                    select_nodes.append(list(context.selected_nodes))
            # just make it behavior like blender's default drag
            for obj_list in select_objs:
                for obj in obj_list:
                    obj.select_set(True)
            if hasattr(context, 'selected_nodes'):
                tree = context.space_data.node_tree
                for node_list in select_nodes:
                    for node in node_list:
                        node.select = True
                if select_nodes:
                    tree.nodes.active = select_nodes[0][0]

        return {'FINISHED'}

    def invoke(self, context, event):
        self.event = event
        if self.directory:
            return self.execute(context)
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    @contextmanager
    def _process_scripts(self, pre: str | None, post: str | None, kwargs: dict):
        if pre is not None:
            self._exec_script(pre, kwargs)
        yield
        if post is not None:
            self._exec_script(post, kwargs)

    def _exec_script(self, script: str, kwargs: dict):
        scripts = script.split(';')
        for s in scripts:
            file = get_ScriptFile(s)
            if not file or not file.exists(): return
            with open(file, 'r', encoding='utf-8') as f:
                data = f.read()
                # pass in kwargs
                exec(data, {**kwargs})

    def _check_extension(self, filename, ext_str: str) -> bool:
        if ';' not in ext_str:
            return filename.endswith(ext_str)
        else:
            exts = ext_str.split(';')
            for ext in exts:
                if filename.endswith(ext): return True
            return False


class DynamicPollDrop():
    poll_region: str = 'WINDOW'
    poll_area: str = 'VIEW_3D'

    @classmethod
    def poll_drop(self, context):
        return (context.region and context.region.type == self.poll_region
                and context.area and context.area.type == self.poll_area)


def gen_import_op(bl_idname, bl_label, bl_import_operator: str, bl_file_extensions,
                  operator_context: str = 'INVOKE_DEFAULT',
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
                  "operator_context": operator_context,
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
