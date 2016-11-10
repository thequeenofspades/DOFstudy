import os
import viz
from shaders import *

shader = texShader()
lightShader = lightShader()
tunnelShader = tunShader()

SCALE = [0.75, 0.75, 0.75]
#SCALE = [1, 1, 1]
TRANSLATION = [-2.35, -1.2, .5]

# Offsets between the bounding box of the room and the actual room.
# These were just guess-and-checked, so may not be totally correct.
BB_OFFSET_XMAX = -0.8
BB_OFFSET_XMIN = 0
BB_OFFSET_ZMAX = -1
BB_OFFSET_ZMIN = 0.25

# DIR = 'Z:/VRITS 2011/Tina R/LabRoom/'

pieces = ['ceiling and cameras.obj', 'wooden overhang.obj', '1.obj', '2.obj', '3.obj', '4.obj', 'door1.obj', 'door2.obj', 'door3.obj',
			'handles and hinges.obj', 'one door wall.obj', 'projector wall.obj', 'two door wall.obj',
			'window wall.obj', 'window.obj', 'windowWood.obj', 'pit.obj', 'plank.obj', 'tunnel.obj', 'stand.obj' ]

CEILING = 0
OVERHANG = 1
FLOOR1 = 2
FLOOR2 = 3
FLOOR3 = 4
FLOOR4 = 5
DOOR1 = 6
DOOR2 = 7
DOOR3 = 8
HANDLES = 9
ONE_DOOR_WALL = 10
PROJECTOR_WALL = 11
TWO_DOOR_WALL = 12
WINDOW_WALL = 13
WINDOW = 14
WINDOW_WOOD = 15

# Pit-specific
PIT = 16
PLANK = 17
TUNNEL = 18
STAND = 19

def getPlankStartPos():
		return [-0.5 * SCALE[0] + TRANSLATION[0], 0 * SCALE[1] + TRANSLATION[1], -0.8 * SCALE[2] + TRANSLATION[2]]
		
def getStandStartPos():
		return [0 * SCALE[0] + TRANSLATION[0], 0 * SCALE[1] + TRANSLATION[1], -0.8 * SCALE[2] + TRANSLATION[2]]
	
def getPitStartPos():
		return [-0.95 * SCALE[0] + TRANSLATION[0], 0.015 * SCALE[1] + TRANSLATION[1], -0.08 * SCALE[2] + TRANSLATION[2]]
		

class LabRoom(viz.VizNode):
	def __init__(self, dir):
		self.node = viz.addGroup()
		viz.VizNode.__init__(self,self.node.id)
		self.floor = []
		self.parts = []
		
		# Add room pieces
		for piece in pieces:
			loc = os.path.join(dir, piece)
			node = viz.addChild(loc, parent=self.node)
			node.setScale(SCALE)
			node.emissive([1,1,1])
			self.parts.append(node)
		
		self.initializeSides()
		
		# Tunnel
		tunnel = self.parts[TUNNEL]
		tunnelShader.applyShader(tunnel)
		tunnel.drawOrder(0, bin = viz.BIN_TRANSPARENT)
		tunnel.blendFunc(viz.GL_SRC_ALPHA,viz.GL_ONE_MINUS_SRC_ALPHA)
		
		# Store floors as group
		for i in xrange(FLOOR1, FLOOR4 + 1):
			self.floor.append(self.parts[i])
		
		self.translateModel(TRANSLATION)
			
	def initializeSides(self):
		self.walls = []
		for i in range(0, 4):
			self.walls.append(viz.addGroup())
			self.walls[i].setParent(self.node)
		self.getPart(ONE_DOOR_WALL).setParent(self.walls[0])
		self.getPart(DOOR3).setParent(self.walls[0])
		
		self.getPart(TWO_DOOR_WALL).setParent(self.walls[1])
		self.getPart(DOOR1).setParent(self.walls[1])
		self.getPart(DOOR2).setParent(self.walls[1])
		
		self.getPart(PROJECTOR_WALL).setParent(self.walls[2])
		
		self.getPart(WINDOW_WALL).setParent(self.walls[3])
		self.getPart(WINDOW).setParent(self.walls[3])
		self.getPart(WINDOW_WOOD).setParent(self.walls[3])
		
		# Reposition PIT, PLANK, and STAND to fit new room.
		self.getPart(PIT).setPosition([-.95 * SCALE[0],.015 * SCALE[1],-.8 * SCALE[2]])
		self.getPart(PIT).setScale([1.25 * SCALE[0],1 * SCALE[1],1.225 * SCALE[2]])
		self.getPart(PLANK).setPosition([-.5 * SCALE[0],0 * SCALE[1],-.8 * SCALE[2]])
		self.getPart(PLANK).setScale([1.2 * SCALE[0],1 * SCALE[1],1 * SCALE[2]])
		self.getPart(STAND).setPosition([0 * SCALE[0],0 * SCALE[1],-.8 * SCALE[2]])
	
	def getWall(self, index):
		return self.walls[index]
	
	def getRoom(self):
		return self.node
	
	def getFloors(self):
		return self.floor
	
	def getPart(self, index):
		return self.parts[index]
		
	def moveRoom(self, pos, mode=viz.ABS_PARENT):
		self.node.setPosition(pos, mode)
	
	def translateModel(self, trans):
		for i in range(20):
			pos = self.getPart(i).getPosition()
			self.getPart(i).setPosition(pos[0] + trans[0], pos[1] + trans[1], pos[2] + trans[2])
	
	def enableClippingPlanes(self):
		bb = self.getBoundingBox()
		self.clipPlane([1, 0, 0, bb.xmin + BB_OFFSET_XMIN * SCALE[0]], 1)
		self.clipPlane([-1, 0, 0, -(bb.xmax + BB_OFFSET_XMAX * SCALE[0])], 2)
		# Some pieces need to rise.
		#self.clipPlane([0, 1, 0, bb.ymin + BOUNDING_BOX_OFFSET * SCALE[1]], 3)
		#self.clipPlane([0, -1, 0, -bb.ymax + BOUNDING_BOX_OFFSET * SCALE[1]], 4)
		self.clipPlane([0, 0, 1, bb.zmin + BB_OFFSET_ZMIN * SCALE[2]], 5)
		self.clipPlane([0, 0, -1, -(bb.zmax + BB_OFFSET_ZMAX * SCALE[2])], 6)
		return