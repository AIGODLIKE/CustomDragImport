import bpy
from bpy.props import StringProperty, EnumProperty, BoolProperty, IntProperty, CollectionProperty

from .public_path import AssetDir, get_AssetDir_path, get_ScriptDir

area_type = {
    'VIEW_3D': '3D View',
    'IMAGE_EDITOR': 'Image Editor',
    'NODE_EDITOR': 'Node Editor',
    'TEXT_EDITOR': 'Text Editor',
}

scripts_types = [
    'pre_script',
    'post_script',
    'foreach_pre_script',
    'foreach_post_script'
]

operator_context = [
    'INVOKE_DEFAULT',
    # 'INVOKE_REGION_WIN',
    # 'INVOKE_REGION_CHANNELS',
    # 'INVOKE_REGION_PREVIEW',
    # 'INVOKE_AREA',
    # 'INVOKE_SCREEN',
    'EXEC_DEFAULT',
    # 'EXEC_REGION_WIN',
    # 'EXEC_REGION_CHANNELS',
    # 'EXEC_REGION_PREVIEW',
    # 'EXEC_AREA',
    # 'EXEC_SCREEN',
]


class CDI_ConfigItem(bpy.types.PropertyGroup):
    name: StringProperty(name='Name', default='New Importer')
    bl_import_operator: StringProperty(name='Operator', default='')
    bl_file_extensions: StringProperty(name='File Extension', default='.txt')
    poll_area: EnumProperty(default='VIEW_3D', name='Area',
                            items=[(k, v, '') for k, v in area_type.items()], )
    # custom
    pre_script: StringProperty(name='Before Import all')
    post_script: StringProperty(name='After Import all')
    foreach_pre_script: StringProperty(name='Before Import one file')
    foreach_post_script: StringProperty(name='After Import one file')
    operator_context: EnumProperty(default='EXEC_DEFAULT', name='Context',
                                   items=[(k, k.replace('_', ' ').title(), '') for k in operator_context])
    # display
    category: StringProperty(default='default')


def load_config_wm():
    import json
    cat_datas = {}  # category only use in display
    for file in get_AssetDir_path(AssetDir.CONFIG).iterdir():
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            cat_datas.update({file.stem: data})

    # clear all item
    bpy.context.window_manager.cdi_config_list.clear()

    for category, datas in cat_datas.items():
        for label, values in datas.items():
            item = bpy.context.window_manager.cdi_config_list.add()
            item.name = label
            for k, v in values.items():
                setattr(item, k, v)
            setattr(item, category, category)

    return cat_datas


def save_config_wm():
    import json
    cat_datas = {}
    for item in bpy.context.window_manager.cdi_config_list:
        if item.category not in cat_datas:
            cat_datas[item.category] = {}
        save_dict = dict(item.items())
        # process saving
        save_dict.pop('name')  # remove name
        save_dict['bl_import_operator'] = item.bl_import_operator  # empty need to save manually
        save_dict['poll_area'] = item.poll_area  # EnumProperty save index instead of string, so handle here
        save_dict['operator_context'] = item.operator_context  # the same as above
        for st in scripts_types:
            if item.get(st) == '': save_dict.pop(st)  # remove empty script
        cat_datas[item.category].update({item.name: save_dict})
    # save in file
    for category, datas in cat_datas.items():
        with open(get_AssetDir_path(AssetDir.CONFIG) / f'{category}.json', 'w', encoding='utf-8') as f:
            json.dump(datas, f, indent=4, allow_nan=True)

    load_config_wm()
    from . import _runtime
    _runtime.unregister()
    _runtime.register()


class CDI_OT_config_sl(bpy.types.Operator):
    bl_idname = 'cdi.config_sl'
    bl_label = 'Save / Load'

    type: EnumProperty(items=[("SAVE", "Save", ''), ("LOAD", "Load", '')], default="LOAD", options={"SKIP_SAVE"})

    def execute(self, context):
        if self.type == 'SAVE':
            save_config_wm()
        else:
            load_config_wm()
        self.report({'INFO'}, f'{self.type.title()} config')
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)


class CDI_UL_ConfigList(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()

        row.prop(item, 'name', text='', emboss=False)
        row.label(text=item.bl_file_extensions)
        row.label(text=area_type.get(item.poll_area, item.poll_area))

    def filter_items(self, context, data, propname):
        items = getattr(data, propname)
        ordered = []
        filtered = [self.bitflag_filter_item] * len(items)

        for i, item in enumerate(items):
            if item.category != context.window_manager.cdi_config_category:
                filtered[i] &= ~self.bitflag_filter_item

        try:
            ordered = bpy.types.UI_UL_list.sort_items_helper(items,
                                                             lambda i: len(getattr(i, filter.filter_type[7:]), True))
        except:
            pass

        return filtered, ordered


class CDI_OT_configlist_edit(bpy.types.Operator):
    bl_idname = 'cdi.configlist_edit'
    bl_label = 'Edit'

    operator_type: EnumProperty(
        items=[
            ('ADD', 'Add', ''),
            ('REMOVE', 'Remove', ''),
            ('MOVE_UP', 'Move Up', ''),
            ('MOVE_DOWN', 'Move Down', ''),
        ]
    )

    def execute(self, context):
        wm = context.window_manager
        if self.operator_type == 'ADD':
            new_item = wm.cdi_config_list.add()
            new_item.name = f'Config{len(wm.cdi_config_list)}'
            # correct index
            old_index = wm.cdi_config_list_index
            new_index = len(wm.cdi_config_list) - 1
            wm.cdi_config_list_index = new_index

            for i in range(old_index, new_index - 1):
                bpy.ops.cdi.configlist_edit(operator_type='MOVE_UP')

        elif self.operator_type == 'REMOVE':
            index = wm.cdi_config_list_index
            wm.cdi_config_list.remove(index)
            wm.cdi_config_list_index = index - 1 if index != 0 else 0

        elif self.operator_type in ['MOVE_UP', 'MOVE_DOWN']:
            my_list = wm.cdi_config_list
            index = wm.cdi_config_list_index
            neighbor = index + (-1 if self.operator_type == 'MOVE_UP' else 1)
            my_list.move(neighbor, index)
            self.move_index(context)

        return {'FINISHED'}

    def move_index(self, context):
        wm = context.window_manager
        index = wm.cdi_config_list_index
        new_index = index + (-1 if self.operator_type == 'MOVE_UP' else 1)
        wm.cdi_config_list_index = max(0, min(new_index, len(wm.cdi_config_list) - 1))


class CDI_OT_script_selector(bpy.types.Operator):
    bl_idname = 'cdi.script_selector'
    bl_label = 'Select Script'
    bl_property = 'enum_script'

    _enum_script = []  # store

    scripts_types: StringProperty()

    def get_script(self, context):
        enum_items = CDI_OT_script_selector._enum_script
        enum_items.clear()
        for file in get_ScriptDir().iterdir():
            enum_items.append((file.name, file.stem, ''))
        return enum_items

    enum_script: EnumProperty(
        name="Scripts",
        items=get_script,
    )

    def execute(self, context):
        wm = context.window_manager
        item = wm.cdi_config_list[wm.cdi_config_list_index]
        if self.scripts_types in scripts_types:
            setattr(item, self.scripts_types, self.enum_script)

        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}


class CDI_OT_idname_selector(bpy.types.Operator):
    bl_idname = 'cdi.idname_selector'
    bl_label = 'Select Operator'
    bl_property = 'enum_idname'

    _enum_idname = []  # store

    def get_idname(self, context):
        enum_items = CDI_OT_idname_selector._enum_idname
        enum_items.clear()

        def get_op_label(bl_idname: str):
            opid = bl_idname.split(".")
            opmod = getattr(bpy.ops, opid[0])
            op = getattr(opmod, opid[1])
            label = op.get_rna_type().bl_rna.name
            return label

        name_ops = {}
        opsdir = dir(bpy.ops)
        for opmodname in opsdir:
            opmod = getattr(bpy.ops, opmodname)
            opmoddir = dir(opmod)
            for o in opmoddir:
                bl_idname = opmodname + "." + o
                label = get_op_label(bl_idname)
                if bl_idname == label: continue  # pass the unnecessary operator
                name_ops[label] = bl_idname

        # sort by bl_idname
        sort_ops = sorted(name_ops.items(), key=lambda x: x[0])
        enum_items = [(bl_idname, label, "") for label, bl_idname in sort_ops]
        print(enum_items)
        return enum_items

    enum_idname: EnumProperty(
        name="Operators",
        items=get_idname,
    )

    def execute(self, context):
        wm = context.window_manager
        item = wm.cdi_config_list[wm.cdi_config_list_index]
        item.bl_import_operator = self.enum_idname

        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}


class CDI_OT_file_ext_editor(bpy.types.Operator):
    bl_idname = 'cdi.file_ext_editor'
    bl_label = 'Edit'

    operator_type: EnumProperty(
        items=[('ADD', 'Add', ''), ('REMOVE', 'Remove', '')], options={'SKIP_SAVE', 'HIDDEN'})

    ext: StringProperty(name='New', options={'SKIP_SAVE'})

    def execute(self, context):
        item = context.window_manager.cdi_config_list[context.window_manager.cdi_config_list_index]
        if self.operator_type == 'REMOVE':
            ori_list = item.bl_file_extensions.split(';')
            ori_list.remove(self.ext)
            item.bl_file_extensions = ';'.join(ori_list)
            if item.bl_file_extensions.startswith(';'):
                item.bl_file_extensions = item.bl_file_extensions[1:]
        else:
            if not self.ext.startswith('.'):
                self.ext = '.' + self.ext
            item.bl_file_extensions += ';' + self.ext
            if item.bl_file_extensions.startswith(';'):
                item.bl_file_extensions = item.bl_file_extensions[1:]

        context.area.tag_redraw()
        return {'FINISHED'}

    def invoke(self, context, event):
        if self.operator_type == 'ADD':
            return context.window_manager.invoke_props_dialog(self)
        else:
            return self.execute(context)


def draw_layout(self, context, layout):
    wm = context.window_manager

    row = layout.split(factor=0.75)
    row.separator()

    row = layout.row()
    row.prop(wm, 'cdi_config_category', text='')
    row = row.row()
    # row.operator(CDI_OT_config_sl.bl_idname, text='Load').type = 'LOAD'
    row.operator(CDI_OT_config_sl.bl_idname, text='Save').type = 'SAVE'

    row = layout.row()
    col = row.column(align=True)
    col.operator(CDI_OT_configlist_edit.bl_idname, icon='ADD', text='').operator_type = 'ADD'
    col.operator(CDI_OT_configlist_edit.bl_idname, icon='REMOVE', text='').operator_type = 'REMOVE'
    col.operator(CDI_OT_configlist_edit.bl_idname, icon='TRIA_UP', text='').operator_type = 'MOVE_UP'
    col.operator(CDI_OT_configlist_edit.bl_idname, icon='TRIA_DOWN', text='').operator_type = 'MOVE_DOWN'

    row.template_list(
        "CDI_UL_ConfigList", "Config List",
        wm, "cdi_config_list",
        wm, "cdi_config_list_index")

    item = wm.cdi_config_list[wm.cdi_config_list_index] if wm.cdi_config_list else None

    if item:
        box = layout.box()
        # box.use_property_split = True

        row = box.row(align=True)
        row.prop(item, 'bl_import_operator')
        row.operator('CDI_OT_idname_selector', icon='VIEWZOOM', text='')
        ################
        # box.prop(item, 'bl_file_extensions')
        row = box.split(factor=0.5)
        row.label(text='File Extensions')
        if ext_list := item.bl_file_extensions.split(';'):
            ext_list = [ext for ext in ext_list if ext != '']
            for ext in ext_list:
                row = row.row()
                op = row.operator('CDI_OT_file_ext_editor', text=ext, icon='X')
                op.ext = ext
                op.operator_type = 'REMOVE'

        row = row.row()
        op = row.operator('CDI_OT_file_ext_editor', icon='ADD', text='')
        op.operator_type = 'ADD'

        box.prop(item, 'poll_area')
        box.prop(item, 'operator_context')
        #######################
        box = box.box()
        box.use_property_split = False
        show = wm.cdi_config_show_advanced
        box.prop(wm, 'cdi_config_show_advanced', icon="TRIA_DOWN" if show else "TRIA_RIGHT", toggle=True, emboss=False)

        if show:
            for st in scripts_types:
                row = box.row()
                row.prop(item, st)
                row.operator(CDI_OT_script_selector.bl_idname, icon='VIEWZOOM', text='').scripts_types = st
            # open folder
            box.operator('wm.path_open', text='Open Script Folder').filepath = str(get_ScriptDir())

def register():
    bpy.utils.register_class(CDI_ConfigItem)
    bpy.utils.register_class(CDI_UL_ConfigList)
    bpy.utils.register_class(CDI_OT_config_sl)
    bpy.utils.register_class(CDI_OT_script_selector)
    bpy.utils.register_class(CDI_OT_idname_selector)
    bpy.utils.register_class(CDI_OT_configlist_edit)
    bpy.utils.register_class(CDI_OT_file_ext_editor)

    bpy.types.WindowManager.cdi_config_list = CollectionProperty(type=CDI_ConfigItem)
    bpy.types.WindowManager.cdi_config_list_index = IntProperty()
    bpy.types.WindowManager.cdi_config_show_advanced = BoolProperty(default=False, name='Advanced')

    cats = load_config_wm().keys()

    bpy.types.WindowManager.cdi_config_category = EnumProperty(items=[(c, c, '') for c in cats], name='Category')


def unregister():
    bpy.utils.unregister_class(CDI_ConfigItem)
    bpy.utils.unregister_class(CDI_UL_ConfigList)
    bpy.utils.unregister_class(CDI_OT_config_sl)
    bpy.utils.unregister_class(CDI_OT_script_selector)
    bpy.utils.unregister_class(CDI_OT_idname_selector)
    bpy.utils.unregister_class(CDI_OT_configlist_edit)
    bpy.utils.unregister_class(CDI_OT_file_ext_editor)

    del bpy.types.WindowManager.cdi_config_show_advanced
    del bpy.types.WindowManager.cdi_config_category
    del bpy.types.WindowManager.cdi_config_list
    del bpy.types.WindowManager.cdi_config_list_index
