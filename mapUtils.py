#!/usr/bin/python
# -*- coding: utf8 -*-

import random

from pandac.PandaModules import *
from wallBuilder import WallBuilder
#-----------------------------------------------------------------------
# Decor building functions and classes
#-----------------------------------------------------------------------
'''
def makeFloor(nbCases, scalex, scaley, texpath):
	cm = CardMaker('card')
	cm.setUvRange(Point2(scalex/nbCases,scaley/nbCases), Point2(0,0))
	cm.setHasNormals(True)
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
'''
def makeWall(scalex, scaley, scaleTex):
	cm = CardMaker('card')
	cm.setUvRange((scalex/scaleTex,0), (0,scaley/scaleTex))
	cm.setHasNormals(True)
	card = NodePath(cm.generate())
	img = loader.loadTexture("img/textures/oldstone4.jpg")
	card.setTexture(img)
	card.setScale(scalex,1,scaley)
	#card.setHpr(0,0,0)
	#card.setTwoSided(True)
	card.setTransparency(TransparencyAttrib.MAlpha)
	return card

class MapWall:
	def __init__(self, x, y,z=0, height=6.0, texScale=5.0):
		self.walls = []
		
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
# CollisionGrid : WIP
#-----------------------------------------------------------------------
class CollisionGrid:
	def __init__(self, map, x=50, y=30, name=None, texPath="img/textures/ice01.jpg", mipImg = None, texScale=50.0):
		self.map = map
		self.name = name
		print "CollisionGrid : initiating %s, scale = %s" % (name, texScale)
		
		self.x = x
		self.y = y
		self.groundTex = texPath
		self.mipImg = mipImg
		self.groundTexScale = texScale
		
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
		if self.groundTex is not None:
			self.tex = loader.loadTexture(self.groundTex)
		self.colTex = loader.loadTexture("img/textures/collision.png")
		self.np.setTexture(self.colTex)
		#self.np.setColor(0,0,1.0,0.1)
		self.np.setTransparency(True)
		
		
		if self.mipImg is not None:
			self.hasGeoMip = True
			self.ground = TerrainGround(self.map,
			self.x,
			self.y,
			self.groundTex, # terrain texture
			self.mipImg, # mipImg
			imgSize=65.0, # mipImg size
			scale=5.0) # terrain height scale
			
		else:
			self.hasGeoMip = False
			self.ground = FlatGround(self.map, self.x, self.y, self.groundTex, self.groundTexScale)
	
		
	def collisionHide(self):
		self.np.hide()
		
	def collisionShow(self):
		self.np.show()
		
	def getTileHeight(self, x, y):
		if not self.hasGeoMip:
			return 0
		else:
			return self.ground.getTileHeight(x, y)
		
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
		
		if self.ground:
			self.ground.destroy()
		
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
		
		if self.mipImg is not None:
			self.hasGeoMip = True
			self.ground = TerrainGround(self.map,
			self.x,
			self.y,
			"img/textures/ice01.jpg", # terrain texture
			"img/mipmaps/ground02.jpg", # mipImg
			imgSize=65.0, # mipImg size
			scale=5.0) # terrain height scale
			
		else:
			self.hasGeoMip = False
			self.ground = FlatGround(self.map, self.x, self.y, self.groundTex, self.groundTexScale)
		
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
		self.clearData()
		self.update()
	
	def clearData(self):
		self.data = [] # [[1,1,1,1,0,1,0,0,...], [1,0,0,...]... ]
		for y in range(self.y):
			tmp = []
			for x in range(self.x):
				tmp.append(0)
			self.data.append(tmp)
	
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
		return 2, 2
		#return None
	
	def destroy(self):
		if self.np:
			self.np.remove()
		if self.ground:
			self.ground.destroy()
		#if self.terrainNP:
		#	self.terrainNP.remove()
		del self.data
		del self.gvd
	
	def setSize(self, x, y):
		oldData = self.data
		oldX = self.x
		oldY = self.y
		
		self.x = int(x)
		self.y = int(y)
		
		self.data = []
		for y in range(self.y):
			tmp = []
			for x in range(self.x):
				if x<oldX and y<oldY:
					tmp.append(oldData[y][x])
				else:
					tmp.append(0)
			self.data.append(tmp)
		self.rebuild()

class FlatGround:
	def __init__(self, map, x=20,y=20, tex="img/textures/ice01.jpg", scale=50.0):
		self.map = map
		self.x = x
		self.y = y
		self.scale = scale
		self.texPath = tex
		self.tex = loader.loadTexture(self.texPath)
		self.tex.setWrapU(Texture.WMRepeat)
		self.tex.setWrapV(Texture.WMRepeat)
		self.makeGround()
		
	def makeGround(self):
		self.cm = CardMaker('card')
		self.cm.setUvRange(Point2(self.x/self.scale,self.y/self.scale), Point2(0,0))
		print "making flat ground with scale = %s" % (self.scale)
		self.cm.setHasNormals(True)
		self.card = NodePath(self.cm.generate())
		
		self.card.setTexture(self.tex)
		self.card.setScale(self.x,1,self.y)
		self.card.setPos(0,0,0.0)
		self.card.setHpr(0,-90,0)
		#card.setTwoSided(True)
		#card.setTransparency(TransparencyAttrib.MAlpha)
		self.card.reparentTo(self.map.mapObjectRoot)
		
	def destroy(self):
		self.card.detachNode()
		self.card.remove()

	def setSize(self, x, y):
		self.destroy()
		self.x = x
		self.y = y
		self.makeGround()
		#self.card.setScale(self.x,1,self.y)

class TerrainGround:
	def __init__(self,
			map,
			x=20,
			y=20,
			tex="img/textures/ice01.jpg",
			mipImg="img/mipmaps/ground02.jpg",
			imgSize=65.0,
			scale=5.0):
		
		self.map = map
		self.x = x
		self.y = y
		self.texPath = tex
		self.terrain = None
		self.terrainNP = None
		self.terrainScale = 0
		self.terrainImgSize = imgSize
		self.mipImg = mipImg
		self.terrainScale = scale
		
		self.initGeoMip()
		
	def initGeoMip(self):
		self.terrain = GeoMipTerrain("ground")
		self.terrain.setHeightfield(self.mipImg)
		#self.terrain.setMinLevel(2)
		#self.terrain.setBruteforce(True)
		#self.terrain.setBlockSize(5)
		
		self.terrainNP = self.terrain.getRoot()
		
		#self.terrainNP.reparentTo(self.map.mapObjectRoot)
		import direct.directbase.DirectStart
		self.terrainNP.reparentTo(render)
		
		self.terrainNP.setScale(self.x/self.terrainImgSize,self.y/self.terrainImgSize,self.terrainScale)
		#self.terrainNP.setPos(0,0,-self.terrainScale)
		self.terrain.generate()
		self.terrainNP.setTexture(loader.loadTexture(self.texPath))
		self.terrainNP.setTexScale(TextureStage.getDefault(),self.terrainImgSize/10,self.terrainImgSize/10)
		self.terrainNP.flattenStrong()
		#self.terrainNP.setCollideMask(BitMask32(1))
		
	def destroy(self):
		if self.terrainNP:
			self.terrainNP.remove()
	
	def getTileHeight(self, x, y):
		if not (0<=x<self.x): return 0 #- self.terrainScale
		if not (0<=y<self.y): return 0 #- self.terrainScale
		
		xPx = int(float(x)/self.x*self.terrainImgSize)
		yPx = int(float(y)/self.y*self.terrainImgSize)
		height = self.terrain.getElevation(xPx, yPx) * self.terrainScale# - self.terrainScale
		#print "Terrain height in %s / %s : %s" % (x, y, height)
		return height
	
if __name__ == "__main__":
	t = TerrainGround("map", 250,120,"img/textures/ice01.jpg", "img/mipmaps/ground02.jpg", 65.0,15.0)
	import sys
	import direct.directbase.DirectStart
	base.accept("escape", sys.exit)
	#t.destroy()
	run()
