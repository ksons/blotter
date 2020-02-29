
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

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        plotter = scene.plotter

        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column()
        col.prop(plotter, "area_x")
        col.prop(plotter, "area_y")

        row = layout.row()
        row.prop(plotter, "sort_paths")
        row.prop(plotter, "join_paths")

        col = layout.column()
        col.active = plotter.join_paths
        col.prop(plotter, "join_paths_threshold")

        row = layout.row()
        row.operator("plot.plot")


def register():
    utils.register_class(PlotPanel)


def unregister():
    utils.unregister_class(PlotPanel)
