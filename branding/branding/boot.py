import frappe


def boot_session(bootinfo):
	"""Injects Theme Settings + the active Menu Override rows into
	frappe.boot so branding.js can apply everything on first paint, with
	no extra API round trip.

	Runs on EVERY page load for EVERY user, including the initial desk
	boot - an unhandled exception here doesn't just skip the theme, it
	takes down the whole site (frappe.SessionBootFailed). That can happen
	from something as ordinary as a `git pull` landing before `bench
	migrate` runs, so a newly-added field briefly doesn't exist on Theme
	Settings yet. getattr(..., None) on every field means a missing
	column degrades to "no value" instead of crashing boot, and the whole
	block is additionally wrapped in try/except as a last resort."""
	try:
		settings = frappe.get_cached_doc("Theme Settings")
		if not settings.get("enabled"):
			bootinfo.branding = {"enabled": 0, "menu_overrides": []}
			return

		def field(name):
			return getattr(settings, name, None)

		bootinfo.branding = {
			"enabled": 1,
			"application_name": field("application_name"),
			"primary_color": field("primary_color"),
			"background_color": field("background_color"),
			"text_color": field("text_color"),
			"border_color": field("border_color"),
			"muted_text_color": field("muted_text_color"),
			"success_color": field("success_color"),
			"warning_color": field("warning_color"),
			"danger_color": field("danger_color"),
			"font_family": field("font_family"),
			"border_radius": field("border_radius"),
			"chart_colors": [row.color for row in (field("chart_colors") or []) if row.color],
			"menu_overrides": frappe.get_all(
				"Menu Override",
				filters={"enabled": 1},
				fields=["match_label", "hide_item", "new_label", "new_link", "new_icon", "open_in_new_tab"],
			),
		}
	except Exception:
		frappe.log_error(title="branding: boot_session failed")
		bootinfo.branding = {"enabled": 0, "menu_overrides": []}
