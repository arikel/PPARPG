#!/usr/bin/python
# -*- coding: utf8 -*-

import random

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
	def __init__(self, name, genre="generic", imgPath="img/items/empty.png", size=1, stackable=True):
		self.name = name
		self.genre = genre
		self.imgPath = imgPath
		self.stackable = stackable
		self.size = size # room taken by this item in an Inventory

		
'''
class Weapon:
	def __init__(self, name, genre, range, rate, ammo, damage, reloadTime):
		self.name = name
		self.genre = genre
		self.range = range
		self.rate = rate
		self.ammo = ammo
		self.damage = damage
		self.reloadTime = reloadTime
		
		
class Armor:
	def __init__(self, name, genre, protection, fireBonus):
		self.name = name
		self.genre = genre
		self.protection = protection
		self.fireBonus = fireBonus
		
'''

class ItemContainer:
	def __init__(self):
		self.item = None
		self.nb = 0
		
	def setItem(self, item, nb=1):
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
	def __init__(self):
		self.slots = {}
		self.nbSlots = 25
		#for i in range(self.nbSlots):
		#	self.slots[]
			
	def hasRoom(self):
		if len(self.slots)<self.limit:
			return True
		return False

	def addItem(self, item, nb):
		pass
		
class CharacterState:
	def __init__(self, name= None):
		if name is None: self.name = "Red Shirt"
		else: self.name = str(name)
		
	def initHp(self, hp=10, hpMax=10):
		self.hp = hp # health points, when 0 -> death, game over
		self.hpMax = hpMax # stun points, when 0 -> messenger.send("player-faint") etc.
	
	def initSp(self, sp=10, spMax=10):
		self.sp = sp# stun points, when 0 -> messenger.send("player-faint") etc.
		self.spMax = spMax 
		
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

class NPCTracker:
	def __init__(self, mapList = []):
		'''tracks where NPCs are, map and coordinates, the quests values and other data are in GameState'''
		self.mapList = mapList
		
class GameState:
	def __init__(self, filename, playerState):
		self.filename = filename
		self.playerState = playerState
		
	def load(self, filename):
		self.filename = filename
		
	def save(self):
		pass
		
	def saveAs(self, filename):
		pass
		
		
