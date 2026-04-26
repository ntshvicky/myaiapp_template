// Theme management
(function () {
  const THEME_KEY = "myaiapp_theme";

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem(THEME_KEY, theme);
    document.querySelectorAll(".swatch").forEach((s) => {
      s.classList.toggle("active", s.dataset.theme === theme);
    });
  }

  // Set active swatch on load
  const saved = localStorage.getItem(THEME_KEY) || "dark";
  document.querySelectorAll(".swatch").forEach((btn) => {
    if (btn.dataset.theme === saved) btn.classList.add("active");
    btn.addEventListener("click", () => applyTheme(btn.dataset.theme));
  });

  // Highlight active nav link
  const path = window.location.pathname;
  document.querySelectorAll(".nav-links a").forEach((a) => {
    if (a.getAttribute("href") && path.startsWith(a.getAttribute("href")) && a.getAttribute("href") !== "/") {
      a.classList.add("active-nav");
    }
  });
})();
