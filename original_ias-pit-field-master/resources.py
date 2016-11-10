###################################################
## Resources for Pit World
## Oliver Castaneda, Michelle Del Rosario 2011
## Remember to recompile this file (run it, not save it) 
## to see the effects updated
###################################################

import viz

#KeyPresses
RESET_KEY = ' '
MOVE_FLOOR_KEY = 'f'
TUNNEL_KEY = 't'
ZOMBIE_KEY = 'z'
FLY_KEY = 's'



# Constants (THESE ARE CRUCIAL DON'T DELETE THEM)
ROOM_SCALE = 0.718
ROOM_MOVE = [-1.75, -1.42, 0.4]

# Room Geometry
ROOM_DIR = 'Resources/Room/'

ROOM_FILE =   ROOM_DIR + 'vhilRoom_pit.obj'
CEILING_FILE =   ROOM_DIR + 'ceiling.obj'
STAND_FILE =  ROOM_DIR + 'stand.obj'
PLANK_FILE =  ROOM_DIR + 'plank.obj'
PIT_FILE =    ROOM_DIR + 'pit.obj'
DIV_FILE = 	  ROOM_DIR + 'divider.obj'
WINDOW_FILE = ROOM_DIR + 'window.obj'
C1_FILE = 	  ROOM_DIR + 'carpet1.obj'
C2_FILE = 	  ROOM_DIR + 'carpet2.obj'
C3_FILE = 	  ROOM_DIR + 'carpet3.obj'
C4_FILE = 	  ROOM_DIR + 'carpet4.obj'
FLOOR_FILE =  ROOM_DIR + 'floor.obj'
TUNNEL_FILE = ROOM_DIR + 'tunnel.obj'


SKY_FILE   = ROOM_DIR + 'sky.obj'
# Textures

ROOM_TEX =  viz.addTexture(ROOM_DIR + 'vhilRoom_uvMapHIRES.jpg')
DIV_TEX = viz.addTexture(ROOM_DIR + 'divider.tga')
STAND_TEX = viz.addTexture(ROOM_DIR + 'stand.tga')
LOGO_TEX =  viz.addTexture(ROOM_DIR + 'logo.jpg')
FLOOR_LOGO_TEX = viz.addTexture(ROOM_DIR + 'floorlogo.jpg')
ASTEROID_TEX = viz.addTexture('Resources/Misc/asteroidMap2.jpg')


#Avatar

AVATAR = 'Resources/Avatars/CC2_m002_hipoly_A3.cfg'
AVATAR_FACE = 'Resources/Avatars/cody_face.vzf'



# Other

VIDEO_FILE = 'Resources/Misc/kaleidoscope.avi'
BODY_CRASH_FILE = 'Resources/Misc/body_crash.wav'
THUD_FILE =  'Resources/Misc/FallSound.wav'
SLIDE_FILE = 'Resources/Misc/doorsMoving.wav'
SWOOSH_FILE = 'Resources/Misc/swoosh.wav'

CITY_MODEL = 'Resources/Misc/city - final.IVE'
# This model doesn't have a skydome, but when used it causes NOTHING to render... No idea why.
#CITY_MODEL = 'Resources/Misc/citywithoutdome.IVE'


ZOMBIE_FILE = 'Resources/Misc/zombie_moan.wav'
WIND_FILE = 'Resources/Misc/windMono.wav'
AMBIENT_WIND_FILE = 'Resources/Misc/Wind_02.wav'
FRIEND_FILE  = 'Resources/Misc/friend.wav'
FIRE_FILE = 'Resources/Misc/sunFire.wav'
ROBOT_FILE = 'Resources/Misc/robot.wav'
ASTEROID_FILE = 'Resources/Misc/asteroidRumbleShort2.wav'
SHOOTING_STAR_FILE = 'Resources/Misc/shootingStarSparkleLoud.wav'

# Sounds
BEE_SOUND = 'Resources/Misc/bumblebee.wav'
BEE_MODEL = 'Resources/Misc/bee[1].dae'
WOOD_CRACK = 'Resources/Misc/wood_crack.wav'
LONG_CRACK = 'Resources/Misc/long_crack.wav'

# Elevator sounds
ELEVATOR_START = 'Resources/Misc/elevatorStart.wav'
ELEVATOR_RUN = 'Resources/Misc/elevatorRunning.wav'
ELEVATOR_STOP = 'Resources/Misc/elevatorStop.wav'

# Solar System models
MARS_MODEL = 'Resources/Misc/Mars/Mars_normal-strong.lwo'
ROVER_MODEL = 'Resources/Misc/Mars Rover Spirit Opportunity.obj'


## Scratch Work:

#Wall positions as seen by PPT Tracking:
#Glass Wall z = -2.554
#Proj Wall z = 2.908
#2 Door Wall x = 3.02
#Concave Wall x = -3.268
#Total z =  5.462
#Total x = 6.288
