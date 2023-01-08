# -*- coding: utf-8 -*-
#
# MerlinMusicPlayerWidget / MerlinMusicPlayerRMS
#
# Coded by Dr.Best (c) 2017
# Support: www.dreambox-tools.info
# E-Mail: dr.best@dreambox-tools.info
#
# This plugin is open source but it is NOT free software.
#

from merlin_musicplayer.emerlinmusicplayer import eMerlinMusicPlayer, eMerlinMusicPlayerWidget, eMerlinEqualizerWidget
from Components.GUIComponent import GUIComponent
from skin import parseSize, parsePosition, parseColor
from Components.AVSwitch import AVSwitch
from Tools.Directories import resolveFilename, SCOPE_SKIN_IMAGE

def getScale():
	return AVSwitch().getFramebufferScale()

class MerlinMusicPlayerWidget(GUIComponent, object):
	def __init__(self):
		GUIComponent.__init__(self)
		self.filename = ""

	GUI_WIDGET = eMerlinMusicPlayerWidget

	
	def postWidgetCreate(self, instance):
		sc = getScale()
		self.instance.setAspectRatio(sc[0], sc[1])

	def preWidgetRemove(self, instance):
		pass
		
	def visGLRandomPause(self):
		return self.instance.visGLRandomPause()

	def visGLRandomNext(self):
		return self.instance.visGLRandomNext()

	def visGLRandomStart(self):
		return self.instance.visGLRandomStart()				
	
	def setCover(self, filename):
		self.filename = filename
		self.instance.setCover(filename)
	
	def applySkin(self, desktop, screen):
		if self.skinAttributes is not None:
			attribs = [ ]
			for (attrib, value) in self.skinAttributes:
				if attrib == "mode":
					mode = -1
					if value == "visUpDown":
						mode = eMerlinMusicPlayerWidget.modeVisUpDown
					elif value == "visRoundCover":
						mode = eMerlinMusicPlayerWidget.modeVisRoundCover
					elif value == "visImagesUp":
						mode = eMerlinMusicPlayerWidget.modeVisImagesUp
					elif value == "visImagesDown":
						mode = eMerlinMusicPlayerWidget.modeVisImagesDown
					elif value == "cover":
						mode = eMerlinMusicPlayerWidget.modeStandardCover
					elif value == "visUp":
						mode = eMerlinMusicPlayerWidget.modeVisUp
					elif value == "blendCover":
						mode = eMerlinMusicPlayerWidget.modeBlendCover
					elif value == "visGLWaves":
						mode = eMerlinMusicPlayerWidget.modeVisGLWaves
					elif value == "visGLEclipse":
						mode = eMerlinMusicPlayerWidget.modeVisGLEclipse
					elif value == "visGLBalls":
						mode = eMerlinMusicPlayerWidget.modeVisGLBalls
					elif value == "visGLDots":
						mode = eMerlinMusicPlayerWidget.modeVisGLDots
					elif value == "visGLSinus":
						mode = eMerlinMusicPlayerWidget.modeVisGLSinus
					elif value == "visGLRandom":
						mode = eMerlinMusicPlayerWidget.modeVisGLRandom
					self.instance.setMode(int(mode))
				elif attrib == "noCoverAvailablePic":
					self.instance.setNoCoverPic(resolveFilename(SCOPE_SKIN_IMAGE, value))
				elif attrib == "pixmap1":
					self.instance.setPixmap1(resolveFilename(SCOPE_SKIN_IMAGE, value))
				elif attrib == "pixmap2":
					self.instance.setPixmap2(resolveFilename(SCOPE_SKIN_IMAGE, value))
				elif attrib == "distance1":
					self.instance.setDistance1(int(value))
				elif attrib == "distance2":
					self.instance.setDistance2(int(value))
				elif attrib == "threshold1":
					self.instance.setThreshold1(int(value))
				elif attrib == "threshold2":
					self.instance.setThreshold2(int(value))
				elif attrib == "smoothing":
					self.instance.setSmoothValue(float(value))
				elif attrib == "internalSize":
					self.instance.setInternalSize(float(value))
				elif attrib == "blendColor":
					self.instance.setBlendColor(parseColor(value))	
				elif attrib == "drawBackground":
					self.instance.setDrawBackground(int(value))	
				elif attrib == "pixmapBackgroundColor1":
					self.instance.setBackgroundPixmapColor1(parseColor(value))
				elif attrib == "pixmapBackground2":
					self.instance.setBackgroundPixmap2(resolveFilename(SCOPE_SKIN_IMAGE, value))
				elif attrib == "maxValue":
					self.instance.setMaxValue(int(value))
				elif attrib == "fadeOutTime":
					self.instance.setFadeOutTime(int(value))
				else:
					attribs.append((attrib,value))
			self.skinAttributes = attribs
		return GUIComponent.applySkin(self, desktop, screen)


from HTMLComponent import HTMLComponent
from VariableValue import VariableValue
from Components import ProgressBar
from merlin_musicplayer.emerlinmusicplayer import eMerlinMusicPlayerRMSSlider

class MerlinMusicPlayerRMS(VariableValue, HTMLComponent, GUIComponent, object):
	def __init__(self):
		GUIComponent.__init__(self)
		VariableValue.__init__(self)
		self.__start = 0
		self.__end = 100

	GUI_WIDGET = eMerlinMusicPlayerRMSSlider

	def postWidgetCreate(self, instance):
		instance.setRange(self.__start, self.__end)

	def setRange(self, range):
		(__start, __end) = range
		if self.instance is not None:
			self.instance.setRange(__start, __end)

	def getRange(self):
		return (self.__start, self.__end)
		
	def applySkin(self, desktop, screen):
		if self.skinAttributes is not None:
			attribs = [ ]
			for (attrib, value) in self.skinAttributes:
				if attrib == "channel":
					self.instance.setChannel(int(value))
				elif attrib == "mode":
					mode = -1
					if value == "standardEnigmaSlider":
						mode = eMerlinMusicPlayerRMSSlider.modeStandardEnigmaSlider
					elif value == "imagesOrientationUp":
						mode = eMerlinMusicPlayerRMSSlider.modeImagesOrientationUp
					elif value == "imagesOrientationDown":
						mode = eMerlinMusicPlayerRMSSlider.modeImagesOrientationDown
					elif value == "singleImageOrientationUp":
						mode = eMerlinMusicPlayerRMSSlider.modeSingleImageOrientationUp
					elif value == "imagesOrientationLeft":
						mode = eMerlinMusicPlayerRMSSlider.modeImagesOrientationLeft
					elif value == "imagesPeakOrientationUp":
						mode = eMerlinMusicPlayerRMSSlider.modeImageRMSPeakUp
					elif value == "imagesPeakOrientationDown":
						mode = eMerlinMusicPlayerRMSSlider.modeImageRMSPeakDown
					elif value == "imagesPeakOrientationLeft":
						mode = eMerlinMusicPlayerRMSSlider.modeImageRMSPeakLeft
					elif value == "imagesPeakOrientationRight":
						mode = eMerlinMusicPlayerRMSSlider.modeImageRMSPeakRight						
					elif value == "imagesOrientationRight":
						mode = eMerlinMusicPlayerRMSSlider.modeImagesOrientationRight
					elif value == "singleImageOrientationLeft":
						mode = eMerlinMusicPlayerRMSSlider.modeSingleImageOrientationLeft
					elif value == "circle":
						mode = eMerlinMusicPlayerRMSSlider.modeCircle
					elif value == "arc":
						mode = eMerlinMusicPlayerRMSSlider.modeArc
					elif value == "square":
						mode = eMerlinMusicPlayerRMSSlider.modeSquare
					elif value == "vumeter":
						mode = eMerlinMusicPlayerRMSSlider.modeVUMeter
					self.instance.setMode(int(mode))
				elif attrib == "pixmap1":
					self.instance.setPixmap1(resolveFilename(SCOPE_SKIN_IMAGE, value))
				elif attrib == "pixmapBackground1":
					self.instance.setBackgroundPixmap1(resolveFilename(SCOPE_SKIN_IMAGE, value))
				elif attrib == "pixmapBackgroundColor1":
					self.instance.setBackgroundPixmapColor1(parseColor(value))
				elif attrib == "distance":
					self.instance.setDistance(int(value))
				elif attrib == "drawBackground":
					self.instance.setDrawBackground(int(value))
				elif attrib == "maxValue":
					self.instance.setMaxValue(int(value))
				elif attrib == "threshold1":
					self.instance.setThreshold1(int(value))
				elif attrib == "threshold2":
					self.instance.setThreshold2(int(value))										
				elif attrib == "smoothing":
					self.instance.setSmoothValue(float(value))					
				elif attrib == "blendColor":
					self.instance.setBlendColor(parseColor(value))
				elif attrib == "startAngle":
					self.instance.setStartAngle(int(value))
				elif attrib == "clockwise":
					self.instance.setClockwise(int(value))
				elif attrib == "arcAngle":
					self.instance.setArcAngle(int(value))	
				elif attrib == "fadeOutTime":
					self.instance.setFadeOutTime(int(value))
				elif attrib == "vumeterLocation" :
					self.instance.setVUMeterPictureLocation(parsePosition(value, ((1,1),(1,1))))
				elif attrib == "vumeterAxis" :
					self.instance.setVUMeterPictureAxis(parsePosition(value, ((1,1),(1,1))))
				elif attrib == "vumeterAttack":
					self.instance.setVUMeterAttackValue(float(value))						
				elif attrib == "adaption":
					self.instance.setAdaption(float(value))
				else:
					attribs.append((attrib,value))
			self.skinAttributes = attribs
		return GUIComponent.applySkin(self, desktop, screen)			

	range = property(getRange, setRange)

class MerlinEqualizerWidget(GUIComponent, object):
	def __init__(self):
		GUIComponent.__init__(self)

	GUI_WIDGET = eMerlinEqualizerWidget

	def initialize(self):
		self.instance.initialize()

	def setValue(self, value):
		self.instance.setValue(value)
	
	def postWidgetCreate(self, instance):
		sc = getScale()
		self.instance.setAspectRatio(sc[0], sc[1])
