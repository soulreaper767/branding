import frappe

DEFAULT_LOGO_URL = "/assets/branding/images/tijarat-logo.png"

# Any Navbar Item whose route contains one of these gets pointed at the
# configured website instead - these are native Frappe doctype records
# (Navbar Settings' help_dropdown/settings_dropdown, child doctype
# Navbar Item), not a file edit and not DOM text-matching, so this is
# stable across Frappe versions.
DOMAIN_MARKERS = ["frappe.io", "frappecloud.com", "erpnext.com", "github.com/frappe"]

LABEL_REPLACEMENTS = {
	"Frappe School": "TijaratOS School",
	"Frappe Forum": "TijaratOS Forum",
	"Frappe Support": "TijaratOS Support",
	"About Frappe": "About TijaratOS",
	"Frappe Cloud": "TijaratOS",
}


def apply_navbar_branding():
	"""Applies the logo + link rewrite from Theme Settings to Website
	Settings and Navbar Settings. Safe to call any time (idempotent) -
	wired to run after every bench migrate in case a Frappe upgrade
	reseeds a new standard Navbar Item pointing at frappe.io."""
	try:
		if not frappe.db.exists("DocType", "Theme Settings"):
			return
		settings = frappe.get_single("Theme Settings")
		logo_url = settings.get("app_logo") or DEFAULT_LOGO_URL
		website_url = settings.get("website_url") or "https://tijaratapp.com"

		_apply_logo(logo_url)
		_apply_dropdown_links(website_url)

		frappe.clear_cache()
		frappe.db.commit()
	except Exception:
		frappe.log_error(title="branding: apply_navbar_branding failed")


def _apply_logo(logo_url):
	website_settings = frappe.get_single("Website Settings")
	for field in ("app_logo", "banner_image", "splash_image", "footer_logo", "favicon"):
		if website_settings.meta.has_field(field):
			website_settings.set(field, logo_url)
	website_settings.save(ignore_permissions=True)

	if frappe.db.exists("DocType", "Navbar Settings"):
		navbar_settings = frappe.get_single("Navbar Settings")
		if navbar_settings.meta.has_field("app_logo"):
			navbar_settings.app_logo = logo_url
			navbar_settings.save(ignore_permissions=True)


def _apply_dropdown_links(website_url):
	if not frappe.db.exists("DocType", "Navbar Settings"):
		return

	navbar_settings = frappe.get_single("Navbar Settings")
	changed = False

	for table_field in ("help_dropdown", "settings_dropdown"):
		for row in navbar_settings.get(table_field) or []:
			route = row.get("route") or ""
			if any(marker in route for marker in DOMAIN_MARKERS):
				row.route = website_url
				changed = True

			label = row.get("item_label") or ""
			if label in LABEL_REPLACEMENTS:
				row.item_label = LABEL_REPLACEMENTS[label]
				changed = True

	if changed:
		navbar_settings.save(ignore_permissions=True)
