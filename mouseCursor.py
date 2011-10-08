#!/usr/bin/python
# -*- coding: utf8 -*-

from pandac.PandaModules import *
from direct.directbase import DirectStart

from guiBase import *

class MouseCursor:
	def __init__(self):
		self.img = {}
		self.img["default"] = loader.loadTexture("img/cursors/cursor3.png")
		self.img["talk"] = loader.loadTexture("img/cursors/mouth.png")
		self.img["hand"] = loader.loadTexture("img/cursors/hand.png")
		
		self.crosshair = loader.loadModel('models/generic/cursor.egg')
		self.crosshair.setTransparency(TransparencyAttrib.MAlpha)

		self.dummyNP = render2d.attachNewNode('crosshair')
		self.crosshair.reparentTo(self.dummyNP)
		self.crosshair.setScale(0.075,0,0.075*RATIO)
		self.crosshair.setPos(0,0,0)
		#self.crosshair.setColor(0.8,0.85,1,1)
		base.mouseWatcherNode.setGeometry(self.dummyNP.node())
		
		self.crosshair.setBin("gui-popup", 100)
		self.mode = None
		self.setMode("default")
		
	def setMode(self, mode="default"):
		if self.mode != mode:
			self.crosshair.setTexture(self.img[mode],1)
			self.mode = mode
			if self.mode == "default":
				self.crosshair.setScale(0.075,0,0.075*RATIO)
			else:
				self.crosshair.setScale(0.0375,0,0.0375*RATIO)
		
	def setImage(self):
		pass

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
			self.picker.showCollisions(np)
			
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
