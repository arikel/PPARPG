#!/usr/bin/python
# -*- coding: utf8 -*-

from direct.showbase.DirectObject import DirectObject


class KeyHandler(DirectObject):
	def __init__(self, keyList):
		self.setKeyList(keyList)
	
	def setKeyList(self, keyList):
		self.keys = {}
		for key in keyList:
			self.accept(key, self.setKey, [key, 1])
			keyup = key + "-up"
			self.accept(keyup, self.setKey, [key, 0])
	
	def getKey(self, key):
		if key in self.keys:
			return self.keys[key]
		return 0
		
	def setKey(self, key, value):
		self.keys[key] = value
