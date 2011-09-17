#!/usr/bin/python
# -*- coding: utf8 -*-

from pandac.PandaModules import *
import direct.directbase.DirectStart
from direct.gui.DirectGui import *
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.interval.IntervalGlobal import *

from guiBase import *

#-------------------------------------------------------------------------------
# Dialog
#-------------------------------------------------------------------------------

class DialogButton(DirectButton):
	def __init__(self, x, y, name = "dialogButton"):
		self.x = x
		self.y = y
		self.name = name
		#print "created dialog button %s" % (name)
		DirectButton.__init__(self,
			frameSize = (-1*RATIO,1*RATIO,-0.04,0.04),
			pos = (x, 1, y),
			pad = (0,0),
			borderWidth=(0.008,0.008),
			#frameColor=(0.2,0.2,0.2,0.8),
			frameColor=(0.1,0.1,0.1,0.8),
			#pressEffect = None,
			#scale = (0.4, 1, 0.1),
			#relief = None,
			
			#relief = DGG.GROOVE,
			relief = DGG.RIDGE,
			rolloverSound = None,#soundDic["rollover"],
			clickSound = None,#soundDic["select_confirm"],
			text_font = FONT,
			#text_scale = (0.01,0.0125,1),
			#text_scale = (0.06,0.06,1.0),
			text_scale = FONT_SCALE,
			text_fg = (0.8,0.8,0.8,1),
			#text_shadow = (0.25,0.25,0.25,1),
			#text_bg = (0,0,0,0.0),
			text = name,
			text_align = TextNode.ALeft,
			text_pos = (-0.95*RATIO, -0.02),
			#geom = None
			text_mayChange = True,
		)
		self.initialiseoptions(DialogButton)
		self.bind(DGG.ENTER, command=self.onHover, extraArgs=[self])
		self.bind(DGG.EXIT, command=self.onOut, extraArgs=[self])
		
	def onHover(self, extraArgs, sentArgs):
		self["text_fg"] = (1,1,1,1)
		self["frameColor"]=(0.2,0.2,0.2,0.8)
		#self["text_shadow"] = (0.0,0.5,0.95,1)
		
	def onOut(self, extraArgs, sentArgs):
		self["text_fg"] = (0.8,0.8,0.8,1)
		self["frameColor"]=(0.1,0.1,0.1,0.8)

class ArrowButton(DirectButton):
	def __init__(self, x, y, sens = "up"):
		self.x = x
		self.y = y
		self.sens = sens
		self.size = 0.05
		
		DirectButton.__init__(self,
			frameSize = (-self.size,self.size,-self.size,self.size),
			pos = (x, 1, y),
			pad = (0,0),
			borderWidth=(0.008,0.008),
			#frameColor=(0.2,0.2,0.2,0.8),
			frameColor=(0.1,0.1,0.1,0.8),
			#pressEffect = None,
			relief = None,#DGG.RIDGE,
			rolloverSound = None,
			clickSound = None,
		)
		self.initialiseoptions(ArrowButton)
		
		self.img = makeImg(0,0,"img/generic/arrow.png", self.size)
		self.img.reparentTo(self)
		if self.sens == "down":
			self.img.setR(180)
		
		self.interval = Sequence()
		self.interval.append(LerpScaleInterval(self.img, 0.3, (self.size*1.3, self.size*1.3, self.size*1.3)))
		self.interval.append(LerpScaleInterval(self.img, 0.3, (self.size, self.size, self.size)))
		
		self.setMode("active")
		
		
		self.bind(DGG.ENTER, command=self.onHover, extraArgs=[self])
		self.bind(DGG.EXIT, command=self.onOut, extraArgs=[self])
		
	def setMode(self, mode):
		self.mode = mode
		if mode == "active":
			self.color = (0.8,0.8,0.8,1)
			self.hoverColor = (1,1,1,1)
		elif mode == "frozen":
			self.color = (0.5,0.5,0.5,1)
			self.hoverColor = (0.5,0.5,0.5,1)
			self.interval.pause()
		self.onOut()
		
	def onHover(self, extraArgs=[], sentArgs=[]):
		#self["text_fg"] = (1,1,1,1)
		#self["frameColor"]=(0.2,0.2,0.2,0.8)
		#print "arrow hover"
		self.img.setColor(self.hoverColor)
		if self.mode == "active":
			self.interval.loop()
		#self["text_shadow"] = (0.0,0.5,0.95,1)
		
	def onOut(self, extraArgs=[], sentArgs=[]):
		#self["text_fg"] = (0.8,0.8,0.8,1)
		#self["frameColor"]=(0.1,0.1,0.1,0.8)
		#print "arrow out"
		self.img.setColor(self.color)
		if self.mode == "active":
			self.interval.pause()
	
class ArrowButtons:
	def __init__(self, x, y):
		self.upArrow = ArrowButton(x,y+0.08,"up")
		self.downArrow = ArrowButton(x,y-0.08,"down")
	def show(self):
		self.upArrow.show()
		self.downArrow.show()
	def hide(self):
		self.upArrow.hide()
		self.downArrow.hide()
	def destroy(self):
		self.upArrow.destroy()
		self.downArrow.destroy()
	def reparentTo(self, np):
		self.upArrow.reparentTo(np)
		self.downArrow.reparentTo(np)
	#def destroy(self):
	#	self.upArrow.destroy()
	#	self.downArrow.destroy()
		
class DialogButtonList:
	def __init__(self, x, y, dataList = []):
		self.x = x
		self.y = y
		self.dataList = dataList
		self.nbItems = len(self.dataList)
		
		self.maxDisplayedItems = 3
		self.maxIndex = max(self.nbItems-self.maxDisplayedItems,0)
		
		self.pos = 0
		self.size = 0.13
		
		
		
		self.frame = DirectScrolledFrame(
			#frameSize = (-1,1,-self.size,self.size),
			canvasSize = (-1*RATIO,1*RATIO,-self.size*self.nbItems,0),# virtual canvas
			frameColor=(0.6, 0.1, 0.1, 0.0),
			#canvasSize = (-2,2,-self.size*self.nbItems,self.size),
			frameSize = (-1,1,-(self.size-0.04)*self.maxDisplayedItems,0), # actual visible frame
			pos = (x, 0, y),
			pad = (0,0),
			borderWidth=(0.0,0.0),
			relief = DGG.GROOVE,
			manageScrollBars = False,
			autoHideScrollBars = False,
			verticalScroll_scale=0.0,
			horizontalScroll_scale=0.0,
			verticalScroll_frameSize=(0.0,0.0,0.0,0.0),
			horizontalScroll_frameSize=(0.0,0.0,0.0,0.0)
		)
		
		
		self.listFrame = DirectFrame(
			frameSize = (-1*RATIO,1*RATIO,-self.size*self.nbItems,0),
			frameColor=(0.7, 0.7, 0.9, 0.0),
			pos = (0,1,0),
			pad = (0,0),
			borderWidth=(0.0,0.0),
			relief = DGG.GROOVE,
		)
		self.listFrame.reparentTo(self.frame.getCanvas())
		
		y = -self.size/2.0+0.02
		for line in self.dataList:
			b = DialogButton(0,y, line[0])
			y -= 0.09
			b.reparentTo(self.listFrame)
			b.bind(DGG.B1PRESS, line[1], line[2])
			
		self.arrows = ArrowButtons(1.08,-0.13)
		self.arrows.reparentTo(self.frame)
		self.arrows.upArrow.bind(DGG.B1PRESS, self.moveIndex, [-1])
		self.arrows.downArrow.bind(DGG.B1PRESS, self.moveIndex, [1])
		
		self.index = 0
		self.setIndex(0)
		
	def setIndex(self, n, extraArgs=[]):
		
		if n<0:
			#print "useless, n<0"
			return False
		if n> self.maxIndex:
			#print "useless, n>max"
			return False
		#print "Setting index %s" % (n)
		self.index = int(n)
		self.listFrame.setPos(0,0,n*0.09)
		if self.maxDisplayedItems >= self.nbItems:
			self.arrows.upArrow.setMode("frozen")
			self.arrows.downArrow.setMode("frozen")
			return
		
		if self.index == 0:
			self.arrows.upArrow.setMode("frozen")
			self.arrows.downArrow.setMode("active")
			
		elif self.index == self.maxIndex:
			self.arrows.downArrow.setMode("frozen")
			self.arrows.upArrow.setMode("active")
		else:
			self.arrows.downArrow.setMode("active")
			self.arrows.upArrow.setMode("active")
			
	def moveIndex(self, n, extraArgs=[]):
		self.setIndex(self.index + n)
		
	def hide(self):
		self.frame.hide()
		
	def show(self):
		self.frame.show()
	
	def destroy(self):
		self.frame.destroy()
		
		
class DialogGui:
	def __init__(self, x, y, name):
		self.x = x
		self.y = y
		
		self.name = name
		self.size = (0.12,1,0.15)
		
		self.frame = DirectFrame(
			frameSize = (-1,1,-0.18,0.18),
			frameColor=(0.1, 0.1, 0.1, 0.8),
			pos = (x, 0, y),
			pad = (0,0),
			borderWidth=(0.0,0.0),
			relief = DGG.GROOVE,
		)
		
		self.portraitPath = "img/portraits/" + name + ".png"
		self.portraitImg = makeImg(-0.87,0.02,self.portraitPath, self.size)
		self.portraitImg.reparentTo(self.frame)
		
		self.mainText = makeMsg(-0.73,0.135,"", "white_transp")
		self.mainText.reparentTo(self.frame)
		
		msgList = []
		self.dialogBList = DialogButtonList(0,-0.69,msgList)
		
	def destroy(self):
		self.frame.destroy()
		self.dialogBList.destroy()
	
	def setMainText(self, text=""):
		self.mainText.setText(text)
		
	def setMenu(self, menu = []):
		self.dialogBList.destroy()
		self.dialogBList = DialogButtonList(0,-0.69,menu)
		
