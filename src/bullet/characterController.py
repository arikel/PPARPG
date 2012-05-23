#!/usr/bin/python
# -*- coding: utf8 -*-

import math

from panda3d.core import *

from panda3d.bullet import BulletWorld, BulletPlaneShape, BulletRigidBodyNode, BulletBoxShape, BulletTriangleMesh
from panda3d.bullet import BulletDebugNode, BulletHeightfieldShape, BulletConvexHullShape, BulletTriangleMeshShape
from panda3d.bullet import ZUp, BulletCapsuleShape
from panda3d.bullet import BulletConeTwistConstraint, BulletSphericalConstraint, BulletSliderConstraint

from direct.fsm.FSM import FSM
from direct.actor.Actor import Actor

from bulletHandler import DynamicObject

#-----------------------------------------------------------------------
# Character controllers
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# helper functions
def angleBetween(A, B):
	A.normalize()
	B.normalize()
	cosAngle = A.dot(B)
	angle = math.acos(cosAngle)
	return angle*180/math.pi


#-----------------------------------------------------------------------
class CharacterController(DynamicObject, FSM):
	def __init__(self, game):
		self.game = game
		FSM.__init__(self, "Player")
		
		# key states
		# dx direction left or right, dy direction forward or backward
		self.kh = self.game.kh
		self.dx = 0
		self.dy = 0
		self.jumping = 0
		self.crouching = 0
		
		# maximum speed when only walking
		self.groundSpeed = 5.0
		
		# acceleration used when walking to rise to self.groundSpeed
		self.groundAccel = 100.0
		
		# maximum speed in the air (air friction)
		self.airSpeed = 30.0
		
		# player movement control when in the air
		self.airAccel = 10.0
		
		# horizontal speed on jump start
		self.jumpSpeed = 5.5
		
		self.turnSpeed = 5
		
		self.moveSpeedVec = Vec3(0,0,0)
		self.platformSpeedVec = Vec3(0,0,0)
		
		h = 1.75
		w = 0.4
		
		self.shape = BulletCapsuleShape(w, h - 2 * w, ZUp)
		self.node = BulletRigidBodyNode('Player')
		self.node.setMass(1.0)
		self.node.addShape(self.shape)
		self.node.setActive(True, True)
		self.node.setDeactivationEnabled(False, True)
		self.node.setFriction(200)
		#self.node.setGravity(10)
		#self.node.setFallSpeed(200)
		self.node.setCcdMotionThreshold(1e-7)
		self.node.setCcdSweptSphereRadius(0.5)
		
		self.np = self.game.render.attachNewNode(self.node)
		self.np.setPos(0, 0, 0)
		self.np.setH(0)
		#self.np.setCollideMask(BitMask32.allOn())
		
		self.game.world.attachRigidBody(self.node)
		self.playerModel = None
		self.slice_able = False
		
	def setActor(self, modelPath, animDic={}, flip = False, pos = (0,0,0), scale = 1.0):
		self.playerModel = Actor(modelPath, animDic)
		self.playerModel.reparentTo(self.np)
		self.playerModel.setScale(scale) # 1ft = 0.3048m
		if flip:
			self.playerModel.setH(180)
		self.playerModel.setPos(pos)
		self.playerModel.setScale(scale)
	
	
	#-------------------------------------------------------------------
	# Speed	
	def getSpeedVec(self):
		return self.node.getLinearVelocity()
	def setSpeedVec(self, speedVec):
		#print "setting speed to %s" % (speedVec)
		self.node.setLinearVelocity(speedVec)
		return speedVec
		
	def setPlatformSpeed(self, speedVec):
		self.platformSpeedVec = speedVec
		
	def getSpeed(self):
		return self.getSpeedVec().length()
	def setSpeed(self, speed):
		speedVec = self.getSpeedVec()
		speedVec.normalize()
		self.setSpeedVec(speedVec*speed)
	
	def getLocalSpeedVec(self):
		return self.np.getRelativeVector(self.getSpeed())
	
	def getSpeedXY(self):
		vec = self.getSpeedVec()
		return Vec3(vec[0], vec[1], 0)
	def setSpeedXY(self, speedX, speedY):
		vec = self.getSpeedVec()
		z = self.getSpeedZ()
		self.setSpeedVec(Vec3(speedX, speedY, z))
	
	def getSpeedH(self):
		return self.getSpeedXY().length()
		
	def getSpeedZ(self):
		return self.getSpeedVec()[2]
	def setSpeedZ(self, zSpeed):
		vec = self.getSpeedVec()
		speedVec = Vec3(vec[0], vec[1], zSpeed)
		return self.setSpeedVec(speedVec)
		
		
	def setLinearVelocity(self, speedVec):
		return self.setSpeedVec(speedVec)
	
	def setAngularVelocity(self, speed):
		self.node.setAngularVelocity(Vec3(0, 0, speed))
	
	def getFriction(self):
		return self.node.getFriction()
	def setFriction(self, friction):
		return self.node.setFriction(friction)
	
	#-------------------------------------------------------------------
	# Acceleration	
	def doJump(self):
		self.setSpeedZ(self.getSpeedZ()+self.jumpSpeed)
	
	def setForce(self, force):
		self.node.applyCentralForce(force)
		
	#-------------------------------------------------------------------
	# contacts
	
	#-------------------------------------------------------------------
	# update

	
		
	def update(self, dt, dx=0, dy=0, jumping=0, crouching=0, dRot=0):
		self.setR(0)
		self.setP(0)
		
		self.jumping = jumping
		self.crouching = crouching
		self.dx = dx
		self.dy = dy
		
		self.setAngularVelocity(dRot*self.turnSpeed)
		
		speedVec = self.getSpeedVec() - self.platformSpeedVec
		speed = speedVec.length()
		localSpeedVec = self.np.getRelativeVector(self.game.render, speedVec)
		pushVec = self.game.render.getRelativeVector(self.np, Vec3(self.dx,self.dy,0))
		if self.dx != 0 or self.dy != 0:
			pushVec.normalize()
		else:
			pushVec = Vec3(0,0,0)
		
		contacts = self.getContacts()
		contact = self.checkFeet()
		
		if self.jumping and contact in contacts:
			self.setFriction(0)
			self.doJump()
		
		if self.jumping:	
			self.setForce(pushVec * self.airAccel)
			
			if speed > self.airSpeed:
				self.setSpeed(self.airSpeed)
		
		else:
			if contacts:
				self.setForce(pushVec * self.groundAccel)
			else:
				self.setForce(pushVec * self.airAccel)
			
			if self.dx == 0 and self.dy == 0:
				self.setFriction(100)
			else:
				self.setFriction(0)
			
			if speed > self.groundSpeed:
				if contacts:
					self.setSpeed(self.groundSpeed)
		
		'''
		if contact in self.game.objects and contact in contacts:
			obj = self.game.objects[contact]
			if type(obj) is KinematicPlatform:
				vec = obj.getSpeedVec()
				#vec.setZ(0)
				#self.addSpeedVec(self.game.objects[contact].getSpeedVec())
				self.setForce(vec*self.node.getMass() * 24)
				#self.platformSpeedVec = self.game.objects[contact].getSpeedVec()
				#self.setSpeedVec(speedVec + self.platformSpeedVec)
			#self.setFriction(100)
			#else:
			#	self.platformSpeedVec = Vec3(0,0,0)
		'''
