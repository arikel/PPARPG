#!/usr/bin/python
# -*- coding: utf8 -*-

from pandac.PandaModules import *
import direct.directbase.DirectStart
from direct.gui.DirectGui import *
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.interval.IntervalGlobal import *

import sys, math, random, os.path, os, re

RATIO = base.getAspectRatio()

textColors = {}
textColors["white"] = ((1,1,1,1), (0,0,0,0.8))
textColors["white_transp"] = ((1,1,1,1), (0,0,0,0.0))

#FONT = loader.loadFont("fonts/oldtypewriter.ttf")
#FONT_SCALE = 0.035

FONT = loader.loadFont("fonts/cour.ttf")#,minFilter=0,magFilter=0)
FONT_SCALE = (16.0/base.win.getXSize(), 16.0/base.win.getYSize(), 0.0)
FONT.setPointSize(20) # a value of 73 or more crashes Panda/Python
#FONT.setPixelsPerUnit(100)
FONT.setSpaceAdvance(2) # decrease as point size is decrease
FONT.setLineHeight(1.5)
FONT.setNativeAntialias(0)
# crashing crap tested :
#FONT.setPageSize(512,512)
#FONT.setRenderMode(TextFont.RMWireframe)
#FONT.setRenderMode(TextFont.RMPolygon)
#FONT.setRenderMode(TextFont.RMSolid)
#FONT.setRenderMode(TextFont.RMInvalid)



FONT2 = loader.loadFont("fonts/oldtypewriter.egg")
FONT_SCALE2 = 0.035

#-------------------------------------------------------------------------------
# makeImg
#-------------------------------------------------------------------------------
def makeImg(x,y, path, scale = 1):
	a = OnscreenImage(image=path, pos=(float(x),0,float(y)), hpr=None, scale=scale, color=None, parent=None, sort=0)
	a.setTransparency(True)
	return a

#-------------------------------------------------------------------------------
# makeMsg
#-------------------------------------------------------------------------------
def makeMsg(x,y, txt = "msg", color = "white"):
	fg = textColors[color][0]
	bg = textColors[color][1]
	M = OnscreenText(style=1, fg=fg, bg=bg, pos=(x, y), align=TextNode.ALeft, scale = FONT_SCALE, mayChange = 1, font = FONT)
	M.setText(txt)
	return M

def makeMsgRight(x,y, txt = "msg", color = "white"):
	m = makeMsg(x, y, txt, color)
	m["align"]=TextNode.ARight
	return m

#-------------------------------------------------------------------------------
# MainButton
#-------------------------------------------------------------------------------
class MainButton(DirectButton):
	def __init__(self, x, y, name):
		DirectButton.__init__(self,
			frameSize = (-0.35,0.35,-0.07,0.07),
			pos = (x, 1, y),
			pad = (0,0),
			borderWidth=(0.008,0.008),
			frameColor=(0.2,0.2,0.2,0.6),
			#pressEffect = None,
			#scale = (0.4, 1, 0.1),
			#relief = None,
			relief = DGG.GROOVE,
			#relief = DGG.RIDGE,
			rolloverSound = None,#soundDic["rollover"],
			clickSound = None,#soundDic["select_confirm"],
			text_font = FONT,
			#text_scale = (0.01,0.0125,1),
			text_scale = (0.06,0.06,1.0),
			text_fg = (0.8,0.8,0.8,1),
			#text_shadow = (0.25,0.25,0.25,1),
			text_bg = (0,0,0,0.0),
			text = name,
			text_align = TextNode.ACenter,
			text_pos = (0, -0.025),
			#geom = None
			text_mayChange = True,
		)
		self.initialiseoptions(MainButton)
		
		self.bind(DGG.ENTER, command=self.onHover, extraArgs=[self])
		self.bind(DGG.EXIT, command=self.onOut, extraArgs=[self])
		
	def onHover(self, extraArgs, sentArgs):
		self["text_fg"] = (1,1,1,1)
		#self["text_shadow"] = (0.0,0.5,0.95,1)
		
	def onOut(self, extraArgs, sentArgs):
		self["text_fg"] = (0.8,0.8,0.8,1)
		#self["text_shadow"] = (0.0,0.5,0.95,1)



