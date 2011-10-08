#!/usr/bin/python
# -*- coding: utf8 -*-

from pandac.PandaModules import *
import direct.directbase.DirectStart
from direct.gui.DirectGui import *
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.interval.IntervalGlobal import *

from guiBase import *
from guiMenu import ActionMenu
from guiDialog import DialogGui

class ItemSlot(DirectButton):
	def __init__(self):
		self.clear()
		self.size = 0.09
		DirectButton.__init__(self,
			frameSize = (-self.size,self.size,-self.size,self.size),
			pos = (0, 1, 0),
			pad = (0,0),
			borderWidth=(0.008,0.008),
			frameColor=(0.2,0.2,0.2,0.6),
			relief = DGG.GROOVE,
			rolloverSound = None,
			clickSound = None,
			sortOrder=-100,
			image = "img/items/empty.png",
			image_scale=0.08,
		)
		self.initialiseoptions(ItemSlot)
		
	def setItem(self, name, nb=1):
		if nb >= 1:
			self.isEmpty = False
			self.itemName = name
			self.itemNb = int(nb)
	def clear(self):
		self.isEmpty = True
		self.itemName = None
	
	
class InventoryGui:
	def __init__(self):
		self.frame = DirectFrame(
			frameSize = (-1,1,-0.78,0.78),
			frameColor=(0.1, 0.1, 0.1, 0.8),
			pos = (0, 0, 0),
			pad = (0,0),
			borderWidth=(0.0,0.0),
			relief = DGG.GROOVE,
			sortOrder = -150
		)
		self.frame.setBin("fixed", -150)
		self.size = 0.08
		self.slots = []
		self.x = 5
		self.y = 8
		self.step = 2*self.size + 0.01
		#self.startx = -0.91
		self.startx = 0.15
		self.starty = 0.65
		
		self.w = (self.x-1)*self.step + 2*self.size
		self.h = (self.y-1)*self.step + 2*self.size
		
		i = 0
		for y in range(self.y):
			for x in range(self.x):
				name = "slot_" + str(i)
				i += 1
				slot = ItemSlot()
				slot.setPos(x*self.step+self.startx, -1, -y*self.step+self.starty)
				slot.reparentTo(self.frame)
				slot.parent = self.frame
				self.slots.append(slot)
				
		#self.slots[2].setImg("img/items/weapons/rifle.png")
		#self.slots[3].setImg("img/items/weapons/katana.png")
		
		self.visible = True
		
		self.info = makeMsg(-0.8,0.8, "Inventory info")
		self.info.reparentTo(self.frame)
		
		self.equipImg = makeImg(-0.55,-0.025,"img/generic/PPARPG_model-sheet-Galya2.png", (0.4,1,0.8))
		self.equipImg.reparentTo(self.frame)
		
		self.hide()
		
	def setInfo(self, msg):
		self.info.setText(str(msg))
		
	def destroy(self):
		self.frame.destroy()
	
	def show(self):
		self.frame.show()
		self.visible = True
		
	def hide(self):
		self.frame.hide()
		self.visible = False
	
	def toggle(self):
		if self.visible:
			self.hide()
		else:
			self.show()
		
	def getMouseSlot(self):
		if base.mouseWatcherNode.hasMouse():
			mpos = base.mouseWatcherNode.getMouse()
			mX = mpos.getX()*RATIO
			mY = mpos.getY()
			if mX < self.startx-self.size:
				return None # x too small
			elif mX> self.startx -self.size + self.w:
				return None # x too big
			else:
				x = int((mX-self.startx+self.size) * self.x / self.w)
				
			if mY > self.starty+self.size:
				return None # y too high
			elif mY< self.starty+self.size - self.h:
				return None # y too low
			else:
				y = -int((mY-self.starty-self.size) * self.y / self.h)
				
			return x, y
		return None
		
class GameGui:
	def __init__(self, mapManager):
		self.mapManager = mapManager
		self.infoLabel = makeMsg(-0.95*RATIO,0.95,"")
		self.objectLabel = makeMsg(-0.95*RATIO,-0.85,"")
		self.inventory = InventoryGui()
		i = 0
		
		#for slot in self.inventory.slots:
		#	slot.bind(DGG.B1PRESS, self.onSelectItem, [i])
		#	i += 1
			
		#self.pickedItem = InventorySlot(0,0,"pickedItem",0.1)
		#self.pickedItem.hide()
		#self.pickedItem.setBin("gui-popup", 50)
		
		self.objectMenu = ActionMenu(0,0)
		self.objectMenu.rebuild(["look", "talk", "attack"])
		
		self.dialogGui = None
		
	def openDialog(self, name):
		self.dialogGui = DialogGui(name)
		
	def closeDialog(self):
		self.dialogGui.destroy()
		self.dialogGui = None
		
		
	def startFollowMouse(self, extraArgs=[]):
		#self.pickedItem["sortOrder"] = 101
		#self.pickedItem.show()
		print "starting follow, slot %s has sortOrder %s" % (self.pickedItem.name, self.pickedItem["sortOrder"])
		self.task = taskMgr.add(self.followTask, "follow")
		
	def followTask(self, task):
		if base.mouseWatcherNode.hasMouse():
			mpos = base.mouseWatcherNode.getMouse()
			#self.pickedItem.setPos(mpos.getX()*RATIO, 1, mpos.getY())
			
			m = self.inventory.getMouseSlot()
			if m is not None:
				x, y = m
				#msg = "Mouse slot : " + str(round(x, 2)) + ", " + str(round(y, 2))
				msg = "Mouse slot : " + str(x) + ", " + str(y)
				self.setInfo(msg)
			else:
				self.setInfo("")
				
		return task.cont
		
	def stopFollowMouse(self, extraArgs=[]):
		
		taskMgr.remove(self.task)
		#self.pickedItem["sortOrder"] = 100
		#self.pickedItem.setBin("fixed", 100)
		#self.pickedItem.hide()
		print "stopped follow, slot %s has sortOrder %s" % (self.pickedItem.name, self.pickedItem["sortOrder"])
		
	def hide(self):
		self.infoLabel.hide()
		self.objectLabel.hide()
		self.inventory.hide()
		self.objectMenu.hide()
		self.visible = False
		
	def show(self):
		self.infoLabel.show()
		self.objectLabel.show()
		#self.inventory.show()
		#self.objectMenu.show()
		self.visible = True
		
	def setInfo(self, info):
		self.infoLabel.setText(str(info))
		
	def clearInfo(self):
		self.infoLabel.setText("")
		
	def setObjInfo(self, mpos, info):
		self.objectLabel.setPos(mpos.getX()*RATIO+0.1, mpos.getY()+0.02)
		self.objectLabel.setText(str(info))
		
	def clearObjInfo(self):
		self.objectLabel.setText("")
	
	def closeMenu(self):
		self.objectMenu.retract()

if __name__=="__main__":
	g = GameGui(None)
	g.inventory.show()
	import sys
	base.accept("escape", sys.exit)
	run()
