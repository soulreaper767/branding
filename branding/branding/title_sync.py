import os
import re

import frappe

# Anchored to the start of a line and matches only a plain string literal
# assigned to app_title / app_logo_url - the exact, single-purpose
# targets. Deliberately does NOT match app_name (a completely different
# hooks.py line/variable, never touched by this app) or anything inside a
# docstring/comment that happens to mention the same words.
TITLE_LINE = re.compile(r'^app_title\s*=\s*(?:"[^"]*"|\'[^\']*\')', re.MULTILINE)
LOGO_LINE = re.compile(r'^app_logo_url\s*=\s*(?:"[^"]*"|\'[^\']*\')', re.MULTILINE)


def apply_all_app_titles():
	"""Re-applies every enabled App Title Override row (both app_title
	and, where set, app_logo_url) - run automatically after every `bench
	migrate` (see hooks.py's after_migrate), so a `bench update` that
	resets an app's hooks.py back to upstream's own values gets silently
	fixed again on the very next migrate, with no extra manual step
	required."""
	if not frappe.db.exists("DocType", "App Title Override"):
		return

	for row in frappe.get_all(
		"App Title Override",
		filters={"enabled": 1},
		fields=["name", "app_name", "new_title", "new_logo_url"],
	):
		status = apply_one_app(row.app_name, row.new_title, row.get("new_logo_url"))
		frappe.db.set_value("App Title Override", row.name, "last_synced_status", status, update_modified=False)

	frappe.clear_cache()
	frappe.db.commit()


def apply_one_app(app_name, new_title, new_logo_url=None):
	"""Rewrites app_title = "..." (and, if given, app_logo_url = "...")
	in <app_name>'s own hooks.py. Returns a short human-readable status
	string covering both, stored back onto the row so a failure (app not
	installed, hooks.py missing, line not found in whatever form this
	Frappe version's hooks.py takes) is visible on the record itself
	rather than only in the error log."""
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

	results = []

	if new_title:
		if TITLE_LINE.search(content):
			content, count = TITLE_LINE.subn(f'app_title = "{new_title}"', content, count=1)
			results.append("title updated" if count else "title unchanged")
		else:
			results.append("no app_title line found")

	if new_logo_url:
		if LOGO_LINE.search(content):
			content, count = LOGO_LINE.subn(f'app_logo_url = "{new_logo_url}"', content, count=1)
			results.append("logo updated" if count else "logo unchanged")
		else:
			results.append("no app_logo_url line found")

	try:
		with open(hooks_path, "w", encoding="utf-8") as f:
			f.write(content)
	except Exception as e:
		return f"Could not write {hooks_path}: {e}"

	return ", ".join(results) + " - restart the web workers to see it take effect"


# Kept as a thin alias - App Title Override's controller and older
# callers refer to this name specifically.
def apply_one_app_title(app_name, new_title):
	return apply_one_app(app_name, new_title)


@frappe.whitelist()
def sync_now():
	"""Manual trigger, callable from the App Title Override list view -
	same effect as saving a row or waiting for the next bench migrate,
	just on demand."""
	frappe.only_for("System Manager")
	apply_all_app_titles()
	return "done"
