import os
import re

import frappe

# Anchored to the start of a line and matches only a plain string literal
# assigned to app_title - the exact, single-purpose target. Deliberately
# does NOT match app_name (a completely different hooks.py line/variable)
# or anything inside a docstring/comment that happens to mention the word
# "title".
TITLE_LINE = re.compile(r'^app_title\s*=\s*(?:"[^"]*"|\'[^\']*\')', re.MULTILINE)


def apply_all_app_titles():
	"""Re-applies every enabled App Title Override row - run automatically
	after every `bench migrate` (see hooks.py's after_migrate), so a
	`bench update` that resets an app's hooks.py back to upstream's own
	title gets silently fixed again on the very next migrate, with no
	extra manual step required."""
	if not frappe.db.exists("DocType", "App Title Override"):
		return

	for row in frappe.get_all(
		"App Title Override", filters={"enabled": 1}, fields=["name", "app_name", "new_title"]
	):
		status = apply_one_app_title(row.app_name, row.new_title)
		frappe.db.set_value("App Title Override", row.name, "last_synced_status", status, update_modified=False)

	frappe.clear_cache()
	frappe.db.commit()


def apply_one_app_title(app_name, new_title):
	"""Rewrites app_title = "..." in <app_name>'s own hooks.py to
	new_title. Returns a short human-readable status string, stored back
	onto the row so a failure (app not installed, hooks.py missing, line
	not found in whatever form this Frappe version's hooks.py takes) is
	visible on the record itself rather than only in the error log."""
	try:
		hooks_path = frappe.get_app_path(app_name, "hooks.py")
	except Exception:
		return f"Could not resolve path for app '{app_name}' - is it installed on this bench?"

	if not os.path.isfile(hooks_path):
		return f"{hooks_path} does not exist"

	try:
		with open(hooks_path, encoding="utf-8") as f:
			content = f.read()
	except Exception as e:
		return f"Could not read {hooks_path}: {e}"

	if not TITLE_LINE.search(content):
		return f"No 'app_title = ...' line found in {hooks_path} - nothing changed"

	new_content, count = TITLE_LINE.subn(f'app_title = "{new_title}"', content, count=1)
	if count == 0 or new_content == content:
		return "Already set to this title"

	try:
		with open(hooks_path, "w", encoding="utf-8") as f:
			f.write(new_content)
	except Exception as e:
		return f"Found the line but could not write {hooks_path}: {e}"

	return f"Updated - restart the web workers (or wait for the next deploy) to see it take effect"


@frappe.whitelist()
def sync_now():
	"""Manual trigger, callable from the App Title Override list view -
	same effect as saving a row or waiting for the next bench migrate,
	just on demand."""
	frappe.only_for("System Manager")
	apply_all_app_titles()
	return "done"
