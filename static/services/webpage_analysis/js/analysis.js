document.addEventListener("DOMContentLoaded", () => {
  const chatC     = document.getElementById("chat-container");
  const input     = document.getElementById("chat-input");
  const sendBtn   = document.getElementById("send-btn");
  const delBtn    = document.getElementById("delete-btn");
  const urlInput  = document.getElementById("url-input");
  const loadBtn   = document.getElementById("load-url-btn");
  const urlStatus = document.getElementById("url-status");

  let currentUrl = (urlInput?.value || "").trim();

  // ─── Markdown helper ───
  const renderMd = (text) => {
    if (!window.marked || !window.DOMPurify) return `<p>${text.replace(/\n/g, "<br>")}</p>`;
    marked.setOptions({ breaks: true, gfm: true });
    return DOMPurify.sanitize(marked.parse(text || ""));
  };

  const scroll = () => { chatC.scrollTop = chatC.scrollHeight; };

  // ─── Add a chat bubble ───
  const addBubble = (content, type, isTyping) => {
    const div = document.createElement("div");
    div.className = `chat ${type}${isTyping ? " typing-message" : ""}`;
    if (type === "incoming") {
      div.innerHTML = `
        <div class="chat-avatar"><i class="fa fa-globe"></i></div>
        <div class="chat-content"><div class="chat-details ai-markdown">${content}</div></div>`;
      if (!isTyping && window.hljs) {
        div.querySelectorAll("pre code").forEach(b => hljs.highlightElement(b));
      }
    } else {
      div.innerHTML = `<div class="chat-content"><div class="chat-details"><p>${content.replace(/</g, "&lt;")}</p></div></div>`;
    }
    const welcome = chatC.querySelector("#default-welcome, .default-text");
    if (welcome) welcome.remove();
    chatC.appendChild(div);
    scroll();
    return div;
  };

  const urlBar = urlInput?.closest(".url-bar-row");

  // ─── Visual state helpers ───
  const setLoaded = () => {
    urlBar?.classList.add("loaded");
    urlBar?.classList.remove("url-error");
    if (urlStatus) { urlStatus.textContent = "✓ Page loaded — ask your question below"; urlStatus.style.color = "#4ade80"; }
    if (loadBtn)   { loadBtn.innerHTML = `<i class="fa fa-check"></i> Loaded`; loadBtn.style.background = "#16a34a"; }
  };
  const setLoading = () => {
    urlBar?.classList.remove("loaded", "url-error");
    if (urlStatus) { urlStatus.textContent = "Fetching page…"; urlStatus.style.color = "var(--text-secondary)"; }
    if (loadBtn)   { loadBtn.disabled = true; loadBtn.innerHTML = `<i class="fa fa-circle-notch fa-spin"></i> Loading…`; loadBtn.style.background = ""; }
  };
  const setError = (msg) => {
    urlBar?.classList.add("url-error");
    urlBar?.classList.remove("loaded");
    if (urlStatus) { urlStatus.textContent = `✗ ${msg}`; urlStatus.style.color = "#f87171"; }
    if (loadBtn)   { loadBtn.disabled = false; loadBtn.innerHTML = `<i class="fa fa-arrow-right"></i> Analyze`; loadBtn.style.background = ""; }
  };
  const resetBtn = () => {
    if (loadBtn) { loadBtn.disabled = false; loadBtn.innerHTML = `<i class="fa fa-arrow-right"></i> Analyze`; loadBtn.style.background = ""; }
  };

  // Reset loaded state when user edits the URL
  urlInput?.addEventListener("input", () => {
    urlBar?.classList.remove("loaded", "url-error");
    if (urlStatus) { urlStatus.textContent = ""; }
    resetBtn();
  });

  // Show ready state if URL already saved in session (page reload)
  if (currentUrl) setLoaded();

  // ─── Load URL (saves to session, no message sent) ───
  const loadUrl = () => {
    const url = urlInput?.value.trim();
    if (!url) { setError("Enter a URL first"); urlInput?.focus(); return; }

    setLoading();

    fetch(window.location.pathname, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded", "X-CSRFToken": CSRF_TOKEN },
      body: new URLSearchParams({ session_id: SESSION_ID, action: "set_url", url }),
    })
      .then(r => {
        const ct = r.headers.get("content-type") || "";
        return ct.includes("application/json") ? r.json() : Promise.resolve({ url });
      })
      .then(d => {
        currentUrl = d.url || url;
        setLoaded();
        input?.focus();
      })
      .catch(() => setError("Could not save URL — check connection"));
  };

  if (loadBtn) loadBtn.addEventListener("click", loadUrl);
  urlInput?.addEventListener("keydown", e => { if (e.key === "Enter") { e.preventDefault(); loadUrl(); } });

  // ─── Send a question ───
  const send = () => {
    const text = (input?.value || "").trim();
    if (!text) return;

    // Guard: must have a URL loaded
    const liveUrl = urlInput?.value.trim();
    if (!currentUrl && !liveUrl) {
      setError("Paste a URL and click Analyze first");
      urlInput?.focus();
      return;
    }

    input.value = "";
    addBubble(text, "outgoing");
    const typing = addBubble(
      `<div class="typing-dots"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>`,
      "incoming", true
    );

    const body = new URLSearchParams({ session_id: SESSION_ID, message: text });
    // If user typed a URL but didn't click Load, send it inline so the backend saves it
    if (liveUrl && liveUrl !== currentUrl) body.set("url", liveUrl);

    fetch(window.location.pathname, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded", "X-CSRFToken": CSRF_TOKEN },
      body,
    })
      .then(r => {
        const ct = r.headers.get("content-type") || "";
        if (!ct.includes("application/json")) {
          // Server returned HTML (error page / redirect) — reload to show saved response
          typing.remove();
          addBubble(
            `<p style='color:#fbbf24'><i class='fa fa-triangle-exclamation'></i> Response received — <a href='javascript:location.reload()' style='color:var(--accent)'>click to refresh</a> and see the result.</p>`,
            "incoming"
          );
          return null;
        }
        return r.json();
      })
      .then(d => {
        if (!d) return;
        typing.remove();
        if (d.current_url) { currentUrl = d.current_url; setLoaded(); }
        const reply = d.bot_response || d.error || "No response.";
        addBubble(renderMd(reply), "incoming");
      })
      .catch(() => {
        typing.remove();
        addBubble(
          `<p style='color:#fbbf24'><i class='fa fa-triangle-exclamation'></i> Response received — <a href='javascript:location.reload()' style='color:var(--accent)'>click to refresh</a> and see the result.</p>`,
          "incoming"
        );
      });
  };

  if (sendBtn) sendBtn.addEventListener("click", send);
  input?.addEventListener("keydown", e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } });

  // ─── Clear history ───
  if (delBtn) {
    delBtn.addEventListener("click", () => {
      if (!confirm("Clear history and reset URL?")) return;
      fetch(window.location.pathname, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded", "X-CSRFToken": CSRF_TOKEN },
        body: new URLSearchParams({ session_id: SESSION_ID, action: "clear_history" }),
      }).then(() => {
        currentUrl = "";
        if (urlInput) urlInput.value = "";
        urlBar?.classList.remove("loaded", "url-error");
        if (urlStatus) urlStatus.textContent = "";
        resetBtn();
        chatC.innerHTML = `
          <div class="default-text" id="default-welcome">
            <div class="welcome-icon"><i class="fa fa-globe"></i></div>
            <h2>Website Analyzer</h2>
            <p>Paste any URL above, click <strong>Load</strong>, then ask your questions below.</p>
          </div>`;
      });
    });
  }

  scroll();
});
