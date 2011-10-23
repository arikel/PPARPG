#!/usr/bin/python
# -*- coding: utf8 -*-

import sys
import os

from pandac.PandaModules import *
from direct.showbase.DirectObject import DirectObject
from direct.task import Task
from direct.directbase import DirectStart
from direct.interval.IntervalGlobal import *

class SkyBox:
	def __init__(self):
		self.models = {}
		self.currentModel = None
		self.intervals = {}
		self.task = None
		self.name = None
		
	def load(self, name):
		if name is None:return
		path = "models/skies/" + str(name) + "/generic_skybox"
		model = loader.loadModel(path)
		model.setScale(1024)
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
			self.currentModel.reparentTo(base.camera)
			self.currentModel.setDepthWrite(False)
			self.currentModel.setBin('background', 1)
			self.currentModel.setCompass()
			
			#self.start()
			return True
		else:
			print("Error : skybox %s not found." % (name))
			return False
			
	def destroy(self):
		for name in self.models:
			self.models[name].remove()
		
		#if self.model:
		#	self.model.remove()
		
			

