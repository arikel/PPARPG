#!/usr/bin/python
# -*- coding: utf8 -*-

from panda3d.core import *

class LightManager(object):
	def __init__(self, game):
		self.game = game
		
	def addAmbientLight(self, color):
		self.ambientLight = AmbientLight('ambientLight')
		self.ambientLight.setColor(color)
		self.alight = self.game.render.attachNewNode(self.ambientLight)
		self.game.render.setLight(self.alight)
	
	def addPointLight(self, color, pos):
		self.pointLight = PointLight("pointLight")
		self.plight = self.game.render.attachNewNode(self.pointLight)
		self.pointLight.setColor(color)
		self.plight.setPos(pos)
		self.game.render.setLight(self.plight)
	
	def addDirectionalLight(self, color, pos, lookAt):
		self.dirlight = DirectionalLight("dLight")
		self.dlight = self.game.render.attachNewNode(self.dirlight)
		self.dirlight.setColor(color)
		self.dlight.setPos(pos)
		self.dlight.lookAt(lookAt)
		self.game.render.setLight(self.dlight)
		
	def toggleLight(self):
		pass
	
	def clearLight(self):
		self.game.render.clearLight()
