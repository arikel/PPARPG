#!/usr/bin/python
# -*- coding: utf8 -*-

import direct.directbase.DirectStart

from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import *

class LightManager:
	def __init__(self, np=render):
		self.lightCenter = np.attachNewNode(PandaNode("center"))
		
		# Create Ambient Light
		self.ambientLight1 = AmbientLight('ambientLight')
		self.ambientLight1.setColor(Vec4(0.2,0.2,0.2, 1))
		self.alight = self.lightCenter.attachNewNode(self.ambientLight1)
		render.setLight(self.alight)
		#render.setShaderInput("alight0", self.alight)
		
		# point light
		self.pointlight = PointLight("Light")
		self.light = self.lightCenter.attachNewNode(self.pointlight)
		self.pointlight.setColor(Vec4(0.8,0.8,0.8,1))
		self.light.setPos(0,0,2)
		render.setLight(self.light)
		
		#render.setShaderInput("plight0", self.light)
		
		# Spotlight
		self.spot = Spotlight("spot")
		#self.spot.getLens().setNearFar(1,50)
		self.spot.getLens().setFov(60)
		self.spot.setColor(Vec4(1,1,1,1))
		self.spotlight = self.lightCenter.attachNewNode(self.spot)
		self.spotlight.setPos(-5,15,8)
		self.spotlight.lookAt(0,-15,-8)
		#self.spotlight.setHpr(0,-45,0)
		
		self.spotlight.node().setShadowCaster(True)
		#render.setLight(self.spotlight)
		#render.setShaderInput("slight0", self.spotlight)
		
		'''
		# directional light
		self.dlight1 = DirectionalLight("dlight")
		self.dlight1.setColor(Vec4(1.2,1.2,1.2,1))
		#self.dlight = self.lightCenter.attachNewNode(self.dlight1)
		self.dlight = render.attachNewNode(self.dlight1)
		self.dlight.lookAt(10,-10,-10)
		self.dlight.node().setShadowCaster(True)
		self.dlight.node().getLens().setFov(35)
		self.dlight.node().getLens().setNearFar(0.2, 200)
		self.dlight.node().setScene(render)
		self.dlight.node().getLens().setFilmSize(1280,1024)
		render.setLight(self.dlight)
		'''
