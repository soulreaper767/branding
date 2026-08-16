# Branding

No-code labels, menus, and theme colors for a Frappe/ERPNext site - independent of any specific ERPNext redesign.

## What it does

- **Label Override** - generic find/replace text rules (e.g. "ERPNext" → "Tijarat"), applied live via Translation records.
- **Menu Override** - hide or relabel any menu/sidebar/dropdown item by matching its visible text.
- **Theme Settings** - core colors, font, corner radius, and a chart color palette, applied to both the Desk and the webshop storefront.

Every rule is individually enable/disable-able. Manage everything from the **Branding** workspace.

## Installation

```bash
bench get-app https://github.com/soulreaper767/branding.git
bench --site your-site install-app branding
```
