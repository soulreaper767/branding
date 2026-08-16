import frappe

DEFAULT_LABEL_OVERRIDES = [
	{"match_text": "ERPNext", "replacement_text": "Tijarat"},
	{"match_text": "Frappe", "replacement_text": "TijaratOS"},
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
	frappe.db.commit()


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
