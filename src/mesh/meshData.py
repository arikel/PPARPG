#!/usr/bin/python
# -*- coding: utf8 -*-

from meshUtils import *

#-----------------------------------------------------------------------
# 
#-----------------------------------------------------------------------
class MeshData(object):
	def __init__(self):
		self.clear()
		
	def clear(self):
		self.vertices = []
		self.normals = []
		self.texcoords = []
		self.colors = []
		
		self.tangents = []
		self.binormals = []
		
		#self.lines = []
		self.triangles = []
		self.tristrips = []
		self.trifans = []
		
	def addVertex(self, x, y, z):
		self.vertices.append([x, y, z])
		
	def addNormal(self, nx, ny, nz):
		self.normals.append([nx, ny, nz])
	
	def addTexcoord(self, u, v):
		self.texcoords.append([u, v])
			
	def addColor(self, c1=1, c2=1, c3=1, c4=1):
		self.colors.append([c1, c2, c3, c4])
		
	def addTangent(self, t1=1, t2=1, t3=1):
		self.tangents.append([t1, t2, t3])
		
	def addBinormal(self, b1=1, b2=1, b3=1):
		self.binormals.append([b1, b2, b3])
		
	def addVertexData(self, x, y, z, nx, ny, nz, u, v, c1=1, c2=1, c3=1, c4=1, t1=1, t2=1, t3=1, b1=1, b2=1, b3=1):
		self.addVertex(x, y, z)
		self.addNormal(nx, ny, nz)
		self.addTexcoord(u, v)
		self.addColor(c1, c2, c3, c4)
		self.addTangent(t1, t2, t3)
		self.addBinormal(b1, b2, b3)
		
	def getNbVertices(self):
		return len(self.vertices)
		
	nbVertices = property(getNbVertices)
	
	#def addLine(self, pointIndexList):
	#	self.lines.append(pointIndexList)
		
	def addTriangle(self, pIndex1, pIndex2, pIndex3):
		self.triangles.append((pIndex1, pIndex2, pIndex3))
		
	def addTristrip(self, pointIndexList):
		self.tristrips.append(pointIndexList)
	
	def addTrifan(self, pointIndexList):
		self.trifans.append(pointIndexList)
	
	def mergeMeshData(self, meshData):
		n = self.nbVertices
		
		if meshData is self:
			#meshData = MeshData()
			#meshData.mergeMeshData(self)
			return
		
		for atr in ("vertices", "normals", "texcoords", "colors", "tangents", "binormals"):
			print "extending %s" % (atr)
			getattr(self, atr).extend(getattr(meshData, atr))
		
		for tri in meshData.triangles:
			newTri = []
			for vIndex in tri:
				newTri.append(vIndex + n)
			self.triangles.append(newTri)
			#print "appended a triangle"
			
		for tristrip in meshData.tristrips:
			newTri = []
			for vIndex in tristrip:
				newTri.append(vIndex + n)
			self.tristrips.append(newTri)
			#print "appended a tristrip"
			
		for trifan in meshData.trifans:
			newTri = []
			for vIndex in trifan:
				newTri.append(vIndex + n)
			self.trifans.append(newTri)
			#print "appended a trifan"
			
		#print "all data merged : end"
		
	def makeGeom(self):
		if not self.nbVertices:
			return None
		self.vformat = makeVertexFormat(color = True, normal = True, texcoord = True, tan_binorm = True)
		self.vdata = GeomVertexData('name', self.vformat, Geom.UHStatic)
		
		self.vWriter = GeomVertexWriter(self.vdata, 'vertex')
		self.nWriter = GeomVertexWriter(self.vdata, 'normal')
		self.tWriter = GeomVertexWriter(self.vdata, 'texcoord')
		self.cWriter = GeomVertexWriter(self.vdata, 'color')
		self.tanWriter = GeomVertexWriter(self.vdata, 'tangent')
		self.binWriter = GeomVertexWriter(self.vdata, 'binormal')
		
		
		self.geom = Geom(self.vdata)
		
		# add vertex data
		for n in xrange(self.nbVertices):
			pos = self.vertices[n]
			normal = self.normals[n]
			texcoord = self.texcoords[n]
			color = self.colors[n]
			tangent = self.tangents[n]
			binormal = self.binormals[n]
			
			self.vWriter.addData3f(pos[0], pos[1], pos[2])
			self.nWriter.addData3f(normal[0], normal[1], normal[2])
			self.tWriter.addData2f(texcoord[0], texcoord[1])
			self.cWriter.addData4f(color[0], color[1], color[2], color[3])
			self.tanWriter.addData3f(tangent[0], tangent[1], tangent[2])
			self.binWriter.addData3f(binormal[0], binormal[1], binormal[2])
			
		
		
		# triangles
		if len(self.triangles):
			trianglePrim = GeomTriangles(Geom.UHStatic)
			for tri in self.triangles:
				if len(tri)!=3:
					continue
				trianglePrim.addVertices(tri[0], tri[1], tri[2])
			trianglePrim.closePrimitive()
			self.geom.addPrimitive(trianglePrim)
		
		# lines
		'''
		if len(self.lines):
			linePrim = GeomLinestrips(Geom.UHStatic)
			for pointList in self.lines:
				for p in pointList:
					linePrim.addVertex(p)
				linePrim.closePrimitive()
			self.geom.addPrimitive(linePrim)
		'''
		# tristrips
		if len(self.tristrips):
			tristripPrim = GeomTristrips(Geom.UHStatic)
			for tristrip in self.tristrips:
				for p in tristrip:
					tristripPrim.addVertex(p)
				tristripPrim.closePrimitive()
			self.geom.addPrimitive(tristripPrim)
		
		# trifans
		if len(self.trifans):
			trifanPrim = GeomTrifans(Geom.UHStatic)
			for trifan in self.trifans:
				for p in trifan:
					trifanPrim.addVertex(p)
				trifanPrim.closePrimitive()
			self.geom.addPrimitive(trifanPrim)
		
		return self.geom
	
#-----------------------------------------------------------------------
# 
#-----------------------------------------------------------------------
class MeshDataComposer(object):
	def __init__(self):
		self.meshData = MeshData()
	
	def reset(self):
		self.meshData.clear()
		
	#-------------------------------------------------------------------
	# 
	def addTriangle(self, posList, texScale=(1.0, 1.0), color=(1,1,1,1)):
		pA = Point3(posList[0])
		pB = Point3(posList[1])
		pC = Point3(posList[2])
		
		normal = (pB-pA).cross(pC-pA)
		normal.normalize()
		
		p1 = self.meshData.nbVertices
		p2 = p1 + 1
		p3 = p2 + 1
		
		# generate the texcoord u,v values
		uA, vA = 0, 0
		uB, vB = texScale[0], 0
		uC, vC = 0.5*texScale[0], texScale[1]
		#AB = (pB - pA).length()
		#AC = (pC - pA).length()
		#BC = (pC - pB).length()
		
		c1, c2, c3, c4 = color[0], color[1], color[2], color[3]
		
		self.meshData.addVertexData(
			pA.getX(), pA.getY(), pA.getZ(),
			normal.getX(), normal.getY(), normal.getZ(),
			uA, vA,
			c1, c2, c3, c4)
		
		self.meshData.addVertexData(
			pB.getX(), pB.getY(), pB.getZ(),
			normal.getX(), normal.getY(), normal.getZ(),
			uB, vB,
			c1, c2, c3, c4)
		
		self.meshData.addVertexData(
			pC.getX(), pC.getY(), pC.getZ(),
			normal.getX(), normal.getY(), normal.getZ(),
			uC, vC,
			c1, c2, c3, c4)
		
		self.meshData.addTriangle(p1, p2, p3)
	
	#-------------------------------------------------------------------
	# 	
	def addQuad(self, pointList, texScale = (1.0, 1.0), texStart = (0,0), color = (1,1,1,1)):
		if len(pointList)<3:
			return
		
		pA = Point3(pointList[0])
		pB = Point3(pointList[1])
		
		if len(pointList) == 3:
			pC = translatePoint(pB, pointList[2])
			pD = translatePoint(pA, pointList[2])
		else:
			pC = Point3(pointList[2])
			pD = Point3(pointList[3])
		
		normal = (pB-pA).cross(pC-pA)
		normal.normalize()
		
		du = (pB - pA).length() * texScale[0]
		dv = (pD - pA).length() * texScale[1]
		
		uA = texStart[0]
		vA = texStart[1]
		uB = uA + du
		vB = vA
		uC = uA + du
		vC = vA + dv
		uD = uA
		vD = vA + dv
		
		c1, c2, c3, c4 = color[0], color[1], color[2], color[3]
		
		p1 = self.meshData.nbVertices
		p2 = p1 + 1
		p3 = p2 + 1
		p4 = p3 + 1
		
		self.meshData.addVertexData(
			pA.getX(), pA.getY(), pA.getZ(),
			normal.getX(), normal.getY(), normal.getZ(),
			uA, vA,
			c1, c2, c3, c4)
		
		self.meshData.addVertexData(
			pB.getX(), pB.getY(), pB.getZ(),
			normal.getX(), normal.getY(), normal.getZ(),
			uB, vB,
			c1, c2, c3, c4)
		
		self.meshData.addVertexData(
			pC.getX(), pC.getY(), pC.getZ(),
			normal.getX(), normal.getY(), normal.getZ(),
			uC, vC,
			c1, c2, c3, c4)
		
		self.meshData.addVertexData(
			pD.getX(), pD.getY(), pD.getZ(),
			normal.getX(), normal.getY(), normal.getZ(),
			uD, vD,
			c1, c2, c3, c4)
		
		self.meshData.addTriangle(p1, p2, p3)
		self.meshData.addTriangle(p1, p3, p4)
		
	#-------------------------------------------------------------------
	# 	
	def addBox(self, size, pos=(0,0,0), rot=0, texScale = (1.0, 1.0), texStart = (0,0), color = (1,1,1,1)):
		x = size[0] / 2.0
		y = size[1] / 2.0
		z = size[2] / 2.0
		
		#print "drawing lines, x = %s" % (x)
		# base points
		p1 = Point3(-x,-y,-z)
		p2 = Point3(x,-y,-z)
		p3 = Point3(x,y,-z)
		p4 = Point3(-x,y,-z)
		# top points
		p1t = Point3(-x,-y,z)
		p2t = Point3(x,-y,z)
		p3t = Point3(x,y,z)
		p4t = Point3(-x,y,z)
		
		pList = [p1, p2, p3, p4, p1t, p2t, p3t, p4t]
		#dP = Point3(pos[0], pos[1], pos[2])
		pList = translatePoints(pList, pos)
		pList = rotatePoints(pList, rot)
		p1, p2, p3, p4, p1t, p2t, p3t, p4t = pList
		
		self.addQuad([p1, p2, p2t, p1t], texScale, texStart=texStart, color=color)
		self.addQuad([p2, p3, p3t, p2t], texScale, texStart=texStart, color=color)
		self.addQuad([p3, p4, p4t, p3t], texScale, texStart=texStart, color=color)
		self.addQuad([p4, p1, p1t, p4t], texScale, texStart=texStart, color=color)
		self.addQuad([p1t, p2t, p3t, p4t], texScale, texStart=texStart, color=color)
		self.addQuad([p1, p4, p3, p2], texScale, texStart=texStart, color=color)
	
	#-------------------------------------------------------------------
	# 
	def addSideWall(self, pointList, dh=2.0, closed = False, texScale=(1.0, 1.0), color=(1,1,1,1)):
		
		nbPts = len(pointList)
		if nbPts < 2:
			return
		try:
			dh = float(dh)
			dh = (0, 0, dh)
		except:
			pass
		
		topPointList = translatePoints(pointList, dh)
		texStart = [0,0]
		
		for i in range(nbPts-1):
			du = (pointList[i+1] - pointList[i]).length() * texScale[0]
			dv = (topPointList[i] - pointList[i]).length() * texScale[1]
			
			self.addQuad([pointList[i], pointList[i+1], topPointList[i+1], topPointList[i]], texScale, texStart, color)
			texStart = [du, dv]
		
		if closed and nbPts>2:
			self.addQuad([pointList[nbPts-1], pointList[0], topPointList[0], topPointList[nbPts-1]], texScale, texStart, color)
		
	
	#-------------------------------------------------------------------
	# 
	def addThickWall(self, pointList, dh=2.0, thickness=0.5, startClosed = False, endClosed = False, closed = False, capped = False, texScale=(1,1), color = (1,1,1,1)):
		nbPts = len(pointList)
		if nbPts < 2:
			print "Error : need at least two points"
			return
		
		rPointList, lPointList = getWallPoints(pointList, thickness, closed)
		if startClosed:
			self.addQuad([lPointList[0], rPointList[0], dh], texScale, color)
			
		if endClosed:
			self.addQuad([rPointList[-1], lPointList[-1], dh], texScale, color)
			
		
		lPointList.reverse()
		self.addSideWall(rPointList, dh, False, texScale)
		self.addSideWall(lPointList, dh, False, texScale)
		
		if closed:
			p1 = rPointList[-1]
			p2 = rPointList[0]
			p3 = translatePoint(p2, dh)
			p4 = translatePoint(p1, dh)
			self.addQuad([p1, p2, p3, p4], texScale, color)
			p1 = lPointList[-1]
			p2 = lPointList[0]
			p3 = translatePoint(p2, dh)
			p4 = translatePoint(p1, dh)
			self.addQuad([p1, p2, p3, p4], texScale, color)
		
		if capped:
			lPointList.reverse()
			rPointList = translatePoints(rPointList, dh)
			lPointList = translatePoints(lPointList, dh)
			
			for i in range(nbPts-1):
				self.addQuad([rPointList[i], rPointList[i+1], lPointList[i+1], lPointList[i]], texScale, color)
			if closed:
				self.addQuad([rPointList[-1], rPointList[0], lPointList[0], lPointList[-1]], texScale, color)
	
	#-------------------------------------------------------------------
	# 
	def addPrism(self, pointList, dh = 0, pos=(0,0,0), rot=(0,0,0), closed = True, capped = True, texScale = (1,1), color = (1,1,1,1)):
		
		nbPts = len(pointList)
		if nbPts < 3:
			return
		try:
			dh = float(dh)
			dh = (0, 0, dh)
		except:
			pass
		
		
		
		
		topPointList = translatePoints(pointList, dh)
		
		pointList = rotatePoints(pointList, rot)
		topPointList = rotatePoints(topPointList, rot)
		
		pointList = translatePoints(pointList, pos)
		topPointList = translatePoints(topPointList, pos)
		
		self.addSideWall(pointList, dh, closed, texScale)
		
		if capped:
			data = getTriangulatorGeomData(topPointList, dh, texScale, color)
			self.mergeTriangulatorData(data)
	
	def addPolygon(self, pointList, dh, texScale=(1,1), color=(1,1,1,1)):
		data = getTriangulatorGeomData(topPointList, dh, texScale, color)
		self.mergeTriangulatorData(data)
			
	def mergeTriangulatorData(self, data):
		p1 = self.meshData.nbVertices
		for i in range(len(data["vertices"])):
			x, y, z = data["vertices"][i]
			nx, ny, nz = data["normals"][i]
			u, v = data["texcoords"][i]
			c1, c2, c3, c4 = data["colors"][i]
			self.meshData.addVertexData(x, y, z, nx, ny, nz, u, v, c1, c2, c3, c4)
			
		for index1, index2, index3 in data["prims"]:
			self.meshData.addTriangle(index1+p1, index2+p1, index3+p1)
	
