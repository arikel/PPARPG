#!/usr/bin/python
# -*- coding: utf8 -*-

from direct.fsm.FSM import FSM

import random
import cPickle as pickle
from time import localtime, gmtime, strftime



from pathFind import *

def jette(n=1,d=6,b=0):
	resList = []
	for i in range(n):
			a = random.randint(1,d)
			resList.append(a)
	res = 0
	for dice in resList:
			res += dice
	res += b
	print "throw : %s dice of %s faces : %s , + %s , total = %s" % (n, d, resList, b, res)
	return res

class Item:
	def __init__(self, name):
		self.name = name
		self.descName = name
		self.genre = "generic"
		self.imgPath = "img/items/default.png"
		self.stackable = True
		self.size = 1 # room taken by this item in an Inventory
		self.equip = None # "torso"...
		
def makeItemGeneric(name, imgPath, size = 1):
	item = Item(name)
	item.imgPath = imgPath
	item.size = size
	return item
	
def makeItemEquip(name, imgPath, size = 1,equip="head"):
	item = makeItemGeneric(name, imgPath, size)
	item.equip = equip
	item.genre = "equip"
	item.stackable = False
	return item
	
itemDB = {}
itemDB["stick"] = makeItemEquip("stick", "img/items/weapons/stick.png", 1, "hand")
itemDB["katana"] = makeItemEquip("katana", "img/items/weapons/katana.png", 1, "hand")
itemDB["shotgunShells"] = makeItemGeneric("shotgunShells", "img/items/weapons/shotgunShells.png", 1)

class CreatureState:
	def __init__(self, name):
		self.name = name
		self.stat = {}
		self.statMax = {}
		for stat in ["healthPoints", "stunPoints", "foodPoints", "waterPoints", "heatPoints"]:
			self.initStat(stat, 10)
		
	def initStat(self, stat, nb):
		self.stat[stat] = nb
		self.statMax[stat] = nb
	
	def checkStat(self, stat):
		self.stat[stat] = max(0, min(self.statMax[stat], self.stat[stat]))
	
	def addToStat(self, stat, n):
		self.stat[stat] += n
		self.checkStat(stat)
		
	def remFromStat(self, stat, n):
		self.addToStat(stat, -n)

	def initCarac(self):
		self.carac = {}
		self.carac["STR"] = 1 # strength
		self.carac["DEX"] = 1 # dexterity
		self.carac["END"] = 1 # endurance / constitution
		self.carac["WIL"] = 1 # willpower
		self.carac["PER"] = 1 # perception
		self.carac["TEC"] = 1 # technology
		#self.carac[""] = 1
		#self.carac[""] = 1
	
	def initSkill(self):
		self.skill = {}
		
	def setMap(self, filename):
		self.map = filename
		
	def setPos(self, pos):
		self.pos = pos
		
class CharacterState(CreatureState):
	def __init__(self, name= None):
		if name is None: name = "Red Shirt"
		else: name = str(name)
		CreatureState.__init__(self, name)
		
	def initSex(self, sex):# yeah, yeah :p
		self.sex = sex
		
	def initInventory(self):
		self.inventory = Inventory()
	
	def onDie(self):
		messenger.send("NPCDied", [self.name])
		
	
		
class PlayerState(CharacterState):
	def __init__(self, name=None):
		CharacterState.__init__(self, name)
		self.questDic = {} # NPCname : {quest1 : value1, quest2, value2...}
		
	def onDie(self):
		messenger.send("playerDied")
		#print "oops, player died :("
	
	def setQuest(self, questName, questKey="main", questVal=0):
		if questName not in self.questDic:
			self.questDic[questName] = {}
		self.questDic[questName][questKey] = questVal
		print "playerState setQuest : %s : %s at %s" % (questName, questKey, questVal)
		
def makePlayerState(name="Galya", sex="female", hp=10, sp=10):
	p = PlayerState(name)
	p.initSex(sex)
	p.setMap("maps/interior2.txt")
	return p



class NPCTracker:
	def __init__(self, mapList = []):
		'''tracks where NPCs are, map and coordinates, the quests values and other data are in GameState'''
		self.mapList = mapList
		
class GameState:
	def __init__(self, filename="save/default.txt", playerState=makePlayerState()):
		self.filename = filename
		self.playerState = playerState
		self.NPCTracker = NPCTracker()
		
		
	def load(self, filename):
		self.filename = filename
		f = open(filename, 'r')
		data = pickle.load(f)
		f.close()
		self.playerState = data["playerState"]
		self.NPCTracker = data["NPCTracker"]
		
		if "time" in data and "timeDisplay" in data:
			pass
		else:
			data["timeDisplay"] = strftime("%a, %d %b %Y %H:%M:%S +0000", localtime())
			data["time"] = localtime()
		self.time = [data["time"], data["timeDisplay"]]
		
		print "game loaded, data was %s" % data
		
	def save(self):
		self.saveAs(self.filename)
		
	def saveAs(self, filename):
		f = open(filename, 'w')
		pickle.dump(self.getSaveData(), f)
		f.close()
		print "game state data saved as %s" % (filename)
		self.filename = filename
		
	def getSaveData(self):
		data = {}
		data["playerState"] = self.playerState
		data["NPCTracker"] = self.NPCTracker
		data["timeDisplay"] = strftime("%a, %d %b %Y %H:%M:%S +0000", localtime())
		data["time"] = localtime()
		#data["questDic"] = self.questDic
		return data
		
	def __repr__(self):
		msg = ""
		msg = msg + "Player name : " + self.playerState.name + "\n"
		msg = msg + "stats : " + str(self.playerState.stat)
		return msg
		
class CreatureAI(FSM):
	def __init__(self, gm, name = "CreatureAI"):
		FSM.__init__(self, name)
		self.gm = gm # MapManager
		self.name = name
		self.timer = 0.0
		
	def start(self):
		self.task = taskMgr.add(self.update, self.name)
		
	def update(self, task):
		dt = globalClock.getDt()
		self.timer -= dt
		#print "%s timer is at %s" % (self.name, self.timer)
		return task.cont
		
	def stop(self):
		taskMgr.remove(self.task)
		
	def goto(self, x, y):
		#print "AI sent a goto instruction for %s : %s / %s" % (self.name, x, y)
		start = (self.mapChar.getTilePos())
		end = (x, y)
		data = self.gm.map.collisionGrid.data
		path = astar(start, end, data)
		if path is []:
			return False
		newPath = []
		for tile in path:
			#newPath.append((tile[0], tile[1], 0))
			newPath.append((tile[0], tile[1], self.gm.map.collisionGrid.getTileHeight(tile[0], tile[1])))
		delay = self.mapChar.setPath(newPath)
		if delay is not None:
			self.timer += delay + random.random()*10.0 + 5.0
		
class NPCAI(CreatureAI):
	def __init__(self, gm, name = "NPCAI"):
		CreatureAI.__init__(self, gm, name)
		self.mapChar = self.gm.NPC[name]
		self.request("Wander")
		
	def resetTimer(self):
		self.timer = random.random() * 10.0 + 5.0
		
		
	def enterWander(self):
		self.task = taskMgr.add(self.updateWander, self.name)
		
	def exitWander(self):
		self.stop()
		
	def update(self, task):
		dt = globalClock.getDt()
		self.timer -= dt
		#print "NPC '%s' timer is at %s" % (self.name, self.timer)
		return task.cont
	
	def updateWander(self, task):
		dt = globalClock.getDt()
		self.timer -= dt
		if self.timer <= 0:
			if self.mapChar.mode == "idle":
				if self.gm.dialog:
					if self.gm.dialog.name != self.name:
						#print "Sending NPC to random pos"
						tile = self.gm.map.collisionGrid.getRandomTile()
						if tile is not None:
							self.goto(tile[0], tile[1])
						#else:
						#	self.mapChar.resetTimer()
				else:
					tile = self.gm.map.collisionGrid.getRandomTile()
					if tile is not None:
						self.goto(tile[0], tile[1])
		return task.cont
