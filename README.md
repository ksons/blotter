# blotter
Experimental addon for blender to plot on an [AxiDraw v3](http://www.axidraw.com/) pen plotter. Currently, it only works on Freestyle renderings.

### NAQ

No one ever asked, but I answer anyway:

* Does it make sense to directly plot from Blender? Probably not. Rather export your Freestyle renderings to SVG and have full control on your drawings in Inksape
* Why do you developed this addon then? Because it is cool somehow. Also look into the ideas section. Some of these feature could go beyond what you can do in SVG

### Installation


    git clone https://github.com/ksons/blotter
    cd blotter
    "C:/Program Files/Blender Foundation/Blender 2.82/2.82/python/bin/python.exe" -m pip install -r ./requirements.txt --target ./addons/blotter/ 

in Blender Preferences, let the Script path point to the blotter repository:

![Blender Preferences](../media/blotter.installation.png?raw=true)

### Usage

The plotter settings including a button to start the plot is added to the `Output Properties` section of the property editor. Make sure you have `Freestyle` activated in the `Render Properties`.

![Plotter Panel](../media/blotter.panel.png?raw=true)

### Ideas / TODOs

- [ ] Expose all AxiDraw settings via Blender UI
- [ ] UI Feedback on progress
- [ ] Give user means to switch pens based on Freestyle Line Style
- [ ] Hatching
- [ ] Render from real 3D - Freestyle basically renders from the render buffer outcomes


### Acknowledgement

This addon is based on the unoffical [axidraw](https://github.com/fogleman/axi) library and the approach was stolen from Folkert de Vries' [Freestyle SVG Export](https://docs.blender.org/manual/en/dev/addons/render/render_freestyle_svg.html).
