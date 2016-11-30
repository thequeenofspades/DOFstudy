# spherical_player.py
#
# By Lucas Sanchez, June 2015
# 
# Class that creates a spherical screen using a
# sphere from the vizshape library. The screen is
# centered at default eyeheight and plays
# the video and audio specified upon calling the
# constructor.
# 
# Usage advice: If you intend to use this player as
# part of an interactive scene where the user will
# be moving around, as opposed to an empty scene
# whose sole purpose is to play spherical video,
# here are some things to keep in mind:
# The closer the user gets to the wall of the
# sphere, the more distorted the image becomes, so
# this spherical screen works best with videos where
# the closest object seen in the video is well
# outside the range of the user's movement and
# reach. This means that the best videos to play
# using this screen are those that contain only
# non-interactive background content for use in the
# scene, not the foreground objects that the user
# gets close to/interacts with. The length of the
# spherical screen's radius should be set to be the
# distance to the closest object in the video. Any
# further and the closer objects will not move
# realistically as the user moves around the scene.
# Any closer and the world will start to curve
# unrealistically as the user approaches the wall of
# the sphere. If everything in the video is much
# further away than the user will ever move, you can
# simply cap off the radius anywhere above 15 meters,
# and that should be large enough to approximate an
# infinitely distant background.
# 
# Known limitations:
# -For use with the vizsonic sound system, such as in PPT1,
#  the audio must be in its own separate file. Any audio that
#  is a part of the video file cannot be played using the
#  vizsonic sound system.
# -You cannot toggle looping when using the ambisonic sound
#  system (in PPT1)
#
# Troubleshooting:
# If you can't find the video sphere, or if you're not in the center,
# it's probably because the sphere is centered by default at position
# [0,1.82,0]. To change this, use the function player.setScreenPosition(newPos).
# 
# If you're in PPT1 and you can't hear sound, make sure the
# sound is being added from a separate file.
#
# # Usage example:
# player = spherical_player.Player('Videos/football_reel_noextra.mp4', 'Videos/reel_audio.wav', PPT1=True, radius=10, playPauseKey=' ', loop=True)
#
# Press Q to decrease the screen radius by 0.5 m.
# Press W to increase the screen radius by 0.5 m.
# Press A to increase playback speed (fast forward / skip forward)
# Press S to decrease playback speed (rewind / skip backward)
# Press D to jump back 3 seconds
# Press E to re-align audio with video when they get out of sync.
# Press L to toggle whether the video loops or not.
# Press P to print the current time of the video.

#############################################################################
# If you are executing this file directly (if __name__ == '__main__'),      #
# make sure these variables are correct:                                    #
                                                                            #
VIVE = True
PPT1 = True
                                                                            #
# Video filepath                                                            #
VIDEO_FILE = 'Videos/Band.kava.mp4'
                                                                            #
# Audio filepath. Put None if not using audio or if using the audio that is #
# already part of the video file. PPT1 requires a separate audio file, but  #
# it is recommended to use audio that is part of the video file when        #
# possible to avoid duplicate audio sources.                                #
AUDIO_FILE = 'Videos/testaudio.wav'
                                                                            #
# Radius of the spherical player. 15 is a good default for distant scenes.  #
RADIUS = 3
                                                                            #
# Whether or not to loop the video by default.                              #
LOOP = True
                                                                            #
# Key to press in order to play/pause the video.                            #
PLAYPAUSE_KEY = ' '
                                                                            #
#############################################################################

import viz
import vizshape
import vizact
import viztask
#from vhil_devkit_Vive import *

DEFAULT_RADIUS = 15
SKIP_PERIOD = .3
JUMP_AMT = 3

class Player:
	def setScreen(self, radius=DEFAULT_RADIUS):
		self.radius = radius
		self.screen = vizshape.addSphere(radius=self.radius,
			slices = 32, stacks = 32,
			flipFaces=True, cullFace=True, lighting=True)
		
		self.screen.setPosition([0,1.82,0]) # Eyeheight
		self.screen.setEuler([180,0,0])
		
		self.screen.emissive([1,1,1])
	
	def resizeScreen(self, newRadius):
		print 'resizing screen to radius ' + str(newRadius)
		self.screen.remove()
		self.setScreen(newRadius)
		self.screen.texture(self.video)
	
	def scaleDown(self):
		newRadius = self.radius - .5
		if newRadius <= 0: return
		self.resizeScreen(newRadius)
	
	def scaleUp(self):
		self.resizeScreen(self.radius + .5)
	
	def setScreenPosition(self, pos):
		self.screen.setPosition(pos)
	
	def setVideo(self, videoFile):
		if self.video: self.video.remove()
		self.video = viz.addVideo(videoFile)
		self.video.loop(viz.ON if self.loopEnabled else viz.OFF)
		self.screen.texture(self.video)
	
	# Sets up everything necessary for playing an audio file.
	# If no audioFile, pass in None.
	def initAudio(self, audioFile):
		self.audio = None
		self.audio_node = viz.addGroup(pos=[0,0,2])
		if self.PPT1:
			import vizsonic
		self.setAudio(audioFile)
	
	# Sets the given audio file to play,
	# or sets audio to None if audioFile
	# is None.
	def setAudio(self, audioFile):
		if self.audio: self.audio.remove()
		
		if audioFile is None:
			self.audio = None
		else:
			if self.PPT1:
				self.audio = self.audio_node.playsound(audioFile, viz.STOP, volume=0.5)
			else:
				self.audio = viz.addAudio(audioFile)
	
	# Set both video and audio files
	# in only ONE function call!
	def setMedia(self, videoFile, audioFile=None):
		self.setVideo(videoFile)
		self.setAudio(audioFile)
		self.play()
	
	def setVolume(self, vol):
		self.audio.volume(vol)
	
	def play(self):
		self.video.play()
		
		if self.audio:
			if self.PPT1:
				if self.loopEnabled:
					self.audio.play(viz.LOOP)
				else:
					self.audio.play(viz.PLAY)
			else:
				self.audio.play()
	
	def pause(self):
		self.video.pause()
		if self.audio: self.audio.pause()
	
	def togglePlayPause(self):
		if self.skipAmount is not 0:
			self.skipTimer.remove()
			self.skipAmount = 0
			print 'spherical screen paused'
		elif self.video.getState() == viz.MEDIA_RUNNING:
			self.pause()
			print 'spherical screen paused'
		else:
			self.play()
			print 'spherical screen playing'

	# Syncs audio with video, because they can get out-of-sync
	# if the video takes longer to load than the audio.
	def syncAV(self):
		self.seek(self.video.getTime())
		print 'Audio synced with video'
	
	# Sets the video (and audio) at the given time.
	def seek(self, time):
		totalTime = self.video.getDuration()
		if time > totalTime:
			time = totalTime
		elif time < 0:
			time = 0
		
		self.video.setTime(time)
		if self.audio: self.audio.setTime(time)
		
	def _skip(self):
		time = self.video.getTime()
		time += self.skipAmount
		self.seek(time)
	
	def skipForward(self):
		self.skipAmount += 1
		if self.skipAmount == 0: # Was skipping backward, now is 0
			self.skipTimer.remove()
		elif self.skipAmount == 1: # Was at 0, now is skipping forward
			self.pause()
			self.skipTimer = vizact.ontimer(SKIP_PERIOD, self._skip)
		print 'skipping forward ' + str(self.skipAmount) + ' seconds per frame.'
	
	def skipBackward(self):
		self.skipAmount -= 1
		if self.skipAmount == 0: # Was skipping forward, now is 0
			self.skipTimer.remove()
		elif self.skipAmount == -1: # Was at 0, now is skipping backward
			self.pause()
			self.skipTimer = vizact.ontimer(SKIP_PERIOD, self._skip)
		print 'skipping backward ' + str(self.skipAmount) + ' seconds per frame.'

	# Seeks the video backward by JUMP_AMT seconds
	def jumpBackward(self):
		print 'jumping backward'
		time = self.video.getTime()
		time -= JUMP_AMT
		self.seek(time)
	
	def printTime(self):
		vidtime = self.video.getTime()
		print "video time: " + str(vidtime)
		if self.audio:
			audtime = self.audio.getTime()
			print "audio time: " + str(audtime)
	
	def toggleLooping(self):
		if self.PPT1:
			print 'You cannot toggle looping in PPT1.'
			return
		self.loopEnabled = False if self.loopEnabled else True
		self.video.loop(viz.TOGGLE)
		if self.audio:
			self.audio.loop(viz.ON if self.loopEnabled else viz.OFF)
		print 'looping set to ' + str(self.loopEnabled)
		
	# Constructor takes the filename of the video, the filename of the
	# audio (if audio file is separate), and an optional flag indicating
	# whether we are using PPT1 (and therefore the vizsonic library).
	# Also optionally takes the length of the radius of the spherical
	# screen, as well as a char to become a keypress that toggles between
	# playing and pausing the video.
	def __init__(self, videoFile, audioFile=None, PPT1=False, radius=DEFAULT_RADIUS, loop=True, playPauseKey=None):
		self.PPT1 = PPT1
		self.setScreen(radius)

		self.loopEnabled = loop
		vizact.onkeydown('l', self.toggleLooping)
		
		self.video = None
		self.setVideo(videoFile)
		self.initAudio(audioFile)
		
		if playPauseKey: vizact.onkeydown(playPauseKey, self.togglePlayPause)
		
		vizact.onkeydown('q', self.scaleDown)
		vizact.onkeydown('w', self.scaleUp)

		self.skipAmount = 0
		vizact.onkeydown('a', self.skipBackward)
		vizact.onkeydown('s', self.skipForward)
		vizact.onkeydown('d', self.jumpBackward)
		vizact.onkeydown('t', self.printTime)

		vizact.onkeydown('f', self.syncAV)

if __name__ == '__main__':
	vhilGo(VIVE, PPT1)

	player = Player(VIDEO_FILE, AUDIO_FILE, PPT1, RADIUS, LOOP, PLAYPAUSE_KEY)

	vizact.onkeydown('r', reset)