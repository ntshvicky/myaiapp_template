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

  // ─── URL status indicator ───
  const setUrlStatus = (msg, ok) => {
    if (!urlStatus) return;
    urlStatus.textContent = msg;
    urlStatus.style.color = ok ? "#4ade80" : "#f87171";
  };

  // Show ready state if URL already saved in session
  if (currentUrl) setUrlStatus("✓ Ready", true);

  // ─── Load URL (saves to session, no message sent) ───
  const loadUrl = () => {
    const url = urlInput?.value.trim();
    if (!url) { setUrlStatus("Enter a URL first", false); return; }

    if (loadBtn) { loadBtn.disabled = true; loadBtn.innerHTML = `<i class="fa fa-circle-notch fa-spin"></i>`; }
    setUrlStatus("", true);

    fetch(window.location.pathname, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded", "X-CSRFToken": CSRF_TOKEN },
      body: new URLSearchParams({ session_id: SESSION_ID, action: "set_url", url }),
    })
      .then(r => r.json())
      .then(d => {
        currentUrl = d.url || url;
        setUrlStatus("✓ Ready — ask your question below", true);
        if (loadBtn) { loadBtn.disabled = false; loadBtn.innerHTML = `<i class="fa fa-check"></i> Loaded`; }
        input?.focus();
        setTimeout(() => { if (loadBtn) loadBtn.innerHTML = `<i class="fa fa-arrow-right"></i> Load`; }, 2000);
      })
      .catch(() => {
        if (loadBtn) { loadBtn.disabled = false; loadBtn.innerHTML = `<i class="fa fa-arrow-right"></i> Load`; }
        setUrlStatus("Could not save URL", false);
      });
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
      setUrlStatus("Paste a URL and click Load first", false);
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
      .then(r => r.json())
      .then(d => {
        typing.remove();
        if (d.current_url) { currentUrl = d.current_url; setUrlStatus("✓ Ready", true); }
        const reply = d.bot_response || d.error || "No response.";
        addBubble(renderMd(reply), "incoming");
      })
      .catch(() => {
        typing.remove();
        addBubble("<p style='color:#f87171'>Connection error. Try again.</p>", "incoming");
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
        setUrlStatus("", true);
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
