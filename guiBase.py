#!/usr/bin/python
# -*- coding: utf8 -*-

from pandac.PandaModules import *
#import direct.directbase.DirectStart
from direct.gui.DirectGui import *
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.interval.IntervalGlobal import *

import sys, math, random, os.path, os, re

RATIO = base.getAspectRatio()

textColors = {}
textColors["white"] = ((1,1,1,1), (0,0,0,0.8))
textColors["white_transp"] = ((1,1,1,1), (0,0,0,0.0))


def loadFont(ref, size=15, spaceAdvance=None, 
	lineHeight=None, scaleFactor=1, 
	textureMargin=2, minFilter=Texture.FTNearest,
	magFilter=Texture.FTNearest, 
	renderMode=None):
	return loader.loadFont(ref, spaceAdvance=spaceAdvance,
		lineHeight=lineHeight, 
		pixelsPerUnit=size,
		scaleFactor=scaleFactor,
		textureMargin=textureMargin,
		minFilter=minFilter, magFilter=magFilter)




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



size = 12.0
sx = 0.04*600.0/base.win.getYSize()
FONT = loadFont("fonts/arial.ttf", size=size)
#FONT = loadFont("fonts/DejaVuSans.ttf", size=size)
#FONT_SCALE = (3*size/base.win.getXSize(), 3*size/base.win.getYSize(), 0.0)
FONT_SCALE = (sx,sx,1)

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
	M = OnscreenText(style=1, fg=fg, bg=bg, pos=(x, y), align=TextNode.ALeft, scale = FONT_SCALE, mayChange = 1, font = FONT,wordwrap=40*base.win.getXSize()/800.0)
	M.setText(txt)
	return M

def makeMsgRight(x,y, txt = "msg", color = "white"):
	m = makeMsg(x, y, txt, color)
	m["align"]=TextNode.ARight
	return m

#-------------------------------------------------------------------------------
# Barre
#-------------------------------------------------------------------------------
class Barre(DirectFrame):
	def __init__(self, w=0.2,h=0.05,x=0.0,y=0.0,hpMax=10.0,color1 = (0.1, 0.4, 0.25, 1.0), color2 = (0.30, 0.85, 0.45, 0.9), text = None):
		self.w = w
		self.wMax = w
		self.h = h
		self.x = x
		self.y = y
		self.hp = hpMax
		self.hpMax = hpMax
		
		#pad = 0.0025
		pad = 2.0/base.win.getYSize()
		DirectFrame.__init__(self,
			frameSize = (-self.w*RATIO-pad,self.w*RATIO+pad,-self.h-pad,self.h+pad),
			frameColor=color1,
			pos = ((self.x+self.w)*RATIO,1,self.y),
			pad = (0,0),
			borderWidth=(0.0,0.0),
			relief = DGG.GROOVE,
		)
		self.initialiseoptions(Barre)
		self.setBin("fixed", 0)
		
		self.bgFrame = DirectFrame(
			frameSize = (-self.w*RATIO-pad*2.0,self.w*RATIO+pad*2.0,-self.h-pad*2.0,self.h+pad*2.0),
			frameColor=color2,
			pos = (0,1,0),
			pad = (0,0),
			borderWidth=(0.0,0.0),
			relief = DGG.GROOVE,
		)
		self.bgFrame.reparentTo(self)
		self.bgFrame.setBin("fixed", -1)
		
		
		self.hpFrame = DirectFrame(
			frameSize = (-self.w*RATIO,self.w*RATIO,-self.h,self.h),
			frameColor=color2,
			pos = (0,1,0),
			pad = (0,0),
			borderWidth=(0.0,0.0),
			relief = DGG.GROOVE,
		)
		self.hpFrame.reparentTo(self)
		self.hpFrame.setBin("fixed", 1)
		
		if text is not None:
			self.msg = makeMsgRight((-0.01-self.w)*RATIO,-0.01,text,"white_transp")
			self.msg.reparentTo(self)
			
	def getHp(self):
		return self.hp
		
	def setHp(self, hp):
		self.hp = float(max(0, min(hp, self.hpMax)))
		self.update()
		
	def update(self):
		self.w = self.wMax * (self.hp / self.hpMax)
		self.hpFrame["frameSize"] = (-self.w*RATIO,self.w*RATIO,-self.h,self.h)
		self.hpFrame.setPos((self.w-self.wMax)*RATIO,1,0)
		
	def setHpMax(self, hp):
		self.hpMax = float(hp)
		self.update()
		
#-------------------------------------------------------------------------------
# MainMenuButton
#-------------------------------------------------------------------------------
class MainMenuButton(DirectButton):
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
			text_font = FONT2,
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
		self.initialiseoptions(MainMenuButton)
		
		self.bind(DGG.ENTER, command=self.onHover, extraArgs=[self])
		self.bind(DGG.EXIT, command=self.onOut, extraArgs=[self])
		
	def onHover(self, extraArgs, sentArgs):
		self["text_fg"] = (1,1,1,1)
		#self["text_shadow"] = (0.0,0.5,0.95,1)
		
	def onOut(self, extraArgs, sentArgs):
		self["text_fg"] = (0.8,0.8,0.8,1)
		#self["text_shadow"] = (0.0,0.5,0.95,1)

#-------------------------------------------------------------------------------
# Entry
#-------------------------------------------------------------------------------
class Entry(DirectEntry):
	def __init__(self, x=0, y=0, name="entrie"):
		DirectEntry.__init__(self,
			text="",
			initialText = "hahaha",
			entryFont = FONT,
			#scale = (FONT_SCALE[0], 1, FONT_SCALE[1]),
			scale=0.04,
			color = (0,0,0,1),
			text_fg = (1,1,1,1),
			width = 25,
		)
		self.initialiseoptions(Entry)
		#print pdir(self)
		self.enterText("ok test")
		self.setText()
		
	def setCommand(self, command, extraArgs=[]):# do NOT overload the "bind" method!
		print "call to setCommand for %s, extra = %s" % (command, extraArgs)
		self["command"] = command
		self["extraArgs"] = extraArgs
		
if __name__=="__main__":
	e = Entry()
	def aff(text, extraArgs = []):
		print "text = ", text, "extraArgs = ", extraArgs
		print "enter"
	e.setCommand(aff, ["text0"])
	
	b = MainMenuButton(0,0,"NEW GAME")
	
	base.accept("escape", sys.exit)
	run()
