bl_info = {
    "name": "Custom Drag Import",
    "author": "AIGODLIKE社区, Atticus",
    "blender": (4, 1, 0),
    "version": (0, 2),
    "category": "Import-Export",
    "support": "COMMUNITY",
}

from . import _runtime, display, keymap


def register():
    _runtime.register()
    display.register()
    keymap.register()


def unregister():
    _runtime.unregister()
    display.unregister()
    keymap.unregister()
