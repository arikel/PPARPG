#!/usr/bin/python
# -*- coding: utf8 -*-

from pandac.PandaModules import *

from direct.interval.IntervalGlobal import *
from direct.actor.Actor import Actor
from direct.task import Task

from guiBase import *

import math, random

mapObjectDB = {} # genre : [modelPath, texturePath, collisionPos]
mapObjectDB["house1"] = ["models/buildings/house", "models/buildings/house.jpg", (2.5,0,1,2)]
mapObjectDB["house2"] = ["models/buildings/ruin_house", "models/buildings/ruin_house.jpg", (5.2,-2.8,2,2)]


mapObjectDB["aldea1"] = ["models/buildings/aldea/aldea1", "models/buildings/aldea/aldea.jpg", (0,-2,1,1.5)]
mapObjectDB["aldea2"] = ["models/buildings/aldea/aldea2", "models/buildings/aldea/aldea.jpg", (0,-0.5,1,1.5)]
mapObjectDB["aldea_wood"] = ["models/props/aldea_wood", "models/buildings/aldea/aldea.jpg", (0,0,1,1)]
mapObjectDB["aldea_pot"] = ["models/props/aldea_pot", "models/buildings/aldea/aldea.jpg", (0,0,0.5,0.5)]

mapObjectDB["barrel"] = ["models/props/barrel", "models/props/barrel.jpg", (0,0,1,0.75)]
mapObjectDB["crate"] = ["models/props/crate1", "models/props/crate1.jpg", (0,0,0.5,0.5)]
mapObjectDB["rock1"] = ["models/props/rock", "models/props/rock.jpg", (0,0,0.5,0.5)]

#mapObjectDB["main_gate"] = ["models/buildings/main_gate", "models/buildings/house.jpg", (0,0,0.5,1.5)]

class MapObject:
	def __init__(self, gm, genre, name):
		self.gm = gm # reference to the game map the object belongs to
		self.genre = genre # NPC, building, decor, item, warp...
		self.name = name
		self.model = None
		self.modelPath = None
		self.texturePath = None
		
		self.state = None
		self.data = {}
		self.dialog = None
		self.task = None
		
		if self.genre in mapObjectDB:
			self.loadModel(mapObjectDB[self.genre][0], mapObjectDB[self.genre][1])
			self.addCollision(mapObjectDB[self.genre][2])
			
	def addCollision(self, pos):
		self.colSphere = CollisionSphere(pos[0],pos[1],pos[2],pos[3])
		#self.colSphere = CollisionTube(0,0,0,0,0,1.8,0.4)
		self.colNodepath = CollisionNode(self.name)
		self.colNode = self.model.attachNewNode(self.colNodepath)
		self.colNode.node().addSolid(self.colSphere)
		
	def loadModel(self, modelPath, texturePath=None):
		if self.model is not None:
			self.model.remove()
		self.modelPath = modelPath
		self.model = loader.loadModel(modelPath)
		self.model.setTransparency(TransparencyAttrib.MAlpha)
		
		if texturePath is not None:
			tex = loader.loadTexture(texturePath)
			self.texturePath = texturePath
			self.model.setTexture(tex)
		
		
	def loadActor(self, modelPath, animDic={}, texturePath=None):
		if self.model is not None:
			self.model.remove()
		
		self.model = Actor(modelPath, animDic)
		self.model.setTransparency(True)
		
		if texturePath is not None:
			tex = loader.loadTexture(texturePath)
			#self.model.clearTexture(TextureStage.getDefault())
			self.model.setTexture(tex)
		
	def reparentTo(self, np):
		self.model.reparentTo(np)
	
	#-------------------------------------------------------------------
	# Pos
	def setPos(self, pos):
		#self.model.setPos(pos[0], pos[1], pos[2])
		self.model.setPos(pos)
	
	def getPos(self):
		if self.model: return self.model.getPos()
		else: return None
			
	
	def setZ(self, z):
		self.model.setZ(z)
		
	def getZ(self):
		return self.model.getZ()
	
	def setTilePos(self, x, y):
		self.setPos((x+0.5, y+0.5, self.model.getZ()))
		
	def getTilePos(self):
		return int(self.model.getX()), int(self.model.getY())
	
	def moveZ(self, dt=0.01):
		self.model.setZ(self.model.getZ()+dt)
		
	#-------------------------------------------------------------------
	# Hpr
	def setHpr(self, hpr):
		self.model.setHpr(hpr)
		
	def getRot(self):
		return self.model.getH()
		
	def setRot(self, n):
		self.model.setH(n)
	
	def rotate(self, dt=0.01):
		self.model.setH(self.model.getH()+dt*50)
	
	#-------------------------------------------------------------------
	# Scale
	def setScale(self, scale):
		self.model.setScale(scale)
		
	def getScale(self):
		return self.model.getScale()
	
	def getScaleX(self):
		return self.model.getSx()
		
	def scale(self, dt=0.01):
		self.model.setScale(self.model.getSx() + dt)
		
	
		
	def destroy(self):
		if self.task:
			taskMgr.remove(self.task)
		if self.model:
			self.model.detachNode()
			self.model.remove()
		
		

#-----------------------------------------------------------------------
# NPC
#-----------------------------------------------------------------------

class NPC(MapObject):
	def __init__(self, name, modelPath="models/characters/male", texPath=None):
		self.name = name
		self.genre = "NPC"
		# actor
		self.model = None
		self.modelPath = modelPath
		modelName = modelPath.split("/")[-1]
		walkanim = "models/characters/" + modelName + "-walk"
		idleanim = "models/characters/" + modelName + "-idle"
		self.animDic = {
			"walk":walkanim,
			"idle": idleanim
		}
		self.texPath = texPath
		self.loadActor(self.modelPath, self.animDic, self.texPath)
		
		# collision
		self.addCollision()
		
		self.speed = 0.4
		
		self.path = []
		self.sequence = Sequence()
		
		
		self.timer = random.random()*5.0
		#self.timerMsg = makeMsg(0,0,"time")
		self.timerMsg = TextNode(self.name)
		self.timerMsg.setFont(FONT)
		self.timerMsg.setTextColor(0,0,0,1)
		
		
		self.timerMsg.setCardColor(1, 1, 1, 0.6)
		self.timerMsg.setCardAsMargin(0.5, 0.5, 0, 0.5)
		self.timerMsg.setCardDecal(True)
		
		self.timerLabel = render.attachNewNode(self.timerMsg)
		self.timerLabel.reparentTo(self.model)
		self.timerLabel.setPos(1,0,3)
		self.timerLabel.setBillboardAxis()
		self.timerLabel.setLightOff()
		#self.timerLabel.clearTexture(TextureStage.getDefault())
		self.timerLabel.setTexture(loader.loadTexture("img/generic/label.png"))
		self.timerLabel.setScale(0.4)
		#self.timerLabel.setColor(1,1,1,0.2)
		#self.timerLabel.setTransparency(True)
		
		self.timerLabel.setShaderOff(True)
		self.timerLabel.setLightOff(True)
		
		self.data = {}
		self.data["name"] = self.name
		
		self.equipped = []
		
		self.setMode("idle")
		self.task = taskMgr.add(self.update, self.name)
		
	def addCollision(self):
		#self.colSphere = CollisionSphere(0,0,0,0.5)
		self.colSphere = CollisionTube(0,0,0,0,0,1.8,0.8)
		self.colNodepath = CollisionNode(self.name)
		self.colNode = self.model.attachNewNode(self.colNodepath)
		self.colNode.node().addSolid(self.colSphere)
		
	def reparentToNPC(self, npc):
		#print "%s is reparenting itself to parent : %s" % (self.name, npc.name)
		self.model.reparentTo(npc.model)
		self.parentName = npc.name
		self.model.setTexture(self.tex)
		
	def addEquipment(self, modelPath, texPath):
		item = EquippedObject(self, modelPath, texPath)
		self.equipped.append(item)
		
	def loop(self, animName):
		self.model.loop(animName)
		for item in self.equipped:
			item.loop(animName)
		
	def stop(self):
		if self.sequence:
			if self.sequence.isPlaying():
				self.sequence.pause()
				#self.sequence = None
				#print "%s stopped walking" % (self.name)
			#self.model.stop()
		self.setMode("idle")
		
		
	def lookAt(self, x, y):
		#self.model.lookAt(self.model, (-x,-y,0))
		a, b = self.getTilePos()
		self.model.lookAt(a-x+0.5,b-y+0.5,self.model.getZ())
		#print "Looking at %s, %s" % (y, x)
		
	def setPath(self, path):
		if path == []:
			#if self.sequence.isPlaying():
			#	self.sequence.pause()
			self.stop()
			self.resetTimer()
			return
			
		if len(self.path)>1 and len(path)>1:
			if self.path[-1] == path[-1]:
				#print "no need to update path, we're already going there..."
				return
		#print "NPC : set path called"
		
		if self.sequence.isPlaying():
			self.sequence.pause()
			
		self.path = path
		self.sequence = Sequence()
		self.resetTimer()
		# lookAt for first move
		a, b = self.getTilePos()
		x = path[0][0] - a
		y = path[0][1] - b
		self.lookAt(x, y)
		
		f = Func(self.setMode, "walk")
		self.sequence.append(f)
		
		for n, tile in enumerate(path):
			if n<len(path)-1:
				x = path[n+1][0] - tile[0]
				y = path[n+1][1] - tile[1]
				f = Func(self.lookAt, x, y)
				self.sequence.append(f)
				
			i = LerpPosInterval(self.model,
				self.speed,
				(tile[0]+0.5, tile[1]+0.5, tile[2])
				)
			self.sequence.append(i)
			self.timer += self.speed
			#print "adding tile %s, %s to path for %s" % (tile[0], tile[1], self.name)
		#print "On NPC start sequence, timer = %s" % (self.timer)
		f = Func(self.setMode, "idle")
		self.sequence.append(f)
		
		self.sequence.start()
		
	def resetTimer(self, args=[]):
		self.timer = random.random()*15.0
		
	def setMode(self, mode):
		self.mode = mode
		self.loop(mode)
		
	def setTimer(self, n):
		self.timer = float(n)
		
	def update(self, task):
		dt = globalClock.getDt()
		self.timer -= dt
		#print "NPC update : timer = %s" % (self.timer)
		
		#timer = str(round(self.timer, 1))
		#msg = self.name + "\n" + self.mode + " / " + timer
		#self.timerMsg.setText(msg)
		
		'''
		pos = self.model.getPos()
		
		p3 = base.cam.getRelativePoint(render, Point3(pos))
		p2 = Point2()
		
		
		if base.camLens.project(p3, p2):
			r2d = Point3(p2[0], 0, p2[1])
			a2d = aspect2d.getRelativePoint(render2d, r2d) 
			
			msg = self.mode + " / " + str(self.timer)
			
			self.timerMsg.setText(msg)
			self.timerMsg.setPos(a2d[0], a2d[1])
		else:
			self.timerMsg.setText("")
		'''
		return task.cont
	
	def destroy(self):
		if self.sequence:
			self.sequence.pause()
		taskMgr.remove(self.task)
		self.model.cleanup()
		self.model.remove()
		
class EquippedObject(MapObject):
	def __init__(self, npc, modelPath, texturePath=None):
		self.npc = npc
		self.modelPath = modelPath
		self.texturePath = texturePath
		
		self.model = Actor(self.modelPath, self.npc.animDic)
		#self.model.setTransparency(True)
		
		if texturePath is not None:
			self.tex = loader.loadTexture(texturePath)
			#self.model.clearTexture(TextureStage.getDefault())
			self.model.setTexture(self.tex)
			
		self.model.reparentTo(self.npc.model)
		self.model.clearTexture(TextureStage.getDefault())
		self.model.setTexture(self.tex)
	
	def loop(self, animName):
		self.model.loop(animName)
		
	def destroy(self):
		self.model.cleanup()
		self.model.remove()	
