#!/usr/bin/python
# -*- coding: utf8 -*-

from panda3d.core import VBase3, Point3, Vec3, Vec4

from panda3d.core import NodePath, PandaNode, Geom, GeomNode
from panda3d.core import LPlanef, Plane
from panda3d.core import GeomVertexFormat, GeomVertexData
from panda3d.core import GeomVertexReader, GeomVertexWriter
from panda3d.core import GeomLinestrips
from panda3d.core import GeomTriangles, GeomTrifans

class LineDrawer:
	def __init__(self, game, color = (1,0.1,0.1,0.0)):
		self.game = game
		self.node = GeomNode("lines")
		self.np = NodePath(self.node)
		self.np.reparentTo(self.game.render)
		self.np.setShaderOff()
		self.np.setLightOff()
		self.color = color
		self.np.setColor(self.color)
		self.path = []
		self.start = (0, 0)
		self.end = (0, 0)
		
	def setStart(self, start):
		self.start = start
		#self.startModel.setPos(start[0]+0.5, start[1]+0.5, 0)
		
	def setEnd(self, end):
		self.end = end
		#self.endModel.setPos(end[0]+0.5, end[1]+0.5, 0)
		
	def clear(self):
		self.np.remove()
		self.node = GeomNode("lines")
		self.np = NodePath(self.node)
		self.np.reparentTo(self.game.render)
		self.np.setShaderOff()
		self.np.setLightOff()
		self.np.setColor(self.color)
		
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
		
	def setPath(self, path):
		self.path = path
		self.clear()
		for pos in range(len(self.path)-1):
			self.drawLine(self.path[pos], self.path[pos+1])

