#!/usr/bin/python
# -*- coding: utf8 -*-

from pandac.PandaModules import *
from direct.showbase.DirectObject import DirectObject
from direct.task import Task
import direct.directbase.DirectStart

from skyBox import SkyBox

from random import random, seed
from math import *
import sys

	
def randVec():
	tmpVec = Vec3(random()-.5,random()-.5,random()-.5)
	#tmpVec.normalize()
	return tmpVec

class GrassParticle:
	def __init__(self, originPos, ray, move = False):
		self.originPos = originPos # Vec3
		self.ray = ray # float
		self.diam = 2*self.ray
		self.move = move
		self.x = (2*random()-1)*self.ray
		self.y = (2*random()-1)*self.ray
		self.z = (2*random()-1)*self.ray
		
		#self.pos = Vec3(self.originPos)+randVec()*self.ray*random()/2
		self.pos = Vec3(self.x, self.y, self.z)
		
		self.frame = 1
		
		#self.size = random()*0.2 + 0.02
		self.size = random()*0.2 + 1.2
		self.color = Vec4(random()/2.0 + 0.5,random()/4.0 + 0.75,random()/4.0 + 0.75,1)
		
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
		seed()
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
			l = [randVec()*100,randVec()*100,187,.1,Vec4(random(),random(),random(),1)]
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

class WaterNode():

	def __init__(self, world, x1, y1, x2, y2, z):
		#print('setting up water plane at z='+str(z))

		# Water surface
		maker = CardMaker( 'water' )
		maker.setFrame( x1, x2, y1, y2 )

		world.waterNP = render.attachNewNode(maker.generate())
		world.waterNP.setHpr(0,-90,0)
		world.waterNP.setPos(0,0,z)
		world.waterNP.setTransparency(TransparencyAttrib.MAlpha )
		world.waterNP.setShader(loader.loadShader( 'shaders/water.sha' ))
		world.waterNP.setShaderInput('wateranim', Vec4( 0.03, -0.015, 64.0, 0 )) # vx, vy, scale, skip
		# offset, strength, refraction factor (0=perfect mirror, 1=total refraction), refractivity
		world.waterNP.setShaderInput('waterdistort', Vec4( 0.4, 4.0, 0.4, 0.45 ))	

		# Reflection plane
		world.waterPlane = Plane( Vec3( 0, 0, z+1 ), Point3( 0, 0, z ) )
		planeNode = PlaneNode( 'waterPlane' )
		planeNode.setPlane( world.waterPlane )

		# Buffer and reflection camera
		buffer = base.win.makeTextureBuffer( 'waterBuffer', 512, 512 )
		buffer.setClearColor( Vec4( 0, 0, 0, 1 ) )

		cfa = CullFaceAttrib.makeReverse( )
		rs = RenderState.make(cfa)

		world.watercamNP = base.makeCamera( buffer )
		world.watercamNP.reparentTo(render)
		
		sa = ShaderAttrib.make()
		sa = sa.setShader(loader.loadShader('shaders/splut3Clipped.sha') )

		cam = world.watercamNP.node()
		cam.getLens( ).setFov( base.camLens.getFov( ) )
		cam.getLens().setNear(1)
		cam.getLens().setFar(5000)
		cam.setInitialState( rs )
		cam.setTagStateKey('Clipped')
		cam.setTagState('True', RenderState.make(sa)) 

		# ---- water textures ---------------------------------------------

		# reflection texture, created in realtime by the 'water camera'
		tex0 = buffer.getTexture( )
		tex0.setWrapU(Texture.WMClamp)
		tex0.setWrapV(Texture.WMClamp)
		ts0 = TextureStage( 'reflection' )
		world.waterNP.setTexture( ts0, tex0 ) 

		# distortion texture
		tex1 = loader.loadTexture('img/textures/water.png')
		ts1 = TextureStage('distortion')
		world.waterNP.setTexture(ts1, tex1)
		
		

class WaterPlane():

	def __init__(self, x1=-10, y1=-10, x2 = 10, y2 = 10):
		# some constants
		self._water_level = Vec4(0.0, 0.0, -0.01, 1.0)
		self.water = WaterNode(self, x1, y1, x2, y2, self._water_level.getZ())
		ambient = Vec4(0.4, 0.4, 0.4, 1)
		direct = Vec4(0.74, 0.74, 0.75, 1)
		# ambient light
		alight = AmbientLight('alight')
		alight.setColor(ambient)
		alnp = render.attachNewNode(alight)
		#render.setLight(alnp)
		# directional ("the sun")
		dlight = DirectionalLight('dlight')
		dlight.setColor(direct)
		dlnp = render.attachNewNode(dlight)
		dlnp.setHpr(0.7,0.2,-0.2)
		#render.setLight(dlnp)

		# make waterlevel and lights available to the terrain shader
		self.waterNP.setShaderInput('lightvec', Vec4(0.7, 0.2, -0.2, 1))
		self.waterNP.setShaderInput('lightcolor', direct)
		self.waterNP.setShaderInput('ambientlight', ambient)
		wl=self._water_level
		wl.setZ(wl.getZ()-0.05)	# add some leeway (gets rid of some mirroring artifacts)
		self.waterNP.setShaderInput('waterlevel', self._water_level)
		self.waterNP.setShaderInput('time', 0.0)
		
		#self.sky = SkyBox()
		#self.sky.load("hipshot1")
		#self.sky.set("hipshot1")
		
		self.prevtime = 0.0
		self.task = taskMgr.add(self.move, "move")
		
	def move(self, task):
		elapsed = task.time - self.prevtime
		
		self.waterNP.setShaderInput('time', task.time)
		#self.waterNP.setShaderInput('cam', base.camera) # moved to camHandler for now
		# update matrix of the reflection camera
		
		mc = base.camera.getMat(render) # WRT render, since our camera will most often be reparented to something else.
		mf = self.waterPlane.getReflectionMat()
		self.watercamNP.setMat(mc * mf)
		
		# Store the task time and continue.
		self.prevtime = task.time
		return Task.cont
		
	def destroy(self):
		taskMgr.remove(self.task)
		
if __name__ == "__main__":
	base.setFrameRateMeter(True)
	#w = WaterPlane()
	p = ParticleEngine(base.camera)
	base.accept("escape", sys.exit)
	run()
