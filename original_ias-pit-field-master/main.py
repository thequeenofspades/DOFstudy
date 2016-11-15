'''
    IAS Study for the Field 2015
    
    One-stage variant of the original 16-stage study.
    Conditions chosen at start time (between subjects design).
    DOF tracking via Oculus position-tracking camera.
'''

import steamvr
import viz, vizfx, vizact, vizjoy, vizinput
import datetime
import random
import xbox_vibration
import pitlabroom

'''
    INSTRUCTIONS
    !!! Make sure the Xbox wireless receiver is connected and the controller is turned on !!!
1. Face HMD North, hit 'r' to reset
2. Open floor with 'f' keypress
3. Start experiment with 'spacebar'
4. Xbox Controls: Directional pad (i.e. "hat") for movement left & right, A button for selection and to disable rumble
5. Fades to black at the end of first stage
'''

# Set these before you start!
RANDOMLY_GENERATE_CONDITION = 1
PPT1 = 0
PPT2 = 0
OCULUS = 1
OCULUS_CAMERA = 1
DATA = 0
XBOX = 0
RUMBLEPAD = 0
CONDITIONS_VISIBLE = 0

EYE_HEIGHT = 1.4 # meters

# TODO:
# change video settings for other comp

# PREVIOUS TODO:
# vibration might happen when audio is playing... make it start at 20 instead of 15?
# rename writeLineToDATAX functions, audo add newline or no?
# make sure rumbles are outputted in order (does this matter to ketaki?)
# data output running averages of positional tracking data outputted at the end

# STRETCH GOALS
# do we want any sounds? what about a new DV: keypress after hearing a beep?
# look through all the inline TODOs
# remove all global vars or move them to the same place
# document the difference between stages, conditions, timers operating at any given time... the flow through basically
# add ability to pause experiment on a keypress (would require rewriting timers to use vizact or viztask instead of ontimer)

cur_question_num = 0
cur_answers = []
POST_SURVEY_QUESTIONS = [
        'I feel like I am a part of the environment in the presentation.',
        'I feel as though I am participating in the displayed environment.',
        'I feel like the objects in the presentation are surrounding me.',
        'I feel a general discomfort.',
        'I feel dizzy.',
        'I feel nauseous.',
        'I feel as though I could fall into the virtual pit.'
    ]
NUM_STAGES = 16
BREAK_STAGE_NUM = 9 # the stage at which to pause for a break (beginning)
LOW_INTENSITY = 0.2
HIGH_INTENSITY = 1.0
MAX_RUMBLE_LENGTH = 10 # in seconds
AVERAGE_IPD = 0.060 # vizard default

STAGE_LENGTH = 60
MAX_RUMBLE_LENGTH = 10
MIN_SECONDS_UNTIL_RUMBLE = 15
MAX_SECONDS_UNTIL_RUMBLE = STAGE_LENGTH - MAX_RUMBLE_LENGTH

# Data file output name
DATAFILE_TRACKING = "_tracking_data.csv"
DATAFILE_RESPONSE = "_response_data.csv"
# Data sample rate (s)
DATA_SAMPLE_RATE = 0.2

def OutputTrackingData():
    global DATAFP1
    global PTID
    result = ""
    result += datetime.datetime.now().strftime("%H:%M:%S.%f") + ","
    vieweul = viz.MainView.getEuler()
    viewpos = viz.MainView.getPosition()
    if PPT1 or PPT2:
        trackerpos = headTracker.getPosition()
    if OCULUS_CAMERA:
        trackerpos = hmd_sensor.getPosition()
    result += str(viewpos[0]) + ","
    result += str(viewpos[1]) + ","
    result += str(viewpos[2]) + ","
    result += str(vieweul[0]) + ","
    result += str(vieweul[1]) + ","
    result += str(vieweul[2]) + ","
    result += str(trackerpos[0]) + ","
    result += str(trackerpos[1]) + ","
    result += str(trackerpos[2]) + "\n"
    writeLineToDATAFP1(result)

def dataFn():
    global trackingDataFn
    trackingDataFn = vizact.ontimer(DATA_SAMPLE_RATE, OutputTrackingData)
  
def writeLineToDATAFP1(line):
    DATAFP1.write(line)
    DATAFP1.flush()
    
def writeLineToDATAFP2(line):
    DATAFP2.write(line)
    DATAFP2.flush()

def writeFileHeaderFP1():
    line1 = "PARTICIPANT_ID, " + PTID + ","
    line1 += "DATE, " + str(datetime.datetime.now()) + "\n"
    writeLineToDATAFP1(line1)
    line2 = "Time,Viewpos_X,Viewpos_Y,Viewpos_Z,Vieweul_Yaw,Vieweul_Pitch,Vieweul_Roll,Headtracker_X,Headtracker_Y,Headtracker_Z" + "\n"
    writeLineToDATAFP1(line2)
    
def writeFileHeaderFP2():
    line1 = "PARTICIPANT_ID, " + PTID + ","
    line1 += "DATE, " + str(datetime.datetime.now()) + "\n"
    writeLineToDATAFP2(line1)

def static_var(varname, value):
    def decorate(func):
        setattr(func, varname, value)
        return func
    return decorate

'''
    LATENCY
'''
panel = None # TODO get rid of this, follow below
@static_var("status", False)
def latency_toggle(value=None):
    global panel, hmd_link

    if value is not None:
        latency_toggle.status = not value

    if latency_toggle.status:
        hmd_link.remove()
        hmd_link = viz.link(hmd_sensor_no_filter, trans_link, priority=0)
        panel.remove()
        panel = hmd.addMessagePanel('Sensor Latency = 0 frames')
    else:
        hmd_link.remove()
        if fps_toggle.status:
            hmd_link = viz.link(hmd_sensor_filter_5, trans_link, priority=0)
        else:
            hmd_link = viz.link(hmd_sensor_filter_6, trans_link, priority=0)
            #hmd_link = viz.link(hmd_sensor_filter_4, trans_link, priority=0)
        panel.remove()
        panel = hmd.addMessagePanel('Sensor Latency = 6 frames')
        #panel = hmd.addMessagePanel('Sensor Latency = 200/3 ms') # TODO talk to Melvin about this

    if not PPT1 and not PPT2:
        hmd_link.setOffset([0,EYE_HEIGHT,0])
            
    latency_toggle.status = not latency_toggle.status


'''
    STEREO VS MONO
'''
@static_var("status", False)
def stereo_toggle(value=None):
    global panel, hmd

    if value is not None:
        stereo_toggle.status = not value

    if stereo_toggle.status:
        hmd.setIPD(AVERAGE_IPD) # TODO set to default
        panel.remove()
        panel = hmd.addMessagePanel('Stereo = ON')
    else:
        hmd.setIPD(0)
        panel.remove()
        panel = hmd.addMessagePanel('Stereo = OFF')

    stereo_toggle.status = not stereo_toggle.status


# Status starts out as True here because Low Persistence
# is on by default!
@static_var("status", True)
def persistence_toggle(value=None):
    global panel, hmd

    if value is not None:
        persistence_toggle.status = not value

    if persistence_toggle.status:
        hmd.setLowPersistence(False)
        panel.remove()
        panel = hmd.addMessagePanel('Low_Persistence = False')
    else:
        hmd.setLowPersistence(True)
        panel.remove()
        panel = hmd.addMessagePanel('Low_Persistence = True')

    persistence_toggle.status = not persistence_toggle.status


'''
    FIELD OF VIEW: Not used
    This implementation does not work correctly
'''
@static_var("status", False)
def fov_toggle(value=None):
    global panel, hmd

    if value is not None:
        fov_toggle.status = not value

    if fov_toggle.status:
        hmd.setZoom(1)
        panel.remove()
        panel = hmd.addMessagePanel('FOV = 100')
    else:
        hmd.setZoom(50)
        panel.remove()
        panel = hmd.addMessagePanel('FOV = 50')

    fov_toggle.status = not fov_toggle.status

'''
    FRAMES PER SECOND
'''
@static_var("status", False)
def fps_toggle(value=None):
    global panel, hmd_link

    if value is not None:
        fps_toggle.status = not value

    if fps_toggle.status:
        viz.setOption('viz.max_frame_rate', 75)
        if latency_toggle.status:
            hmd_link.remove()
            hmd_link = viz.link(hmd_sensor_filter_5, trans_link, priority=0)
        panel.remove()
        panel = hmd.addMessagePanel('Refresh = 75')
    else:
        viz.setOption('viz.max_frame_rate', 60)
        if latency_toggle.status:
            hmd_link.remove()
            hmd_link = viz.link(hmd_sensor_filter_4, trans_link, priority=0)
        panel.remove()
        panel = hmd.addMessagePanel('Refresh = 60')

    if not PPT1 and not PPT2:
        hmd_link.setOffset([0,EYE_HEIGHT,0])
        
    fps_toggle.status = not fps_toggle.status

'''
    DEGREES OF FREEDOM
    Only works when tracking is enabled (PPT1 = 1 | PPT2 = 1)
'''
@static_var("status", False)
def dof_toggle(value=None):
    global panel, hmd_link, trans_link
    
    if value is not None:
        dof_toggle.status = not value

    if dof_toggle.status:
        if PPT1 or PPT2:
            trans_link.setMask(viz.LINK_ALL)
        if OCULUS_CAMERA:
            hmd_link.setMask(viz.LINK_ALL)
        if PPT1 or PPT2 or OCULUS_CAMERA:
            panel.remove()
            panel = hmd.addMessagePanel('DOF = 6')
    else:
        if PPT1 or PPT2:
            trans_link.setMask(viz.LINK_ORI)
        if OCULUS_CAMERA:
            hmd_link.setMask(viz.LINK_ORI)
        if PPT1 or PPT2 or OCULUS_CAMERA:
            panel.remove()
            panel = hmd.addMessagePanel('DOF = 3')

    dof_toggle.status = not dof_toggle.status

'''
    TIMEWARP: Not used
'''
@static_var("status", False)
def timewarp_toggle(value=None):
    global panel, hmd

    if value is not None:
        timewarp_toggle.status = not value

    if timewarp_toggle.status:
        hmd.setTimeWarp(True)
        panel.remove()
        panel = hmd.addMessagePanel('Timewarp = ON')
    else:
        hmd.setTimeWarp(False)
        panel.remove()
        panel = hmd.addMessagePanel('Timewarp = OFF')

    timewarp_toggle.status = not timewarp_toggle.status


def createRoom():
    # load in the entire room, store all geometry in the roomgroup
    global room, floors, floorSound
    room = pitlabroom.LabRoom(dir="LabRoom")
    room.getPart(pitlabroom.TUNNEL).visible(viz.OFF)
    room.getPart(pitlabroom.PLANK).visible(viz.OFF)
    floors = True
    if PPT1:
        floorSound = room.getPart(pitlabroom.PIT).playsound('doorsMoving.wav', viz.STOP)
    else:
        floorSound = viz.addAudio('doorsMoving.wav')
    #floorSound = room.getPart(pitlabroom.PIT).playsound('doorsMoving.wav', viz.STOP, volume=1.0)

#    room.getPart(pitlabroom.FLOOR1).visible(viz.OFF)
#    room.getPart(pitlabroom.FLOOR2).visible(viz.OFF)
#    room.getPart(pitlabroom.FLOOR3).visible(viz.OFF)
#    room.getPart(pitlabroom.FLOOR4).visible(viz.OFF)

def moveFloor():
    global floors, floorSound
    c = room.getFloors()
    if(floors):
        closeTime = 7 #seconds
        speed = 0.5
        floorSound.play()
        print '\nOpening the floors...'
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
        print '\nClosing the floors...'
        reset = vizact.moveTo(pitlabroom.TRANSLATION, speed = 0.5)
        floors = True
        for cp in c:
            cp.addAction(reset)
        vizact.ontimer2(1.75,0,floorSound.play)

def addCubes():
    import vizshape
#    cube1 = vizshape.addCube(size=0.75, color=viz.RED)
#    cube2 = vizshape.addCube(size=0.5, color=viz.BLUE)
#    cube1.setPosition([-1.5,0.25,-1.5])
#    cube2.setPosition([1.5,0.5,1.5])
    column1 = vizshape.addBox(size=[0.75,12,0.75], color=viz.RED)
    column2 = vizshape.addBox(size=[0.5,12,0.5], color=viz.BLUE)
    column1.setPosition([-1.5,-5,-1.5])
    column2.setPosition([1.5,-5,1.5])


# before Vizard 5.1 and it's Direct to HMD mode
#LEFTMOST_RADIO_BUTTON_X = 0.35
#RADIO_BUTTON_Y = 0.3
#DISTANCE_BETWEEN_RADIO_BUTTONS = 0.08
#QUESTION_TEXTBOX_X = 0.5
#QUESTION_TEXTBOX_Y = 0.35

OCULUS_RESOLUTION_X = 960.0
OCULUS_RESOLUTION_Y = 1080.0

LEFTMOST_RADIO_BUTTON_X = 0.5
RADIO_BUTTON_Y = 0.0
X_DISTANCE_BETWEEN_RADIO_BUTTONS = 0.08
QUESTION_TEXTBOX_X = 0.67
QUESTION_TEXTBOX_Y = 0.05

if not CONDITIONS_VISIBLE:
    # move GUI up
    RADIO_BUTTON_Y += 0.25
    QUESTION_TEXTBOX_Y += 0.25

def setUpGUI():
    global GUI, radioGroup, canvas

    class GUIContainer(object):
        pass

    GUI = GUIContainer()
    
    canvas = viz.addGUICanvas()

    GUI.question = viz.addTextbox(parent=canvas)
    GUI.question.overflow(viz.OVERFLOW_GROW)
    GUI.question.message('Update this to question text')
    GUI.question.setPosition(QUESTION_TEXTBOX_X*OCULUS_RESOLUTION_X,QUESTION_TEXTBOX_Y*OCULUS_RESOLUTION_Y)

    GUI.box1 = viz.addTextbox(parent=canvas)
    GUI.box1.length(2.1)
    GUI.box1.overflow(viz.OVERFLOW_GROW)
    GUI.box1.message("Not at all")
    GUI.box1.setPosition(.65*OCULUS_RESOLUTION_X,RADIO_BUTTON_Y*OCULUS_RESOLUTION_Y) #.46

    GUI.box2 = viz.addTextbox(parent=canvas)
    GUI.box2.length(.5)
    GUI.box2.overflow(viz.OVERFLOW_GROW)
    GUI.box2.message("Completely")
    GUI.box2.setPosition(.87*OCULUS_RESOLUTION_Y,RADIO_BUTTON_Y*OCULUS_RESOLUTION_Y) #.76

    GUI.myRadio1 = viz.addRadioButton(1, parent=canvas)
    GUI.myRadio2 = viz.addRadioButton(1, parent=canvas)
    GUI.myRadio3 = viz.addRadioButton(1, parent=canvas)
    GUI.myRadio4 = viz.addRadioButton(1, parent=canvas)
    GUI.myRadio5 = viz.addRadioButton(1, parent=canvas)

    radioGroup = GUI.myRadio1.getGroup()

    for i, button in enumerate(radioGroup.getButtons()):
        button.setPosition((LEFTMOST_RADIO_BUTTON_X*OCULUS_RESOLUTION_X)+(i*(X_DISTANCE_BETWEEN_RADIO_BUTTONS*OCULUS_RESOLUTION_X)),RADIO_BUTTON_Y*OCULUS_RESOLUTION_Y)

    GUI.myRadio3.set(viz.ON) # set default to center
    
    readyBlackScreen() # for the end

    # draw everything in front of the black screen
#    for elem in [a for a in dir(GUI) if not a.startswith('__') and not callable(getattr(GUI,a))]:
#       getattr(GUI,elem).drawOrder(1, bin=viz.BIN_FRONT_TO_BACK)

def hideGUI():
    for elem in [a for a in dir(GUI) if not a.startswith('__') and not callable(getattr(GUI,a))]:
       getattr(GUI,elem).visible(viz.OFF)

def showGUI():
    for elem in [a for a in dir(GUI) if not a.startswith('__') and not callable(getattr(GUI,a))]:
       getattr(GUI,elem).visible(viz.ON)

def setUpGamepad():
    global gamepad, xbox

    gamepad = vizjoy.add()
    if gamepad.id == -1: # indicates failure connecting to gamepad
        print 'Gamepad must be turned on and connected.'
        viz.quit()

    # debugging DirectInput for Xbox 360 controllers
#    import vizconfig
#    dinput = viz.add('DirectInput.dle')
#    for sensor in dinput.getXboxControllerList():
#        vizconfig.register(sensor)
#    vizconfig.getConfigWindow().setWindowVisible(True)

    def hat(e):
        if e.hat == 90:
            buttons = radioGroup.getButtons()
            for i,b in enumerate(buttons):
                if b.get() == viz.ON:
                    b.set(viz.OFF)
                    buttons[min(i+1,len(buttons)-1)].set(viz.ON)
                    return
        if e.hat == 270:
            buttons = radioGroup.getButtons()
            for i,b in enumerate(buttons):
                if b.get() == viz.ON:
                    b.set(viz.OFF)
                    buttons[max(i-1,0)].set(viz.ON)
                    return

    def joymove(e):
        if e.pos[0] == 1.0:
            buttons = radioGroup.getButtons()
            for i,b in enumerate(buttons):
                if b.get() == viz.ON:
                    b.set(viz.OFF)
                    buttons[min(i+1,len(buttons)-1)].set(viz.ON)
                    return
        if e.pos[0] == -1.0:
            buttons = radioGroup.getButtons()
            for i,b in enumerate(buttons):
                if b.get() == viz.ON:
                    b.set(viz.OFF)
                    buttons[max(i-1,0)].set(viz.ON)
                    return

    def buttondown(e):
        global rumbling, time_rumbling, cur_answers
        # debugging rumble stuff
#        gamepad.hasFFB() # True only if Logitech drivers are installed, False for Xbox 360 gamepad
#        gamepad.setForce(.5) # results in "not exclusive" error with the Logitech rumblepad
#        gamepad.addForce(.5,.5) # results in "not exclusive" error
#        vizjoy.rumble(.5,duration=.75) # has no effect on our gamepads

        if RUMBLEPAD:
            if e.button == 2:
                # TODO: output state of radio buttons to data file
                advanceToNextQuestion()
        if XBOX:
            if e.button == 1:
                if rumbling:
                    rumbling = False
                    time_rumbling = datetime.datetime.now() - time_rumbling # timedelta
                    print 'Milliseconds to disable', cur_rumble_type, 'rumble:', timedelta_milliseconds(time_rumbling)
                    if DATA:
                        ol = 'RUMBLE' + cur_rumble_type + ',' + str(timedelta_milliseconds(time_rumbling)) + '\n'
                        writeLineToDATAFP2(ol)
                    stopVibratingGamepad(controller_id=0)
                    disableGamepad()
                else:
                    #print vars(radioGroup.getSelected())
                    buttons = radioGroup.getButtons()
                    for i,b in enumerate(buttons):
                        if b.get() == viz.ON:
                            cur_answers.append(i+1) # scale from 1-5
                            break
                    advanceToNextQuestion()
            # example usage of xbox_vibration
#            if e.button == 2:
#                controller_id = e.joy.id # usually 0
#                num_seconds = 2
#                xbox_vibration.vibrate_for(controller_id, 1, 1, num_seconds)

    viz.callback(vizjoy.BUTTONDOWN_EVENT, buttondown)
    if RUMBLEPAD:
        viz.callback(vizjoy.HAT_EVENT, hat)
    if XBOX:
        #viz.callback(vizjoy.MOVE_EVENT, joymove) # for use with upper left joystick, too sensitive
        viz.callback(vizjoy.HAT_EVENT, hat) # for use with lower left control pad

def vibrateGamepad(controller_id, intensity=None, num_seconds=None):
    if not intensity:
        intensity = HIGH_INTENSITY # default
    if num_seconds:
        xbox_vibration.vibrate_for(controller_id, intensity, intensity, num_seconds)
    else:
        xbox_vibration.start_vibration(controller_id, intensity, intensity)

def stopVibratingGamepad(controller_id):
    xbox_vibration.stop_vibration(controller_id)

def disableGamepad():
    gamepad.setEnabled(viz.OFF)

def enableGamepad():
    gamepad.setEnabled(viz.ON)

def timedelta_milliseconds(td):
    return td.days*86400000 + td.seconds*1000 + td.microseconds/1000

cur_rumble_type = None
rumbling = False
def promptWithRumble(intensity=None):
    global rumbling, time_rumbling, cur_rumble_type
    if rumbling: # edge case where previous rumble hasn't been exited
        rumbling = False
        #time_rumbling = datetime.datetime.now() - time_rumbling # timedelta
        #print 'Rumble exceeded maximum:', timedelta_milliseconds(time_rumbling)
        print cur_rumble_type, 'Rumble exceeded maximum (PWR):', MAX_RUMBLE_LENGTH*1000
        if DATA:
            ol = 'RUMBLE' + cur_rumble_type + ',' + str(MAX_RUMBLE_LENGTH*1000) + '\n'
            writeLineToDATAFP2(ol)
        stopVibratingGamepad(controller_id=0)
    enableGamepad()
    rumbling = True
    time_rumbling = datetime.datetime.now()
    if intensity:
        if intensity == 1.0:
            cur_rumble_type = "HIGH" # TODO set this back to None
        else:
            cur_rumble_type = "LOW"
        vibrateGamepad(controller_id=0, intensity=intensity, num_seconds=MAX_RUMBLE_LENGTH)
    else:
        vibrateGamepad(controller_id=0, num_seconds=MAX_RUMBLE_LENGTH)


### from Melvin's condition_code ###

# Create 16 random conditions
conditions = [x for x in xrange(16)]

# Shuffle the conditions
random.seed()
random.shuffle(conditions)

def pick_condition():
    if conditions:
        return conditions.pop()

def set_condition(condition):
    status = []

    latency_toggle(condition & (1 << 0))
    if condition & (1 << 0):
        status.extend(["latency: 200/3"]) # TODO should be 4 frames
    else:
        status.extend(["latency: 0"])

    # fps_toggle(condition & (1 << 1))
    # if condition & (1 << 1):
    #     status.extend(["fps: 60"])
    # else:
    #     status.extend(["fps: 75"])

    stereo_toggle(condition & (1 << 1))
    if condition & (1 << 1):
        status.extend(["stereo: off"])
    else:
        status.extend(["stereo: on"])

    dof_toggle(condition & (1 << 2))
    if condition & (1 << 2):
        status.extend(["dof: 3"])
    else:
        status.extend(["dof: 6"])

    # persistence_toggle(not (condition & (1 << 3)))
    # if not (condition & (1 << 3)):
    #     status.extend(["Low Persistence: True"])
    # else:
    #     status.extend(["Low Persistence: False"])

    return status

def set_input_conditions():
    status = []
    if LATENCY_VALUE == "0 FRAMES":
        status.extend(["latency: 0 frames"])
        latency_toggle(False)
    elif LATENCY_VALUE == "6 FRAMES":
        status.extend(["latency: 6 frames"])
        latency_toggle(True)
    if STEREO_VALUE == "ON":
        status.extend(["stereo: on"])
        stereo_toggle(False)
    elif STEREO_VALUE == "OFF":
        status.extend(["stereo: off"])
        stereo_toggle(True)
    if DOF_VALUE == "3":
        status.extend(["dof: 3"])
        dof_toggle(True)
    elif DOF_VALUE == "6":
        status.extend(["dof: 6"])
        dof_toggle(False)
    return status

def updateConditions():
    global panel, status

    status = set_input_conditions()
    if panel:
        panel.remove()
    panel = hmd.addMessagePanel("\n".join(status))
    if not CONDITIONS_VISIBLE:
        panel.visible(viz.OFF)
    print '\nStage:', cur_stage, ',', 'Status:', status
    if DATA:
        ol = 'STAGE,' + str(cur_stage) + ',' + 'STATUS,' + str(status) + '\n'
        writeLineToDATAFP2(ol)
        # workaround hack since status is a list of strings rather than objects
        # example status format: ['latency: 0', 'stereo: on', 'dof: 6'] # 'Low Persistence: True']
        ol = status[0][:7] + ',' + status[1][:6] + ',' + status[2][:3] + '\n' # + status[3][:15] + '\n'
        writeLineToDATAFP2(ol)
        ol = status[0][9:] + ',' + status[1][8:] + ',' + status[2][5:] + '\n' # + status[3][17:] + '\n'
        writeLineToDATAFP2(ol)
    
def startStage():
    global lowRumbleTimer, highRumbleTimer, askQuestionsTimer
    global lookAroundTimer, leanAudioTimer, conditionOverTimer
    
    if DATA:
        ol = 'STAGE,' + str(cur_stage) + '\n'
        writeLineToDATAFP1(ol)
    
    first_trigger = random.randint(MIN_SECONDS_UNTIL_RUMBLE, MAX_SECONDS_UNTIL_RUMBLE)
    next_possible_timings = set( range(MIN_SECONDS_UNTIL_RUMBLE, first_trigger-MAX_RUMBLE_LENGTH) + range(first_trigger+MAX_RUMBLE_LENGTH+1, MAX_SECONDS_UNTIL_RUMBLE) )
    second_trigger = random.sample(next_possible_timings,1)[0]
    
    num_seconds_until_low_rumble = first_trigger
    num_seconds_until_high_rumble = second_trigger
    num_seconds_until_questions = STAGE_LENGTH
    print 'Seconds until low rumble:',  num_seconds_until_low_rumble
    print 'Seconds until high rumble:',  num_seconds_until_high_rumble
    if DATA:
        ol = 'LOW_RUMBLE_TRIGGER_AFTER,' + str(num_seconds_until_low_rumble) + ',' + 'HIGH_RUMBLE_TRIGGER_AFTER,' + str(num_seconds_until_high_rumble) + '\n'
        writeLineToDATAFP2(ol)
    
    lowRumbleTimer = vizact.ontimer2(num_seconds_until_low_rumble,0,promptWithRumble,LOW_INTENSITY)
    highRumbleTimer = vizact.ontimer2(num_seconds_until_high_rumble,0,promptWithRumble,HIGH_INTENSITY)
    askQuestionsTimer = vizact.ontimer2(num_seconds_until_questions,0,askQuestions)
    
    TIME_UNTIL_LOOK_AROUND_AUDIO = 4
    TIME_UNTIL_LEAN_AUDIO = 12
    TIME_UNTIL_CONDITION_OVER_AUDIO = STAGE_LENGTH - 9
    
    # make the below global and remember to disable them on skip!
    if not cur_stage == 1:
        reached_next_phase.play()
    lookAroundTimer = vizact.ontimer2(TIME_UNTIL_LOOK_AROUND_AUDIO,0,look_left_and_right.play)
    leanAudioTimer = vizact.ontimer2(TIME_UNTIL_LEAN_AUDIO,0,indicateLean)
    conditionOverTimer = vizact.ontimer2( TIME_UNTIL_CONDITION_OVER_AUDIO,0,condition_over.play)

cur_stage = 0
def progressToNextStage():
    
    # for debugging, when 'n' is pressed
    global lowRumbleTimer, highRumbleTimer, askQuestionsTimer
    lowRumbleTimer.remove()
    highRumbleTimer.remove()
    askQuestionsTimer.remove()
    
    # for debugging, when 'n' is pressed
    global lookAroundTimer, leanAudioTimer, conditionOverTimer
    reached_next_phase.stop()
    look_left_and_right.stop()
    lean_in_to_the_pit.stop()
    condition_over.stop()
    lookAroundTimer.remove()
    leanAudioTimer.remove()
    conditionOverTimer.remove()
    
    global cur_stage    
    cur_stage += 1
    if cur_stage > NUM_STAGES:
        endExperiment()
        return
    if cur_stage == BREAK_STAGE_NUM:
        if DATA:
            writeLineToDATAFP1('BREAK\n')
            trackingDataFn.setEnabled(viz.OFF)
        vizact.onkeydown('c', continueExperiment)
        print '\nReached Stage ' + str(BREAK_STAGE_NUM) + ': Time for a break!'
        print 'Press "c" when ready to continue.'
        turnScreenBlack()
        return
    updateConditions()
    startStage()

def continueExperiment():
    global blackScreenPC, blackScreenHMD
    blackScreenPC.alpha(0.0) # hide the black screens
    blackScreenHMD.alpha(0.0)
    if DATA:
        trackingDataFn.setEnabled(viz.ON)
    updateConditions()
    startStage()
    
def startExperiment():
    if DATA:
        writeLineToDATAFP1('EXPERIMENT STARTED\n')
        viz.director(dataFn)
    global cur_stage
    cur_stage = 1
    startEventFn.remove() # to prevent accidentally resetting
    updateConditions()
    startStage()

def endExperiment():
    print '\nExperiment over.'
    turnScreenBlack()
    if DATA:
        writeLineToDATAFP1('EXPERIMENT OVER\n')
        trackingDataFn.setEnabled(viz.OFF)
        DATAFP1.close()
        DATAFP2.close()

def askQuestions():
    global rumbling, time_rumbling
    if rumbling:
        rumbling = False
        #time_rumbling = datetime.datetime.now() - time_rumbling # timedelta
        #print 'Rumble exceeded maximum:', timedelta_milliseconds(time_rumbling)
        print cur_rumble_type, 'Rumble exceeded maximum (AQ):', MAX_RUMBLE_LENGTH*1000
        if DATA:
            ol = 'RUMBLE' + cur_rumble_type + ',' + str(MAX_RUMBLE_LENGTH*1000) + '\n'
            writeLineToDATAFP2(ol)
        stopVibratingGamepad(controller_id=0)
    showGUI()
    enableGamepad()
    advanceToNextQuestion()

def postSurveyQuestionsCompleted():
    global cur_question_num, cur_answers
    hideGUI()
    disableGamepad()
    print 'Answers to Stage', cur_stage, ':', cur_answers
    if DATA:
        ol = 'Q1,Q2,Q3,Q4,Q5,Q6,Q7' + '\n'
        writeLineToDATAFP2(ol)
        ol = str(cur_answers[0]) + ',' + str(cur_answers[1]) + ',' + str(cur_answers[2]) + ',' + str(cur_answers[3]) + ',' + str(cur_answers[4]) + ',' + str(cur_answers[5]) + ',' + str(cur_answers[6]) + '\n'
        writeLineToDATAFP2(ol)
    cur_question_num = 0
    cur_answers = []
    # progressToNextStage() # no longer auto-progress, instead...
    endExperiment()

def advanceToNextQuestion():
    global cur_question_num
    
    num = cur_question_num
    if num >= len(POST_SURVEY_QUESTIONS):
        postSurveyQuestionsCompleted()
        return
    GUI.question.message(POST_SURVEY_QUESTIONS[cur_question_num])
    GUI.myRadio3.set(viz.ON)

    cur_question_num = num + 1

def indicateLean():
    lean_in_to_the_pit.play()
    if DATA:
        writeLineToDATAFP1('START LEAN\n')
        print 'Starting lean...'
        
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

def setUpAudio():        
    global look_left_and_right, reached_next_phase, lean_in_to_the_pit, condition_over
    
    if PPT1:
        look_left_and_right = room.playsound("Audio/look_left.wav", viz.STOP)
        reached_next_phase = room.playsound("Audio/next_phase.wav", viz.STOP)
        lean_in_to_the_pit = room.playsound("Audio/lean.wav", viz.STOP)
        condition_over = room.playsound("Audio/condition_over.wav", viz.STOP)
    else:
        look_left_and_right = viz.addAudio("Audio/look_left.wav")
        reached_next_phase = viz.addAudio("Audio/next_phase.wav")
        lean_in_to_the_pit = viz.addAudio("Audio/lean.wav")
        condition_over = viz.addAudio("Audio/condition_over.wav")

def readyBlackScreen(): # add black quad to screen
    global blackScreenPC
    blackScreenPC = viz.addTexQuad(parent=viz.ORTHO)
    blackScreenPC.alignment(viz.ALIGN_LEFT_BOTTOM)
    blackScreenPC.color(viz.BLACK)
    blackScreenPC.alpha(0.0)
    #blackScreenPC.drawOrder(-1, bin=viz.BIN_FRONT_TO_BACK) # for debugging on-screen GUI
    viz.link(viz.MainWindow.WindowSize,blackScreenPC,mask=viz.LINK_SCALE)
    
    global blackScreenHMD
    blackScreenHMD = viz.addTexQuad(parent=canvas)
    blackScreenHMD.setSize([9000,9000])
    blackScreenHMD.alignment(-1000)
    blackScreenHMD.color(viz.BLACK)
    blackScreenHMD.alpha(0.0)
    #blackScreenHMD.drawOrder(-1, bin=viz.BIN_FRONT_TO_BACK)

def turnScreenBlack():
    #blackScreen.visible(True)
    #blackScreen.color(viz.BLACK)
    blackScreenPC.runAction(vizact.fadeTo(1.0,time=3.0))
    blackScreenHMD.runAction(vizact.fadeTo(1.0,time=3.0))
    #fade_out = vizact.fadeTo(viz.BLACK,time=3.0,interpolate=vizact.easeOutStrong)
    #blackScreen.runAction(vizact.sequence(fade_out,vizact.method.visible(False)))


if __name__ == '__main__':

    if DATA:
        PTID = vizinput.input('What is the participant number?')
        DATAFP1 = open("TrackingData/"+PTID+DATAFILE_TRACKING, 'w')
        writeFileHeaderFP1()
        DATAFP2 = open("ResponseData/"+PTID+DATAFILE_RESPONSE, 'w')
        writeFileHeaderFP2()

    if RANDOMLY_GENERATE_CONDITION:
        LATENCY_VALUE = vizact.choice(['0 FRAMES','6 FRAMES'], mode=vizact.RANDOM).generate()
        STEREO_VALUE = vizact.choice(['ON','OFF'], mode=vizact.RANDOM).generate()
        DOF_VALUE = vizact.choice(['3','6'], mode=vizact.RANDOM).generate()
    else:
        LATENCY_VALUE = ['0 FRAMES','6 FRAMES'][vizinput.choose('Choose LATENCY',['0 FRAMES','6 FRAMES'])]
        STEREO_VALUE = ['ON','OFF'][vizinput.choose('Choose STEREO',['ON','OFF'])]
        DOF_VALUE = ['3','6'][vizinput.choose('Choose DOF',['3','6'])]

    if PPT1:
        import vizsonic
        configureSound()
    
    # make sure these are enabled on the PPT computers, if not the framerate drops signficantly
    # however these options may cause performance problems when running on lesser hardware (e.g. in the dev room)
    viz.setOption('viz.glFinish', 1)
    viz.setMultiSample(4)
    
    viz.go()
    viz.window.setSize(1260,790)

    if OCULUS:
        hmd = steamvr.HMD()
        hmd_sensor = hmd.getSensor()
        hmd_sensor.reset()
        
        if PPT1:
            PPT_HOSTNAME = '171.64.33.43'
        if PPT2:
            PPT_HOSTNAME = '171.64.32.54'
        if PPT1 or PPT2:
            vrpn = viz.add('vrpn7.dle')
            headTracker = vrpn.addTracker('PPT0@' + PPT_HOSTNAME, 0)
            headPPT = viz.mergeLinkable(headTracker,hmd_sensor)
            trans_link = viz.link(headPPT, viz.MainView)
        else:
            trans_link = viz.MainView # non-tracking workaround for development
            
        def resetHMD():
            print '\nResetting HMD...'
            hmd_sensor.reset()
        vizact.onkeydown('r', resetHMD)

        filter = viz.add('filter.dle')
        hmd_sensor_no_filter = filter.delay(hmd_sensor, frames=0)
        hmd_sensor_filter_4 = filter.delay(hmd_sensor, frames=4)
        hmd_sensor_filter_5 = filter.delay(hmd_sensor, frames=5)
        hmd_sensor_filter_6 = filter.delay(hmd_sensor, frames=6)
        
        hmd_link = viz.link(hmd_sensor_no_filter, trans_link, priority=0)
        if not PPT1 and not PPT2:
            hmd_link.setOffset([0,EYE_HEIGHT,0])

        #panel = hmd.addMessagePanel('No Variables Active')
        if not CONDITIONS_VISIBLE:
            #panel.visible(viz.OFF)
            pass

        vizact.onkeydown('1', latency_toggle)
        vizact.onkeydown('2', dof_toggle)
        vizact.onkeydown('3', stereo_toggle)

#        vizact.onkeydown('4', persistence_toggle)
#        vizact.onkeydown('5', fps_toggle)
#        vizact.onkeydown('6', stereo_toggle)
#        vizact.onkeydown('7', timewarp_toggle)
#        vizact.onkeydown('8', fov_toggle)

    createRoom()
    addCubes()

    #world = viz.addChild('maze.osgb')
    #viz.eyeheight(EYE_HEIGHT)
        
    setUpAudio()
    
    setUpGUI()
    hideGUI()

    setUpGamepad()
    disableGamepad()
    
    random.seed()
    
    if RANDOMLY_GENERATE_CONDITION:
        def printCondition():
            print 'Current Condition -', 'Latency:', LATENCY_VALUE, ', Stereo:', STEREO_VALUE, ', DOF:', DOF_VALUE
        vizact.ontimer2(2,0,printCondition) # print 2 seconds after program start

    if DOF_VALUE and not PPT1 and not PPT2 and not OCULUS_CAMERA:
        print 'DOF Tracking not enabled. No PPT or Oculus camera present.'
        viz.quit()
    
    startEventFn = vizact.onkeydown(' ', startExperiment)
    # vizact.onkeydown('n', progressToNextStage) # for debugging purposes only
    vizact.onkeydown('f', moveFloor)


