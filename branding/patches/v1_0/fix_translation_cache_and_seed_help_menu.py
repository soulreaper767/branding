import frappe

from branding.branding.install import seed_menu_overrides


def execute():
	"""Two fixes for a site that installed this app before both were
	caught: (1) Label Override was clearing frappe's generic cache
	instead of the dedicated frappe.translate.clear_cache(), which is
	the one that actually busts the year-long browser cache Frappe
	serves translations with - existing rows' Translation records were
	correct in the database the whole time, just invisible client-side.
	(2) "About" and "Frappe Support" (the "?" help menu) weren't in the
	original default Menu Override seed list, which only covered the
	user-avatar menu - adds them now the same way."""
	try:
		frappe.translate.clear_cache()
	except Exception:
		frappe.log_error(title="branding: fix_translation_cache_and_seed_help_menu - cache clear failed")

	try:
		if frappe.db.exists("DocType", "Menu Override"):
			seed_menu_overrides()
			frappe.db.commit()
	except Exception:
		frappe.log_error(title="branding: fix_translation_cache_and_seed_help_menu - seeding failed")
