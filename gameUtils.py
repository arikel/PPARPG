#!/usr/bin/python
# -*- coding: utf8 -*-

from direct.fsm.FSM import FSM

import random
import cPickle as pickle

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

class ItemContainer:
	def __init__(self, genre = "generic"):
		self.item = None
		self.nb = 0
		
	def setItem(self, item, nb=1):
		#if item
		self.item = item
		self.nb = int(nb)
		
	def addItem(self, item, nb=1):
		if self.item == item and item.stackable:
			self.nb += nb
		elif self.item is None:
			self.item = item
			self.nb = int(nb)
		else:
			print("Error : can't stack %s with %s" % (item.name, self.item.name))
		
class Inventory:
	def __init__(self, slots = 25, room = 50.0):
		self.slots = {}
		self.nbSlots = slots
		for i in range(self.nbSlots):
			self.slots[i] = None
		self.room = room
		
		self.equipSlots = {}
		for key in ["head", "torso", "legs", "feet", "left-hand", "right-hand"]:
			self.equipSlots[key] = None
		
	def hasRoom(self):
		if len(self.slots)<self.nbSlots:
			return True
		return False
	
	def addItem(self, item, nb):
		pass
		
		
class CreatureState:
	def __init__(self, name):
		self.name = name
		
	def initHp(self, hp=10, hpMax=10):
		self.hp = hp # health points, when 0 -> death, game over
		self.hpMax = hpMax # stun points, when 0 -> messenger.send("player-faint") etc.
	
	def initSp(self, sp=10, spMax=10):
		self.sp = sp# stun points, when 0 -> messenger.send("player-faint") etc.
		self.spMax = spMax 
		
	def checkHp(self):
		self.hp = max(0, min(self.maxHp, self.hp))
	
	def addHp(self, n):
		self.hp += n
		self.checkHp()
		
	def remHp(self, n):
		self.addHp(-n)
	
	def checkSp(self):
		self.sp = max(0, min(self.maxSp, self.sp))	
		
	def addSp(self, n):
		self.sp += n
		self.checkSp()
		
	def remSp(self, n):
		self.addSp(-n)
		
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
		
		
		
class CharacterState(CreatureState):
	def __init__(self, name= None):
		if name is None: self.name = "Red Shirt"
		else: self.name = str(name)
		
	def initSex(self, sex):# yeah, yeah :p
		self.sex = sex
		
	def initInventory(self):
		self.inventory = Inventory()
	
	def onDie(self):
		messenger.send("NPCDied", [self.name])
		
		
class PlayerState(CharacterState):
	def __init__(self, name=None):
		#CharacterState.__init__(self, name)
		if name is None: self.name = "Galya"
		else: self.name = str(name)
		
	def onDie(self):
		messenger.send("playerDied")
		#print "oops, player died :("
	
	def setMap(self, filename):
		self.map = filename	
		
def makePlayerState(name="Galya", sex="female", hp=10, sp=10):
	p = PlayerState(name)
	p.initSex(sex)
	p.initHp(hp)
	p.initSp(sp)
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
		self.questDic = {}
		
	def load(self, filename):
		self.filename = filename
		f = open(filename, 'r')
		data = pickle.load(f)
		f.close()
		self.playerState = data["playerState"]
		self.NPCTracker = data["NPCTracker"]
		self.questDic = data["questDic"]
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
		data["questDic"] = self.questDic
		return data

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
			self.timer += delay + random.random()*10.0
		
class NPCAI(CreatureAI):
	def __init__(self, gm, name = "NPCAI"):
		CreatureAI.__init__(self, gm, name)
		self.mapChar = self.gm.NPC[name]
		self.request("Wander")
		
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
						else:
							self.mapChar.resetTimer()
				else:
					tile = self.gm.map.collisionGrid.getRandomTile()
					if tile is not None:
						self.goto(tile[0], tile[1])
		return task.cont
