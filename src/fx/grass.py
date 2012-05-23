#!/usr/bin/python
# -*- coding: utf8 -*-

import random
from math import *

from panda3d.core import *

def randVec():
	tmpVec = Vec3(random.random()-.5,random.random()-.5,random.random()-.5)
	#tmpVec.normalize()
	return tmpVec

class GrassParticle:
	def __init__(self, originPos, ray, move = False):
		self.originPos = originPos # Vec3
		self.ray = ray # float
		self.diam = 2*self.ray
		self.move = move
		self.x = (2*random.random()-1)*self.ray
		self.y = (2*random.random()-1)*self.ray
		self.z = (2*random.random()-1)*self.ray
		
		#self.pos = Vec3(self.originPos)+randVec()*self.ray*random.random()/2
		self.pos = Vec3(self.x, self.y, self.z)
		
		self.frame = 1
		
		#self.size = random.random()*0.2 + 0.02
		self.size = random.random()*0.2 + 1.2
		self.color = Vec4(random.random()/2.0 + 0.5,random.random()/4.0 + 0.75,random.random()/4.0 + 0.75,1)
		
		self.moveVec = randVec() * 0.01 # + Vec3(0,0,0.02)
		
	def setOriginPos(self, originPos):
		self.originPos = originPos
		dx = self.x - originPos[0]
		dy = self.y - originPos[1]
		dz = self.z - originPos[2]
		
		if dx>self.ray:
			self.x = self.x - self.diam
			#print "particle out, X axis +"
		elif dx < -self.ray:
			self.x = self.x + self.diam
			#print "particle out, X axis -"
		if dy>self.ray:
			self.y = self.y - self.diam
			#print "particle out, Y axis +"
		elif dy < -self.ray:
			self.y = self.y + self.diam
			#print "particle out, Y axis -"
			
		if dz>self.ray:
			self.z = self.z - self.diam
			#print "particle out, Z axis +"
		elif dz < -self.ray:
			self.z = self.z + self.diam
			#print "particle out, Z axis -"
		
		if self.move:
			self.x += self.moveVec[0]
			self.y += self.moveVec[1]
			self.z += self.moveVec[2]
		#self.pos = Vec3(self.x, self.y, self.z)
		self.pos = Vec3(self.x, self.y, 1)
			
		
				
class GrassEngine:
	# grass engine used to have some grass visible only when we're looking at...
	def __init__(self, model, nb=600, ray=50.0, move = False):
		self.np = model
		self.pos = self.np.getPos()
		
		self.ray = ray
		#self.pos = Vec3(pos) # a Vec3
		self.move = move
		maxParticles = 5000 # max number of particle (1000) triangles we will display
		self.generator = MeshDrawer()
		self.generator.setBudget(maxParticles)
		#self.generator.setPlateSize(1)
		#self.generator.setClip(0,0,1,1)
		self.generatorNode = self.generator.getRoot()
		self.generatorNode.reparentTo(render)
		self.generatorNode.setDepthWrite(False)
		self.generatorNode.setTransparency(True)
		#self.generatorNode.setTwoSided(True)
		tex0 = loader.loadTexture("img/textures/plants/grass_1.png")
		#tex0.setWrapU(Texture.WMClamp)
		#tex0.setWrapV(Texture.WMClamp)
		self.generatorNode.setTexture(tex0)
		self.generatorNode.setBin("fixed",0)
		self.generatorNode.setLightOff(True)
		self.generatorNode.setShaderOff(True)
		#self.generatorNode.setScale(1.0,1.0,0.25)
		self.generatorNode.node().setBounds(BoundingSphere((0, 0, 0), 10000000*self.ray))
		self.generatorNode.node().setFinal(True)
		random.seed()
		self.particles = []
		minDist = 10000
		maxDist = -1
		totalDist = 0
		
		for i in range(nb):
			p = GrassParticle(self.pos, self.ray, self.move)
			self.particles.append(p)
			dist = Vec3(self.pos - p.pos).length()
			if dist < minDist:
				minDist = dist
			if dist > maxDist:
				maxDist = dist
			totalDist += dist
		moyDist = totalDist/nb
		#print "ParticleEngine generated, minDist = %s, maxDist = %s, averageDist = %s" % (minDist, maxDist, moyDist)
		
		'''
		# create 100 random lines
		lines = []
		for i in range(100):
			l = [randVec()*100,randVec()*100,187,.1,Vec4(random.random(),random.random(),random.random(),1)]
			lines.append(l)
		'''
		
		self.speed = 50.0
		
		self.start()
		
	def setPos(self, pos):
		self.pos = pos
		
	def start(self):
		if (not(taskMgr.hasTaskNamed("drawStarDust"))):
			taskMgr.add(self.drawTask, "drawStarDust")
		self.generatorNode.reparentTo(render)
		
	def stop(self):
		if (taskMgr.hasTaskNamed("drawStarDust")):
			taskMgr.remove("drawStarDust")
		self.generatorNode.detachNode()
		
		
	def drawTask(self, task):
		""" this is called every frame to regen the mesh """
		#t = globalClock.getFrameTime()
		self.pos = self.np.getPos(render)
		self.generator.begin(base.cam,render)
		#for pos,frame,size,color in self.particles:
		for p in self.particles:
			p.setOriginPos(self.pos)
			#print "Position origine : %s" % (self.pos)
			#self.generator.billboard(p.pos,p.frame,p.size,p.color)
			#direction = render.getRelativeVector(self.np, (0,self.speed/10.0,0))
			#alpha = min(self.speed/100.0, 1)
			#direction = Vec3(direction)
			#self.generator.segment(p.pos,p.pos+direction,1,0.5,Vec4(1,1,1,alpha))
			self.generator.billboard(p.pos,p.frame,p.size,p.color)
		'''
		for start,stop,frame,size,color in lines:
			generator.segment(start,stop,frame,size*sin(t*2)+2,color)
		'''
		self.generator.end()
		return Task.cont
		
	def draw(self, speed):
		self.pos = self.np.getPos()
		self.generator.begin(base.cam,render)
		for p in self.particles:
			p.setOriginPos(self.pos)
			#direction = render.getRelativeVector(self.np, (0,speed/5.0,0))
			#direction = Vec3(0,speed,0)
			#self.generator.segment(p.pos,p.pos+direction,1,0.5,Vec4(1,1,1,1))
			self.generator.billboard(p.pos,1,(p.size*2,p.size/2.0,p.size/2.0),p.color)
		self.generator.end()
		
		
	def destroy(self):
		self.stop()
		self.particles = []
		self.generatorNode.detachNode()
		self.generatorNode.removeNode()
		self.generatorNode.remove()
