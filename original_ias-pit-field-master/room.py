########################################
#  PPT room constructor                #
#  Oliver Castaneda 2011               #
########################################
#  Requires resources.py and shaders.py
#  Make sure to compile this file in your 
#  directory before using it!
#
# Available Objects:
#	walls   (includes a border of the floor)
#	ceiling
#	pit
#	stand
#	divider (the wooden hmd dispenser)
#	plank   (a wooden plank on the floor)
#	window  (observation window)
#   c[4]    (the 4 movable floor parts)
#
#
# To load the room:
#   import room
#	roomGroup = room.PPTRoom()
# To access an object:
#	ceiling = roomGroup.ceiling
#	ceiling.alpha(0) #turn off the ceiling
# Add a video:
#   myVideo = viz.add('myvid.avi')
#   roomGroup.window.texture(myVideo)
#	myVideo.play()
############################################
	

import viz
from resources import *
from shaders import *

shader = texShader()
lightShader = lightShader()
tunnelShader = tunShader()

def PPTRoom():
	roomGroup = viz.addGroup()
	
	#LOAD FILE
	pit = viz.add(PIT_FILE)
	pit.setPosition([0,-0.03,0])
	stand = viz.add(STAND_FILE)
	stand.texture(STAND_TEX)
	room = viz.add(ROOM_FILE)
	room.texture(ROOM_TEX)
	
	### PLANK SETTINGS ###
	plank = viz.add(PLANK_FILE)
	plank.setScale(1.3,1,1.4)
	plank.setPosition([-.45,0,0])

	miniPlank1 = viz.add(PLANK_FILE)
	miniPlank1.setScale(.45,1,1.4)
	miniPlank1.setPosition([.3,0,0])
	miniPlank1.center([.3,0,0])
	miniPlank1.visible(viz.OFF)
	miniPlank2 = viz.add(PLANK_FILE)
	miniPlank2.setScale(.45,1,1.4)
	miniPlank2.setPosition([1.4,0,0])
	miniPlank2.center([2.5,0,0])
	miniPlank2.visible(viz.OFF)
	
	window = viz.add(WINDOW_FILE)
	ceiling = viz.add(CEILING_FILE)
	divider = viz.add(DIV_FILE)
	floor = viz.add(FLOOR_FILE)
	divider.texture(DIV_TEX)
	tunnel = viz.add(TUNNEL_FILE)
	
	roomGroup.c = []
	c = []
	c.append(viz.add(C1_FILE))
	c.append(viz.add(C2_FILE))
	c.append(viz.add(C3_FILE))
	c.append(viz.add(C4_FILE))
	
	for cp in c:
		shader.applyShader(cp)
		cp.parent(roomGroup)
		roomGroup.c.append(cp)
	
	
	###SHADING
	shader.applyShader(room)
	shader.applyShader(pit)
	shader.applyShader(stand)
	shader.applyShader(ceiling)
	shader.applyShader(plank)
	shader.applyShader(miniPlank1)
	shader.applyShader(miniPlank2)
	shader.applyShader(floor)
	
	lightShader.setLightColor([0.5, 0.5, 0.5])
	lightShader.setLightDir([0.4,0.9,-0.4])
	lightShader.applyShader(divider)
	
	tunnelShader.applyShader(tunnel)
	tunnel.drawOrder(0, bin = viz.BIN_TRANSPARENT)
	
	
	#window.texture(LOGO_TEX)
	window.appearance(viz.DECAL)
	
	##ADD TO ROOM
	room.parent(roomGroup)
	pit.parent(roomGroup)
	stand.parent(roomGroup)
	plank.parent(roomGroup)
	miniPlank1.parent(roomGroup)
	miniPlank2.parent(roomGroup)
	window.parent(roomGroup)
	ceiling.parent(roomGroup)
	divider.parent(roomGroup)
	floor.parent(roomGroup)
	tunnel.parent(roomGroup)
	roomGroup.blendFunc(viz.GL_SRC_ALPHA,viz.GL_ONE_MINUS_SRC_ALPHA)
	tunnel.blendFunc(viz.GL_SRC_ALPHA,viz.GL_ONE_MINUS_SRC_ALPHA)
	
	room.walls = room
	roomGroup.tunnel = tunnel
	roomGroup.stand = stand
	roomGroup.plank = plank
	roomGroup.pit = pit
	roomGroup.miniPlank1 = miniPlank1
	roomGroup.miniPlank2 = miniPlank2
	roomGroup.window = window
	roomGroup.divider = divider
	roomGroup.ceiling = ceiling
	roomGroup.floor = floor
	roomGroup.floor.remove()
	roomGroup.floors = True
	roomGroup.setScale([ROOM_SCALE, ROOM_SCALE, ROOM_SCALE])
	roomGroup.setPosition(ROOM_MOVE)
	return roomGroup
	