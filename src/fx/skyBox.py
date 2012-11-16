#!/usr/bin/python
# -*- coding: utf8 -*-

import sys
import os

from panda3d.core import *
from direct.interval.IntervalGlobal import *

class SkyBox:
	def __init__(self, game):
		self.game = game
		self.models = {}
		self.currentModel = None
		self.intervals = {}
		self.task = None
		self.name = None
		
	def load(self, name):
		if name is None:return
		path = "models/skies/" + str(name) + "/generic_skybox"
		model = self.game.loader.loadModel(path)
		model.setScale(10)
		model.setBin('background', 1)
		model.setDepthWrite(0)
		model.setLightOff()
		model.setShaderOff()
		self.models[name] = model
		self.intervals[name] = LerpHprInterval(self.models[name], 5.0, (360,0,0))
		
	def unload(self, name):
		if name in self.models:
			#self.models[name].detachNode()
			self.models[name].remove()
			del self.models[name]

	def set(self, name):
		if name is None:
			if self.currentModel:
				self.currentModel.detachNode()
			self.name = None
			return
			
		if name in self.models:
			self.name = name
			if self.currentModel:
				self.currentModel.detachNode()
			self.currentModel = self.models[name]
			#self.currentModel.reparentTo(render)
			self.currentModel.reparentTo(self.game.camera)
			self.currentModel.setDepthWrite(False)
			self.currentModel.setBin('background', 1)
			self.currentModel.setCompass()
			
			#self.start()
			return True
		else:
			print("Error : skybox %s not found." % (name))
			return False
	
	def hide(self):
		if self.currentModel:
			self.currentModel.hide()
			
	def show(self):
		if self.currentModel:
			self.currentModel.show()
			
	def destroy(self):
		for name in self.models:
			self.models[name].remove()
		
		#if self.model:
		#	self.model.remove()
		
			
class Sky(object):
	def __init__(self, game):
		self.game = game
		self.skyNP = loader.loadModel( 'models/skies/sky.egg' )
		self.skyNP.reparentTo( self.game.render )
		self.skyNP.setScale( 4000, 4000, 1000 )
		self.skyNP.setPos( 0, 0, 0 )
		self.skyNP.setTexture( loader.loadTexture( 'img/textures/clouds.png' ) )
		self.skyNP.setShader( loader.loadShader( 'shaders/sky.sha' ) )
		#_sky      = Vec4( 0.25, 0.50, 1.0, 0.1 )            # r, g, b, skip
		_sky      = Vec4( 0.0, 0.0, 0.0, 0.1 )
		#_clouds   = Vec4( 0.004, 0.002, 0.008, 0.010 ) # vx, vy, vx, vy
		_clouds   = Vec4( 0.004, 0.002, 0.008, 0.010 )
		self.skyNP.setShaderInput( 'sky', _sky )
		self.skyNP.setShaderInput( 'clouds', _clouds )
		self.skyNP.setTransparency(True)
		
	def hide(self):
		self.skyNP.hide()
			
	def show(self):
		self.skyNP.show()
		
	
