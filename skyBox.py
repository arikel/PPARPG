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
		
	def load(self, name):
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
			self.models[name].detachNode()
			del self.models[name]
			
	def start(self):
		if not (taskMgr.hasTaskNamed("skyTask")):
			taskMgr.add(self.task, "skyTask")
		
				
	def stop(self):
		if (taskMgr.hasTaskNamed("skyTask")):
			#print("Stopping skyTask")
			taskMgr.remove("skyTask")
		if self.currentModel:
			self.currentModel.detachNode()
		
	def task(self, task):
		self.currentModel.setPos(base.camera.getPos(render))
		return Task.cont
			
	def set(self, name):
		if name in self.models:
			if self.currentModel:
				self.currentModel.detachNode()
			self.currentModel = self.models[name]
			#self.currentModel.reparentTo(render)
			self.currentModel.reparentTo(base.camera)
			self.currentModel.setCompass()
			
			#self.start()
			return True
		else:
			print("Error : skybox %s not found." % (name))
			return False
			
			
	def clear(self, extraArgs=[]):
		#self.currentModel.detachNode()
		self.stop()


