#!/usr/bin/python
# -*- coding: utf8 -*-

from panda3d.core import *
from config import *

loadPrcFileData("setup", """sync-video 0
show-frame-rate-meter #t
win-size %s %s
win-fixed-size 1
#yield-timeslice 0 
#client-sleep 0 
#multi-sleep 0
basic-shaders-only #f
fullscreen %s
#audio-library-name null
text-minfilter linear_mipmap_nearest
text-flatten 0
framebuffer-multisample 1
multisamples 2
""" % (1024, 768, False))

from direct.showbase.ShowBase import ShowBase
from direct.fsm.FSM import FSM

from panda3d.bullet import BulletWorld, BulletPlaneShape, BulletRigidBodyNode, BulletBoxShape
from panda3d.bullet import BulletDebugNode

from src import *

class Game(GameBase, FSM):
	def __init__(self):
		GameBase.__init__(self, KEY_LIST)
		
		FSM.__init__(self, 'Game')
		self.setBackgroundColor(0,0,0)
		
		self.accept("space", self.toggleFPS)
		self.accept("escape", self.taskMgr.stop)
		
		
		'''
		self.shape = BulletPlaneShape(Vec3(0, 0, 1), 1)
 
		self.node = BulletRigidBodyNode('Ground')
		self.node.addShape(self.shape)
		 
		self.np = self.render.attachNewNode(self.node)
		self.np.setPos(0, 0, 0)
		
		self.world.attachRigidBody(self.node)
		'''
		
		self.debugNode = BulletDebugNode('Debug')
		self.debugNode.showWireframe(True)
		self.debugNode.showConstraints(True)
		self.debugNode.showBoundingBoxes(True)
		self.debugNode.showNormals(True)
		self.debugNP = self.render.attachNewNode(self.debugNode)
		self.debugNP.show()
		
		
		self.bulletbox = BulletBoxShape(Vec3(0.5, 0.5, 0.5))

		self.bulletboxnode = BulletRigidBodyNode('Box')
		self.bulletboxnode.setMass(1.0)
		self.bulletboxnode.addShape(self.bulletbox)
		 
		self.bulletboxnp = self.render.attachNewNode(self.bulletboxnode)
		#self.bulletboxnp = NodePath(self.bulletboxnode)
		#self.bulletboxnp.reparentTo(self.render)
		self.bulletboxnp.setPos(0, 0, 15)
		self.bulletboxnp.setScale(5,3,0.5)
		self.world.attachRigidBody(self.bulletboxnode)
		self.model = self.loader.loadModel("models/props/crate.egg")
		self.model.reparentTo(self.bulletboxnp)
		
		
		#---------------------------------------------------------------
		# Ground (StaticTerrain)
		self.ground = StaticTerrain(self, 'models/terrain.jpg', 50)
		self.ground.setTexture(self.loader.loadTexture("models/ground.jpg"))
		
		self.sky = SkyBox(self)
		self.sky.set("teal1")
		
		self.cursor = MouseCursor(self)
		self.cursor.addCursor("cursor2")
		
		self.hideCursor()
		self.lightManager = LightManager(self)
		self.lightManager.addAmbientLight(Vec4(.5,.5,.5,1))
		self.lightManager.addPointLight(Vec4(1.0,1.0,1.0,1.0), Point3(2,-4,5))
		self.taskMgr.add(self.update, "update")
		
		print self.getAspectRatio()
		
		self.camHandler = CamHandler(self)
		self.accept(K_DRAG, self.camHandler.startDrag)
		self.accept(K_DRAG+"-up", self.camHandler.stopDrag)
		
	def update(self, task):
		self.globalClock.tick()
		t = self.globalClock.getFrameTime()
		dt = self.globalClock.getDt()
		
		self.updatePhysics(dt)
		
		self.player.update(dt,
			self.kh.getKey(K_RIGHT) - self.kh.getKey(K_LEFT),
			self.kh.getKey(K_FORWARD) - self.kh.getKey(K_BACKWARD),
			self.kh.getKey(K_JUMP),
			self.kh.getKey(K_CROUCH),
			self.kh.getKey(K_TURN_LEFT) - self.kh.getKey(K_TURN_RIGHT))
		
		self.camHandler.update()
		
		return task.cont
		
g = Game()
g.run()
