#!/usr/bin/python
# -*- coding: utf8 -*-

from config import *
if CONFIG_FULLSCREEN:
	fullscreen = "#t"
else:
	fullscreen = "#f"
	
from pandac.PandaModules import *

loadPrcFileData("setup", """sync-video 0
show-frame-rate-meter #t
#win-size 800 600
#win-size 1024 768
#win-size 1280 960
#win-size 1280 1024
win-size %s %s
win-fixed-size 1
#yield-timeslice 0 
#client-sleep 0 
#multi-sleep 0
basic-shaders-only #f
fullscreen %s
#audio-library-name null
""" % (CONFIG_W, CONFIG_H, fullscreen))


import direct.directbase.DirectStart
from direct.showbase.DirectObject import DirectObject
from direct.task import Task
from direct.interval.IntervalGlobal import *
from direct.gui.OnscreenText import OnscreenText
from direct.filter.CommonFilters import CommonFilters
from direct.fsm.FSM import FSM

import sys
import cPickle as pickle


from camHandler import CamHandler
from pathFind import *

from skyBox import SkyBox
from lightManager import LightManager

from mouseCursor import *

from gui import *
from mapObject import *
from dialog import *
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

	
	def startDrag(self, mapObj):
		self.draggingObject = True
		self.draggedObject = mapObj
		
	def stopDrag(self):
		self.draggingObject = False
		self.draggedObject = None
	
		
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
		
	


#-----------------------------------------------------------------------
# MapManagerBase, for MapManager and MapEditor
#-----------------------------------------------------------------------
class MapManagerBase(DirectObject):
	def __init__(self, gm):
		self.gm = gm # Game
		self.clicker = Clicker()
		self.map = self.gm.map
		self.camHandler = self.gm.camHandler
		
		self.keyDic = {}
		
		
	def startAccept(self):
		for key in [
			"mouse1", "mouse3",
			FORWARD, BACKWARD,
			STRAFE_LEFT, STRAFE_RIGHT,
			TURN_LEFT, TURN_RIGHT,
			UP, DOWN,"h", "b", "t", "g"
			]:
			self.keyDic[key] = 0
			self.accept(key, self.setKey, [key, 1])
			keyUp = key + "-up"
			self.accept(keyUp, self.setKey, [key, 0])
	'''	
	def stopAccept(self):
		self.ignoreAll()
	'''
	def setKey(self, key, value):
		#print "MapManagerBase received %s" % (key)
		self.keyDic[key] = value
		
	def setMap(self, map):
		self.map = map
		self.clicker.setHeight(self.map.collisionGrid.terrainScale)
		
	def getHoverObjectName(self):
		if base.mouseWatcherNode.hasMouse():
			mpos = base.mouseWatcherNode.getMouse()
			pos = self.clicker.getMouseTilePos(mpos)
			res = self.clicker.getMouseObject(self.map.mapObjectRoot)
			if res is not None:
				#print "Found a name : %s " % (res.getIntoNodePath().getName())
				name = res.getIntoNodePath().getName()
				
				return name
		
		#self.msg.setText("")
		return None
	
	def getHoverNPCName(self):
		if base.mouseWatcherNode.hasMouse():
			mpos = base.mouseWatcherNode.getMouse()
			pos = self.clicker.getMouseTilePos(mpos)
			res = self.clicker.getMouseObject(self.map.NPCroot)
			if res is not None:
				name = res.getIntoNodePath().getName()
				return name
		
		#self.msg.setText("")
		return None
	
	def updateCam(self, dt=0.01):
		if self.keyDic[FORWARD]:
			self.camHandler.forward(dt)
		if self.keyDic[BACKWARD]:
			self.camHandler.backward(dt)
		
		if self.keyDic[STRAFE_LEFT]:
			self.camHandler.strafeLeft(dt)
			
		if self.keyDic[STRAFE_RIGHT]:
			self.camHandler.strafeRight(dt)
			
		if self.keyDic[TURN_LEFT]:
			self.camHandler.turnLeft(dt)
		if self.keyDic[TURN_RIGHT]:
			self.camHandler.turnRight(dt)
			
		if self.keyDic[UP]:
			self.camHandler.lookUp(dt)
		if self.keyDic[DOWN]:
			self.camHandler.lookDown(dt)
	
#-----------------------------------------------------------------------
# MapManager : handles the map while in game
#-----------------------------------------------------------------------
class MapManager(MapManagerBase):
	def __init__(self, gm):
		self.mode = "move" # talk, fight
		
		MapManagerBase.__init__(self, gm)
		
		# NPCs
		self.NPC = {}
		for name in ["ula2", "Kimmo", "Drunkard", "Camilla"]:
			x, y = self.map.collisionGrid.getRandomTile()
			self.addNPC(name, "models/characters/male", "models/characters/humanTex2.png", x,y)
		
		name = self.gm.playerData["name"]
		sex = self.gm.playerData["sex"]
		
		if sex == "male":
			pass
		modelPath = "models/characters/male"
		
		self.player = NPC(name, modelPath)
		
		self.player.setTilePos(5, 3)
		self.player.reparentTo(render)
		
		self.dialog = None # current dialog
		
		self.msg = makeMsg(-1.3,0.95,"...")
		
		self.msgTilePos = makeMsg(-1.2,0.95,"...")
	
	def start(self):
		self.msg.show()
		self.msgTilePos.show()
		
		self.task = taskMgr.add(self.update, "MapManagerTask")
		self.startAccept()
		if self.map.bgMusic:
			self.map.bgMusic.play()
		
	def stop(self):
		self.msg.hide()
		self.msgTilePos.hide()
		
		taskMgr.remove(self.task)
		self.ignoreAll()
	
	def startAccept(self):
		for key in [
			"mouse1", "mouse3",
			FORWARD, BACKWARD,
			STRAFE_LEFT, STRAFE_RIGHT,
			TURN_LEFT, TURN_RIGHT,
			UP, DOWN,"h", "b", "t", "g"
			]:
			self.keyDic[key] = 0
			self.accept(key, self.setKey, [key, 1])
			keyUp = key + "-up"
			self.accept(keyUp, self.setKey, [key, 0])
		self.setMode(self.mode)
		
	def setMode(self, mode="move"):
		if mode == "move":
			print "Map Manager switched to move mode"
			self.mode = "move"
			self.accept("mouse1", self.onClickObject) # left click
			#self.accept("mouse2", self.onClickObject2) # scroll click
			#self.accept("mouse3", self.onClickObject3) # right click
			self.accept("wheel_up", self.camHandler.moveHeight, [-0.05])
			self.accept("wheel_down", self.camHandler.moveHeight, [0.05])
				
		elif mode == "talk":
			print "Map manager switched to talk mode"
			self.mode = "talk"
			self.ignore("mouse1")
			self.ignore("mouse2")
			self.ignore("mouse3")
			
		elif mode == "fight":
			print "Map Manager switched to fight mode"
			self.mode = "fight"
			self.accept("mouse1", self.onClickObject) # left click
			#self.accept("mouse2", self.onClickObject2) # scroll click
			#self.accept("mouse3", self.onClickObject3) # right click
		
		modeMsg = "Game mode : " + self.mode
		self.msgTilePos.setText(modeMsg)
	
			
		
	
	def onClickObject(self):
		# click on MapObject :
		name = self.getHoverNPCName()
		if name is not None:
			print "map manager : left click on NPC : %s, opening dialog" % (name)
			self.openDialog(name)
			return
		
		name = self.getHoverObjectName()
		if name is not None:
			print "map manager : left click on map object : %s" % (name)
			return
			
		if base.mouseWatcherNode.hasMouse():
			mpos = base.mouseWatcherNode.getMouse()
			pos = self.clicker.getMouseTilePos(mpos)
			self.playerGoto(pos[0], pos[1])
			print "Player goto %s/%s" % (pos[0], pos[1])
			return
		# and this should never happen
		print "WARNING : map manager : left click on nothing?!"
		return False
			
	def addNPC(self, name, modelName, tex, x, y):
		npc = NPC(name, modelName, tex)
		npc.setTilePos(x, y)
		self.NPC[name] = npc
		npc.reparentTo(self.map.NPCroot)
	
	def removeNPC(self, name):
		if name in self.NPC:
			self.NPC[name].destroy()
			del self.NPC[name]
		
	def removeAllNPC(self):
		for name in self.NPC.keys():
			self.NPC[name].destroy()
			del self.NPC[name]
		
	def playerGoto(self, x, y):
		start = (self.player.getTilePos())
		end = (x, y)
		data = self.map.collisionGrid.data
		path = astar(start, end, data)
		if path is []:
			#print "... but no good path found"
			return False
		newPath = []
		for tile in path:
			newPath.append((tile[0], tile[1], self.map.collisionGrid.getTileHeight(tile[0], tile[1])))
		self.player.setPath(newPath)
		return True
	
	def NPCGoto(self, name, x, y):
		#print "NPCGoto called!"
		if name not in self.NPC:
			#print "%s is not a known NPC" % (name)	
			return False
		start = (self.NPC[name].getTilePos())
		end = (x, y)
		data = self.map.collisionGrid.data
		path = astar(start, end, data)
		if path is []:
			#print "... but no good path found"
			return False
		#else:
		#	print "NPCGoto : path found : %s" % (path)
		newPath = []
		for tile in path:
			newPath.append((tile[0], tile[1], self.map.collisionGrid.getTileHeight(tile[0], tile[1])))
		self.NPC[name].setPath(newPath)
	
	def openDialog(self, name):
		if self.dialog:
			#print "There was dialog garbage left, %s got his/her dialog shut unpolitely." % (self.dialog.name)
			#self.dialog.destroy()
			print "... but a dialog is already open for %s, aborting." % self.dialog.name
			return False
		if name in self.NPC:
			self.NPC[name].stop()
			if name in dialogDic:
				self.dialog = dialogDic[name](self, name)
			else:
				self.dialog = Dialog(self, name)
		else:
			print "Error, dialog called for unknown NPC : %s" % (name)
			
		
	def update(self, task):
		dt = globalClock.getDt()
		if base.mouseWatcherNode.hasMouse():
			mpos = base.mouseWatcherNode.getMouse()
			pos = self.clicker.getMouseTilePos(mpos)
		else:
			mpos = None
			pos = None
			#return task.cont
		
		if self.mode == "move" and mpos is not None:
			name = self.getHoverObjectName()
			if name is not None:
				msg = "in game object : " + name
				self.msg.setText(msg)
				self.msg.setPos(mpos.getX()*1.33+0.1, mpos.getY()+0.02)
				
			else:
				name = self.getHoverNPCName()
				if name is not None:
					msg = "talk to : " + name
					self.msg.setText(msg)
					self.msg.setPos(mpos.getX()*1.33+0.1, mpos.getY()+0.02)
				else:
					self.msg.setText("")
		

		if self.keyDic[FORWARD]:
			self.camHandler.forward(dt)
		if self.keyDic[BACKWARD]:
			self.camHandler.backward(dt)
		
		if self.keyDic[STRAFE_LEFT]:
			self.camHandler.strafeLeft(dt)
			
		if self.keyDic[STRAFE_RIGHT]:
			self.camHandler.strafeRight(dt)
			
		if self.keyDic[TURN_LEFT]:
			self.camHandler.turnLeft(dt)
		if self.keyDic[TURN_RIGHT]:
			self.camHandler.turnRight(dt)
			
		if self.keyDic[UP]:
			self.camHandler.lookUp(dt)
		if self.keyDic[DOWN]:
			self.camHandler.lookDown(dt)
		
		#-------------------------------------------------
		# NPC random movement
		for name in self.NPC:
			npc = self.NPC[name]
			if npc.timer <= 0:
				if npc.mode == "idle":
					if self.dialog:
						if self.dialog.name != name:
							#print "Sending NPC to random pos"
							tile = self.map.collisionGrid.getRandomTile()
							if tile is not None:
								self.NPCGoto(name, tile[0], tile[1])
							else:
								npc.resetTimer()
					else:
						tile = self.map.collisionGrid.getRandomTile()
						if tile is not None:
							self.NPCGoto(name, tile[0], tile[1])
		
		return task.cont

#-----------------------------------------------------------------------
# MapEditor : handles the map editing
#-----------------------------------------------------------------------
class MapEditor(MapManagerBase):
	def __init__(self, gm):
		self.mode = "collision"
		
		MapManagerBase.__init__(self, gm)
		
		# while self.mode == "edit", self.objectMode can become :
		# drag, rotating, scaling
		self.objectMode = None
		self.selectedObj = None
		
		self.gui = EditorGui(self)
		
		
	#-----------------------------
	# modes and input
	
	def start(self):
		print "Starting editor"
		self.gui.show()
		self.startAccept()
		self.task = taskMgr.add(self.update, "MapEditorTask")
		if self.map.bgMusic:
			self.map.bgMusic.stop()
		
	def stop(self):
		print "Stopping editor"
		self.gui.hide()
		taskMgr.remove(self.task)
		self.ignoreAll()
		
	def startAccept(self):
		for key in [
			"mouse1", "mouse3",
			FORWARD, BACKWARD,
			STRAFE_LEFT, STRAFE_RIGHT,
			TURN_LEFT, TURN_RIGHT,
			UP, DOWN,
			EDITOR_DOWN, EDITOR_LEFT, EDITOR_RIGHT, EDITOR_UP,
			"h", "b", "t", "g"
			]:
			self.keyDic[key] = 0
			self.accept(key, self.setKey, [key, 1])
			keyUp = key + "-up"
			self.accept(keyUp, self.setKey, [key, 0])
		
		self.setMode(self.mode)
		self.accept("space", self.toggle)
		
		self.accept(SAVE_MAP, self.save)
		self.accept(LOAD_MAP, self.load, ["maps/mapCode.txt"])
		
	def setMode(self, mode="collision"):
		if mode == "collision":
			msg = "Editor switched to collision mode"
			self.mode = "collision"
			self.gui.setInfo(msg)
			
			for key in ["mouse1", "mouse2", "mouse3"]:
				self.keyDic[key] = 0
				self.accept(key, self.setKey, [key, 1])
				keyUp = key + "-up"
				self.accept(keyUp, self.setKey, [key, 0])
				
			self.accept(CLEAR_COLLISION, self.map.clearCollision)
			self.accept(FILL_COLLISION, self.map.fillCollision)
			
		elif mode == "object":
			msg = "Editor switched to object mode"
			self.mode = "object"
			self.gui.setInfo(msg)
			
			self.accept("mouse1", self.onClickObject) # left click
			self.accept("mouse2", self.onClickObject2) # scroll click
			self.accept("mouse3", self.onClickObject3) # right click
			
			self.ignore(CLEAR_COLLISION)
			self.ignore(FILL_COLLISION)
			
		self.accept("wheel_up", self.camHandler.moveHeight, [-0.2])
		self.accept("wheel_down", self.camHandler.moveHeight, [0.2])
		
	def toggle(self):
		if self.mode == "collision":
			self.setMode("object")
		elif self.mode == "object":
			self.setMode("collision")
	
	def stopObjectAction(self):
		self.objectMode = None
		self.selectedObj = None
		self.gui.objectMenu.hide()
		self.startAccept()
		
	def startDrag(self, obj, extraArgs=[]):
		self.gui.objectMenu.hide()
		self.objectMode = "drag"
		self.gui.setInfo("dragging")
		self.selectedObj = obj
		self.accept("mouse1", self.stopDrag)
	
	def stopDrag(self, extraArgs=[]):
		self.gui.setInfo("stopped dragging")
		self.stopObjectAction()
		
	def startMoveZ(self, obj, extraArgs=[]):
		self.gui.objectMenu.hide()
		self.objectMode = "moveZ"
		self.gui.setInfo("moving object Z")
		self.selectedObj = obj
		self.accept("mouse1", self.stopMoveZ)
	
	def stopMoveZ(self, extraArgs=[]):
		self.gui.setInfo("stopped moving object Z")
		self.stopObjectAction()
		
	def startRotate(self, obj, extraArgs=[]):
		self.gui.objectMenu.hide()
		self.objectMode = "rotate"
		self.gui.setInfo("rotating object")
		self.selectedObj = obj
		self.accept("mouse1", self.stopRotate)
	
	def stopRotate(self, extraArgs=[]):
		self.gui.setInfo("stopped rotating object")
		self.stopObjectAction()
		
	#-----------------------------
	# map file handling
	def save(self):
		msg = "Editor : saving map"
		self.gui.setInfo(msg)
		self.map.save(self.map.filename)
		
	
	def load(self, filename, extraArgs=[]):
		#print "Editor : loading map %s" % (filename)
		msg = "Loading map " + filename + "... Please wait..."
		self.gui.setInfo(msg)
		self.gm.load(filename)
		
	#-----------------------------
	# map objects
	def addMapObject(self, genre, name, pos=(0,0,0), hpr=(0,0,0), scale=(1,1,1)):
		if name not in self.map.mapObjects:
			mapObject = MapObject(self, genre, name)
			mapObject.setPos(pos) #-self.collisionGrid.terrainScale/3.0)
			mapObject.setHpr(hpr)
			mapObject.setScale(scale)
			mapObject.reparentTo(self.map.mapObjectRoot)
			self.map.mapObjects[name] = mapObject
		
	def removeMapObject(self, name, extraArgs=[]):
		if name in self.map.mapObjects:
			self.stopObjectAction()
			self.map.mapObjects[name].destroy()
			del self.map.mapObjects[name]
		
	def setMapObjectPos(self, name, x, y, z=0):
		if name in self.mapObjects:
			self.map.mapObjects[name].setPos(x, y, z)
	
	
	def onClickObject(self):
		# click on MapObject :
		name = self.getHoverObjectName()
		if name is not None:
			print "map editor : left click on %s" % (name)
		else:
			print "map editor : left click on nothing"
			
	def onClickObject2(self):
		# click on MapObject :
		name = self.getHoverObjectName()
		if name is not None:
			print "map editor : middle click on %s" % (name)
		else:
			print "map editor : middle click on nothing"
	
	
	def onClickObject3(self):
		# click on MapObject :
		name = self.getHoverObjectName()
		if name is not None:
			print "map editor : right click on %s" % (name)
			if base.mouseWatcherNode.hasMouse():
				mpos = base.mouseWatcherNode.getMouse()
				self.gui.openObjectMenu(self.map.mapObjects[name], mpos)
				self.gui.objectMenu.buttons[1].bind(DGG.B1PRESS, self.startDrag, [self.map.mapObjects[name]])
				self.gui.objectMenu.buttons[2].bind(DGG.B1PRESS, self.startRotate, [self.map.mapObjects[name]])
				self.gui.objectMenu.buttons[3].bind(DGG.B1PRESS, self.startMoveZ, [self.map.mapObjects[name]])
				self.gui.objectMenu.buttons[5].bind(DGG.B1PRESS, self.removeMapObject, [name])
				
		else:
			print "map editor : right click on nothing"
			self.gui.objectMenu.hide()
	
	#-----------------------------
	# map collisions	
	def clearCollision(self, args=[]):
		if self.mode == "collision":
			self.map.collisionGrid.clear()
		
	def fillCollision(self, args=[]):
		if self.mode == "collision":
			self.map.collisionGrid.fill()
		
	def addCollision(self, x, y):
		self.map.collisionGrid.showTile(x, y)
		
	def removeCollision(self, x, y):
		self.map.collisionGrid.hideTile(x, y)
		
	
	def checkObj(self, dt=0.01):
		if self.keyDic[EDITOR_LEFT]:
			self.selectedObj.rotate(dt)
		elif self.keyDic[EDITOR_RIGHT]:
			self.selectedObj.rotate(-dt)
			
		if self.keyDic[EDITOR_UP]:
			self.selectedObj.moveZ(dt)
		elif self.keyDic[EDITOR_DOWN]:
			self.selectedObj.moveZ(-dt)
	
	#-----------------------------
	# editor update task
	def update(self, task):
		dt = globalClock.getDt()
		if base.mouseWatcherNode.hasMouse():
			mpos = base.mouseWatcherNode.getMouse()
			pos = self.clicker.getMouseTilePos(mpos)
		else:
			mpos = None
			pos = None
		
		# collision editing
		if self.mode == "collision" and self.keyDic["mouse1"] and pos is not None:
			self.addCollision(pos[0], pos[1])
		
		elif self.mode == "collision" and self.keyDic["mouse3"] and pos is not None:
			self.removeCollision(pos[0], pos[1])
		
		# map objects control
		
		if self.mode == "object" and mpos is not None:
			if self.objectMode == "drag":
				objPos = self.clicker.getMousePos(mpos)
				objPos = Vec3(objPos[0], objPos[1], self.selectedObj.getZ())
				self.selectedObj.setPos(objPos)
				self.checkObj(dt)
			#elif self.objectMode == "rotate":
			elif self.objectMode == "rotate" or self.objectMode == "moveZ":
				self.checkObj(dt)
				
			name = self.getHoverObjectName()
			if name is not None:
				msg = "mapObject : " + name
				self.gui.setObjInfo(mpos, msg)
			else:
				self.gui.clearObjInfo()
		
		# camera control
		if self.keyDic[FORWARD]:
			self.camHandler.forward(dt)
		if self.keyDic[BACKWARD]:
			self.camHandler.backward(dt)
		
		if self.keyDic[STRAFE_LEFT]:
			self.camHandler.strafeLeft(dt)
			
		if self.keyDic[STRAFE_RIGHT]:
			self.camHandler.strafeRight(dt)
			
		if self.keyDic[TURN_LEFT]:
			self.camHandler.turnLeft(dt)
		if self.keyDic[TURN_RIGHT]:
			self.camHandler.turnRight(dt)
			
		if self.keyDic[UP]:
			self.camHandler.lookUp(dt)
		if self.keyDic[DOWN]:
			self.camHandler.lookDown(dt)
				
		return task.cont
	

#-----------------------------------------------------------------------
# Game : FSM, switch between game playing and map editing
#-----------------------------------------------------------------------
class Game(FSM, DirectObject):
	def __init__(self, filename):
		FSM.__init__(self, 'Game')
		self.map = None
		self.mapManager = None
		self.editor = None
		
		self.loadGameMap(filename)
				
		# camera handler
		self.camHandler = CamHandler()
		self.setMode("playing")
		
		self.cursor = MouseCursor()
		
		self.playerData = {}
		self.playerData["name"] = "Gaspard"
		self.playerData["sex"] = "male"
		
		self.mapManager = MapManager(self)
		self.editor = MapEditor(self)
		
		self.mapManager.player.data = self.playerData
		
		# light
		if CONFIG_LIGHT:
			self.light = LightManager()
			self.light.lightCenter.setPos(0,0,0)
			self.light.lightCenter.reparentTo(base.camera)
		
		self.accept(OPEN_EDITOR, self.toggle)
			
		self.request("Game")
			
	def loadGameMap(self, filename):
		print "Game : load game map %s" % (filename)
		if self.map:
			self.mapManager.removeAllNPC()
			self.map.destroy()
			del self.map
			
		self.map = Map(filename)
		if self.map.collisionGrid:
			print "Game : loaded new game map %s, it has a collisionGrid %s" % (str(self.map), str(self.map.collisionGrid))
		else:
			print "Game : loaded new game map %s, but WARNING : collisionGrid not found" % (filename)
			
		if self.mapManager:
			print "Game : assigning new map %s to mapManager" % (filename)
			self.mapManager.setMap(self.map)
		if self.editor:
			print "Game : assigning new map %s to editor" % (filename)
			self.editor.setMap(self.map)
		
	def load(self, filename):
		self.prevState = self.state
		self.request("LoadMode")
		self.loadGameMap(filename)
		self.request(self.prevState)
		
	def setMode(self, mode):
		self.mode = mode
		#self.camHandler.setMode(mode)
	
	def toggle(self):
		if self.state == "Game":
			self.request("Editor")
		elif self.state == "Editor":
			self.request("Game")
	
	def enterLoadMode(self):
		print "Game : Entering load mode"
		
		
	def exitLoadMode(self):
		print "Game : Exiting load mode"
		
	
	def enterGame(self):
		self.setMode("playing")
		self.mapManager.start()
		
	def exitGame(self):
		self.mapManager.stop()
		
	def enterEditor(self):
		self.setMode("edit")
		self.editor.start()
		
	def exitEditor(self):
		self.editor.stop()
		
if __name__ == "__main__":
	
	game = Game("maps/mapCode3.txt")
	
	props = WindowProperties()
	props.setCursorHidden(True) 
	base.win.requestProperties(props)
	
	base.accept("escape", sys.exit)
	
	base.disableMouse()
	base.setFrameRateMeter(True)
	
	render.setShaderAuto()
	render.setTransparency(TransparencyAttrib.MAlpha)
	#render.setAntialias(AntialiasAttrib.MMultisample)
	#render.setAntialias(AntialiasAttrib.MAuto)
	#PStatClient.connect()
	
	run()
