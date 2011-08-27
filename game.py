#!/usr/bin/python
# -*- coding: utf8 -*-

from pandac.PandaModules import * 

loadPrcFileData("setup", """sync-video 0
show-frame-rate-meter #t
#win-size 800 600
win-size 1024 768
#win-size 1280 960
#win-size 1280 1024
win-fixed-size 1
#yield-timeslice 0 
#client-sleep 0 
#multi-sleep 0
basic-shaders-only #f
fullscreen #f
#audio-library-name null
""")


import direct.directbase.DirectStart
from direct.showbase.DirectObject import DirectObject
from direct.actor.Actor import Actor

from direct.task import Task
from direct.interval.IntervalGlobal import *
from direct.gui.OnscreenText import OnscreenText
from direct.filter.CommonFilters import CommonFilters
from direct.fsm.FSM import FSM

import sys, random
import cPickle as pickle

from camHandler import CamHandler
from pathFind import *

from skyBox import SkyBox
from lightManager import LightManager

from mouseCursor import *
from gui import *
from dialog import *


			

	
class Clicker:
	def __init__(self):
		"""
		This class is used to handle clicks on the collision / pathfinding grid
		"""
		self.plane = Plane(Vec3(0, 0, 1), Point3(0, 0, 0))
		self.picker = CollisionTraverser()
		self.pq     = CollisionHandlerQueue()
		self.pickerNode = CollisionNode('mouseRay')
		self.pickerNP = camera.attachNewNode(self.pickerNode)
		self.pickerNode.setFromCollideMask(BitMask32.bit(1))
		self.pickerRay = CollisionRay()
		self.pickerNode.addSolid(self.pickerRay)
		self.picker.addCollider(self.pickerNP, self.pq)
		self.picker.showCollisions(render)
		
	def getMouseObject(self, np=render):
		if base.mouseWatcherNode.hasMouse():
			mpos = base.mouseWatcherNode.getMouse()
			
			self.pickerRay.setFromLens(base.camNode, mpos.getX(), mpos.getY())
			self.picker.traverse(np)
			if self.pq.getNumEntries() > 0:
				self.pq.sortEntries()
				#print "y'a eu %s collisions!!!" % (self.pq.getNumEntries())
				res = self.pq.getEntry(0)
				#print "Entry = %s" % (res)
				#print dir(res)
				return res
			#else:
			#	print "y'a rien eu..."
		return None
		
	def getMousePos(self, mpos=None):
		if mpos is None:
			if base.mouseWatcherNode.hasMouse():
				mpos = base.mouseWatcherNode.getMouse()
			else:
				return None
			
		pos3d = Point3()
		nearPoint = Point3()
		farPoint = Point3()
		base.camLens.extrude(mpos, nearPoint, farPoint)
		if self.plane.intersectsLine(pos3d,
				render.getRelativePoint(camera, nearPoint),
				render.getRelativePoint(camera, farPoint)):
			
			x = pos3d.getX()
			y = pos3d.getY()
			return int(x), int(y)
		return None


#-----------------------------------------------------------------------
# NPC
#-----------------------------------------------------------------------

class NPC:
	def __init__(self, name, modelName, tex):
		self.name = name
		path = "models/" + modelName
		self.model = Actor(path, {
			"walk":"models/male-walk",
			"idle": "models/male-idle"
		})
		texPath = "models/" + tex
		self.tex = loader.loadTexture(texPath)
		self.model.setTexture(self.tex)
		self.model.reparentTo(render)
		
		#self.colSphere = CollisionSphere(0,0,0.45,0.4)
		self.colSphere = CollisionTube(0,0,0,0,0,1.8,0.4)
		self.colNodepath = CollisionNode(self.name)
		self.colNode = self.model.attachNewNode(self.colNodepath)
		self.colNode.node().addSolid(self.colSphere)
		
		self.speed = 0.4
		
		self.path = []
		self.sequence = Sequence()
		self.setMode("idle")
		
		self.timer = random.random()*5.0
		
		self.data = {}
		self.data["name"] = self.name
		
		self.task = taskMgr.add(self.update, self.name)
		
	def reparentToNPC(self, npc):
		#print "%s is reparenting itself to parent : %s" % (self.name, npc.name)
		self.model.reparentTo(npc.model)
		self.parentName = npc.name
		self.model.setTexture(self.tex)
		
	def loop(self, animName):
		self.model.loop(animName)
		
	def stop(self):
		self.model.stop()
		
	def setPos(self, *pos):
		self.model.setPos(pos)
		
	def setTilePos(self, x, y):
		self.setPos(x+0.5, y+0.5, 0)
		
	def getTilePos(self):
		return int(self.model.getX()), int(self.model.getY()) 
		
	def lookAt(self, x, y):
		#self.model.lookAt(self.model, (-x,-y,0))
		a, b = self.getTilePos()
		self.model.lookAt(a-x+0.5,b-y+0.5,self.model.getZ())
		#print "Looking at %s, %s" % (y, x)
		
	def setPath(self, path):
		if path == []:
			return
		if len(self.path)>1 and len(path)>1:
			if self.path[-1] == path[-1]:
				return
		#print "NPC : set path called"
		
		if self.sequence.isPlaying():
			self.sequence.pause()
			
		self.path = path
		self.sequence = Sequence()
		self.timer = random.random()*15.0
		# lookAt for first move
		a, b = self.getTilePos()
		x = path[0][0] - a
		y = path[0][1] - b
		self.lookAt(x, y)
		
		f = Func(self.setMode, "walk")
		self.sequence.append(f)
		
		for n, tile in enumerate(path):
			if n<len(path)-1:
				x = path[n+1][0] - tile[0]
				y = path[n+1][1] - tile[1]
				f = Func(self.lookAt, x, y)
				self.sequence.append(f)
				
			i = LerpPosInterval(self.model,
				self.speed,
				(tile[0]+0.5, tile[1]+0.5, tile[2])
				)
			self.sequence.append(i)
			self.timer += self.speed
			#print "adding tile %s, %s to path for %s" % (tile[0], tile[1], self.name)
		#print "On NPC start sequence, timer = %s" % (self.timer)
		f = Func(self.setMode, "idle")
		self.sequence.append(f)
		
		self.sequence.start()
		
	def setMode(self, mode):
		self.mode = mode
		self.loop(mode)
		
	def setTimer(self, n):
		self.timer = float(n)
		
	def update(self, task):
		dt = globalClock.getDt()
		self.timer -= dt
		#print "NPC update : timer = %s" % (self.timer)
		
		'''
		if self.sequence.isPlaying() and self.mode == "idle":
			self.setMode("walk")
			
		elif not self.sequence.isPlaying() and self.mode == "walk":
			self.setMode("idle")
		'''
		return task.cont
		
		
def makeFloor(nbCases, scalex, scaley):
	cm = CardMaker('card')
	cm.setUvRange(Point2(scalex/2,scaley/2), Point2(0,0))
	cm.setHasNormals(True)
	#card = render.attachNewNode(cm2.generate())
	card = NodePath(cm.generate())
	img = loader.loadTexture("img/textures/floor01.png")
	img.setWrapU(Texture.WMRepeat)
	img.setWrapV(Texture.WMRepeat)
	
	card.setTexture(img)
	#card2.setScale(512.0/512.0, 1, 512.0/384.0)
	card.setScale(scalex,1,scaley)
	card.setPos(0,0,-0.01)
	card.setHpr(0,-90,0)
	#card.setTwoSided(True)
	card.setTransparency(TransparencyAttrib.MAlpha)
	return card
	
def makeWall(scalex, scaley, scaleTex):
	cm = CardMaker('card')
	cm.setUvRange((scalex/scaleTex,0), (0,scaley/scaleTex))
	cm.setHasNormals(True)
	card = NodePath(cm.generate())
	img = loader.loadTexture("img/textures/oldstone4.jpg")
	card.setTexture(img)
	card.setScale(scalex,1,scaley)
	#card.setHpr(0,0,0)
	card.setTwoSided(True)
	card.setTransparency(TransparencyAttrib.MAlpha)
	return card

class MapWall:
	def __init__(self, x, y,z=0):
		self.walls = []
		
		height = 6.0
		texScale = 5.0
		
		wall1 = makeWall(x, height, texScale)
		wall1.reparentTo(render)
		wall1.setPos(0,y,z)
		self.walls.append(wall1)
		
		wall1 = makeWall(x, height, texScale)
		wall1.reparentTo(render)
		wall1.setPos(x,0,z)
		wall1.setHpr(180,0,0)
		self.walls.append(wall1)
		
		wall1 = makeWall(y, height, texScale)
		wall1.reparentTo(render)
		wall1.setPos(0,0,z)
		wall1.setHpr(90,0,0)
		self.walls.append(wall1)
		
		wall1 = makeWall(y, height, texScale)
		wall1.reparentTo(render)
		wall1.setPos(x,y,z)
		wall1.setHpr(-90,0,0)
		self.walls.append(wall1)
		
	def destroy(self):
		for wall in self.walls:
			wall.remove()
	
		
#-----------------------------------------------------------------------
# CollisionGrid
#-----------------------------------------------------------------------
class CollisionGrid:
	def __init__(self, x=50, y=30, name=None, texPath=None):
		self.name = name
		
		self.x = x
		self.y = y
		
		self.data = [] # [[1,1,1,1,0,1,0,0,...], [1,0,0,...]... ]
		for y in range(self.y):
			tmp = []
			for x in range(self.x):
				tmp.append(0)
			self.data.append(tmp)
				
		
		self.node = GeomNode("tiledMesh")
		self.gvd = GeomVertexData('name', GeomVertexFormat.getV3n3c4t2(), Geom.UHStatic)
		self.geom = Geom(self.gvd)
		self.prim = GeomTriangles(Geom.UHStatic)
		
		self.update()
		
		i = 0
		for x in range(self.x * self.y):
			self.prim.addVertices(i, i + 3, i + 2)
			self.prim.addVertices(i, i + 2, i + 1)
			i += 4
		
		self.prim.closePrimitive()
		self.geom.addPrimitive(self.prim)
		self.node.addGeom(self.geom)
		
		self.np = NodePath(self.node)
		self.np.reparentTo(render)
		#self.np.setTwoSided(True)
		#self.np.setTransparency(True)
		self.tex = loader.loadTexture(texPath)
		self.np.setTexture(self.tex)
		#self.np.setColor(0,0,1.0,0.1)
		#self.np.setTransparency(True)
		
		self.terrain = GeoMipTerrain("ground")
		self.terrain.setHeightfield("models/grounds/ground02.jpg")
		#self.terrain.setMinLevel(2)
		#self.terrain.setBruteforce(True)
		self.terrainScale = 5.0
		self.terrainImgSize = 65.0
		self.terrainNP = self.terrain.getRoot()
		self.terrainNP.reparentTo(render)
		self.terrainNP.setScale(self.x/self.terrainImgSize,self.y/self.terrainImgSize,self.terrainScale)
		self.terrainNP.setPos(0,0,-self.terrainScale)
		self.terrain.generate()
		self.terrainNP.setTexture(loader.loadTexture("img/textures/ice01.jpg"))
		self.terrainNP.setTexScale(TextureStage.getDefault(),self.terrainImgSize/10,self.terrainImgSize/10)
		self.terrainNP.flattenStrong()
		#self.terrainNP.setCollideMask(BitMask32(1))
		
	def collisionHide(self):
		self.np.hide()
		
	def collisionShow(self):
		self.np.show()
		
	def getTileHeight(self, x, y):
		if not (0<=x<self.x): return - self.terrainScale
		if not (0<=y<self.y): return - self.terrainScale
		xPx = int(float(x)/self.x*self.terrainImgSize)
		yPx = int(float(y)/self.y*self.terrainImgSize)
		height = self.terrain.getElevation(xPx, yPx) * self.terrainScale - self.terrainScale
		#print "Terrain height in %s / %s : %s" % (x, y, height)
		return height
		
	def update(self):
		self.vertex = GeomVertexWriter(self.gvd, 'vertex')
		self.texcoord = GeomVertexWriter(self.gvd, 'texcoord')
		self.color = GeomVertexWriter(self.gvd, 'color')
		self.normal = GeomVertexWriter(self.gvd, 'normal')
		
		i = 0
		for y in range(self.y):
			for x in range(self.x):
				if self.data[y][x] == 1:
					self.addWallTile(x, y)
				else:
					self.addEmptyTile(x, y)
				i += 4
			
	def rebuild(self):
		self.update()

		
	def addWallTile(self, x, y):
		
		norm, norm2 = random.random()/2.0, random.random()/2.0
		#z = 0
		z1 = self.getTileHeight(x, y) + 0.35
		z2 = self.getTileHeight(x, y+1) + 0.35
		z3 = self.getTileHeight(x+1, y+1) + 0.35
		z4 = self.getTileHeight(x+1, y) + 0.35
		
		self.vertex.addData3f(x, y, z1)
		self.texcoord.addData2f(0, 0)
		self.color.addData4f(1, 1, 1, 1)
		self.normal.addData3f(norm,norm2,1)
		
		self.vertex.addData3f(x, y+1, z2)
		self.texcoord.addData2f(0, 1)
		self.color.addData4f(1, 1, 1, 1)
		self.normal.addData3f(norm,norm2,1)
		
		self.vertex.addData3f(x+1, y+1, z3)
		self.texcoord.addData2f(1, 1)
		self.color.addData4f(1, 1, 1, 1)
		self.normal.addData3f(norm,norm2,1)
		
		self.vertex.addData3f(x+1, y, z4)
		self.texcoord.addData2f(1, 0)
		self.color.addData4f(1, 1, 1, 1)
		self.normal.addData3f(norm,norm2,1)

	def addEmptyTile(self, x, y):
		#z = random()/100.0
		z = 0
		self.vertex.addData3f(x, y, z)
		self.texcoord.addData2f(0, 0)
		self.color.addData4f(1, 1, 1, 1)
		self.normal.addData3f(0,0,1)
		
		self.vertex.addData3f(x, y, z)
		self.texcoord.addData2f(0, 1)
		self.color.addData4f(1, 1, 1, 1)
		self.normal.addData3f(0,0,1)
		
		self.vertex.addData3f(x, y, z)
		self.texcoord.addData2f(1, 1)
		self.color.addData4f(1, 1, 1, 1)
		self.normal.addData3f(0,0,1)
		
		self.vertex.addData3f(x, y, z)
		self.texcoord.addData2f(1, 0)
		self.color.addData4f(1, 1, 1, 1)
		self.normal.addData3f(0,0,1)
		
	def hideTile(self, x, y):
		if (0<=x<self.x) and (0<=y<self.y):
			if self.data[y][x]!=0:
				self.data[y][x] = 0
				row = (self.x*y + x)*4
				
				self.vertex = GeomVertexWriter(self.gvd, 'vertex')
				self.texcoord = GeomVertexWriter(self.gvd, 'texcoord')
				self.color = GeomVertexWriter(self.gvd, 'color')
				self.normal = GeomVertexWriter(self.gvd, 'normal')
				
				self.vertex.setRow(row)
				self.texcoord.setRow(row)
				self.color.setRow(row)
				self.normal.setRow(row)
				
				self.addEmptyTile(x, y)
				#self.update()
	
	def showTile(self, x, y):
		if (0<=x<self.x) and (0<=y<self.y):
			if self.data[y][x]!=1:
				self.data[y][x] = 1
				row = (self.x*y + x)*4
				
				self.vertex = GeomVertexWriter(self.gvd, 'vertex')
				self.texcoord = GeomVertexWriter(self.gvd, 'texcoord')
				self.color = GeomVertexWriter(self.gvd, 'color')
				self.normal = GeomVertexWriter(self.gvd, 'normal')
				
				self.vertex.setRow(row)
				self.texcoord.setRow(row)
				self.color.setRow(row)
				self.normal.setRow(row)
				
				self.addWallTile(x, y)
				
				#self.update()
		
		
	def fill(self):
		for y in range(self.y):
			for x in range(self.x):
				self.data[y][x] = 1
		self.update()
		
	def clear(self):
		self.data = [] # [[1,1,1,1,0,1,0,0,...], [1,0,0,...]... ]
		for y in range(self.y):
			for x in range(self.x):
				self.data[y][x] = 0
		self.update()
	
	def fillBorder(self):
		for y in range(self.y):
			for x in range(self.x):
				if self.data[y][x] == 0:
					if (x==0) or (y==0):
						self.data[y][x] = 1
					if (x==self.x-1) or (y==self.y-1):
						self.data[y][x] = 1
					
		self.update()
		
	def getRandomTile(self):
		while True:
			x = random.randint(1,self.x-1)
			y = random.randint(1,self.y-1)
			if self.data[y][x]==0:
				#print "returning random free tile : %s %s" % (x, y)
				return x, y
	

	
class GameMap(DirectObject):
	def __init__(self, x, y):
		self.x = x
		self.y = y
		
		#self.floor = makeFloor(20, self.x, self.y)
		#self.floor.reparentTo(render)
		
		self.root = NodePath("root")
		self.root.reparentTo(render)
		
		self.collisionGrid = CollisionGrid(x, y, "the camp", "img/textures/sand2.jpg")
		self.collisionGrid.fillBorder()
		self.mapWall = MapWall(x, y, -3)
		
		self.clicker = Clicker()
		
		# NPCs
		self.NPC = {}
		for name in ["ula2", "Kimmo", "Drunkard", "Camilla"]:
			x, y = self.collisionGrid.getRandomTile()
			self.addNPC(name, "male", "humanTex2.png", x,y)
		
		'''
		for name in ["coco", "myrdhen", "noob"]:
			x, y = self.collisionGrid.getRandomTile()
			self.addNPC(name, "male", "humanTex2.png", x,y)
		'''
		
		
		'''
		for i in range(50):
			name = "noob" + str(i)
			x, y = self.collisionGrid.getRandomTile()
			self.addNPC(name, "male", "humanTex.png", x,y)
		'''
		
		self.player = NPC("arikel", "male", "humanTex2.png")
		self.player.setTilePos(1, 1)
		
		#npc.model.reparentTo(self.root)
		
		# light
		self.light = LightManager()
		self.light.lightCenter.setPos(0,0,0)
		self.light.lightCenter.reparentTo(base.camera)
		
		
		self.keyDic = {}
		for key in ["mouse1", "mouse3", "z", "s", "q", "d", "a", "e", "r", "f"]:
			self.keyDic[key] = 0
			self.accept(key, self.setKey, [key, 1])
			keyUp = key + "-up"
			self.accept(keyUp, self.setKey, [key, 0])
		
		
		self.camHandler = CamHandler()
		self.setMode("playing")
		
		self.accept("space", self.toggle)
		self.accept("quit", self.quit, [["this one is from GameMap", "this one too"]])
		self.accept("m", self.save, ["mapCode.txt"])
		self.accept("p", self.load, ["mapCode.txt"])
		
		self.msg = makeMsg(-1.3,0.95,"PPARPG : a new hope...")
		#self.msg2 = makeMsgLeft2(-0.8,0.7,"This is a new hope for PARPG...")
		self.cursor = MouseCursor()
		
		self.dialog = None # current dialog
		
		self.load("mapCode.txt")
		
		taskMgr.add(self.update, "gameMapTask")
		
		
	def openDialog(self, name):
		if self.dialog:
			#print "There was dialog garbage left, %s got his/her dialog shut unpolitely." % (self.dialog.name)
			#self.dialog.destroy()
			#print "a dialog is already open"
			return False
			
		if name == "Camilla":
			self.dialog = DialogCamilla(self)
		else:
			self.dialog = Dialog(self, name)
			
		msg = "You are now talking to " + name
		self.dialog.setMainText(msg)
		
	def quit(self, args=[], extraArgs=[]):
		print "Quit has really been fired from an event, baby! args were : \n- %s\nExtra args were:\n%s" % (str(args), str(extraArgs))
		
		
		
	def save(self, filename):
		mapData = {}
		mapData["collision"] = self.collisionGrid.data
		mapData["models"] = ["house", "barrel"]
		
		f = open(filename, 'w')
		pickle.dump(mapData, f)
		f.close()
		print "map data saved as %s" % (filename)
		
		
		
	def load(self, filename):
		mapData = pickle.load(open(filename, 'r'))
		self.collisionGrid.data = mapData["collision"]
		print "models in use : %s" % (mapData["models"])
		self.collisionGrid.update()
		
	def setKey(self, key, value):
		self.keyDic[key] = value
		
	def setMode(self, mode):
		self.mode = mode
		self.camHandler.setMode(mode)
		
	def toggle(self):
		if self.mode == "edit":
			self.mode = "playing"
			#self.collisionGrid.collisionHide()
			self.camHandler.setMode("playing")
			#base.enableMouse()
			
		else:
			self.mode = "edit"
			self.camHandler.setMode("edit")
			#self.collisionGrid.collisionShow()
			#base.disableMouse()
		
	def addNPC(self, name, modelName, tex, x, y):
		npc = NPC(name, modelName, tex)
		npc.setTilePos(x, y)
		self.NPC[name] = npc
		npc.model.reparentTo(self.root)
		
	def playerGoto(self, x, y):
		start = (self.player.getTilePos())
		end = (x, y)
		data = self.collisionGrid.data
		path = astar(start, end, data)
		if path is []:
			#print "... but no good path found"
			return False
		newPath = []
		for tile in path:
			newPath.append((tile[0], tile[1], self.collisionGrid.getTileHeight(tile[0], tile[1])))
		self.player.setPath(newPath)
		return True
	
	def NPCGoto(self, name, x, y):
		#print "NPCGoto called!"
		if name not in self.NPC:
			#print "%s is not a known NPC" % (name)	
			return False
		start = (self.NPC[name].getTilePos())
		end = (x, y)
		data = self.collisionGrid.data
		path = astar(start, end, data)
		if path is []:
			#print "... but no good path found"
			return False
		#else:
		#	print "NPCGoto : path found : %s" % (path)
		newPath = []
		for tile in path:
			newPath.append((tile[0], tile[1], self.collisionGrid.getTileHeight(tile[0], tile[1])))
		self.NPC[name].setPath(newPath)
		
		
	def update(self, task):
		dt = globalClock.getDt()
		if base.mouseWatcherNode.hasMouse():
			mpos = base.mouseWatcherNode.getMouse()
		else:
			return task.cont
		
		
			
		
		#res = self.clicker.getMouseObject(self.root)
		res = self.clicker.getMouseObject(render)
		if res is not None:
			#print "Found a name : %s " % (res.getIntoNodePath().getName())
			name = res.getIntoNodePath().getName()
			msg = "Pointing on " + name
			self.msg.setText(msg)
			self.msg.setPos(mpos.getX()*1.33+0.1, mpos.getY()+0.02)
			if self.keyDic["mouse1"] and name != self.player.name:
				self.openDialog(name)
			
		else:
			self.msg.setText("")
		
		
		pos = self.clicker.getMousePos(mpos)
		if pos is None:
			return task.cont
		
		
		if self.mode == "edit":
			if self.keyDic["mouse1"]:
				self.collisionGrid.showTile(pos[0], pos[1])
			elif self.keyDic["mouse3"]:
				self.collisionGrid.hideTile(pos[0], pos[1])
		elif self.mode == "playing":
			if self.keyDic["mouse1"]:
				self.playerGoto(pos[0], pos[1])
				
				#for name in self.NPC:
				#	self.NPCGoto(name, pos[0], pos[1])
		
		if self.keyDic["z"]:
			self.camHandler.forward(dt)
		if self.keyDic["s"]:
			self.camHandler.backward(dt)
		
		if self.keyDic["q"]:
			self.camHandler.strafeLeft(dt)
			
		if self.keyDic["d"]:
			self.camHandler.strafeRight(dt)
			
		if self.keyDic["a"]:
			self.camHandler.turnLeft(dt)
		if self.keyDic["e"]:
			self.camHandler.turnRight(dt)
			
		if self.keyDic["r"]:
			self.camHandler.lookUp(dt)
		if self.keyDic["f"]:
			self.camHandler.lookDown(dt)
		
		
		for name in self.NPC:
			npc = self.NPC[name]
			if npc.timer <= 0:
				if npc.mode == "idle":
					#print "Sending NPC to random pos"
					x, y = self.collisionGrid.getRandomTile()
					self.NPCGoto(name, x, y)
				#elif npc.mode == "walk":
					
		return task.cont
				




gamemap = GameMap(40,25)

house = loader.loadModel("models/buildings/house")
house.reparentTo(render)
house.setPos(15,12,-2)
#house.setColor(1,1,1,0.5)
house.setTransparency(True)

for i in [(15.5,20.5,-2), (12.5,15.5,-2), (8.5,4.5,-2)]:
	barrel = loader.loadModel("models/buildings/crate1")
	barrel.reparentTo(render)
	barrel.setPos(i)

for i in [(12.5,18.5,-2), (14.5,15.5,-2), (9.5,6.5,-2)]:
	barrel = loader.loadModel("models/buildings/barrel")
	barrel.reparentTo(render)
	barrel.setPos(i)

for i in [(10.5,14.5,-2), (14.5,11.5,-2), (11.5,9.5,-2)]:
	barrel = loader.loadModel("models/buildings/barrel2")
	barrel.reparentTo(render)
	barrel.setPos(i)

sky = SkyBox()
#sky.load("hipshot1")
sky.load("teal1")
sky.set("teal1")

#button = MainButton(-0.5,0.8, u"PPARPG coming...")
#dg = DialogGui(0,-0.5,"Kimmo")


base.accept("escape", sys.exit)

base.disableMouse()

base.setFrameRateMeter(True)

props = WindowProperties()
props.setCursorHidden(True) 
base.win.requestProperties(props)

bgMusic = loader.loadSfx("music/preciouswasteland.ogg")
bgMusic.setLoop(True)
bgMusic.play()

#messenger.send("quit", [["and", "a", "shit", "load", "of", "other", "things"]])

render.setShaderAuto()
#render.setAntialias(AntialiasAttrib.MMultisample)
#render.setAntialias(AntialiasAttrib.MAuto)

run()
