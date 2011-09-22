#!/usr/bin/python
# -*- coding: utf8 -*-

from pandac.PandaModules import *
from direct.showbase.DirectObject import DirectObject
from direct.task import Task
import direct.directbase.DirectStart

from skyBox import SkyBox

class WaterNode():

	def __init__(self, world, x1, y1, x2, y2, z):
		print('setting up water plane at z='+str(z))

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
		
if __name__ == "__main__":
	base.setFrameRateMeter(True)
	w = WaterPlane()
	run()
