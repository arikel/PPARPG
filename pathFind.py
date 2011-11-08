#!/usr/bin/python
# -*- coding: utf8 -*-

from pandac.PandaModules import * 


#-----------------------------------------------------------------------
# pathfinding
#-----------------------------------------------------------------------


def heurisDist(a,b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])
    
class PathfindNode:
	def __init__(self,prev,pos,dest):
		self.prev,self.pos,self.dest = prev,pos,dest
		if self.prev == None: self.g = 0
		else: self.g = self.prev.g + 1
		self.h = heurisDist(pos,dest)
		self.f = self.g+self.h

def astar(start,end,layer):
	"""
	start = (x1, y1), end = (x2, y2), layer = CollisionGrid.data
	0 = empty, 1 = wall
	taken from Phil's pygame utilities (check PGU on pygame.org)
	"""
	#print "calling astar for start : %s and end : %s" % (start, end)
	if len(start)<=1:return []
	if len(end)<=1:return []
	
	
	w,h = len(layer[0]),len(layer)
	if start[0] < 0 or start[1] < 0 or start[0] >= w or start[1] >= h: return []
	if end[0] < 0 or end[1] < 0 or end[0] >= w or end[1] >= h: return []
	if layer[start[1]][start[0]]: return []
	if layer[end[1]][end[0]]: return []
	
	opens = []
	open = {}
	closed = {}
	cur = PathfindNode(None,start,end)
	open[cur.pos] = cur
	opens.append(cur)
	while len(open):
		cur = opens.pop(0)
		if cur.pos not in open: continue
		del open[cur.pos]
		closed[cur.pos] = cur
		if cur.pos == end: break
		for dx,dy in [(0,-1),(1,0),(0,1),(-1,0),(-1,-1),(1,-1),(-1,1),(1,1)]:
			x,y = pos = cur.pos[0]+dx,cur.pos[1]+dy
			
			if not (0<=y<len(layer)):continue
			if not (0<=x<len(layer[0])):continue
			
			if layer[y][x]>0: continue
			#check for blocks of diagonals
			if layer[cur.pos[1]+dy][cur.pos[0]]>0: continue
			if layer[cur.pos[1]][cur.pos[0]+dx]>0: continue
			
			new = PathfindNode(cur,pos,end)
			if pos in open and new.f >= open[pos].f: continue
			if pos in closed and new.f >= closed[pos].f: continue
			if pos in open: del open[pos]
			if pos in closed: del closed[pos]
			open[pos] = new
			lo = 0
			hi = len(opens)
			while lo < hi:
				mid = (lo+hi)/2
				if new.f < opens[mid].f: hi = mid
				else: lo = mid + 1
			opens.insert(lo,new)
	
	if cur.pos != end: 
		return []
					
	path = []
	while cur.prev != None:
		path.append(cur.pos)
		cur = cur.prev
	#path.append(start)
	path.reverse()
	return path

class Drawer:
	def __init__(self):
		self.node = GeomNode("lines")
		self.np = NodePath(self.node)
		self.np.reparentTo(render)
		self.np.setShaderOff()
		self.np.setLightOff()
		self.path = []
		self.start = (0, 0)
		self.end = (0, 0)
		self.h = 0.2
		'''
		self.startModel = loader.loadModel("frowney")
		self.endModel = loader.loadModel("smiley")
		self.startModel.reparentTo(render)
		self.endModel.reparentTo(render)
		'''
	def setStart(self, start):
		self.start = start
		#self.startModel.setPos(start[0]+0.5, start[1]+0.5, 0)
		
	def setEnd(self, end):
		self.end = end
		#self.endModel.setPos(end[0]+0.5, end[1]+0.5, 0)
		
	def clear(self):
		self.np.remove()
		self.node = GeomNode("lines")
		self.np = NodePath(self.node)
		self.np.reparentTo(render)
		self.np.setShaderOff()
		self.np.setLightOff()
		
	def destroy(self):
		self.np.detachNode()
		del self.np
		
	def drawLine(self, start, end):
		#print "Draw line : %s, %s" % (str(start), str(end))
		self.node.addGeom(self.line(start, end))
	
	def line (self, start, end):
		# since we're doing line segments, just vertices in our geom
		format = GeomVertexFormat.getV3()
	   
		# build our data structure and get a handle to the vertex column
		vdata = GeomVertexData ('', format, Geom.UHStatic)
		vertices = GeomVertexWriter (vdata, 'vertex')
		   
		# build a linestrip vertex buffer
		lines = GeomLinestrips (Geom.UHStatic)
	   
		vertices.addData3f (start[0]+0.5, start[1]+0.5, self.h)
		vertices.addData3f (end[0]+0.5, end[1]+0.5, self.h)
	   
		lines.addVertices (0, 1)
		 
		lines.closePrimitive()
	   
		geom = Geom (vdata)
		geom.addPrimitive (lines)
		# Add our primitive to the geomnode
		#self.gnode.addGeom (geom)
		return geom
		
	def setPath(self, path):
		self.path = path
		self.clear()
		for pos in range(len(self.path)-1):
			self.drawLine(self.path[pos], self.path[pos+1])
