from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
import gettext

LOCALES_DOMAIN = "SDGRadio"
LOCALES_RELPATH = "Extensions/SDGRadio/locale"


def _locale_init():
	gettext.bindtextdomain(
		LOCALES_DOMAIN,
		resolveFilename(SCOPE_PLUGINS, LOCALES_RELPATH))


def _(txt):
	try:
		t = gettext.dgettext(LOCALES_DOMAIN, txt)
		if t == txt:
			t = gettext.gettext(txt)
		return t
	except Exception:
		return txt


_locale_init()
language.addCallback(_locale_init)
