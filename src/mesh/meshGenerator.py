#!/usr/bin/python
# -*- coding: utf8 -*-
import random

from panda3d.core import *

from gameBase import GameBase

#-----------------------------------------------------------------------
class VertexData(object):
	def __init__(self, x, y, z, nx, ny, nz, u, v, c1, c2, c3, c4):
		# vertex position data
		self.v = (x, y, z)
		# vertex normal
		self.n = (nx, ny, nz)
		# vertex colors
		self.c = (c1, c2, c3, c4)
		# vertex texture coordinates
		self.t = (u, v)
		
	def setPos(self, x, y, z):
		self.v = (x, y, z)
		
	def setNormal(self, nx, ny, nz):
		self.n = (nx, ny, nz)
		
	def setColor(self, c1, c2, c3, c4 = 0):
		self.c = (c1, c2, c3, c4)
		
	def setTexcoord(self, u, v):
		self.t = (u, v)
		
#-----------------------------------------------------------------------
class MeshGenerator(object):
	def __init__(self, game, texPath="models/rs-metal07.jpg"):
		self.game = game
		self.texPath = texPath
		self.tex = self.game.loader.loadTexture(self.texPath)
		self.reset()
		
	#-------------------------------------------------------------------
	# 
	def reset(self):
		self.node = GeomNode("meshGenerator")
		self.vdata = GeomVertexData('meshGenVdata', GeomVertexFormat.getV3n3c4t2(), Geom.UHStatic)
		self.geom = Geom(self.vdata)
		self.node.addGeom(self.geom)
		self.prim = GeomTriangles(Geom.UHStatic)
		self.geom.addPrimitive(self.prim)
		
		self.np = None
		self.nbPrims = 0
		self.nbVertices = 0
		
		self.initReaders()
		self.initWriters()
	
	#-------------------------------------------------------------------
	# 	
	def initReaders(self):
		self.vReader = GeomVertexReader(self.vdata, 'vertex')
		self.nReader = GeomVertexReader(self.vdata, 'normal')
		self.tReader = GeomVertexReader(self.vdata, 'texcoord')
		self.cReader = GeomVertexReader(self.vdata, 'color')
		
	def initWriters(self):
		self.vWriter = GeomVertexWriter(self.vdata, 'vertex')
		self.nWriter = GeomVertexWriter(self.vdata, 'normal')
		self.tWriter = GeomVertexWriter(self.vdata, 'texcoord')
		self.cWriter = GeomVertexWriter(self.vdata, 'color')
		
		
	#-------------------------------------------------------------------
	# 
	def addVertexData(self, vertexData):
		self.vWriter.addData3f(vertexData.v)
		self.nWriter.addData3f(vertexData.n)
		self.tWriter.addData2f(vertexData.t)
		self.cWriter.addData4f(vertexData.c)
		self.nbVertices += 1
		
	def getVertexData(self, index):
		self.initReaders()
		self.vReader.setRow(index)
		self.nReader.setRow(index)
		self.cReader.setRow(index)
		self.tReader.setRow(index)
		x, y, z = self.vReader.getData3f()
		nx, ny, nz = self.nReader.getData3f()
		u, v = self.tReader.getData2f()
		c1, c2, c3, c4 = self.cReader.getData4f()
		
		return VertexData(x, y, z, nx, ny, nz, u, v, c1, c2, c3, c4)
		
	def setVertexData(self, index, vertexData):
		if index > self.nbVertices-1:
			return False
		
		self.initWriters()
		self.vWriter.setRow(index)
		self.nWriter.setRow(index)
		self.cWriter.setRow(index)
		self.tWriter.setRow(index)
		
		self.vWriter.setData3f(vertexData.v)
		self.nWriter.setData3f(vertexData.n)
		self.tWriter.setData2f(vertexData.t)
		self.cWriter.setData4f(vertexData.c)
	
	#-------------------------------------------------------------------
	# 	
	def addTriangle(self, a, b, c):
		
		startN = self.nbVertices
		
		self.addVertexData(a)
		self.addVertexData(b)
		self.addVertexData(c)
		
		self.prim.addVertices(startN, startN+1, startN+2)
		self.nbPrims += 1
	
	#-------------------------------------------------------------------
	# 
	def addQuad(self, a, b, c, d):
		startN = self.nbVertices
		
		self.addVertexData(a)
		self.addVertexData(b)
		self.addVertexData(c)
		self.addVertexData(d)
		
		self.prim.addVertices(startN, startN+1, startN+2)
		self.prim.addVertices(startN, startN+2, startN+3)
		self.nbPrims += 2
	
	
	
	def generate(self):
		self.prim.closePrimitive()
		
		self.np = NodePath(self.node)
		self.np.reparentTo(self.game.render)
		self.np.setTexture(self.tex)
		self.np.setTransparency(TransparencyAttrib.MAlpha)
	
	
		
	def moveUV(self, index, x, y):
		vdata = self.getVertexData(index)
		vdata.t = (vdata.t[0] + x, vdata.t[1] + y)
		self.setVertexData(index, vdata)

#-----------------------------------------------------------------------
class MeshGame(GameBase):
	def __init__(self):
		GameBase.__init__(self)
		
	def startUVMove(self, m):
		self.taskMgr.remove("moveUV")
		self.m = m
		self.taskMgr.add(self.moveUVTask, "moveUV")
		
	def moveUVTask(self, task):
		dt = self.globalClock.getDt()
		for i in range(self.m.nbVertices):
			self.m.moveUV(i, -dt/1000.0, -dt/3000.0)
		return task.cont
	
	def update(self, dt):
		self.globalClock.tick()
		t = self.globalClock.getFrameTime()
		dt = self.globalClock.getDt()
		return
	
#-----------------------------------------------------------------------
if __name__ == "__main__":
	
	loadPrcFileData("setup", """sync-video 0
show-frame-rate-meter #t
win-size %s %s
win-fixed-size 1
yield-timeslice 0 
client-sleep 0 
multi-sleep 0
basic-shaders-only #f
fullscreen %s
audio-library-name null
#text-minfilter linear_mipmap_nearest
#text-flatten 0
#framebuffer-multisample 1
#multisamples 2
bullet-additional-damping 1
bullet-solver-iterations 10
framebuffer-stencil #t
#dump-generated-shaders #t
""" % (800, 600, False))
	
	from gameBase import GameBase
	g = MeshGame()
	shader = Shader.load("shaders/point.sha")
	g.render.setShader(shader)
	
	g.render.setShaderInput("light", g.np)
	#g.render.setShaderInput("cam", g.camera)
	
	#g.toggleFPS()
	#g.addLight()
	#g.render.setShaderOff()
	
	g.accept("escape", g.quit)
	m = MeshGenerator(g)
	
	v1 = VertexData(-1,0,-1, 0,-1,1, 0,0, 0,0,1,1)
	v2 = VertexData(1,0,-1,  0,-1,1, 0,1, 1,1,1,1)
	v3 = VertexData( 1,0,1,  0,-1,1, 1,1, 1,0,0,1)
	v4 = VertexData( -1,0,1, 0,-1,1, 1,0, 1,1,1,1)
	
	v5 = VertexData(-1,-1,-1, 0,0,1, 0,0, 0,0,0,1)
	v6 = VertexData(1,-1,-1,  0,0,1, 0,1, 1,1,1,1)
	v7 = VertexData( 1,1,-1,  0,0,1, 1,1, 0,0,0,1)
	v8 = VertexData( -1,1,-1, 0,0,1, 1,0, 1,1,1,1)
	
	m.addQuad(v1, v2, v3, v4)
	m.addQuad(v5, v6, v7, v8)
	m.generate()
	
	#v5 = VertexData( -1,0,2, 0,-1,0, 1.5,0, 1,1,1,0)
	#m.setVertexData(3, v5)
	
	g.startUVMove(m)
	
	#print "read row = %s" % (m.vReader.getReadRow())
	#print "write row = %s" % (m.vWriter.getWriteRow())
	g.run()
