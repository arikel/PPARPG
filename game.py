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
text-minfilter linear_mipmap_nearest
text-flatten 0
framebuffer-multisample 1
multisamples 2
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


from camHandler import EditorCamHandler, GameCamHandler
from lightManager import LightManager
from mouseCursor import *

#from gui import *
#from guiDialog import *
from guiEditor import EditorGui
from guiGame import GameGui
from guiMenu import MainMenu

from dialog import *
from mapObject import *
from map import Map

from effects import WaterPlane, GrassEngine
from wallBuilder import WallBuilder

from gameUtils import *

#-----------------------------------------------------------------------
# MapManagerBase, for MapManager and MapEditor
#-----------------------------------------------------------------------
class MapManagerBase(DirectObject):
	def __init__(self, gm):
		self.gm = gm # Game
		self.cursor = self.gm.cursor
		self.clicker = Clicker()
		self.map = self.gm.map
		#self.camHandler = self.gm.camHandler
		#for obj in self.map.mapObjects.values():
		#	print "map manager base : %s is at %s" % (obj.name, obj.getPos())
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
		if self.map.collisionGrid.hasGeoMip:
			self.clicker.setHeight(self.map.collisionGrid.ground.terrainScale)
		else:
			self.clicker.setHeight(0)
		
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
	
	def getHoverCreatureName(self):
		if base.mouseWatcherNode.hasMouse():
			mpos = base.mouseWatcherNode.getMouse()
			pos = self.clicker.getMouseTilePos(mpos)
			res = self.clicker.getMouseObject(self.map.creatureRoot)
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
		
		# player
		self.gameState = self.gm.gameState
		self.playerState = self.gm.playerState
		name = self.playerState.name
		sex = self.playerState.sex
		
		if sex == "male":
			modelPath = "models/characters/neoMale"
		else:
			modelPath = "models/characters/neoFemale"
			
		self.player = MapNPC(self, name, modelPath, "models/characters/female1.jpg", "player")
		self.player.addEquipment("models/characters/female_hair", "models/characters/female_hair.jpg")
		self.player.addEquipment("models/equipment/bag", "models/equipment/bag1.jpg")
		startX, startY = self.map.collisionGrid.getRandomTile()
		self.player.setTilePos(startX, startY)
		self.player.reparentTo(render)
		self.player.toggleLabel()
		
		
		
		# NPCs
		self.NPC = {}
		self.NPCAI = {}
		
		for name, sex in [("ula2", "female"), ("Kimmo", "male"), ("Drunkard", "male"), ("Camilla", "female")]:
			x, y = self.map.collisionGrid.getRandomTile()
			# yes, we will have to think about something smarter in the long run, i know...
			if sex == "female":
				self.addNPC(name, "models/characters/neoFemale", "models/characters/female1.jpg", x,y)
			else:
				self.addNPC(name, "models/characters/neoMale", "models/characters/neoMale.jpg", x,y)
		
		self.NPC["Camilla"].addEquipment("models/characters/female_hair", "models/characters/female_hair2.jpg")
		self.NPC["Camilla"].addEquipment("models/equipment/stick", "models/equipment/stick.jpg")
		
		self.NPC["ula2"].addEquipment("models/characters/female_hair", "models/characters/female_hair3.jpg")
		
		self.NPC["ula2"].addEquipment("models/equipment/bag", "models/equipment/bag1.jpg")
		self.NPC["Kimmo"].addEquipment("models/equipment/bag", "models/equipment/bag1.jpg")
		self.NPC["Drunkard"].addEquipment("models/equipment/stick", "models/equipment/stick.jpg")
		
		# monsters
		self.mobs = {}
		
		# drops
		self.drops = {}
		self.addDrop("machin", 5, self.player.getPos()+Vec3(4,0,0.25))
		self.addDrop("machin", 5, self.player.getPos()+Vec3(0,2,0.25))
		self.addDrop("machin", 5, self.player.getPos()+Vec3(4,2,0.25))
		
		
		
		
		
		self.dialog = None # current dialog
		
		self.gui = GameGui(self)
		self.gui.hide()
		#self.map.collisionHide()
		#for obj in self.map.mapObjects.values():
		#	print "map manager init says : %s is at %s" % (obj.name, obj.getPos())
			
	def start(self):
		self.gui.show()
		
		self.task = taskMgr.add(self.update, "MapManagerTask")
		self.startAccept()
		if self.map.bgMusic:
			self.map.bgMusic.play()
			#self.map.bgMusic.setVolume(0.4)
		if self.map.bgSound:
			self.map.bgSound.play()
		for NPCAI in self.NPCAI:
			self.NPCAI[NPCAI].request("Wander")
			
	def stop(self):
		self.gui.hide()
		taskMgr.remove(self.task)
		self.ignoreAll()
		if self.map.bgMusic:
			self.map.bgMusic.stop()
			#self.map.bgMusic.setVolume(0.4)
		if self.map.bgSound:
			self.map.bgSound.stop()
		for NPCAI in self.NPCAI:
			self.NPCAI[NPCAI].request("Pause")
		
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
		self.setMode(self.mode) # mouse click events

		self.accept(SAVE, self.save, [self.gameState.filename])
		self.accept(OPEN, self.load, [self.gameState.filename])
		
		self.accept(INVENTORY, self.gui.inventory.toggle)
		self.accept("mouse2", self.gm.gameCam.startDrag)
		self.accept("mouse2-up", self.gm.gameCam.stopDrag)
		self.accept("wheel_up", self.gm.gameCam.zoom, [1.0])
		self.accept("wheel_down", self.gm.gameCam.zoom, [-1.0])
		
		self.accept("playerDied", self.onPlayerDie)
		
		
		
	def onPlayerDie(self):
		print "Map Manager : the player has died, let's move to title screen..."
		
	def save(self, filename):
		#f = open(filename, 'w')
		#pickle.dump(self.gm.playerData, f)
		#f.close()
		self.gm.gameState.saveAs(filename)
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
			#print "Map Manager switched to move mode"
			self.mode = "move"
			self.accept("mouse1", self.onClickObject) # left click
			#self.accept("mouse2", self.onClickObject2) # scroll click
			self.accept("mouse3", self.onClickObject3) # right click
			#self.accept("wheel_up", self.camHandler.moveHeight, [-0.02])
			#self.accept("wheel_down", self.camHandler.moveHeight, [0.02])
				
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
		if self.dialog:return
		
		name = self.getHoverNPCName()
		if name is not None and not self.gui.inventory.visible and not self.dialog:
			print "map manager : left click on NPC : %s, opening dialog" % (name)
			if self.getPlayerDistToNPC(name)< 4.0:
				self.openDialog(name)
			else:
				x, y = self.map.getClosestOpenTile(self.NPC[name].getTilePos()[0], self.NPC[name].getTilePos()[1])
				self.playerGoto(x, y)
			return
		
		name = self.getHoverObjectName()
		if name is not None and not self.gui.inventory.visible and not self.dialog:
			print "map manager : left click on map object : %s, position = %s" % (name, self.map.mapObjects[name].getPos())
			return
			
		name = self.getHoverCreatureName()
		if name is not None:
			print "Click on %s" % (name)
			return
			
		if base.mouseWatcherNode.hasMouse() and not self.gui.inventory.visible and not self.dialog:
			mpos = base.mouseWatcherNode.getMouse()
			pos = self.clicker.getMouseTilePos(mpos)
			self.playerGoto(pos[0], pos[1])
			print "Player goto %s/%s" % (pos[0], pos[1])
			return
		# and this should never happen
		print "WARNING : map manager : left click on nothing?!"
		return False
	
	
	def onClickObject3(self):
		# click on MapObject :
		if self.dialog:return
		
		name = self.getHoverNPCName()
		if name is not None and not self.gui.inventory.visible and not self.dialog:
			print "map manager : right click on NPC : %s, label toggle" % (name)
			#self.NPC[name].toggleLabel()
			self.gui.objectMenu.rebuild(["look", "talk", "attack"])
			self.gui.objectMenu.buttons[0].bind(DGG.B1PRESS, self.onTalkTo, [name])
			self.gui.objectMenu.buttons[1].bind(DGG.B1PRESS, self.onTalkTo, [name])
			self.gui.objectMenu.buttons[2].bind(DGG.B1PRESS, self.onTalkTo, [name])
			self.gui.objectMenu.expand()
			if base.mouseWatcherNode.hasMouse():
				mpos = base.mouseWatcherNode.getMouse()
				self.gui.objectMenu.setPos(mpos)
				self.gm.cursor.setMode()
			#self.openDialog(name)
			return
		
		name = self.getHoverObjectName()
		if name is not None and not self.gui.inventory.visible and not self.dialog:
			print "map manager : right click on map object : %s, position = %s" % (name, self.map.mapObjects[name].getPos())
			return
		
		name = self.getHoverCreatureName()
		if name is not None and not self.gui.inventory.visible and not self.dialog:
			print "map manager : right click on map creature / drop : %s, position = %s" % (name, self.drops[name].getPos())
			return
			
		if base.mouseWatcherNode.hasMouse() and not self.dialog:
			#mpos = base.mouseWatcherNode.getMouse()
			#pos = self.clicker.getMouseTilePos(mpos)
			#self.playerGoto(pos[0], pos[1])
			#print "Player goto %s/%s" % (pos[0], pos[1])
			#self.gm.cursor.setMode()
			self.gui.inventory.toggle()
			return
		# and this should never happen
		#print "WARNING : map manager : right click on nothing?!"
		return False
	
	def onTalkTo(self, name, extraArgs=[]):
		self.gui.closeMenu() # in case we asked the talk to from this context menu
		
		if self.getPlayerDistToNPC(name)< 4.0:
			self.openDialog(name)
		else:
			tile = self.map.getClosestOpenTile(self.NPC[name].getTilePos()[0], self.NPC[name].getTilePos()[1])
			if tile:
				x, y = tile
				self.playerGoto(x, y)
				self.player.sequence.append(Func(self.onTalkTo, name))
				self.player.sequence.resume() # ?
				#print "Appended talkTo %s to sequence %s" % (name, self.player.sequence)
			else:
				print "%s can't be reached." % (name)
				
		self.gm.cursor.setMode()
		
		
	def getDropNewName(self, genre):
		i = 1
		tmpName = genre + "_" + str(i)
		while tmpName in self.drops:
			i = i+1
			tmpName = genre + "_" + str(i)
		return tmpName
		
	def addDrop(self, genre, nb, pos):
		name = self.getDropNewName(genre)
		drop = MapDrop(self, name, genre, nb, pos)
		self.drops[name] = drop
			
	def addNPC(self, name, modelName, tex, x, y):
		npc = MapNPC(self, name, modelName, tex)
		npc.setTilePos(x, y)
		self.NPC[name] = npc
		npc.reparentTo(self.map.NPCroot)
		ai = NPCAI(self, name)
		self.NPCAI[name] = ai
		
	def removeNPC(self, name):
		if name in self.NPC:
			self.NPC[name].destroy()
			del self.NPC[name]
		if name in self.NPCAI:
			self.NPCAI[name].stop()
			del self.NPCAI[name]
			
	def removeAllNPC(self):
		for name in self.NPC.keys():
			self.NPC[name].destroy()
			del self.NPC[name]
			if name in self.NPCAI:
				self.NPCAI[name].stop()
				del self.NPCAI[name]

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
	
	def getPlayerDistToNPC(self, name):
		return Vec3(self.NPC[name].getPos() - self.player.getPos()).length()
		
	def getPlayerDistToMapObject(self, name):
		return Vec3(self.map.mapObjects[name].getPos() - self.player.getPos()).length()
	
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
	
	def openDialog(self, name, extraArgs=[]):
		if self.dialog:
			#print "There was dialog garbage left, %s got his/her dialog shut unpolitely." % (self.dialog.name)
			#self.dialog.destroy()
			print "... but a dialog is already open for %s, aborting." % self.dialog.name
			return False
		if name in self.NPC:
			self.NPC[name].stop()
			playerPos = self.player.getTilePos()
			npcPos = self.NPC[name].getTilePos()
			lookDirX, lookDirY = playerPos[0]-npcPos[0], playerPos[1]-npcPos[1]
			self.NPC[name].lookAt(lookDirX, lookDirY)
			
			self.player.stop()
			self.player.lookAt(-lookDirX, -lookDirY)
			
			if name in dialogDic:
				self.gui.openDialog(name)
				self.dialog = dialogDic[name](self, name)
			else:
				self.gui.openDialog(name)
				self.dialog = Dialog(self, name)
		else:
			print "Error, dialog called for unknown NPC : %s" % (name)
			
	def updateCam(self):
		self.gm.gameCam.update()
	
	def update(self, task):
		self.updateCam()
		if self.dialog:
			self.cursor.clear()
			return task.cont
			
		if self.gui.inventory.visible:
			#self.gui.clearObjInfo()
			#self.cursor.clear()
			#self.gm.cursor.setMode()
			return task.cont
		
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
				msg = "in game object : " + name + "\npos = " + str(self.map.mapObjects[name].getPos())
				#self.gui.setObjInfo(mpos, msg)
				self.cursor.setMode("hand")
				self.cursor.setInfo(msg)
				return task.cont
			
			name = self.getHoverNPCName()
			if name is not None:
				msg = "talk to : " + name + "\npos = " + str(self.NPC[name].getPos())
				#self.gui.setObjInfo(mpos, msg)
				self.cursor.setInfo(msg)
				if not self.gui.objectMenu.open:
					self.cursor.setMode("talk")
				return task.cont
			
			name = self.getHoverCreatureName()
			if name is not None:
				self.cursor.setMode("hand")
				msg = "drop : " + name
				self.cursor.setInfo(msg)
				#self.gui.setObjInfo(mpos, msg)
				return task.cont
				
			#self.gm.cursor.setMode("default")
			#self.gui.clearObjInfo()
			if self.cursor.item is None:
				self.cursor.clear()
			#if self.cursor.item is not None and self.cursor.mode is "default":
			else:
				self.cursor.setInfo(str(self.cursor.itemNb))
				
			return task.cont
		
		return task.cont

#-----------------------------------------------------------------------
# MapEditor : handles the map editing
#-----------------------------------------------------------------------
class MapEditor(MapManagerBase):
	def __init__(self, gm):
		self.mode = "collision"
		
		MapManagerBase.__init__(self, gm)
		self.camHandler = self.gm.editorCam
		# while self.mode == "edit", self.objectMode can become :
		# drag, rotating, scaling
		self.objectMode = None
		self.selectedObj = None
		
		self.gui = EditorGui(self)
		
	#-----------------------------
	# modes and input
	
	def start(self):
		#print "Starting editor"
		self.gui.show()
		self.startAccept()
		self.task = taskMgr.add(self.update, "MapEditorTask")
		#if self.map.bgMusic:
		#	self.map.bgMusic.stop()
		#self.map.collisionShow()
		self.map.collisionGrid.rebuild()
		print "rebuilding grid"
		
	def stop(self):
		#print "Stopping editor"
		self.gui.hide()
		taskMgr.remove(self.task)
		self.ignoreAll()
		#self.map.collisionHide()
		self.map.collisionGrid.np.flattenStrong()
		print "flattening grid"
		self.camHandler.stop()
		
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
				self.gui.objectMenu.buttons[5].bind(DGG.B1PRESS, self.duplicateMapObject, [self.map.mapObjects[name]])
				self.gui.objectMenu.buttons[6].bind(DGG.B1PRESS, self.removeMapObject, [name])
				
		else:
			print "map editor : right click on nothing"
			self.gui.objectMenu.hide()
		
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
		
	def duplicateMapObject(self, obj, extraArgs=[]):
		self.gui.addObjectMenu.retract()
		genre = obj.genre
		name = self.map.getAvailableName(genre)
		self.addMapObject(genre, name)
		newObj = self.map.mapObjects[name]
		newObj.setScale(obj.getScale())
		newObj.setRot(obj.getRot())
		self.setMode("object")
		self.startDrag(newObj)
		
		
	def removeMapObject(self, name, extraArgs=[]):
		if name in self.map.mapObjects:
			self.stopObjectAction()
			self.map.removeMapObject(name)
			#self.map.mapObjects[name].destroy()
			#del self.map.mapObjects[name]
		
	def setMapObjectPos(self, name, x, y, z=0):
		if name in self.mapObjects:
			self.map.mapObjects[name].setPos(x, y, z)
	
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
				#msg = "mapObject : " + name
				msg = "Map object : " + name + "\npos = " + str(self.map.mapObjects[name].getPos())
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
	def __init__(self, gamefilename=None):
		FSM.__init__(self, 'Game')
		self.gameState = GameState()
		if gamefilename is None:
			gamefilename = "save/default.txt"
		
		self.gameState.load(gamefilename)
		self.playerState = self.gameState.playerState
		self.gamefilename = gamefilename
		self.map = None
		self.mapManager = None
		self.editor = None
		self.prevMode = None # previous mode
		
		self.cursor = MouseCursor()
		
		self.mainMenu = MainMenu()
		self.mainMenu.buttons[0].bind(DGG.B1PRESS, self.request, ["Game"])
		self.mainMenu.buttons[3].bind(DGG.B1PRESS, self.quit)
		self.mainMenu.hide()
		
		self.mainMenuImg = makeImg(0,0,"img/bg/title1.jpg", (RATIO, 0,1))
		self.mainMenuImg.setBin("fixed", -150)
		self.request("MainMenu")
		
	def initGame(self, gamefilename=None):
		if gamefilename is None:
			gamefilename = self.gamefilename
		self.gameState = GameState()
		self.gameState.load(gamefilename)
		self.playerState = self.gameState.playerState
		
		self.loadGameMap(self.gameState.playerState.map)
		
		# editor camera handler
		self.editorCam = EditorCamHandler()
		
		
		
		self.playerData = {}
		self.playerData["name"] = "Galya"
		self.playerData["sex"] = "female"
		
		#print "Game manager : creating map manager"
		self.mapManager = MapManager(self)
		self.mapManager.playerData = self.playerData
		
		# game camera handler
		self.gameCam = GameCamHandler(self.mapManager.player.model)
		self.setMode("playing")
		
		#print "Game manager : creating map editor"
		self.editor = MapEditor(self)
		
		
		
		# light
		if CONFIG_LIGHT:
			self.light = LightManager(self.mapManager.player.model)
			self.light.lightCenter.setPos(0,0,3)
			self.light.lightCenter.reparentTo(self.mapManager.player.model)
		
		self.accept(OPEN_EDITOR, self.toggle)
		
	def quit(self, sentArgs=[]):
		sys.exit()
			
	def loadGameMap(self, filename):
		print "Game : load game map %s" % (filename)
		if self.map:
			self.mapManager.removeAllNPC()
			self.map.destroy()
			#del self.map
			
		self.map = Map(filename)
		if self.map.collisionGrid:
			#print "Game : loaded new game map %s, it has a collisionGrid %s" % (str(self.map), str(self.map.collisionGrid))
			print "Game : loaded new game map from file %s " % (filename)
		else:
			print "Game : loaded new game map %s, but WARNING : collisionGrid not found" % (filename)
			
		if self.mapManager:
			#print "Game : assigning new map %s to mapManager" % (filename)
			self.mapManager.setMap(self.map)
		if self.editor:
			#print "Game : assigning new map %s to editor" % (filename)
			self.editor.setMap(self.map)
		
	def load(self, filename):
		self.prevState = self.state
		self.request("LoadMode")
		self.loadGameMap(filename)
		self.request(self.prevState)
		
	def setMode(self, mode):
		self.mode = mode
		if mode == "game":
			self.gameCam.start()
		else:
			self.editorCam.start()
		
	def toggle(self):
		if self.state == "Game":
			self.request("Editor")
		elif self.state == "Editor":
			self.request("Game")
	
	def enterMainMenu(self, sentArgs=[]):
		self.mainMenu.show()
		self.mainMenuImg.show()
		self.accept("escape", self.request, ["Game"])
		
	def exitMainMenu(self):
		self.mainMenu.hide()
		self.mainMenuImg.hide()
		
	def enterLoadMode(self, sentArgs=[]):
		print "Game : Entering load mode"
		
		
	def exitLoadMode(self):
		print "Game : Exiting load mode"
		
	
	def enterGame(self, sentArgs=[]):
		if not self.map:
			self.initGame()
			
		self.setMode("game")
		self.accept("escape", self.request, ["MainMenu"])
		self.mapManager.start()
		
	def exitGame(self):
		self.mapManager.stop()
		
	def enterEditor(self, sentArgs=[]):
		self.setMode("edit")
		self.editor.start()
		
	def exitEditor(self):
		self.editor.stop()
		
if __name__ == "__main__":
	render.setShaderAuto()
	
	'''
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
	
	render.setShader(Shader.load("shaders/manouShadow.cg"))
	render.setShaderInput('push', 0.5,0.5,0.5 )
	render.setShaderInput('shadowcam', shadow_cam )
	render.setShaderInput('light1', light1 )
	render.setShaderInput('light2', light2 ) 
	render.setShaderInput('camera', base.camera)
	render.setShaderInput('globalambient', 0.5,0.5,0.5)
	render.setShaderInput('lightcolor', 1.0,1.0,1.0)
	render.setShaderInput('lightparams', 90,0,0)
	render.setShaderInput('shadowmap',shadow_map)
	render.setShaderInput('scale',1,1,1,1)
	render.node().setBounds(OmniBoundingVolume())
	render.node().setFinal(1)
	'''
	
	#game = Game("save/default.txt")
	game = Game()
	#game.map.setSize(250,180)
	#game.map.setGroundTexture("img/textures/ice01.jpg")
	#game.map.clearWalls()
	#game.map.clearInnerWall()
	
	
	#game.map.setSky("hipshot2")
	#game.map.setSky(None)
	#game.map.mapObjectRoot.flattenStrong()
	#print "hp = ", game.playerState.hp
	
	'''
	#size = 100
	#w0 = WaterPlane(-size, -size, size, size)
	#w0.destroy()
	w0 = WaterPlane(-20, -20, game.map.x+20, game.map.y+20)
	
	for i in range(5):
		crystal = loader.loadModel("models/props/crystal2")
		
		crystal.setShaderAuto()
		#crystal.setLightOff()
		ts = TextureStage('ts')
		ts.setMode(TextureStage.MGlow)
		crystal.setTexture(ts, loader.loadTexture("img/generic/glow.png"))
		crystal.setPos(22,12,0)
		h = random.randint(-30,30)
		p = random.randint(-30,30)
		r = random.randint(-30,30)
		s = random.random()*0.5+0.1
		crystal.setHpr(h,p,r)
		crystal.setScale(s)
		crystal.reparentTo(render)
	
	
	
	
	
	
	grassNp = NodePath("grass")
	grassNp.setPos(0,100,0)
	grassNp.reparentTo(base.camera)
	p = GrassEngine(grassNp, 100, 100)
	'''
	
	props = WindowProperties()
	props.setCursorHidden(True) 
	base.win.requestProperties(props)
	
	#base.accept("escape", sys.exit)
	base.camLens.setNearFar(1.0, 2000)
	base.disableMouse()
	base.setFrameRateMeter(True)
	
	
	
	color = (0,0,0,1)
	#color = (1,1,1,1)
	expfog = Fog("Scene-wide exponential Fog object")
	expfog.setColor(color)
	expfog.setExpDensity(0.02)
	#render.setFog(expfog)
	base.setBackgroundColor(color)
	
	#render.setAntialias(AntialiasAttrib.MMultisample)
	render.setAntialias(AntialiasAttrib.MAuto)
	#render.setAttrib(LightRampAttrib.makeHdr0())
	render.setAttrib(LightRampAttrib.makeHdr1())
	#render.setAttrib(LightRampAttrib.makeHdr2())
	#render.setAttrib(LightRampAttrib.makeSingleThreshold(0.5, 0.5))
	#render.setAttrib(LightRampAttrib.makeDoubleThreshold(0.5, 0.5, 0.5, 0.5))
	
	#filters = CommonFilters(base.win, base.cam)
	#filters.setCartoonInk(separation=0.5)
	#filters.setViewGlow()
	#filters.setVolumetricLighting(caster=game.mapManager.player.model)
	#filters.setBloom()
	#PStatClient.connect()
	#loadPrcFileData('setup', 'dump-generated-shaders #t')
	
	run()
