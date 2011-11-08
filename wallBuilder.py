#!/usr/bin/python
# -*- coding: utf8 -*-
import random

from pandac.PandaModules import *
from mouseCursor import Clicker

class WallBuilder:
	def __init__(self, width = 0.5, height = 1.6, texPath="img/textures/collision.png", pointList = []):
		self.width = width
		self.height = height
		self.texPath = texPath
		
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
		
	def getSaveData(self):
		data = []
		data.append(self.width)
		data.append(self.height)
		data.append(self.texPath)
		data.append(self.pointList)
		return data
		
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
		
		
	def makeWall(self, startN, p1, p2, h=None):
		if h is None:
			h = self.height
		
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
	
	'''	
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
	'''
	
	def destroy(self):
		if self.np:
			self.np.remove()
		#del self.data
		del self.gvd

class RockWallBuilder:
	def __init__(self, np, pointList=[]):
		print "creating RockWall"
		self.np = np
		self.pointList = pointList
		if len(self.pointList)<2:
			return
		
		self.rocks = []
		baseScale = 0.95
		rndScale = 0.95
		step = 2.5
		
		for i in range(len(self.pointList)-1):
			p1 = self.pointList[i]
			p2 = self.pointList[i+1]
			dist = (p2-p1).length()
			fac = step/dist
			p0 = p2-p1
			stepVec = Vec3(p0.getX()*fac,p0.getY()*fac,p0.getZ()*fac)
			n = 0
			while (n * step < dist):
				p = p1 + Vec3(n*stepVec[0],n*stepVec[1],n*stepVec[2])
				#print "adding rock at %s" % (p)
				rock = loader.loadModel("models/props/rock2")
				rock.reparentTo(render)
				rock.setPos(p)
				rock.setScale(baseScale+random.random()*rndScale)
				rock.setH(random.random()*180)
				self.rocks.append(rock)
				n = n+1
	
	def destroy(self):
		for rock in self.rocks:
			rock.remove()
		
class ModelWallBuilder:
	def __init__(self, np, modelPath, texPathList=["img/textures/concrete01.jpg"], baseScale=1.0, rndScale=0.0, step=1.0, tilt=180.0, pointList=[]):
		
		self.np = np
		self.modelPath = modelPath
		self.texPathList = texPathList
		
		self.pointList = pointList
		
		if len(self.pointList)<2:
			return
		
		self.baseScale = baseScale
		self.rndScale = rndScale
		self.step = step
		self.tilt = tilt
		self.rocks = []
		
		for i in range(len(self.pointList)-1):
			p1 = self.pointList[i]
			p2 = self.pointList[i+1]
			dist = (p2-p1).length()
			fac = self.step/dist
			p0 = p2-p1
			stepVec = Vec3(p0.getX()*fac,p0.getY()*fac,p0.getZ()*fac)
			n = 0
			while (n * self.step < dist):
				p = p1 + Vec3(n*stepVec[0],n*stepVec[1],n*stepVec[2])
				#print "adding rock at %s" % (p)
				rock = loader.loadModel(self.modelPath)
				rock.setTexture(loader.loadTexture(self.texPathList[random.randint(0,len(self.texPathList)-1)]), 1)
				
				rock.reparentTo(render)
				rock.setPos(p)
				rock.setScale(self.baseScale+random.random()*self.rndScale)
				rock.setH(random.random()*self.tilt)
				self.rocks.append(rock)
				n = n+1
	
	def getRockNbBetween(self, p1, p2):
		dist = (p2-p1).length()
		n = 1
		while (n * self.step < dist):
			n = n+1
		return n
		
	def removeLastPoint(self):
		if len(self.pointList)>1:
			nb = self.getRockNbBetween(self.pointList[-2], self.pointList[-1])
			for i in range(nb):
				self.rocks[-i-1].detachNode()
				#self.rocks.remove(self.rocks[-i-1])
				#del self.rocks[-i-1]
			#self.pointList.remove(self.pointList[-1])
			
			self.pointList.pop(-1)
			
	def destroy(self):
		for rock in self.rocks:
			rock.remove()
		
	def getSaveData(self):
		data = []
		data.append(self.modelPathList)
		data.append(self.texPathList)
		data.append(self.baseScale)
		data.append(self.rndScale)
		data.append(self.step)
		data.append(self.tilt)
		data.append(self.pointList)
		
		
if __name__=="__main__":
	w = WallBuilder(0.1,2.5, "img/textures/wood_wall.jpg", [Point3(0,0,0),Point3(10,0,0)])
	import sys
	base.accept("escape", sys.exit)
	run()



