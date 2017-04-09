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
from collections import OrderedDict
from core import G
import filechooser as fc

import skeleton
import getpath

import numpy as np
import os


class PerspectiveTaskView(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Perspective')

        self.human = gui3d.app.selectedHuman
        self.humanPos = [0.0, 0.0, 0.0]
        self.currentframe = 0
        self.framesloaded = 0

        animbox = self.addLeftWidget(gui.GroupBox('Frames'))

        self.avFramesText = animbox.addWidget(gui.TextView('Available frames: 0'))

        self.playbackSlider = animbox.addWidget(gui.Slider(label=['Current frame', ': %d']))
        self.playbackSlider.setMin(0)

        @self.playbackSlider.mhEvent
        def onChange(value):
            self.currentframe = int(value)
            self.updateFrame()
        
        self.nextframeButton = animbox.addWidget(gui.Button('Next frame'))

        @self.nextframeButton.mhEvent
        def onClicked(event):
            anim = self.human.getActiveAnimation()
            if anim:
                if self.currentframe >= anim.nFrames-1:
                    self.currentframe = 0
                else:
                    self.currentframe += 1

                self.updateFrame()
                self.playbackSlider.setValue(self.currentframe)

        self.prevframeButton = animbox.addWidget(gui.Button('Previous frame'))

        @self.prevframeButton.mhEvent
        def onClicked(event):
            anim = self.human.getActiveAnimation()
            if anim:
                if self.currentframe <= 0:
                    self.currentframe = anim.nFrames-1
                else:
                    self.currentframe -= 1

                self.updateFrame()
                self.playbackSlider.setValue(self.currentframe)

        projbox = self.addLeftWidget(gui.GroupBox('Projection'))

        self.projRadioButtonGroup = []

        self.persButton = projbox.addWidget(gui.RadioButton(self.projRadioButtonGroup, 'Perspective',selected=G.app.modelCamera.projection))

        @self.persButton.mhEvent
        def onClicked(event):
            G.app.guiCamera.projection = True
            G.app.guiCamera.fixedRadius = True
            G.app.modelCamera.projection = True
            G.app.modelCamera.fixedRadius = True
            if G.app.backgroundGradient:
                G.app.removeObject(G.app.backgroundGradient)
            G.app.backgroundGradient = None
            # G.app.modelCamera.updateCamera()

        self.orthButton = projbox.addWidget(gui.RadioButton(self.projRadioButtonGroup, 'Orthogonal',selected=not G.app.modelCamera.projection))

        @self.orthButton.mhEvent
        def onClicked(event):
            G.app.guiCamera.projection = False
            G.app.guiCamera.fixedRadius = False
            G.app.modelCamera.projection = False
            G.app.modelCamera.fixedRadius = False
            G.app.loadBackgroundGradient()
            # G.app.modelCamera.updateCamera()

        self.fovslider = projbox.addWidget(gui.Slider(label=['Camera focus', '= %.2f'], min=25.0, max=130.0, value=90.0))
        @self.fovslider.mhEvent
        def onChange(value):
            G.app.modelCamera.setFovAngle(value)
            G.app.guiCamera.setFovAngle(value)
            #G.app.modelCamera.updateCamera()
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
            self.updateFrame()


    def updateFrame(self):
        self.human.setToFrame(self.currentframe)
        self.human.refreshPose()

    def onShow(self, event):
        self.currentframe = 0
        gui3d.TaskView.onShow(self, event)
        if gui3d.app.getSetting('cameraAutoZoom'):
            gui3d.app.setGlobalCamera()

        self.playbackSlider.setEnabled(False)
        self.prevframeButton.setEnabled(False)
        self.nextframeButton.setEnabled(False)
        if self.human.getSkeleton():
            if self.human.getActiveAnimation():
                maxframes = self.human.getActiveAnimation().nFrames
                if  maxframes > 1:
                    self.avFramesText.setText('Available frames: ' + str(maxframes))
                    self.playbackSlider.setEnabled(True)
                    self.playbackSlider.setMax(maxframes -1)
                    self.prevframeButton.setEnabled(True)
                    self.nextframeButton.setEnabled(True)
                    self.playbackSlider.setValue(self.currentframe)
                    self.updateFrame()
                elif  maxframes == 1:
                    self.avFramesText.setText('Available frames: 1')

    def onHide(self, event):
        gui3d.TaskView.onHide(self, event)

    def onHumanChanged(self, event):
        human = event.human
        if event.change == 'reset':
            if self.isShown():
                # Refresh onShow status
                self.onShow(event)


def load(app):
    category = app.getCategory('Community')
    taskview = category.addTask(PerspectiveTaskView(category))


def unload(app):
    pass
