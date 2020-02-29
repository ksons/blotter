
from bpy import (
    utils,
    types
)


class PlotPanel(types.Panel):
    """Creates a Panel in the render context of the properties editor"""
    bl_idname = "RENDER_PT_PlotOutputPanel"
    bl_space_type = 'PROPERTIES'
    bl_label = "Plotter"
    bl_region_type = 'WINDOW'
    bl_context = "output"

    def draw_header(self, context):
        # self.layout.prop(context.scene.plotter, "use_svg_export", text="")
        pass

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        plotter = scene.plotter

        # layout.active = (plotter.use_svg_export and freestyle.mode != 'SCRIPT')
        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column()
        col.prop(plotter, 'area_x')
        col.prop(plotter, 'area_y')

        row = layout.row()
        row.operator("plot.plot")


def register():
    utils.register_class(PlotPanel)


def unregister():
    utils.unregister_class(PlotPanel)
