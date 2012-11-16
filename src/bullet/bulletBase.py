#!/usr/bin/python
# -*- coding: utf8 -*-

import math

from panda3d.core import *

from panda3d.bullet import BulletWorld, BulletPlaneShape, BulletRigidBodyNode, BulletBoxShape, BulletTriangleMesh
from panda3d.bullet import BulletDebugNode, BulletHeightfieldShape, BulletConvexHullShape, BulletTriangleMeshShape
from panda3d.bullet import ZUp, BulletCapsuleShape
from panda3d.bullet import BulletConeTwistConstraint, BulletSphericalConstraint, BulletSliderConstraint


class NodePathOwner(object):
	
	
	def reparentTo(self, np):
		self.np.reparentTo(np)
	
	#-------------------------------------------------------------------
	# Pos
	#-------------------------------------------------------------------
	def getPos(self):
		return self.np.getPos()
	def setPos(self, *args):
		self.np.setPos(args)
	def getX(self):
		return self.np.getX()
	def getY(self):
		return self.np.getY()
	def getZ(self):
		return self.np.getZ()
	def setX(self, *args):
		self.np.setX(*args)
	def setY(self, *args):
		self.np.setY(*args)
	def setZ(self, *args):
		self.np.setZ(*args)
		
	#-------------------------------------------------------------------
	# Hpr
	#-------------------------------------------------------------------	
	def setHpr(self, *args):
		self.np.setHpr(args)
	def getHpr(self):
		return self.np.getHpr()
	def getH(self):
		return self.np.getH()
	def getP(self):
		return self.np.getP()
	def getR(self):
		return self.np.getR()
	def setH(self, *args):
		self.np.setH(*args)
	def setP(self, *args):
		self.np.setP(*args)
	def setR(self, *args):
		self.np.setR(*args)
	
	def lookAt(self, *args):
		self.np.lookAt(args)
	
	#-------------------------------------------------------------------
	# Shader
	#-------------------------------------------------------------------	
	def setShaderAuto(self):
		self.np.setShaderAuto()
		
	def setShaderOff(self):
		self.np.setShaderOff()
		
	def setShader(self, shader):
		self.np.setShader(shader)
		
	def setShaderInput(self, key, value):
		self.np.setShaderInput(key, value)
	
	def setTexture(self, tex):
		self.np.setTexture(tex)
	
	def setGlowOn(self):
		#ts = TextureStage('ts')
		#ts.setMode(TextureStage.MGlow)
		self.np.setTexture(self.game.ts, self.game.glowTex)
		#self.setTexture(self.game.ts, self.game.glowTex)
		self.setShaderAuto()
		
	def setGlowOff(self):
		self.np.setTexture(self.game.ts, self.game.noGlowTex)
		#self.setTexture(self.game.ts, self.game.noGlowTex)
		self.setShaderAuto()
		
#-----------------------------------------------------------------------
# Bullet classes
#-----------------------------------------------------------------------
class BulletObject(NodePathOwner):
	slice_able = False
	
	def activate(self):
		return
	
	def destroy(self):
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
		
	



#-----------------------------------------------------------------------
#

 
class StaticPackBase(object):
	def __init__(self, name, game):
		self.game = game
		self.name = name
		
		self.node = BulletRigidBodyNode(self.name)
		self.np = self.game.render.attachNewNode(self.node)
		self.game.world.attachRigidBody(self.node)
		
	def addBox(self, sx, sy, sz, px, py, pz):
		shape = BulletBoxShape(Vec3(sx/2.0, sy/2.0, sz/2.0))
		t = TransformState.makePosHprScaleShear((px, py, pz+sz/2.0), (0,0,0), (1,1,1), (0,0,0))
		self.node.addShape(shape, t)
		
	def addPlane(self, normal, offset):
		self.node.addShape(BulletPlaneShape(normal, -offset))
		
	def addTriangle(self, p1, p2, p3):
		mesh = BulletTriangleMesh()
		mesh.addTriangle(p1, p2, p3)
		shape = BulletTriangleMeshShape(mesh, dynamic=False)
		self.node.addShape(shape)
		
	def addQuad(self, p1, p2, p3, p4):
		mesh = BulletTriangleMesh()
		mesh.addTriangle(p1, p2, p3)
		mesh.addTriangle(p1, p3, p4)
		shape = BulletTriangleMeshShape(mesh, dynamic=False)
		self.node.addShape(shape)
		
	def clear(self):
		self.game.world.removeRigidBody(self.node)
		self.np.remove()
		
		self.node = BulletRigidBodyNode(self.name)
		self.np = self.game.render.attachNewNode(self.node)
		self.game.world.attachRigidBody(self.node)
		


	

"""
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
"""

