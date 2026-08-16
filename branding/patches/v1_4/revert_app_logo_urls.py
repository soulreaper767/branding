import frappe

from branding.branding.title_sync import apply_one_app

# Original values, exactly as verified against frappe/erpnext/hrms's own
# hooks.py before this app ever touched them - restoring these undoes the
# app_logo_url edit completely, leaving app_title (which is wanted) alone.
ORIGINAL_LOGO_URLS = {
	"frappe": "/assets/frappe/images/frappe-framework-logo.svg",
	"erpnext": "/assets/erpnext/images/erpnext-logo.svg",
	"hrms": "/assets/hrms/images/frappe-hr-logo.svg",
}


def execute():
	try:
		for app_name, original_logo_url in ORIGINAL_LOGO_URLS.items():
			apply_one_app(app_name, new_title=None, new_logo_url=original_logo_url)

		if frappe.db.exists("DocType", "App Title Override"):
			for name in frappe.get_all("App Title Override", pluck="name"):
				frappe.db.set_value("App Title Override", name, "new_logo_url", "")
			# Re-apply title only for every row now that logo is out of the
			# picture, so a row that failed earlier (e.g. hrms) gets a fresh
			# attempt and its Last Sync Result reflects what actually
			# happened this time.
			for row in frappe.get_all(
				"App Title Override", filters={"enabled": 1}, fields=["name", "app_name", "new_title"]
			):
				status = apply_one_app(row.app_name, row.new_title)
				frappe.db.set_value(
					"App Title Override", row.name, "last_synced_status", status, update_modified=False
				)

		frappe.clear_cache()
		frappe.db.commit()
	except Exception:
		frappe.log_error(title="branding: revert_app_logo_urls patch failed")
