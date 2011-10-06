#!/usr/bin/python
# -*- coding: utf8 -*-

from pandac.PandaModules import *
import direct.directbase.DirectStart
from direct.gui.DirectGui import *
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.interval.IntervalGlobal import *

from guiBase import *
from guiMenu import *

class InventorySlot(DirectButton):
	def __init__(self, x, y, name, size=0.1):
		self.name = name
		self.x = x
		self.y = y
		self.size = size
		
		DirectButton.__init__(self,
			frameSize = (-self.size,self.size,-self.size,self.size),
			pos = (x, 1, y),
			pad = (0,0),
			borderWidth=(0.008,0.008),
			frameColor=(0.2,0.2,0.2,0.6),
			relief = DGG.GROOVE,
			rolloverSound = None,#soundDic["rollover"],
			clickSound = None,#soundDic["select_confirm"],
			sortOrder=-100
		)
		self.initialiseoptions(InventorySlot)
		#print "at init, slot %s has sortOrder %s" % (self.name, self["sortOrder"])
		#self.bind(DGG.ENTER, command=self.onHover, extraArgs=[self])
		#self.bind(DGG.EXIT, command=self.onOut, extraArgs=[self])
		
		
		self.bgImg = makeImg(0,0,"img/items/empty.png", self.size)
		self.bgImg.reparentTo(self)
		
		self.imgPath = None
		self.img = None
		self.following = False
		self.parent = None
		
	def setImg(self, imgPath):
		self.setEmpty()
		self.imgPath = imgPath
		self.img = makeImg(0,0,imgPath, self.size*0.9)
		self.img.reparentTo(self)
		
	def setEmpty(self):
		if self.img:
			self.img.destroy()
			self.img = None
			self.imgPath = None
	
	def onHover(self, extraArgs, sentArgs):
		pass
		
	def onOut(self, extraArgs, sentArgs):
		pass
		

	
	
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
		self.startx = -0.91
		self.starty = 0.69
		
		self.w = (self.x-1)*self.step + 2*self.size
		self.h = (self.y-1)*self.step + 2*self.size
		
		i = 0
		for y in range(self.y):
			for x in range(self.x):
				name = "slot_" + str(i)
				i += 1
				slot = InventorySlot(x*self.step+self.startx, -y*self.step+self.starty, name, size=self.size)
				slot.reparentTo(self.frame)
				slot.parent = self.frame
				self.slots.append(slot)
				
		self.slots[2].setImg("img/items/weapons/rifle.png")
		self.slots[3].setImg("img/items/weapons/katana.png")
		self.visible = True
		
		self.info = makeMsg(-0.8,0.8, "Inventory info")
		self.info.reparentTo(self.frame)
		
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
		self.infoLabel = makeMsgRight(0.95*RATIO,-0.95,"")
		self.objectLabel = makeMsg(-0.95*RATIO,-0.85,"")
		self.inventory = InventoryGui()
		i = 0
		for slot in self.inventory.slots:
			slot.bind(DGG.B1PRESS, self.onSelectItem, [i])
			i += 1
		self.pickedItem = InventorySlot(0,0,"pickedItem",0.1)
		self.pickedItem.hide()
		self.pickedItem.setBin("gui-popup", 50)
		
		self.objectMenu = ActionMenu(0,0)
		self.objectMenu.rebuild(["look", "talk", "attack"])
		
	def onSelectItem(self, i, extraArgs=[]):
		print "selected slot number %s, extraArgs = %s" % (i, extraArgs)
		self.inventory.getMouseSlot()
		if self.inventory.slots[i].imgPath:
			self.pickedItem.setImg(self.inventory.slots[i].imgPath)
		self.startFollowMouse()
		self.pickedItem.bind(DGG.B1PRESS, self.stopFollowMouse)
		
	def startFollowMouse(self, extraArgs=[]):
		self.pickedItem["sortOrder"] = 101
		self.pickedItem.show()
		#print "starting follow, slot %s has sortOrder %s" % (self.name, self["sortOrder"])
		self.task = taskMgr.add(self.followTask, "follow")
		
	def followTask(self, task):
		if base.mouseWatcherNode.hasMouse():
			mpos = base.mouseWatcherNode.getMouse()
			self.pickedItem.setPos(mpos.getX()*RATIO, 1, mpos.getY())
			
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
		self.pickedItem["sortOrder"] = 100
		self.pickedItem.setBin("fixed", 100)
		self.pickedItem.hide()
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
		self.objectMenu.show()
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
