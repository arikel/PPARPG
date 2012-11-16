#!/usr/bin/python
# -*- coding: utf8 -*-

from panda3d.core import *
from direct.interval.IntervalGlobal import *
from direct.showbase.PythonUtil import fitDestAngle2Src 
from direct.task import Task
from direct.fsm.FSM import FSM

class CamHandler(FSM):
	def __init__(self, game):
		FSM.__init__(self, "camera")
		
		self.game = game
		self.game.disableMouse()
		
		self.speed = 15.0
		self.intervalSpeed = 2.0
		self.playerNp = self.game.player.np
		self.playerNp.setTransparency(TransparencyAttrib.MAlpha)
		
		self.gameNp = NodePath("gameCam")
		self.gameNp.setPos(0,0,0)
		self.gameNp.reparentTo(self.game.render)
		
		self.gameNp2 = NodePath("gameCam2")
		self.gameNp2.setPos(0,-20,0)
		self.gameNp2.reparentTo(self.gameNp)
		
		self.zoomMin = 0.0
		self.zoomMax = 30.0
		self.pMin = -89.999
		self.pMax = 89.999
		self.baseDx=0.0
		self.baseDy=0.0
		
		self.dragging = False
		self.ratio = self.game.getAspectRatio()
		
		self.mode = "3rd" # 3rd person view
		self.mouse_y_inverted = False
		self.mouse_x_inverted = False
		self.sensivity = 1.0
		
		#self.start_3rd()
		self.request("ViewRPG")
		
	def enterViewRPG(self):
		self.zoom = self.zoom_3rd
		self.update = self.update_3rd
		self.rotate = self.rotate_3rd
		self.startDrag = self.startDrag_3rd
		self.stopDrag = self.stopDrag_3rd
		
		self.game.camera.wrtReparentTo(self.gameNp2)
		LerpPosHprInterval(self.game.camera, self.intervalSpeed, (0,0,0), hpr=(0,0,0), blendType="easeInOut").start()
		
	def exitViewRPG(self):
		pass
		
	def zoom_3rd(self, dist=1.0):
		d = self.gameNp2.getY()
		self.gameNp2.setPos(0, d+dist, 0)
		if d < - self.zoomMax:
			self.gameNp2.setY(-self.zoomMax)
		elif self.gameNp2.getY() > - self.zoomMin:
			self.gameNp2.setY(-self.zoomMin)
		
		d = self.gameNp2.getY()
		if d > -10:
			self.playerNp.setColor(1,1,1,d/(-10.0))
		else:
			self.playerNp.setColor(1,1,1,1)
			
			
	def rotate_3rd(self):
		if self.game.mouseWatcherNode.hasMouse():
			x, y = self.game.mouseWatcherNode.getMouse()
			dx = self.baseDx - x
			dy = self.baseDy - y
			#self.gameNp.setH(self.gameNp, dx*100.0)
			self.gameNp.setH(self.gameNp.getH() + dx*100.0)
			self.gameNp.setP(self.gameNp.getP() - dy*100.0)
			#self.gameNp.setR(0)
			if self.gameNp.getP() < self.pMin:
				self.gameNp.setP(self.pMin)
			elif self.gameNp.getP() > self.pMax:
				self.gameNp.setP(self.pMax)
			if dx != 0 or dy != 0:
				self.baseDx = x
				self.baseDy = y
				#print "new pos : %s %s" % (self.baseDx, self.baseDy)
			
	
	def start_3rd(self):
		self.game.camera.wrtReparentTo(self.gameNp2)
		LerpPosHprInterval(self.game.camera, self.intervalSpeed, (0,0,0), hpr=(0,0,0), blendType="easeInOut").start()
		
	def startDrag_3rd(self):
		if self.game.mouseWatcherNode.hasMouse():
			mpos = self.game.mouseWatcherNode.getMouse()
			self.baseDx = mpos.getX()
			self.baseDy = mpos.getY()
			self.dragging = True
		
	def stopDrag_3rd(self):
		self.dragging = False
		
	def update_3rd(self):
		self.gameNp.setPos(self.playerNp, (0,0,1))
		self.gameNp.setH(self.playerNp, 0)
		
		if self.dragging:
			self.rotate()
	
	
