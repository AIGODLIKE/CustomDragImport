bl_info = {
    "name": "Batch Drag Import",
    "author": "AIGODLIKE社区, Atticus",
    "blender": (4, 1, 0),
    "version": (0, 1),
    "category": "Import-Export",
    "support": "COMMUNITY",
}

from . import _runtime,preference


def register():
    _runtime.register()
    preference.register()


def unregister():
    _runtime.unregister()
    preference.unregister()
