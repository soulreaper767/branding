// branding: applies Theme Settings + Menu Overrides across the Desk.
// Two-layer approach, same proven pattern as the app this replaces:
//   1. CSS custom properties (--brand-*), consumed by branding.css, plus
//      a remap onto Frappe's own theme variables so native components
//      (buttons, cards, the Kanban board) pick up the palette too.
//   2. Menu label-text overrides are DOM-level and re-applied on every
//      mutation, since the Desk's own chrome re-renders dynamically and a
//      one-time pass would get silently wiped out on the next render.

(function () {
	function setVar(root, name, value) {
		if (value) root.style.setProperty(name, value);
	}

	const FONT_STACKS = {
		Inter: "'Inter', sans-serif",
		"Noto Sans": "'Noto Sans', sans-serif",
		Roboto: "'Roboto', sans-serif",
		"Open Sans": "'Open Sans', sans-serif",
		"System UI": "system-ui, sans-serif",
	};

	const RADIUS_MAP = {
		"Sharp (0px)": "0px",
		"Subtle (4px)": "4px",
		"Rounded (8px)": "8px",
		"Pill (999px)": "999px",
	};

	function applyIconOverride(el, newIcon) {
		if (!newIcon) return;
		const iconEl = el.querySelector(".icon, .es-icon, svg, .sidebar-item-icon, img");
		if (!iconEl) return;

		if (/[./]/.test(newIcon)) {
			const img = document.createElement("img");
			img.src = newIcon;
			img.className = iconEl.className || "icon";
			img.style.width = "1em";
			img.style.height = "1em";
			img.style.objectFit = "contain";
			iconEl.replaceWith(img);
			return;
		}

		const use = iconEl.tagName === "svg" ? iconEl.querySelector("use") : el.querySelector("svg use");
		if (use) {
			use.setAttribute("href", `#icon-${newIcon}`);
			use.setAttribute("xlink:href", `#icon-${newIcon}`);
		}
		Array.prototype.slice.call(iconEl.classList).forEach((c) => {
			if (c.indexOf("lucide-") === 0) iconEl.classList.remove(c);
		});
		iconEl.classList.add(`lucide-${newIcon}`);
	}

	function applyMenuOverrides() {
		const overrides = (window.branding && window.branding._menuOverrides) || [];
		if (!overrides.length) return;

		const candidates = document.querySelectorAll(
			"a, .sidebar-item, .standard-sidebar-item, .dropdown-item, .workspace-sidebar-item, [data-label]"
		);

		candidates.forEach((el) => {
			const text = (el.textContent || "").trim();
			if (!text) return;

			const override = overrides.find((o) => o.match_label && o.match_label.trim() === text);
			if (!override) return;

			if (override.hide_item) {
				el.style.display = "none";
				return;
			}
			if (override.new_label) {
				const textNode = Array.prototype.slice
					.call(el.childNodes)
					.find((n) => n.nodeType === Node.TEXT_NODE && n.textContent.trim());
				if (textNode) textNode.textContent = override.new_label;
			}
			if (override.new_link && el.tagName === "A") {
				el.setAttribute("href", override.new_link);
				if (override.open_in_new_tab) el.setAttribute("target", "_blank");
			}
			if (override.new_icon) applyIconOverride(el, override.new_icon);
		});
	}

	let debounceTimer = null;
	function watchForRerenders() {
		const observer = new MutationObserver(() => {
			clearTimeout(debounceTimer);
			debounceTimer = setTimeout(applyMenuOverrides, 150);
		});
		observer.observe(document.body, { childList: true, subtree: true });
	}

	function applyTheme(settings) {
		const root = document.documentElement;

		if (!settings || Number(settings.enabled) === 0) {
			root.removeAttribute("data-branding-theme");
			window.branding._menuOverrides = [];
			return;
		}

		setVar(root, "--brand-primary", settings.primary_color);
		setVar(root, "--brand-bg", settings.background_color);
		setVar(root, "--brand-text", settings.text_color);
		setVar(root, "--brand-border", settings.border_color);
		setVar(root, "--brand-muted", settings.muted_text_color);
		setVar(root, "--brand-success", settings.success_color);
		setVar(root, "--brand-warning", settings.warning_color);
		setVar(root, "--brand-danger", settings.danger_color);

		if (settings.font_family && FONT_STACKS[settings.font_family]) {
			setVar(root, "--brand-font", FONT_STACKS[settings.font_family]);
		}
		if (settings.border_radius && RADIUS_MAP[settings.border_radius]) {
			setVar(root, "--brand-radius", RADIUS_MAP[settings.border_radius]);
		}

		(settings.chart_colors || []).forEach((color, i) => {
			setVar(root, `--brand-chart-${i + 1}`, color);
		});

		root.setAttribute("data-branding-theme", "on");

		window.branding._menuOverrides = settings.menu_overrides || [];
		applyMenuOverrides();
	}

	window.branding = window.branding || {};
	window.branding.applyTheme = applyTheme;

	function boot() {
		const settings = (window.frappe && frappe.boot && frappe.boot.branding) || null;
		applyTheme(settings);
		watchForRerenders();
	}

	if (window.frappe && frappe.ready) {
		frappe.ready(boot);
	} else {
		document.addEventListener("DOMContentLoaded", boot);
	}
})();
