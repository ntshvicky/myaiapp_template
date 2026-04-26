document.addEventListener("DOMContentLoaded", () => {
  const genBtn      = document.getElementById("gen-btn");
  const promptInput = document.getElementById("prompt-input");
  const genStatus   = document.getElementById("gen-status");
  const newArea     = document.getElementById("new-image-area");

  if (!genBtn) return;

  genBtn.addEventListener("click", generate);
  promptInput?.addEventListener("keydown", e => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); generate(); }
  });

  function generate() {
    const prompt = promptInput?.value.trim();
    if (!prompt) { promptInput?.focus(); return; }

    genBtn.disabled = true;
    if (genStatus) genStatus.style.display = "block";

    fetch(window.location.pathname, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded", "X-CSRFToken": CSRF_TOKEN },
      body: new URLSearchParams({ session_id: SESSION_ID, prompt }),
    })
      .then(r => r.json())
      .then(d => {
        genBtn.disabled = false;
        if (genStatus) genStatus.style.display = "none";

        if (d.image_url) {
          // Show newly generated image at top
          if (newArea) {
            newArea.innerHTML = `
              <div style="background:var(--card-bg);border:1px solid var(--glass-border);border-radius:0.75rem;overflow:hidden">
                <img src="${escHtml(d.image_url)}" alt="${escHtml(prompt)}"
                     style="width:100%;max-height:520px;object-fit:contain;display:block;background:rgba(0,0,0,0.2)">
                <div style="padding:0.75rem 1rem;display:flex;align-items:center;justify-content:space-between;gap:0.75rem">
                  <p style="font-size:0.82rem;color:var(--text-secondary);margin:0;flex:1">${escHtml(prompt)}</p>
                  <a href="${escHtml(d.image_url)}" download style="font-size:0.8rem;color:var(--accent);text-decoration:none;border:1px solid var(--accent);padding:0.3rem 0.6rem;border-radius:0.3rem;white-space:nowrap">
                    <i class="fa fa-download"></i> Download
                  </a>
                </div>
              </div>`;
          }
          // Clear prompt for next
          if (promptInput) promptInput.value = "";
        } else {
          alert(d.error || "Image generation failed.");
        }
      })
      .catch(() => {
        genBtn.disabled = false;
        if (genStatus) genStatus.style.display = "none";
        alert("Connection error. Please try again.");
      });
  }

  function escHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;")
      .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }
});
