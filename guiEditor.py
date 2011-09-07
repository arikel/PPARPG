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

class EditorGui:
	def __init__(self, editor):
		self.editor = editor
		
		self.topMenu = TopMenu(-0.7*RATIO, 0.9, 0.2,0.04, ["File", "New", "Open...", "Save", "Save as..."])
		mapList = os.listdir("maps")
		self.topMenu.menu.addSubMenu(1, mapList)
		for i, map in enumerate(mapList):
			path = "maps/" + map
			self.topMenu.menu.subMenus[0].buttons[i].bind(DGG.B1PRESS, self.editor.load, [path])
		
		self.objectMenu = ActionMenu(-0.7*RATIO, 0.9, 0.16,0.035, ["Object", "Grab", "Rotate", "MoveZ", "Scale","Duplicate", "Destroy"])
		
		print "creating EditorGui with object menu %s" % (self.objectMenu)
		
		self.infoLabel = makeMsgRight(0.95*RATIO,-0.95,"")
		self.objectLabel = makeMsg(-0.95*RATIO,-0.85,"")
		
		self.hide()
		
	def hide(self):
		self.topMenu.hide()
		self.objectMenu.hide()
		self.infoLabel.hide()
		self.objectLabel.hide()
		self.visible = False
		
	def show(self):
		self.topMenu.show()
		#self.objectMenu.show()
		self.infoLabel.show()
		self.objectLabel.show()
		self.visible = True
		
	def openObjectMenu(self, obj, mpos):
		"""obj is a MapObject"""
		self.objectMenu.show()
		pos = (mpos[0] + self.objectMenu.w, mpos[1])
		self.objectMenu.setPos(pos)
		
	def toggleVisible(self):
		if self.visible:
			self.hide()
		else:
			self.show()
	
	def setInfo(self, info):
		self.infoLabel.setText(str(info))
		
	def setObjInfo(self, mpos, info):
		self.objectLabel.setPos(mpos.getX()*1.33+0.1, mpos.getY()+0.02)
		self.objectLabel.setText(str(info))
		
	def clearObjInfo(self):
		self.objectLabel.setText("")
