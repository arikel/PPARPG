#!/usr/bin/python
# -*- coding: utf8 -*-


import random
import math

from panda3d.core import ClockObject
from panda3d.core import VBase3, Point2, Point3, Vec3, Vec4

from panda3d.core import NodePath, PandaNode, ModelRoot, Geom, GeomNode
from panda3d.core import LPlanef, Plane
from panda3d.core import GeomVertexFormat, GeomVertexData
from panda3d.core import GeomVertexReader, GeomVertexWriter
from panda3d.core import GeomLinestrips
from panda3d.core import GeomTriangles, GeomTrifans
from panda3d.core import Triangulator

from panda3d.core import AmbientLight, DirectionalLight, PointLight
from panda3d.core import loadPrcFileData

if __name__ == "__main__":
	loadPrcFileData("setup", """sync-video 0
show-frame-rate-meter #t
win-size %s %s
win-fixed-size 1
#yield-timeslice 0 
#client-sleep 0 
#multi-sleep 0
basic-shaders-only #f
fullscreen %s
#audio-library-name null
text-minfilter linear_mipmap_nearest
text-flatten 0
framebuffer-multisample 1
multisamples 2
notify-output panda.log
notify-level-util error
notify-level error
default-directnotify-level error
""" % (1024, 768, False))

from direct.showbase.ShowBase import ShowBase
from direct.showbase.DirectObject import DirectObject

from lineDrawer import LineDrawer

#-----------------------------------------------------------------------
# list manipulation functions
#-----------------------------------------------------------------------
def removeDoubles(seq):
	# this code is not clear, it's fast
	seen = set()
	seen_add = seen.add
	return [x for x in seq if x not in seen and not seen_add(x)]

def orderPointsFromPairs(seq):
	nb = len(seq)
	if nb<2:return []
	pts = {}
	for pair in seq:
		p1 = pair[0]
		p2 = pair[1]
		if p1 in pts:
			pts[p1] += 1
		else:
			pts[p1] = 1
		if p2 in pts:
			pts[p2] += 1
		else:
			pts[p2] = 1
	correct = True
	for pt in pts:
		if pts[pt] != 2:
			print "WARNING : %s is present %s times instead of 2" % (pt, pts[pt])
			correct = False
	if not correct:
		return []
		
	# choose the two first points
	startP = seq[0][0]
	nextP = seq[0][1]
	# find the last point
	for pair in seq:
		if startP in pair and nextP not in pair:
			if startP == pair[0]:
				endP = pair[1]
			else:
				endP = pair[0]
	
	
	res = []
	res.append(startP)
	res.append(nextP)
	
	while (len(res) < nb):
		for pair in seq:
			nextP = res[-1]
			p1 = pair[0]
			p2 = pair[1]
			if nextP in pair:
				if nextP == p1 and p2 not in res:
					res.append(p2)
					if p2 == endP:
						return res
				elif nextP == p2 and p1 not in res:
					res.append(p1)
					if p1 == endP:
						return res
			#print "(seq = %s) (len = %s) res = %s\n\n" % (nb, len(res), res)
	return res
	
#-----------------------------------------------------------------------
# geometry (math) functions
#-----------------------------------------------------------------------

def closeEnough(v1, v2):
	return (v2-v1).length()<0.0001
	'''
	if (v2-v1).length()<0.0001:
		return True
	return False
	'''
	
def sameSide(p1,p2,A,B):
	cp1 = (B-A).cross(p1-A)
	cp2 = (B-A).cross(p2-A)
	if cp1.dot(cp2)>= 0: return True
	return False

def pointInTriangle(p,A,B,C):
	if sameSide(p,A,B,C) and sameSide(p,B,A,C) and sameSide(p,C,A,B):
		vecNorm = (A-B).cross(A-C)
		if (p-A).dot(vecNorm)< 0.0001:
			return True
	return False

def isAnEar(A, B, C, restOfPointsList):
	for point in restOfPointsList:
		if pointInTriangle(point, A, B, C):
			return False
	return True

def angleBetween(A, B):
	A.normalize()
	B.normalize()
	cosAngle = A.dot(B)
	angle = math.acos(cosAngle)
	return angle*180/math.pi
	
def checkCounterClockWise(A, B, C, normalVec):
	# this is not perfect
	p = normalVec.dot(A.cross(B) + B.cross(C) + C.cross(A))
	if p>0.0:
		return True
	return False
	'''
	# this works even worse
	print "checking counterclockwise for A = %s , B = %s , C = %s" % (A, B, C)
	v1 = B-A
	v2 = C-A
	v = v1.cross(v2)
	print normalVec
	nv = Vec3(normalVec[0], normalVec[1], normalVec[2])
	if angleBetween(nv, v)<90:
		return True
	return False
	'''
		
#-----------------------------------------------------------------------
# Geom data functions
#-----------------------------------------------------------------------

def getGeomData(geomNode, scale=1):
	"""
	returns a dict : data = {"prims":[], "vertices" : [], "normals" : [], "texcoords" : []}
	with the data found inside the GeomNode's Geom's GeomPrimitive
	"""
	if not geomNode:
		return None
	
	data = {"prims":[], "vertices" : [], "normals" : [], "texcoords" : []}
	
	if geomNode.getNumGeoms()!=1:
		print "error : num geoms = %s" % (geomNode.getNumGeoms())
		return None
	
	geom = geomNode.getGeom(0)
	prim = geom.getPrimitive(0)
	prims = {}
	
	#print "before decompose : prim = %s" % (prim)
	prim = prim.decompose()
	#print "after decompose : prim = %s" % (prim)
	for p in range(prim.getNumPrimitives()):
		s = prim.getPrimitiveStart(p)
		e = prim.getPrimitiveEnd(p)
		vertexList = []
		#print "adding vertices from %s to %s" % (s, e)
		for i in range(s, e):
			'''
			vi = prim.getVertex(i)
			vreader.setRow(vi)
			v = vreader.getData3f()
			v = VBase3(v[0]*scale, v[1]*scale, v[2]*scale)
			vertexList.append(v)
			'''
			vi = prim.getVertex(i)
			vertexList.append(vi)
		prims[p]=vertexList
		data["prims"].append(vertexList)
	
	vdata = geom.getVertexData()
	vreader = GeomVertexReader(vdata, 'vertex')
	nvreader = GeomVertexReader(vdata, 'normal')
	tvreader = GeomVertexReader(vdata, 'texcoord')
	
	while not vreader.isAtEnd():
		v = vreader.getData3f()
		n = nvreader.getData3f()
		t = tvreader.getData2f()
		data["vertices"].append(v)
		data["normals"].append(n)
		data["texcoords"].append(t)
		
	return data

def getTriangulatorGeomData(pointList, normalVec):
	"""
	takes a list of points and a normal vector,
	gets the corresponding triangulated polygon,
	returns a dict with the data of that triangulated polygon :
	data = {"prims":[], "vertices" : [], "normals" : [], "texcoords" : []}
	"""
	data = {"prims":[], "vertices" : [], "normals" : [], "texcoords" : []}
	#prim = GeomTriangles(Geom.UHStatic)
	trig = Triangulator()
	#vdata = GeomVertexData('trig', GeomVertexFormat.getV3n3c4t2(), Geom.UHStatic)
	#vwriter = GeomVertexWriter(vdata, 'vertex')
	#nvwriter = GeomVertexWriter(vdata, 'normal')
	#tvwriter = GeomVertexWriter(vdata, 'texcoord')
	
	for x, y, z in pointList:
		vi = trig.addVertex(x, y)
		#vwriter.addData3f(x, y, z)
		data["vertices"].append(Point3(x, y, z))
		#nvwriter.addData3f(normalVec)
		data["normals"].append(normalVec)
		#tvwriter.addData2f(x,y)
		data["texcoords"].append(Point2(x, y))
		trig.addPolygonVertex(vi)
		#print "added vertex vi = %s" % (vi)
	try:
		trig.triangulate()
	except:
		return None
	
	#prim = GeomTriangles(Geom.UHStatic)
	for i in range(trig.getNumTriangles()):
		A, B, C = trig.getTriangleV0(i), trig.getTriangleV1(i), trig.getTriangleV2(i)
		#print "triangle %s : %s, %s, %s" % (i, A, B, C)
		
		
		if normalVec[2]<0:
			#prim.addVertices(A, B, C)
			data["prims"].append((A, B, C))
		else:
			#prim.addVertices(A, C, B)
			data["prims"].append((A, C, B))
		
		
		#prim.closePrimitive()
	
	return data

def reverseCapData(data):
	for i in range(len(data["prims"])):
		prim = data["prims"][i]
		data["prims"][i] = (prim[0], prim[2], prim[1])
	for i in range(len(data["normals"])):
		n = data["normals"][i]
		data["normals"][i] = -n
	return data
	
#-----------------------------------------------------------------------
# MeshHandler
#-----------------------------------------------------------------------

class MeshHandler(object):
	def __init__(self, game):
		"""
		MeshHandler init needs a "game" instance to be able to
		use that ShowBase's render and loader.loadModel
		"""
		self.game = game
		self.vListAbove = [] # list of vertices indexes for the ones that are above the last self.plane set
		self.vListBehind = []
		self.modelPath = None
		self.np = None
		self.texture = None
		self.planeNormal = None
		self.planePoint = None
	
	#-------------------------------------------------------------------
	# load model
	def setModelPath(self, modelPath):
		self.modelPath = modelPath
		self.np = self.game.loader.loadModel(self.modelPath)
		#self.np.reparentTo(self.game.render)
		self.vertices = []
		self.normals = []
		self.texcoords = []
		
		self.texture = self.np.findAllTextures().getTexture(0)
		self.getModelPrims()
		self.processVertexData()
	
	def setModel(self, model):
		self.np = model
		#self.np.reparentTo(self.game.render)
		self.vertices = []
		self.normals = []
		self.texcoords = []
		
		self.texture = self.np.findAllTextures().getTexture(0)
		self.getModelPrims()
		self.processVertexData()

	#-------------------------------------------------------------------
	# make self.prims when self.np is a model
	# dict of primitive indexes -> vertices index (v1, v2, v3)
	def getModelPrims(self, scale=1):
		if self.np.findAllMatches('**/+GeomNode'):
			geomNode = self.np.findAllMatches('**/+GeomNode')[0].node()
		else:
			geomNode = self.np.getNode(0)
		geom = geomNode.getGeom(0)
		self.vdata = geom.getVertexData()
		primList = getGeomData(geomNode)["prims"]
		self.prims = {}
		for i in range(len(primList)):
			self.prims[i] = primList[i]

	#-------------------------------------------------------------------
	# self.vertices, self.normals, self.texcoords
	# lists holding the current model's data
	def processVertexData(self):
		vreader = GeomVertexReader(self.vdata, 'vertex')
		nvreader = GeomVertexReader(self.vdata, 'normal')
		tvreader = GeomVertexReader(self.vdata, 'texcoord')
		while not vreader.isAtEnd():
			v = vreader.getData3f()
			n = nvreader.getData3f()
			t = tvreader.getData2f()
			self.vertices.append(v)
			self.normals.append(n)
			self.texcoords.append(t)
	
	#-------------------------------------------------------------------
	# Slicing functions
	#-------------------------------------------------------------------
	
	def setPlane(self, plane):
		if not self.np:
			print "WARNING : can't set plane without a NodePath to cut"
			return False
		self.plane = plane
		planeNormal = plane.getNormal()
		planePoint = plane.getPoint()
		
		# convert the point and normal of the plane
		# to the local object coordinates system
		self.planeNormal = self.np.getRelativeVector(self.game.render, planeNormal)
		self.planePoint = self.np.getRelativePoint(self.game.render, planePoint)
		
	
	def getVerticesAboveBehindLists(self, plane):
		if not self.np:
			return None
		
		self.setPlane(plane)
		
		self.vListAbove = []
		self.vListBehind = []
		
		# get the list of indices of the vertices that are either
		# completely above the cut, on the cut, or completely behind the cut
		for n, vertex in enumerate(self.vertices):
			v = vertex - self.planePoint
			if angleBetween(v, self.planeNormal)<90:
				self.vListAbove.append(n)
			else:
				self.vListBehind.append(n)
		
		# get the list of indices of the prims that are either
		# completely above the cut, on the cut, or completely behind the cut
		self.tAbove = []
		self.tCut = []
		self.tBehind = []
		for triIndex, vIndex in self.prims.items():
			if vIndex[0] in self.vListAbove and vIndex[1] in self.vListAbove and vIndex[2] in self.vListAbove:
				self.tAbove.append(triIndex)
			elif vIndex[0] in self.vListBehind and vIndex[1] in self.vListBehind and vIndex[2] in self.vListBehind:
				self.tBehind.append(triIndex)
			else:
				self.tCut.append(triIndex)
	
	# some shortcut functions
	def addAboveVData(self, V, N, T):
		self.dataAbove["vertices"].append(V)
		self.dataAbove["normals"].append(N)
		self.dataAbove["texcoords"].append(T)
		
	def addAbovePrim(self, v1, v2, v3):
		self.dataAbove["prims"].append((v1, v2, v3))
	
	def addBehindVData(self, V, N, T):
		self.dataBehind["vertices"].append(V)
		self.dataBehind["normals"].append(N)
		self.dataBehind["texcoords"].append(T)
		
	def addBehindPrim(self, v1, v2, v3):
		self.dataBehind["prims"].append((v1, v2, v3))
	
	# self.dataAbove initial filling (with only prims fully above the cut)
	def getPrimsAbove(self):
		self.dataAbove = {"prims" : [], "vertices" : [], "normals" : [], "texcoords" : []}
		for triIndex in self.tAbove:
			primIndex = len(self.dataAbove["vertices"])
			for vIndex in self.prims[triIndex]:
				v = self.vertices[vIndex]
				n = self.normals[vIndex]
				t = self.texcoords[vIndex]
				self.addAboveVData(v, n, t)
			self.addAbovePrim(primIndex, primIndex+1, primIndex+2)
	
	# self.dataBehind initial filling (with only prims fully behind the cut)
	def getPrimsBehind(self):
		self.dataBehind = {"prims" : [], "vertices" : [], "normals" : [], "texcoords" : []}
		for triIndex in self.tBehind:
			primIndex = len(self.dataBehind["vertices"])
			for vIndex in self.prims[triIndex]:
				v = self.vertices[vIndex]
				n = self.normals[vIndex]
				t = self.texcoords[vIndex]
				self.addBehindVData(v, n, t)
			self.addBehindPrim(primIndex, primIndex+1, primIndex+2)
	
	
	def fillCutPrimAbove(self, p1, p2, p3, R1, R2, NR1, NR2, TR1, TR2):
		P1 = self.vertices[p1]
		P2 = self.vertices[p2]
		P3 = self.vertices[p3]
			
		N1 = self.normals[p1]
		N2 = self.normals[p2]
		N3 = self.normals[p3]
			
		T1 = self.texcoords[p1]
		T2 = self.texcoords[p2]
		T3 = self.texcoords[p3]
		
		if p1 in self.vListAbove:
			primIndex = len(self.dataAbove["vertices"])
			if checkCounterClockWise(P1, R1, R2, N1):
				self.addAboveVData(P1, N1, T1)
				self.addAboveVData(R1, N1, TR1)
				self.addAboveVData(R2, N1, TR2)
			else:
				self.addAboveVData(P1, N1, T1)
				self.addAboveVData(R2, N1, TR2)
				self.addAboveVData(R1, N1, TR1)
			self.addAbovePrim(primIndex, primIndex+1, primIndex+2)
		
		else:
			if checkCounterClockWise(P2, R1, R2, N1) and checkCounterClockWise(P2, R2, P3, N1):
				primIndex = len(self.dataAbove["vertices"])
				self.addAboveVData(P2, N2, T2)
				self.addAboveVData(R1, N2, TR1)
				self.addAboveVData(R2, N2, TR2)
				self.addAbovePrim(primIndex, primIndex+1, primIndex+2)
				
				primIndex = len(self.dataAbove["vertices"])
				self.addAboveVData(P2, N2, T2)
				self.addAboveVData(R2, N2, TR2)
				self.addAboveVData(P3, N3, T3)
				self.addAbovePrim(primIndex, primIndex+1, primIndex+2)
			
			elif checkCounterClockWise(P2, R2, R1, N1) and checkCounterClockWise(P2, R1, P3, N1):
				primIndex = len(self.dataAbove["vertices"])
				self.addAboveVData(P2, N2, T2)
				self.addAboveVData(R2, N2, TR2)
				self.addAboveVData(R1, N2, TR1)
				self.addAbovePrim(primIndex, primIndex+1, primIndex+2)
				
				primIndex = len(self.dataAbove["vertices"])
				self.addAboveVData(P2, N2, T2)
				self.addAboveVData(R1, N2, TR1)
				self.addAboveVData(P3, N3, T3)
				self.addAbovePrim(primIndex, primIndex+1, primIndex+2)
			
			elif checkCounterClockWise(P3, R1, R2, N1) and checkCounterClockWise(P3, R2, P2, N1):
				primIndex = len(self.dataAbove["vertices"])
				self.addAboveVData(P3, N3, T3)
				self.addAboveVData(R1, N2, TR1)
				self.addAboveVData(R2, N2, TR2)
				self.addAbovePrim(primIndex, primIndex+1, primIndex+2)
				
				primIndex = len(self.dataAbove["vertices"])
				self.addAboveVData(P3, N3, T3)
				self.addAboveVData(R2, N2, TR2)
				self.addAboveVData(P2, N2, T2)
				self.addAbovePrim(primIndex, primIndex+1, primIndex+2)
			
			elif checkCounterClockWise(P3, R2, R1, N1) and checkCounterClockWise(P3, R1, P2, N1):
				primIndex = len(self.dataAbove["vertices"])
				self.addAboveVData(P3, N3, T3)
				self.addAboveVData(R2, N2, TR2)
				self.addAboveVData(R1, N1, TR1)
				self.addAbovePrim(primIndex, primIndex+1, primIndex+2)
				
				primIndex = len(self.dataAbove["vertices"])
				self.addAboveVData(P3, N3, T3)
				self.addAboveVData(R1, N2, TR1)
				self.addAboveVData(P2, N2, T2)
				self.addAbovePrim(primIndex, primIndex+1, primIndex+2)
	
	def fillCutPrimBehind(self, p1, p2, p3, R1, R2, NR1, NR2, TR1, TR2):
		P1 = self.vertices[p1]
		P2 = self.vertices[p2]
		P3 = self.vertices[p3]
			
		N1 = self.normals[p1]
		N2 = self.normals[p2]
		N3 = self.normals[p3]
			
		T1 = self.texcoords[p1]
		T2 = self.texcoords[p2]
		T3 = self.texcoords[p3]
		
		if p1 in self.vListBehind:
			primIndex = len(self.dataBehind["vertices"])
			if checkCounterClockWise(P1, R1, R2, N1):
				self.addBehindVData(P1, N1, T1)
				self.addBehindVData(R1, N1, TR1)
				self.addBehindVData(R2, N1, TR2)
			else:
				self.addBehindVData(P1, N1, T1)
				self.addBehindVData(R2, N1, TR2)
				self.addBehindVData(R1, N1, TR1)
			self.addBehindPrim(primIndex, primIndex+1, primIndex+2)
		
		else:
			if checkCounterClockWise(P2, R1, R2, N1) and checkCounterClockWise(P2, R2, P3, N1):
				primIndex = len(self.dataBehind["vertices"])
				self.addBehindVData(P2, N2, T2)
				self.addBehindVData(R1, N2, TR1)
				self.addBehindVData(R2, N2, TR2)
				self.addBehindPrim(primIndex, primIndex+1, primIndex+2)
				
				primIndex = len(self.dataBehind["vertices"])
				self.addBehindVData(P2, N2, T2)
				self.addBehindVData(R2, N2, TR2)
				self.addBehindVData(P3, N3, T3)
				self.addBehindPrim(primIndex, primIndex+1, primIndex+2)
			
			elif checkCounterClockWise(P2, R2, R1, N1) and checkCounterClockWise(P2, R1, P3, N1):
				primIndex = len(self.dataBehind["vertices"])
				self.addBehindVData(P2, N2, T2)
				self.addBehindVData(R2, N2, TR2)
				self.addBehindVData(R1, N2, TR1)
				self.addBehindPrim(primIndex, primIndex+1, primIndex+2)
				
				primIndex = len(self.dataBehind["vertices"])
				self.addBehindVData(P2, N2, T2)
				self.addBehindVData(R1, N2, TR1)
				self.addBehindVData(P3, N3, T3)
				self.addBehindPrim(primIndex, primIndex+1, primIndex+2)
			
			elif checkCounterClockWise(P3, R1, R2, N1) and checkCounterClockWise(P3, R2, P2, N1):
				primIndex = len(self.dataBehind["vertices"])
				self.addBehindVData(P3, N3, T3)
				self.addBehindVData(R1, N2, TR1)
				self.addBehindVData(R2, N2, TR2)
				self.addBehindPrim(primIndex, primIndex+1, primIndex+2)
				
				primIndex = len(self.dataBehind["vertices"])
				self.addBehindVData(P3, N3, T3)
				self.addBehindVData(R2, N2, TR2)
				self.addBehindVData(P2, N2, T2)
				self.addBehindPrim(primIndex, primIndex+1, primIndex+2)
			
			elif checkCounterClockWise(P3, R2, R1, N1) and checkCounterClockWise(P3, R1, P2, N1):
				primIndex = len(self.dataBehind["vertices"])
				self.addBehindVData(P3, N3, T3)
				self.addBehindVData(R2, N2, TR2)
				self.addBehindVData(R1, N1, TR1)
				self.addBehindPrim(primIndex, primIndex+1, primIndex+2)
				
				primIndex = len(self.dataBehind["vertices"])
				self.addBehindVData(P3, N3, T3)
				self.addBehindVData(R1, N2, TR1)
				self.addBehindVData(P2, N2, T2)
				self.addBehindPrim(primIndex, primIndex+1, primIndex+2)
	
	def mergeDataAbove(self, data):
		for index1, index2, index3 in data["prims"]:
			primIndex = len(self.dataAbove["vertices"])
			v = data["vertices"][index1]
			n = data["normals"][index1]
			t = data["texcoords"][index1]
			v2 = data["vertices"][index2]
			n2 = data["normals"][index2]
			t2 = data["texcoords"][index2]
			v3 = data["vertices"][index3]
			n3 = data["normals"][index3]
			t3 = data["texcoords"][index3]
			
			self.addAboveVData(v, n, t)
			self.addAboveVData(v2, n2, t2)
			self.addAboveVData(v3, n3, t3)
			self.addAbovePrim(primIndex, primIndex+1, primIndex+2)
	
	def mergeDataBehind(self, data):
		for index1, index2, index3 in data["prims"]:
			primIndex = len(self.dataBehind["vertices"])
			v = data["vertices"][index1]
			n = data["normals"][index1]
			t = data["texcoords"][index1]
			v2 = data["vertices"][index2]
			n2 = data["normals"][index2]
			t2 = data["texcoords"][index2]
			v3 = data["vertices"][index3]
			n3 = data["normals"][index3]
			t3 = data["texcoords"][index3]
			
			self.addBehindVData(v, n, t)
			self.addBehindVData(v2, n2, t2)
			self.addBehindVData(v3, n3, t3)
			self.addBehindPrim(primIndex, primIndex+1, primIndex+2)
	
	def getCutMeshData(self, plane):
		if not self.np:
			return None
		
		# prepare cutting
		self.getVerticesAboveBehindLists(plane)
		
		if len(self.vListAbove)==0 or len(self.vListBehind)==0:
			return None
		
		# add the prims that are completely above the cut
		self.getPrimsAbove()
		
		# add the prims that are completely behind the cut
		self.getPrimsBehind()
		
		# self.intersectPointList : list of intersection points of the cut plane
		# resSeg : list of pairs of close intersection points
		self.intersectPointList = []
		resSeg = []
		
		#for triIndex in self.getTrianglesCut():
		for triIndex in self.tCut:
			v1, v2, v3 = self.prims[triIndex]
			# find the point p1 that is alone on his side of the cut
			# (it's common to both intersections with the triangle prim)
			if ((v1 in self.vListAbove) and (v2 in self.vListAbove)) or ((v1 in self.vListBehind) and (v2 in self.vListBehind)):
				p1 = v3
				p2 = v1
				p3 = v2
			elif ((v3 in self.vListAbove) and (v2 in self.vListAbove)) or ((v3 in self.vListBehind) and (v2 in self.vListBehind)):
				p1 = v1
				p2 = v2
				p3 = v3
			else:
				p1 = v2
				p2 = v1
				p3 = v3
			
			P1 = self.vertices[p1]
			P2 = self.vertices[p2]
			P3 = self.vertices[p3]
			
			N1 = self.normals[p1]
			N2 = self.normals[p2]
			N3 = self.normals[p3]
			
			T1 = self.texcoords[p1]
			T2 = self.texcoords[p2]
			T3 = self.texcoords[p3]
			
			# find the two intersection points, calculate their normals and texcoords
			
			r1 = self.planeNormal.dot(self.planePoint - P1) / self.planeNormal.dot(P2-P1)
			r2 = self.planeNormal.dot(self.planePoint - P1) / self.planeNormal.dot(P3-P1)
			
			
			R1 = P1 + (P2-P1)*r1
			R2 = P1 + (P3-P1)*r2
			NR1 = N1
			NR2 = N2
			TR1 = T1*(1-r1)+T2*r1
			TR2 = T1*(1-r2)+T3*r2
			
			# remove possible "doubles",
			# which is the reason we use self.intersectPointList
			for p in self.intersectPointList:
				if closeEnough(p, R1):
					R1 = p
				if closeEnough(p, R2):
					R2 = p
			# append the intersection points as pairs of close ones
			# to be able to get the order of the points for the triangulation
			resSeg.append((R1, R2))
			
			self.intersectPointList.append(R1)
			self.intersectPointList.append(R2)
			
			# fill the data corresponding to the new triangles generated
			# by the cut
			self.fillCutPrimAbove(p1, p2, p3, R1, R2, NR1, NR2, TR1, TR2)
			self.fillCutPrimBehind(p1, p2, p3, R1, R2, NR1, NR2, TR1, TR2)
			
		self.intersectPointList = orderPointsFromPairs(resSeg)
		if not self.intersectPointList:
			return None
		
		#---------------------------------------------------------------
		# Triangulation
		data = getTriangulatorGeomData(self.intersectPointList, self.planeNormal)
		self.mergeDataAbove(data)
		
		data2 = reverseCapData(data)
		self.mergeDataBehind(data2)
		
		return self.dataAbove, self.dataBehind
	
	def getCutGeoms(self, plane):
		data = self.getCutMeshData(plane)
		if not data:
			return None
		dataAbove, dataBehind = data[0], data[1]
		geomAbove = self.buildGeom(dataAbove)
		geomBehind = self.buildGeom(dataBehind)
		return geomAbove, geomBehind
	
	def getCutNp(self, plane):
		data = self.getCutGeoms(plane)
		if not data:
			return None
		geom1, geom2 = data[0], data[1]
		return self.makeNpFromGeom(geom1), self.makeNpFromGeom(geom2)
	
	def makeNpFromGeom(self, geom):
		np = NodePath(geom)
		np.setTexture(self.texture)
		return np

	def buildGeom(self, meshData):
		prims = meshData["prims"]
		vertices = meshData["vertices"]
		normals = meshData["normals"]
		texcoords = meshData["texcoords"]
		
		vdata = GeomVertexData('mesh', GeomVertexFormat.getV3n3t2(), Geom.UHStatic)
		vwriter = GeomVertexWriter(vdata, 'vertex')
		nvwriter = GeomVertexWriter(vdata, 'normal')
		tvwriter = GeomVertexWriter(vdata, 'texcoord')
		
		for i in range(len(vertices)):
			v = vertices[i]
			n = normals[i]
			t = texcoords[i]
			vwriter.addData3f(v)
			nvwriter.addData3f(n)
			tvwriter.addData2f(t)
		
		prim = GeomTriangles(Geom.UHStatic)
		
		for i in range(len(prims)):
			A, B, C = prims[i]
			prim.addVertices(A, B, C)
			prim.closePrimitive()
		
		geom = Geom(vdata)
		geom.addPrimitive(prim)
		
		geomNode = GeomNode('trig')
		geomNode.addGeom(geom)
		geomNode.unify(1, True)
		
		return geomNode
		

#-----------------------------------------------------------------------
# Game
#-----------------------------------------------------------------------
class Game(ShowBase):
	def __init__(self):
		ShowBase.__init__(self)
		self.setBackgroundColor(0.2,0.2,0.2)
		self.accept("escape", self.taskMgr.stop)
		#self.accept("mouse1", self.onClick)
		#self.accept("mouse2", self.onClick2)
		self.globalClock = ClockObject()
		
		self.addLight()
		
		self.liner = LineDrawer(self)
		
		self.taskMgr.add(self.update, "update")
		
	def update(self, task):
		self.globalClock.tick()
		t = self.globalClock.getFrameTime()
		#print t
		dt = self.globalClock.getDt()
		
		return task.cont
	
	def addLight(self):
		self.render.clearLight()
		self.lightCenter = self.render.attachNewNode(PandaNode("center"))
		#self.lightCenter.setCompass()
		
		# ambient light
		self.ambientLight = AmbientLight('ambientLight')
		self.ambientLight.setColor(Vec4(0.5,0.5,0.5, 1))
		self.alight = self.lightCenter.attachNewNode(self.ambientLight)
		self.render.setLight(self.alight)
		
		# point light
		self.pointlight = PointLight("pLight")
		self.light = self.lightCenter.attachNewNode(self.pointlight)
		self.pointlight.setColor(Vec4(0.8,0.8,0.8,1))
		self.light.setPos(0,0,2)
		self.render.setLight(self.light)
		
		# directional light
		self.dirlight = DirectionalLight("dLight")
		self.dlight = self.lightCenter.attachNewNode(self.dirlight)
		self.dirlight.setColor(Vec4(0.8,0.8,0.8,1))
		self.dirlight.setShadowCaster(True)
		
		self.dlight.setPos(0,0,5)
		self.dlight.lookAt(5,10,0)
		self.render.setLight(self.dlight)
		
		self.render.setShaderAuto()
		



if __name__ == "__main__":
	g = Game()
	p = Plane(Vec3(0.5,0.0,-1), Point3(0,0,1.2))
	base = g.loader.loadModel("models/bulb.egg")
	base.reparentTo(g.render)
	base.setPos(3.5,3.8,-2)
	
	g.globalClock.tick()
	t0 = g.globalClock.getFrameTime()
	
	m = MeshHandler(g)
	m.setModelPath("models/bulb.egg")
	np1, np2 = m.getCutNp(p)
	np1.reparentTo(g.render)
	np2.reparentTo(g.render)
	np1.setPos(-5,1,-1)
	np2.setPos(-5,1,0)
	
	g.globalClock.tick()
	print "Total Slicing done in %s s" % (g.globalClock.getFrameTime()-t0)
	
	g.run()
	
