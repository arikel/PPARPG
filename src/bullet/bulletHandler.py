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

#-----------------------------------------------------------------------
# Bullet classes
#-----------------------------------------------------------------------
class BulletObject(object):
	slice_able = False
	# NodePath manipulation
	
	#for attrib in ["getPos", "setPos", "getHpr", "setHpr"]
	
	def getPos(self):
		return self.np.getPos()
	def setPos(self, *args):
		self.np.setPos(args)
	def setHpr(self, *args):
		self.np.setHpr(args)
	def setH(self, *args):
		self.np.setH(*args)
	def setP(self, *args):
		self.np.setP(*args)
	def setR(self, *args):
		self.np.setR(*args)
	
	def activate(self):
		return
	
	def destroy(self):
		#self.np.detachNode()
		self.np.remove()
		self.game.world.removeRigidBody(self.node)
	
	def getContacts(self):
		res = []
		cntTest = self.game.world.contactTest(self.node)
		cnt = cntTest.getContacts()
		return cnt
		
	# debug
	def debugOn(self):
		self.node.setDebugEnabled(True)
		
	def debugOff(self):
		self.node.setDebugEnabled(False)
		
	def toggleDebug(self):
		if self.node.isDebugEnabled():
			self.debugOff()
		else:
			self.debugOn()
	
	def onClick(self):
		return
		
	def update(self, dt):
		return
		
	def setTexture(self, tex):
		self.np.setTexture(tex)
		
class DynamicObject(BulletObject):
	
	def activate(self):
		self.node.setActive(True)
		
	def setForce(self, force):
		self.node.applyCentralForce(force)
		
	def checkFeet(self):
		p1 = Point3(self.getPos())
		p2 = Point3(self.getPos() + Point3(0,0,-1))
		
		result = self.game.world.rayTestClosest(p1, p2)
		
		#ts1 = TransformState.makePos(p1)
		#ts2 = TransformState.makePos(p2)
		#result = self.game.world.sweepTestClosest(self.shape, ts1, ts2, 0)
		
		if result.hasHit():
			pos = result.getHitPos()
			n = result.getHitNormal()
			frac = result.getHitFraction()
			node = result.getNode()
			#print "Checked feet for %s, hit : pos = %s (self pos = %s), norm = %s, frac = %s, node = %s" % (self.name, pos, self.getPos(), n, frac, node.getName())
			return node.getName()
			
		else:
			#print "nothing under %s's feet, pos = %s" % (self.name, self.getPos())
			return None
	
	
		
	def getContacts(self):
		res = []
		cntTest = self.game.world.contactTest(self.node)
		cnt = cntTest.getContacts()
		
		
		
		
		
		for c in cnt:
			mpoint = c.getManifoldPoint()
			d = mpoint.getDistance()
			mpoint.getAppliedImpulse()
			pa = mpoint.getPositionWorldOnA()
			pb = mpoint.getPositionWorldOnB()
			a = mpoint.getLocalPointA()
			b = mpoint.getLocalPointB()
			
			node0 = c.getNode0()
			node1 = c.getNode1()
			
			nodeName0 = node0.getName()
			nodeName1 = node1.getName()
			
			
			
			if nodeName0 != self.name and nodeName0 not in res:
				res.append(nodeName0)
				node = node0
				#extraSpeedVec = node.getLinearVelocity()
				#self.setSpeedVec(self.getSpeedVec() + extraSpeedVec)
			
			elif nodeName1 != self.name and nodeName1 not in res:
				res.append(nodeName1)
				node = node1
				#extraSpeedVec = node.getLinearVelocity()
				#self.setSpeedVec(self.getSpeedVec() + extraSpeedVec)
			#speed = extraSpeedVec.length()
			
			#print "Contact between %s and %s, distance = %s\n- pA = %s\n- pB = %s, speed = %s" % (nodeName0, nodeName1, d, pa, pb, speed)
			
		return res
	
	
	
	#-------------------------------------------------------------------
	# Speed	
	def getSpeedVec(self):
		return self.node.getLinearVelocity()
	def setSpeedVec(self, speedVec):
		#print "setting speed to %s" % (speedVec)
		self.node.setLinearVelocity(speedVec)
		return speedVec
		
	def addSpeedVec(self, speedVec):
		self.speedVec = self.getSpeedVec()
		self.setSpeedVec(self.speedVec + Vec3(speedVec[0], speedVec[1], 0))
		
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
	
	def getAngularVelocity(self):
		return self.node.getAngularVelocity()
		
	def setAngularVelocity(self, vec):
		self.node.setAngularVelocity(vec)
	
	def getFriction(self):
		return self.node.getFriction()
	def setFriction(self, friction):
		return self.node.setFriction(friction)

	
	

#-----------------------------------------------------------------------
# Box
class DynamicBox(DynamicObject):
	def __init__(self, name, game, pos):
		self.name = name
		self.game = game
		self.shape = BulletBoxShape(Vec3(0.5, 0.5, 0.5))
		self.node = BulletRigidBodyNode(name)
		self.node.setMass(10.0)
		self.node.addShape(self.shape)
		self.setFriction(20)
		
		self.np = self.game.render.attachNewNode(self.node)
		self.np.setPos(pos)
		self.game.world.attachRigidBody(self.node)
		self.model = self.game.loader.loadModel("models/crate.egg")
		self.model.reparentTo(self.np)
		
		self.node.setCcdMotionThreshold(1e-7)
		self.node.setCcdSweptSphereRadius(0.5)
		self.debugOff()
		self.slice_able = True
	
	def update(self, dt):
		#self.activate()
		#if self.node.isActive():
		#	return
		contact = self.checkFeet()
		contacts = self.getContacts()
		
		if contact in self.game.objects and contact in contacts:
			obj = self.game.objects[contact]
			if type(obj) is KinematicPlatform:
				self.activate()
				self.setAngularVelocity(self.getAngularVelocity()*0.9)
				self.setFriction(0.1)
				#print "%s is a box sliding on %s" % (self.name, obj.name)
				#self.addSpeedVec(self.game.objects[contact].getSpeedVec())
				#self.setForce(obj.getSpeedVec()*self.node.getMass() * 100)
				platform_speed = obj.getSpeedVec()
				force = platform_speed * self.node.getMass() * 50
				#self.setSpeedXY(platform_speed[0], platform_speed[1])
				self.setSpeedVec(platform_speed)
				#self.setAngularVelocity(0)
				
				#self.node.addLin(obj.getSpeedVec()*self.node.getMass() * 100)
				#self.node.applyCentralForce(force)
				#self.setForce(force)
				#self.setFriction(20)
				#self.setPos(self.getPos() + obj.getSpeedVec())
				#self.node.setActive(False)
			else:
				self.setFriction(20)
#-----------------------------------------------------------------------
# Model
class DynamicModel(DynamicObject):
	def __init__(self, name, modelPath, game, pos):
		self.name = name
		self.modelPath = modelPath
		self.game = game
		
		self.model = self.game.loader.loadModel(self.modelPath)
		geomNodes = self.model.findAllMatches('**/+GeomNode')
		self.geomNode = geomNodes.getPath(0).node()
		self.geom = self.geomNode.getGeom(0)
		self.shape = BulletConvexHullShape()
		self.shape.addGeom(self.geom)
		
		self.node = BulletRigidBodyNode(self.name)
		self.node.setMass(10.0)
		self.node.addShape(self.shape)
		
		self.np = self.game.render.attachNewNode(self.node)
		self.np.setPos(pos)
		self.game.world.attachRigidBody(self.node)
		
		self.model.reparentTo(self.np)
		
		self.node.setCcdMotionThreshold(1e-7)
		self.node.setCcdSweptSphereRadius(0.5)
		self.slice_able = True

#-----------------------------------------------------------------------
# Np
class DynamicNp(DynamicObject):
	def __init__(self, name, model, game, pos):
		self.name = name
		self.game = game
		
		self.model = model
		self.geomNode = self.model.node()
		self.geom = self.geomNode.getGeom(0)
		
		# with triangle mesh it crashes
		#mesh = BulletTriangleMesh()
		#mesh.addGeom(self.geom)
		#self.shape = BulletTriangleMeshShape(mesh, dynamic=True)
		
		# with convex hull
		self.shape = BulletConvexHullShape()
		self.shape.addGeom(self.geom)
		
		self.node = BulletRigidBodyNode(self.name)
		self.node.setMass(10.0)
		self.node.addShape(self.shape)
		
		self.np = self.game.render.attachNewNode(self.node)
		self.np.setPos(pos)
		self.game.world.attachRigidBody(self.node)
		
		self.model.reparentTo(self.np)
		
		self.node.setCcdMotionThreshold(1e-7)
		self.node.setCcdSweptSphereRadius(0.5)
		self.slice_able = True
		
#-----------------------------------------------------------------------
# Terrain
class StaticTerrain(BulletObject):
	def __init__(self, game, imgPath, height):
		self.game = game
		self.img = PNMImage(Filename(imgPath))
		self.shape = BulletHeightfieldShape(self.img, height, 2)
		self.node = BulletRigidBodyNode('Ground')
		self.node.addShape(self.shape)
		
		self.np = self.game.render.attachNewNode(self.node)
		self.np.setPos(0, 0, 0)
		self.np.setScale(1, 1, 1)
		self.game.world.attachRigidBody(self.node)
		
		self.terrain = GeoMipTerrain('terrain')
		self.terrain.setHeightfield(self.img)
		self.terrain.generate()
		self.terrainNP = self.terrain.getRoot()
		self.offset = self.img.getXSize() / 2.0 - 0.5
		self.terrainNP.setSz(height)
		self.terrainNP.setPos(-self.offset,-self.offset,-height/2.0)
		#self.terrainNP.flattenStrong()
		self.terrainNP.reparentTo(self.np)
		
		self.terrainNP.show()
		self.debugOff()
		self.slice_able = False

#-----------------------------------------------------------------------
# Model
class StaticModel(BulletObject):
	def __init__(self, name, modelPath, displayModelPath, game, pos):
		self.name = name
		self.modelPath = modelPath
		self.game = game
		
		self.model = self.game.loader.loadModel(self.modelPath)
		geomNodes = self.model.findAllMatches('**/+GeomNode')
		self.geomNode = geomNodes.getPath(0).node()
		self.geom = self.geomNode.getGeom(0)
		
		#self.shape = BulletConvexHullShape()
		#self.shape.addGeom(self.geom)
		
		mesh = BulletTriangleMesh()
		mesh.addGeom(self.geom)
		self.shape = BulletTriangleMeshShape(mesh, dynamic=False)
		
		self.node = BulletRigidBodyNode(self.name)
		self.node.addShape(self.shape)
		
		self.np = self.game.render.attachNewNode(self.node)
		self.np.setPos(pos)
		self.game.world.attachRigidBody(self.node)
		
		#self.model.reparentTo(self.np)
		
		self.displayModel = self.game.loader.loadModel(displayModelPath)
		self.displayModel.reparentTo(self.np)
		self.displayModel.setTwoSided(True)
		self.slice_able = False

class KinematicPlatform(BulletObject):
	def __init__(self, name, game, x, y, z, pos):
		
		self.name = name
		self.game = game
		self.shape = BulletBoxShape(Vec3(x, y, z))
		self.node = BulletRigidBodyNode(self.name)
		self.node.addShape(self.shape)
		
		self.np = self.game.render.attachNewNode(self.node)
		self.np.setPos(pos)
		self.game.world.attachRigidBody(self.node)
		self.model = self.game.loader.loadModel("models/platform.egg")
		self.model.reparentTo(self.np)
		self.model.setScale(x*2,y*2,z*2)
		
		self.node.setCcdMotionThreshold(1e-7)
		self.node.setCcdSweptSphereRadius(0.5)
		#self.node.setFriction(5)
		#self.debugOff()
		self.speedVec = Vec3(0,0,0)
		self.lastPos = Vec3(self.getPos())
		self.slice_able = False
		
	def getSpeedVec(self):
		return self.speedVec
		
	def update(self, dt):
		currentPos = Vec3(self.getPos())
		
		currentPos.setZ(0)
		
		dVec = currentPos - self.lastPos
		self.speedVec = dVec * (1.0 / dt)
		#print "speedVec = %s, currentPos = %s, lastPos = %s, dVec = %s" % (self.speedVec, currentPos, self.lastPos, dVec)
		self.lastPos = currentPos
		
		self.lastPos.setZ(0)
		
class DynamicPlatform(DynamicObject):
	def __init__(self, name, game, x, y, z, pos):
		self.name = name
		self.game = game
		self.shape = BulletBoxShape(Vec3(x, y, z))
		self.node = BulletRigidBodyNode(self.name)
		self.node.addShape(self.shape)
		
		self.np = self.game.render.attachNewNode(self.node)
		self.np.setPos(pos)
		self.game.world.attachRigidBody(self.node)
		#self.model = self.game.loader.loadModel("models/crate.egg")
		#self.model.reparentTo(self.np)
		
		self.node.setCcdMotionThreshold(1e-7)
		self.node.setCcdSweptSphereRadius(0.5)
		#self.node.setFriction(5)
		#self.debugOff()
		self.speedVec = Vec3(0,0,0)
		self.lastPos = Vec3(self.getPos())
		self.slice_able = False
		#self.node.setCcdMotionThreshold(1e-7)
		#self.node.setCcdSweptSphereRadius(0.5)
		
	def update(self, dt):
		return
