import bpy
from .display import draw_layout


class CDI_Preference(bpy.types.AddonPreferences):
    bl_idname = __package__

    def draw(self, context):
        layout = self.layout
        draw_layout(self, context, layout)


def register():
    bpy.utils.register_class(CDI_Preference)


def unregister():
    bpy.utils.unregister_class(CDI_Preference)
