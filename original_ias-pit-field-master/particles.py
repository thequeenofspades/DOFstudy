import shaders
from random import *
import vizact
import vizshape
import viz
import math

def sum(v1, v2):
	ans = []
	for i in range(len(v1)):
		ans.append(v1[i]+v2[i])
	return ans
	
def scale(v1, f):
	ans = []
	for i in range(len(v1)):
		ans.append(v1[i] * f)
	return ans

def dot(v1,v2):
	ans = 0
	for i in range(len(v1)):
		ans+=(v1[i] * v2[i])
	return ans

def magnitude(v1):
	return math.sqrt(dot(v1,v1))

def normalize(v1):
	return scale(v1, 1.0/(magnitude(v1)))
		
		
class ParticleSystem:
	def __init__(self):
		self.dots = []
		self.n = 400
		self.size = 1.0
		self.color = [1.0, 1.0, 1.0]
		self.shader = shaders.partShader()
		self.loc = [0.0, 1.0, 0.0]
		self.root = viz.addGroup()
	def setNumParticles(self, nn):
		self.n = nn
	def setColor(self, col):
		self.color = col
		self.shader.setColor(col)
	def setPosition(self, loc):
		self.loc = loc
		self.root.setPosition(self.loc)
	def setSize(self, s):
		self.size = s
	def create(self):
		self.spinning = vizact.spin(0,1,0, 2.0)
		self.root.addAction(self.spinning)
		for i in range(self.n):
			self.dots.append(viz.addTexQuad(parent=self.root, size=random()*0.2+0.05))
		for dot in self.dots:
			theta = random() * math.pi * 2
			phi = random() * math.pi * 2
			loc = [math.sin(theta),0.0, math.cos(theta)]
			loc = scale(loc, math.cos(phi))
			loc[1] = math.sin(phi)
			loc = scale(loc, math.sqrt(random())*self.size/2)
			loc[1] *= 0.5		
			shade = math.sin(loc[1])*0.25+0.75;
			self.shader.setColor(scale(self.color, shade));
			self.shader.applyShader(dot)
			dot.billboard(viz.BILLBOARD_VIEW_POS)
			dot.setPosition(loc)
			dot.drawOrder(1, bin=viz.BIN_TRANSPARENT)
		self.root.blendFunc(viz.GL_SRC_ALPHA,viz.GL_ONE_MINUS_SRC_ALPHA)
		
		