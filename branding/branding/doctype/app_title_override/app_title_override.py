import frappe
from frappe.model.document import Document

from branding.branding.title_sync import apply_one_app


class AppTitleOverride(Document):
	def on_update(self):
		if self.enabled and self.app_name and self.new_title:
			status = apply_one_app(self.app_name, self.new_title, self.get("new_logo_url"))
			frappe.db.set_value(self.doctype, self.name, "last_synced_status", status, update_modified=False)
			frappe.clear_cache()
