import viz


DIR = 'Z:/VRITS 2011/Tina R/LabRoom/'

pieces = ['ceiling and cameras.obj', 'wooden overhang.obj', 'floor.obj', 'door1.obj', 'door2.obj', 'door3.obj',
			'handles and hinges.obj', 'one door wall.obj', 'projector wall.obj', 'two door wall.obj',
			'window wall.obj', 'window.obj', 'windowWood.obj' ]
CEILING = 0
OVERHANG = 1
FLOOR = 2
DOOR1 = 3
DOOR2 = 4
DOOR3 = 5
HANDLES = 6
ONE_DOOR_WALL = 7
PROJECTOR_WALL = 8
TWO_DOOR_WALL = 9
WINDOW_WALL = 10
WINDOW = 11
WINDOW_WOOD = 12

# Texturing for the 4 floor pieces is strange.
'''pieces = ['ceiling and cameras.obj', 'wooden overhang.obj', '1.obj', '2.obj', '3.obj', '4.obj', 'door1.obj', 'door2.obj', 'door3.obj',
			'handles and hinges.obj', 'one door wall.obj', 'projector wall.obj', 'two door wall.obj',
			'window wall.obj', 'window.obj', 'windowWood.obj' ]
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
WINDOW_WOOD = 15'''


class LabRoom(viz.VizNode):
	def __init__(self):
		self.group = viz.addGroup()
		self.floor = viz.addGroup()
		self.parts = []
		for piece in pieces:
			loc = DIR + piece
			node = viz.addChild(loc, parent=self.group)
			node.emissive([1,1,1])
			self.parts.append(node)
		'''for i in xrange(FLOOR1, FLOOR4 + 1):
			self.parts[i].addParent(self.floor)'''
		self.initializeSides()
		
	def initializeSides(self):
		self.walls = []
		for i in range(0, 4):
			self.walls.append(viz.addGroup())
		self.getPart(ONE_DOOR_WALL).setParent(self.walls[0])
		self.getPart(DOOR3).setParent(self.walls[0])
		
		self.getPart(TWO_DOOR_WALL).setParent(self.walls[1])
		self.getPart(DOOR1).setParent(self.walls[1])
		self.getPart(DOOR2).setParent(self.walls[1])
		
		self.getPart(PROJECTOR_WALL).setParent(self.walls[2])
		
		self.getPart(WINDOW_WALL).setParent(self.walls[3])
		self.getPart(WINDOW).setParent(self.walls[3])
		self.getPart(WINDOW_WOOD).setParent(self.walls[3])
	
	def getWall(self, index):
		return self.walls[index]
	
	def getRoom(self):
		return self.group
	
	def getFloor(self):
		return self.parts[FLOOR]
		#return self.floor
	
	def getPart(self, index):
		return self.parts[index]
		
	def setPosition(self, pos, mode=viz.ABS_PARENT):
		self.group.setPosition(pos, mode)