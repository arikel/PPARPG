#!/usr/bin/python
# -*- coding: utf8 -*-

from pandac.PandaModules import *

from direct.interval.IntervalGlobal import *
from direct.task import Task
import direct.directbase.DirectStart

class NPC:
	def __init__(self):
		self.model = loader.loadModel('smiley')
		self.model.reparentTo(render)
		self.seq = Sequence()
		
	def lookAt(self, target):
		self.model.lookAt(target)
	
	def setPath(self):
		if self.seq.isPlaying():
			self.seq.pause()
		self.seq.append(Func(self.lookAt, Point3(0,5,5)))
		self.seq.loop()
		
for i in range(5):
	n = NPC()
	n.setPath()
	
run()
