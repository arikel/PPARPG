#!/usr/bin/python
# -*- coding: utf8 -*-

import direct.directbase.DirectStart
from direct.showbase.DirectObject import DirectObject
from direct.task import Task
from direct.interval.IntervalGlobal import *
from direct.gui.OnscreenText import OnscreenText
from direct.filter.CommonFilters import CommonFilters
from direct.fsm.FSM import FSM

import sys
import cPickle as pickle


from map import *
'''
class Drawer:
	def __init__(self):
		self.node = GeomNode("lines")
		self.np = NodePath(self.node)
		self.np.reparentTo(render)
		self.np.setShaderOff()
		self.np.setLightOff()
		self.path = []
		self.h = 0.05

	def clear(self):
		#self.np.remove()
		print pdir(self.node)
		self.node.removeAllGeoms()
		self.node = GeomNode("lines")
		self.np = NodePath(self.node)
		self.np.reparentTo(render)
		self.np.setShaderOff()
		self.np.setLightOff()
		
	def destroy(self):
		self.np.detachNode()
		del self.np
		
	def drawLine(self, start, end):
		#print "Draw line : %s, %s" % (str(start), str(end))
		self.node.addGeom(self.line(start, end))
	
	def line (self, start, end):
		# since we're doing line segments, just vertices in our geom
		format = GeomVertexFormat.getV3()
	   
		# build our data structure and get a handle to the vertex column
		vdata = GeomVertexData ('', format, Geom.UHStatic)
		vertices = GeomVertexWriter (vdata, 'vertex')
		   
		# build a linestrip vertex buffer
		lines = GeomLinestrips (Geom.UHStatic)
	   
		vertices.addData3f (start[0], start[1], start[2])
		vertices.addData3f (end[0], end[1], end[2])
	   
		lines.addVertices (0, 1)
		 
		lines.closePrimitive()
	   
		geom = Geom (vdata)
		geom.addPrimitive (lines)
		# Add our primitive to the geomnode
		#self.gnode.addGeom (geom)
		return geom
		
class ColGrid:
	def __init__(self, x=120, y=80):
		self.plane = Plane(Vec3(0, 0, 1), Point3(0, 0, 0))
		self.x = x
		self.y = y
		self.h = 0.2
		
		self.data = []
		self.colDic = {}
		for y in range(self.y):
			tmp = []
			for x in range(self.x):
				tmp.append(0)
			self.data.append(tmp)
			self.colDic[(x, y)] = None
			
		self.gridDrawer = Drawer()
		for x in range(self.x+1):
			self.gridDrawer.drawLine(Point3(x,0,self.h), (x,self.y,self.h))
		for y in range(self.y+1):
			self.gridDrawer.drawLine(Point3(0,y,self.h), (map.x,y,self.h))
		self.gridDrawer.np.flattenStrong()
		self.gridDrawer.np.setColor(0.8,0.5,0.5)
		
		self.closedTiles = []
		self.colDrawer = Drawer()
		self.colDrawer.np.setColor(1,0,0)
		
	def closeTile(self, x, y):
		if (not(0<=x < self.x)) or (not(0<=y<self.y)):
			return
		if (x, y) in self.colDic:
			if self.colDic[(x, y)] is not None:
				return
		if self.data[y][x] == 1:
			return
			
		
		self.data[y][x] = 1
		self.colDrawer.drawLine(Point3(x,y,0.2), Point3(x+1, y+1, 0.2))
		self.colDrawer.drawLine(Point3(x,y+1,0.2), Point3(x+1, y, 0.2))
		self.colDic[(x, y)] = self.colDrawer.node.getNumGeoms()
		
	def openTile(self, x, y):
		if (not(0<=x < self.x)) or (not(0<=y<self.y)):
			return
		if (x, y) in self.colDic:
			if self.colDic[(x, y)] is None:
				return
		i = self.colDic[(x, y)]
		self.colDrawer.node.removeGeom(i*2)
		self.colDrawer.node.removeGeom(i*2) # and not i*2 + 1
		self.colDic[(x, y)] = None
		
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
		
	def fill(self):
		self.colDrawer.node.removeAllGeoms()
		self.closedTiles = []
		for x in range(self.x):
			for y in range(self.y):
				self.closeTile(x, y)
'''

map = Map()
map.name = "hello"
map.x = 120
map.y = 80
map.collision = []
for y in range(map.y):
	tmp = []
	for x in range(map.x):
		tmp.append(0)
	map.collision.append(tmp)
map.groundTex = "img/textures/ice01.jpg"
map.groundTexScale = 5.0
#map.collisionGrid = CollisionGrid(map, map.name, map.groundTex, None, map.groundTexScale)
#map.collisionGrid.data = map.collision
#map.collisionGrid.rebuild()
map.ground = FlatGround(map)
map.innerWall = InnerWall(map, 4.0, "img/textures/wood03.jpg", 5.0)

l1 = [Point3(20,0.5,0), Point3(20,15.5,0)]
map.walls.append(WallBuilder(0.4, 3.0, "img/textures/bborder03.jpg", [Point3(20,0,0), Point3(20,15,0)]))
map.walls.append(WallBuilder(0.4, 3.0, "img/textures/bborder03.jpg", [Point3(12,0,0), Point3(12,15,0)]))
	
map.setSky("daysky0")

#map.setBgSound("sounds/wind.ogg")
map.setBgMusic("music/Irradiated_Dreams.ogg")

map.collisionGrid = CollisionGrid(map)

#grid = ColGrid(map.x, map.y)

def opentile(extra = []):
	x, y = map.collisionGrid.getMouseTilePos()
	map.collisionGrid.hideTile(x, y)
	
def closetile(extra = []):
	a = map.collisionGrid.getMouseTilePos()
	if a is None:return
	x, y = a[0], a[1]
	for X, Y in ((x-1,y-1), (x, y-1), (x+1, y-1), (x-1,y), (x, y), (x+1, y), (x-1,y+1), (x, y+1), (x+1, y+1)):
		map.collisionGrid.showTile(X, Y)

map.collisionGrid.adding = False
map.collisionGrid.removing = False

def startAdd(extras = []):
	map.collisionGrid.adding = True
	map.collisionGrid.removing = False
	
def stopAdd(extras=[]):
	map.collisionGrid.adding = False
	
def startRem(extras = []):
	map.collisionGrid.removing = True
	map.collisionGrid.adding = False
	
def stopRem(extras=[]):
	map.collisionGrid.removing = False
	
	

def updateCol(task):
	if map.collisionGrid.adding:
		closetile()
	elif map.collisionGrid.removing:
		opentile()
		
	return task.cont


base.accept("escape", sys.exit)
base.accept("mouse1", startAdd)
base.accept("mouse3", startRem)
base.accept("mouse1-up", stopAdd)
base.accept("mouse3-up", stopRem)
base.accept("f", map.collisionGrid.fill)

base.setFrameRateMeter(True)
base.camLens.setNearFar(1,500)
base.disableMouse()
base.camera.setPos(50,5,15)
base.camera.lookAt(50,25,0)

taskMgr.add(updateCol, "updateCol")

run()
