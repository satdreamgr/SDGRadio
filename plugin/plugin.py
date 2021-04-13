from . import _
from utils import SDR_MIN_FREQ, SDR_MAX_FREQ, DAB_FREQ, SKIN
from Components.ActionMap import HelpableActionMap, ActionMap
from Components.AVSwitch import AVSwitch
from Components.config import config, getConfigListEntry, ConfigSubsection, ConfigText, ConfigSelection, ConfigSelectionNumber, ConfigYesNo, ConfigFloat
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Pixmap import Pixmap, MultiPixmap
from Components.Sources.StaticText import StaticText
from Plugins.Plugin import PluginDescriptor
from Screens.ChoiceBox import ChoiceBox
from Screens.Console import Console
from Screens.HelpMenu import HelpableScreen
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


config.plugins.SDGRadio = ConfigSubsection()
config.plugins.SDGRadio.frequency_fm = ConfigText(default="89.0")
config.plugins.SDGRadio.frequency_nfm = ConfigText(default="89.0")
config.plugins.SDGRadio.frequency_am = ConfigText(default="0.8")
config.plugins.SDGRadio.frequency_lsb = ConfigText(default="0.8")
config.plugins.SDGRadio.frequency_usb = ConfigText(default="0.8")
config.plugins.SDGRadio.frequency_dab = ConfigText(default="174.928")
config.plugins.SDGRadio.presets_fm = ConfigText(default="0,0,0,0,0,0,0,0,0,0")
config.plugins.SDGRadio.presets_nfm = ConfigText(default="0,0,0,0,0,0,0,0,0,0")
config.plugins.SDGRadio.presets_am = ConfigText(default="0,0,0,0,0,0,0,0,0,0")
config.plugins.SDGRadio.presets_lsb = ConfigText(default="0,0,0,0,0,0,0,0,0,0")
config.plugins.SDGRadio.presets_usb = ConfigText(default="0,0,0,0,0,0,0,0,0,0")
config.plugins.SDGRadio.presets_dab = ConfigText(default="0,0,0,0,0,0,0,0,0,0")
config.plugins.SDGRadio.rds = ConfigYesNo(default=False)
config.plugins.SDGRadio.modulation = ConfigSelection(default="fm", choices=[
	("fm", _("FM")),
	("nfm", _("NFM")),
	("am", _("AM")),
	("lsb", _("LSB")),
	("usb", _("USB")),
	("dab", _("DAB/DAB+"))
])
config.plugins.SDGRadio.tuning = ConfigSelection(default="simple", choices=[
	("simple", _("simple")),
	("advanced", _("advanced"))
])
config.plugins.SDGRadio.ppmoffset = ConfigSelectionNumber(-100, 100, 1, 0)
choicelist = [("automatic", _("auto"))]
for i in range(0, 51): # 0 to 50
	choicelist.append((str(i)))
config.plugins.SDGRadio.fmgain = ConfigSelection(default="automatic", choices=choicelist)
config.plugins.SDGRadio.dabgain = ConfigSelection(default="automatic", choices=choicelist)
config.plugins.SDGRadio.gain = ConfigSelection(default="automatic", choices=choicelist)
config.plugins.SDGRadio.fmbandwidth = ConfigSelectionNumber(50, 180, 1, 171)
config.plugins.SDGRadio.bandwidth = ConfigSelectionNumber(1, 32, 1, 20)
config.plugins.SDGRadio.sbbandwidth = ConfigSelectionNumber(1, 16, 1, 5)
config.plugins.SDGRadio.fmregion = ConfigSelection(default="eu-int", choices=[
	("eu-int", _("Europe/World")),
	("amer", _("America")),
	("ru", _("Russia")),
	("cn", _("China")),
	("jp", _("Japan"))
])
config.plugins.SDGRadio.usepartial = ConfigYesNo(default=False)
config.plugins.SDGRadio.userbds = ConfigYesNo(default=False)
config.plugins.SDGRadio.pcm = ConfigYesNo(default=True)
config.plugins.SDGRadio.edge = ConfigYesNo(default=False)
config.plugins.SDGRadio.dc = ConfigYesNo(default=False)
config.plugins.SDGRadio.deemp = ConfigYesNo(default=False)
config.plugins.SDGRadio.direct = ConfigYesNo(default=False)
config.plugins.SDGRadio.offset = ConfigYesNo(default=False)


class SDGRadioSetup(ConfigListScreen, Screen):

	def __init__(self, session):
		Screen.__init__(self, session)
		self.setTitle(_("SDR setup"))
		self.skinName = ["SDGRadioSetup", "Setup"]

		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("OK"))
		self["description"] = Label("") # filled automatically when calling createSummary()

		self["setupActions"] = ActionMap(["OkCancelActions", "ColorActions"],
			{
				"cancel": self.keyCancel,
				"red": self.keyCancel,
				"ok": self.keySave,
				"green": self.keySave
			}, -2)

		configlist = []

		configlist.append(getConfigListEntry(_('Tuning mode'),
			config.plugins.SDGRadio.tuning,
			_('Select the tuning mode for analog modulations. "simple" is designed for listening to radio stations,'
				' as it applies band limits and allows only rough frequency changes. "advanced" disables limits and'
				' allows precise control over frequency selection.')))

		configlist.append(getConfigListEntry(_('PPM offset'),
			config.plugins.SDGRadio.ppmoffset,
			_('Use PPM offset to correct the oscillator frequency. Get proper value using "rtl_test -p" or "kalibrate".')))

		configlist.append(getConfigListEntry(_('Tuner gain for FM'),
			config.plugins.SDGRadio.fmgain,
			_('Set the tuner gain value for FM band (default = auto).')))

		configlist.append(getConfigListEntry(_('Tuner gain for DAB/DAB+'),
			config.plugins.SDGRadio.dabgain,
			_('Set the tuner gain value for DAB/DAB+ (default = auto).')))

		configlist.append(getConfigListEntry(_('Tuner gain for other bands and DAB'),
			config.plugins.SDGRadio.gain,
			_('Set the tuner gain value for AM, NFM, LSB, and USB (default = auto).')))

		configlist.append(getConfigListEntry(_('Bandwidth for FM in k/sec'),
			config.plugins.SDGRadio.fmbandwidth,
			_('Set the frequency bandwidth for FM band. For RDS set to 171 (default = 171k).')))

		configlist.append(getConfigListEntry(_('Bandwidth for NFM/AM in k/sec'),
			config.plugins.SDGRadio.bandwidth,
			_('Set the frequency bandwidth for NFM and AM bands (default = 20k).')))

		configlist.append(getConfigListEntry(_('Bandwidth for LSB/USB in k/sec'),
			config.plugins.SDGRadio.sbbandwidth,
			_('Set the frequency bandwidth for LSB and USB bands (default = 5k).')))

		configlist.append(getConfigListEntry(_('FM region'),
			config.plugins.SDGRadio.fmregion,
			_('Select FM band range by region. "Russia" provides 64-108 MHz (full FM band), "Europe/World" 87.5-108 MHz,'
				' "Japan" 76-95 MHz, "China" 76-108 MHz and "America" 88.1-107.9 MHz.')))

		configlist.append(getConfigListEntry(_('Use partial RDS info'),
			config.plugins.SDGRadio.usepartial,
			_('Use RDS info before it is fully received. This could be useful when reception is noisy.')))

		configlist.append(getConfigListEntry(_('Use RBDS instead of RDS'),
			config.plugins.SDGRadio.userbds,
			_('Use RBDS instead of ordinary RDS info. If FM region is set to "America", RBDS is selected automatically.')))

		configlist.append(getConfigListEntry(_('PCM output'),
			config.plugins.SDGRadio.pcm,
			_('Output PCM instead of AAC/MPEG when using DAB/DAB+.')))

		configlist.append(getConfigListEntry(_('Lower edge tuning'),
			config.plugins.SDGRadio.edge,
			_('Enable lower edge tuning for analog radio.')))

		configlist.append(getConfigListEntry(_('DC filter'),
			config.plugins.SDGRadio.dc,
			_('Enable the DC blocking filter.')))

		configlist.append(getConfigListEntry(_('De-emphasis filter'),
			config.plugins.SDGRadio.deemp,
			_('Enable the de-emphasis filter.')))

		configlist.append(getConfigListEntry(_('Direct sampling'),
			config.plugins.SDGRadio.direct,
			_('Enable direct sampling for the tuner.')))

		configlist.append(getConfigListEntry(_('Offset tuning'),
			config.plugins.SDGRadio.offset,
			_('Enable offset tuning.')))

		ConfigListScreen.__init__(self, configlist, session)


class SDGRadioInput(ConfigListScreen, Screen):

	def __init__(self, session, frequency):
		Screen.__init__(self, session)
		self.setTitle(_("SDR input"))
		self.skinName = ["SDGRadioInput", "Setup"]

		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("OK"))
		self["description"] = Label("") # filled automatically when calling createSummary()

		self["setupActions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"cancel": self.keyCancel,
			"red": self.keyCancel,
			"ok": self.ok,
			"green": self.ok
		}, -2)

		# split frequency string to interger and decimal parts
		freq = frequency.partition(".")
		freqInt = "{:0>4s}".format(freq[0])
		freqDec = "{:0<4s}".format(freq[2])

		#self.input = ConfigSubsection() # not needed
		self.inputfreq = ConfigFloat(default=[int(freqInt), int(freqDec)], limits=[(SDR_MIN_FREQ, SDR_MAX_FREQ), (0, 9999)])

		configlist = []

		configlist.append(getConfigListEntry(_('Frequency in MHz'),
			self.inputfreq,
			_('Enter the desired frequency. You can input values between %(min)d - %(max)d MHz with up to 4 decimal digits'
				' (precision of 0.1 KHz).') % {'min': SDR_MIN_FREQ, 'max': SDR_MAX_FREQ}))

		ConfigListScreen.__init__(self, configlist, session)

	def ok(self):
		self.close(str(self.inputfreq.float)) # nothing to save, just pass the value


class SDGRadioScreen(Screen, HelpableScreen):

	def __init__(self, session):
		self.modulation = config.plugins.SDGRadio.modulation
		self.frequency = eval("config.plugins.SDGRadio.frequency_%s" % self.modulation.value)
		self.playbackFrequency = None # currently playing frequency
		self.playbackPreset = None # currently playing preset
		self.presets = [] # preset list for current modulation
		self.log = [] # log messages
		self.programs = [] # DAB program list
		self.console = None

		Screen.__init__(self, session)
		HelpableScreen.__init__(self)
		self.setTitle(_("Software defined radio"))
		self.skin = SKIN
		self.skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/SDGRadio")

		for i in range(0, 10):
			self["mem_%d" % i] = MultiPixmap()

		self["modulation"] = Label()
		self["freq"] = Label()
		self["freq_off"] = Label()
		self["freq_units"] = Label()
		self["dab_channel"] = Label()
		self["radiotext"] = Label()
		self["prog_type"] = Label()
		self["pi"] = Label()
		self["traffic"] = Label()
		self["af"] = Label()
		self["ct"] = Label()
		self["eon"] = Label()
		self["rt+"] = Label()
		self["pic"] = Pixmap()
		self["rds_icon"] = Pixmap()
		self["rt_icon"] = Pixmap()
		self["ps_icon"] = Pixmap()

		self["key_red"] = StaticText()
		self["key_green"] = StaticText(_("Play"))
		self["key_yellow"] = StaticText()
		self["key_blue"] = StaticText()

		self["actions"] = HelpableActionMap(self, "SDGRadioActions",
		{
			"cancel": (self.cancel, _("Close plugin")),
			"ok": (self.selectFreq, _("Play current frequency")),

			"info": (self.showPrograms, _("Show DAB program list")),
			"menu": (self.showMenu, _("Open advanced options menu")),

			"red": (self.toggleModulation, _("Change modulation")),
			"green": (self.togglePlayback, _("Start/stop playback")),
			"yellow": (self.yellow, _("Switch RDS on/off")),
			"blue": (self.showInput, _("Open frequency input screen")),
			"blue_long": (self.showLog, _("Cmd execution log")),

			"0": (boundFunction(self.selectPreset, 0), _("Play memory preset %d") % 0),
			"1": (boundFunction(self.selectPreset, 1), _("Play memory preset %d") % 1),
			"2": (boundFunction(self.selectPreset, 2), _("Play memory preset %d") % 2),
			"3": (boundFunction(self.selectPreset, 3), _("Play memory preset %d") % 3),
			"4": (boundFunction(self.selectPreset, 4), _("Play memory preset %d") % 4),
			"5": (boundFunction(self.selectPreset, 5), _("Play memory preset %d") % 5),
			"6": (boundFunction(self.selectPreset, 6), _("Play memory preset %d") % 6),
			"7": (boundFunction(self.selectPreset, 7), _("Play memory preset %d") % 7),
			"8": (boundFunction(self.selectPreset, 8), _("Play memory preset %d") % 8),
			"9": (boundFunction(self.selectPreset, 9), _("Play memory preset %d") % 9),

			"long0": (boundFunction(self.storePreset, 0), _("Store frequency to memory preset %d") % 0),
			"long1": (boundFunction(self.storePreset, 1), _("Store frequency to memory preset %d") % 1),
			"long2": (boundFunction(self.storePreset, 2), _("Store frequency to memory preset %d") % 2),
			"long3": (boundFunction(self.storePreset, 3), _("Store frequency to memory preset %d") % 3),
			"long4": (boundFunction(self.storePreset, 4), _("Store frequency to memory preset %d") % 4),
			"long5": (boundFunction(self.storePreset, 5), _("Store frequency to memory preset %d") % 5),
			"long6": (boundFunction(self.storePreset, 6), _("Store frequency to memory preset %d") % 6),
			"long7": (boundFunction(self.storePreset, 7), _("Store frequency to memory preset %d") % 7),
			"long8": (boundFunction(self.storePreset, 8), _("Store frequency to memory preset %d") % 8),
			"long9": (boundFunction(self.storePreset, 9), _("Store frequency to memory preset %d") % 9),

			"up": (boundFunction(self.freqUp, "1"), _("Increase frequency by 1 MHz / KHz")),
			"down": (boundFunction(self.freqDown, "1"), _("Decrease frequency by 1 MHz / KHz")),
			"upRepeated": (boundFunction(self.freqUp, "10"), _("Increase frequency by 10 MHz / KHz (long press)")),
			"downRepeated": (boundFunction(self.freqDown, "10"), _("Decrease frequency by 10 MHz / KHz (long press)")),

			"right": (boundFunction(self.freqUp, "0.05"), _("Increase frequency by 0.05 MHz")),
			"left": (boundFunction(self.freqDown, "0.05"), _("Decrease frequency by 0.05 MHz")),
			"rightRepeated": (boundFunction(self.freqUp, "0.1"), _("Increase frequency by 0.1 MHz (long press)")),
			"leftRepeated": (boundFunction(self.freqDown, "0.1"), _("Decrease frequency by 0.1 MHz (long press)")),

			"nextBouquet": (boundFunction(self.freqUp, "0.0001"), _("Increase frequency by 0.0001 MHz")),
			"prevBouquet": (boundFunction(self.freqDown, "0.0001"), _("Decrease frequency by 0.0001 MHz")),
		}, -2)

		self.onLayoutFinish.extend([self.getConfigOptions, self.getPresets, self.updateFreqWidget,
									self.updateExtraWidgets, self.redText, self.yellowText, self.blueText])

		self.oldService = self.session.nav.getCurrentlyPlayingServiceReference() # get currently playing service
		self.session.nav.stopService() # stop currently playing service
		eConsoleAppContainer().execute("showiframe /usr/share/enigma2/radio.mvi") # display radio mvi
		#self.Scale = AVSwitch().getFramebufferScale()

	def getConfigOptions(self):
		self.tuning = config.plugins.SDGRadio.tuning.value
		self.ppmoffset = str(config.plugins.SDGRadio.ppmoffset.value)
		self.fmgain = config.plugins.SDGRadio.fmgain.value
		self.dabgain = config.plugins.SDGRadio.dabgain.value
		self.gain = config.plugins.SDGRadio.gain.value
		self.fmbandwidth = str(config.plugins.SDGRadio.fmbandwidth.value)
		self.bandwidth = str(config.plugins.SDGRadio.bandwidth.value)
		self.sbbandwidth = str(config.plugins.SDGRadio.sbbandwidth.value)
		self.fmregion = config.plugins.SDGRadio.fmregion.value
		self.usepartial = config.plugins.SDGRadio.usepartial.value
		self.userbds = config.plugins.SDGRadio.userbds.value
		self.pcm = config.plugins.SDGRadio.pcm.value
		self.edge = config.plugins.SDGRadio.edge.value
		self.dc = config.plugins.SDGRadio.dc.value
		self.deemp = config.plugins.SDGRadio.deemp.value
		self.direct = config.plugins.SDGRadio.direct.value
		self.offset = config.plugins.SDGRadio.offset.value

	def stopRadio(self):
		self.doConsoleStop()
		self.updateMiscWidgets(False)
		self.playbackFrequency = None
		self.playbackPreset = None

	def playRadio(self):
		self.doConsoleStop()
		self.updateMiscWidgets(True)
		self.console = eConsoleAppContainer()
		self.console.stderrAvail.append(self.cbStderrAvail)
		#self.console.appClosed.append(self.cbAppClosed)

		if self.modulation.value == "fm":
			if config.plugins.SDGRadio.rds.value:
				cmd = "rtl_fm -f %sM -M fm -l 0 -A std -s %sk %s -p %s %s %s %s %s %s -F 9 - | %s | gst-launch-1.0 fdsrc ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=%s000 ! audioresample ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=48000 ! dvbaudiosink" % (self.frequency.value, self.fmbandwidth, self.getFmGain(), self.ppmoffset, self.getEdge(), self.getDc(), self.getDeemp(), self.getDirect(), self.getOffset(), self.rdsOptions(), self.fmbandwidth)
			else:
				cmd = "rtl_fm -f %sM -M fm -l 0 -A std -s %sk %s -p %s %s %s %s %s %s -F 0 - | gst-launch-1.0 fdsrc ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=%s000 ! audioresample ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=48000 ! dvbaudiosink" % (self.frequency.value, self.fmbandwidth, self.getFmGain(), self.ppmoffset, self.getEdge(), self.getDc(), self.getDeemp(), self.getDirect(), self.getOffset(), self.fmbandwidth)
		elif self.modulation.value == "nfm":
			cmd = "rtl_fm -f %sM -M fm -A std -s %sk %s -p %s %s %s %s %s %s - | gst-launch-1.0 fdsrc ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=%s000 ! audioresample ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=48000 ! dvbaudiosink" % (self.frequency.value, self.bandwidth, self.getGain(), self.ppmoffset, self.getEdge(), self.getDc(), self.getDeemp(), self.getDirect(), self.getOffset(), self.bandwidth)
		elif self.modulation.value == "am":
			cmd = "rtl_fm -f %sM -M am -A std -s %sk %s -p %s %s %s %s %s %s - | gst-launch-1.0 fdsrc ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=%s000 ! audioresample ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=48000 ! dvbaudiosink" % (self.frequency.value, self.bandwidth, self.getGain(), self.ppmoffset, self.getEdge(), self.getDc(), self.getDeemp(), self.getDirect(), self.getOffset(), self.bandwidth)
		elif self.modulation.value == "lsb":
			cmd = "rtl_fm -f %sM -M lsb -A std -s %sk %s -p %s %s %s %s %s %s - | gst-launch-1.0 fdsrc ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=%s000 ! audioresample ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=48000 ! dvbaudiosink" % (self.frequency.value, self.sbbandwidth, self.getGain(), self.ppmoffset, self.getEdge(), self.getDc(), self.getDeemp(), self.getDirect(), self.getOffset(), self.sbbandwidth)
		elif self.modulation.value == "usb":
			cmd = "rtl_fm -f %sM -M usb -A std -s %sk %s -p %s %s %s %s %s %s - | gst-launch-1.0 fdsrc ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=%s000 ! audioresample ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=48000 ! dvbaudiosink" % (self.frequency.value, self.sbbandwidth, self.getGain(), self.ppmoffset, self.getEdge(), self.getDc(), self.getDeemp(), self.getDirect(), self.getOffset(), self.sbbandwidth)
		elif self.modulation.value == "dab":
			if self.pcm:
				cmd = "dab-rtlsdr-sdgradio-pcm -C %s -W30 -p %s %s | gst-launch-1.0 fdsrc ! audio/x-raw, format=S16LE, channels=2, layout=interleaved, rate=48000 ! dvbaudiosink" % (DAB_FREQ.get(Decimal(self.frequency.value), "5A"), self.ppmoffset, self.getDabGain())
			else:
				cmd = "dab-rtlsdr-sdgradio -C %s -W30 -p %s %s | gst-launch-1.0 fdsrc ! faad ! dvbaudiosink" % (DAB_FREQ.get(Decimal(self.frequency.value), "5A"), self.ppmoffset, self.getDabGain())
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
				self["ps_icon"].show()

			if "partial_ps" in rds and self.getTitle() != rds["partial_ps"].encode("utf8"):
				self.setTitle(rds["partial_ps"].encode("utf8"))
				self["pic"].hide()
				self["ps_icon"].show()

			if "radiotext" in rds and self["radiotext"].getText() != rds["radiotext"].encode("utf8"):
				self["radiotext"].setText(rds["radiotext"].encode("utf8"))
				self["rt_icon"].show()

			if "partial_radiotext" in rds and self["radiotext"].getText() != rds["partial_radiotext"].encode("utf8"):
				self["radiotext"].setText(rds["partial_radiotext"].encode("utf8"))
				self["rt_icon"].show()

			if "prog_type" in rds and self["prog_type"].getText() != rds["prog_type"].encode("utf8"):
				self["prog_type"].setText(rds["prog_type"].encode("utf8"))

			if "pi" in rds and not "callsign" in rds and self["pi"].getText() != rds["pi"].encode("utf8"):
				self["pi"].setText(rds["pi"].encode("utf8").replace("0x", "PI: "))

			if "callsign" in rds and self["pi"].getText() != rds["callsign"].encode("utf8"):
				self["pi"].setText(rds["callsign"].encode("utf8"))

			if "callsign_uncertain" in rds and self["pi"].getText() != rds["callsign_uncertain"].encode("utf8"):
				self["pi"].setText(rds["callsign_uncertain"].encode("utf8"))

			if "pi" in rds and not str(rds["pi"]) == "0x0000" or "callsign" in rds or "callsign_uncertain" in rds or "pi" in rds and str(rds["pi"]) == "0x0000" or "partial_ps" in rds and str(rds["pi"]) == "0x0000":
				self["rds_icon"].show()

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
			msg = "processRds exception: %s data: %s\n" % (e, binascii.hexlify(data))
			self.log.append(msg)
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

	def getFmGain(self):
		return "-g %s" % self.fmgain if self.fmgain != "automatic" else ""

	def getDabGain(self):
		return "-G %s" % self.dabgain if self.dabgain != "automatic" else "-Q"

	def getGain(self):
		return "-g %s" % self.gain if self.gain != "automatic" else ""

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
			self.console.kill()
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
		if value != "0.0001" or self.tuning == "advanced":
			self.freqChange(Decimal(value))

	def freqDown(self, value):
		if value != "0.0001" or self.tuning == "advanced":
			self.freqChange(-Decimal(value))

	def freqChange(self, value):
		oldFreq = Decimal(self.frequency.value)

		if self.modulation.value == "dab":
			#oldFreq = Decimal(self.frequency.value)
			newFreq = oldFreq + value
			if newFreq < Decimal("174.928"):
				newFreq = Decimal("174.928")
			if newFreq > Decimal("239.200"):
				newFreq = Decimal("239.200")
			if newFreq > oldFreq:
				newFreq = min(filter(lambda x: x >= newFreq, DAB_FREQ.keys()))
			else:
				newFreq = max(filter(lambda x: x <= newFreq, DAB_FREQ.keys()))
		else:
			if self.tuning == "simple":
				if self.modulation.value in ("am", "lsb", "usb"):
					lower = Decimal("0.52") # 520 KHz
					upper = Decimal("2.0") # 2000 KHz
					if value == Decimal("0.05"):
						value = Decimal("1")
					elif value == Decimal("-0.05"):
						value = Decimal("-1")
					elif value == Decimal("0.10"):
						value = Decimal("10")
					elif value == Decimal("-0.10"):
						value = Decimal("-10")
					value = value * Decimal("0.001") # step 1000 times smaller, since we display in KHz
				elif self.modulation.value in ("fm", "nfm"):
					if self.fmregion == "ru":
						lower = Decimal("64.0")
						upper = Decimal("108.0")
					elif self.fmregion == "eu-int":
						lower = Decimal("87.5")
						upper = Decimal("108.0")
					elif self.fmregion == "jp":
						lower = Decimal("76.0")
						upper = Decimal("95.0")
					elif self.fmregion == "cn":
						lower = Decimal("76.0")
						upper = Decimal("108.0")
					elif self.fmregion == "amer":
						lower = Decimal("88.1")
						upper = Decimal("107.9")
			else: # advanced mode, no limits
				lower = Decimal(SDR_MIN_FREQ)
				upper = Decimal(SDR_MAX_FREQ)

			newFreq = oldFreq + value
			if newFreq < lower:
				newFreq = lower
			if newFreq > upper:
				newFreq = upper

		self.frequency.value = str(newFreq)
		self.frequency.save()
		self.updateFreqWidget()

	def freqQuantize(self): # used for cutting extra decimal digits when retuning to "simple" mode
		for mod in ("fm", "nfm"):
			frequency = eval("config.plugins.SDGRadio.frequency_%s" % mod)
			value = Decimal(frequency.value).quantize(Decimal("0.1"))
			frequency.value = str(value)
			frequency.save()
		for mod in ("am", "lsb", "usb"):
			frequency = eval("config.plugins.SDGRadio.frequency_%s" % mod)
			value = Decimal(frequency.value).quantize(Decimal("0.001"))
			frequency.value = str(value)
			frequency.save()

	def getPresets(self):
		self.presets = []
		presetsConfig = eval("config.plugins.SDGRadio.presets_%s" % self.modulation.value)
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
			self.updateFreqWidget()
			self.playRadio()

	def storePreset(self, number):
		currentFreq = self.frequency.value
		if currentFreq in ("", "0"):
			msg = _("Error storing memory preset! Please select a valid frequency and try again.")
			self.session.open(MessageBox, msg, MessageBox.TYPE_ERROR, timeout=10, close_on_any_key=True)
		else:
			self.presets[number] = currentFreq
			self["mem_%d" % number].setPixmapNum(1) # preset stored
			msg = _("Selected frequency successfuly stored to memory preset %d.") % number
			self.session.open(MessageBox, msg, MessageBox.TYPE_INFO, timeout=10, close_on_any_key=True)

	def savePresets(self):
		presets = eval("config.plugins.SDGRadio.presets_%s" % self.modulation.value)
		presets.value = ",".join(self.presets)
		presets.save()

	def updateMiscWidgets(self, play=False):
		self["radiotext"].setText("")
		self["prog_type"].setText("")
		self["pi"].setText("")
		self["traffic"].setText("")
		self["af"].setText("")
		self["ct"].setText("")
		self["eon"].setText("")
		self["rt+"].setText("")
		self["rds_icon"].hide()
		self["rt_icon"].hide()
		self["ps_icon"].hide()
		if play is False:
			self["key_green"].setText(_("Play"))
			self.setTitle(_("Software defined radio"))
			if self.playbackPreset:
				self["mem_%d" % self.playbackPreset].setPixmapNum(1) # preset stored
		else:
			self["key_green"].setText(_("Stop"))
			self.setTitle(_("Playing %(freq)s %(units)s") % {"freq": self["freq"].getText().strip("!"), "units": self["freq_units"].getText()})

	def updateFreqWidget(self): # this is for displaying only
		if self.modulation.value == "dab":
			self["freq"].setText(self.frequency.value)
			self["dab_channel"].setText(DAB_FREQ.get(Decimal(self.frequency.value), ""))
		else:
			if self.tuning == "simple":
				if self.modulation.value in ("am", "lsb", "usb"):
					self["freq"].setText("{:!>4.0f}".format(Decimal(self.frequency.value) * Decimal("1000")))
				elif self.modulation.value in ("fm", "nfm"):
					freq = "{:!>6.2f}".format(Decimal(self.frequency.value))
					self["freq"].setText("".join((freq[:5], "!")) if freq.endswith("0") else freq)
			else:
				self["freq"].setText("{:09.4f}".format(Decimal(self.frequency.value)))
			self["dab_channel"].setText("")

	def updateExtraWidgets(self):
		self["modulation"].setText(self.modulation.getText()) # current modulation
		if self.tuning == "simple":
			self["freq_off"].setText("")
			if self.modulation.value in ("am", "lsb", "usb"):
				self["freq_units"].setText("KHz")
			else:
				self["freq_units"].setText("MHz")
		elif self.modulation.value == "dab":
			self["freq_off"].setText("888.888") # 6 digits
			self["freq_units"].setText("MHz")
		else:
			self["freq_off"].setText("8888.8888") # 8 digits
			self["freq_units"].setText("MHz")

	def toggleModulation(self):
		self.stopRadio()
		self.savePresets()
		self.modulation.selectNext()
		self.modulation.save()
		self.frequency = eval("config.plugins.SDGRadio.frequency_%s" % self.modulation.value)
		self.freqChange(Decimal(0)) # evaluate current frequency and update freq widget
		self.updateExtraWidgets()
		self.redText()
		self.yellowText()
		self.blueText()
		self.getPresets()

	def redText(self):
		idx = self.modulation.index
		idx = (idx + 1) % len(self.modulation.choices) # get next index (cycle through indices)
		choice = self.modulation.choices[idx]
		self["key_red"].setText(_("Switch to %s") % self.modulation.description[choice]) # next available modulation

	def togglePlayback(self):
		if self.playbackFrequency is None and self.frequency.value != "0": # not playing
			self.playbackFrequency = self.frequency.value
			self.playRadio()
		else:
			self.stopRadio()

	def yellow(self):
		if self.modulation.value == "fm":
			config.plugins.SDGRadio.rds.value = not config.plugins.SDGRadio.rds.value
			config.plugins.SDGRadio.rds.save()
			if self.playbackFrequency: # playback is active, restart it
				self.playRadio()
		elif self.modulation.value == "dab":
			if self.console:
				self.console.write("\n") # new line switches to next program
		self.yellowText()

	def yellowText(self):
		if self.modulation.value == "fm":
			if config.plugins.SDGRadio.rds.value:
				self["key_yellow"].setText(_("RDS on"))
			else:
				self["key_yellow"].setText(_("RDS off"))
		elif self.modulation.value == "dab":
			self["key_yellow"].setText(_("Switch program"))
		else:
			self["key_yellow"].setText("")

	def showInput(self):
		if self.tuning == "advanced" and self.modulation.value != "dab":
			def freqInputCb(value):
				if value is not False and isinstance(value, str):
					self.stopRadio()
					self.frequency.value = value
					self.updateFreqWidget()
			self.session.openWithCallback(freqInputCb, SDGRadioInput, self.frequency.value)

	def blueText(self):
		if self.tuning == "advanced" and self.modulation.value != "dab":
			self["key_blue"].setText(_("Frequency input"))
		else:
			self["key_blue"].setText("")

	def showInfo(self):
		self.stopRadio()
		self.session.open(Console, _("Info"), ["sleep 0.5 && rtl_eeprom"])

	def showLog(self):
		text = "".join(self.log)
		open("/tmp/sdgradio.log", "w").write(text)
		self.session.open(Console, _("Log"), ["cat << EOF\n%s\nEOF" % text])

	def showPrograms(self):
		if self.modulation.value == "dab":
			if self.programs:
				def showProgramsCb(choice):
					if choice and self.console:
						self.console.write("%s\n" % choice[1])
				self.session.openWithCallback(showProgramsCb, ChoiceBox, title=_("Choose a radio program"), list=self.programs)
			else:
				self.session.open(MessageBox, _("There are no programs available on this frequency."), MessageBox.TYPE_ERROR)

	def showSetup(self):
		def showSetupCb(retval=True): # KeyCancel returns False, while KeySave returns None!
			if retval is True:
				self.stopRadio()
				oldtuning = self.tuning
				self.getConfigOptions()
				if self.tuning != oldtuning:
					self.updateExtraWidgets()
					self.blueText()
					if self.tuning == "simple":
						self.freqQuantize()
				self.freqChange(Decimal(0)) # evaluate current frequency and update freq widget
		self.session.openWithCallback(showSetupCb, SDGRadioSetup)

	def showMenu(self):
		keys = ["menu", "1", "2"]
		choices = []
		choices.append((_("Setup menu"), self.showSetup, "menu"))
		choices.append((_("Cmd execution log"), self.showLog, "log"))
		choices.append((_("SDR device information"), self.showInfo, "info"))

		def showMenuCb(choice):
			if choice is not None:
				choice[1]()
		self.session.openWithCallback(showMenuCb, ChoiceBox, title=_("Choose an action"), list=choices, keys=keys)

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
		else:
			msg = "showPicture: cannot find image: %s\n" % image
			self.log.append(msg)

	def showPictureFinish(self, image, picInfo=None):
		ptr = self.picloads.getData()
		if ptr:
			self["pic"].instance.setPixmap(ptr.__deref__())
			self["pic"].show()
			del self.picloads
			os.remove(image)

	def cancel(self):
		self.doConsoleStop()
		self.savePresets()
		config.plugins.SDGRadio.save()
		eConsoleAppContainer().execute("rtl_eeprom") # hack: run rtl_eeprom to shutdown tuner
		self.close(False, self.session)
		self.session.nav.playService(self.oldService)


def main(session, **kwargs):
	session.open(SDGRadioScreen)


def Plugins(**kwargs):
	return PluginDescriptor(
		name=_("Software defined radio"),
		description=_("Listen to radio using a RTL-SDR USB tuner"),
		where=PluginDescriptor.WHERE_PLUGINMENU,
		needsRestart=False,
		icon="sdgradio.png",
		fnc=main
	)
