from Components.ActionMap import ActionMap
from Components.AVSwitch import AVSwitch
from Components.config import config, getConfigListEntry, ConfigSubsection, ConfigText, ConfigInteger, ConfigSelection, ConfigSlider, ConfigYesNo
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
config.sdgradio.last = ConfigText(default="87.5")
config.sdgradio.lastbutton = ConfigInteger(default=0, limits=(0, 9))
config.sdgradio.a = ConfigText(default="87.5")
config.sdgradio.b = ConfigText(default="88.0")
config.sdgradio.c = ConfigText(default="90.0")
config.sdgradio.d = ConfigText(default="92.0")
config.sdgradio.e = ConfigText(default="94.0")
config.sdgradio.f = ConfigText(default="98.0")
config.sdgradio.g = ConfigText(default="100.0")
config.sdgradio.h = ConfigText(default="102.0")
config.sdgradio.i = ConfigText(default="107.0")
config.sdgradio.j = ConfigText(default="108.0")
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
			<widget name="dab_channel" position="0,80" size="120,120" font="Digital;60" valign="center"/>
			<widget name="freq" position="120,80" size="330,120" font="Digital;60" valign="center" halign="center"/>
			<widget name="prog_type" position="0,200" size="450,40" font="Regular;24" valign="center" halign="center"/>
			<widget name="pi" position="0,240" size="150,40" font="Regular;24" valign="center" halign="center"/>
			<widget name="traffic" position="150,240" size="150,40" font="Regular;24" valign="center" halign="center"/>
			<widget name="af" position="300,240" size="150,40" font="Regular;24" valign="center" halign="center"/>
			<widget name="eon" position="0,280" size="150,40" font="Regular;24" valign="center" halign="center"/>
			<widget name="ct" position="150,280" size="150,40" font="Regular;24" valign="center" halign="center"/>
			<widget name="rt+" position="300,280" size="150,40" font="Regular;24" valign="center" halign="center"/>
			<widget name="radiotext" position="0,320" size="680,80" font="Regular;24" valign="center" halign="center"/>
			<widget name="pic" position="480,80" size="200,200" alphatest="blend"/>
			<widget name="mem_0" pixmaps="/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/btn_mem_00_up.png,/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/btn_mem_00_down.png" position="190,420" size="40,40" alphatest="blend"/>
			<widget name="mem_1" pixmaps="/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/btn_mem_01_up.png,/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/btn_mem_01_down.png" position="240,420" size="40,40" alphatest="blend"/>
			<widget name="mem_2" pixmaps="/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/btn_mem_02_up.png,/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/btn_mem_02_down.png" position="290,420" size="40,40" alphatest="blend"/>
			<widget name="mem_3" pixmaps="/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/btn_mem_03_up.png,/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/btn_mem_03_down.png" position="340,420" size="40,40" alphatest="blend"/>
			<widget name="mem_4" pixmaps="/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/btn_mem_04_up.png,/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/btn_mem_04_down.png" position="390,420" size="40,40" alphatest="blend"/>
			<widget name="mem_5" pixmaps="/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/btn_mem_05_up.png,/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/btn_mem_05_down.png" position="440,420" size="40,40" alphatest="blend"/>
			<widget name="mem_6" pixmaps="/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/btn_mem_06_up.png,/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/btn_mem_06_down.png" position="490,420" size="40,40" alphatest="blend"/>
			<widget name="mem_7" pixmaps="/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/btn_mem_07_up.png,/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/btn_mem_07_down.png" position="540,420" size="40,40" alphatest="blend"/>
			<widget name="mem_8" pixmaps="/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/btn_mem_08_up.png,/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/btn_mem_08_down.png" position="590,420" size="40,40" alphatest="blend"/>
			<widget name="mem_9" pixmaps="/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/btn_mem_09_up.png,/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/btn_mem_09_down.png" position="640,420" size="40,40" alphatest="blend"/>
			<ePixmap pixmap="buttons/key_info.png" position="0,420" size="40,40" alphatest="blend"/>
			<ePixmap pixmap="buttons/key_menu.png" position="50,420" size="40,40" alphatest="blend"/>
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)

		for i in range(0, 10):
			self["mem_%d" % i] = MultiPixmap()

		self["freq"] = Label()
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

		self["key_red"] = StaticText(config.sdgradio.modulation.getText())
		#self["key_green"] = StaticText(_("Save"))
		self["key_yellow"] = StaticText("")
		self["key_blue"] = StaticText(_("Log"))

		self["actions"] = ActionMap(["SDGRadioActions"],
		{
			"cancel": self.cancel,
			"ok": self.ok,

			"info": self.info,
			"menu": self.showMenu,
			"file": self.showPrograms,

			"red": self.red,
			#"green": self.green,
			"yellow": self.yellow,
			"blue": self.blue,

			"0": boundFunction(self.buttonNumber, 0),
			"1": boundFunction(self.buttonNumber, 1),
			"2": boundFunction(self.buttonNumber, 2),
			"3": boundFunction(self.buttonNumber, 3),
			"4": boundFunction(self.buttonNumber, 4),
			"5": boundFunction(self.buttonNumber, 5),
			"6": boundFunction(self.buttonNumber, 6),
			"7": boundFunction(self.buttonNumber, 7),
			"8": boundFunction(self.buttonNumber, 8),
			"9": boundFunction(self.buttonNumber, 9),

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

		self.log = [] # log messages
		self.programs = [] # DAB program list
		self.console = None
		self.getConfigOptions() # Load configuration
		self.onLayoutFinish.append(self.startup)

		self.oldService = self.session.nav.getCurrentlyPlayingServiceReference() # get currently playing service
		self.session.nav.stopService() # stop currently playing service
		eConsoleAppContainer().execute("showiframe /usr/share/enigma2/radio.mvi") # display radio mvi
		#self.Scale = AVSwitch().getFramebufferScale()

	def playRadio(self, freq):
		self.doConsoleStop()
		time.sleep(0.3)
		self.console = eConsoleAppContainer()
		self.console.stderrAvail.append(self.cbStderrAvail)
		#self.console.appClosed.append(self.cbAppClosed)

		if config.sdgradio.modulation.value == "fm":
			if config.sdgradio.rds.value:
				cmd = "rtl_fm -f %sM -M fm -l 0 -A std -s %sk -g %s -p %d %s %s %s %s %s -F 9 - | %s | gst-launch-1.0 fdsrc ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=%s000 ! audioresample ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=48000 ! dvbaudiosink" % (freq, self.fmbandwidth, self.fmgain, self.ppmoffset, self.getEdge(), self.getDc(), self.getDeemp(), self.getDirect(), self.getOffset(), self.rdsOptions(), self.fmbandwidth)
			else:
				cmd = "rtl_fm -f %sM -M fm -l 0 -A std -s %sk -g %s -p %d %s %s %s %s %s -F 0 - | gst-launch-1.0 fdsrc ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=%s000 ! audioresample ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=48000 ! dvbaudiosink" % (freq, self.fmbandwidth, self.fmgain, self.ppmoffset, self.getEdge(), self.getDc(), self.getDeemp(), self.getDirect(), self.getOffset(), self.fmbandwidth)
		elif config.sdgradio.modulation.value == "nfm":
			cmd = "rtl_fm -f %sM -M fm -A std -s %sk -g %s -p %d %s %s %s %s %s - | gst-launch-1.0 fdsrc ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=%s000 ! audioresample ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=48000 ! dvbaudiosink" % (freq, self.bandwidth, self.gain, self.ppmoffset, self.getEdge(), self.getDc(), self.getDeemp(), self.getDirect(), self.getOffset(), self.bandwidth)
		elif config.sdgradio.modulation.value == "am":
			cmd = "rtl_fm -f %sM -M am -A std -s %sk -g %s -p %d %s %s %s %s %s - | gst-launch-1.0 fdsrc ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=%s000 ! audioresample ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=48000 ! dvbaudiosink" % (freq, self.bandwidth, self.gain, self.ppmoffset, self.getEdge(), self.getDc(), self.getDeemp(), self.getDirect(), self.getOffset(), self.bandwidth)
		elif config.sdgradio.modulation.value == "lsb":
			cmd = "rtl_fm -f %sM -M lsb -A std -s %sk -g %s -p %d %s %s %s %s %s - | gst-launch-1.0 fdsrc ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=%s000 ! audioresample ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=48000 ! dvbaudiosink" % (freq, self.sbbandwidth, self.gain, self.ppmoffset, self.getEdge(), self.getDc(), self.getDeemp(), self.getDirect(), self.getOffset(), self.sbbandwidth)
		elif config.sdgradio.modulation.value == "usb":
			cmd = "rtl_fm -f %sM -M usb -A std -s %sk -g %s -p %d %s %s %s %s %s - | gst-launch-1.0 fdsrc ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=%s000 ! audioresample ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=48000 ! dvbaudiosink" % (freq, self.sbbandwidth, self.gain, self.ppmoffset, self.getEdge(), self.getDc(), self.getDeemp(), self.getDirect(), self.getOffset(), self.sbbandwidth)
		elif config.sdgradio.modulation.value == "dab":
			if self.pcm:
				cmd = "dab-rtlsdr-sdgradio-pcm -C %s -W30 -p %d %s | gst-launch-1.0 fdsrc ! audio/x-raw, format=S16LE, channels=2, layout=interleaved, rate=48000 ! dvbaudiosink" % (DAB_FREQ.get(Decimal(freq), "5A"), self.ppmoffset, self.getDabGain())
			else:
				cmd = "dab-rtlsdr-sdgradio -C %s -W30 -p %d %s | gst-launch-1.0 fdsrc ! faad ! dvbaudiosink" % (DAB_FREQ.get(Decimal(freq), "5A"), self.ppmoffset, self.getDabGain())
		else:
			cmd = "rtl_fm -f %sM -M wbfm -s 200000 -r 48000 - | gst-launch-1.0 fdsrc ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=48000 ! dvbaudiosink" % freq

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

	def buttonSelect(self, number, freq):
		self["freq"].setText(freq)
		self.freqChange(Decimal(0))
		self["radiotext"].setText("")
		self["prog_type"].setText("")
		self["pi"].setText("")
		self["traffic"].setText("")
		self["af"].setText("")
		self["ct"].setText("")
		self["eon"].setText("")
		self["rt+"].setText("")
		self.setTitle("SDG Radio %s" % freq)
		self.playRadio(freq)
		config.sdgradio.last.value = freq
		config.sdgradio.last.save()
		for i in range(0, 10):
			if i == number:
				config.sdgradio.lastbutton.value = i
				config.sdgradio.lastbutton.save()
				self["mem_%d" % i].setPixmapNum(1)
			else:
				self["mem_%d" % i].setPixmapNum(0)

	def buttonNumber(self, number):
		freq = eval("config.sdgradio.%s.value" % chr(97 + number))
		self.buttonSelect(number, freq)

	def freqChange(self, value):
		freq = self["freq"].getText()
		newfreq = Decimal(freq) + value
		if config.sdgradio.modulation.value == "fm" and self.fmregion == "ru":
			if newfreq < Decimal("64.0"):
				newfreq = Decimal("64.0")
			if newfreq > Decimal("108.0"):
				newfreq = Decimal("108.0")
		elif config.sdgradio.modulation.value == "fm" and self.fmregion == "eu-int":
			if newfreq < Decimal("87.5"):
				newfreq = Decimal("87.5")
			if newfreq > Decimal("108.0"):
				newfreq = Decimal("108.0")
		elif config.sdgradio.modulation.value == "fm" and self.fmregion == "jp":
			if newfreq < Decimal("76.0"):
				newfreq = Decimal("76.0")
			if newfreq > Decimal("95.0"):
				newfreq = Decimal("95.0")
		elif config.sdgradio.modulation.value == "fm" and self.fmregion == "amer":
			if newfreq < Decimal("88.1"):
				newfreq = Decimal("88.1")
			if newfreq > Decimal("107.9"):
				newfreq = Decimal("107.9")
		elif config.sdgradio.modulation.value == "fm" and self.fmregion == "free":
			if newfreq < Decimal("0.0"):
				newfreq = Decimal("0.0")
			if newfreq > Decimal("1766.0"):
				newfreq = Decimal("1766.0")
		elif config.sdgradio.modulation.value == "dab":
			if newfreq < Decimal("174.928"):
				newfreq = Decimal("174.928")
			if newfreq > Decimal("239.2"):
				newfreq = Decimal("239.2")
			if newfreq > Decimal(freq):
				newfreq = min(filter(lambda x: x >= newfreq, DAB_FREQ.keys()))
			else:
				newfreq = max(filter(lambda x: x <= newfreq, DAB_FREQ.keys()))
		else:
			if newfreq < Decimal("0.0"):
				newfreq = Decimal("0.0")
			if newfreq > Decimal("1766.0"):
				newfreq = Decimal("1766.0")
		self["freq"].setText(str(newfreq))
		self["dab_channel"].setText(DAB_FREQ.get(newfreq, ""))

	def freqUp(self, value):
		self.freqChange(Decimal(value))

	def freqDown(self, value):
		self.freqChange(-Decimal(value))

	def ok(self):
		freq = self["freq"].getText()
		lastfreq = config.sdgradio.last.value
		if Decimal(freq) != Decimal(lastfreq):
			self.buttonSelect(config.sdgradio.lastbutton.value, freq)

	def red(self):
		config.sdgradio.modulation.selectNext()
		config.sdgradio.modulation.save()
		self["key_red"].setText(config.sdgradio.modulation.getText())
		self.freqChange(Decimal(0))
		self.yellowText()

	def storePreset(self, number):
		freq = self["freq"].getText()
		preset = eval("config.sdgradio.%s" % chr(97 + number))
		preset.value = freq
		preset.save()
		self.buttonSelect(number, freq)
		msg = _("Selected frequency of %s MHz successfuly stored to memory preset %d.") % (freq, number)
		self.session.open(MessageBox, msg, MessageBox.TYPE_INFO, timeout=5, close_on_any_key=True)

	def startup(self):
		self.yellowText()
		self.buttonSelect(config.sdgradio.lastbutton.value, config.sdgradio.last.value)

	def cancel(self):
		self.doConsoleStop()
		config.sdgradio.last.save()
		config.sdgradio.lastbutton.save()
		config.sdgradio.save()
		self.close(False, self.session)
		self.session.nav.playService(self.oldService)

	def info(self):
		self.doConsoleStop()
		self.session.open(Console, _("Info"), ["sleep 0.5 && rtl_eeprom"])

	def yellow(self):
		self.yellowText()
		if config.sdgradio.modulation.value == "fm":
			config.sdgradio.rds.value = not config.sdgradio.rds.value
			config.sdgradio.rds.save()
			self.doConsoleStop()
			self.buttonSelect(config.sdgradio.lastbutton.value, config.sdgradio.last.value)
		elif config.sdgradio.modulation.value == "dab":
			if self.console:
				self.console.write("\n") # new line switches to next program

	def yellowText(self):
		if config.sdgradio.modulation.value == "fm":
			if config.sdgradio.rds.value:
				self["key_yellow"].setText(_("RDS On"))
			else:
				self["key_yellow"].setText(_("RDS Off"))
		elif config.sdgradio.modulation.value == "dab":
			self["key_yellow"].setText(_("Next Station"))
		else:
			self["key_yellow"].setText("")

	def blue(self):
		text = "".join(self.log)
		self.session.open(Console, _("Log"), ["cat << EOF\n%s\nEOF" % text])

	def showPrograms(self):
		if config.sdgradio.modulation.value == "dab" and self.console:
			if self.programs:
				self.session.openWithCallback(self.programAction, ChoiceBox, title=_("Select Radio Program"), list=self.programs)
			else:
				self.session.open(MessageBox, _("No Programs"), MessageBox.TYPE_ERROR)

	def programAction(self, choice):
		if choice and self.console:
			self.console.write("%s\n" % choice[1])

	def getConfigOptions(self):
		print "[SDG radio] Reading config options"
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

	def showMenu(self):
		def showMenuCb(retval=True): # KeyCancel returns False, while KeySave returns None!
			if retval is True:
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
