#!/usr/bin/python
# -*- coding: utf8 -*-

from pandac.PandaModules import *

from direct.interval.IntervalGlobal import *
from direct.actor.Actor import Actor
from direct.task import Task

from gui import *

import math, random


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
		
	def addCollision(self):
		self.colSphere = CollisionSphere(0,0,0,0.5)
		#self.colSphere = CollisionTube(0,0,0,0,0,1.8,0.4)
		self.colNodepath = CollisionNode(self.name)
		self.colNode = self.model.attachNewNode(self.colNodepath)
		self.colNode.node().addSolid(self.colSphere)
		
	def loadModel(self, modelPath, texturePath=None):
		if self.model is not None:
			self.model.remove()
		self.modelPath = modelPath
		self.model = loader.loadModel(modelPath)
		if texturePath is not None:
			tex = loader.loadTexture(texturePath)
			self.texturePath = texturePath
			self.model.setTexture(tex)
		
		
	def loadActor(self, modelPath, animDic={}, texturePath=None):
		if self.model is not None:
			self.model.remove()
		
		self.model = Actor(modelPath, animDic)
		
		if texturePath is not None:
			tex = loader.loadTexture(texturePath)
			self.model.setTexture(tex)
		
	def reparentTo(self, np):
		self.model.reparentTo(np)
		
	def setPos(self, *pos):
		self.model.setPos(pos)
		
	def setHpr(self, *hpr):
		self.model.setHpr(hpr)
		
	def setRot(self, n):
		self.model.setH(n)
		
	def setScale(self, *scale):
		self.model.setScale(scale)
		
	def setTilePos(self, x, y):
		self.setPos(x+0.5, y+0.5, 0)
		
	def getTilePos(self):
		return int(self.model.getX()), int(self.model.getY())
		
	def destroy(self):
		if self.task:
			taskMgr.remove(self.task)
		self.model.remove()
		
		

#-----------------------------------------------------------------------
# NPC
#-----------------------------------------------------------------------

class NPC(MapObject):
	def __init__(self, name, modelName, tex):
		self.name = name
		path = "models/characters/" + modelName
		self.model = Actor(path, {
			"walk":"models/characters/male-walk",
			"idle": "models/characters/male-idle"
		})
		texPath = "models/characters/" + tex
		self.tex = loader.loadTexture(texPath)
		self.model.setTexture(self.tex)
		self.model.reparentTo(render)
		
		self.addCollision()
		
		self.speed = 0.4
		
		self.path = []
		self.sequence = Sequence()
		self.setMode("idle")
		
		self.timer = random.random()*5.0
		#self.timerMsg = makeMsg(0,0,"time")
		self.timerMsg = TextNode(self.name)
		self.timerMsg.setFont(FONT)
		#self.timerMsg.setTextColor(1,1,1,1)
		
		
		self.timerMsg.setCardColor(1, 1, 1, 0.8)
		self.timerMsg.setCardAsMargin(0.5, 0.5, 0, 0.5)
		self.timerMsg.setCardDecal(True)
		
		self.timerLabel = render.attachNewNode(self.timerMsg)
		self.timerLabel.reparentTo(self.model)
		self.timerLabel.setPos(1,0,3)
		self.timerLabel.setBillboardAxis()
		self.timerLabel.setLightOff()
		#self.timerLabel.clearTexture(TextureStage.getDefault())
		self.timerLabel.setTexture(loader.loadTexture("img/generic/label.png"))
		#self.timerLabel.setColor(1,1,1,0.2)
		#self.timerLabel.setTransparency(True)
		
		self.data = {}
		self.data["name"] = self.name
		
		self.task = taskMgr.add(self.update, self.name)
		
	def addCollision(self):
		#self.colSphere = CollisionSphere(0,0,0,0.5)
		self.colSphere = CollisionTube(0,0,0,0,0,1.8,0.4)
		self.colNodepath = CollisionNode(self.name)
		self.colNode = self.model.attachNewNode(self.colNodepath)
		self.colNode.node().addSolid(self.colSphere)
		
	def reparentToNPC(self, npc):
		#print "%s is reparenting itself to parent : %s" % (self.name, npc.name)
		self.model.reparentTo(npc.model)
		self.parentName = npc.name
		self.model.setTexture(self.tex)
		
	def loop(self, animName):
		self.model.loop(animName)
		
	def stop(self):
		if self.sequence:
			if self.sequence.isPlaying():
				self.sequence.pause()
				#self.sequence = None
				#print "%s stopped walking" % (self.name)
			#self.model.stop()
		self.setMode("idle")
		
	def setPos(self, *pos):
		self.model.setPos(pos)
		
	def setTilePos(self, x, y):
		self.setPos(x+0.5, y+0.5, 0)
		
	def getTilePos(self):
		return int(self.model.getX()), int(self.model.getY())
		
	def lookAt(self, x, y):
		#self.model.lookAt(self.model, (-x,-y,0))
		a, b = self.getTilePos()
		self.model.lookAt(a-x+0.5,b-y+0.5,self.model.getZ())
		#print "Looking at %s, %s" % (y, x)
		
	def setPath(self, path):
		if path == []:
			if self.sequence.isPlaying():
				self.sequence.pause()
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
		self.timer = random.random()*15.0
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
		
	def setMode(self, mode):
		self.mode = mode
		self.loop(mode)
		
	def setTimer(self, n):
		self.timer = float(n)
		
	def update(self, task):
		dt = globalClock.getDt()
		self.timer -= dt
		#print "NPC update : timer = %s" % (self.timer)
		timer = str(round(self.timer, 1))
		msg = self.name + "\n" + self.mode + " / " + timer
		self.timerMsg.setText(msg)
		
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
		self.model.remove()
		
