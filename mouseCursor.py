#!/usr/bin/python
# -*- coding: utf8 -*-

from pandac.PandaModules import *
from direct.directbase import DirectStart

class MouseCursor:
	def __init__(self):
		
		self.crosshair = loader.loadModel('models/generic/cursor.egg')
		#self.crosshair.reparentTo(render2d)
		self.crosshairTexture = loader.loadTexture("img/generic/crosshair1.png")
		self.crosshair.setTexture(self.crosshairTexture,1)
		self.crosshair.setTransparency(TransparencyAttrib.MAlpha)

		self.dummyNP = render2d.attachNewNode('crosshair')
		self.crosshair.reparentTo(self.dummyNP)
		self.crosshair.setScale(0.03,0,0.04)
		self.crosshair.setPos(0,5,0)
		self.crosshair.setColor(0.8,0.85,1,1)
		base.mouseWatcherNode.setGeometry(self.dummyNP.node())
		
		self.crosshair2 = loader.loadModel('models/generic/cursor.egg')
		self.crosshair2.reparentTo(render2d)
		self.crosshair2Texture = loader.loadTexture("img/generic/crosshair3.png")
		self.crosshair2.setTexture(self.crosshair2Texture,1)
		self.crosshair2.setTransparency(TransparencyAttrib.MAlpha)
		#self.interval = LerpHprInterval(self.crosshair2, 2, (0,0,360))
		#self.interval.loop()
		
		
		self.dummyNP2 = render2d.attachNewNode('crosshair2')
		self.crosshair2.reparentTo(self.dummyNP2)
		self.crosshair2.setScale(0.03,0,0.04)
		self.crosshair2.setPos(0.03,5,-0.035)
		self.crosshair2.setColor(0.8,0.85,1,1)
		
		self.crosshair.setBin("gui-popup", 100)
		self.crosshair2.setBin("gui-popup", 100)
		
		
		self.mode = 0 # or 1
		self.toggle()
		
	def setMode(self, n=0):
		if n != self.mode:
			self.mode = n
			if n == 0:
				base.mouseWatcherNode.setGeometry(self.dummyNP.node())
				#self.crosshair2.detachNode()
				self.crosshair2.hide()
				self.crosshair.show()
				#self.crosshair.reparentTo(self.dummyNP)
			else:
				base.mouseWatcherNode.setGeometry(self.dummyNP2.node())
				#self.crosshair.detachNode()
				self.crosshair2.show()
				self.crosshair.hide()
				#self.crosshair2.reparentTo(self.dummyNP2)
				
		
	def toggle(self):
		if self.mode == 0:
			self.setMode(1)
		else:
			self.setMode(0)


#-----------------------------------------------------------------------
# Clicker
#-----------------------------------------------------------------------
class Clicker:
	def __init__(self, z=0):
		"""
		This class is used to handle clicks on the collision / pathfinding grid
		"""
		self.plane = Plane(Vec3(0, 0, 1), Point3(0, 0, z))
		self.picker = CollisionTraverser()
		self.pq     = CollisionHandlerQueue()
		self.pickerNode = CollisionNode('mouseRay')
		self.pickerNP = camera.attachNewNode(self.pickerNode)
		self.pickerNode.setFromCollideMask(BitMask32.bit(1))
		self.pickerRay = CollisionRay()
		self.pickerNode.addSolid(self.pickerRay)
		self.picker.addCollider(self.pickerNP, self.pq)
		#self.picker.showCollisions(render)
		
	def setHeight(self, z):
		self.plane = Plane(Vec3(0, 0, 1), Point3(0, 0, z))
		print "Clicker set new height : %s" % (z)
		
	def getMouseObject(self, np=render):
		if base.mouseWatcherNode.hasMouse():
			#self.picker.showCollisions(np)
			
			mpos = base.mouseWatcherNode.getMouse()
			self.pickerRay.setFromLens(base.camNode, mpos.getX(), mpos.getY())
			self.picker.traverse(np)
			if self.pq.getNumEntries() > 0:
				self.pq.sortEntries()
				#print "y'a eu %s collisions!!!" % (self.pq.getNumEntries())
				res = self.pq.getEntry(0)
				#print "Entry = %s" % (res)
				#print dir(res)
				return res
			#else:
			#	print "y'a rien eu..."
		return None
		
	def getMouseTilePos(self, mpos=None):
		if mpos is None:
			if base.mouseWatcherNode.hasMouse():
				mpos = base.mouseWatcherNode.getMouse()
			else:
				return None
			
		pos3d = Point3()
		nearPoint = Point3()
		farPoint = Point3()
		base.camLens.extrude(mpos, nearPoint, farPoint)
		if self.plane.intersectsLine(pos3d,
				render.getRelativePoint(camera, nearPoint),
				render.getRelativePoint(camera, farPoint)):
			
			x = pos3d.getX()
			y = pos3d.getY()
			return int(x), int(y)
		return None

	def getMousePos(self, mpos=None):
		if mpos is None:
			if base.mouseWatcherNode.hasMouse():
				mpos = base.mouseWatcherNode.getMouse()
			else:
				return None
			
		pos3d = Point3()
		nearPoint = Point3()
		farPoint = Point3()
		base.camLens.extrude(mpos, nearPoint, farPoint)
		if self.plane.intersectsLine(pos3d,
				render.getRelativePoint(camera, nearPoint),
				render.getRelativePoint(camera, farPoint)):
			
			x = pos3d.getX()
			y = pos3d.getY()
			return x, y
		return None
