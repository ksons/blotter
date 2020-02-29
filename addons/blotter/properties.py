from bpy import (
    utils,
    types

)

from bpy.props import (
    FloatProperty,
    BoolProperty,
    PointerProperty
)

V3_BOUNDS = (0, 0, 11.8, 8.58)
DIN_A4 = (0.297, 0.21)
INCH_TO_METERS = 0.0254


class PlotProperties(types.PropertyGroup):
    """Implements the properties for the plotter output exporter"""
    bl_idname = "OUTPUT_PT_plotter_props"

    area_x: FloatProperty(
        name="Plot Area X",
        description="Width of the area to plot",
        min=V3_BOUNDS[0] * INCH_TO_METERS,
        max=V3_BOUNDS[2] * INCH_TO_METERS,
        default=DIN_A4[0],
        precision=3,
        unit="LENGTH"
    )
    area_y: FloatProperty(
        name="Plot Area Y",
        description="Height of the area to plot",
        min=V3_BOUNDS[1] * INCH_TO_METERS,
        max=V3_BOUNDS[3] * INCH_TO_METERS,
        default=DIN_A4[1],
        precision=3,
        unit="LENGTH"
    )

    sort_paths: BoolProperty(
        name="Sort Paths",
        description="Sort the paths in order to optimize pen travel",
        default=True
    )

    join_paths: BoolProperty(
        name="Join Paths",
        description="Join paths in order to optimize number of strokes",
        default=True
    )

    join_paths_threshold: FloatProperty(
        name="Join Threshold",
        description="Similarity of strokes in order to join",
        min=0.001,
        max=1,
        default=0.01,
        precision=3
    )


def register():
    utils.register_class(PlotProperties)
    types.Scene.plotter = PointerProperty(type=PlotProperties)


def unregister():
    utils.unregister_class(PlotProperties)
