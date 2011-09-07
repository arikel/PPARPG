#!/usr/bin/python
# -*- coding: utf8 -*-

from pandac.PandaModules import *
import direct.directbase.DirectStart
from direct.gui.DirectGui import *
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.interval.IntervalGlobal import *

from guiBase import *
from guiMenu import *

class GameGui:
	def __init__(self, mapManager):
		self.mapManager = mapManager
		self.infoLabel = makeMsgRight(0.95*RATIO,-0.95,"")
		self.objectLabel = makeMsg(-0.95*RATIO,-0.85,"")
		
	def hide(self):
		self.infoLabel.hide()
		self.objectLabel.hide()
		self.visible = False
		
	def show(self):
		self.infoLabel.show()
		self.objectLabel.show()
		self.visible = True
		
	def setInfo(self, info):
		self.infoLabel.setText(str(info))
		
	def clearInfo(self):
		self.infoLabel.setText("")
		
	def setObjInfo(self, mpos, info):
		self.objectLabel.setPos(mpos.getX()*1.33+0.1, mpos.getY()+0.02)
		self.objectLabel.setText(str(info))
		
	def clearObjInfo(self):
		self.objectLabel.setText("")
