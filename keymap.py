import bpy
import rna_keymap_ui

from .display import draw_layout
from .public_data import area_type

addon_keymaps = []


def draw_keymap(self, context, layout):
    col = layout.box().column()
    col.label(text="Keymap", icon="KEYINGSET")
    km = None
    wm = context.window_manager
    kc = wm.keyconfigs.user

    old_km_name = ""
    get_kmi_l = []

    for km_add, kmi_add in addon_keymaps:
        for km_con in kc.keymaps:
            if km_add.name == km_con.name:
                km = km_con
                break

        for kmi_con in km.keymap_items:
            if kmi_add.idname == kmi_con.idname and kmi_add.name == kmi_con.name:
                get_kmi_l.append((km, kmi_con))

    get_kmi_l = sorted(set(get_kmi_l), key=get_kmi_l.index)

    for km, kmi in get_kmi_l:
        if not km.name == old_km_name:
            col.label(text=str(km.name), icon="DOT")

        col.context_pointer_set("keymap", km)
        rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)

        old_km_name = km.name


def register():
    import sys
    if sys.platform != 'win32': return

    wm = bpy.context.window_manager

    pref = bpy.context.preferences.addons[__package__].preferences

    for k, v in area_type.items():
        km = wm.keyconfigs.addon.keymaps.new(name=v, space_type=k)
        if pref.clipboard_keymap == '0':
            kmi = km.keymap_items.new('cdi.popup_operator', 'V', 'PRESS', ctrl=True, alt=False,
                                      shift=True)
        else:
            # click drag
            kmi = km.keymap_items.new('cdi.popup_operator', 'LEFTMOUSE', 'CLICK_DRAG', ctrl=True, alt=True,
                                      shift=False)
        addon_keymaps.append((km, kmi))


def unregister():
    import sys
    if sys.platform != 'win32': return

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)

    addon_keymaps.clear()
