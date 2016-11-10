# Melvin Low
# Contact: mwlow@cs.stanford.edu
#
# Variables to test:
#   x Mono v Stereo
#   x Degrees of Freedom: 3 v 6
#   x Latency: low v high
#   x Update Rate: low v high
#
# Functionality recently included:
#   x DK2 Support
#   x 60/75 fps refresh
#   x Keyboard shortcut for indicating in the data output when the participant is answering questions
#   x Keyboard shortcut for indicating in the data output when the next condition begins
#   x 0/3 frames delay
#   x Data output changes (print statement for phase, or disable timer)
#
# Functionality to include:
#   x Display notification of next condition on HMD screen
#   x Print condition number to console
#   x Print notification to console when final condition has been completed


## ENTER PARITICIPANT ID HERE ##
participantID = 10

## CHANGE WHETHER NEXT_CONDITION       ##
## notification appears in the headset ##
HMDnextCondition = True

import oculus
import viz
import vizfx
import vizact
import vizinput
import time
import Queue
#import vizshape
#import viztask
import vizmat
import vizsonic
import pitlabroom
from shaders import * 
from resources import *
import particles
import random
import math
from datetime import datetime

##################################
##################################
##################################

class labTracker(object):
    def __init__(self, hmd):
        viz.mouse.setVisible(viz.OFF)
        viz.cursor(viz.OFF)
        vrpn = viz.add('vrpn7.dle')
        self.markers = [vrpn.addTracker('PPT0@171.64.33.43', x) for x in range(1)]
        
        ORI_TRACKER = hmd.getSensor()
        
        #Non-OH tracker since we are not using optical heading in this program.
        self.tracker = viz.mergeLinkable(self.markers[0], ORI_TRACKER)
        
    def get(self):
        return self.tracker
    
    def getMarkerPosition(self, markerID):
        return self.markers[markerID-1].getPosition()

        
##################################
##################################
##################################

headLocation = viz.addGroup()
view = viz.MainView
viz.link(view, headLocation)

def moveFloor():
    print "called move floor"
    #Add global variable to get location of floors, play sound from them (not the stand)
    global floorSound, floors
    c = room.getFloors()
    if(floors):
        closeTime = 7 #seconds
        speed = 0.5
        floorSound.play()
        print 'OPENING THE FLOORS!'
        #Puts normal room texture on window
        #roomGroup.window.texture(FLOOR_LOGO_TEX)
        moveLeft = vizact.move([-speed,0,0], closeTime)
        moveRight = vizact.move([speed,0,0], closeTime)
        moveForward = vizact.move([0,0,speed], closeTime)
        moveBack = vizact.move([0,0,-speed], closeTime)
        floors = False
        
        c[0].addAction(moveLeft)
        c[1].addAction(moveBack)
        c[2].addAction(moveRight)
        c[3].addAction(moveForward)
    else:
        print 'CLOSING THE FLOORS!'
        floorSound.play()
        reset = vizact.moveTo(pitlabroom.TRANSLATION, speed = 0.5)
        floors = True
        for cp in c:
            cp.addAction(reset)
            
def configureSound():
    #Good adjustment for reverb and room
    vizsonic.setReverb (6.0, 0.2, 0.5, 0.9, 0.1)
    vizsonic.setSimulatedRoomRadius(30,30)
    vizsonic.setShaker(1.0)
    viz.setOption('sound3d.useViewRotation', 0)
    #Set auarlizer to play towards center of room
    #viz.setListenerSound3D(subview)
    #Turn on sound debugging?
    viz.setDebugSound3D(False)
    
def loadSounds():
    global thudSound, floorSound, windySound, elevatorRun, elevatorStart, elevatorStop
    thudSound = room.getPart(pitlabroom.PIT).playsound(BODY_CRASH_FILE, viz.STOP, volume = 1.0)
    floorSound = room.getPart(pitlabroom.PIT).playsound(SLIDE_FILE, viz.STOP, volume = 1.0)
    #floorSound = room.getPart(pitlabroom.STAND).playsound(SLIDE_FILE, viz.STOP, volume = 1.0)
    windySound = headLocation.playsound(SWOOSH_FILE, viz.STOP, volume = 0.75)
    elevatorRun = room.getPart(pitlabroom.STAND).playsound(ELEVATOR_RUN, viz.STOP, volume = 1.0)
    elevatorStart = room.getPart(pitlabroom.STAND).playsound(ELEVATOR_START, viz.STOP, volume = 1.0)
    elevatorStop = room.getPart(pitlabroom.STAND).playsound(ELEVATOR_STOP, viz.STOP, volume = 1.0)

def CreateRoom():
    #Load in the entire room, store all geometry in the roomgroup
    global floors
    floors = True
    global room 
    room = pitlabroom.LabRoom()
    room.getPart(pitlabroom.TUNNEL).visible(viz.OFF)
    room.getPart(pitlabroom.PLANK).visible(viz.OFF)


##################################
##################################
##################################


def static_var(varname, value):
    """Decorator for initializing a static variable within a function."""
    def decorate(func):
        setattr(func, varname, value)
        return func
    return decorate


class _FovDistortionCorrectionEffect(vizfx.postprocess.BaseShaderEffect):
    fov_x = 1.0
    fov_y = 1.0
    
    def _getFragmentCode(self):
        return """
        uniform vec2 LensCenter;
        uniform vec2 ScreenCenter;
        uniform vec2 Scale;
        uniform vec2 ScaleIn;
        uniform vec4 HmdWarpParam;
        uniform vec4 ChromAbParam;
        uniform sampler2D vizpp_InputTex;

        void main() {
            float x = (gl_FragCoord.x/1920.0*2.0) - 1.0;
            float y = (gl_FragCoord.y/1080.0*2.0) - 1.0;
            if (x < -%(x)s || x > %(x)s || y < -%(y)s || y > %(y)s) {
                gl_FragColor = vec4(0);
                return;
            }


            vec2  theta = (gl_TexCoord[0].xy - LensCenter) * ScaleIn; // Scales to [-1, 1]
            float rSq= theta.x * theta.x + theta.y * theta.y;
            vec2  theta1 = theta * (HmdWarpParam.x + HmdWarpParam.y * rSq + HmdWarpParam.z * rSq * rSq + HmdWarpParam.w * rSq * rSq * rSq);

            // Detect whether blue texture coordinates are out of range since these will scaled out the furthest.
            vec2 thetaBlue = theta1 * (ChromAbParam.z + ChromAbParam.w * rSq);
            vec2 tcBlue = LensCenter + Scale * thetaBlue;
            if (!all(equal(clamp(tcBlue, ScreenCenter-vec2(0.5,0.5), ScreenCenter+vec2(0.5,0.5)), tcBlue))) {
                gl_FragColor = vec4(0);
                return;
            }

            // Now do blue texture lookup.
            float blue = texture2D(vizpp_InputTex, tcBlue).b;

            // Do green lookup (no scaling).
            vec2  tcGreen = LensCenter + Scale * theta1;
            vec4  center = texture2D(vizpp_InputTex, tcGreen);

            // Do red scale and lookup.
            vec2  thetaRed = theta1 * (ChromAbParam.x + ChromAbParam.y * rSq);
            vec2  tcRed = LensCenter + Scale * thetaRed;
            float red = texture2D(vizpp_InputTex, tcRed).r;

            gl_FragColor = vec4(red, center.g, blue, center.a);
        }
        """ % {"x": _FovDistortionCorrectionEffect.fov_x, "y": _FovDistortionCorrectionEffect.fov_y}

    def _createUniforms(self):
        self.uniforms.addFloat('Scale',[0.5,0.5])
        self.uniforms.addFloat('ScaleIn',[2.0,2.0])
        self.uniforms.addFloat('LensCenter',[0.5,0.5])
        self.uniforms.addFloat('ScreenCenter',[0.5,0.5])
        self.uniforms.addFloat('HmdWarpParam',[0,0,0,0])
        self.uniforms.addFloat('ChromAbParam',[0,0,0,0])


@static_var("tracking_buffer", Queue.Queue())
@static_var("cached_position", ([0, 0, 0]))
@static_var("cached_rotation", ([0, 0, 0]))
@static_var("last_render_time", 0)
def update_tracking(stereo="", fov_x="", x=True, y=True, z=True, yaw=True, pitch=True, roll=True, delay=0, framerate=75, trial=0, **kwargs):
    global file
    
    current_render_time = time.time() * 1000.0

    if delay:
        while update_tracking.tracking_buffer.qsize() > delay:
            update_tracking.tracking_buffer.get()
            
        if update_tracking.tracking_buffer.qsize() == delay:
            next_rotation, next_position = update_tracking.tracking_buffer.get()
            update_tracking.cached_rotation = [j if i else k for i, j, k in zip([yaw, pitch, roll], next_rotation, update_tracking.cached_rotation)]
            update_tracking.cached_position = [j if i else k for i, j, k in zip([x, y, z], next_position, update_tracking.cached_position)]
        
        update_tracking.tracking_buffer.put((hmd.getSensor().getEuler(), tracker.getMarkerPosition(1)))

    else:
        # Get and store rotational and positional data
        update_tracking.cached_rotation = [j if i else k for i, j, k in zip([yaw, pitch, roll], hmd.getSensor().getEuler(), update_tracking.cached_rotation)]
        update_tracking.cached_position = [j if i else k for i, j, k in zip([x, y, z], tracker.getMarkerPosition(1), update_tracking.cached_position)]

    if framerate < 75 and current_render_time - update_tracking.last_render_time <= 1000.0/framerate:
        return
    update_tracking.last_render_time = current_render_time
    
    view_matrix = viz.Matrix()
    #m = viz.Matrix.euler(update_tracking.cached_rotation[0], 0, 0)
    view_matrix.setPosition(update_tracking.cached_position)
    view_matrix.setEuler(update_tracking.cached_rotation)
    viz.MainView.setMatrix(view_matrix)
    
    if x:
        dof = "DOF: 6"
    else: 
        dof = "DOF: 3"
    
    data = ', '.join(
        (
            str(datetime.utcnow()), 
            str(trial), 
            str(dof), #degrees of freedom
            str(stereo), #mono/stereo
            str(delay), #latency
            str(framerate), #framerate
            str(update_tracking.cached_rotation),
            str(update_tracking.cached_position)
        )
    )
    
    #print data
    file.write(data + "\n")

print_options = []
    
@static_var("render_event", None)
@static_var("shader", _FovDistortionCorrectionEffect)
@static_var("trial", 0)
def option_handler(option):
    global hmd
    global file
    global print_options
    
    options = {}
    print_options = []
    
    options["trial"] = option_handler.trial
    option_handler.trial += 1

    # Position Lock - 1st bit
    options["yaw"] = options["pitch"] = options["roll"] = True
    options["x"] = options["y"] = options["z"] = (True, False)[bool(option & (1 << 0))]
    if option & (1 << 0):
        print_options.append("Degrees of Freedom: 3")
    else:
        print_options.append("Degrees of Freedom: 6")

#No FOV for now
#    # FOV X - 2nd bit
#    option_handler.shader.fov_x = (1.0, 0.75)[bool(option & (1 << 1))]
#    options["fov_x"] = ("normal", "restricted")[bool(option & (1 << 1))]
#    if option & (1 << 1):
#        print_options.append("FOV X")

    # Framerate - 2nd bit
    #viz.setOption('viz.max_frame_rate', (75, 60)[bool(option & (1 << 1))])
    options["framerate"] = (75, 60)[bool(option & (1 << 1))]
    if option & (1 << 1):
        print_options.append("Framerate: 60")
    else:
        print_options.append("Framerate: 75")

    # Mono Stereo - 3rd bit
    #oculus._DistortionCorrectionEffect = option_handler.shader
    #hmd.remove()
    #hmd = oculus.Rift(window=viz.MainWindow, autoDetectMonitor=True) #TODO: Is there an easier way than removing the hmd?
    hmd.setIPD( (0.06, 0)[bool(option & (1 << 2))] )
    options["stereo"] = ("stereo", "mono")[bool(option & (1 << 2))]
    if option & (1 << 2):
        print_options.append("Mono  ")
    else:
        print_options.append("Stereo")

    # Latency - 4th bit
    
    #This code looks like it sets latency to 3 only if framerate is 60; else latency = 4. Why?
    #options["delay"] = (0, (3 if option & (1 << 4) else 4))[bool(option & (1 << 3))]
    options["delay"] = (0, 3)[bool(option & (1 << 3))]
    
    if option & (1 << 3):
        print_options.append("Latency: 3")
    else:
        print_options.append("Latency: 0")

    if option_handler.render_event:
        option_handler.render_event.remove()
    
    option_handler.render_event = vizact.ontimer(0, update_tracking, **(options))
    
    #print print_options
    file.write(str(print_options) + "\n")

def option_generator():
    options = list(range(0, 16))
    random.shuffle(options)
    while options:
        yield option_handler(options.pop())
        
def setupHMD():
    global hmd
    global tracker
    #For the FOV distortion effect
    #oculus._DistortionCorrectionEffect = _FovDistortionCorrectionEffect
    
    #Windows and views:                                            #
    #Enable Oculus as the main window and enable fullscreen on the #
    #computer monitor as the mirror, or secondary window.          #
    #
    
    hmd = oculus.Rift(window=viz.MainWindow, autoDetectMonitor=True)
    #hmd.setTimeWarp(True)
    
#    # make the oculus window visible only for the Master
#    with viz.cluster.MaskedContext(viz.CLIENT1):# hide
#        viz.MainWindow.visible(False)
#    with viz.cluster.MaskedContext(viz.MASTER):# show
#        viz.MainWindow.visible(True)
#    
#    # set the fullscreen monitor
#    with viz.cluster.MaskedContext(viz.MASTER):# only for clients with this display
#        viz.window.setFullscreenMonitor(2)
#        viz.window.setFullscreen(True)
#
#    # necessary?
#    viz.window.setFullscreen(True)
#
#    mirror = viz.addWindow()
#    mirrorView = viz.addView()
#    mirror.setView(mirrorView)
#    
#    #set placement with alignment: free
#    mirror.setPosition(0, 1, mode=viz.WINDOW_NORMALIZED)
#    mirror.setSize(1, 1, mode=viz.WINDOW_NORMALIZED)
#
#    with viz.cluster.MaskedContext(viz.MASTER) :# hide
#        mirror.visible(False)
#    with viz.cluster.MaskedContext(viz.CLIENT1) :# show
#        mirror.visible(True)
#
#    # set the fullscreen monitor
#    with viz.cluster.MaskedContext(viz.CLIENT1):# only for clients with this display
#        viz.window.setFullscreenMonitor(1)
#        viz.window.setFullscreen(True)
#
#    #set some parameters
#    VFOV = 60
#    aspect = viz.AUTO_COMPUTE
#    stereo = viz.OFF
#    mirror.fov(VFOV, aspect)
#    mirror.stereo(stereo)


    ### Trackers ###
    #hmd.getSensor().setPrediction(True)
    tracker = labTracker(hmd)
    #tracker1 = labTracker.get(tracker)
    
    ### Link tracker with views.
    #oculusViewLink = viz.link(tracker1, viz.MainView)
    #oculusViewLink.preTrans([0,-0.08,-0.07])
    
#    mirrorViewLink = viz.link(oculusViewLink, mirrorView)
    

if __name__ == '__main__':
    viz.setMultiSample(8)
    #viz.setOption('viz.glFinish', 1)
    #viz.vsync(viz.ON)
    viz.go(viz.FULLSCREEN)
    
    setupHMD()
    CreateRoom()
    configureSound()
    loadSounds()

    vizact.onkeydown("r", hmd.getSensor().reset)
    vizact.onkeydown("f", moveFloor)   # f

    #participantID = vizinput.input("Enter the participant ID: ")
    global file
    file = open("experiment_data/data" + str(participantID) + ".txt", "w")
    file.write("Participant ID: " + str(participantID) + '\n')
    
    def answerQuestions():
        file.write("ANSWERING QUESTIONS!" + '\n''\n')
        print "Participant is now answering questions for this condition. Press n to begin the next condition when finished with questions."

    def nextCondition():
        file.write("NEXT CONDITION BEGINS!" + '\n''\n')
        generator.next()
        printCondition()
        
    def printCondition():
        print "Current condition options: " + str(print_options)

    vizact.onkeydown('q', answerQuestions)
    generator = option_generator()
    vizact.onkeydown("n", nextCondition)
    vizact.onkeydown("p", printCondition)

    option_handler(0) 