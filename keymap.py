import bpy
from .display import draw_layout
from .public_data import area_type

addon_keymaps = []


def register():
    wm = bpy.context.window_manager

    for k, v in area_type.items():
        km = wm.keyconfigs.addon.keymaps.new(name=v, space_type=k)
        # click drag
        kmi = km.keymap_items.new('cdi.popup_operator', 'LEFTMOUSE', 'CLICK_DRAG', ctrl=True, alt=True,
                                  shift=False)
        addon_keymaps.append((km, kmi))


def unregister():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)

    addon_keymaps.clear()
