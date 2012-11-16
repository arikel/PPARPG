#!/usr/bin/python
# -*- coding: utf8 -*-

from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from panda3d.bullet import BulletWorld

from keyHandler import KeyHandler
from bullet import CharacterController
from camHandler import CamHandler

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
		self.world.setGravity(Vec3(0, 0, -12.81))
		self.gravityUp = False
		
		#---------------------------------------------------------------
		# Player
		#---------------------------------------------------------------
		# CharacterController
		self.player = CharacterController(self)
		self.player.setActor('models/characters/kasia_model', {
				'walk' : 'models/characters/kasia_idle.egg'
			},
			flip = True,
			pos = (0,0,-1),
			scale = 0.125)
		self.player.setPos(0, -5, 3)
		self.player.playerModel.loop("walk")
		self.playerNp = self.player.np
		
		#---------------------------------------------------------------
		# Camera
		self.camHandler = CamHandler(self)
		
		#---------------------------------------------------------------
		# task
		#self.taskMgr.add(self.update, "update")
	
	#---------------------------------------------------------------
	# FPS
	def toggleFPS(self):
		if self.frameRateMeter:
			self.setFrameRateMeter(False)
		else:
			self.setFrameRateMeter(True)
	
	#---------------------------------------------------------------
	# Mouse cursor
	def hideCursor(self):
		props = WindowProperties()
		props.setCursorHidden(True) 
		self.win.requestProperties(props)
	def showCursor(self):
		props = WindowProperties()
		props.setCursorHidden(False)
		self.win.requestProperties(props)
	
	#---------------------------------------------------------------
	# Fog
	def setFog(self):
		myFog = Fog("Fog")
		myFog.setColor((0,0,0,1))
		myFog.setExpDensity(0.025)
		self.render.setFog(myFog)
		self.fog = True
		
	def clearFog(self):
		self.render.clearFog()
		self.fog = False
		
	def toggleFog(self):
		if self.fog:
			self.clearFog()
		else:
			self.setFog()
	
	
	#---------------------------------------------------------------
	# Camera	
	def setFov(self, x):
		self.camLens.setFov(x)
	
	def getFov(self):
		return self.camLens.getFov()[0]
	
	def setNear(self, n):
		self.camLens.setNear(n)
		
	def setFar(self, n):
		self.camLens.setFar(n)
	
	#---------------------------------------------------------------	
	# Physics
	
	def toggleGravity(self):
		if self.gravityUp:
			self.gravityUp = False
			self.world.setGravity(Vec3(0,0,-9.8))
		else:
			self.gravityUp = True
			self.world.setGravity(Vec3(0,0,9.8))
		
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
	
	def quit(self, extraArgs = []):
		self.taskMgr.stop()
	
	def stop(self, extraArgs = []):
		self.taskMgr.stop()
		
	def start(self):
		self.taskMgr.run()
		
