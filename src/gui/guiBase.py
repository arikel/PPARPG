#!/usr/bin/python
# -*- coding: utf8 -*-

from panda3d.core import *
from direct.gui.DirectGui import *
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.interval.IntervalGlobal import *

import sys, math, random, os.path, os, re

#RATIO = base.getAspectRatio()
RATIO = 1.25

textColors = {}
textColors["white"] = ((1,1,1,1), (0,0,0,0.8))
textColors["white_transp"] = ((1,1,1,1), (0,0,0,0.0))
#-------------------------------------------------------------------------------
# GuiBase
#-------------------------------------------------------------------------------

class GuiBase(object):
	def __init__(self, game):
		self.game = game
		
		self.winX = self.game.win.getXSize()
		self.winY = self.game.win.getYSize()
		self.ratio = float(self.winX) / self.winY
		
		self.fonts = []
		sx = 0.04*600.0/self.winX
		self.fonts.append(self.loadFont("fonts/arial.ttf", sx))
		self.fonts.append(self.game.loader.loadFont("fonts/oldtypewriter.ttf"))
		
		self.button = MainMenuButton(0,0,"EXIT", self.fonts[1])
		self.button.setPos(1.3333 - self.button.getWidth()/2, 0, 1- self.button.getHeight()/2)
		
		#self.hidePlayerHud()
		#self.hidePauseMenu()
		#self.hideOptionMenu()
		
		
	def showMainMenu(self):
		self.mainMenu.show()
		self.mainMenu.enable()
		self.mainMenu.buttons[1].disable() # remove when actual options can be used
		
	def hideMainMenu(self):
		self.mainMenu.hide()
		self.mainMenu.disable()
		
	def showPauseMenu(self):
		self.pauseMenu.show()
		self.pauseMenu.enable()
		
	def hidePauseMenu(self):
		self.pauseMenu.hide()
		self.pauseMenu.disable()
		
	def showPlayerHud(self):
		for label in [self.label, self.label0, self.label1]:
			label.show()
		self.crosshair.show()
		
	def hidePlayerHud(self):
		for label in [self.label, self.label0, self.label1]:
			label.hide()
		self.crosshair.hide()
		
	def showOptionMenu(self):
		self.optionMenu.show()
		
		
	def hideOptionMenu(self):
		self.optionMenu.hide()	
		
	def loadFont(self,
		fontPath,
		size,
		spaceAdvance=None,
		lineHeight=None,
		scaleFactor=1, 
		textureMargin=2,
		minFilter=Texture.FTNearest,
		magFilter=Texture.FTNearest, 
		renderMode=None):
		
		return self.game.loader.loadFont(
			fontPath,
			spaceAdvance=spaceAdvance,
			lineHeight=lineHeight, 
			pixelsPerUnit=size,
			scaleFactor=scaleFactor,
			textureMargin=textureMargin,
			minFilter=minFilter,
			magFilter=magFilter)
		
	def makeLabel(self, fontIndex, msg, scale):
		fg = textColors["white"][0]
		bg = textColors["white"][1]
		M = OnscreenText(
			style=1,
			fg=fg,
			bg=bg,
			pos=(0, 0),
			align=TextNode.ALeft,
			scale = scale,
			mayChange = 1,
			font = self.fonts[fontIndex],
			wordwrap=40*self.winX/800.0)
			
		M.setText(msg)
		return M



#-------------------------------------------------------------------------------
# makeImg
#-------------------------------------------------------------------------------
def makeImg(path, x, y, scale = 1):
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
# MainMenuButton
#-------------------------------------------------------------------------------
class MainMenuButton(DirectButton):
	def __init__(self, x, y, name, font):
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
			text_font = font,
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
		self.name = name
		self.bind(DGG.ENTER, command=self.onHover, extraArgs=[self])
		self.bind(DGG.EXIT, command=self.onOut, extraArgs=[self])
		
	#def setState(self, state):
	#	self["state"] = state
	def disable(self):
		#print "Disabling button %s" % (self.name)
		self["text_fg"] = (0.4,0.4,0.4,1)
		self["state"] = DGG.DISABLED
		
	def enable(self):
		#print "Enabling button %s" % (self.name)
		self["text_fg"] = (0.8,0.8,0.8,1)
		self["state"] = DGG.NORMAL
		
	def onHover(self, extraArgs, sentArgs):
		self["text_fg"] = (1,1,1,1)
		#self["text_shadow"] = (0.0,0.5,0.95,1)
		
	def onOut(self, extraArgs, sentArgs):
		self["text_fg"] = (0.8,0.8,0.8,1)
		#self["text_shadow"] = (0.0,0.5,0.95,1)
#-------------------------------------------------------------------------------
# MainMenu (title screen)
#-------------------------------------------------------------------------------
class MainMenu:
	def __init__(self, gui, font):
		self.gui = gui
		self.buttons = []
		startX = 0.0
		startY = 0.4
		step = -0.2
		
		for i, label in enumerate(["NEW GAME", "OPTIONS", "QUIT"]):
			button = MainMenuButton(startX, startY + i*step, label, font)
			self.buttons.append(button)
		
	def hide(self):
		for b in self.buttons:
			b.hide()
	def show(self):
		for b in self.buttons:
			b.show()
	
	def disable(self):
		for b in self.buttons:
			b.disable()
	def enable(self):
		for b in self.buttons:
			b.enable()

#-------------------------------------------------------------------------------
# PauseMenu
#-------------------------------------------------------------------------------
class PauseMenu(MainMenu):
	def __init__(self, gui, font):
		self.gui = gui
		self.buttons = []
		startX = -0.6
		startY = 0.8
		step = -0.2
		
		for i, label in enumerate(["CONTINUE", "MAIN MENU", "QUIT"]):
			button = MainMenuButton(startX, startY + i*step, label, font)
			self.buttons.append(button)
		
#-------------------------------------------------------------------------------
# CheckButton
#-------------------------------------------------------------------------------
class CheckButton(DirectCheckButton):
	def __init__(self):
		DirectCheckButton.__init__(self, scale = 0.05, text_fg = (0,0,1,1), text_bg = (1,0,0,1), text = "Mouse Inverted", textMayChange=1)
		self.initialiseoptions(CheckButton)
		#self.setScale(0.06)
		#self["boxRelief"] = DGG.SUNKEN
		#self["boxImage"] = "img/gui/tick2.png"
		#self["boxBorder"] = 0
		#self["pressEffect"] = 0
		self["text_fg"] = (1,1,1,1)
		self["text_scale"] = (1,1)
		self["text"] = "restart"
		self.setText()
		
	def setButtonText(self, text):
		self["text"] = text
		
	def setCommand(self, command):
		#print "setting check button command"
		self["command"] = command
		
		
#-------------------------------------------------------------------------------
# OptionMenu
#-------------------------------------------------------------------------------
class OptionMenu(object):
	def __init__(self, gui, font):
		self.gui = gui
		self.buttons = []
		self.checkButtons = []
		startX = -0.6
		startY = 0.8
		step = -0.2
	
		self.mouseInvertedButton = CheckButton()
		self.mouseInvertedButton.setPos(0.8, 0.6, 0)
		self.mouseInvertedButton.setCommand(self.command)
		self.mouseInvertedButton.setButtonText("Mouse inverted")
		
	def command(self, status):
		print "check clicked, status = %s" % (status)
		
	def hide(self):
		self.mouseInvertedButton.hide()
	def show(self):
		self.mouseInvertedButton.show()
		
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
'''
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
'''

"""
FONT2 = loader.loadFont("fonts/oldtypewriter.egg")
FONT_SCALE2 = 0.035



size = 12.0
sx = 0.04*600.0/base.win.getYSize()
FONT = loadFont("fonts/arial.ttf", size=size)
#FONT = loadFont("fonts/DejaVuSans.ttf", size=size)
#FONT_SCALE = (3*size/base.win.getXSize(), 3*size/base.win.getYSize(), 0.0)
FONT_SCALE = (sx,sx,1)
"""


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

		
if __name__=="__main__":
	e = Entry()
	def aff(text, extraArgs = []):
		print "text = ", text, "extraArgs = ", extraArgs
		print "enter"
	e.setCommand(aff, ["text0"])
	
	b = MainMenuButton(0,0,"NEW GAME")
	
	base.accept("escape", sys.exit)
	run()
