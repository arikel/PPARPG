#!/usr/bin/python
# -*- coding: utf8 -*-

from pandac.PandaModules import * 
from direct.interval.IntervalGlobal import *
from direct.showbase.PythonUtil import fitDestAngle2Src 

class CamHandler:
	def __init__(self, playerNp=None):
		self.speed = 15.0
		self.intervalSpeed = 0.8
		
		self.playingNp = NodePath("camHandler")
		self.playingNp.setPos(10,10,15.0)
		self.playingNp.reparentTo(render)
		
		base.camera.reparentTo(self.playingNp)
		
		self.editNp = NodePath("camHandler2")
		self.editNp.setPos(10,10,60)
		self.editNp.reparentTo(render)
		
		if playerNp is not None:
			self.gameNp = NodePath("camHandler3")
			self.gameNp.setPos(0,0,2.0)
			self.gameNp.reparentTo(playerNp)
			
			self.gameNp2 = NodePath("camHandler3")
			self.gameNp2.setPos(0,-20,5.0)
			self.gameNp2.reparentTo(self.gameNp)
			
			
		self.prevCamHpr = Vec3(0,-45,0)
		self.prevCamHpr2 = Vec3(0,-90,0)
		
		base.camera.setHpr(0,-90,0)
		self.mode = "edit"
		self.setMode("playing") # "edit"
			
	def forward(self, dt):
		if self.mode == "playing":
			self.playingNp.setPos(self.playingNp, (0,dt*self.speed, 0))
		elif self.mode == "edit":
			self.editNp.setPos(self.editNp, (0,dt*self.speed, 0))
		elif self.mode == "game":
			pass
	def backward(self, dt):
		if self.mode == "playing":
			self.playingNp.setPos(self.playingNp, (0,-dt*self.speed, 0))
		elif self.mode == "edit":
			self.editNp.setPos(self.editNp, (0,-dt*self.speed, 0))
		
	def strafeLeft(self, dt):
		if self.mode == "playing":
			self.playingNp.setPos(self.playingNp, (-dt*self.speed,0, 0))
		elif self.mode == "edit":
			self.editNp.setPos(self.editNp, (-dt*self.speed,0, 0))
			
	def strafeRight(self, dt):
		if self.mode == "playing":
			self.playingNp.setPos(self.playingNp, (dt*self.speed,0, 0))
		elif self.mode == "edit":
			self.editNp.setPos(self.editNp, (dt*self.speed,0, 0))
			
	def turnLeft(self, dt):
		if self.mode == "playing":
			self.playingNp.setH(self.playingNp, dt*self.speed*10)
		elif self.mode == "edit":
			self.editNp.setH(self.editNp, dt*self.speed*10)
			
	def turnRight(self, dt):
		if self.mode == "playing":
			self.playingNp.setH(self.playingNp, -dt*self.speed*10)
		elif self.mode == "edit":
			self.editNp.setH(self.editNp, -dt*self.speed*10)
			
	def lookUp(self, dt):
		#if self.mode == "playing":
		base.camera.setP(base.camera, dt*self.speed*5)
		
	def lookDown(self, dt):
		#if self.mode == "playing":
		base.camera.setP(base.camera, -dt*self.speed*5)

	
	def moveHeight(self, dt):
		if self.mode == "playing":
			self.playingNp.setPos(self.playingNp, (0,0,dt*self.speed*10))
			if self.playingNp.getZ()<0:
				self.playingNp.setZ(0)
		elif self.mode == "edit":
			self.editNp.setPos(self.editNp, (0,0,dt*self.speed*10))
			if self.editNp.getZ()<0:
				self.editNp.setZ(0)
				
	def update(self):
		while self.playingNp.getH()<-180.0:
			self.playingNp.setH(self.playingNp.getH()+360.0)
		while self.playingNp.getH()>180.0:
			self.playingNp.setH(self.playingNp.getH()-360.0)
		while self.editNp.getH()<-180.0:
			self.editNp.setH(self.editNp.getH()+360.0)
		while self.editNp.getH()>180.0:
			self.editNp.setH(self.editNp.getH()-360.0)
	
	def toggle(self):
		if self.mode == "playing":
			self.setMode("edit")
		else:
			self.setMode("playing")
			
	def setMode(self, mode):
		if mode == "edit" and self.mode == "playing":
			self.prevCamHpr = base.camera.getHpr()
		elif self.mode == "edit" and mode == "playing":
			self.prevCamHpr2 = base.camera.getHpr()
			
		self.mode = mode
		#self.update()
		
		if self.mode == "playing":
			base.camera.wrtReparentTo(self.playingNp)
			render.setShaderInput('cam', self.playingNp)
			
			origHpr = base.camera.getHpr()
			#targetHpr = (0,-45,0)
			targetHpr = self.prevCamHpr
			
			targetHpr = VBase3(fitDestAngle2Src(origHpr[0], targetHpr[0]),
				fitDestAngle2Src(origHpr[1], targetHpr[1]),
				fitDestAngle2Src(origHpr[2], targetHpr[2]))
			
			i1 = LerpPosInterval(base.camera, self.intervalSpeed, (0,0,0), blendType="easeInOut")
			#i2 = LerpHprInterval(base.camera, self.intervalSpeed, (0,-45,0), blendType="easeInOut")
			i2 = LerpHprInterval(base.camera, self.intervalSpeed, targetHpr, blendType="easeInOut")
			
			paral = Parallel(i1, i2)
			paral.start()
			
		elif self.mode == "edit":
			
			
			base.camera.wrtReparentTo(self.editNp)
			render.setShaderInput('cam', self.editNp)
			
			origHpr = base.camera.getHpr()
			targetHpr = self.prevCamHpr2
			
			targetHpr = VBase3(fitDestAngle2Src(origHpr[0], targetHpr[0]),
				fitDestAngle2Src(origHpr[1], targetHpr[1]),
				fitDestAngle2Src(origHpr[2], targetHpr[2]))
				
			i1 = LerpPosInterval(base.camera, self.intervalSpeed, (0,0,0), blendType="easeInOut")
			i2 = LerpHprInterval(base.camera, self.intervalSpeed, targetHpr, blendType="easeInOut")
			paral = Parallel(i1, i2)
			paral.start()
