from Components.config import config
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
import gettext

try:
	cat = gettext.translation("SDGRadio", resolveFilename(SCOPE_PLUGINS, "Extensions/SDGRadio/locale/"), [config.osd.language.getText()])
	_ = cat.gettext
except IOError:
	pass
