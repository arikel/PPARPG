#!/usr/bin/python
# -*- coding: utf8 -*-

from pandac.PandaModules import *

import cPickle as pickle

from skyBox import SkyBox
from mapObject import *
from mapUtils import *

#-----------------------------------------------------------------------
# Map
#-----------------------------------------------------------------------
class Map:
	def __init__(self, filename = None):
		self.name = None
		self.filename = filename
		
		self.x = 0
		self.y = 0
		
		self.NPCroot = NodePath("root")
		self.NPCroot.reparentTo(render)
		
		self.mapObjectRoot = NodePath("mapObjectRoot")
		self.mapObjectRoot.reparentTo(render)
		#self.mapObjectRoot.setTransparency(True)
		#self.mapObjectRoot.setTransparency(TransparencyAttrib.MAlpha)
		self.mapObjects = {} # map objects
		
		self.mapWall = None
		self.collisionGrid = None
		self.sky = None
		self.music = None
		
		if self.filename is not None:
			self.load()
	
	def collisionHide(self):
		self.collisionGrid.collisionHide()
		
	def collisionShow(self):
		self.collisionGrid.collisionShow()
		
	'''
	def startDrag(self, mapObj):
		self.draggingObject = True
		self.draggedObject = mapObj
		
	def stopDrag(self):
		self.draggingObject = False
		self.draggedObject = None
	'''
	def setDim(self, x, y):
		self.x = int(x)
		self.y = int(y)
		self.collisionGrid.setDim(x, y)
		
	def save(self, filename):
		mapData = {}
		mapData["name"] = self.name
		mapData["X"] = self.x
		mapData["Y"] = self.y
		mapData["collision"] = self.collisionGrid.data
		if self.collisionGrid.hasGeoMip:
			mapData["geomip"] = [self.collisionGrid.texPath, self.collisionGrid.geoMipPath]
			
		mapData["mapObjects"] = []
		for elem in self.mapObjects.values():
			model = elem.model
			mapObjectData = []
			mapObjectData.append(elem.name)
			mapObjectData.append(elem.genre)
			mapObjectData.append(model.getPos())
			mapObjectData.append(model.getHpr())
			mapObjectData.append(model.getScale())
			mapData["mapObjects"].append(mapObjectData)
		
		if self.sky:
			mapData["skybox"] = self.sky.name
		
		if self.music:
			mapData["music"] = self.music
		
		f = open(filename, 'w')
		pickle.dump(mapData, f)
		f.close()
		print "map data saved as %s" % (filename)
		
	def destroy(self):
		print "Map : Map %s destroyed" % (self.name)
		if self.mapWall:
			self.mapWall.destroy()
			
		if self.collisionGrid:
			self.collisionGrid.destroy()
			del self.collisionGrid
			print "Map : collisionGrid destroyed"
		for mapObj in self.mapObjects.values():
			self.removeMapObject(mapObj.name)

		if self.sky:
			self.sky.destroy()
			
	def load(self, filename=None):
		"Map : Loading map %s" % (filename)
		
		if filename is None:
			filename = self.filename
		if filename is None:
			return False
		#self.destroy()
		
		f = open(filename, 'r')
		mapData = pickle.load(f)
		f.close()
		del f
		
		if "name" in mapData:
			self.name = mapData["name"]
			print "Map : Loading map named %s" % (self.name)
		if "X" in mapData:
			self.x = mapData["X"]	
		if "Y" in mapData:
			self.y = mapData["Y"]
		
		if "geomip" in mapData:
			tex = mapData["geomip"][0]
			geomipTex = mapData["geomip"][1]
			print "Map : Creating mipmap collision grid on Map load"
			self.collisionGrid = CollisionGrid(self.x, self.y, self.name, tex, geomipTex)
		else:
			print "Map : Creating flat collision grid on Map load"
			self.collisionGrid = CollisionGrid(self.x, self.y, self.name)
		if not self.collisionGrid:
			print "Map : WARNING : collision grid should be there"
		if "skybox" in mapData:
			name = mapData["skybox"]
			self.sky = SkyBox()
			self.sky.load(name)
			self.sky.set(name)
		else:
			self.sky = None
		
		if "music" in mapData:
			self.music = mapData["music"]
			self.bgMusic = loader.loadSfx(self.music)
			self.bgMusic.setLoop(True)
			
			
		else:
			self.music = None
			self.bgMusic = None
			
		self.mapWall = MapWall(self.x, self.y, 0)
		
		self.collisionGrid.data = mapData["collision"]
		
		print "Map : rebuild asked in load function"
		
		self.collisionGrid.rebuild()
		
		print "Map : looks like the rebuild went ok"
		
		print "models in use : %s" % (mapData["mapObjects"])
		for data in mapData["mapObjects"]:
			name = data[0]
			genre = data[1]
			pos = data[2]
			hpr = data[3]
			scale = data[4]
			self.addMapObject(
				genre,
				name,
				(pos.getX(), pos.getY(), pos.getZ()),
				(hpr.getX(), hpr.getY(), hpr.getZ()),
				(scale.getX(), scale.getY(), scale.getZ())
				)
			
		
	
	def addMapObject(self, genre, name, pos=(0,0,0), hpr=(0,0,0), scale=(1,1,1)):
		if name not in self.mapObjects:
			mapObject = MapObject(self, genre, name)
			mapObject.setPos(pos) #-self.collisionGrid.terrainScale/3.0)
			mapObject.setHpr(hpr)
			mapObject.setScale(scale)
			mapObject.reparentTo(self.mapObjectRoot)
			self.mapObjects[name] = mapObject
		
	def removeMapObject(self, name):
		if name in self.mapObjects:
			self.mapObjects[name].destroy()
			del self.mapObjects[name]
	'''
	def setMapObjectPos(self, name, x, y, z=0):
		if name in self.mapObjects:
			self.mapObjects[name].setPos(x, y, z)
	'''	
			
	def clearCollision(self, args=[]):
		print "Map %s : clear collision called" % (str(self))
		self.collisionGrid.clear()
		
	def fillCollision(self, args=[]):
		print "Map %s : fill collision called" % (str(self))
		self.collisionGrid.fill()
