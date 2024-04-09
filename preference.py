import bpy
from .display import draw_layout, area_type
from ._runtime import CDI_OT_popup_operator


class CDI_Preference(bpy.types.AddonPreferences):
    bl_idname = __package__

    def draw(self, context):
        layout = self.layout
        draw_layout(self, context, layout)


addon_keymaps = []


def add_km():
    wm = bpy.context.window_manager

    for k, v in area_type.items():
        km = wm.keyconfigs.addon.keymaps.new(name=v, space_type=k)
        # click drag
        kmi = km.keymap_items.new('cdi.popup_operator', 'LEFTMOUSE', 'CLICK_DRAG', ctrl=True, alt=True,
                                  shift=False)
        addon_keymaps.append((km, kmi))


def remove_km():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)

    addon_keymaps.clear()


def register():
    bpy.utils.register_class(CDI_Preference)
    add_km()


def unregister():
    bpy.utils.unregister_class(CDI_Preference)
    remove_km()
