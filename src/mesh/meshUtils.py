#!/usr/bin/python
# -*- coding: utf8 -*-

import random

from panda3d.core import Point2, Point3, Vec3, Vec4, VBase4, NodePath
from panda3d.core import Triangulator
from panda3d.core import GeomVertexArrayFormat, GeomVertexFormat, GeomVertexData, InternalName
from panda3d.core import GeomVertexReader, GeomVertexWriter, Geom, GeomNode
from panda3d.core import GeomLinestrips, GeomTriangles, GeomTristrips, GeomTrifans

from panda3d.core import Material, Texture, TextureStage

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

def getOdds(l):
	newList = []
	for i in range(len(l)):
		if i % 2:
			newList.append(l[i])
	return newList

def getEvens(l):
	newList = []
	for i in range(len(l)):
		if (i % 2) == 0:
			newList.append(l[i])
	return newList

#-----------------------------------------------------------------------
# geometry (math) functions
#-----------------------------------------------------------------------

def closeEnough(v1, v2):
	return (v2-v1).length()<0.0001
	
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
def getIntersection4Points(p1, p2, p3, p4):
	x1, y1 = p1.getX(), p1.getY()
	x2, y2 = p2.getX(), p2.getY()
	x3, y3 = p3.getX(), p3.getY()
	x4, y4 = p4.getX(), p4.getY()
	
	denom = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
	if denom == 0:
		print "Error : parallel lines?"
		return None
	
	ua = ( (x4 - x3)*(y1 - y3) - (y4 - y3)*(x1 - x3) ) / denom
	#ub = ( (x2 - x1)*(y1 - y3) - (y2 - y1)*(x1 - x3) ) / denom
	x = x1 + ua * (x2 - x1)
	y = y1 + ua * (y2 - y1)
	return (x, y)

def translatePoint(p, vec):
	try:
		vec = float(vec)
		vec = Point3(0,0,vec)
	except:
		vec = Point3(vec)
	p = p + vec
	return p
	
def translatePoints(pList, vec):
	newList = []
	for p in pList:
		newList.append(translatePoint(p, vec))
	return newList

def rotatePoint(p, hpr, basePoint=Point3(0,0,0)):
	try:
		hpr = float(hpr)
		hpr = (hpr, 0, 0)
	except:
		pass
	n0 = NodePath("tempRotator0")
	n0.setPos(basePoint)
	n = NodePath("tempRotator")
	n.setHpr(hpr)
	return n.getRelativePoint(n0, p)

def rotatePoints(pList, angle, basePoint=Point3(0,0,0)):
	newList = []
	for p in pList:
		newList.append(rotatePoint(p, angle, basePoint))
	return newList

def scalePoint(p, scaleVec):
	#if type(scaleVec) is float or type(scaleVec) is int:
		#scaleVec = Vec3(scaleVec, scaleVec, scaleVec)
	try:
		scaleVec = float(scaleVec)
		scaleVec = (scaleVec, scaleVec, scaleVec)
	except:
		pass
	
	resP = Point3()
	resP.setX(p.getX() * scaleVec[0])
	resP.setY(p.getY() * scaleVec[1])
	resP.setZ(p.getZ() * scaleVec[2])
	return resP

def getCirclePoints(centerP, radius, normalVec, nbSides, angleStart = 0.0, angleEnd = 360.0):
	nCenter = NodePath("center")
	n0 = NodePath("tempRotator0")
	n1 = NodePath("tempRotator1")
	n2 = NodePath("tempRotator2")
	
	n0.setPos(centerP)
	n1.setPos(centerP + normalVec)
	
	n0.lookAt(n1)
	n2.reparentTo(n0)
	n2.setPos(0, 0, radius)
	dAngle = float(angleEnd-angleStart) / nbSides
	res = []
	for i in range(nbSides+1):
		n0.setR(angleStart + i*dAngle)
		res.append(n2.getPos(nCenter))
	return res
	
#-----------------------------------------------------------------------
# Triangulator
# horizontal triangulation helper function
# to make the buildings' roof, levels' floor, etc.
#-----------------------------------------------------------------------
def getTriangulatorGeomData(pointList, normalVec, texScale=(1,1), color=(1,1,1,1)):
	"""
	takes a list of points and a normal vector,
	gets the corresponding triangulated polygon,
	returns a dict with the data of that triangulated polygon :
	data = {"prims":[], "vertices" : [], "normals" : [], "texcoords" : []}
	"""
	data = {"prims":[], "vertices" : [], "normals" : [], "texcoords" : [], "colors" : []}
	normalVec = Vec3(normalVec)
	normalVec.normalize()
	u, v = texScale
	trig = Triangulator()
	
	for x, y, z in pointList:
		if normalVec[2]>0:
			vi = trig.addVertex(x, y)
			data["texcoords"].append(Point2(x*u, y*u))
		elif normalVec[1]>0:
			vi = trig.addVertex(x, z)
			data["texcoords"].append(Point2(x*u, z*u))
		else:
			vi = trig.addVertex(y, z)
			data["texcoords"].append(Point2(y*u, z*u))
		data["vertices"].append(Point3(x, y, z))
		data["normals"].append(normalVec)
		data["colors"].append(color)
		trig.addPolygonVertex(vi)
	
	trig.triangulate()
	
	for i in xrange(trig.getNumTriangles()):
		A, B, C = trig.getTriangleV0(i), trig.getTriangleV1(i), trig.getTriangleV2(i)
		data["prims"].append((A, B, C))
		#if normalVec[2]>0:
		#	data["prims"].append((A, B, C))
		#else:
		#	data["prims"].append((A, C, B))
		
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
# Wall points functions
#-----------------------------------------------------------------------
def getWallSidePoints(centerPoint, prevPoint = None, nextPoint = None, thickness = 1.0):
	if prevPoint == None and nextPoint == None:
		print "Error : at least one more point is needed"
		return None
	
	z = centerPoint.getZ()
	
	if prevPoint == None:
		dy = nextPoint - centerPoint
		dy.setZ(0)
		dy.normalize()
		dx = dy.cross(Vec3(0,0,1))
		rPoint = centerPoint + dx * (thickness/2.0)
		lPoint = centerPoint - dx * (thickness/2.0)
	elif nextPoint == None:
		dy = centerPoint - prevPoint
		dy.setZ(0)
		dy.normalize()
		dx = dy.cross(Vec3(0,0,1))
		rPoint = centerPoint + dx * (thickness/2.0)
		lPoint = centerPoint - dx * (thickness/2.0)
	else:
		dyPrev = centerPoint - prevPoint
		dyPrev.setZ(0)
		dyPrev.normalize()
		dxPrev = dyPrev.cross(Vec3(0,0,1))
		rPrevPoint = prevPoint + dxPrev * (thickness/2.0)
		lPrevPoint = prevPoint - dxPrev * (thickness/2.0)
		
		dyNext = centerPoint - nextPoint
		dyNext.setZ(0)
		dyNext.normalize()
		dxNext = dyNext.cross(Vec3(0,0,1))
		rNextPoint = nextPoint + dxNext * (thickness/2.0)
		lNextPoint = nextPoint - dxNext * (thickness/2.0)
		
		# right side
		p1 = rPrevPoint
		p2 = rPrevPoint + dyPrev
		p3 = lNextPoint
		p4 = lNextPoint + dyNext
		x1, y1 = p1.getX(), p1.getY()
		x2, y2 = p2.getX(), p2.getY()
		x3, y3 = p3.getX(), p3.getY()
		x4, y4 = p4.getX(), p4.getY()
		
		denom = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
		if denom == 0:
			print "Error : parallel walls?"
			return centerPoint + dxPrev * (thickness/2.0), centerPoint - dxPrev * (thickness/2.0)
			#return None
		ua = ( (x4 - x3)*(y1 - y3) - (y4 - y3)*(x1 - x3) ) / denom
		#ub = ( (x2 - x1)*(y1 - y3) - (y2 - y1)*(x1 - x3) ) / denom
		x = x1 + ua * (x2 - x1)
		y = y1 + ua * (y2 - y1)
		rPoint = Point3(x, y, centerPoint.getZ())
		
		# left side
		p1 = lPrevPoint
		p2 = lPrevPoint + dyPrev
		p3 = rNextPoint
		p4 = rNextPoint + dyNext
		x1, y1 = p1.getX(), p1.getY()
		x2, y2 = p2.getX(), p2.getY()
		x3, y3 = p3.getX(), p3.getY()
		x4, y4 = p4.getX(), p4.getY()
		
		denom = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
		if denom == 0:
			print "Error : parallel walls?"
			return centerPoint + dxPrev * (thickness/2.0), centerPoint - dxPrev * (thickness/2.0)
			return None
		ua = ( (x4 - x3)*(y1 - y3) - (y4 - y3)*(x1 - x3) ) / denom
		#ub = ( (x2 - x1)*(y1 - y3) - (y2 - y1)*(x1 - x3) ) / denom
		x = x1 + ua * (x2 - x1)
		y = y1 + ua * (y2 - y1)
		lPoint = Point3(x, y, centerPoint.getZ())
	
	return rPoint, lPoint
	
#-----------------------------------------------------------------------	
def getWallPoints(pathPointList, thickness = 1.0, closed=False):
	nbPts = len(pathPointList)
	if nbPts<2:
		print "Error, no valid pointList for wall"
		return None
	if nbPts<3 and closed:
		print "Error : it takes at least 3 points to close"
		return None
	
	pointList = []
	rightPointList = []
	leftPointList = []
	
	for i, point in enumerate(pathPointList):
		prevPoint = None
		if i == 0 and closed:
			prevPoint = pathPointList[-1]
		if i > 0:
			prevPoint = pathPointList[i-1]
		
		nextPoint = None
		if i == nbPts - 1 and closed:
			nextPoint = pathPointList[0]
		if i < nbPts - 1:
			nextPoint = pathPointList[i+1]
		
		rPoint, lPoint = getWallSidePoints(point, prevPoint, nextPoint, thickness)
		rightPointList.append(rPoint)
		leftPointList.append(lPoint)
	#leftPointList.reverse()
	return rightPointList, leftPointList
	
def getPolygonInteriorPoints(pointList, dist):
	return getWallPoints(pointList, dist*2.0, True)[1]

def getPolygonExteriorPoints(pointList, dist):
	return getWallPoints(pointList, dist*2.0, True)[0]

#-----------------------------------------------------------------------
# Geom data functions
#-----------------------------------------------------------------------

def makeVertexFormat(color = True, normal = False, texcoord = False, tan_binorm = False):
	myArray = GeomVertexArrayFormat()
	myArray.addColumn(InternalName.make('vertex'), 3, Geom.NTFloat32, Geom.CPoint)
	if color:
		myArray.addColumn(InternalName.make('color'), 4, Geom.NTFloat32, Geom.CColor)
	if normal:
		myArray.addColumn(InternalName.make('normal'), 3, Geom.NTFloat32, Geom.CVector)
	if texcoord:
		myArray.addColumn(InternalName.make('texcoord'), 2, Geom.NTFloat32, Geom.CTexcoord)
	if tan_binorm:
		myArray.addColumn(InternalName.make('tangent'), 3, Geom.NTFloat32, Geom.CVector)
		myArray.addColumn(InternalName.make('binormal'), 3, Geom.NTFloat32, Geom.CVector)
	myFormat = GeomVertexFormat()
	myFormat.addArray(myArray)
	myFormat = GeomVertexFormat.registerFormat(myFormat)
	
	return myFormat

	
def getGeomData(geom=None):
	"""
	returns a dict : data = {"prims":[], "vertices" : [], "normals" : [], "texcoords" : []}
	with the data found inside the Geom's GeomPrimitive
	"""
	if not geom:
		return None
	
	data = {"vertices" : [], "normals" : [], "texcoords" : [], "colors" : [], "tangents":[], "binormals":[], "lines":[], "triangles":[], "tristrips":[], "trifans":[]}
	
	#prim = geom.getPrimitive(0)
	#prims = {}
	
	#print "before decompose : prim = %s" % (prim)
	#prim = prim.decompose()
	#print "after decompose : prim = %s" % (prim)
	
	for gPrim in geom.getPrimitives():
		for p in range(gPrim.getNumPrimitives()):
			s = gPrim.getPrimitiveStart(p)
			e = gPrim.getPrimitiveEnd(p)
			vertexList = []
			for i in range(s, e):
				vi = gPrim.getVertex(i)
				vertexList.append(vi)
			if type(gPrim) is  GeomLinestrips:
				data["lines"].append(vertexList)
			elif type(gPrim) is GeomTriangles:
				data["triangles"].append(vertexList)
			elif type(gPrim) is GeomTristrips:
				data["tristrips"].append(vertexList)
			elif type(gPrim) is GeomTrifans:
				data["trifans"].append(vertexList)
			
			#print "appended primitive number %s, type is %s" % (p, type(gPrim))
	
	vdata = geom.getVertexData()
	vreader = GeomVertexReader(vdata, 'vertex')
	nreader = GeomVertexReader(vdata, 'normal')
	treader = GeomVertexReader(vdata, 'texcoord')
	creader = GeomVertexReader(vdata, 'color')
	tanReader = GeomVertexReader(vdata, 'tangent')
	binReader = GeomVertexReader(vdata, 'binormal')
	
	while not vreader.isAtEnd():
		v = vreader.getData3f()
		n = nreader.getData3f()
		t = treader.getData2f()
		c = creader.getData4f()
		tangent = tanReader.getData3f()
		binormal = binReader.getData3f()
		
		data["vertices"].append(v)
		data["normals"].append(n)
		data["texcoords"].append(t)
		data["colors"].append(c)
		data["tangents"].append(tangent)
		data["binormals"].append(binormal)
		
	return data

#-----------------------------------------------------------------------
# random functions
#-----------------------------------------------------------------------
def getRandomBool():
	#return random.randint(0,1)
	return random.choice([0,1])
	
def getRandomColor():
	c1 = random.uniform(0,1)
	c2 = random.uniform(0,1)
	c3 = random.uniform(0,1)
	return (c1, c2, c3, 1)


#-----------------------------------------------------------------------
# render states functions
#-----------------------------------------------------------------------

def makeMaterial(ambient=(0,0,0,1), diffuse=(1,1,1,1), emission=(0.01,0.01,0.01,1), shininess=1, specular=(0.2,0.2,0.2,1)):
	m = Material()
	m.setAmbient(Vec4(ambient))
	m.setDiffuse(Vec4(diffuse))
	m.setEmission(Vec4(emission))
	m.setShininess(shininess)
	m.setSpecular(Vec4(specular))
	return m
	
def makeRenderState(material = None, diffuseTexture=None, normalTexture=None, glowTexture=None):
	n = NodePath("n")
	
	if not material:
		material = makeMaterial((0,0,0,1), (1,1,1,1), (0.01,0.01,0.01,1), 1, (1,1,1,1))
	
	n.setMaterial(material)
	
	if diffuseTexture:
		tsDiffuse = TextureStage('diffuse')
		tsDiffuse.setMode(TextureStage.MModulate)
		n.setTexture(tsDiffuse, diffuseTexture)
		
	if glowTexture:
		tsGlow = TextureStage('glow')
		tsGlow.setMode(TextureStage.MGlow)
		n.setTexture(tsGlow, glowTexture)
		
	if normalTexture:
		tsNormal = TextureStage('normal')
		tsNormal.setMode(TextureStage.MNormal)
		n.setTexture(tsNormal, normalTexture)
	
	# weird bugs :|
	#n.setTransparency(True)
	#n.setColorOff()
	return n.getState()
	

	
