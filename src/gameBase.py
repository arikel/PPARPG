#!/usr/bin/python
# -*- coding: utf8 -*-

from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from panda3d.bullet import BulletWorld

from keyHandler import KeyHandler
from bullet import CharacterController

class GameBase(ShowBase):
	def __init__(self, KEY_LIST):
		ShowBase.__init__(self)
		
		#---------------------------------------------------------------
		# clock
		self.globalClock = ClockObject()
		
		#---------------------------------------------------------------
		# KeyHandler
		self.kh = KeyHandler(KEY_LIST)
		
		#---------------------------------------------------------------
		# Bullet
		self.world = BulletWorld()
		self.world.setGravity(Vec3(0, 0, -9.81))
		self.gravityUp = False
		
		#---------------------------------------------------------------
		# Player
		#---------------------------------------------------------------
		# CharacterController
		self.player = CharacterController(self)
		self.player.setActor('models/characters/female262.egg', {
				'walk' : 'models/characters/female262-walk.egg'
			},
			flip = True,
			pos = (0,0,-1),
			scale = 1.0)
		self.player.setPos(0, -5, 3)
		self.player.playerModel.loop("walk")
		self.playerNp = self.player.np
		
		#---------------------------------------------------------------
		# task
		#self.taskMgr.add(self.update, "update")
	
	def hideCursor(self):
		props = WindowProperties()
		props.setCursorHidden(True) 
		self.win.requestProperties(props)
	
	def toggleGravity(self):
		if self.gravityUp:
			self.gravityUp = False
			self.world.setGravity(Vec3(0,0,-9.8))
		else:
			self.gravityUp = True
			self.world.setGravity(Vec3(0,0,9.8))
		
	def toggleFPS(self):
		if self.frameRateMeter:
			self.setFrameRateMeter(False)
		else:
			self.setFrameRateMeter(True)
		
	def toggleDebug(self):
		if self._debug:
			self._debug = False
			self.debugNP.hide()
		else:
			self._debug = True
			self.debugNP.show()

	def updatePhysics(self, dt):
		#self.world.doPhysics(dt, 20, 1.0/180)
		self.world.doPhysics(dt)
		#cnt = self.world.contactTest(self.ground.node)
		#for boxName in self.objects:
		#	self.objects[boxName].update(dt)
		'''
			cntTest = self.world.contactTest(self.objects[boxName].node)
			cnt = cntTest.getContacts()
			for c in cnt:
				node0 = c.getNode0().getName()
				node1 = c.getNode1().getName()
				#print node0, " in contact with ", node1
		'''
		
	def update(self, task):
		self.globalClock.tick()
		t = self.globalClock.getFrameTime()
		dt = self.globalClock.getDt()
		self.updatePhysics(dt)
		self.player.update(dt)
		return task.cont
	
	def quit(self):
		self.taskMgr.stop()
