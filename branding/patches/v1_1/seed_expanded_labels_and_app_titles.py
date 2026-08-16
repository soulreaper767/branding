import frappe

from branding.branding.install import seed_app_title_overrides, seed_label_overrides


def execute():
	"""Applies the App Title Override doctype (new) and the expanded
	Label Override default list to a site that installed this app before
	both existed."""
	try:
		if frappe.db.exists("DocType", "Label Override"):
			seed_label_overrides()

		if frappe.db.exists("DocType", "App Title Override"):
			seed_app_title_overrides()

		frappe.db.commit()
	except Exception:
		frappe.log_error(title="branding: seed_expanded_labels_and_app_titles patch failed")
