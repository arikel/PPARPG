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
from gameUtils import itemDB

class ItemSlot(DirectButton):
	def __init__(self, name, transp = False):
		self.name = name
		self.size = 0.07
		if transp:imgPath = None
		else:imgPath="img/items/empty.png"
		
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
			image = imgPath,
			image_scale=0.06,
		)
		self.initialiseoptions(ItemSlot)
		self.setBin("fixed", -149)
		self.nb = 0
		self.nbLabel = makeMsgRight(0.05,-0.05,str(self.nb), "white_transp")
		self.nbLabel.setBin("fixed", -148)
		self.nbLabel.reparentTo(self)
		
		self.itemImg = None
		self.clear()
		
	def setItem(self, name, nb=1):
		if nb >= 1:
			if name in itemDB:
				item = itemDB[name]
				self.isEmpty = False
				self.nb = int(nb)
				self.itemName = name
				if nb > 1:
					self.nbLabel.setText(str(self.nb))
					print "Setting item number : %s" % (nb)
					
				else:
					self.nbLabel.setText("")
					print "item number is 1"
				
				if self.itemImg:self.itemImg.destroy()
				self.itemImg = makeImg(0,0,item.imgPath,0.06)
				self.itemImg.reparentTo(self)
			else:
				print "Name %s not found in itemDB, nb was %s" % (name, nb)
		else:
			print "impossible to set %s %s on this slot %s" % (nb, name, self.name)
			self.clear()
				
	def clear(self):
		self.isEmpty = True
		self.itemName = None
		self.nb = 0
		self.nbLabel.setText("")
		if self.itemImg:
			self.itemImg.destroy()
		self.itemImg = None
		
class InventoryGui:
	def __init__(self, mapManager):
		self.mapManager = mapManager
		self.playerState = self.mapManager.playerState
		
		self.frame = DirectFrame(
			frameSize = (-1,1,-0.78,0.78),
			frameColor=(0.1, 0.1, 0.1, 0.95),
			pos = (0, 0, 0),
			pad = (0,0),
			borderWidth=(0.0,0.0),
			relief = DGG.GROOVE,
			sortOrder = -150
		)
		self.frame.setBin("fixed", -150)
		self.size = 0.08
		self.slots = {}
		self.x = 5
		self.y = 6
		self.step = 1.8*self.size# + 0.01
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
				slot = ItemSlot(name)
				slot.setPos(x*self.step+self.startx, -1, -y*self.step+self.starty)
				slot.reparentTo(self.frame)
				slot.parent = self.frame
				self.slots[name] = slot
				#self.slots[name].bind(DGG.B1PRESS, self.onSlotClick, [self.slots[name].name])
		#self.slots[2].setImg("img/items/weapons/rifle.png")
		#self.slots[3].setImg("img/items/weapons/katana.png")
		
		
		self.slots["head"] = ItemSlot("head", True)
		self.slots["head"].setPos(-0.565, 0, 0.55)
		
		self.slots["torso"] = ItemSlot("torso", True)
		self.slots["torso"].setPos(-0.565, 0, 0.2)
		
		self.slots["legs"] = ItemSlot("legs", True)
		self.slots["legs"].setPos(-0.565, 0, -0.2)
		
		self.slots["feet"] = ItemSlot("feet", True)
		self.slots["feet"].setPos(-0.565, 0, -0.6)
		
		
		self.slots["right-hand"] = ItemSlot("right-hand", True)
		self.slots["right-hand"].setPos(-0.815, 0, -0.01)
		
		self.slots["left-hand"] = ItemSlot("left-hand", True)
		self.slots["left-hand"].setPos(-0.315, 0, -0.01)
		
		for key in self.slots:
			self.slots[key].reparentTo(self.frame)
			self.slots[key].bind(DGG.B1PRESS, self.onSlotClick, [self.slots[key].name])
		self.visible = True
		
		self.info = makeMsg(-0.74*RATIO,0.72, "INVENTORY")
		self.info.reparentTo(self.frame)
		
		self.equipImg = makeImg(-0.55,-0.025,"img/generic/PPARPG_model-sheet-Galya2.png", (0.4,1,0.8))
		self.equipImg.reparentTo(self.frame)
		
		
		self.eyeButton = DirectButton(
			frameSize = (-self.size,self.size,-self.size,self.size),
			pos = (-0.25, 1, 0.6),
			pad = (0,0),
			borderWidth=(0.008,0.008),
			frameColor=(0.2,0.2,0.2,0.6),
			relief = DGG.GROOVE,
			rolloverSound = None,
			clickSound = None,
			sortOrder=-100,
			image = "img/items/eye2.png",
			image_scale=0.07,
		)
		self.eyeButton.reparentTo(self.frame)
		
		self.mouthButton = DirectButton(
			frameSize = (-self.size,self.size,-self.size,self.size),
			pos = (-0.85, 1, 0.6),
			pad = (0,0),
			borderWidth=(0.008,0.008),
			frameColor=(0.2,0.2,0.2,0.6),
			relief = DGG.GROOVE,
			rolloverSound = None,
			clickSound = None,
			sortOrder=-100,
			image = "img/items/mouth2.png",
			image_scale=0.07,
		)
		self.mouthButton.reparentTo(self.frame)
		
		x = 0.15
		y = -0.2
		step = 0.06
		
		
		
		self.heatBar = Barre(0.12,0.01,x,y,30, color1 = (0.4, 0.25, 0.2, 1.0), color2 = (0.85, 0.65, 0.25, 0.9), text = "Heat")
		self.heatBar.reparentTo(self.frame)
		
		self.foodBar = Barre(0.12,0.01,x,y-step,30, color1 = (0.2, 0.1, 0.05, 1.0), color2 = (0.45, 0.15, 0.0, 0.9), text = "Food")
		self.foodBar.reparentTo(self.frame)
		
		self.waterBar = Barre(0.12,0.01,x,y-2*step,30, color1 = (0.1, 0.25, 0.4, 1.0), color2 = (0.30, 0.45, 0.85, 0.9), text = "Water")
		self.waterBar.reparentTo(self.frame)
		
		self.heatBar.setHp(27)
		self.foodBar.setHp(12)
		self.waterBar.setHp(20)
		
		self.slots["slot_1"].setItem("katana", 1)
		self.slots["slot_2"].setItem("shotgunShells", 25)
		
		self.hide()
		
	def onSlotClick(self, slotName, extraArgs=[]):
		#print "InventoryGui : slot %s has been clicked on." % (slotName)
		#item = self.slots[slotName]
		if self.slots[slotName].isEmpty:
			print "Slot %s clicked (empty)" % (slotName)
			if self.mapManager.cursor.item is not None:
				print "cursor puts %s * %s on empty slot" % (self.mapManager.cursor.item, self.mapManager.cursor.itemNb)
				#self.slots[slotName].setItem(self.mapManager.cursor.item, self.mapManager.cursor.itemNb)
				#self.mapManager.cursor.clear()
				self.onPutItem(slotName)
		else:
			print "Slot %s containing %s %s clicked." % (slotName, self.slots[slotName].nb, self.slots[slotName].itemName)
			if self.mapManager.cursor.item is None:
				print "Picking item from inventory"
				#self.mapManager.cursor.setItem(self.slots[slotName].itemName, self.slots[slotName].nb)
				#self.slots[slotName].clear()
				self.onPickItem(slotName)
			else:
				print "Switching items"
				self.onSwitchItem(slotName)
				#item1 = self.slots[slotName].itemName
				#nb1 = self.slots[slotName].nb
				#item2 = self.mapManager.cursor.item
				#nb2 = self.mapManager.cursor.itemNb
				
				#self.mapManager.cursor.setItem(item1, nb1)
				#self.slots[slotName].setItem(item2, nb2)
				
	def onPickItem(self, slotName):
		self.mapManager.cursor.setItem(self.slots[slotName].itemName, self.slots[slotName].nb)
		self.slots[slotName].clear()
	
	def onSwitchItem(self, slotName):
		item1 = self.slots[slotName].itemName
		nb1 = self.slots[slotName].nb
		item2 = self.mapManager.cursor.item
		nb2 = self.mapManager.cursor.itemNb
		
		self.mapManager.cursor.setItem(item1, nb1)
		self.slots[slotName].setItem(item2, nb2)
		
	def onPutItem(self, slotName):
		itemName = self.mapManager.cursor.item
		itemNb = self.mapManager.cursor.itemNb
		
		for equipName in ["torso", "head", "legs", "feet"]:
			if slotName == equipName and itemDB[itemName].equip != equipName:
				print "item %s won't fit on slot %s" % (itemName, slotName)
				return
		
		self.slots[slotName].setItem(self.mapManager.cursor.item, self.mapManager.cursor.itemNb)
		self.mapManager.cursor.clearItem()
		self.mapManager.cursor.clearInfo()
		
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
	
	def toggle(self, extraArgs=[]):
		if self.visible:
			self.hide()
		else:
			self.show()
	'''	
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
	'''
	
class GameGui:
	def __init__(self, mapManager):
		self.mapManager = mapManager
		self.playerState = self.mapManager.playerState
		
		self.infoLabel = makeMsg(-0.95*RATIO,0.95,"")
		self.objectLabel = makeMsg(-0.95*RATIO,-0.85,"")
		self.inventory = InventoryGui(self.mapManager)
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
		
		self.size = 0.09
		self.invButton = DirectButton(
			frameSize = (-self.size,self.size,-self.size,self.size),
			pos = (0.92*RATIO, 1, -0.9),
			pad = (0,0),
			borderWidth=(0.008,0.008),
			frameColor=(0.0,0.0,0.0,0.0),
			relief = DGG.GROOVE,
			rolloverSound = None,
			clickSound = None,
			sortOrder=-100,
			#image = "img/items/backpack6.png",
			#image_scale=0.08,
		)
		self.bagImg = makeImg(0.95*RATIO, -0.92, "img/items/bag.png", 0.08)
		self.invButton.bind(DGG.B1PRESS, self.inventory.toggle)
		
		self.hpBar = Barre(0.12,0.01,-0.95,-0.85,30, color1 = (0.1, 0.4, 0.25, 1.0), color2 = (0.30, 0.85, 0.45, 0.9), text = "HP")
		self.spBar = Barre(0.12,0.01,-0.95,-0.90,30, color1 = (0.1, 0.25, 0.4, 1.0), color2 = (0.30, 0.45, 0.85, 0.9), text = "SP")
		self.spBar.setHp(20)
		
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
		self.invButton.hide()
		self.bagImg.hide()
		
		self.hpBar.hide()
		
		self.visible = False
		
	def show(self):
		self.infoLabel.show()
		self.objectLabel.show()
		self.invButton.show()
		self.bagImg.show()
		#self.inventory.show()
		#self.objectMenu.show()
		
		self.hpBar.show()
		
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
