#!/usr/bin/python
# -*- coding: utf8 -*-

from pandac.PandaModules import * 
from direct.interval.IntervalGlobal import *
from direct.showbase.PythonUtil import fitDestAngle2Src 
from direct.task import Task
import direct.directbase.DirectStart

class EditorCamHandler:
	def __init__(self):
		self.speed = 15.0
		self.intervalSpeed = 0.8
		
		
		self.editNp = NodePath("Editorcam")
		self.editNp.setPos(10,10,60)
		self.editNp.reparentTo(render)
		
		self.editNp2 = NodePath("Editorcam")
		self.editNp2.setPos(0,0,0)
		self.editNp2.setHpr(0,-90,0)
		self.editNp2.reparentTo(self.editNp)
		
	def forward(self, dt):
		self.editNp.setPos(self.editNp, (0,dt*self.speed, 0))
	def backward(self, dt):
		self.editNp.setPos(self.editNp, (0,-dt*self.speed, 0))
		
	def strafeLeft(self, dt):
		self.editNp.setPos(self.editNp, (-dt*self.speed,0, 0))
			
	def strafeRight(self, dt):
		self.editNp.setPos(self.editNp, (dt*self.speed,0, 0))
			
	def turnLeft(self, dt):
		self.editNp.setH(self.editNp, dt*self.speed*10)
			
	def turnRight(self, dt):
		self.editNp.setH(self.editNp, -dt*self.speed*10)
			
	def lookUp(self, dt):
		self.editNp2.setP(self.editNp2, dt*self.speed*5)
		
	def lookDown(self, dt):
		self.editNp2.setP(self.editNp2, -dt*self.speed*5)

	
	def moveHeight(self, dt):
		self.editNp.setPos(self.editNp, (0,0,dt*self.speed*10))
		if self.editNp.getZ()<0:
			self.editNp.setZ(0)
		
	
	def start(self):
		base.camera.wrtReparentTo(self.editNp2)
		#render.setShaderInput('cam', self.editNp)
		# trick to avoid the camera hiccup, we delay the possible auto shader regenerating
		taskMgr.doMethodLater(1.0, self.setShaderCam, "setShaderCam")
		
		'''	
		targetHpr = VBase3(fitDestAngle2Src(origHpr[0], targetHpr[0]),
			fitDestAngle2Src(origHpr[1], targetHpr[1]),
			fitDestAngle2Src(origHpr[2], targetHpr[2]))
		'''
		
		LerpPosHprInterval(base.camera, self.intervalSpeed, (0,0,0), hpr=(0,0,0), blendType="easeInOut").start()
	
	def setShaderCam(self, task):
		render.setShaderInput('cam', self.editNp)
		return task.done
	
	def stop(self):
		pass
		
	def update(self):
		pass
	
class GameCamHandler:
	def __init__(self, playerNp):
		self.speed = 15.0
		self.intervalSpeed = 0.8
		self.playerNp = playerNp
		self.gameNp = NodePath("gameCam")
		self.gameNp.setPos(0,0,2.0)
		self.gameNp.reparentTo(render)
		
		self.gameNp2 = NodePath("gameCam2")
		self.gameNp2.setPos(0,-20,0)
		self.gameNp2.reparentTo(self.gameNp)
		
		self.zoomMin = 2.0
		self.zoomMax = 30.0
		self.pMin = -80.0
		self.pMax = 5.0
		self.baseDx=0.0
		self.baseDy=0.0
		
		self.dragging = False
		
	def zoom(self, dist=1.0):
		self.gameNp2.setPos(0, self.gameNp2.getY()+dist, 0)
		if self.gameNp2.getY() < - self.zoomMax:
			self.gameNp2.setY(-self.zoomMax)
		elif self.gameNp2.getY() > - self.zoomMin:
			self.gameNp2.setY(-self.zoomMin)
		
	def rotate(self):
		if base.mouseWatcherNode.hasMouse():
			mpos = base.mouseWatcherNode.getMouse()
			dx = self.baseDx - mpos.getX()
			dy = self.baseDy - mpos.getY()
			self.gameNp.setH(self.gameNp, dx*100)
			self.gameNp.setP(self.gameNp, -dy*100)
			self.gameNp.setR(0)
			if self.gameNp.getP() < self.pMin:
				self.gameNp.setP(self.pMin)
			elif self.gameNp.getP() > self.pMax:
				self.gameNp.setP(self.pMax)
			
			self.baseDx = mpos.getX()
			self.baseDy = mpos.getY()
			
	def start(self):
		base.camera.wrtReparentTo(self.gameNp2)
		LerpPosHprInterval(base.camera, self.intervalSpeed, (0,0,0), hpr=(0,0,0), blendType="easeInOut").start()
		
	
		
	def startDrag(self):
		if base.mouseWatcherNode.hasMouse():
			mpos = base.mouseWatcherNode.getMouse()
			self.baseDx = mpos.getX()
			self.baseDy = mpos.getY()
			self.dragging = True
		
	def stopDrag(self):
		self.dragging = False
		
	def update(self):
		self.gameNp.setPos(self.playerNp, (0,0,2))
		if self.dragging:
			self.rotate()
			
	
