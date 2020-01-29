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
	705, 870, 35, 35,
	755, 870, 35, 35,
	805, 870, 35, 35,
	855, 870, 35, 35,
	905, 870, 35, 35,
	955, 870, 35, 35,
	1005, 870, 35, 35,
	1055, 870, 35, 35,
	1105, 870, 35, 35,
	1155, 870, 35, 35,

	765, 440, 150, 35, 30,
	765, 500, 150, 35, 30,
	920, 440, 720, 100, 95,
	920, 440, 720, 100, 95,
	1645, 505, 65, 35, 30,

	920, 545, 720, 55, 40,
	825, 402, 85, 30,
	1650, 545, 30, 30,
	1645, 600, 60, 30,
	920, 600, 720, 140, 30,

	1420, 400, 290, 35, 30,
	920, 400, 130, 35, 30,
	1055, 400, 85, 35, 30,
	1145, 400, 45, 35, 30,
	1195, 400, 45, 35, 30,
	1245, 400, 80, 35, 30,
	1335, 400, 55, 35, 30,
	640, 540, 280, 200,

	670, 918, 195, 40, 25,
	925, 918, 185, 40, 25,
	1150, 918, 270, 40, 25,
	1460, 918, 270, 40, 25,

	635, 405, 30, 30,
	670, 408, 130, 30, 25
)

SKIN = """
	<screen name="SDGRadioScreen" title="Software defined radio" position="center,center" size="e,e" flags="wfNoBorder" backgroundColor="transparent">
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
		<widget name="radiotext" position="%d,%d" size="%d,%d" font="Regular;%d" valign="top" halign="center" foregroundColor="#ffffc6" backgroundColor="#003258" transparent="1" noWrap="1"/>

		<widget name="prog_type" position="%d,%d" size="%d,%d" font="Regular;%d" valign="center" halign="right" foregroundColor="#00deff" backgroundColor="#003258" zPosition="5" transparent="1"/>
		<widget name="pi" position="%d,%d" size="%d,%d" font="Regular;%d" valign="center" halign="left" foregroundColor="#00deff" backgroundColor="#003258" zPosition="5" transparent="1"/>
		<widget name="traffic" position="%d,%d" size="%d,%d" font="Regular;%d" valign="center" halign="left" foregroundColor="#00deff" backgroundColor="#003258" zPosition="5" transparent="1"/>
		<widget name="af" position="%d,%d" size="%d,%d" font="Regular;%d" valign="center" halign="center" foregroundColor="#00deff" backgroundColor="#003258" zPosition="5" transparent="1"/>
		<widget name="ct" position="%d,%d" size="%d,%d" font="Regular;%d" valign="center" halign="center" foregroundColor="#00deff" backgroundColor="#003258" zPosition="5" transparent="1"/>
		<widget name="eon" position="%d,%d" size="%d,%d" font="Regular;%d" valign="center" halign="center" foregroundColor="#00deff" backgroundColor="#003258" zPosition="5" transparent="1"/>
		<widget name="rt+" position="%d,%d" size="%d,%d" font="Regular;%d" valign="center" halign="center" foregroundColor="#00deff" backgroundColor="#003258" zPosition="5" transparent="1"/>
		<widget name="pic" position="%d,%d" size="%d,%d" alphatest="on" scale="1" backgroundColor="#003258" zPosition="10" transparent="1"/>

		<widget source="key_red" render="Label" position="%d,%d" size="%d,%d" font="Regular;%d" valign="center" foregroundColor="#000000" backgroundColor="#ffffff" noWrap="1" transparent="1"/>
		<widget source="key_green" render="Label" position="%d,%d" size="%d,%d" font="Regular;%d" valign="center" foregroundColor="#000000" backgroundColor="#ffffff" noWrap="1" transparent="1"/>
		<widget source="key_yellow" render="Label" position="%d,%d" size="%d,%d" font="Regular;%d" valign="center" foregroundColor="#000000" backgroundColor="#ffffff" noWrap="1" transparent="1"/>
		<widget source="key_blue" render="Label" position="%d,%d" size="%d,%d" font="Regular;%d" valign="center" foregroundColor="#000000" backgroundColor="#ffffff" noWrap="1" transparent="1"/>

		<ePixmap pixmap="~/img/clock.png" position="%d,%d" size="%d,%d" alphatest="blend" scale="1"/>
		<widget source="global.CurrentTime" render="Label" position="%d,%d" size="%d,%d" font="SDGRadio;%d" valign="center" foregroundColor="#00deff" backgroundColor="#003258" transparent="1">
			<convert type="ClockToText">Default</convert>
		</widget>
	</screen>""" % tuple([i * getDesktop(0).size().height() / 1080 for i in SKIN_DATA])
