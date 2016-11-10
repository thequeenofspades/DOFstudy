# Copyright (c) 2001-2014 WorldViz LLC.
# All rights reserved.
import viz
import vizdlg
import vizfx.postprocess
from vizfx.postprocess.composite import StereoEffect

# Eye cup flags
EYECUP_A	= 0
EYECUP_B	= 1
EYECUP_C	= 2

# Gender flags
GENDER_UNSPECIFIED	= 0
GENDER_MALE			= 1
GENDER_FEMALE		= 2

# Sensor orientation flags
ORI_DEFAULT	= 0
ORI_RAW		= 1

class _DistortionCorrectionEffect(vizfx.postprocess.BaseShaderEffect):

	def _getFragmentCode(self):
		return """
		uniform vec2 LensCenter;
		uniform vec2 ScreenCenter;
		uniform vec2 Scale;
		uniform vec2 ScaleIn;
		uniform vec4 HmdWarpParam;
		uniform vec4 ChromAbParam;
		uniform sampler2D vizpp_InputTex;

		void main()
		{
			vec2  theta = (gl_TexCoord[0].xy - LensCenter) * ScaleIn; // Scales to [-1, 1]
			float rSq= theta.x * theta.x + theta.y * theta.y;
			vec2  theta1 = theta * (HmdWarpParam.x + HmdWarpParam.y * rSq + HmdWarpParam.z * rSq * rSq + HmdWarpParam.w * rSq * rSq * rSq);

			// Detect whether blue texture coordinates are out of range since these will scaled out the furthest.
			vec2 thetaBlue = theta1 * (ChromAbParam.z + ChromAbParam.w * rSq);
			vec2 tcBlue = LensCenter + Scale * thetaBlue;
			if (!all(equal(clamp(tcBlue, ScreenCenter-vec2(0.5,0.5), ScreenCenter+vec2(0.5,0.5)), tcBlue)))
			{
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
		"""

	def _createUniforms(self):
		self.uniforms.addFloat('Scale',[0.5,0.5])
		self.uniforms.addFloat('ScaleIn',[2.0,2.0])
		self.uniforms.addFloat('LensCenter',[0.5,0.5])
		self.uniforms.addFloat('ScreenCenter',[0.5,0.5])
		self.uniforms.addFloat('HmdWarpParam',[0,0,0,0])
		self.uniforms.addFloat('ChromAbParam',[0,0,0,0])

_extension = None
def getExtension():
	"""Get Oculus extension object"""
	global _extension
	if _extension is None:
		_extension = viz.addExtension('oculus.dle')
	return _extension

def getSensors():
	"""Returns a list of all Oculus sensor objects"""
	return getExtension().getHMDList()

class HMD(viz.EventClass):
	def __init__(self, autoDetectMonitor=True, sensor=None, stereo=viz.STEREO_HORZ, cluster_stereo=None, window=viz.MainWindow):
		viz.EventClass.__init__(self)

		# Get sensor from extension if not specified
		if sensor is None:
			allSensors = getSensors()
			if allSensors:
				sensor = allSensors[0]
			else:
				viz.logError('** ERROR: Failed to detect Oculus HMD')

		#Save parameters
		self._stereo = stereo
		self._cluster_stereo = cluster_stereo
		self._lastAppliedWindow = window
		self._sensor = sensor
		self._effect = StereoEffect(_DistortionCorrectionEffect(),_DistortionCorrectionEffect(),priority=-1000)
		self._hud_root = None

		#Apply settings
		if window is not None:
			self.apply(window)
			if self._sensor:
				vizfx.postprocess.addEffect(self._effect,window)
				vizfx.postprocess.getEffectManager(window).setRenderScale(self._sensor.getRenderScale())

		if autoDetectMonitor:
			monitor = None
			if self._sensor:
				monitor = self._sensor.getMonitorNumber(default=None)
			if monitor is None:
				monitor = self.getMonitorNumber(default=None)
			if monitor is None:
				viz.logWarn('** WARNING: Failed to detect',self.MODEL_NAME,'HMD')
			else:
				viz.window.setFullscreenMonitor(monitor)

		#Handle window size
		self.callback(viz.WINDOW_SIZE_EVENT,self._onSize)
		self._updateViewport()

	@classmethod
	def getMonitorNumber(cls, default=1):
		"""Attempts to detect the monitor number associated with the Sony HMD"""

		# List of detected monitors
		monitors = viz.window.getMonitorList()

		# First check for matching monitors by name
		for m in monitors:
			if 'rift' in m.name.lower():
				return m.id

		# If HMD is behind a splitter, then name won't appear
		# Fallback on checking for matching resolution (1280 x 800)
		# Check in reverse order since HMD is usually a secondary monitor
		for m in reversed(monitors):
			if tuple(m.size) == cls.MODEL_RESOLUTION:
				return m.id

		return default

	def _onSize(self,e):
		"""Update viewport when window is resized"""
		self._updateViewport()

	def _updateViewport(self):
		"""Update HMD viewport setting from current window size"""
		if self._lastAppliedWindow and self._sensor:
			w,h = self._lastAppliedWindow.getSize(viz.WINDOW_PIXELS)
			self._sensor.setViewport([0,0,w,h])
			self._dirty()

	def _dirty(self):
		"""Flag window settings as dirty and update"""
		if self._lastAppliedWindow:
			self.apply(self._lastAppliedWindow)

	def _eventClassRemoved(self):
		self._effect.remove()
		if self._sensor and self._lastAppliedWindow:
			vizfx.postprocess.getEffectManager(self._lastAppliedWindow).setRenderScale(1.0)
		if self._hud_root:
			self._hud_root.remove()

	def remove(self):
		"""Remove the HMD resources"""
		self.unregister()

	def getHUD(self):
		"""Returns the root HUD node"""
		if not self._hud_root:
			root = viz.addGroup()
			root.setReferenceFrame(viz.RF_VIEW)
			root.drawOrder(100000)
			root.disable(viz.DEPTH_TEST)
			root.disable(viz.LIGHTING)
			self._hud_root = root
		return self._hud_root

	def addMessagePanel(self, message, pos=(0,0,3)):
		"""Add a message panel to the HMD HUD"""
		panel = vizdlg.MessagePanel(message, align=viz.ALIGN_CENTER, fontHint=0, parent=self.getHUD())
		panel.setMatrix(viz.Matrix.scale([0.01,0.01,1.0]), node='gui_group')
		panel.setPosition(pos)
		return panel

	def getSensor(self):
		"""Returns HMD sensor"""
		return self._sensor

	def setIPD(self, ipd):
		"""Set IPD of the HMD"""
		if self._sensor:
			self._sensor.setIPD(ipd)
			self._dirty()

	def getIPD(self):
		"""Get IPD of the HMD"""
		if self._sensor:
			return self._sensor.getIPD()
		return 0.0

	def setZoom(self, factor):
		"""Set the FOV zoom factor"""
		if self._sensor:
			self._sensor.setZoom(factor)
			self._dirty()

	def getZoom(self):
		"""Get the FOV zoom factor"""
		if self._sensor:
			return self._sensor.getZoom()
		return 1.0

	def getProfile(self):
		"""Get user profile settings of HMD"""
		if self._sensor:
			return self._sensor.getProfile()
		return None

	def apply(self,window):
		"""Apply HMD settings to specified window"""

		# Apply HMD settings to window
		self._sensor.setIPD(0)
		sensor = self._sensor
		if sensor:
			window.ipd(0)
			for eye in (viz.LEFT_EYE,viz.RIGHT_EYE):
				if eye == viz.LEFT_EYE:
					effect = self._effect.getLeftEffect()
				else:
					effect = self._effect.getRightEffect()
			
				eye_m = viz.LEFT_EYE
				proj = sensor.getProjectionMatrix(eye_m)
				window.setProjectionMatrix(proj,viz.BOTH_EYE)

				effect.uniforms.setValue('LensCenter',sensor.getLensCenter(eye_m))
				effect.uniforms.setValue('ScreenCenter',sensor.getScreenCenter(eye_m))
				effect.uniforms.setValue('HmdWarpParam',sensor.getDistortionParameters(eye_m))
				effect.uniforms.setValue('ChromAbParam',sensor.getChromaticAberrationParameters(eye_m))
				effect.uniforms.setValue('Scale',sensor.getChromaticAberrationScale(eye_m))
				effect.uniforms.setValue('ScaleIn',sensor.getDistortionCoordinateScale(eye_m))

		#Setup correct stereo mode
		if self._cluster_stereo is not None and viz.cluster:
			with viz.cluster.MaskedContext(self._cluster_stereo[0]):
				window.stereo(viz.STEREO_LEFT|viz.HMD)
			with viz.cluster.MaskedContext(self._cluster_stereo[1]):
				window.stereo(viz.STEREO_RIGHT|viz.HMD)
		else:
			window.stereo(self._stereo|viz.HMD)

		#Save applied window
		self._lastAppliedWindow = window

	def createConfigUI(self):
		"""Implement configurable interface"""
		if self._sensor:
			ui = self._sensor.createConfigUI()
			ui.addFloatRangeItem('IPD',[0.0,0.5],fset=self.setIPD,fget=self.getIPD)
			ui.addFloatRangeItem('Zoom',[0.5,2.0],fset=self.setZoom,fget=self.getZoom)
			return ui

class Rift(HMD):
	MODEL_NAME = 'Oculus Rift'
	MODEL_RESOLUTION = (1280,800)

if __name__ == '__main__':

	viz.setMultiSample(8)
	viz.go(viz.FULLSCREEN)

	# Helps reduce latency
	viz.setOption('viz.glFinish',1)

	hmd = Rift()
	hmd.getSensor().setPrediction(True)

	import vizact
	vizact.onkeydown('r',hmd.getSensor().reset)

	MOVE_SPEED = 2.0

	def UpdateView():
		yaw,pitch,roll = hmd.getSensor().getEuler()
		m = viz.Matrix.euler(yaw,0,0)
		m.setPosition(viz.MainView.getPosition())
		dm = viz.getFrameElapsed() * MOVE_SPEED
		if viz.key.isDown(viz.KEY_UP):
			m.preTrans([0,0,dm])
		if viz.key.isDown(viz.KEY_DOWN):
			m.preTrans([0,0,-dm])
		if viz.key.isDown(viz.KEY_LEFT):
			m.preTrans([-dm,0,0])
		if viz.key.isDown(viz.KEY_RIGHT):
			m.preTrans([dm,0,0])
		m.setEuler([yaw,pitch,roll])
		viz.MainView.setMatrix(m)
	vizact.ontimer(0,UpdateView)

	viz.add('piazza.osgb')
	viz.add('piazza_animations.osgb')