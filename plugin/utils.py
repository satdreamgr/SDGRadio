from collections import OrderedDict
from decimal import Decimal
from enigma import getDesktop
from Tools.Directories import resolveFilename, SCOPE_PLUGINS


try:
	addFont(resolveFilename(SCOPE_PLUGINS, "Extensions/SDGRadio/fonts/mssdr-digitali.ttf"), "Digital", 90, 1)
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

SKIN = """
	<screen name="SDGRadioScreen" title="Software defined radio" position="center,center" size="680,460">
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
		<widget name="mem_0" pixmaps="~/img/mem_0_empty.png,~/img/mem_0_stored.png,~/img/mem_0_selected.png" position="190,420" size="40,40" alphatest="blend"/>
		<widget name="mem_1" pixmaps="~/img/mem_1_empty.png,~/img/mem_1_stored.png,~/img/mem_1_selected.png" position="240,420" size="40,40" alphatest="blend"/>
		<widget name="mem_2" pixmaps="~/img/mem_2_empty.png,~/img/mem_2_stored.png,~/img/mem_2_selected.png" position="290,420" size="40,40" alphatest="blend"/>
		<widget name="mem_3" pixmaps="~/img/mem_3_empty.png,~/img/mem_3_stored.png,~/img/mem_3_selected.png" position="340,420" size="40,40" alphatest="blend"/>
		<widget name="mem_4" pixmaps="~/img/mem_4_empty.png,~/img/mem_4_stored.png,~/img/mem_4_selected.png" position="390,420" size="40,40" alphatest="blend"/>
		<widget name="mem_5" pixmaps="~/img/mem_5_empty.png,~/img/mem_5_stored.png,~/img/mem_5_selected.png" position="440,420" size="40,40" alphatest="blend"/>
		<widget name="mem_6" pixmaps="~/img/mem_6_empty.png,~/img/mem_6_stored.png,~/img/mem_6_selected.png" position="490,420" size="40,40" alphatest="blend"/>
		<widget name="mem_7" pixmaps="~/img/mem_7_empty.png,~/img/mem_7_stored.png,~/img/mem_7_selected.png" position="540,420" size="40,40" alphatest="blend"/>
		<widget name="mem_8" pixmaps="~/img/mem_8_empty.png,~/img/mem_8_stored.png,~/img/mem_8_selected.png" position="590,420" size="40,40" alphatest="blend"/>
		<widget name="mem_9" pixmaps="~/img/mem_9_empty.png,~/img/mem_9_stored.png,~/img/mem_9_selected.png" position="640,420" size="40,40" alphatest="blend"/>
		<ePixmap pixmap="buttons/key_info.png" position="0,420" size="40,40" alphatest="blend"/>
		<ePixmap pixmap="buttons/key_menu.png" position="50,420" size="40,40" alphatest="blend"/>
	</screen>"""
