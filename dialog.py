#!/usr/bin/python
# -*- coding: utf8 -*-

from pandac.PandaModules import * 

from direct.task import Task
from direct.interval.IntervalGlobal import *
from direct.fsm.FSM import FSM

import sys, random

#from gui import *
from guiDialog import *

class Dialog:
	def __init__(self, gm, name):
		self.gm = gm # MapManager
		self.playerData = gm.playerData
		print "Initialising script for NPC %s, playerData = %s" % (name, self.playerData)
		self.name = name # the name of the NPC running this dialog with the player
		self.gui = DialogGui(0,-0.5,name)
		self.intro()
		
	def destroy(self, args=[]):
		self.gui.destroy()
		self.gm.dialog = None
		if self.name in self.gm.NPC:
			self.gm.NPC[self.name].resetTimer()
		
	def setMainText(self, text):
		self.gui.setMainText(text)
	
	def setMenu(self, menu):
		self.gui.setMenu(menu)
		
	def getQuestValue(self):
		if self.name not in self.playerData:
			return 0
		else:
			return self.playerData[self.name]
		
	def intro(self):
		msg = "You are talking to " + self.name
		msg = msg + ". Please note that this is a work in progress, and as such it features things spread here and there without much sense or reason, just for the sake of testing them. No real gameplay is available yet. We're sorry about that, join #PPARPG on Freenode if you want to ask anything, make suggestions, or even help...\nThanks for testing anyway."
		
		self.setMainText(msg)
		
		msg1 = "'Hello, " + self.name + "!'"
		msg2 = "'So " + self.name + " is your name, huh?'"
		
		menu = [
			[msg1, self.l_hello, []],
			[msg2, self.l_askName, []],
			["Close", self.destroy, []],
		]
		self.setMenu(menu)
		return 1
		
	def l_hello(self, args=[]):
		msg1 = "Hi there, " + self.playerData["name"] + "..."
		self.setMainText(msg1)
		self.l_close()
		return 1
		
	def l_askName(self, args=[]):
		msg1 = self.name + " looks at you for a moment.\n\n" + self.name + " : 'That's my name, why do you care?'"
		self.setMainText(msg1)
		self.l_close()
		return 1
		
	def l_close(self, args=[]):
		menu = [["Close", self.destroy, []]]
		self.setMenu(menu)
		return 1
		
class DialogCamilla(Dialog):
	def __init__(self, gm, name = "Camilla"):
		Dialog.__init__(self, gm, "Camilla")
		
	def intro(self):
		if self.getQuestValue()>1:
			msg = "Camilla is looking at you suspiciously...\n\nCarmilla : 'What is it you want now, " + self.playerData["name"] + "?'"
		else:
			msg = "Camilla looks kindly at you."
			
		self.setMainText(msg)
		
		msg1 = "'Hello, " + self.name + "!'"
		msg2 = "'Camilla, you seem to know a lot of stuff about what's going on here...'"		
		menu = [
			[msg1, self.l_hello, []],
			[msg2, self.l_askStuff, []],
			["Close", self.destroy, []]
		]
		self.setMenu(menu)
		return 1
		
	def l_hello(self, args=[]):
		if self.getQuestValue()>0:
			msg = "Camilla : '... hello again, " + self.playerData["name"] + "...'"
		else:
			msg = "Camilla : 'Oh hello there, young " + self.playerData["name"] + ".'"
			self.playerData[self.name] = 1
			print "current playerdata : %s" % (self.playerData)
			
		self.setMainText(msg)
		self.l_close()
		return 1
		
	def l_askStuff(self, args=[]):
		if self.getQuestValue()>1:
			msg = "Camilla : 'Enough with that, i have no idea what you're talking\nabout!'"
			self.setMainText(msg)
			self.l_close()
		else:
			msg = "Camilla : 'A lot of stuff? what do you mean by that?'"
			self.playerData[self.name] = 1
			self.setMainText(msg)
			menu = [
				["'Come on, you know *exactly* what i mean...'", self.l_insist, []],
				["'Don't try to lie to me...'", self.l_insist, []],
				["'I knew you'd try to lie to me...'", self.l_insist, []],
				["'You know who you're lying to, girl?'", self.l_insist, []],
				["'Ah, my bad, forget about that...'", self.l_close2, []],
			]
			self.setMenu(menu)
		return 1
		
	def l_insist(self, args=[]):
		msg = "Camilla : 'No, really, i have no idea what you're talking about!'"
		self.playerData[self.name] = 2
		self.setMainText(msg)
		self.l_close();
		return 1
		
	def l_close2(self, args=[]):
		self.setMainText("...")
		menu = [["Close", self.destroy, []]]
		self.setMenu(menu)
		return 1
		
dialogDic = {}
dialogDic["Camilla"] = DialogCamilla
for name in ["Kimmo", "ula2", "Drunkard"]:
	dialogDic[name] = Dialog

