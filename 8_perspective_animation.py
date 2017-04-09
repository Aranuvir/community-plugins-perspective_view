#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Jonas Hauquier, punkduck

**Copyright(c):**      MakeHuman Team 2001-2017

**Licensing:**         AGPL3 (http://www.makehuman.org/doc/node/the_makehuman_application.html)

    This file is part of MakeHuman (www.makehuman.org).

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Experimental plugin based on 3_library_animation.py, which allows to show bvh files
frame by frame and is able to switch between orthogonal and  perspective view.
"""

import mh
import gui
import gui3d
import log
from core import G


class PerspectiveTaskView(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Perspective')
        self.isOrthoView = True

        projbox = self.addLeftWidget(gui.GroupBox('Projection'))

        self.projRadioButtonGroup = []

        self.persButton = projbox.addWidget(gui.RadioButton(self.projRadioButtonGroup, 'Perspective',selected=G.app.modelCamera.projection))
        @self.persButton.mhEvent
        def onClicked(event):
            self.toggleView()
            self.isOrthoView=False

        self.orthButton = projbox.addWidget(gui.RadioButton(self.projRadioButtonGroup, 'Orthogonal',selected=not G.app.modelCamera.projection))
        @self.orthButton.mhEvent
        def onClicked(event):
            self.toggleView()
            self.isOrthoView = True


        self.fovslider = projbox.addWidget(gui.Slider(label='Camera focus= %.2f', min=25.0, max=130.0, value=90.0))
        @self.fovslider.mhEvent
        def onChange(value):
            for camera in G.cameras:
                camera.setFovAngle(value)
            G.app.redraw()

        posbox = self.addLeftWidget(gui.GroupBox('Position'))

        self.xposslider = posbox.addWidget(gui.Slider(label=['X-position', '= %.2f'], min=-10.0, max=10.0, value=0.0))
        @self.xposslider.mhEvent
        def onChange(value):
            self.humanPos[0] = value
            G.app.selectedHuman.setPosition(self.humanPos)
            self.updateFrame()

        self.yposslider = posbox.addWidget(gui.Slider(label=['Y-position', '= %.2f'], min=-10.0, max=10.0, value=0.0))
        @self.yposslider.mhEvent
        def onChange(value):
            self.humanPos[1] = value
            G.app.selectedHuman.setPosition(self.humanPos)
            self.updateFrame()

        self.zposslider = posbox.addWidget(gui.Slider(label=['Z-position', '= %.2f'], min=-10.0, max=10.0, value=0.0))
        @self.zposslider.mhEvent
        def onChange(value):
            self.humanPos[2] = value
            G.app.selectedHuman.setPosition(self.humanPos)
            self.updateFrame()

        self.resetButton = posbox.addWidget(gui.Button('Reset position'))
        @self.resetButton.mhEvent
        def onClicked(event):
            self.humanPos = [0.0, 0.0, 0.0]
            self.xposslider.setValue (0.0)
            self.yposslider.setValue (0.0)
            self.zposslider.setValue (0.0)
            G.app.selectedHuman.setPosition(self.humanPos)

    def toggleView(self):
        if self.isOrthoView:
            for camera in G.cameras:
                camera.switchToPerspective()
            if G.app.backgroundGradient:
                G.app.removeObject(G.app.backgroundGradient)
                G.app.backgroundGradient = None
            self.persButton.setSelected(True)
            self.orthButton.setSelected(False)
        else:
            for camera in G.cameras:
                camera.switchToOrtho()
            if not G.app.backgroundGradient:
                G.app.loadBackgroundGradient()
            self.persButton.setSelected(False)
            self.orthButton.setSelected(True)

def load(app):
    category = app.getCategory('Community')
    taskview = category.addTask(PerspectiveTaskView(category))


def unload(app):
    pass
