import bpy
from bpy.props import StringProperty, EnumProperty, BoolProperty, IntProperty, CollectionProperty

from .public_path import AssetDir, get_AssetDir_path, get_ScriptDir

area_type = {
    'VIEW_3D': '3D View',
    'IMAGE_EDITOR': 'Image Editor',
    'NODE_EDITOR': 'Node Editor',
    'TEXT_EDITOR': 'Text Editor',
    'CONSOLE': 'Console',
    'OUTLINER': 'Outliner',
    'PROPERTIES': 'Properties',
    'FILE_BROWSER': 'File Browser',
    'PREFERENCES': 'Preferences',
}

scripts_types = [
    'pre_script',
    'post_script',
    'foreach_pre_script',
    'foreach_post_script'
]


class CDI_ConfigItem(bpy.types.PropertyGroup):
    name: StringProperty(name='Name', default='New Importer')
    bl_idname: StringProperty()
    bl_import_operator: StringProperty()
    bl_file_extensions: StringProperty(name='File Extension', default='.txt')
    poll_area: EnumProperty(default='VIEW_3D',
                            items=[(k, v, '') for k, v in area_type.items()], )
    # custom
    pre_script: StringProperty(name='Pre Script')
    post_script: StringProperty(name='Post Script')
    foreach_pre_script: StringProperty(name='Foreach Pre Script')
    foreach_post_script: StringProperty(name='Foreach Post Script')
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
        # remove key 'name'
        save_dict.pop('name')
        save_dict['poll_area'] = item.poll_area
        cat_datas[item.category].update({item.name:save_dict })

    for category, datas in cat_datas.items():
        with open(get_AssetDir_path(AssetDir.CONFIG) / f'{category}.json', 'w', encoding='utf-8') as f:
            json.dump(datas, f, indent=4, allow_nan=True)


class CDI_OT_config_sl(bpy.types.Operator):
    bl_idname = 'cdi.config_sl'
    bl_label = 'Save / Load'

    type: EnumProperty(items=[("SAVE", "Save", ''), ("LOAD", "Load", '')], default="LOAD", options={"SKIP_SAVE"})

    def execute(self, context):
        if self.type == 'SAVE':
            save_config_wm()
        else:
            load_config_wm()
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
            enum_items.append((file.stem, file.name, ''))
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


def draw_layout(self, context, layout):
    wm = context.window_manager

    row = layout.split(factor=0.75)
    row.separator()

    row = layout.row()
    row.prop(wm, 'cdi_config_category', text='')
    row = row.row()
    # row.operator(CDI_OT_config_sl.bl_idname, text='Load').type = 'LOAD'
    row.operator(CDI_OT_config_sl.bl_idname, text='Save').type = 'SAVE'

    layout.template_list(
        "CDI_UL_ConfigList", "Config List",
        wm, "cdi_config_list",
        wm, "cdi_config_list_index")

    item = wm.cdi_config_list[wm.cdi_config_list_index] if wm.cdi_config_list else None
    if item:
        box = layout.box()
        box.prop(item, 'bl_idname')
        box.prop(item, 'bl_import_operator')
        box.prop(item, 'bl_file_extensions')
        box.prop(item, 'poll_area')

        box = box.box()
        show = wm.cdi_config_show_advanced
        box.prop(wm, 'cdi_config_show_advanced', icon="TRIA_DOWN" if show else "TRIA_RIGHT", toggle=True)

        if show:
            for st in scripts_types:
                row = box.row()
                row.prop(item, st)
                row.operator(CDI_OT_script_selector.bl_idname, icon='VIEWZOOM', text='').scripts_types = st


def register():
    bpy.utils.register_class(CDI_ConfigItem)
    bpy.utils.register_class(CDI_UL_ConfigList)
    bpy.utils.register_class(CDI_OT_config_sl)
    bpy.utils.register_class(CDI_OT_script_selector)

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

    del bpy.types.WindowManager.cdi_config_show_advanced
    del bpy.types.WindowManager.cdi_config_category
    del bpy.types.WindowManager.cdi_config_list
    del bpy.types.WindowManager.cdi_config_list_index
