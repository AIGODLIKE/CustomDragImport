bl_info = {
    "name": "Custom Drag Import",
    "author": "AIGODLIKE社区, Atticus",
    "blender": (4, 1, 0),
    "version": (0, 3),
    "category": "Import-Export",
    "support": "COMMUNITY",
}

from . import _runtime, display, keymap, translations
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))


def register():
    _runtime.register()
    display.register()
    keymap.register()
    translations.register()


def unregister():
    _runtime.unregister()
    display.unregister()
    keymap.unregister()
    translations.unregister()
