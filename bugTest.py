#!/usr/bin/python
# -*- coding: utf8 -*-

from pandac.PandaModules import *

from direct.interval.IntervalGlobal import *
from direct.task import Task
import direct.directbase.DirectStart

class NPC(NodePath):
	def __init__(self, name):
		NodePath.__init__(self, name)
		self.name = name
		self.model = loader.loadModel('smiley')
		self.model.reparentTo(self)
		self.seq = Sequence()
		self.reparentTo(render)
		
	def lookAt(self, x, y):
		self.model.lookAt(Point3(x, y, 0))
	
	def setPath(self):
		if self.seq.isPlaying():
			self.seq.pause()
		self.seq = Sequence()
		for i in range(5):
			self.seq.append(Func(self.lookAt, i, i))
			pos_i = LerpPosInterval(self.model,	5,(i, -i, 0))
			self.seq.append(pos_i)
		self.seq.loop()
		
for i in range(5):
	name = "NPC"
	n = NPC(name)
	n.setPath()
	
run()
