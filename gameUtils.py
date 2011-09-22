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

class NPCTracker:
	def __init__(self, mapList = []):
		self.mapList = mapList
		
