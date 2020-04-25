from collections import OrderedDict
from decimal import Decimal
from enigma import addFont, getDesktop
from Tools.Directories import resolveFilename, SCOPE_PLUGINS


try:
	addFont(resolveFilename(SCOPE_PLUGINS, "Extensions/SDGRadio/fonts/DSEG7Classic-BoldItalic.ttf"), "SDGRadio", 100, 1)
except:
	print "[SDGRadio] failed to add font"


SDR_MIN_FREQ = 0
SDR_MAX_FREQ = 1766

DAB_FREQ = OrderedDict([
	(Decimal("174.928"), "5A"), (Decimal("176.640"), "5B"), (Decimal("178.352"), "5C"), (Decimal("180.064"), "5D"),
	(Decimal("181.936"), "6A"), (Decimal("183.648"), "6B"), (Decimal("185.360"), "6C"), (Decimal("187.072"), "6D"),
	(Decimal("188.928"), "7A"), (Decimal("190.640"), "7B"), (Decimal("192.352"), "7C"), (Decimal("194.064"), "7D"),
	(Decimal("195.936"), "8A"), (Decimal("197.648"), "8B"), (Decimal("199.360"), "8C"), (Decimal("201.072"), "8D"),
	(Decimal("202.928"), "9A"), (Decimal("204.640"), "9B"), (Decimal("206.352"), "9C"), (Decimal("208.064"), "9D"),
	(Decimal("209.936"), "10A"), (Decimal("211.648"), "10B"), (Decimal("213.360"), "10C"), (Decimal("215.072"), "10D"),
	(Decimal("216.928"), "11A"), (Decimal("218.640"), "11B"), (Decimal("220.352"), "11C"), (Decimal("222.064"), "11D"),
	(Decimal("223.936"), "12A"), (Decimal("225.648"), "12B"), (Decimal("227.360"), "12C"), (Decimal("229.072"), "12D"),
	(Decimal("230.748"), "13A"), (Decimal("232.496"), "13B"), (Decimal("234.208"), "13C"), (Decimal("235.776"), "13D"),
	(Decimal("237.488"), "13E"), (Decimal("239.200"), "13F")
])

SKIN_DATA = (
	1155, 630,

	105, 495, 35, 35,
	155, 495, 35, 35,
	205, 495, 35, 35,
	255, 495, 35, 35,
	305, 495, 35, 35,
	355, 495, 35, 35,
	405, 495, 35, 35,
	455, 495, 35, 35,
	505, 495, 35, 35,
	555, 495, 35, 35,

	165, 65, 150, 35, 30,
	165, 125, 150, 35, 30,
	320, 65, 720, 100, 95,
	320, 65, 720, 100, 95,
	1045, 130, 65, 35, 30,

	320, 170, 720, 55, 40,
	225, 29, 85, 30,
	1060, 170, 30, 30,
	1045, 230, 60, 30,
	320, 230, 720, 140, 30,

	820, 27, 290, 35, 30,
	320, 27, 130, 35, 30,
	455, 27, 85, 35, 30,
	545, 27, 45, 35, 30,
	595, 27, 45, 35, 30,
	645, 27, 80, 35, 30,
	735, 27, 55, 35, 30,
	40, 165, 280, 200,

	25, 550, 35, 35,
	335, 550, 35, 35,
	585, 550, 35, 35,
	865, 550, 35, 35,

	65, 550, 265, 35, 24,
	375, 550, 205, 35, 24,
	625, 550, 235, 35, 24,
	905, 550, 235, 35, 24,

	35, 30, 30, 30,
	70, 32, 130, 30, 24
)

SKIN = """
	<screen name="SDGRadioScreen" title="Software defined radio" position="center,center" size="%d,%d" flags="wfNoBorder" backgroundColor="transparent">
		<ePixmap pixmap="~/img/radiobackground.png" position="center,center" size="e,e" alphatest="on" scale="1" zPosition="-10"/>
		<widget name="mem_1" pixmaps="~/img/mem_1_empty.png,~/img/mem_1_stored.png,~/img/mem_1_selected.png" position="%d,%d" size="%d,%d" alphatest="blend" scale="1" zPosition="5"/>
		<widget name="mem_2" pixmaps="~/img/mem_2_empty.png,~/img/mem_2_stored.png,~/img/mem_2_selected.png" position="%d,%d" size="%d,%d" alphatest="blend" scale="1" zPosition="5"/>
		<widget name="mem_3" pixmaps="~/img/mem_3_empty.png,~/img/mem_3_stored.png,~/img/mem_3_selected.png" position="%d,%d" size="%d,%d" alphatest="blend" scale="1" zPosition="5"/>
		<widget name="mem_4" pixmaps="~/img/mem_4_empty.png,~/img/mem_4_stored.png,~/img/mem_4_selected.png" position="%d,%d" size="%d,%d" alphatest="blend" scale="1" zPosition="5"/>
		<widget name="mem_5" pixmaps="~/img/mem_5_empty.png,~/img/mem_5_stored.png,~/img/mem_5_selected.png" position="%d,%d" size="%d,%d" alphatest="blend" scale="1" zPosition="5"/>
		<widget name="mem_6" pixmaps="~/img/mem_6_empty.png,~/img/mem_6_stored.png,~/img/mem_6_selected.png" position="%d,%d" size="%d,%d" alphatest="blend" scale="1" zPosition="5"/>
		<widget name="mem_7" pixmaps="~/img/mem_7_empty.png,~/img/mem_7_stored.png,~/img/mem_7_selected.png" position="%d,%d" size="%d,%d" alphatest="blend" scale="1" zPosition="5"/>
		<widget name="mem_8" pixmaps="~/img/mem_8_empty.png,~/img/mem_8_stored.png,~/img/mem_8_selected.png" position="%d,%d" size="%d,%d" alphatest="blend" scale="1" zPosition="5"/>
		<widget name="mem_9" pixmaps="~/img/mem_9_empty.png,~/img/mem_9_stored.png,~/img/mem_9_selected.png" position="%d,%d" size="%d,%d" alphatest="blend" scale="1" zPosition="5"/>
		<widget name="mem_0" pixmaps="~/img/mem_0_empty.png,~/img/mem_0_stored.png,~/img/mem_0_selected.png" position="%d,%d" size="%d,%d" alphatest="blend" scale="1" zPosition="5"/>

		<widget name="modulation" position="%d,%d" size="%d,%d" font="Regular;%d" valign="center" halign="right" foregroundColor="#0090e6" backgroundColor="#003258" transparent="1"/>
		<widget name="dab_channel" position="%d,%d" size="%d,%d" font="Regular;%d" valign="center" halign="right" foregroundColor="#0090e6" backgroundColor="#003258" transparent="1"/>
		<widget name="freq_off" position="%d,%d" size="%d,%d" font="SDGRadio;%d" valign="center" halign="center" foregroundColor="#283742" backgroundColor="#003258" transparent="1" zPosition="-5"/>
		<widget name="freq" position="%d,%d" size="%d,%d" font="SDGRadio;%d" valign="center" halign="center" foregroundColor="#0090e6" backgroundColor="#003258" transparent="1"/>
		<widget name="freq_units" position="%d,%d" size="%d,%d" font="Regular;%d" valign="center" halign="right" foregroundColor="#0090e6" backgroundColor="#003258" transparent="1"/>

		<widget source="Title" render="Label" position="%d,%d" size="%d,%d" font="Regular;%d" halign="center" valign="center" foregroundColor="#00deff" backgroundColor="#003258" transparent="1" noWrap="1"/>
		<widget name="rds_icon" pixmap="~/img/rds_on.png" position="%d,%d" size="%d,%d" alphatest="blend" scale="1" zPosition="5" transparent="1"/>
		<widget name="ps_icon" pixmap="~/img/ps_on.png" position="%d,%d" size="%d,%d" alphatest="blend" scale="1" zPosition="5" transparent="1"/>
		<widget name="rt_icon" pixmap="~/img/rt_on.png" position="%d,%d" size="%d,%d" alphatest="blend" scale="1" zPosition="5" transparent="1"/>
		<widget name="radiotext" position="%d,%d" size="%d,%d" font="Regular;%d" valign="top" halign="center" foregroundColor="#ffffc6" backgroundColor="#003258" transparent="1"/>

		<widget name="prog_type" position="%d,%d" size="%d,%d" font="Regular;%d" valign="center" halign="right" foregroundColor="#00deff" backgroundColor="#003258" zPosition="5" transparent="1"/>
		<widget name="pi" position="%d,%d" size="%d,%d" font="Regular;%d" valign="center" halign="left" foregroundColor="#00deff" backgroundColor="#003258" zPosition="5" transparent="1"/>
		<widget name="traffic" position="%d,%d" size="%d,%d" font="Regular;%d" valign="center" halign="left" foregroundColor="#00deff" backgroundColor="#003258" zPosition="5" transparent="1"/>
		<widget name="af" position="%d,%d" size="%d,%d" font="Regular;%d" valign="center" halign="center" foregroundColor="#00deff" backgroundColor="#003258" zPosition="5" transparent="1"/>
		<widget name="ct" position="%d,%d" size="%d,%d" font="Regular;%d" valign="center" halign="center" foregroundColor="#00deff" backgroundColor="#003258" zPosition="5" transparent="1"/>
		<widget name="eon" position="%d,%d" size="%d,%d" font="Regular;%d" valign="center" halign="center" foregroundColor="#00deff" backgroundColor="#003258" zPosition="5" transparent="1"/>
		<widget name="rt+" position="%d,%d" size="%d,%d" font="Regular;%d" valign="center" halign="center" foregroundColor="#00deff" backgroundColor="#003258" zPosition="5" transparent="1"/>
		<widget name="pic" position="%d,%d" size="%d,%d" alphatest="on" scale="1" backgroundColor="#003258" zPosition="10" transparent="1"/>

		<widget objectTypes="key_red,StaticText" source="key_red" render="Pixmap" pixmap="~/img/key_red.png" position="%d,%d" size="%d,%d" alphatest="blend" zPosition="5" transparent="1" scale="1">
			<convert type="ConditionalShowHide" />
		</widget>
		<widget objectTypes="key_green,StaticText" source="key_green" render="Pixmap" pixmap="~/img/key_green.png" position="%d,%d" size="%d,%d" alphatest="blend" zPosition="5" transparent="1" scale="1">
			<convert type="ConditionalShowHide"/>
		</widget>
		<widget objectTypes="key_yellow,StaticText" source="key_yellow" render="Pixmap" pixmap="~/img/key_yellow.png" position="%d,%d" size="%d,%d" alphatest="blend" zPosition="5" transparent="1" scale="1">
			<convert type="ConditionalShowHide"/>
		</widget>
		<widget objectTypes="key_blue,StaticText" source="key_blue" render="Pixmap" pixmap="~/img/key_blue.png" position="%d,%d" size="%d,%d" alphatest="blend" zPosition="5" transparent="1" scale="1">
			<convert type="ConditionalShowHide"/>
		</widget>

		<widget source="key_red" render="Label" position="%d,%d" size="%d,%d" font="Regular;%d" valign="center" foregroundColor="#000000" backgroundColor="#ffffff" noWrap="1" transparent="1"/>
		<widget source="key_green" render="Label" position="%d,%d" size="%d,%d" font="Regular;%d" valign="center" foregroundColor="#000000" backgroundColor="#ffffff" noWrap="1" transparent="1"/>
		<widget source="key_yellow" render="Label" position="%d,%d" size="%d,%d" font="Regular;%d" valign="center" foregroundColor="#000000" backgroundColor="#ffffff" noWrap="1" transparent="1"/>
		<widget source="key_blue" render="Label" position="%d,%d" size="%d,%d" font="Regular;%d" valign="center" foregroundColor="#000000" backgroundColor="#ffffff" noWrap="1" transparent="1"/>

		<ePixmap pixmap="~/img/clock.png" position="%d,%d" size="%d,%d" alphatest="blend" scale="1"/>
		<widget source="global.CurrentTime" render="Label" position="%d,%d" size="%d,%d" font="SDGRadio;%d" valign="center" foregroundColor="#00deff" backgroundColor="#003258" transparent="1">
			<convert type="ClockToText">Default</convert>
		</widget>
	</screen>""" % tuple([i * getDesktop(0).size().height() / 1080 for i in SKIN_DATA])

RAW_DATA = (
	1155, 611,
	15, 15, 1125, 40, 30,
	15, 70, 1125, 456,
	260, 551, 35, 35,
	767, 551, 35, 35,
	310, 550, 300, 35, 31,
	817, 550, 300, 35, 31,
	15, 541, 1125, 55
	)

RAWSKIN = """
	<screen name="RawFile" position="center,center" size="%d,%d" title=" " transparent="0">
		<widget source="curdir" render="Label" position="%d,%d" size="%d,%d" valign="center" halign="center" zPosition="1" foregroundColor="#00f0f0f0" font="Regular;%d" backgroundColor="#333333" transparent="0" noWrap="1" />
		<widget name="filelist" position="%d,%d" size="%d,%d" scrollbarMode="showOnDemand" />
		<ePixmap pixmap="~/img/key_red.png" position="%d,%d" size="%d,%d" alphatest="on" zPosition="2" />
		<widget objectTypes="key_green,StaticText" source="key_green" render="Pixmap" pixmap="~/img/key_green.png" position="%d,%d" size="%d,%d" alphatest="on" zPosition="2" >
			<convert type="ConditionalShowHide" />
		</widget>
		<widget source="key_red" render="Label" position="%d,%d" size="%d,%d" valign="center" halign="left" backgroundColor="#f0f0f0" font="Regular;%d" transparent="1" zPosition="2" />
		<widget source="key_green" render="Label" position="%d,%d" size="%d,%d" valign="center" halign="left" backgroundColor="#f0f0f0" font="Regular;%d" transparent="1" zPosition="2" />
		<eLabel position="%d,%d" size="%d,%d" backgroundColor="#333333" transparent="0" zPosition="1" />
	</screen>"""  % tuple([s * getDesktop(0).size().height() / 1080 for s in RAW_DATA])
