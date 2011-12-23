#!/usr/bin/python
# -*- coding: utf8 -*-

from pandac.PandaModules import *

import cPickle as pickle

from skyBox import SkyBox
from mapObject import *
from mapUtils import *
from wallBuilder import *
from effects import WaterPlane, GrassEngine

#-----------------------------------------------------------------------
# Map
#-----------------------------------------------------------------------
class Map:
	def __init__(self, filename = None):
		self.name = None
		self.filename = filename
		
		self.x = 0
		self.y = 0
		
		self.NPCroot = NodePath("NPCroot")
		self.NPCroot.reparentTo(render)
		
		self.mapObjectRoot = NodePath("mapObjectRoot")
		self.mapObjectRoot.reparentTo(render)
		#self.mapObjectRoot.setTransparency(True)
		#self.mapObjectRoot.setTransparency(TransparencyAttrib.MAlpha)
		self.mapObjects = {} # map objects
		self.walls = [] # dynamic walls, see WallBuilder in wallBuilder.py
		self.innerWall = None
		self.water = None
		
		self.creatureRoot = NodePath("creatureRoot")
		self.creatureRoot.reparentTo(render)
		
		self.collisionGrid = None
		self.sky = None
		self.bgMusic = None
		self.bgSound = None
		
		if self.filename is not None:
			self.load()
	
	def getAvailableName(self, genre):
		i = 1
		tmpName = genre + "_" + str(i)
		while tmpName in self.mapObjects:
			i = i+1
			tmpName = genre + "_" + str(i)
		return tmpName
		
	def collisionHide(self):
		self.collisionGrid.collisionHide()
		
	def collisionShow(self):
		self.collisionGrid.collisionShow()
	
	def setSize(self, x, y):
		self.x = int(x)
		self.y = int(y)
		self.collisionGrid.setSize(x, y)
		
	def save(self, filename):
		mapData = {}
		mapData["name"] = self.name
		mapData["X"] = self.x
		mapData["Y"] = self.y
		mapData["collision"] = self.collisionGrid.data
		mapData["groundTex"] = self.groundTex
		print "Map saving : groundTex = %s" % (self.groundTex)
		mapData["groundTexScale"] = self.groundTexScale
		
		if self.collisionGrid.hasGeoMip:
			mapData["mipImg"] = [self.collisionGrid.texPath, self.collisionGrid.geoMipPath]
			
		mapData["mapObjects"] = []
		for elem in self.mapObjects.values():
			mapData["mapObjects"].append(elem.getSaveData())
			
		mapData["walls"] = []
		for wall in self.walls:
			mapData["walls"].append(wall.getSaveData())
		
		if self.innerWall:
			mapData["innerWall"] = self.innerWall.getSaveData()
		
		if self.water:
			mapData["water"] = True
		
		if self.sky:
			mapData["skybox"] = self.sky.name
		
		if self.bgMusic:
			mapData["music"] = self.music
		if self.bgSound:
			mapData["ambientSound"] = self.ambientSound
		
		f = open(filename, 'w')
		pickle.dump(mapData, f)
		f.close()
		print "map data saved as %s" % (filename)
		
	def clearWalls(self):
		for wall in self.walls:
			wall.destroy()
		self.walls = []
		
	def clearInnerWall(self):
		if self.innerWall:
			self.innerWall.destroy()
			self.innerWall = None
		
	def setGroundTexture(self, texPath):
		if self.collisionGrid.ground:
			self.collisionGrid.ground.setTexture(texPath)
			self.groundTex = texPath
			
	def destroy(self):
		#print "Map : Map %s destroyed" % (self.name)
		if self.innerWall:
			self.innerWall.destroy()
			
		if self.collisionGrid:
			self.collisionGrid.destroy()
			del self.collisionGrid
			#print "Map : collisionGrid destroyed"
		for mapObj in self.mapObjects.values():
			self.removeMapObject(mapObj.name)
		#if self.ground:
		#	self.ground.destroy()
			
		if self.sky:
			self.sky.destroy()
		
		self.clearWalls()
		self.clearInnerWall()
		if self.water:
			self.water.destroy()
		#for wall in self.walls:
		#	wall.destroy()
		
	def load(self, filename=None):
		if filename is None:
			filename = self.filename
		if filename is None:
			return False
		#self.destroy()
		
		f = open(filename, 'r')
		mapData = pickle.load(f)
		f.close()
		
		if "name" in mapData:
			self.name = mapData["name"]
			print "Map : Loading map named %s" % (self.name)
		if "X" in mapData:
			self.x = mapData["X"]	
		if "Y" in mapData:
			self.y = mapData["Y"]
		
		if "groundTex" in mapData:
			self.groundTex = mapData["groundTex"]
		else:
			self.groundTex = "img/textures/ice01.jpg"
			
		if "groundTexScale" in mapData:
			self.groundTexScale = mapData["groundTexScale"]
		else:
			self.groundTexScale = 50.0
			
		if "mipImg" in mapData:
			#tex = mapData["geomip"][0]
			#geomipTex = mapData["geomip"][1]
			#print "Map : Creating mipmap collision grid on Map load"
			self.mipImg = mapData["mipImg"]
			self.collisionGrid = CollisionGrid(self, self.name, self.groundTex, self.mipImg, self.groundTexScale)
		else:
			#print "Map : Creating flat collision grid on Map load"
			self.collisionGrid = CollisionGrid(self, self.name, self.groundTex, None, self.groundTexScale)
			
		#if not self.collisionGrid:
		#	print "Map : WARNING : collision grid should be there"
		
		if "walls" in mapData:
			for wallData in mapData["walls"]:
				wall = WallBuilder(wallData[0], wallData[1], wallData[2], wallData[3])
				self.walls.append(wall)
		
		if "innerWall" in mapData:
			self.innerWall = InnerWall(self, mapData["innerWall"][0], mapData["innerWall"][1],mapData["innerWall"][2])
		else:
			self.innerWall = None
		
		if "water" in mapData:
			self.water = WaterPlane(-20, -20, self.x+20, self.y+20)
			
		if "skybox" in mapData:
			self.setSky(mapData["skybox"])
			#name = mapData["skybox"]
			#self.sky = SkyBox()
			#self.sky.load(name)
			#self.sky.set(name)
		else:
			self.sky = None
		
		if "music" in mapData:
			self.setBgMusic(mapData["music"])
			#self.music = mapData["music"]
			#self.bgMusic = loader.loadSfx(self.music)
			#self.bgMusic.setLoop(True)
		
		if "ambientSound" in mapData:
			self.setBgSound(mapData["ambientSound"])
			#self.ambientSound = mapData["ambientSound"]
			#self.bgSound = loader.loadSfx(self.ambientSound)
			#self.bgSound.setLoop(True)
			
		else:
			self.ambientSound = None
			self.bgSound = None
			
		self.collisionGrid.data = mapData["collision"]
		self.collisionGrid.rebuild()
		
		#print "models in use : %s" % (mapData["mapObjects"])
		for data in mapData["mapObjects"]:
			name = data[0]
			genre = data[1]
			pos = data[2]
			hpr = data[3]
			scale = data[4]
			self.addMapObject(
				genre,
				name,
				pos,
				hpr,
				scale
				#(pos.getX(), pos.getY(), pos.getZ()),
				#(hpr.getX(), hpr.getY(), hpr.getZ()),
				#(scale.getX(), scale.getY(), scale.getZ())
				)
		
		#self.rock = RockWallBuilder(self.mapObjectRoot, [Point3(0,0,0), Point3(self.x, 0,0), Point3(self.x, self.y,0), Point3(0,self.y,0), Point3(0,0,0)])
		#self.rock = ModelWallBuilder(self.mapObjectRoot, "models/props/rock1", ["img/textures/block01c.jpg", "img/textures/block01d.jpg"], 1.0, 1.5, 4.0, 180.0, [Point3(0,0,0), Point3(self.x, 0,0), Point3(self.x, self.y,0), Point3(0,self.y,0), Point3(0,0,0)])
		#self.rock.removeLastPoint()
		
	def setBgMusic(self, musicPath):
		#if self.bgMusic:
		#	self.bgMusic.stop()
		self.music = musicPath
		self.bgMusic = loader.loadSfx(self.music)
		self.bgMusic.setLoop(True)
		
	def setBgSound(self, soundPath):
		#if self.bgSound:
		#	self.bgSound.stop()
		self.ambientSound = soundPath
		self.bgSound = loader.loadSfx(self.ambientSound)
		self.bgSound.setLoop(True)
	
	def setSky(self, skyName):
		if self.sky:
			self.sky.destroy()
		self.sky = SkyBox()
		self.sky.load(skyName)
		self.sky.set(skyName)
		
	def addMapObject(self, genre, name, pos=(0,0,0), hpr=(0,0,0), scale=(1,1,1)):
		if name not in self.mapObjects:
			mapObject = MapObject(self, genre, name)
			mapObject.setPos(pos) #-self.collisionGrid.terrainScale/3.0)
			#print "Map add object : new object %s at position %s" % (name, mapObject.getPos())
			mapObject.setHpr(hpr)
			mapObject.setScale(scale)
			mapObject.reparentTo(self.mapObjectRoot)
			self.mapObjects[name] = mapObject
			#print "-> position is : %s" % (mapObject.getPos())
		
	def removeMapObject(self, name):
		if name in self.mapObjects:
			self.mapObjects[name].destroy()
			del self.mapObjects[name]
			
	def clearCollision(self, args=[]):
		print "Map %s : clear collision called" % (str(self))
		self.collisionGrid.clear()
		
	def fillCollision(self, args=[]):
		print "Map %s : fill collision called" % (str(self))
		self.collisionGrid.fill()
	
	def getClosestOpenTile(self, x, y):
		return self.collisionGrid.getClosestOpenTile(x,y)
	
def makeNewMap(name = "map", x=30, y=20, groundTex="img/textures/ice01.jpg", groundTexScale = 50.0):
	map = Map()
	map.name = name
	map.x = x
	map.y = y
	map.collision = []
	for y in range(map.y):
		tmp = []
		for x in range(map.x):
			tmp.append(0)
		map.collision.append(tmp)
	map.groundTex = groundTex
	map.groundTexScale = groundTexScale
	map.collisionGrid = CollisionGrid(map, map.name, map.groundTex, None, map.groundTexScale)
	map.collisionGrid.data = map.collision
	map.collisionGrid.rebuild()
	
	#map.innerWall = InnerWall(map, 4.0, "img/textures/wood03.jpg", 5.0)
	
	l1 = [Point3(20,0.5,0), Point3(20,15.5,0)]
	#map.walls.append(WallBuilder(0.4, 3.0, "img/textures/bborder03.jpg", [Point3(20,0,0), Point3(20,15,0)]))
	#map.walls.append(WallBuilder(0.4, 3.0, "img/textures/bborder03.jpg", [Point3(12,0,0), Point3(12,15,0)]))
	
	map.setSky("daysky0")
	
	#map.setBgSound("sounds/wind.ogg")
	map.setBgMusic("music/Irradiated_Dreams.ogg")
	return map
	
if __name__=="__main__":
	map = makeNewMap("Undernil", 50, 30, "img/textures/ice01.jpg", 5.0)
	#map.setSize(50,30)
	map.save("maps/001-1.txt")
