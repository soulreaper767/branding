import frappe
from frappe.model.document import Document

from branding.branding.title_sync import apply_one_app_title


class AppTitleOverride(Document):
	def on_update(self):
		if self.enabled and self.app_name and self.new_title:
			status = apply_one_app_title(self.app_name, self.new_title)
			frappe.db.set_value(self.doctype, self.name, "last_synced_status", status, update_modified=False)
			frappe.clear_cache()
