#!/usr/bin/python
# -*- coding: utf8 -*-

from pandac.PandaModules import *
from mouseCursor import Clicker

class WallBuilder:
	def __init__(self, width = 0.5, height = 1.6, texPath="img/textures/collision.png", pointList = []):
		self.width = width
		self.height = height
		self.texPath = texPath
		self.wallPath = []
		
		self.node = GeomNode("tiledMesh")
		self.gvd = GeomVertexData('name', GeomVertexFormat.getV3n3c4t2(), Geom.UHStatic)
		self.geom = Geom(self.gvd)
		self.prim = GeomTriangles(Geom.UHStatic)
		
		self.nbVertices = 0
		self.nbFaces = 0
		
		if self.texPath is not None:
			self.tex = loader.loadTexture(self.texPath)
		
		self.np = None
		
		#self.pointList = [Point3(0,0,0), Point3(250,0,0), Point3(250,120,0), Point3(0,120,0), Point3(0,0,0)]
		self.pointList = pointList
		self.makeFaces()
		
	def makeFaces(self):
		if self.np:
			self.np.remove()
		
		self.node = GeomNode("tiledMesh")
		self.gvd = GeomVertexData('name', GeomVertexFormat.getV3n3c4t2(), Geom.UHStatic)
		self.geom = Geom(self.gvd)
		
		self.prim = GeomTriangles(Geom.UHStatic)
		
		self.vertex = GeomVertexWriter(self.gvd, 'vertex')
		self.texcoord = GeomVertexWriter(self.gvd, 'texcoord')
		self.color = GeomVertexWriter(self.gvd, 'color')
		self.normal = GeomVertexWriter(self.gvd, 'normal')
		
		n = 0
		for i in range(len(self.pointList)-1):
			self.makeWall(n, self.pointList[i], self.pointList[i+1], self.height)
			n += 20
		
		
		self.prim.closePrimitive()
		self.geom.addPrimitive(self.prim)
		self.node.addGeom(self.geom)
		
		self.np = NodePath(self.node)
		self.np.reparentTo(render)
		#self.np.setTwoSided(True)
		self.np.setTexture(self.tex)
		#self.np.setColor(0,0,1.0,0.1)
		self.np.setTransparency(True)
		
		
	def makeWall(self, startN, p1, p2, h=1.0):
		self.addWallRight(p1, p2, h)
		self.addWallLeft(p1, p2, h)
		self.addWallTop(p1, p2, h)
		self.addWallFront(p1, p2, h)
		self.addWallBack(p1, p2, h)
		
		self.makeWallRight(startN+0)
		self.makeWallLeft(startN+4)
		self.makeWallTop(startN+8)
		self.makeWallFront(startN+12)
		self.makeWallBack(startN+16)
		
	def makeWallLeft(self, startN):
		self.prim.addVertices(startN, startN+1, startN+2)
		self.prim.addVertices(startN+1, startN+3, startN+2)
		
	def makeWallRight(self, startN):
		self.prim.addVertices(startN, startN+2, startN+1)
		self.prim.addVertices(startN+1, startN+2, startN+3)
		
	def makeWallTop(self, startN):
		self.makeWallLeft(startN)
		
	def makeWallFront(self, startN):
		self.makeWallRight(startN)
		
	def makeWallBack(self, startN):
		self.makeWallLeft(startN)
	
	def addQuad(self, pos1, pos2, pos3, pos4, vecLeft, scale=1):
		
		self.vertex.addData3f(pos1)
		self.texcoord.addData2f(0, 0)
		self.color.addData4f(1, 1, 1, 1)
		self.normal.addData3f(vecLeft)
		
		self.vertex.addData3f(pos2)
		self.texcoord.addData2f(1*scale, 0)
		self.color.addData4f(1, 1, 1, 1)
		self.normal.addData3f(vecLeft)
		
		self.vertex.addData3f(pos3)
		self.texcoord.addData2f(0, 1)
		self.color.addData4f(1, 1, 1, 1)
		self.normal.addData3f(vecLeft)
		
		self.vertex.addData3f(pos4)
		self.texcoord.addData2f(1*scale, 1)
		self.color.addData4f(1, 1, 1, 1)
		self.normal.addData3f(vecLeft)
		
		self.nbVertices += 4
		self.nbFaces += 1
	
	def addWallRight(self, p1, p2, h=1.0):
		vecForward = Vec3(p2-p1)
		vecRight = Vec3(0,0,1).cross(vecForward)
		vecRight.normalize()
		vecRight = vecRight * self.width
		pos1 = p1 + vecRight
		pos2 = p1 + vecRight + vecForward
		pos3 = p1 + vecRight + Vec3(0,0,h)
		pos4 = p1 + vecRight + vecForward + Vec3(0,0,h)
		scale = vecForward.length()
		self.addQuad(pos1, pos2, pos3, pos4, vecRight, scale)
		
	def addWallLeft(self, p1, p2, h=1.0):
		vecForward = Vec3(p2-p1)
		vecLeft = Vec3(0,0,1).cross(-vecForward)
		vecLeft.normalize()
		vecLeft = vecLeft * self.width
		
		pos1 = p1 + vecLeft
		pos2 = p1 + vecLeft + vecForward
		pos3 = p1 + vecLeft + Vec3(0,0,h)
		pos4 = p1 + vecLeft + vecForward + Vec3(0,0,h)
		scale = vecForward.length()
		self.addQuad(pos1, pos2, pos3, pos4, vecLeft, scale)
		

		
	def addWallTop(self, p1, p2, h=1.0):
		vecForward = Vec3(p2-p1)
		vecLeft = Vec3(0,0,1).cross(-vecForward)
		vecLeft.normalize()
		vecLeft = vecLeft * self.width
		pos1 = p1 + vecLeft + Vec3(0,0,h)
		pos2 = p1 + vecLeft + vecForward + Vec3(0,0,h)
		pos3 = p1 - vecLeft + Vec3(0,0,h)
		pos4 = p1 - vecLeft + vecForward + Vec3(0,0,h)
		
		self.addQuad(pos1, pos2, pos3, pos4, vecLeft, 1)
		
	def addWallFront(self, p1, p2, h=1.0):
		vecForward = Vec3(p2-p1)
		vecLeft = Vec3(0,0,1).cross(-vecForward)
		vecLeft.normalize()
		vecLeft = vecLeft * self.width
		pos1 = p1 + vecLeft
		pos2 = p1 - vecLeft
		pos3 = p1 + vecLeft + Vec3(0,0,h)
		pos4 = p1 - vecLeft + Vec3(0,0,h)
		
		self.addQuad(pos1, pos2, pos3, pos4, vecLeft, self.width)
		
	def addWallBack(self, p1, p2, h=1.0):
		vecForward = Vec3(p2-p1)
		vecLeft = Vec3(0,0,1).cross(-vecForward)
		vecLeft.normalize()
		vecLeft = vecLeft * self.width
		pos1 = p1 + vecLeft + vecForward
		pos2 = p1 - vecLeft + vecForward
		pos3 = p1 + vecLeft + Vec3(0,0,h) + vecForward
		pos4 = p1 - vecLeft + Vec3(0,0,h) + vecForward
		
		self.addQuad(pos1, pos2, pos3, pos4, vecLeft, self.width)
		
	def hideTile(self, x, y):
		if (0<=x<self.x) and (0<=y<self.y):
			if self.data[y][x]!=0:
				self.data[y][x] = 0
				row = (self.x*y + x)*4
				
				self.vertex = GeomVertexWriter(self.gvd, 'vertex')
				self.texcoord = GeomVertexWriter(self.gvd, 'texcoord')
				self.color = GeomVertexWriter(self.gvd, 'color')
				self.normal = GeomVertexWriter(self.gvd, 'normal')
				
				self.vertex.setRow(row)
				self.texcoord.setRow(row)
				self.color.setRow(row)
				self.normal.setRow(row)
				
				self.addEmptyTile(x, y)
				#self.update()
	
	def showTile(self, x, y):
		if (0<=x<self.x) and (0<=y<self.y):
			if self.data[y][x]!=1:
				self.data[y][x] = 1
				row = (self.x*y + x)*4
				
				self.vertex = GeomVertexWriter(self.gvd, 'vertex')
				self.texcoord = GeomVertexWriter(self.gvd, 'texcoord')
				self.color = GeomVertexWriter(self.gvd, 'color')
				self.normal = GeomVertexWriter(self.gvd, 'normal')
				
				self.vertex.setRow(row)
				self.texcoord.setRow(row)
				self.color.setRow(row)
				self.normal.setRow(row)
				
				self.addWallTile(x, y)
				
				#self.update()
	
	def destroy(self):
		if self.np:
			self.np.remove()
		del self.data
		del self.gvd


if __name__=="__main__":
	w = WallBuilder(0.1,2.5, "img/textures/wood_wall.jpg")
	import sys
	base.accept("escape", sys.exit)
	run()



