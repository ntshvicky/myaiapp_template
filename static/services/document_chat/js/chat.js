document.addEventListener("DOMContentLoaded", () => {
  const chatC   = document.getElementById("chat-container");
  const input   = document.getElementById("chat-input");
  const sendBtn = document.getElementById("send-btn");
  const delBtn  = document.getElementById("delete-btn");

  if (!chatC) return;

  const renderMd = (text) => {
    if (!window.marked || !window.DOMPurify) return `<p>${text.replace(/\n/g, "<br>")}</p>`;
    marked.setOptions({ breaks: true, gfm: true });
    return DOMPurify.sanitize(marked.parse(text || ""));
  };

  const scroll = () => { chatC.scrollTop = chatC.scrollHeight; };

  const addBubble = (content, type, isTyping) => {
    const div = document.createElement("div");
    div.className = `chat ${type}${isTyping ? " typing-message" : ""}`;
    if (type === "incoming") {
      div.innerHTML = `
        <div class="chat-avatar"><i class="fa fa-file-text"></i></div>
        <div class="chat-content"><div class="chat-details ai-markdown">${content}</div></div>`;
      if (!isTyping && window.hljs) {
        div.querySelectorAll("pre code").forEach(b => hljs.highlightElement(b));
      }
    } else {
      div.innerHTML = `<div class="chat-content"><div class="chat-details"><p>${content.replace(/</g,"&lt;")}</p></div></div>`;
    }
    const welcome = chatC.querySelector(".default-text");
    if (welcome) welcome.remove();
    chatC.appendChild(div);
    scroll();
    return div;
  };

  // Apply markdown to existing bot messages on page load
  chatC.querySelectorAll(".ai-markdown").forEach(node => {
    const raw = node.textContent;
    node.innerHTML = renderMd(raw);
    if (window.hljs) node.querySelectorAll("pre code").forEach(b => hljs.highlightElement(b));
  });

  const send = () => {
    const txt = input.value.trim();
    if (!txt || !SESSION_ID) return;
    input.value = "";
    addBubble(txt, "outgoing");
    const typing = addBubble(
      `<div class="typing-dots"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>`,
      "incoming", true
    );

    fetch(AJAX_URL, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded", "X-CSRFToken": CSRF_TOKEN },
      body: new URLSearchParams({ session_id: SESSION_ID, message: txt }),
    })
      .then(r => r.json())
      .then(d => {
        typing.remove();
        addBubble(renderMd(d.bot_response || d.error || "No response."), "incoming");
      })
      .catch(() => {
        typing.remove();
        addBubble("<p style='color:#f87171'>Connection error. Try again.</p>", "incoming");
      });
  };

  if (sendBtn) sendBtn.addEventListener("click", send);
  if (input) input.addEventListener("keydown", e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } });

  if (delBtn) {
    delBtn.addEventListener("click", () => {
      if (!SESSION_ID || !confirm("Clear document chat history?")) return;
      fetch(AJAX_URL, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded", "X-CSRFToken": CSRF_TOKEN },
        body: new URLSearchParams({ session_id: SESSION_ID, action: "clear_history" }),
      }).then(() => {
        chatC.innerHTML = `
          <div class="default-text">
            <div class="welcome-icon"><i class="fa fa-file-text"></i></div>
            <h2>History cleared</h2><p>Ask a new question about this document.</p>
          </div>`;
      });
    });
  }

  scroll();
});
