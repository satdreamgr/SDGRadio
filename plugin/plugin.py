from Components.AVSwitch import AVSwitch
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.config import config, ConfigSubsection, ConfigText, ConfigInteger, ConfigBoolean, ConfigSelection
from Plugins.Plugin import PluginDescriptor
from Screens.ChoiceBox import ChoiceBox
from Screens.Console import Console
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Tools.BoundFunction import boundFunction
from enigma import eConsoleAppContainer

import json
import time
import binascii
from decimal import Decimal
from collections import OrderedDict

config.sdgradio = ConfigSubsection()
config.sdgradio.last = ConfigText(default = "87.5")
config.sdgradio.lastbutton = ConfigInteger(default = 0, limits = (0, 9))
config.sdgradio.a = ConfigText(default = "87.5")
config.sdgradio.b = ConfigText(default = "89.0")
config.sdgradio.c = ConfigText(default = "94.0")
config.sdgradio.d = ConfigText(default = "96.0")
config.sdgradio.e = ConfigText(default = "98.0")
config.sdgradio.f = ConfigText(default = "98.0")
config.sdgradio.g = ConfigText(default = "100.0")
config.sdgradio.h = ConfigText(default = "102.0")
config.sdgradio.i = ConfigText(default = "107.0")
config.sdgradio.j = ConfigText(default = "108.0")
config.sdgradio.rds = ConfigBoolean(default = False)
config.sdgradio.modulation = ConfigSelection(choices=[("fm", _("FM")), ("am", _("AM")), ("lsb", _("LSB")), ("usb", _("USB")), ("dab", _("DAB/DAB+"))], default="fm")
config.sdgradio.ppmoffset = ConfigInteger(default = 0)

DAB_FREQ = OrderedDict([(Decimal('174.928'), '5A'), (Decimal('176.64'), '5B'), (Decimal('178.352'), '5C'), (Decimal('180.064'), '5D'), (Decimal('181.936'), '6A'), (Decimal('183.648'), '6B'), (Decimal('185.36'), '6C'), (Decimal('187.072'), '6D'), (Decimal('188.928'), '7A'), (Decimal('190.64'), '7B'), (Decimal('192.352'), '7C'), (Decimal('194.064'), '7D'), (Decimal('195.936'), '8A'), (Decimal('197.648'), '8B'), (Decimal('199.36'), '8C'), (Decimal('201.072'), '8D'), (Decimal('202.928'), '9A'), (Decimal('204.64'), '9B'), (Decimal('206.352'), '9C'), (Decimal('208.064'), '9D'), (Decimal('209.936'), '10A'), (Decimal('211.648'), '10B'), (Decimal('213.36'), '10C'), (Decimal('215.072'), '10D'), (Decimal('216.928'), '11A'), (Decimal('218.64'), '11B'), (Decimal('220.352'), '11C'), (Decimal('222.064'), '11D'), (Decimal('223.936'), '12A'), (Decimal('225.648'), '12B'), (Decimal('227.36'), '12C'), (Decimal('229.072'), '12D'), (Decimal('230.748'), '13A'), (Decimal('232.496'), '13B'), (Decimal('234.208'), '13C'), (Decimal('235.776'), '13D'), (Decimal('237.488'), '13E'), (Decimal('239.2'), '13F')])

try:
	from enigma import addFont
	addFont('/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/fonts/mssdr-digitali.ttf', 'Digital', 90, 1)
except:
	print "[SDGRadio] failed to add font"

BTN_MEM_DOWN = "/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/btn_mem_0%d_down.png"
BTN_MEM_UP = "/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/btn_mem_0%d_up.png"

class SDGRadioScreen(Screen):
	skin="""
	<screen name="SDGRadioScreen" position="center,center" size="1280,720" title="SDG Radio" backgroundColor="transparent" flags="wfNoBorder">
	<widget source="Title" render="Label" position="230,68" size="820,50" backgroundColor="#50000000" transparent="1" zPosition="5" font="Regular; 28" valign="center" halign="center" noWrap="1" foregroundColor="#ff1100" />
	<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/fleched.png" position="145,81" size="32,32" transparent="0" zPosition="8" alphatest="on" />
	<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/flecheg.png" position="1054,81" size="32,32" transparent="0" zPosition="8" alphatest="on" />
	<eLabel position="310,130" zPosition="-1" size="828,460" backgroundColor="transpBA" transparent="0" font="Regular; 0" foregroundColor="transparent" />
	<ePixmap name="" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/logo.png" position="1098,84" size="24, 24" alphatest="blend" zPosition="10" />
	<eLabel name="" position="140,64" size="1000,60" zPosition="-1" backgroundColor="NLPreBlack" />
	<eLabel name="" position="140,594" size="1000,60" backgroundColor="NLPreBlack" zPosition="-1" />
	<eLabel name="" position="140,124" size="165,471" backgroundColor="#000064c7" zPosition="0" />
	<eLabel position="151,198" zPosition="1" size="146,310" backgroundColor="transpBA" transparent="0" />
	<widget source="global.CurrentTime" render="Label" position="140,166" size="165,25" backgroundColor="#000064c7" transparent="1" font="Regular; 22" valign="center" halign="center" foregroundColor="white" zPosition="2">
	<convert type="ClockToText">Format:%d-%m-%Y</convert>
	</widget>
	<widget source="global.CurrentTime" render="Label" position="140,133" size="165,25" backgroundColor="#000064c7" transparent="1" font="Regular; 22" valign="center" halign="center" foregroundColor="white" zPosition="2">
	<convert type="ClockToText">Format:%A</convert>
	</widget>
	<widget source="global.CurrentTime" render="Label" position="140,529" size="110,40" backgroundColor="#000064c7" transparent="1" font="Regular; 32" halign="right" valign="center" zPosition="2" foregroundColor="white">
	<convert type="ClockToText">Format:%-H:%M</convert>
	</widget>
	<widget source="global.CurrentTime" render="Label" position="247,533" size="45,20" font="Regular; 20" halign="left" valign="center" transparent="1" backgroundColor="#000064c7" foregroundColor="jeaune" zPosition="2">
	<convert type="ClockToText">Format: :%S</convert>
	</widget>
	<eLabel name="" position="340,594" size="200,6" zPosition="0" backgroundColor="red" />
	<eLabel name="" position="540,594" size="200,6" zPosition="1" backgroundColor="green" />
	<eLabel name="" position="740,594" size="200,6" zPosition="2" backgroundColor="yellow" />
	<eLabel name="" position="940,594" size="200,6" zPosition="2" backgroundColor="#000064c7" />
	<eLabel name="" position="140,594" size="200,6" zPosition="2" backgroundColor="white" />
	<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/line1.png" position="155,205" size="135,1" scale="1" zPosition="10" alphatest="blend" />
	<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/line1.png" position="155,500" size="135,1" scale="1" zPosition="10" alphatest="blend" />
	<widget name="key_red" position="340,600" size="200,50" backgroundColor="transpBA" zPosition="1" transparent="1" font="Regular; 22" halign="center" valign="center" foregroundColor="white" />
	<widget name="key_green" position="540,600" size="200,50" backgroundColor="transpBA" zPosition="1" transparent="1" font="Regular; 22" halign="center" valign="center" foregroundColor="white" />
	<widget name="key_yellow" position="740,600" size="200,50" backgroundColor="transpBA" zPosition="1" transparent="1" font="Regular; 22" halign="center" valign="center" foregroundColor="white" />
	<widget name="key_blue" position="940,600" size="200,50" backgroundColor="transpBA" zPosition="1" transparent="1" font="Regular;22" halign="center" valign="center" foregroundColor="white" />
	<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/key_info.png" position="175,610" size="40,30" alphatest="blend" transparent="1" zPosition="1" />
	<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/key_menu.png" position="225,610" size="40,30" alphatest="blend" transparent="1" zPosition="1" />
	<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/flecheg.png" position="157,277" size="40,30" alphatest="blend" transparent="1" zPosition="2" />
	<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/fleched.png" position="263,277" size="40,30" alphatest="blend" transparent="1" zPosition="2" />
	<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/flecheh.png" position="210,235" size="40,30" alphatest="blend" transparent="1" zPosition="2" />
	<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/flecheb.png" position="210,315" size="40,30" alphatest="blend" transparent="1" zPosition="2" />
	<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/radio-frequency.png" position="310,130" size="828,460" scale="1" zPosition="0" alphatest="blend" />
	<widget name="mem_0" position="182,355" size="40,30" alphatest="on" zPosition="2" />
	<widget name="mem_1" position="232,355" size="40,30" alphatest="on" zPosition="2" />
	<widget name="mem_2" position="157,390" size="40,30" alphatest="on" zPosition="2" />
	<widget name="mem_3" position="205,390" size="40,30" alphatest="on" zPosition="2" />
	<widget name="mem_4" position="252,390" size="40,30" alphatest="on" zPosition="2" />
	<widget name="mem_5" position="157,425" size="40,30" alphatest="on" zPosition="2" />
	<widget name="mem_6" position="205,425" size="40,30" alphatest="on" zPosition="2" />
	<widget name="mem_7" position="252,425" size="40,30" alphatest="on" zPosition="2" />
	<widget name="mem_8" position="182,463" size="40,30" alphatest="on" zPosition="2" />
	<widget name="mem_9" position="232,463" size="40,30" alphatest="on" zPosition="2" />
	<widget name="freq" position="560,187" size="440,120" valign="center" halign="center" zPosition="2" foregroundColor="#ff1100" font="Digital;160" transparent="1" backgroundColor="#ff1100" />
	<widget name="prog_type" position="651,370" size="300,30" valign="center" halign="center" zPosition="2" foregroundColor="#ff1100" font="Regular;30" transparent="1" backgroundColor="#ff1100" />
	<widget name="radiotext" position="316,460" size="590,110" valign="center" halign="center" zPosition="2" foregroundColor="#ff1100" font="Regular;24" transparent="1" backgroundColor="#ff1100" />
	<widget source="global.CurrentTime" render="Label" position="0,0" size="0,0" halign="center" valign="center" noWrap="1" zPosition="1" foregroundColor="white" font="Digital;120" transparent="1">
	<convert type="ClockToText">WithSeconds</convert>
	</widget>
	<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/SDGRadio/img/key_ok.png" position="205,277" size="40,32" transparent="0" zPosition="10" alphatest="on" />
	<eLabel name="Select" text="Select" position="151,210" size="146,22" foregroundColor="white" font="Regular; 22" zPosition="5" halign="center" />
	</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)

		for i in range(0,10):
			self["mem_%d" % i] = Pixmap()

		self["freq"] = Label()
		self["radiotext"] = Label()
		self["prog_type"] = Label()
		self["key_red"] = Label(config.sdgradio.modulation.getText())
		self["key_green"] = Label(_("Save"))
		self["key_yellow"] = Label()
		self["key_blue"] = Label(_("Log"))
		self["info"] = Label(_("Info"))

		# get currently playing service
		self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()

		# stop currently playing service
		self.session.nav.stopService()

		# log messages
		self.log = []

		# dab program list
		self.programs = []

		# display radio mvi
		eConsoleAppContainer().execute("showiframe /usr/share/enigma2/radio.mvi")

		#self.Scale = AVSwitch().getFramebufferScale()

		self["actions"] = ActionMap(["SetupActions", "DirectionActions", "WizardActions", "ColorActions", "MenuActions", "ChannelSelectEPGActions", "ChannelSelectBaseActions"],
		{
			"back": self.cancel, # add the RC Command "cancel" to close your Screen
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
			"up": boundFunction(self.up, "0.1"),
			"down": boundFunction(self.down, "0.1"),
			"left": self.left,
			"right": self.right,
			"ok": self.ok,
			"upRepeated": boundFunction(self.up, "0.1"),
			"downRepeated": boundFunction(self.down, "0.1"),
			"leftRepeated": self.left,
			"rightRepeated": self.right,
			"info": self.info,
			"red": self.red,
			"green": self.green,
			"yellow": self.yellow,
			"blue": self.blue,
			"nextBouquet": boundFunction(self.up, "0.0001"),
			"prevBouquet": boundFunction(self.down, "0.0001"),
			"nextMarker": boundFunction(self.up, "0.001"),
			"prevMarker": boundFunction(self.down, "0.001"),
			"menu": self.showPrograms,
		}, -1)

		self.Console = None
		self.onLayoutFinish.append(self.startup)

	def PlayRadio(self, freq):
		self.yellow_text()
		self.doConsoleStop()
		time.sleep(0.3)
		self.Console = eConsoleAppContainer()
		self.Console.stderrAvail.append(self.cbStderrAvail)
		#self.Console.appClosed.append(self.cbAppClosed)
		if config.sdgradio.modulation.value == "fm":
			if config.sdgradio.rds.value:
				cmd = "rtl_fm -f %sM -M fm -l 0 -A std -s 171k -g 40 -E deemp -F 0 - | redsea -e | gst-launch-1.0 fdsrc ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=171000 ! audioresample ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=48000 ! dvbaudiosink" % freq
			else:
				cmd = "rtl_fm -f %sM -M fm -l 0 -A std -s 171k -g 40 -E deemp -F 0 - | gst-launch-1.0 fdsrc ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=171000 ! audioresample ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=48000 ! dvbaudiosink" % freq
		elif config.sdgradio.modulation.value == "am":
			cmd = "rtl_fm -f %sM -M am -A std -s 10k -g 40 - | gst-launch-1.0 fdsrc ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=10000 ! audioresample ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=48000 ! dvbaudiosink" % freq
		elif config.sdgradio.modulation.value == "lsb":
			cmd = "rtl_fm -f %sM -M lsb -A std -s 3k -g 40 - | gst-launch-1.0 fdsrc ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=3000 ! audioresample ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=48000 ! dvbaudiosink" % freq
		elif config.sdgradio.modulation.value == "usb":
			cmd = "rtl_fm -f %sM -M usb -A std -s 3k -g 40 - | gst-launch-1.0 fdsrc ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=3000 ! audioresample ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=48000 ! dvbaudiosink" % freq
		elif config.sdgradio.modulation.value == "dab":
			cmd = "dab-rtlsdr-sdgradio -C %s -W30 -p %d | gst-launch-1.0 fdsrc ! queue ! faad ! dvbaudiosink" % (DAB_FREQ.get(Decimal(freq), '5A'), config.sdgradio.ppmoffset.value)
		else:
			cmd = "rtl_fm -f %sM -M wbfm -s 200000 -r 48000 - | gst-launch-1.0 fdsrc ! audio/x-raw, format=S16LE, channels=1, layout=interleaved, rate=48000 ! dvbaudiosink" % freq
		print "[SDGRadio] PlayRadio cmd: %s" % cmd
		self.Console.execute(cmd)

	def RDSProcess(self, data):
		try:
			rds = json.loads(data.decode('utf8', 'ignore'))
			if "ps" in rds and self.getTitle() != rds["ps"].encode('utf8'):
				self.setTitle(rds["ps"].encode('utf8'))
			if "radiotext" in rds and self["radiotext"].getText() != rds["radiotext"].encode('utf8'):
				self["radiotext"].setText(rds["radiotext"].encode('utf8'))
			if "partial_radiotext" in rds and self["radiotext"].getText() != rds["partial_radiotext"].encode('utf8'):
				self["radiotext"].setText(rds["partial_radiotext"].encode('utf8'))
			if "prog_type" in rds and self["prog_type"].getText() != rds["prog_type"].encode('utf8'):
				self["prog_type"].setText(rds["prog_type"].encode('utf8'))
			if "programType" in rds:
				self["prog_type"].setText(rds["programType"].encode('utf8'))
			if "programName" in rds and "programId" in rds:
				self.programs.append((rds["programName"].encode('utf8'), rds["programId"]))
		except Exception as e:
			str = "[SDGRadio] RDSProcess Exception: %s data: %s" % (e, binascii.hexlify(data))
			self.log.append(str)
			print str

	def cbStderrAvail(self, data):
		#print "[SDGRadio] cbStderrAvail ", data
		for line in data.splitlines():
			if not line:
				continue
			if "{" in line and "}" in line and ":" in line:
				self.RDSProcess(line)
		if not data in self.log:
			self.log.append(data)
		while len(self.log) > 200:
			self.log.pop(0)

	def doConsoleStop(self):
		if self.Console:
			self.Console.sendCtrlC()
			self.Console.sendEOF()
			if self.Console.running():
				self.Console.kill()
			self.Console = None
			self.log = []
			self.programs = []

	def ButtonSelect(self, number, freq):
		self["freq"].setText(freq)
		self.freqChange(Decimal(0))
		self["radiotext"].setText("")
		self["prog_type"].setText("")
		self.setTitle("SDG Radio %s" % freq)
		self.PlayRadio(freq)
		config.sdgradio.last.value = freq
		config.sdgradio.last.save()
		for i in range(0, 10):
			if i == number:
				config.sdgradio.lastbutton.value = i
				config.sdgradio.lastbutton.save()
				self["mem_%d" % i].instance.setPixmapFromFile(BTN_MEM_DOWN % i)
			else:
				self["mem_%d" % i].instance.setPixmapFromFile(BTN_MEM_UP % i)

	def buttonNumber(self, number):
		print "[SDGRadio] buttonNumber %d" % number
		freq = eval("config.sdgradio.%s.value" % chr(97+number))
		self.ButtonSelect(number, freq)

	def freqChange(self, value):
		freq = self["freq"].getText()
		newfreq = Decimal(freq) + value
		if config.sdgradio.modulation.value == "fm":
			if newfreq < Decimal("87.5"):
				newfreq = Decimal("87.5")
			if newfreq > Decimal("108.0"):
				newfreq = Decimal("108.0")
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

	def up(self, value):
		self.freqChange(Decimal(value))

	def down(self, value):
		self.freqChange(-Decimal(value))

	def left(self):
		self.freqChange(-Decimal("1"))

	def right(self):
		self.freqChange(Decimal("1"))

	def ok(self):
		freq = self["freq"].getText()
		lastfreq = config.sdgradio.last.value
		if Decimal(freq) != Decimal(lastfreq):
			self.ButtonSelect(config.sdgradio.lastbutton.value, freq)

	def red(self):
		print "[SDGRadio] red"
		config.sdgradio.modulation.selectNext()
		config.sdgradio.modulation.save()
		self["key_red"].setText(config.sdgradio.modulation.getText())
		self.freqChange(Decimal(0))

	def green(self):
		print "[SDGRadio] green"
		freq = self["freq"].getText()
		lastbutton = config.sdgradio.lastbutton.value
		if lastbutton >=0 and lastbutton <= 9:
			current_config = eval("config.sdgradio.%s" % chr(97+lastbutton))
			current_config.value = freq
			current_config.save()
		self.ButtonSelect(lastbutton, freq)
		self.session.open(MessageBox, _("Save"), MessageBox.TYPE_INFO, timeout = 5, close_on_any_key = True)

	def startup(self):
		self.ButtonSelect(config.sdgradio.lastbutton.value, config.sdgradio.last.value)

	def cancel(self):
		print "[SDGRadio] cancel"
		self.doConsoleStop()
		config.sdgradio.last.save()
		config.sdgradio.lastbutton.save()
		config.sdgradio.save()
		self.close(False, self.session)
		self.session.nav.playService(self.oldService)

	def info(self):
		print "[SDGRadio] info"
		self.doConsoleStop()
		self.session.open(Console,_("Info"),["sleep 0.5 && rtl_eeprom"])

	def yellow(self):
		print "[SDGRadio] yellow"
		self.yellow_text()
		if config.sdgradio.modulation.value == "fm":
			config.sdgradio.rds.value = not config.sdgradio.rds.value
			config.sdgradio.rds.save()
			self.doConsoleStop()
			self.startup()
		elif config.sdgradio.modulation.value == "dab":
			if self.Console:
				self.Console.write("\n") # new line switches to next program

	def blue(self):
		print "[SDGRadio] blue"
		text = "".join(self.log)
		self.session.open(Console,_("Log"),["cat << EOF\n%s\nEOF" % text])

	def yellow_text(self):
		if config.sdgradio.modulation.value == "fm":
			if config.sdgradio.rds.value:
				self["key_yellow"].setText(_("RDS On"))
			else:
				self["key_yellow"].setText(_("RDS Off"))
		elif config.sdgradio.modulation.value == "dab":
			self["key_yellow"].setText(_("Next Station"))
		else:
			self["key_yellow"].setText("")

	def showPrograms(self):
		print "[SDGRadio] showPrograms"
		if config.sdgradio.modulation.value == "dab" and self.Console:
			if self.programs:
				self.session.openWithCallback(self.programAction, ChoiceBox, title=_("Select Radio Program"), list=self.programs)
			else:
				self.session.open(MessageBox, _("No Programs"), MessageBox.TYPE_ERROR)

	def programAction(self, choice):
		print "[SDGRadio] programAction"
		if choice and self.Console:
			self.Console.write("%s\n" % choice[1])

def main(session, **kwargs):
	session.open(SDGRadioScreen)

def Plugins(**kwargs):
	return PluginDescriptor(name="Enigma2 Radio", description="Software Defined Radio",
		where = PluginDescriptor.WHERE_PLUGINMENU,
		needsRestart=False, icon="img/sdgradio.png", fnc=main)
