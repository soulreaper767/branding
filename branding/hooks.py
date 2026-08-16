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

# Seeds two starter Label Override rows (ERPNext -> Application Name,
# Frappe -> Application Name + "OS") and the default Menu Override rows
# (avatar menu reduced to "Switch to Portal") on a fresh install.
after_install = "branding.branding.install.after_install"
