import frappe
from frappe.model.document import Document


class LabelOverride(Document):
	"""Keeps a native Translation record in sync with this row so the
	replacement actually takes effect through Frappe's own __() layer -
	no separate "sync" step needed, it's live the moment a row is saved.

	Known limitation: renaming match_text on an existing row leaves the
	old Translation record behind (there's nothing to key off to find it -
	the doc's own before-save state isn't tracked here). Low-stakes and
	easy to fix by hand (delete the stale Translation) since this is a
	handful of admin-managed rows, not bulk data."""

	def on_update(self):
		if self.enabled and self.match_text:
			_upsert_translation(self.match_text, self.replacement_text)
		else:
			_remove_translation(self.match_text)
		frappe.clear_cache()

	def on_trash(self):
		_remove_translation(self.match_text)
		frappe.clear_cache()


def _upsert_translation(source_text, translated_text):
	languages = frappe.get_all("Language", filters={"enabled": 1}, pluck="name") or []
	if "en" not in languages:
		languages.append("en")

	for language in languages:
		existing = frappe.db.get_value(
			"Translation", {"source_text": source_text, "language": language}, "name"
		)
		if existing:
			frappe.db.set_value("Translation", existing, "translated_text", translated_text)
		else:
			frappe.get_doc(
				{
					"doctype": "Translation",
					"language": language,
					"source_text": source_text,
					"translated_text": translated_text,
				}
			).insert(ignore_permissions=True)


def _remove_translation(source_text):
	if not source_text:
		return
	for name in frappe.get_all("Translation", filters={"source_text": source_text}, pluck="name"):
		frappe.delete_doc("Translation", name, ignore_permissions=True, force=True)
