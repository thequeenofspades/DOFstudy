import viz
import steamvr
import viztask
import vizinfo
import vizdlg
import random
import time
import spherical_player_Vive

viz.setMultiSample(8)
viz.fov(60)
viz.go()

######VIVE CODE; UNCOMMENT IF USING VIVE######
'''
# Setup SteamVR HMD
hmd = steamvr.HMD()
if not hmd.getSensor():
	sys.exit('SteamVR HMD not detected')
	
# Setup navigation node and link to main view
navigationNode = viz.addGroup()
viewLink = viz.link(navigationNode, viz.MainView)
viewLink.preMultLinkable(hmd.getSensor())
'''

#Add vizinfo panel to display instructions
info = vizinfo.InfoPanel("Press spacebar to choose conditions")

SURVEY_QUESTIONS = [
        'I feel like I am a part of the environment in the presentation.',
        'I feel as though I am participating in the displayed environment.',
        'I feel like the objects in the presentation are surrounding me.',
        'I feel a general discomfort.',
        'I feel dizzy.',
        'I feel nauseous.',
    ]

def pickConditions():
	info.visible(viz.OFF)
	conditions = {}
	#Choose or randomly determine content type (360 video or 3d content)
	contentTypes = ["Random", "Spherical Video", "3D Content"]
	gui = vizinfo.InfoPanel('Choose content type', title='Set Conditions', align=viz.ALIGN_CENTER, icon=False)
	droplist = gui.addItem(viz.addDropList())
	droplist.addItems(contentTypes)
	submitButton = gui.addItem(viz.addButtonLabel('Continue'), align=viz.ALIGN_RIGHT_CENTER)
	yield viztask.waitButtonUp(submitButton)
	conditions['contentType'] = droplist.getItems()[ droplist.getSelection() ]
	if conditions['contentType'] == "Random":
		conditions['contentType'] = random.choice(contentTypes[1:])
		message = conditions['contentType'] + ' randomly chosen as content type\n'
		gui.setText(message)
	else:
		gui.setText('')
	#Choose or randomly determine content from list based on content type
	message = gui.getText() + 'Choose content'
	gui.setText(message)
	if conditions['contentType'] == "Spherical Video":
		contentList = ["Random", "Arbuckle Cafe", "Happy Hopkins Seal", "VISA Patriots", "Zoo"]
	else:
		contentList = ["Random", "Art Gallery", "Earthquake"]
	droplist.clearItems()
	droplist.addItems(contentList)
	yield viztask.waitButtonUp(submitButton)
	conditions['content'] = droplist.getItems()[ droplist.getSelection() ]
	if conditions['content'] == "Random":
		conditions['content'] = random.choice(contentList[1:])
		message = conditions['content'] + ' randomly chosen as content\n'
		gui.setText(message)
	else:
		gui.setText('')
	#Choose or randomly determine DOF condition
	message = gui.getText() + 'Choose degrees of freedom'
	gui.setText(message)
	DOFList = ["Random", "3 Degrees", "6 Degrees"]
	droplist.clearItems()
	droplist.addItems(DOFList)
	yield viztask.waitButtonUp(submitButton)
	conditions['dof'] = droplist.getItems()[ droplist.getSelection() ]
	if conditions['dof'] == "Random":
		conditions['dof'] = random.choice(DOFList[1:])
		message = conditions['dof'] + ' randomly chosen as DOF\n'
		gui.setText(message)
	else:
		gui.setText('')
	#Choose or randomly determine stimuli type
	message = gui.getText() + 'Choose stimuli type'
	gui.setText(message)
	stimuliTypes = ["Random", "Auditory", "Haptic"]
	droplist.clearItems()
	droplist.addItems(stimuliTypes)
	yield viztask.waitButtonUp(submitButton)
	conditions['stimuliType'] = droplist.getItems()[ droplist.getSelection() ]
	if conditions['stimuliType'] == "Random":
		conditions['stimuliType'] = random.choice(stimuliTypes[1:])
		message = conditions['stimuliType'] + ' randomly chosen as stimuli type\n'
		gui.setText(message)
	else:
		gui.setText('')
	droplist.remove()
	yield viztask.waitButtonUp(submitButton)
	gui.remove()
	viztask.returnValue(conditions)
	
def addContent(type, content):
	if type == "Spherical Video":
		videoFiles = {"Arbuckle Cafe": "Arbuckle_11-9-16.mp4", "Happy Hopkins Seal": "happyhopkinsseal_2min.mp4",
						"VISA Patriots": "VISA Patriots.mp4", "Zoo": "zoo2.mp4"}
		videoFile = "360 Videos/" + videoFiles[content]
		player = spherical_player_Vive.Player(videoFile, radius=2.7, playPauseKey='p')
	
def track():
	info.visible(viz.OFF)
	#TODO: set DOF based on conditions and set up tracking
	data = {'stimuli1': 0.0, 'stimuli2': 0.0, 'tracking': []}
	#track for 1 minute
	elapsed = 0.0
	#generate two random times at least 5 seconds apart between elapsed time 5 seconds and 55 seconds
	while abs(data['stimuli1'] - data['stimuli2']) < 5.0:
		data['stimuli1'] = round(random.uniform(5.0,55.0), 1)
		data['stimuli2'] = round(random.uniform(5.0,55.0), 1)
	while elapsed < 60.0:
		#TODO: append tracking data to data['tracking']
		if abs(elapsed - data['stimuli1']) < 0.05:
			#TODO: trigger high-intensity stimuli
			print "Stimuli 1"
		if abs(elapsed - data['stimuli2']) < 0.05:
			#TODO: trigger low-intensity stimuli
			print "Stimuli 2"
		yield viztask.waitTime(0.1)
		elapsed = elapsed + 0.1
	print "Done!"
	viztask.returnValue(data)

def study_flow():
	#Wait for spacebar to choose conditions
	yield viztask.waitKeyDown(' ')
	conditions = yield pickConditions()
	addContent(conditions['contentType'], conditions['content'])
	info.visible(viz.ON)
	info.setText('Press spacebar to begin tracking')
	yield viztask.waitKeyDown(' ')
	data = yield track()
	print "Here"
	info.visible(viz.ON)
	info.setText('Press spacebar to answer survey questions')
	yield viztask.waitKeyDown(' ')
	answers = yield surveyQuestions()
	#Log results to file
	try:
		with open('participant_data.txt','w') as f:
			#write participant data to file
			f.write("Conditions\n")
			for key in conditions.keys():
				line = key + ": " + conditions[key]
				f.write(line)
				f.write("\n")
			f.write("\nTracking\n")
			f.write(str(data['stimuli1']))
			f.write("\n")
			f.write(str(data['stimuli2']))
			f.write("\n")
			for line in data['tracking']:
				f.write(str(line))
				f.write("\n")
			f.write("\nSurvey\n")
			for line in answers:
				f.write(str(line))
				f.write("\n")
	except IOError:
		viz.logWarn('Could not log results to file. Make sure you have permission to write to folder')
	info.visible(viz.ON)
	info.setText('Press spacebar to exit')
	yield viztask.waitKeyDown(' ')
	viz.quit()

def surveyQuestions():
	#Hide info panel currently displayed
	info.visible(viz.OFF)
	answers = []
	#Display each question along with a dropdown menu for response
	for question in SURVEY_QUESTIONS:
		surveyQuestions = vizinfo.InfoPanel('',title='Survey Question',align=viz.ALIGN_CENTER, icon=False)
		surveyQuestions.addItem(viz.addText(question))
		droplist = surveyQuestions.addItem(viz.addDropList())
		droplist.addItems(["Not at all accurate", "Slightly inaccurate", "Neither accurate nor inaccurate", "Slightly accurate", "Very accurate"])
		submitButton = surveyQuestions.addItem(viz.addButtonLabel('Continue'), align=viz.ALIGN_RIGHT_CENTER)
		yield viztask.waitButtonUp(submitButton)
		answers.append(droplist.getItems()[ droplist.getSelection() ])
		surveyQuestions.remove()
	viztask.returnValue(answers)

viztask.schedule(study_flow)