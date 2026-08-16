import frappe


def execute():
	if not frappe.db.exists("DocType", "Theme Settings"):
		return

	from branding.branding.navbar_branding import apply_navbar_branding

	apply_navbar_branding()
