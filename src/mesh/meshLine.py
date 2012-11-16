#!/usr/bin/python
# -*- coding: utf8 -*-

import random

from panda3d.core import VBase3, Point2, Point3, Vec3, Vec4

from panda3d.core import NodePath, PandaNode, Geom, GeomNode
from panda3d.core import LPlanef, Plane
from panda3d.core import GeomVertexFormat, GeomVertexData
from panda3d.core import GeomVertexReader, GeomVertexWriter
from panda3d.core import GeomLinestrips
from panda3d.core import GeomTriangles, GeomTrifans

from meshUtils import *

class LineMesh:
	def __init__(self, game, color=(1,1,1,1)):
		self.game = game
		self.node = GeomNode("lines")
		self.np = NodePath(self.node)
		self.np.reparentTo(self.game.render)
		self.np.setShaderOff()
		self.format = makeVertexFormat()
		self.vertices = []
		self.lines = []
		self.color = color
		
	def getNbVertices(self):
		return len(self.vertices)
		
	def getNbLines(self):
		return len(self.lines)
	
	def getRandomColor(self):
		return getRandomColor()
		'''
		c1 = random.uniform(0,1)
		c2 = random.uniform(0,1)
		c3 = random.uniform(0,1)
		return (c1, c2, c3, 1)
		'''
		
	nbVertices = property(getNbVertices)
	nbLines = property(getNbLines)
	
	def reset(self):
		self.clearMesh()
		self.vertices = []
		self.lines = []
	
	def clearMesh(self):
		#if self.np:
		#	self.np.remove()
		self.node.removeAllGeoms()
		
		self.vdata = GeomVertexData ('name', self.format, Geom.UHStatic)
		self.vWriter = GeomVertexWriter (self.vdata, 'vertex')
		self.cWriter = GeomVertexWriter (self.vdata, 'color')
		
		self.geom = Geom(self.vdata)
		#self.node = GeomNode("lines")
		
		self.node.addGeom(self.geom)
		
		#self.np = NodePath(self.node)
		#self.np.reparentTo(self.game.render)
		
	def draw(self):
		self.clearMesh()
		#print "vertices : %s" % (self.vertices)
		
		for p in self.vertices:
			self.vWriter.addData3f(p[0], p[1], p[2])
			self.cWriter.addData4f(self.color)
			
		lines = GeomLinestrips (Geom.UHStatic)
		for line in self.lines:
			lines.addVertices(line[0], line[1])
			lines.closePrimitive()
		self.geom.addPrimitive (lines)
		
	def addLineStrip(self, pointList, closed = False):
		nbPts = len(pointList)
		if nbPts < 2:
			return
		
		nbV = self.nbVertices
		
		#for p in pointList:
		#	self.vertices.append(p)
		self.vertices.extend(pointList)
		
		for i in range(nbPts-1):
			self.lines.append((nbV + i, nbV + i + 1))
		if closed:
			self.lines.append((nbV + nbPts - 1, nbV))
	
	def addBox(self, size, pos, rot=0):
		x = size[0] / 2.0
		y = size[1] / 2.0
		z = size[2] / 2.0
		
		#print "drawing lines, x = %s" % (x)
		# base points
		p1 = Point3(-x,-y,-z)
		p2 = Point3(x,-y,-z)
		p3 = Point3(x,y,-z)
		p4 = Point3(-x,y,-z)
		# top points
		p1t = Point3(-x,-y,z)
		p2t = Point3(x,-y,z)
		p3t = Point3(x,y,z)
		p4t = Point3(-x,y,z)
		
		pList = [p1, p2, p3, p4, p1t, p2t, p3t, p4t]
		#dP = Point3(pos[0], pos[1], pos[2])
		newList = translatePoints(pList, dP)
		newList = rotatePoints(newList, rot)
		
		self.addLineStrip(newList[0:4], True)
		self.addLineStrip(newList[4:8], True)
		for i in range(4):
			self.addLineStrip([newList[i], newList[i+4]], False)
		
	
		
	def addSideWall(self, pointList, dh=2.0, closed = False):
		nbPts = len(pointList)
		if nbPts < 2:
			return
		try:
			dh = float(dh)
			dh = (0, 0, dh)
		except:
			pass
		
		topPointList = translatePoints(pointList, dh)
		self.addLineStrip(pointList, closed)
		self.addLineStrip(topPointList, closed)
		
		for i in range(nbPts):
			p1 = pointList[i]
			p1t = topPointList[i]
			self.addLineStrip([p1, p1t])
		
	def addThickWall(self, pointList, dh, thickness, closed, capped = False):
		rPointList, lPointList = getWallPoints(pointList, dh, thickness, closed, capped)
		
		if closed:
			self.addSideWall(rPointList, dh, True)
			self.addSideWall(lPointList, dh, True)
			
		else:
			newList = []
			newList.extend(rPointList)
			lPointList.reverse()
			newList.extend(lPointList)
			self.addSideWall(newList, dh, True)
		
			#print "adding wall, pointList = %s" % (newList)
		#self.addPrism(newList, h)
		
	def addPrism(self, pointList, dh = 0, pos=(0,0,0), rot=(0,0,0), closed = True):
		nbPts = len(pointList)
		if nbPts < 3:
			return
		try:
			dh = float(dh)
			dh = (0, 0, dh)
		except:
			pass
		
		topPointList = translatePoints(pointList, dh)
		
		pointList = rotatePoints(pointList, rot)
		topPointList = rotatePoints(topPointList, rot)
		
		pointList = translatePoints(pointList, pos)
		topPointList = translatePoints(topPointList, pos)
		
		self.addLineStrip(pointList, True)
		self.addLineStrip(topPointList, True)
		for i in range(nbPts):
			self.addLineStrip([pointList[i], topPointList[i+nbPts]], False)
		
		
	def addCylinder(self, pA, pB, radius = 2.0, nbSides = 16):
		normalVec = pB - pA
		basePoints = getCirclePoints(pA, radius, normalVec, nbSides)
		
		self.addPrism(basePoints, normalVec)
	
	def addCylinderShear(self, pA, normalVec, dh, radius = 2.0, nbSides = 16, pos=(0,0,0), rot=(0,0,0), closed = True):
		pointList = getCirclePoints(pA, radius, normalVec, nbSides)
		self.addPrism(pointList, dh, pos, rot, closed)
