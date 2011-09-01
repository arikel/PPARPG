#!/usr/bin/python
# -*- coding: utf8 -*-

import random

from pandac.PandaModules import *

#-----------------------------------------------------------------------
# Decor building functions and classes
#-----------------------------------------------------------------------

def makeFloor(nbCases, scalex, scaley, texpath):
	cm = CardMaker('card')
	cm.setUvRange(Point2(scalex/nbCases,scaley/nbCases), Point2(0,0))
	cm.setHasNormals(True)
	#card = render.attachNewNode(cm2.generate())
	card = NodePath(cm.generate())
	img = loader.loadTexture(texpath)
	img.setWrapU(Texture.WMRepeat)
	img.setWrapV(Texture.WMRepeat)
	
	card.setTexture(img)
	card.setScale(scalex,1,scaley)
	card.setPos(0,0,0.0)
	card.setHpr(0,-90,0)
	#card.setTwoSided(True)
	#card.setTransparency(TransparencyAttrib.MAlpha)
	return card
	
def makeWall(scalex, scaley, scaleTex):
	cm = CardMaker('card')
	cm.setUvRange((scalex/scaleTex,0), (0,scaley/scaleTex))
	cm.setHasNormals(True)
	card = NodePath(cm.generate())
	img = loader.loadTexture("img/textures/oldstone4.jpg")
	card.setTexture(img)
	card.setScale(scalex,1,scaley)
	#card.setHpr(0,0,0)
	card.setTwoSided(True)
	card.setTransparency(TransparencyAttrib.MAlpha)
	return card

class MapWall:
	def __init__(self, x, y,z=0):
		self.walls = []
		
		height = 6.0
		texScale = 5.0
		
		wall1 = makeWall(x, height, texScale)
		wall1.reparentTo(render)
		wall1.setPos(0,y,z)
		self.walls.append(wall1)
		
		wall1 = makeWall(x, height, texScale)
		wall1.reparentTo(render)
		wall1.setPos(x,0,z)
		wall1.setHpr(180,0,0)
		self.walls.append(wall1)
		
		wall1 = makeWall(y, height, texScale)
		wall1.reparentTo(render)
		wall1.setPos(0,0,z)
		wall1.setHpr(90,0,0)
		self.walls.append(wall1)
		
		wall1 = makeWall(y, height, texScale)
		wall1.reparentTo(render)
		wall1.setPos(x,y,z)
		wall1.setHpr(-90,0,0)
		self.walls.append(wall1)
		
	def destroy(self):
		for wall in self.walls:
			wall.remove()
	
		
#-----------------------------------------------------------------------
# CollisionGrid
#  this class handles the ground : a dynamic mesh for the collision grid,
#  and either a textured geoMipTerrain or a flat card to walk on.
#  Each Map has its own CollisionGrid
#-----------------------------------------------------------------------
class CollisionGrid:
	def __init__(self, x=50, y=30, name=None, texPath="img/textures/ice01.jpg", geoMipPath = None):
		self.name = name
		print "CollisionGrid : initiating %s" % (name)
		
		self.x = x
		self.y = y
		self.texPath = texPath
		self.geoMipPath = geoMipPath
		
		self.data = [] # [[1,1,1,1,0,1,0,0,...], [1,0,0,...]... ]
		for y in range(self.y):
			tmp = []
			for x in range(self.x):
				tmp.append(0)
			self.data.append(tmp)
				
		
		self.node = GeomNode("tiledMesh")
		self.gvd = GeomVertexData('name', GeomVertexFormat.getV3n3c4t2(), Geom.UHStatic)
		self.geom = Geom(self.gvd)
		self.prim = GeomTriangles(Geom.UHStatic)
		
		self.update()
		
		i = 0
		for x in range(self.x * self.y):
			self.prim.addVertices(i, i + 3, i + 2)
			self.prim.addVertices(i, i + 2, i + 1)
			i += 4
		
		self.prim.closePrimitive()
		self.geom.addPrimitive(self.prim)
		self.node.addGeom(self.geom)
		
		self.np = NodePath(self.node)
		self.np.reparentTo(render)
		#self.np.setTwoSided(True)
		#self.np.setTransparency(True)
		if self.texPath is not None:
			self.tex = loader.loadTexture(self.texPath)
		self.colTex = loader.loadTexture("img/textures/collision.png")
		self.np.setTexture(self.colTex)
		#self.np.setColor(0,0,1.0,0.1)
		self.np.setTransparency(True)
		
		self.hasGeoMip = False
		self.terrain = None
		self.terrainNP = None
		self.terrainScale = 0
		
		if self.geoMipPath is not None:
			self.ground = None
			self.initGeoMip()
			
		else:
			
			self.ground = makeFloor(8, self.x, self.y, self.texPath)
			self.ground.reparentTo(render)
			
	def initGeoMip(self):
		if self.ground:
			self.ground.remove()
			
		if self.terrainNP:
			self.terrainNP.remove()
			
		self.hasGeoMip = True
		self.terrain = GeoMipTerrain("ground")
		self.terrain.setHeightfield(self.geoMipPath)
		#self.terrain.setMinLevel(2)
		#self.terrain.setBruteforce(True)
		self.terrainScale = 5.0
		self.terrainImgSize = 65.0
		self.terrainNP = self.terrain.getRoot()
		self.terrainNP.reparentTo(render)
		self.terrainNP.setScale(self.x/self.terrainImgSize,self.y/self.terrainImgSize,self.terrainScale)
		#self.terrainNP.setPos(0,0,-self.terrainScale)
		self.terrain.generate()
		self.terrainNP.setTexture(loader.loadTexture(self.texPath))
		self.terrainNP.setTexScale(TextureStage.getDefault(),self.terrainImgSize/10,self.terrainImgSize/10)
		self.terrainNP.flattenStrong()
		#self.terrainNP.setCollideMask(BitMask32(1))
		
	def removeGeoMip(self):
		if self.terrainNP:
			self.terrainNP.remove()
			self.hasGeoMip = False
			self.terrain = None
			self.terrainNP = None
			self.terrainScale = 0
			self.ground = makeFloor(8, self.x, self.y, self.texPath)
			self.ground.reparentTo(render)
			self.update()
		
	def addGeoMip(self, geomipPath, texPath="img/textures/ice01.jpg", imgSize = 65.0, scale = 5.0):
		if self.terrainNP:
			self.terrainNP.remove()
		if self.ground:
			self.ground.remove()
		
		self.geoMipPath = geomipPath
		self.texPath = texPath
		
		self.hasGeoMip = True
		self.terrain = GeoMipTerrain("ground")
		self.terrain.setHeightfield(self.geoMipPath)
		#self.terrain.setMinLevel(2)
		#self.terrain.setBruteforce(True)
		self.terrainScale = scale
		self.terrainImgSize = imgSize
		self.terrainNP = self.terrain.getRoot()
		self.terrainNP.reparentTo(render)
		self.terrainNP.setScale(self.x/self.terrainImgSize,self.y/self.terrainImgSize,self.terrainScale)
		#self.terrainNP.setPos(0,0,-self.terrainScale)
		self.terrain.generate()
		self.terrainNP.setTexture(loader.loadTexture(self.texPath))
		self.terrainNP.setTexScale(TextureStage.getDefault(),self.terrainImgSize/10,self.terrainImgSize/10)
		self.terrainNP.flattenStrong()
		
	def collisionHide(self):
		self.np.hide()
		
	def collisionShow(self):
		self.np.show()
		
	def getTileHeight(self, x, y):
		if not self.hasGeoMip:
			return 0
		if not (0<=x<self.x): return 0 #- self.terrainScale
		if not (0<=y<self.y): return 0 #- self.terrainScale
		
		xPx = int(float(x)/self.x*self.terrainImgSize)
		yPx = int(float(y)/self.y*self.terrainImgSize)
		height = self.terrain.getElevation(xPx, yPx) * self.terrainScale# - self.terrainScale
		#print "Terrain height in %s / %s : %s" % (x, y, height)
		return height
		
	def update(self):
		self.vertex = GeomVertexWriter(self.gvd, 'vertex')
		self.texcoord = GeomVertexWriter(self.gvd, 'texcoord')
		self.color = GeomVertexWriter(self.gvd, 'color')
		self.normal = GeomVertexWriter(self.gvd, 'normal')
		
		i = 0
		for y in range(self.y):
			for x in range(self.x):
				if self.data[y][x] == 1:
					self.addWallTile(x, y)
				else:
					self.addEmptyTile(x, y)
				i += 4
			
	def rebuild(self):
		# Needed to update the map after it has been resized
		if self.np:
			self.np.remove()
		if self.terrainNP:
			self.terrainNP.remove()
		self.y = len(self.data)
		self.x = len(self.data[0])
		
		self.node = GeomNode("tiledMesh")
		self.gvd = GeomVertexData('name', GeomVertexFormat.getV3n3c4t2(), Geom.UHStatic)
		self.geom = Geom(self.gvd)
		self.prim = GeomTriangles(Geom.UHStatic)
		
		self.update()
		
		i = 0
		for x in range(self.x * self.y):
			#self.prim.addVertices(i, i + 3, i + 2)
			#self.prim.addVertices(i, i + 2, i + 1)
			self.prim.addVertices(i, i + 2, i + 1)
			self.prim.addVertices(i, i + 3, i + 2)
			i += 4
		
		self.prim.closePrimitive()
		self.geom.addPrimitive(self.prim)
		self.node.addGeom(self.geom)
		
		self.np = NodePath(self.node)
		self.np.reparentTo(render)
		#self.np.setTwoSided(True)
		self.np.setTexture(self.colTex)
		#self.np.setColor(0,0,1.0,0.1)
		self.np.setTransparency(True)
		
		if self.hasGeoMip:
			self.initGeoMip()
		
		
	def addWallTile(self, x, y):
		
		norm, norm2 = random.random()/2.0, random.random()/2.0
		#z = 0
		z1 = self.getTileHeight(x, y) + 0.01
		z2 = self.getTileHeight(x, y+1) + 0.01
		z3 = self.getTileHeight(x+1, y+1) + 0.01
		z4 = self.getTileHeight(x+1, y) + 0.01
		
		self.vertex.addData3f(x, y, z1)
		self.texcoord.addData2f(0, 0)
		self.color.addData4f(1, 1, 1, 1)
		self.normal.addData3f(norm,norm2,1)
		
		self.vertex.addData3f(x, y+1, z2)
		self.texcoord.addData2f(0, 1)
		self.color.addData4f(1, 1, 1, 1)
		self.normal.addData3f(norm,norm2,1)
		
		self.vertex.addData3f(x+1, y+1, z3)
		self.texcoord.addData2f(1, 1)
		self.color.addData4f(1, 1, 1, 1)
		self.normal.addData3f(norm,norm2,1)
		
		self.vertex.addData3f(x+1, y, z4)
		self.texcoord.addData2f(1, 0)
		self.color.addData4f(1, 1, 1, 1)
		self.normal.addData3f(norm,norm2,1)

	def addEmptyTile(self, x, y):
		#z = random()/100.0
		z = 0
		self.vertex.addData3f(x, y, z)
		self.texcoord.addData2f(0, 0)
		self.color.addData4f(1, 1, 1, 1)
		self.normal.addData3f(0,0,1)
		
		self.vertex.addData3f(x, y, z)
		self.texcoord.addData2f(0, 1)
		self.color.addData4f(1, 1, 1, 1)
		self.normal.addData3f(0,0,1)
		
		self.vertex.addData3f(x, y, z)
		self.texcoord.addData2f(1, 1)
		self.color.addData4f(1, 1, 1, 1)
		self.normal.addData3f(0,0,1)
		
		self.vertex.addData3f(x, y, z)
		self.texcoord.addData2f(1, 0)
		self.color.addData4f(1, 1, 1, 1)
		self.normal.addData3f(0,0,1)
		
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
		
		
	def fill(self):
		for y in range(self.y):
			for x in range(self.x):
				self.data[y][x] = 1
		self.update()
		
	def clear(self):
		self.data = [] # [[1,1,1,1,0,1,0,0,...], [1,0,0,...]... ]
		for y in range(self.y):
			tmp = []
			for x in range(self.x):
				tmp.append(0)
			self.data.append(tmp)
		#for y in range(self.y):
		#	for x in range(self.x):
		#		self.data[y][x] = 0
		self.update()
	
	def fillBorder(self):
		for y in range(self.y):
			for x in range(self.x):
				if self.data[y][x] == 0:
					if (x==0) or (y==0):
						self.data[y][x] = 1
					if (x==self.x-1) or (y==self.y-1):
						self.data[y][x] = 1
					
		self.update()
		
	def getRandomTile(self):
		#while True:
		for i in range(10):# if no success after ten tries, give up and wait
			x = random.randint(1,self.x-1)
			y = random.randint(1,self.y-1)
			if self.data[y][x]==0:
				#print "returning random free tile : %s %s" % (x, y)
				return x, y
		return 10, 10
		#return None
	
	def destroy(self):
		if self.np:
			self.np.remove()
		if self.terrainNP:
			self.terrainNP.remove()
		del self.data
		del self.gvd
