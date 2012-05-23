#!/usr/bin/python
# -*- coding: utf8 -*-

from panda3d.core import TransparencyAttrib

class MouseCursor:
	def __init__(self, game):
		self.game = game
		self.mode = None
		self.cursorDic = {}
		self.npDic = {}
		
	def addCursor(self, name):
		
		crosshair = self.game.loader.loadModel('models/generic/cursor.egg')
		#self.crosshair.reparentTo(render2d)
		crosshairTexture = self.game.loader.loadTexture("img/cursors/" + name + ".png")
		crosshair.setTexture(crosshairTexture,1)
		crosshair.setTransparency(TransparencyAttrib.MAlpha)
		
		dummyNP = self.game.render2d.attachNewNode(name)
		crosshair.reparentTo(dummyNP)
		crosshair.setScale(0.06,0,0.08)
		crosshair.setPos(0,5,0)
		crosshair.setColor(0.8,0.85,1,1)
		self.game.mouseWatcherNode.setGeometry(dummyNP.node())
		
		crosshair.setBin("gui-popup", 100)
		self.cursorDic[name] = crosshair
		self.npDic[name] = dummyNP
		
	def setMode(self, name):
		if name == self.mode:
			return True
		if name not in self.cursorDic:
			return False
		self.cursorDic[self.mode].hide()
		self.mode = name
		self.game.mouseWatcherNode.setGeometry(self.npDic[name].node())
		self.cursorDic[self.mode].show()
		
	
