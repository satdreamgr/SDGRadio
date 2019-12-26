from Components.ActionMap import ActionMap
from Components.AVSwitch import AVSwitch
from Components.config import config, getConfigListEntry, ConfigSubsection, ConfigText, ConfigSelection, ConfigSlider, ConfigYesNo
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Pixmap import Pixmap, MultiPixmap
from Components.Sources.StaticText import StaticText
from Plugins.Plugin import PluginDescriptor
from Screens.ChoiceBox import ChoiceBox
from Screens.Console import Console
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Tools.BoundFunction import boundFunction
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from enigma import eConsoleAppContainer, ePicLoad

import os
import json
import time
import binascii
from decimal import Decimal
from collections import OrderedDict

try:
	from enigma import addFont
	addFont(resolveFilename(SCOPE_PLUGINS, "Extensions/SDGRadio/fonts/mssdr-digitali.ttf"), "Digital", 90, 1)
except:
	print "[SDGRadio] failed to add font"


class ConfigTextSlider(ConfigSlider):
	def __init__(self, default=0, increment=1, limits=(0, 100)):
		ConfigSlider.__init__(self, default, increment, limits)

	def getText(self):
		return str(self.value)

	def getMulti(self, selected):
		self.checkValues()
		return ("text", str(self.value))


config.sdgradio = ConfigSubsection()
config.sdgradio.frequency_fm = ConfigText(default="87.5")
config.sdgradio.frequency_nfm = ConfigText(default="87.5")
config.sdgradio.frequency_am = ConfigText(default="0.53")
config.sdgradio.frequency_lsb = ConfigText(default="0.53")
config.sdgradio.frequency_usb = ConfigText(default="0.53")
config.sdgradio.frequency_dab = ConfigText(default="174.928")
config.sdgradio.presets_fm = ConfigText(default="0,0,0,0,0,0,0,0,0,0")
config.sdgradio.presets_nfm = ConfigText(default="0,0,0,0,0,0,0,0,0,0")
config.sdgradio.presets_am = ConfigText(default="0,0,0,0,0,0,0,0,0,0")
config.sdgradio.presets_lsb = ConfigText(default="0,0,0,0,0,0,0,0,0,0")
config.sdgradio.presets_usb = ConfigText(default="0,0,0,0,0,0,0,0,0,0")
config.sdgradio.presets_dab = ConfigText(default="0,0,0,0,0,0,0,0,0,0")
config.sdgradio.rds = ConfigYesNo(default=False)
config.sdgradio.modulation = ConfigSelection(default="fm", choices=[
	("fm", _("FM")),
	("nfm", _("NFM")),
	("am", _("AM")),
	("lsb", _("LSB")),
	("usb", _("USB")),
	("dab", _("DAB/DAB+"))
])
config.sdgradio.ppmoffset = ConfigTextSlider(default=0, limits=(-100, 100))
config.sdgradio.fmgain = ConfigTextSlider(default=20, limits=(0, 50))
choicelist = [("automatic", _("Auto"))]
for i in range(0, 51): # 0 to 50
	choicelist.append((str(i)))
config.sdgradio.gain = ConfigSelection(default="50", choices=choicelist)
config.sdgradio.bandwidth = ConfigTextSlider(default=20, limits=(1, 32))
config.sdgradio.fmbandwidth = ConfigTextSlider(default=171, limits=(50, 180))
config.sdgradio.sbbandwidth = ConfigTextSlider(default=5, limits=(1, 16))
config.sdgradio.pcm = ConfigYesNo(default=False)
config.sdgradio.usepartial = ConfigYesNo(default=False)
config.sdgradio.userbds = ConfigYesNo(default=False)
config.sdgradio.fmregion = ConfigSelection(default="eu-int", choices=[
	("eu-int", _("Europe/World")),
	("amer", _("America")),
	("ru", _("Russia")),
	("jp", _("Japan")),
	("free", _("Free tuning"))
])
config.sdgradio.edge = ConfigYesNo(default=False)
config.sdgradio.dc = ConfigYesNo(default=False)
config.sdgradio.deemp = ConfigYesNo(default=False)
config.sdgradio.direct = ConfigYesNo(default=False)
config.sdgradio.offset = ConfigYesNo(default=False)


DAB_FREQ = OrderedDict([(Decimal("174.928"), "5A"), (Decimal("176.640"), "5B"), (Decimal("178.352"), "5C"), (Decimal("180.064"), "5D"),
						(Decimal("181.936"), "6A"), (Decimal("183.648"), "6B"), (Decimal("185.360"), "6C"), (Decimal("187.072"), "6D"),
						(Decimal("188.928"), "7A"), (Decimal("190.640"), "7B"), (Decimal("192.352"), "7C"), (Decimal("194.064"), "7D"),
						(Decimal("195.936"), "8A"), (Decimal("197.648"), "8B"), (Decimal("199.360"), "8C"), (Decimal("201.072"), "8D"),
						(Decimal("202.928"), "9A"), (Decimal("204.640"), "9B"), (Decimal("206.352"), "9C"), (Decimal("208.064"), "9D"),
						(Decimal("209.936"), "10A"), (Decimal("211.648"), "10B"), (Decimal("213.360"), "10C"), (Decimal("215.072"), "10D"),
						(Decimal("216.928"), "11A"), (Decimal("218.640"), "11B"), (Decimal("220.352"), "11C"), (Decimal("222.064"), "11D"),
						(Decimal("223.936"), "12A"), (Decimal("225.648"), "12B"), (Decimal("227.360"), "12C"), (Decimal("229.072"), "12D"),
						(Decimal("230.748"), "13A"), (Decimal("232.496"), "13B"), (Decimal("234.208"), "13C"), (Decimal("235.776"), "13D"),
						(Decimal("237.488"), "13E"), (Decimal("239.200"), "13F")])


class SDGRadioSetup(ConfigListScreen, Screen):

	def __init__(self, session):
		Screen.__init__(self, session)
		self.setTitle(_("SDGRadio setup"))
		self.skinName = ["SDGRadioSetup", "Setup"]

		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("Ok"))
		self["description"] = Label("") # filled automatically when calling createSummary()

		self["setupActions"] = ActionMap(["OkCancelActions", "ColorActions"],
			{
				"cancel": self.keyCancel,
				"red":self.keyCancel,
				"ok": self.keySave,
				"green": self.keySave
			}, -2)

		configlist = []

		configlist.append(getConfigListEntry(_('PPM Offset:'),
			config.sdgradio.ppmoffset,
			_('Use PPM Offset to correct oscillator frequency. Get value using rtl_test -p or kalibrate')))

		configlist.append(getConfigListEntry(_('Tuner gain for FM:'),
			config.sdgradio.fmgain,
			_('Set the tuner gain value for FM band (default = 20)')))

		configlist.append(getConfigListEntry(_('Tuner gain for other bands and DAB:'),
			config.sdgradio.gain,
			_('Set the tuner gain value for all bands and DAB/DAB+ except FM')))

		configlist.append(getConfigListEntry(_('Bandwidth for FM in k/sec:'),
			config.sdgradio.fmbandwidth,
			_('Set the frequency bandwidth for FM band. For RDS set to 171 (default = 171k)')))

		configlist.append(getConfigListEntry(_('Bandwidth for NFM/AM in k/sec:'),
			config.sdgradio.bandwidth,
			_('Set the frequency bandwidth for NFM and AM bands (default = 20k)')))

		configlist.append(getConfigListEntry(_('Bandwidth for USB/LSB in k/sec:'),
			config.sdgradio.sbbandwidth,
			_('Set the frequency bandwidth for USB and LSB bands (default = 5k)')))

		configlist.append(getConfigListEntry(_('FM Region:'),
			config.sdgradio.fmregion,
			_('Select FM band range by region. "Russia" provides full FM band (64-108 MHz), Europe/World (87.5 - 108 MHz), Japan (76-95 MHz), America (88.1-107.9 MHz). "Free tuning" disables FM limits')))

		configlist.append(getConfigListEntry(_('Use partial info for RDS:'),
			config.sdgradio.usepartial,
			_('Use partial info for RDS data before it is fully received. This could be useful when reception is noisy')))

		configlist.append(getConfigListEntry(_('Use RBDS instead or RDS:'),
			config.sdgradio.userbds,
			_('Use RBDS data instead of the ordinary RDS info (if region is "America", RBDS is selected automatically)')))

		configlist.append(getConfigListEntry(_('PCM:'),
			config.sdgradio.pcm,
			_('Output PCM instead of AAC/MPEG when using DAB/DAB+')))

		configlist.append(getConfigListEntry(_('Enable lower edge tuning:'),
			config.sdgradio.edge,
			_('Enable lower edge tuning for analog radio')))

		configlist.append(getConfigListEntry(_('Enable DC:'),
			config.sdgradio.dc,
			_('Enable DC blocking filter')))

		configlist.append(getConfigListEntry(_('Enable de-emphasis:'),
			config.sdgradio.deemp,
			_('Enable the de-emphasis filter')))

		configlist.append(getConfigListEntry(_('Enable direct sampling:'),
			config.sdgradio.direct,
			_('Enable direct sampling for the tuner')))

		configlist.append(getConfigListEntry(_('Enable offset tuning:'),
			config.sdgradio.offset,
			_('Enable offset tuning')))

		ConfigListScreen.__init__(self, configlist, session)


class SDGRadioScreen(Screen):

	skin = """
		<screen name="SDGRadioScreen" title="SDG radio" position="center,center" size="680,460">
			<ePixmap pixmap="buttons/red.png" position="0,0" size="40,40" alphatest="blend"/>
			<ePixmap pixmap="buttons/green.png" position="170,0" size="40,40" alphatest="blend"/>
			<ePixmap pixmap="buttons/yellow.png" position="340,0" size="40,40" alphatest="blend"/>
			<ePixmap pixmap="buttons/blue.png" position="510,0" size="40,40" alphatest="blend"/>
			<widget source="key_red" render="Label" position="40,0" zPosition="1" size="130,40" font="Regular;20" valign="center" transparent="1"/>
			<widget source="key_green" render="Label" position="210,0" zPosition="1" size="130,40" font="Regular;20" valign="center" transparent="1"/>
			<widget source="key_yellow" render="Label" position="380,0" zPosition="1" size="130,40" font="Regular;20" valign="center" transparent="1"/>
			<widget source="key_blue" render="Label" position="550,0" zPosition="1" size="130,40" font="Regular;20" valign="center" transparent="1"/>
			<widget name="freq" position="0,80" size="450,120" font="Digital;60" valign="center" halign="center"/>
			<widget name="prog_type" position="0,200" size="450,40" font="Regular;24" valign="center" halign="center"/>
			<widget name="pi" position="0,240" size="150,40" font="Regular;24" valign="center" halign="center"/>
			<widget name="traffic" position="150,240" size="150,40" font="Regular;24" valign="center" halign="center"/>
			<widget name="af" position="300,240" size="150,40" font="Regular;24" valign="center" halign="center"/>
			<widget name="eon" position="0,280" size="150,40" font="Regular;24" valign="center" halign="center"/>
			<widget name="ct" position="150,280" size="150,40" font="Regular;24" valign="center" halign="center"/>
			<widget name="rt+" position="300,280" size="150,40" font="Regular;24" valign="center" halign="center"/>
			<widget name="radiotext" position="0,320" size="680,80" font="Regular;24" valign="center" halign="center"/>
			<widget name="pic" position="480,80" size="200,200" alphatest="blend"/>
			<widget name="mem_0" pixmaps="/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/mem_0_empty.png,/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/mem_0_stored.png,/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/mem_0_selected.png" position="190,420" size="40,40" alphatest="blend"/>
			<widget name="mem_1" pixmaps="/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/mem_1_empty.png,/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/mem_1_stored.png,/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/mem_1_selected.png" position="240,420" size="40,40" alphatest="blend"/>
			<widget name="mem_2" pixmaps="/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/mem_2_empty.png,/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/mem_2_stored.png,/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/mem_2_selected.png" position="290,420" size="40,40" alphatest="blend"/>
			<widget name="mem_3" pixmaps="/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/mem_3_empty.png,/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/mem_3_stored.png,/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/mem_3_selected.png" position="340,420" size="40,40" alphatest="blend"/>
			<widget name="mem_4" pixmaps="/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/mem_4_empty.png,/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/mem_4_stored.png,/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/mem_4_selected.png" position="390,420" size="40,40" alphatest="blend"/>
			<widget name="mem_5" pixmaps="/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/mem_5_empty.png,/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/mem_5_stored.png,/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/mem_5_selected.png" position="440,420" size="40,40" alphatest="blend"/>
			<widget name="mem_6" pixmaps="/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/mem_6_empty.png,/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/mem_6_stored.png,/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/mem_6_selected.png" position="490,420" size="40,40" alphatest="blend"/>
			<widget name="mem_7" pixmaps="/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/mem_7_empty.png,/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/mem_7_stored.png,/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/mem_7_selected.png" position="540,420" size="40,40" alphatest="blend"/>
			<widget name="mem_8" pixmaps="/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/mem_8_empty.png,/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/mem_8_stored.png,/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/mem_8_selected.png" position="590,420" size="40,40" alphatest="blend"/>
			<widget name="mem_9" pixmaps="/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/mem_9_empty.png,/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/mem_9_stored.png,/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/mem_9_selected.png" position="640,420" size="40,40" alphatest="blend"/>
			<ePixmap pixmap="buttons/key_info.png" position="0,420" size="40,40" alphatest="blend"/>
			<ePixmap pixmap="buttons/key_menu.png" position="50,420" size="40,40" alphatest="blend"/>
		</screen>"""

	def __init__(self, session):
		self.modulation = config.sdgradio.modulation
		self.frequency = eval("config.sdgradio.frequency_%s" % self.modulation.value)
		self.playbackFrequency = None # currently playing frequency
		self.playbackPreset = None # currently playing preset
		self.presets = [] # preset list for current modulation
		self.log = [] # log messages
		self.programs = [] # DAB program list
		self.console = None

		Screen.__init__(self, session)
		self.setTitle(_("SDG radio"))

		for i in range(0, 10):
			self["mem_%d" % i] = MultiPixmap()

		self["freq"] = Label()
		self["radiotext"] = Label()
		self["prog_type"] = Label()
		self["pi"] = Label()
		self["traffic"] = Label()
		self["af"] = Label()
		self["ct"] = Label()
		self["eon"] = Label()
		self["rt+"] = Label()
		self["pic"] = Pixmap()

		self["key_red"] = StaticText(self.modulation.getText())
		self["key_green"] = StaticText(_("Play"))
		self["key_yellow"] = StaticText("")
		self["key_blue"] = StaticText(_("Log"))

		self["actions"] = ActionMap(["SDGRadioActions"],
		{
			"cancel": self.cancel,
			"ok": self.selectFreq,

			"info": self.showInfo,
			"menu": self.showMenu,
			"file": self.showPrograms,

			"red": self.toggleModulation,
			"green": self.togglePlayback,
			"yellow": self.yellow,
			"blue": self.showLog,

			"0": boundFunction(self.selectPreset, 0),
			"1": boundFunction(self.selectPreset, 1),
			"2": boundFunction(self.selectPreset, 2),
			"3": boundFunction(self.selectPreset, 3),
			"4": boundFunction(self.selectPreset, 4),
			"5": boundFunction(self.selectPreset, 5),
			"6": boundFunction(self.selectPreset, 6),
			"7": boundFunction(self.selectPreset, 7),
			"8": boundFunction(self.selectPreset, 8),
			"9": boundFunction(self.selectPreset, 9),

			"long0": boundFunction(self.storePreset, 0),
			"long1": boundFunction(self.storePreset, 1),
			"long2": boundFunction(self.storePreset, 2),
			"long3": boundFunction(self.storePreset, 3),
			"long4": boundFunction(self.storePreset, 4),
			"long5": boundFunction(self.storePreset, 5),
			"long6": boundFunction(self.storePreset, 6),
			"long7": boundFunction(self.storePreset, 7),
			"long8": boundFunction(self.storePreset, 8),
			"long9": boundFunction(self.storePreset, 9),

			"right": boundFunction(self.freqUp, "1"),
			"left": boundFunction(self.freqDown, "1"),
			"rightRepeated": boundFunction(self.freqUp, "1"),
			"leftRepeated": boundFunction(self.freqDown, "1"),

			"up": boundFunction(self.freqUp, "0.1"),
			"down": boundFunction(self.freqDown, "0.1"),
			"upRepeated": boundFunction(self.freqUp, "0.1"),
			"downRepeated": boundFunction(self.freqDown, "0.1"),

			"nextMarker": boundFunction(self.freqUp, "0.001"),
			"prevMarker": boundFunction(self.freqDown, "0.001"),

			"nextBouquet": boundFunction(self.freqUp, "0.0001"),
			"prevBouquet": boundFunction(self.freqDown, "0.0001"),
		}, -2)

		self.onLayoutFinish.extend([self.getPresets, self.updateFreq, self.yellowText, self.getConfigOptions])

		self.oldService = self.session.nav.getCurrentlyPlayingServiceReference() # get currently playing service
		self.session.nav.stopService() # stop currently playing service
		eConsoleAppContainer().execute("showiframe /usr/share/enigma2/radio.mvi") # display radio mvi
		#self.Scale = AVSwitch().getFramebufferScale()

	def getConfigOptions(self):
		self.ppmoffset = config.sdgradio.ppmoffset.value
		self.fmgain = config.sdgradio.fmgain.value
		self.gain = config.sdgradio.gain.value
		self.fmbandwidth = config.sdgradio.fmbandwidth.value
		self.bandwidth = config.sdgradio.bandwidth.value
		self.sbbandwidth = config.sdgradio.sbbandwidth.value
		self.fmregion = config.sdgradio.fmregion.value
		self.usepartial = config.sdgradio.usepartial.value
		self.userbds = config.sdgradio.userbds.value
		self.pcm = config.sdgradio.pcm.value
		self.edge = config.sdgradio.edge.value
		self.dc = config.sdgradio.dc.value
		self.deemp = config.sdgradio.deemp.value
		self.direct = config.sdgradio.direct.value
		self.offset = config.sdgradio.offset.value

	def updateScreen(self, play=False):
		self["radiotext"].setText("")
		self["prog_type"].setText("")
		self["pi"].setText("")
		self["traffic"].setText("")
		self["af"].setText("")
		self["ct"].setText("")
		self["eon"].setText("")
		self["rt+"].setText("")
		if play is False:
			self["key_green"].setText(_("Play"))
			self.setTitle(_("SDG radio"))
			if self.playbackPreset:
				self["mem_%d" % self.playbackPreset].setPixmapNum(1) # preset stored
		else:
			self["key_green"].setText(_("Stop"))
			self.setTitle(_("SDG radio %s") % self["freq"].getText())

	def updateFreq(self):
		if self.modulation.value in ("am", "lsb", "usb"):
			freq = str(Decimal(self.frequency.value) * 1000)
			units = "KHz"
		else:
			freq = self.frequency.value
			units = "MHz"
		dab = DAB_FREQ.get(Decimal(self.frequency.value), "") if self.modulation.value == "dab" else ""
		txt = "  ".join(filter(None, (dab, freq, units)))
		self["freq"].setText(txt)

	def stopRadio(self):
		self.doConsoleStop()
		self.updateScreen(False)
		self.playbackFrequency = None
		self.playbackPreset = None

	def playRadio(self):
		self.doConsoleStop()
		self.updateScreen(True)
		time.sleep(0.3)
		self.console = eConsoleAppContainer()
		self.console.stderrAvail.append(self.cbStderrAvail)
		#self.console.appClosed.append(self.cbAppClosed)

		if self.modulation.value == "fm":
			if config.sdgradio.rds.value:
				cmd = "rtl_fm -f %sM -M fm -l 0 -A std -s %sk -g %s -p %d %s %s %s %s %s -F 9 - | %s | gst-launch-1.0 fdsrc ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=%s000 ! audioresample ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=48000 ! dvbaudiosink" % (self.frequency.value, self.fmbandwidth, self.fmgain, self.ppmoffset, self.getEdge(), self.getDc(), self.getDeemp(), self.getDirect(), self.getOffset(), self.rdsOptions(), self.fmbandwidth)
			else:
				cmd = "rtl_fm -f %sM -M fm -l 0 -A std -s %sk -g %s -p %d %s %s %s %s %s -F 0 - | gst-launch-1.0 fdsrc ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=%s000 ! audioresample ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=48000 ! dvbaudiosink" % (self.frequency.value, self.fmbandwidth, self.fmgain, self.ppmoffset, self.getEdge(), self.getDc(), self.getDeemp(), self.getDirect(), self.getOffset(), self.fmbandwidth)
		elif self.modulation.value == "nfm":
			cmd = "rtl_fm -f %sM -M fm -A std -s %sk -g %s -p %d %s %s %s %s %s - | gst-launch-1.0 fdsrc ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=%s000 ! audioresample ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=48000 ! dvbaudiosink" % (self.frequency.value, self.bandwidth, self.gain, self.ppmoffset, self.getEdge(), self.getDc(), self.getDeemp(), self.getDirect(), self.getOffset(), self.bandwidth)
		elif self.modulation.value == "am":
			cmd = "rtl_fm -f %sM -M am -A std -s %sk -g %s -p %d %s %s %s %s %s - | gst-launch-1.0 fdsrc ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=%s000 ! audioresample ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=48000 ! dvbaudiosink" % (self.frequency.value, self.bandwidth, self.gain, self.ppmoffset, self.getEdge(), self.getDc(), self.getDeemp(), self.getDirect(), self.getOffset(), self.bandwidth)
		elif self.modulation.value == "lsb":
			cmd = "rtl_fm -f %sM -M lsb -A std -s %sk -g %s -p %d %s %s %s %s %s - | gst-launch-1.0 fdsrc ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=%s000 ! audioresample ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=48000 ! dvbaudiosink" % (self.frequency.value, self.sbbandwidth, self.gain, self.ppmoffset, self.getEdge(), self.getDc(), self.getDeemp(), self.getDirect(), self.getOffset(), self.sbbandwidth)
		elif self.modulation.value == "usb":
			cmd = "rtl_fm -f %sM -M usb -A std -s %sk -g %s -p %d %s %s %s %s %s - | gst-launch-1.0 fdsrc ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=%s000 ! audioresample ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=48000 ! dvbaudiosink" % (self.frequency.value, self.sbbandwidth, self.gain, self.ppmoffset, self.getEdge(), self.getDc(), self.getDeemp(), self.getDirect(), self.getOffset(), self.sbbandwidth)
		elif self.modulation.value == "dab":
			if self.pcm:
				cmd = "dab-rtlsdr-sdgradio-pcm -C %s -W30 -p %d %s | gst-launch-1.0 fdsrc ! audio/x-raw, format=S16LE, channels=2, layout=interleaved, rate=48000 ! dvbaudiosink" % (DAB_FREQ.get(Decimal(self.frequency.value), "5A"), self.ppmoffset, self.getDabGain())
			else:
				cmd = "dab-rtlsdr-sdgradio -C %s -W30 -p %d %s | gst-launch-1.0 fdsrc ! faad ! dvbaudiosink" % (DAB_FREQ.get(Decimal(self.frequency.value), "5A"), self.ppmoffset, self.getDabGain())
		else:
			cmd = "rtl_fm -f %sM -M wbfm -s 200000 -r 48000 - | gst-launch-1.0 fdsrc ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=48000 ! dvbaudiosink" % self.frequency.value

		print "[SDGRadio] playRadio cmd: %s" % cmd
		self.console.execute(cmd)

	def processRds(self, data):
		try:
			rds = json.loads(data.decode("utf8", "ignore"))

			if "ps" in rds and self.getTitle() != rds["ps"].encode("utf8"):
				self.setTitle(rds["ps"].encode("utf8"))
				self["pic"].hide()

			if "partial_ps" in rds and self.getTitle() != rds["partial_ps"].encode("utf8"):
				self.setTitle(rds["partial_ps"].encode("utf8"))
				self["pic"].hide()

			if "radiotext" in rds and self["radiotext"].getText() != rds["radiotext"].encode("utf8"):
				self["radiotext"].setText(rds["radiotext"].encode("utf8"))

			if "partial_radiotext" in rds and self["radiotext"].getText() != rds["partial_radiotext"].encode("utf8"):
				self["radiotext"].setText(rds["partial_radiotext"].encode("utf8"))

			if "prog_type" in rds and self["prog_type"].getText() != rds["prog_type"].encode("utf8"):
				self["prog_type"].setText(rds["prog_type"].encode("utf8"))

			if "pi" in rds and not "callsign" in rds and self["pi"].getText() != rds["pi"].encode("utf8"):
				self["pi"].setText(rds["pi"].encode("utf8").replace("0x","PI: "))

			if "callsign" in rds and self["pi"].getText() != rds["callsign"].encode("utf8"):
				self["pi"].setText(rds["callsign"].encode("utf8"))

			if "callsign_uncertain" in rds and self["pi"].getText() != rds["callsign_uncertain"].encode("utf8"):
				self["pi"].setText(rds["callsign_uncertain"].encode("utf8"))

			if "programType" in rds:
				txt = u"%s kbps %s %s" % (rds["bitrate"], rds["dabType"], rds["programType"])
				self["prog_type"].setText(txt.encode("utf8"))

			if "programName" in rds and "programId" in rds:
				self.programs.append((rds["programName"].encode("utf8"), rds["programId"]))

			if "mot" in rds:
				self.showPicture(rds["mot"].encode("utf8"))

			if "alt_kilohertz" in rds and self["af"].getText() != rds["alt_kilohertz"]:
				self["af"].setText("AF")

			if "other_network" in rds and self["eon"].getText() != rds["other_network"]:
				self["eon"].setText("EON")

			if "clock_time" in rds:
				self["ct"].setText("CT")

			if "radiotext_plus" in rds:
				self["rt+"].setText("RT+")

			traffic = ""
			if "tp" in rds and str(rds["tp"]) == "True":
				traffic = "TP"
			if "ta" in rds and str(rds["ta"]) == "True":
				if traffic:
					traffic += " TA"
				else:
					traffic = "TA"
			self["traffic"].setText(traffic)

		except Exception as e:
			msg = "processRds exception: %s data: %s" % (e, binascii.hexlify(data))
			self.log.append(str)
			print "[SDGRadio] %s" % msg

	def rdsOptions(self):
		if self.usepartial and not self.userbds:
			return "redsea -e -p"
		elif not self.usepartial and self.userbds or not self.usepartial and self.fmregion == "amer":
			return "redsea -e -u"
		elif self.usepartial and self.userbds or self.usepartial and self.fmregion == "amer":
			return "redsea -e -p -u"
		else:
			return "redsea -e"

	def getDabGain(self):
		return "-G %s" % self.gain if self.gain != "automatic" else "-Q"

	def getEdge(self):
		return "-E edge" if self.edge is True else ""

	def getDc(self):
		return "-E dc" if self.dc is True else ""

	def getDeemp(self):
		return "-E deemp" if self.deemp is True else ""

	def getDirect(self):
		return "-E direct" if self.direct is True else ""

	def getOffset(self):
		return "-E offset" if self.offset is True else ""

	def cbStderrAvail(self, data):
		#print "[SDGRadio] cbStderrAvail ", data
		for line in data.splitlines():
			if not line:
				continue
			if "{" in line and "}" in line and ":" in line:
				self.processRds(line)
		if not data in self.log:
			self.log.append(data)
		while len(self.log) > 200:
			self.log.pop(0)

	def doConsoleStop(self):
		if self.console:
			self.console.sendCtrlC()
			self.console.sendEOF()
			if self.console.running():
				self.console.kill()
			self.console = None
			self.log = []
			self.programs = []

	def selectFreq(self):
		if self.frequency.value != self.playbackFrequency:
			selPreset = self.playbackPreset
			if selPreset:
				self["mem_%d" % selPreset].setPixmapNum(1) # preset stored
			self.playbackFrequency = self.frequency.value
			self.playbackPreset = None
			self.playRadio()

	def freqUp(self, value):
		self.freqChange(Decimal(value))

	def freqDown(self, value):
		self.freqChange(-Decimal(value))

	def freqChange(self, value):
		oldFreq = self.frequency.value
		newFreq = Decimal(oldFreq) + value
		if self.modulation.value == "fm" and self.fmregion == "ru":
			if newFreq < Decimal("64.0"):
				newFreq = Decimal("64.0")
			if newFreq > Decimal("108.0"):
				newFreq = Decimal("108.0")
		elif self.modulation.value == "fm" and self.fmregion == "eu-int":
			if newFreq < Decimal("87.5"):
				newFreq = Decimal("87.5")
			if newFreq > Decimal("108.0"):
				newFreq = Decimal("108.0")
		elif self.modulation.value == "fm" and self.fmregion == "jp":
			if newFreq < Decimal("76.0"):
				newFreq = Decimal("76.0")
			if newFreq > Decimal("95.0"):
				newFreq = Decimal("95.0")
		elif self.modulation.value == "fm" and self.fmregion == "amer":
			if newFreq < Decimal("88.1"):
				newFreq = Decimal("88.1")
			if newFreq > Decimal("107.9"):
				newFreq = Decimal("107.9")
		elif self.modulation.value == "fm" and self.fmregion == "free":
			if newFreq < Decimal("0.0"):
				newFreq = Decimal("0.0")
			if newFreq > Decimal("1766.0"):
				newFreq = Decimal("1766.0")
		elif self.modulation.value == "dab":
			if newFreq < Decimal("174.928"):
				newFreq = Decimal("174.928")
			if newFreq > Decimal("239.2"):
				newFreq = Decimal("239.2")
			if newFreq > Decimal(oldFreq):
				newFreq = min(filter(lambda x: x >= newFreq, DAB_FREQ.keys()))
			else:
				newFreq = max(filter(lambda x: x <= newFreq, DAB_FREQ.keys()))
		else:
			if newFreq < Decimal("0.0"):
				newFreq = Decimal("0.0")
			if newFreq > Decimal("1766.0"):
				newFreq = Decimal("1766.0")
		self.frequency.value = str(newFreq)
		self.frequency.save()
		self.updateFreq()

	def getPresets(self):
		self.presets = []
		presetsConfig = eval("config.sdgradio.presets_%s" % self.modulation.value)
		presets = presetsConfig.value.split(",")
		for index, preset in enumerate(presets):
			self.presets.append(preset)
			if preset == "0":
				self["mem_%d" % index].setPixmapNum(0) # preset empty
			else:
				self["mem_%d" % index].setPixmapNum(1) # preset stored

	def selectPreset(self, number):
		newFreq = self.presets[number]
		selPreset = self.playbackPreset
		if newFreq != "0" and number != selPreset: # preset not empty and not already selected
			self["mem_%d" % number].setPixmapNum(2) # preset selected
			if selPreset:
				self["mem_%d" % selPreset].setPixmapNum(1) # preset stored
			self.frequency.value = newFreq
			self.frequency.save()
			self.playbackFrequency = newFreq
			self.playbackPreset = number
			self.updateFreq()
			self.playRadio()

	def storePreset(self, number):
		currentFreq = self.frequency.value
		if currentFreq in ("", "0"):
			msg = _("Error storing memory preset! Please select a valid frequency and try again.")
		else:
			self.presets[number] = currentFreq
			self["mem_%d" % number].setPixmapNum(1) # preset stored
			msg = _("Selected frequency of %s MHz successfuly stored to memory preset %d.") % (currentFreq, number)
		self.session.open(MessageBox, msg, MessageBox.TYPE_ERROR, timeout=10, close_on_any_key=True)

	def savePresets(self):
		presets = eval("config.sdgradio.presets_%s" % self.modulation.value)
		presets.value = ",".join(self.presets)
		presets.save()

	def toggleModulation(self):
		self.stopRadio()
		self.savePresets()
		self.modulation.selectNext()
		self.modulation.save()
		self["key_red"].setText(self.modulation.getText())
		self.frequency = eval("config.sdgradio.frequency_%s" % self.modulation.value)
		self.freqChange(Decimal(0)) # evaluate current frequency and update screen
		self.yellowText()
		self.getPresets()

	def togglePlayback(self):
		if self.playbackFrequency is None and self.frequency.value != "0": # not playing
			self.playbackFrequency = self.frequency.value # move to play readio?
			self.playRadio()
		else:
			self.stopRadio()

	def yellow(self):
		if self.modulation.value == "fm":
			config.sdgradio.rds.value = not config.sdgradio.rds.value
			config.sdgradio.rds.save()
			self.playRadio()
		elif self.modulation.value == "dab":
			if self.console:
				self.console.write("\n") # new line switches to next program
		self.yellowText()

	def yellowText(self):
		if self.modulation.value == "fm":
			if config.sdgradio.rds.value:
				self["key_yellow"].setText(_("RDS On"))
			else:
				self["key_yellow"].setText(_("RDS Off"))
		elif self.modulation.value == "dab":
			self["key_yellow"].setText(_("Next Station"))
		else:
			self["key_yellow"].setText("")

	def cancel(self):
		self.doConsoleStop()
		self.savePresets()
		config.sdgradio.save()
		self.close(False, self.session)
		self.session.nav.playService(self.oldService)

	def showInfo(self):
		self.stopRadio()
		self.session.open(Console, _("Info"), ["sleep 0.5 && rtl_eeprom"])

	def showLog(self):
		text = "".join(self.log)
		self.session.open(Console, _("Log"), ["cat << EOF\n%s\nEOF" % text])

	def showPrograms(self):
		if self.modulation.value == "dab":
			if self.programs:
				def showProgramsCb(choice):
					if choice and self.console:
						self.console.write("%s\n" % choice[1])
				self.session.openWithCallback(showProgramsCb, ChoiceBox, title=_("Select Radio Program"), list=self.programs)
			else:
				self.session.open(MessageBox, _("No Programs"), MessageBox.TYPE_ERROR)

	def showMenu(self):
		def showMenuCb(retval=True): # KeyCancel returns False, while KeySave returns None!
			if retval is True:
				self.stopRadio()
				self.getConfigOptions()
		self.session.openWithCallback(showMenuCb, SDGRadioSetup)

	def showPicture(self, image):
		if os.path.exists(image):
			sc = AVSwitch().getFramebufferScale()
			self.picloads = ePicLoad()
			self.picloads.PictureData.get().append(boundFunction(self.showPictureFinish, image))
			self.picloads.setPara((
				self["pic"].instance.size().width(),
				self["pic"].instance.size().height(),
				sc[0], sc[1], False, 1, "#00000000"))
			self.picloads.startDecode(image)

	def showPictureFinish(self, image, picInfo=None):
		ptr = self.picloads.getData()
		if ptr:
			self["pic"].instance.setPixmap(ptr.__deref__())
			self["pic"].show()
			del self.picloads
			os.remove(image)

def main(session, **kwargs):
	session.open(SDGRadioScreen)

def Plugins(**kwargs):
	return PluginDescriptor(
		name="Enigma2 Radio",
		description="Software Defined Radio",
		where=PluginDescriptor.WHERE_PLUGINMENU,
		needsRestart=False,
		icon="img/sdgradio.png",
		fnc=main
	)
