// ─── Theme management ───────────────────────────────────────────────────────
const THEME_KEY = "myaiapp_theme";

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem(THEME_KEY, theme);
  // Update active ring on all swatches
  document.querySelectorAll(".swatch").forEach((s) =>
    s.classList.toggle("active", s.dataset.theme === theme)
  );
}

// Apply saved theme immediately (anti-flash — also done inline in <head>)
const _savedTheme = localStorage.getItem(THEME_KEY) || "dark";
document.documentElement.setAttribute("data-theme", _savedTheme);

// Attach swatch click listeners — use event delegation on the container
// so it works even if called before full DOM parse.
function _initTheme() {
  // Mark active swatch
  document.querySelectorAll(".swatch").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.theme === _savedTheme);
  });

  // Delegate clicks on the swatches wrapper
  const swatchWrap = document.querySelector(".theme-swatches");
  if (swatchWrap) {
    swatchWrap.addEventListener("click", (e) => {
      const btn = e.target.closest(".swatch");
      if (btn && btn.dataset.theme) applyTheme(btn.dataset.theme);
    });
  } else {
    // Fallback: attach directly if wrapper not found (shouldn't happen)
    document.querySelectorAll(".swatch").forEach((btn) =>
      btn.addEventListener("click", () => applyTheme(btn.dataset.theme))
    );
  }
}

// Run after DOM is ready (works whether script is in <head> or <body>)
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", _initTheme);
} else {
  _initTheme();
}

// ─── Active nav link ─────────────────────────────────────────────────────────
function _initActiveNav() {
  const path = window.location.pathname;
  document.querySelectorAll(".nav-links a").forEach((a) => {
    const href = a.getAttribute("href");
    if (href && href !== "/" && path.startsWith(href)) {
      a.classList.add("active-nav");
    }
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", _initActiveNav);
} else {
  _initActiveNav();
}
