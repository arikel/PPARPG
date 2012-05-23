#!/usr/bin/python
# -*- coding: utf8 -*-

from panda3d.core import *

class SkyBox:
	def __init__(self, game):
		self.game = game
		self.models = {}
		self.currentModel = None
		self.name = None
		
	def load(self, name):
		if name in self.models:
			return False
		path = "models/skies/" + str(name) + "/generic_skybox"
		model = self.game.loader.loadModel(path)
		model.setScale(10)
		model.setBin('background', 1)
		model.setDepthWrite(0)
		model.setLightOff()
		model.setShaderOff()
		self.models[name] = model
		
	def unload(self, name):
		if name in self.models:
			self.models[name].remove()
			del self.models[name]

	def set(self, name):
		if name is None:
			if self.currentModel:
				self.currentModel.detachNode()
			self.name = None
			self.currentModel = None
			return
			
		if name not in self.models:
			self.load(name)
		
		self.name = name
		if self.currentModel:
			self.currentModel.detachNode()
		self.currentModel = self.models[name]
		self.currentModel.reparentTo(self.game.camera)
		self.currentModel.setDepthWrite(False)
		self.currentModel.setBin('background', 1)
		self.currentModel.setCompass()
		return True
			
	def destroy(self):
		for name in self.models:
			self.models[name].remove()
	
	def clear(self):
		if self.currentModel:
			self.currentModel.detachNode()
		self.currentModel = None
		self.name = None
	
			

