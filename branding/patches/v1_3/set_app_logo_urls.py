import frappe

from branding.branding.install import DEFAULT_APP_TITLE_OVERRIDES


def execute():
	"""App Title Override rows created by the earlier seed patch predate
	the new_logo_url field - back-fills it onto those existing rows
	(inserting a fresh one for any app not already present) and saves,
	which triggers each row's own on_update and rewrites app_logo_url in
	that app's hooks.py immediately."""
	if not frappe.db.exists("DocType", "App Title Override"):
		return

	for row in DEFAULT_APP_TITLE_OVERRIDES:
		existing_name = frappe.db.exists("App Title Override", {"app_name": row["app_name"]})
		if existing_name:
			doc = frappe.get_doc("App Title Override", existing_name)
			if doc.get("new_logo_url") == row["new_logo_url"]:
				continue
			doc.new_logo_url = row["new_logo_url"]
			doc.save(ignore_permissions=True)
		else:
			frappe.get_doc({"doctype": "App Title Override", **row}).insert(ignore_permissions=True)

	frappe.db.commit()
