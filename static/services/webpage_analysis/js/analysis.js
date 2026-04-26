document.addEventListener("DOMContentLoaded", () => {
  const chatC   = document.getElementById("chat-container");
  const input   = document.getElementById("chat-input");
  const sendBtn = document.getElementById("send-btn");
  const delBtn  = document.getElementById("delete-btn");

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
        <div class="chat-avatar"><i class="fa fa-globe"></i></div>
        <div class="chat-content"><div class="chat-details ai-markdown">${content}</div></div>`;
      if (!isTyping && window.hljs) {
        div.querySelectorAll("pre code").forEach(b => hljs.highlightElement(b));
      }
    } else {
      div.innerHTML = `<div class="chat-content"><div class="chat-details"><p>${content.replace(/</g,"&lt;")}</p></div></div>`;
    }
    const welcome = chatC.querySelector("#default-welcome, .default-text");
    if (welcome) welcome.remove();
    chatC.appendChild(div);
    scroll();
    return div;
  };

  const send = () => {
    const text = input.value.trim();
    if (!text) return;
    input.value = "";
    addBubble(text, "outgoing");
    const typing = addBubble(
      `<div class="typing-dots"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>`,
      "incoming", true
    );

    fetch(window.location.pathname, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded", "X-CSRFToken": CSRF_TOKEN },
      body: new URLSearchParams({ session_id: SESSION_ID, message: text }),
    })
      .then(r => r.json())
      .then(d => {
        typing.remove();
        const reply = d.bot_response || d.error || "No response.";
        addBubble(renderMd(reply), "incoming");
      })
      .catch(() => {
        typing.remove();
        addBubble("<p style='color:#f87171'>Connection error. Try again.</p>", "incoming");
      });
  };

  sendBtn.addEventListener("click", send);
  input.addEventListener("keydown", e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } });

  delBtn.addEventListener("click", () => {
    if (!confirm("Clear analysis history?")) return;
    fetch(window.location.pathname, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded", "X-CSRFToken": CSRF_TOKEN },
      body: new URLSearchParams({ session_id: SESSION_ID, action: "clear_history" }),
    }).then(() => {
      chatC.innerHTML = `
        <div class="default-text" id="default-welcome">
          <div class="welcome-icon"><i class="fa fa-globe"></i></div>
          <h2>Website Analyzer</h2>
          <p>Enter a URL followed by <code>::</code> and your question.</p>
        </div>`;
    });
  });

  scroll();
});
