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


from lightManager import LightManager

from mouseCursor import *

#from gui import *
#from guiDialog import *
from guiEditor import EditorGui
from guiGame import GameGui

from dialog import *
from mapObject import *
from map import Map

from effects import WaterPlane, GrassEngine
from wallBuilder import WallBuilder



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
		return None
	
	def getHoverNPCName(self):
		if base.mouseWatcherNode.hasMouse():
			mpos = base.mouseWatcherNode.getMouse()
			pos = self.clicker.getMouseTilePos(mpos)
			res = self.clicker.getMouseObject(self.map.NPCroot)
			if res is not None:
				name = res.getIntoNodePath().getName()
				return name
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
		for name, sex in [("ula2", "female"), ("Kimmo", "male"), ("Drunkard", "male"), ("Camilla", "female")]:
			x, y = self.map.collisionGrid.getRandomTile()
			# yes, we will have to think about something smarter in the long run, i know...
			if sex == "female":
				self.addNPC(name, "models/characters/female", "models/characters/female1.jpg", x,y)
			else:
				self.addNPC(name, "models/characters/male", "models/characters/humanTex2.png", x,y)

		name = self.gm.playerData["name"]
		sex = self.gm.playerData["sex"]
		
		if sex == "male":
			modelPath = "models/characters/male"
		else:
			modelPath = "models/characters/female"
		
		
		self.player = NPC(name, modelPath)
		self.player.addEquipment("models/characters/female_hair", "models/characters/female_hair.jpg")
		self.player.addEquipment("models/equipment/bag", "models/equipment/bag.jpg")
		
		self.NPC["Camilla"].addEquipment("models/characters/female_hair", "models/characters/female_hair2.jpg")
		self.NPC["Camilla"].addEquipment("models/equipment/stick", "models/equipment/stick.jpg")
		
		self.NPC["ula2"].addEquipment("models/characters/female_hair", "models/characters/female_hair3.jpg")
		
		self.NPC["ula2"].addEquipment("models/equipment/bag", "models/equipment/bag.jpg")
		self.NPC["Kimmo"].addEquipment("models/equipment/bag", "models/equipment/bag.jpg")
		self.NPC["Drunkard"].addEquipment("models/equipment/stick", "models/equipment/stick.jpg")
		
		self.player.setTilePos(5, 3)
		self.player.reparentTo(render)
		
		self.dialog = None # current dialog
		
		#self.msg = makeMsg(-1.3,0.95,"...")
		
		#self.msgTilePos = makeMsg(-1.2,0.95,"...")
		
		self.gui = GameGui(self)
		
	def start(self):
		#self.msg.show()
		#self.msgTilePos.show()
		self.gui.show()
		
		self.task = taskMgr.add(self.update, "MapManagerTask")
		self.startAccept()
		if self.map.bgMusic:
			self.map.bgMusic.play()
			self.map.bgMusic.setVolume(0.4)
		if self.map.bgSound:
			self.map.bgSound.play()
			
	def stop(self):
		#self.msg.hide()
		#self.msgTilePos.hide()
		self.gui.hide()
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
		
		self.accept(SAVE, self.save, ["save/sonia.txt"])
		self.accept(OPEN, self.load, ["save/sonia.txt"])
		self.accept(INVENTORY, self.gui.inventory.toggle)
		
	def save(self, filename):
		f = open(filename, 'w')
		pickle.dump(self.gm.playerData, f)
		f.close()
		print "player data saved as %s" % (filename)
		
	def load(self, filename):
		f = open(filename, 'r')
		playerData = pickle.load(f)
		f.close()
		self.gm.playerData = playerData
		#for key in playerData:
		#	self.gm.playerData[key] = playerData[key]
		print("player data loaded from file %s, data = %s" % (filename, self.gm.playerData))
		self.playerData = self.gm.playerData
		
	def setMode(self, mode="move"):
		if mode == "move":
			print "Map Manager switched to move mode"
			self.mode = "move"
			self.accept("mouse1", self.onClickObject) # left click
			#self.accept("mouse2", self.onClickObject2) # scroll click
			#self.accept("mouse3", self.onClickObject3) # right click
			self.accept("wheel_up", self.camHandler.moveHeight, [-0.02])
			self.accept("wheel_down", self.camHandler.moveHeight, [0.02])
				
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
		#self.msgTilePos.setText(modeMsg)
		self.gui.setInfo(modeMsg)
			
		
	
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
				#self.msg.setText(msg)
				#self.msg.setPos(mpos.getX()*1.33+0.1, mpos.getY()+0.02)
				self.gui.setObjInfo(mpos, msg)
				
			else:
				name = self.getHoverNPCName()
				if name is not None:
					msg = "talk to : " + name
					#self.msg.setText(msg)
					#self.msg.setPos(mpos.getX()*1.33+0.1, mpos.getY()+0.02)
					self.gui.setObjInfo(mpos, msg)
				else:
					self.gui.clearObjInfo()
					#self.msg.setText("")
		
		self.updateCam(dt)
		
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
		self.map.collisionShow()
		
	def stop(self):
		print "Stopping editor"
		self.gui.hide()
		taskMgr.remove(self.task)
		self.ignoreAll()
		self.map.collisionHide()
		
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
		
		self.accept(SAVE, self.save)
		self.accept(OPEN, self.load, ["maps/mapCode.txt"])
		
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
			
		self.accept("wheel_up", self.camHandler.moveHeight, [-0.05])
		self.accept("wheel_down", self.camHandler.moveHeight, [0.05])
		
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
	
	def startScale(self, obj, extraArgs=[]):
		self.gui.objectMenu.hide()
		self.objectMode = "scale"
		self.gui.setInfo("scaling object")
		self.selectedObj = obj
		self.accept("mouse1", self.stopScale)
	
	def stopScale(self, extraArgs=[]):
		self.gui.setInfo("stopped scaling object")
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
		self.map.addMapObject(genre, name, pos, hpr, scale)
		
	def addNewMapObject(self, genre, extraArgs=[]):
		self.gui.addObjectMenu.retract()
		name = self.map.getAvailableName(genre)
		self.addMapObject(genre, name)
		obj = self.map.mapObjects[name]
		self.setMode("object")
		self.startDrag(obj)
		
	def removeMapObject(self, name, extraArgs=[]):
		if name in self.map.mapObjects:
			self.stopObjectAction()
			self.map.removeMapObject(name)
			#self.map.mapObjects[name].destroy()
			#del self.map.mapObjects[name]
		
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
				self.gui.objectMenu.buttons[4].bind(DGG.B1PRESS, self.startScale, [self.map.mapObjects[name]])
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
	
	def scaleObj(self, dt=0.01):
		if self.keyDic[EDITOR_UP]:
			self.selectedObj.scale(dt)
		elif self.keyDic[EDITOR_DOWN]:
			self.selectedObj.scale(-dt)
	
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
			elif self.objectMode == "scale":
				self.scaleObj(dt)
				
			name = self.getHoverObjectName()
			if name is not None:
				msg = "mapObject : " + name
				self.gui.setObjInfo(mpos, msg)
			else:
				self.gui.clearObjInfo()
		
		# camera control
		self.updateCam(dt)
		
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
		self.playerData["name"] = "Galya"
		self.playerData["sex"] = "female"
		
		self.mapManager = MapManager(self)
		self.editor = MapEditor(self)
		
		self.mapManager.playerData = self.playerData
		
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
		self.camHandler.setMode(mode)
	
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
	#render.setShaderAuto()
	render.setShaderOff()
	
	
	genShader = loader.loadShader("shaders/arishade2.sha")
	render.setShaderInput('cam', base.camera)
	render.setShaderInput('bgcolor', 1,1,1)
	light1 = NodePath("light")
	light1.setPos(25,30,15)
	light2 = NodePath("light2")
	light2.setPos(27,32,14)
	
	render.setShaderInput('light', light1)
	render.setShaderInput('light2', light2)
	
	
	render.setShader(genShader)
	
	'''
	shadow_map_temp = Texture()
	shadow_buffer = base.win.makeTextureBuffer('shadow', 2048, 2048, shadow_map_temp)

	shadow_cam = base.makeCamera(shadow_buffer)
	shadow_cam.reparentTo(light1)
	  
	lens = OrthographicLens()
	lens.setFilmSize(500, 500)  # Or whatever is appropriate for your scene
	shadow_cam.node().setLens(lens)
	shadow_cam.node().getDisplayRegion(0).setClearColor(Vec4(0, 0, 0, 1))
	shadow_cam.node().getDisplayRegion(0).setClearColorActive(1)
	shadow_cam.reparentTo(light1)
	shadow_cam.lookAt(light2)

	shadow_map = Texture()
	shadow_map.setMinfilter(Texture.FTShadow)
	shadow_map.setMagfilter(Texture.FTShadow)
	shadow_buffer.addRenderTexture(shadow_map, GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPDepth)
	'''
	
	game = Game("maps/mapCode3.txt")
	w0 = WaterPlane(-1000,-1000,1000,1000)
	
	l1 = [Point3(0,0,0), Point3(250,0,0), Point3(250,120,0), Point3(0,120,0), Point3(0,0,0)]
	w1 = WallBuilder(0.2, 4.0, "img/textures/wood_wall.jpg", l1)
	
	l2 = [Point3(50,0,0), Point3(50,40,0), Point3(80,40,0), Point3(60,120,0)]
	w2 = WallBuilder(0.2, 4.0, "img/textures/wood_wall.jpg", l2)
	
	p = GrassEngine(base.camera, 200, 100)
	
	'''
	for i in range(200):
		aloe = loader.loadModel("models/nature/grass_1")
		aloe.reparentTo(render)
		aloe.setScale(0.25*random.randint(1,5))
		aloe.setTwoSided(True)
		aloe.setBillboardAxis()
		aloe.setPos(random.randint(1,200),random.randint(1,100),0)
		
	for i in range(200):
		aloe = loader.loadModel("models/nature/grass_2")
		aloe.reparentTo(render)
		aloe.setScale(0.25*random.randint(1,5))
		aloe.setTwoSided(True)
		aloe.setBillboardAxis()
		aloe.setPos(random.randint(1,200),random.randint(1,100),0)
	'''
	props = WindowProperties()
	props.setCursorHidden(True) 
	base.win.requestProperties(props)
	
	base.accept("escape", sys.exit)
	base.camLens.setNearFar(1.0, 5000)
	base.disableMouse()
	base.setFrameRateMeter(True)
	
	
	#color = (0.8,0.8,0.8,0.5)
	color = (1,1,1,1)
	expfog = Fog("Scene-wide exponential Fog object")
	expfog.setColor(color)
	expfog.setExpDensity(0.01)
	#render.setFog(expfog)
	base.setBackgroundColor(color)
	
	
	#render.flattenStrong()
	#render.flattenMedium()
	#render.setTransparency(TransparencyAttrib.MAlpha)
	#render.setAntialias(AntialiasAttrib.MMultisample)
	#render.setAntialias(AntialiasAttrib.MAuto)
	
	#PStatClient.connect()
	#loadPrcFileData('setup', 'dump-generated-shaders #t')
	
	#shader = loader.loadShader("shaders/arishade2.sha")
	#render.setShader(shader)
	#render.setShaderInput("light", game.light.light)
	#render.setShaderInput("light2", game.light.lightCenter)
	#render.setShaderInput("cam", base.camera)
	
	run()
