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

from . import (
    ui,
    properties
)

from freestyle.types import (
    StrokeShader,
)
import parameter_editor

import bpy
import os
import sys
import itertools

sys.path.insert(0, os.path.dirname(__file__))

try:
    import axi
except ImportError as e:
    print("Could not load axi library")
    print(e)


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


def render_height(scene):
    render = scene.render
    return int(render.resolution_y * render.resolution_percentage / 100)


def render_width(scene):
    render = scene.render
    return int(render.resolution_x * render.resolution_percentage / 100)


def scale_factor(scene):
    return min(1.0 / render_height(scene) * properties.V3_BOUNDS[3],
               1.0 / render_width(scene) * properties.V3_BOUNDS[2])


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

    def __init__(self, name,  res_y, scale, split_at_invisible, frame_current):
        StrokeShader.__init__(self)
        # attribute 'name' of 'StrokeShader' objects is not writable, so _name
        # is used
        self._name = name
        self.h = res_y
        self.scale = scale
        self.frame_current = frame_current
        self.strokes = []
        self.split_at_invisible = split_at_invisible

    @staticmethod
    def pathgen(stroke, height, split_at_invisible,
                f=lambda v: not v.attribute.visible):
        """Generator that creates SVG paths (as strings) from the current
         stroke """
        if len(stroke) <= 1:
            return []

        it = iter(stroke)
        # start first path
        for v in it:
            x, y = v.point
            yield (x, height - y)

            if split_at_invisible and v.attribute.visible is False:
                # fast-forward till the next visible vertex
                it = itertools.dropwhile(f, it)

                # yield next visible vertex
                svert = next(it, None)
                if svert is None:
                    break
                x, y = svert.point
                yield (x, height - y)

    def shade(self, stroke):
        stroke = list(self.pathgen(stroke, self.h, self.split_at_invisible))
        self.strokes.append(stroke)

    def get_strokes(self):
        return self.strokes


class PathPlotterCallback(ParameterEditorCallback):

    def __init__(self):
        self.lineset = []
        self.shader = None

    def poll(self, scene, linestyle):
        return scene.render.use_freestyle

    def modifier_post(self, scene, layer, lineset):
        if not self.poll(scene, lineset.linestyle):
            return []

        split = True  # scene.svg_export.split_at_invisible
        self.shader = PathPlotter(lineset.name or "", render_height(
            scene), scale_factor(scene), split, scene.frame_current)
        return [self.shader]

    def lineset_post(self, scene, layer, lineset):
        if not self.poll(scene, lineset.linestyle):
            return []

        self.lineset.extend(self.shader.get_strokes())


def connect_plotter():
    d = axi.Device()
    d.enable_motors()
    d.zero_position()
    return d


def disconnect_plotter(d):
    d.zero_position()
    d.disable_motors()
    d.pen_up()


class OperatorPlot(bpy.types.Operator):
    bl_idname = "plot.plot"
    bl_label = "Plot"
    bl_description = "Render and plot the result to an AxiDraw plotter."

    def execute(self, context):
        plotter = context.scene.plotter
        self.report({'INFO'}, "Area X: %f; Area Y: %f" %
                    (plotter.area_x, plotter.area_y))

        pp = PathPlotterCallback()
        editor = parameter_editor

        def render_complete(scene):
            if not pp.lineset:
                return

            device = connect_plotter()
            if not device:
                self.report({'ERROR'}, "Failed to connect to AxiDraw.")
                return

            drawing = axi.Drawing(pp.lineset)
            drawing = drawing.scale(scale_factor(scene))

            if plotter.join_paths:
                drawing = drawing.join_paths(plotter.join_paths_threshold)

            if plotter.sort_paths:
                drawing = drawing.sort_paths()

            device.run_drawing(drawing, True)

            disconnect_plotter(device)

            editor.callbacks_lineset_post.remove(pp.lineset_post)
            editor.callbacks_modifiers_post.remove(pp.modifier_post)
            bpy.app.handlers.render_complete.remove(render_complete)

        try:
            editor.callbacks_lineset_post.append(pp.lineset_post)
            editor.callbacks_modifiers_post.append(pp.modifier_post)
            bpy.app.handlers.render_complete.append(render_complete)

            bpy.ops.render.render('EXEC_DEFAULT')

        except Exception as e:
            self.report({'ERROR'}, "Failed to plot.")
            print(str(e))

        return {'FINISHED'}


def register():
    properties.register()
    ui.register()
    bpy.utils.register_class(OperatorPlot)


def unregister():
    properties.unregister()
    ui.unregister()
    bpy.utils.unregister_class(OperatorPlot)


if __name__ == "__main__":
    register()
