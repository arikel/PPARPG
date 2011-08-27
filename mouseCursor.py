#!/usr/bin/python
# -*- coding: utf8 -*-

from pandac.PandaModules import *

class MouseCursor:
	def __init__(self):
		
		self.crosshair = loader.loadModel('models/generic/cursor.egg')
		#self.crosshair.reparentTo(render2d)
		self.crosshairTexture = loader.loadTexture("img/generic/crosshair1.png")
		self.crosshair.setTexture(self.crosshairTexture,1)
		self.crosshair.setTransparency(TransparencyAttrib.MAlpha)

		self.dummyNP = render2d.attachNewNode('crosshair')
		self.crosshair.reparentTo(self.dummyNP)
		self.crosshair.setScale(0.03,0,0.04)
		self.crosshair.setPos(0,5,0)
		self.crosshair.setColor(0.8,0.85,1,1)
		base.mouseWatcherNode.setGeometry(self.dummyNP.node())
		
		self.crosshair2 = loader.loadModel('models/generic/cursor.egg')
		self.crosshair2.reparentTo(render2d)
		self.crosshair2Texture = loader.loadTexture("img/generic/crosshair2.png")
		self.crosshair2.setTexture(self.crosshair2Texture,1)
		self.crosshair2.setTransparency(TransparencyAttrib.MAlpha)
		#self.interval = LerpHprInterval(self.crosshair2, 2, (0,0,360))
		#self.interval.loop()
		
		
		self.dummyNP2 = render2d.attachNewNode('crosshair2')
		self.crosshair2.reparentTo(self.dummyNP2)
		self.crosshair2.setScale(0.03,0,0.04)
		self.crosshair2.setPos(0.03,5,-0.035)
		self.crosshair2.setColor(0.8,0.85,1,1)
		
		self.crosshair.setBin("gui-popup", 100)
		self.crosshair2.setBin("gui-popup", 100)
		
		
		self.mode = 0 # or 1
		self.toggle()
		
	def setMode(self, n=0):
		if n != self.mode:
			self.mode = n
			if n == 0:
				base.mouseWatcherNode.setGeometry(self.dummyNP.node())
				#self.crosshair2.detachNode()
				self.crosshair2.hide()
				self.crosshair.show()
				#self.crosshair.reparentTo(self.dummyNP)
			else:
				base.mouseWatcherNode.setGeometry(self.dummyNP2.node())
				#self.crosshair.detachNode()
				self.crosshair2.show()
				self.crosshair.hide()
				#self.crosshair2.reparentTo(self.dummyNP2)
				
		
	def toggle(self):
		if self.mode == 0:
			self.setMode(1)
		else:
			self.setMode(0)
