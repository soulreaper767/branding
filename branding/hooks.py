app_name = "branding"
app_title = "Branding"
app_publisher = "Sibyl Technologies"
app_description = "No-code labels, menus, and theme colors - independent of any specific ERPNext redesign."
app_email = "hello@tijaratapp.com"
app_license = "MIT"

# Included on every Desk page load.
app_include_css = "/assets/branding/css/branding.css"
app_include_js = "/assets/branding/js/branding.js"

# Included on every website/portal page load - a separate hook from
# app_include_*, which never reaches website pages at all. Scoped by CSS
# selector / element id rather than a JS guard, so it's inert on pages
# that don't have the elements it targets (e.g. the webshop-specific
# rules only match elements that exist on webshop's own pages).
web_include_css = "/assets/branding/css/webshop.css"
web_include_js = "/assets/branding/js/webshop.js"

# Injects Theme Settings + active Menu Overrides into frappe.boot.branding
# so the theme is available client-side immediately on first paint, with
# no extra API call.
boot_session = "branding.branding.boot.boot_session"

# Seeds starter Label Override, Menu Override, and App Title Override
# rows on a fresh install.
after_install = "branding.branding.install.after_install"

# App Title Override edits app_title directly in another app's own
# hooks.py, on disk - a `bench update` resets that file back to
# upstream's own title, so this re-applies every enabled row after every
# `bench migrate` (which normally follows an update anyway) with no
# separate manual step required. apply_navbar_branding (logo + help/user
# menu links, both native Website Settings/Navbar Settings records) is
# idempotent and cheap, so it rides along on the same hook in case a
# Frappe upgrade reseeds a new standard Navbar Item pointing at frappe.io.
after_migrate = [
	"branding.branding.title_sync.apply_all_app_titles",
	"branding.branding.navbar_branding.apply_navbar_branding",
]
