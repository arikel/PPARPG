#!/usr/bin/python
# -*- coding: utf8 -*-

import math
import random

from panda3d.core import *

from panda3d.bullet import BulletWorld, BulletPlaneShape, BulletRigidBodyNode, BulletBoxShape, BulletTriangleMesh
from panda3d.bullet import BulletDebugNode, BulletHeightfieldShape, BulletConvexHullShape, BulletTriangleMeshShape
from panda3d.bullet import ZUp, BulletCapsuleShape
from panda3d.bullet import BulletConeTwistConstraint, BulletSphericalConstraint, BulletSliderConstraint

from direct.actor.Actor import Actor

from direct.interval.IntervalGlobal import *

from bulletDynamic import DynamicObject

#-----------------------------------------------------------------------
# helper functions
def angleBetween(A, B):
	A.normalize()
	B.normalize()
	cosAngle = A.dot(B)
	angle = math.acos(cosAngle)
	return angle*180/math.pi


class BulletNPC(DynamicObject):
	def __init__(self, name, game, pos):
		self.game = game
		self.name = name
		
		self.jumping = 0
		self.crouching = 0
		
		# maximum speed when only walking
		self.groundSpeed = 4.0
		
		# acceleration used when walking to rise to self.groundSpeed
		self.groundAccel = 150.0
		
		self.groundFriction = 0.0
		
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
		self.node = BulletRigidBodyNode(self.name)
		self.node.setMass(1.0)
		self.node.addShape(self.shape)
		self.node.setActive(True, True)
		self.node.setDeactivationEnabled(False, True)
		self.node.setFriction(self.groundFriction)
		#self.node.setGravity(10)
		#self.node.setFallSpeed(200)
		self.node.setCcdMotionThreshold(1e-7)
		
		# do not use setCcdSweptSphereRadius
		# it messes up the bite contact test
		#self.node.setCcdSweptSphereRadius(0.5)
		
		self.node.setAngularFactor(Vec3(0,0,1))
		
		self.np = self.game.render.attachNewNode(self.node)
		self.setPos(pos)
		self.setH(0)
		#self.np.setCollideMask(BitMask32.allOn())
		
		self.game.world.attachRigidBody(self.node)
		self.playerModel = Actor("models/monsters/ghoul2.egg", {"idle":"models/monsters/ghoul2-idle.egg", "walk" : "models/monsters/ghoul2-walk.egg"})
		self.playerModel.setScale(0.15)
		self.playerModel.setZ(0.15)
		self.playerModel.reparentTo(self.np)
		
		interval = Wait(random.uniform(0,1))
		i2 = Func(self.startWalkAnim)
		seq = Sequence()
		seq.append(interval)
		seq.append(i2)
		seq.start()
		
		self.growlTimer = 5.0
		self.sound = None
		self.alive = True
		
		self.targetNp = NodePath(self.name)
		
		self.brainTimer = 0.0
		self.brainDelay = 1.2
		
		self.currentForce = Vec3(0,0,0)
		
	def startWalkAnim(self):
		self.playerModel.loop("walk")
		
	def stopWalkAnim(self):
		self.playerModel.loop("idle")
		
	def checkFront(self):
		p1 = Point3(self.getPos())
		direction = self.game.playerNp.getPos() - self.getPos()
		direction.normalize()
		direction = direction * 2.0
		p2 = Point3(self.getPos() + direction)
		
		result = self.game.world.rayTestClosest(p1, p2)
		
		#ts1 = TransformState.makePos(p1)
		#ts2 = TransformState.makePos(p2)
		#result = self.game.world.sweepTestClosest(self.shape, ts1, ts2, 0)
		
		if result.hasHit():
			pos = result.getHitPos()
			n = result.getHitNormal()
			frac = result.getHitFraction()
			node = result.getNode()
			return node.getName()
		return None
	
	def checkRight(self):
		p1 = Point3(self.getPos())
		direction = self.game.playerNp.getPos() - self.getPos()
		direction.normalize()
		right = direction.cross(Vec3(0,0,1))
		right = right * 2.0
		p2 = Point3(self.getPos() + right)
		result = self.game.world.rayTestClosest(p1, p2)
		
		if result.hasHit():
			pos = result.getHitPos()
			n = result.getHitNormal()
			frac = result.getHitFraction()
			node = result.getNode()
			return node.getName()	
		return None
	
	def checkLeft(self):
		p1 = Point3(self.getPos())
		direction = self.game.playerNp.getPos() - self.getPos()
		direction.normalize()
		left = -direction.cross(Vec3(0,0,1))
		left = left * 2.0
		p2 = Point3(self.getPos() + left)
		result = self.game.world.rayTestClosest(p1, p2)
		
		if result.hasHit():
			pos = result.getHitPos()
			n = result.getHitNormal()
			frac = result.getHitFraction()
			node = result.getNode()
			return node.getName()
		return None
				
	def updateDirection(self):
		direction = self.game.playerNp.getPos() - self.getPos()
		direction.setZ(0)
		direction.normalize()
		direction = direction * self.groundAccel
		right = direction.cross(Vec3(0,0,1))
		left = -right
		
		inFront = self.checkFront()
		inRight = self.checkRight()
		inLeft = self.checkLeft()
		
		if inFront == "boxpack":
			if inRight == "boxpack":
				if inLeft == "boxPack":
					self.currentForce = -direction
					
				else:
					self.currentForce = left
					
			else:
				self.currentForce = right
		else:
			self.currentForce = direction
			
	def update(self, dt = 0.0):
		if not self.alive:
			return
		
		self.brainTimer -= dt
		if self.brainTimer <= 0.0:
			self.updateDirection()
			self.brainTimer = self.brainDelay
		
		self.setForce(self.currentForce)
		self.capSpeedXY()
		
		speedVec = self.getSpeedVec()
		
		self.targetNp.setPos(self.getPos() + speedVec)
		self.lookAt(self.targetNp)
		
		# growl!
		self.growlTimer -= dt
		if self.growlTimer <= 0.0:
			if self.sound:
				self.game.soundDic3D[self.sound].stop()
				self.game.detachSound(self.sound)
			
			growlIndex = random.randint(1, len(self.game.zombieGrowlSounds))
			soundName = "monster-" + str(growlIndex)
			self.sound = soundName
			self.game.attachSound(soundName, self.np)
			self.game.playSound3D(soundName)
			self.growlTimer = 1.0 + random.uniform(0.0, 1.0)
			
			#print "Growl from %s" % (self.name)
		
		# bite! # player is the only one checking for that now
		#res = self.getContacts()
		#if "player" in res:
			#print "%s took a bite on player at %s!" % (self.name, self.game.globalClock.getFrameTime())
			#self.game.onDie()
		
	def destroy(self):
		self.alive = False
		self.game.world.removeRigidBody(self.node)
		self.stopWalkAnim()
		self.np.setTransparency(True)
		self.np.setColor(1,1,1,1)
		self.setGlowOff()
		
		i1 = Wait(random.uniform(0,1))
		i2 = LerpColorInterval(self.np, 1.0, (1,1,1,0))
		i3 = Func(self.np.remove)
		seq = Sequence()
		seq.append(i1)
		seq.append(i2)
		seq.append(i3)
		seq.start()
		
			
