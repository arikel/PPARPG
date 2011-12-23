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
		for i in range(5):
			self.seq.append(Func(self.lookAt, Point3(0,i,i)))
			pos_i = LerpPosInterval(self.model,	5,(i, -i, 0))
			self.seq.append(pos_i)
		self.seq.loop()
		
for i in range(5):
	n = NPC()
	n.setPath()
	
run()
