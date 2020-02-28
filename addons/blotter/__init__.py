# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

import bpy
from bpy.app.handlers import persistent

from pyaxidraw import axidraw
import parameter_editor

from freestyle.types import (
    StrokeShader,
)

from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    PointerProperty,
)

bl_info = {
    "name": "Blotter: Draw Freestyle using AxiDraw",
    "author": "Kristian Sons",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "Properties > Render > Blotter",
    "description": "Render Freestyle images directly on the AxiDraw",
    "warning": "",
    "wiki_url": "",
    "support": 'TESTING',
    "category": "Render",
}

V3_BOUNDS = (0, 0, 11.8, 8.58)
DIN_A4 = (0.297, 0.21)
INCH_TO_METERS = 0.0254


def render_height(scene):
    return int(scene.render.resolution_y * scene.render.resolution_percentage / 100)


def render_width(scene):
    return int(scene.render.resolution_x * scene.render.resolution_percentage / 100)


def scale_factor(scene):
    return min(1.0 / render_height(scene) * V3_BOUNDS[3], 1.0 / render_width(scene) * V3_BOUNDS[2])


class PlotProperties(bpy.types.PropertyGroup):
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


class ParameterEditorCallback(object):
    """Object to store callbacks for the Parameter Editor in"""

    def lineset_pre(self, scene, layer, lineset):
        raise NotImplementedError()

    def modifier_post(self, scene, layer, lineset):
        raise NotImplementedError()

    def lineset_post(self, scene, layer, lineset):
        raise NotImplementedError()


class PathPlotter(StrokeShader):
    """Stroke Shader for writing stroke data to a .svg file."""

    def __init__(self, name, style, res_y, scale, split_at_invisible, stroke_color_mode, frame_current):
        StrokeShader.__init__(self)
        # attribute 'name' of 'StrokeShader' objects is not writable, so _name is used
        self._name = name
        self.h = res_y
        self.scale = scale
        self.frame_current = frame_current
        self.strokes = []
        self.split_at_invisible = split_at_invisible
        self.stroke_color_mode = stroke_color_mode  # BASE | FIRST | LAST
        self.style = style

    @classmethod
    def from_lineset(cls, lineset,  res_y, scale, split_at_invisible, use_stroke_color, frame_current, *, name=""):
        """Builds a SVGPathShader using data from the given lineset"""
        name = name or lineset.name
        linestyle = lineset.linestyle
        # extract style attributes from the linestyle and scene
        style = {
            'fill': 'none',
            'stroke-width': linestyle.thickness,
            'stroke-linecap': linestyle.caps.lower(),
            'stroke-opacity': linestyle.alpha
        }
        # get dashed line pattern (if specified)
        if linestyle.use_dashed_line:
            style['stroke-dasharray'] = ",".join(str(elem)
                                                 for elem in get_dashed_pattern(linestyle))
        # return instance
        return cls(name, style, res_y, scale, split_at_invisible, use_stroke_color, frame_current)

    @staticmethod
    def pathgen(stroke, style, height, split_at_invisible, stroke_color_mode, f=lambda v: not v.attribute.visible):
        """Generator that creates SVG paths (as strings) from the current stroke """
        if len(stroke) <= 1:
            return []

        print("Stroke Shader", str(stroke))

        it = iter(stroke)
        # start first path
        for v in it:
            x, y = v.point
            yield (x, height - y)
            if split_at_invisible and v.attribute.visible is False:
                # end current and start new path;
                # yield '" />' + path
                # fast-forward till the next visible vertex
                it = itertools.dropwhile(f, it)
                # yield next visible vertex
                svert = next(it, None)
                if svert is None:
                    break
                x, y = svert.point
                yield (x, height - y)

    def shade(self, stroke):
        stroke = list(self.pathgen(stroke, self.style, self.h,
                                   self.split_at_invisible, self.stroke_color_mode))
        self.strokes.append(stroke)
        # convert to actual XML. Empty strokes are empty strings; they are ignored.
        # self.elements.extend(et.XML(elem) for elem in stroke_to_paths if elem) # if len(elem.strip()) > len(self.path))

    def get_strokes(self):
        """Write SVG data tree to file """
        print("Write", self.scale)

        return self.strokes


class PlotPanel(bpy.types.Panel):
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


class PathPlotterCallback(ParameterEditorCallback):

    def __init__(self):
        self.lineset = []
        self.shader = None

    def poll(self, scene, linestyle):
        return scene.render.use_freestyle

    def modifier_post(self, scene, layer, lineset):
        if not self.poll(scene, lineset.linestyle):
            return []

        print("modifier callback", lineset)

        split = True  # scene.svg_export.split_at_invisible
        stroke_color_mode = 'BASE'  # lineset.linestyle.stroke_color_mode
        self.shader = PathPlotter.from_lineset(
            lineset,
            render_height(scene), scale_factor(scene), split, stroke_color_mode, scene.frame_current, name=layer.name + '_' + lineset.name)
        return [self.shader]

    def lineset_post(self, scene, layer, lineset):
        if not self.poll(scene, lineset.linestyle):
            return []

        self.lineset.extend(self.shader.get_strokes())


def plot_lineset(ad, lineset, scale):
    for stroke in lineset:
        for i, line in enumerate(stroke):
            if not i:
                print("moveto: {} {}".format(line[0], line[1]))
                ad.moveto(line[0] * scale, line[1] * scale)
            else:
                print("lineto: {} {}".format(line[0], line[1]))
                ad.lineto(line[0] * scale, line[1] * scale)


def initalize_plotter():
    ad = axidraw.AxiDraw()
    ad.interactive()
    if not ad.connect():
        return None
    ad.moveto(0, 0)
    return ad


def disconnect_plotter(ad):
    ad.moveto(0, 0)
    ad.disconnect()


class OperatorPlot(bpy.types.Operator):
    bl_idname = "plot.plot"
    bl_label = "Plot"
    bl_description = "Render and plot the result to an AxiDraw plotter."

    def execute(self, context):
        plotter = context.scene.plotter
        self.report(
            {'INFO'}, "Area X: %f; Area Y: %f" % (plotter.area_x, plotter.area_y))

        pp = PathPlotterCallback()

        def render_complete(scene, cb):
            print("render_complete", str(pp.lineset),
                  scene, cb, scale_factor(scene))

            ad = initalize_plotter()
            if not ad:
                self.report({'ERROR'}, "Failed to connect to AxiDraw.")
                return

            plot_lineset(ad, pp.lineset, scale_factor(scene))

            disconnect_plotter(ad)
            parameter_editor.callbacks_lineset_post.remove(
                pp.lineset_post)
            parameter_editor.callbacks_modifiers_post.remove(
                pp.modifier_post)
            bpy.app.handlers.render_complete.remove(render_complete)

        try:

            parameter_editor.callbacks_lineset_post.append(
                pp.lineset_post)
            parameter_editor.callbacks_modifiers_post.append(
                pp.modifier_post)

            bpy.app.handlers.render_complete.append(render_complete)

            bpy.ops.render.render('EXEC_DEFAULT')

        except Exception as e:
            self.report({'ERROR'}, "Failed to plot.")
            print(str(e))

        return {'FINISHED'}


classes = (
    PlotProperties,
    PlotPanel,
    OperatorPlot
)


def register():
    print("register")

    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.plotter = PointerProperty(type=PlotProperties)

    # add callbacks
    # bpy.app.handlers.render_pre.append(svg_export_header)
    # bpy.app.handlers.render_complete.append(render_complete)


def unregister():
    # remove callbacks
    # bpy.app.handlers.render_pre.remove(svg_export_header)

    print("unregister")


if __name__ == "__main__":
    register()