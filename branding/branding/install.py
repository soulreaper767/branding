import frappe

# "ERPNext"-origin strings become the plain product name; "Frappe"-origin
# strings become that name + "OS" - two different targets, not one shared
# one. All of these are routed through Frappe's own __() translation call
# somewhere (verified against frappe/frappe's actual source for the About
# dialog and the "Powered by" footer specifically), which is exactly what
# Label Override's Translation-record mechanism targets - if a given
# label doesn't visibly change after adding a row for it, that's a sign
# the label isn't translated at all and needs a one-off direct edit
# instead (see App Title Override for the one case handled that way:
# app_title itself, which is a plain hooks.py constant, not translated
# text).
DEFAULT_LABEL_OVERRIDES = [
	{"match_text": "ERPNext", "replacement_text": "Tijarat"},
	{"match_text": "Frappe", "replacement_text": "TijaratOS"},
	{"match_text": "Frappe Framework", "replacement_text": "TijaratOS"},
	{"match_text": "Frappe Framework Version", "replacement_text": "TijaratOS Version"},
	{"match_text": "Frappe Technologies", "replacement_text": "TijaratOS"},
	{"match_text": "Frappe Cloud", "replacement_text": "TijaratOS"},
	{"match_text": "Frappe School", "replacement_text": "TijaratOS School"},
	{"match_text": "Frappe Forum", "replacement_text": "TijaratOS Forum"},
	{"match_text": "Frappe Support", "replacement_text": "TijaratOS Support"},
	{"match_text": "About Frappe", "replacement_text": "About TijaratOS"},
	{"match_text": "Powered by Frappe", "replacement_text": "Powered by TijaratOS"},
	{"match_text": "Built on Frappe Framework", "replacement_text": "Built on TijaratOS"},
	{"match_text": "Open Source applications for the web.", "replacement_text": "TijaratOS"},
	{"match_text": "Frappe HR", "replacement_text": "TijaratOS HR"},
	{"match_text": "HRMS", "replacement_text": "TijaratOS HR"},
]

# app_title is a plain Python constant in each app's own hooks.py, not
# routed through __() at all - Label Override can't reach it, which is
# why it gets the direct-file-edit treatment instead (see
# App Title Override / title_sync.py).
DEFAULT_APP_TITLE_OVERRIDES = [
	{"app_name": "frappe", "new_title": "TijaratOS"},
	{"app_name": "erpnext", "new_title": "Tijarat"},
	{"app_name": "hrms", "new_title": "TijaratOS HR"},
]

# The top-right user-avatar dropdown - hidden down to a single item,
# "View Website" relabeled to "Switch to Portal". "About" and "Frappe
# Support" are a different menu (the "?" help icon) but hidden the same
# way, by exact visible text.
DEFAULT_MENU_HIDES = [
	"My Settings",
	"Toggle Theme",
	"Toggle Full Width",
	"Session Defaults",
	"Reload",
	"Log out",
	"About",
	"Frappe Support",
]
DEFAULT_MENU_RELABEL = {"match_label": "View Website", "new_label": "Switch to Portal"}

DEFAULT_CHART_COLORS = ["#4f46e5", "#0ea5e9", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"]


def after_install():
	seed_label_overrides()
	seed_menu_overrides()
	seed_chart_colors()
	seed_app_title_overrides()
	frappe.db.commit()

	from branding.branding.navbar_branding import apply_navbar_branding

	apply_navbar_branding()


def seed_label_overrides():
	"""Normal, editable/deletable starter rows - not enforced, just a
	sensible starting point so there's something to see and adjust rather
	than a blank list."""
	for row in DEFAULT_LABEL_OVERRIDES:
		if not frappe.db.exists("Label Override", {"match_text": row["match_text"]}):
			frappe.get_doc({"doctype": "Label Override", **row}).insert(ignore_permissions=True)


def seed_menu_overrides():
	existing = set(frappe.get_all("Menu Override", pluck="match_label"))

	for label in DEFAULT_MENU_HIDES:
		if label not in existing:
			frappe.get_doc(
				{"doctype": "Menu Override", "match_label": label, "hide_item": 1}
			).insert(ignore_permissions=True)

	if DEFAULT_MENU_RELABEL["match_label"] not in existing:
		frappe.get_doc({"doctype": "Menu Override", **DEFAULT_MENU_RELABEL}).insert(ignore_permissions=True)


def seed_chart_colors():
	settings = frappe.get_single("Theme Settings")
	if settings.chart_colors:
		return
	for color in DEFAULT_CHART_COLORS:
		settings.append("chart_colors", {"color": color})
	settings.save(ignore_permissions=True)


def seed_app_title_overrides():
	"""Each insert() below triggers App Title Override's own on_update
	hook, which rewrites that app's hooks.py immediately - so this both
	creates the record and applies it in one step, same as a user saving
	one by hand."""
	for row in DEFAULT_APP_TITLE_OVERRIDES:
		if not frappe.db.exists("App Title Override", {"app_name": row["app_name"]}):
			frappe.get_doc({"doctype": "App Title Override", **row}).insert(ignore_permissions=True)
