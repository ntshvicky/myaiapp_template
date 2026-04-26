document.addEventListener("DOMContentLoaded", () => {
  let imageId = "";
  const sel           = document.getElementById("img-select");
  const chatC         = document.getElementById("image-chat-container");
  const input         = document.getElementById("chat-input");
  const sendBtn       = document.getElementById("send-btn");
  const clearBtn      = document.getElementById("delete-btn");
  const preview       = document.getElementById("image-preview");
  const previewEmpty  = document.getElementById("image-preview-empty");
  const previewMeta   = document.getElementById("image-preview-meta");
  const suggestionBar = document.getElementById("img-suggestions");

  // --- Markdown helper (reuse marked + DOMPurify from base) ---
  const renderMd = (text) => {
    if (!window.marked || !window.DOMPurify) return `<p>${text.replace(/\n/g, "<br>")}</p>`;
    marked.setOptions({ breaks: true, gfm: true });
    return DOMPurify.sanitize(marked.parse(text || ""));
  };

  // --- Update image preview ---
  const updatePreview = () => {
    const opt = sel.options[sel.selectedIndex];
    if (!opt || !opt.value) {
      imageId = "";
      preview.style.display = "none";
      preview.src = "";
      previewMeta.style.display = "none";
      previewEmpty.style.display = "";
      if (suggestionBar) suggestionBar.style.display = "none";
      return;
    }
    imageId = opt.value;
    const url  = opt.dataset.url  || "";
    const name = opt.dataset.name || "image";

    preview.src = url;
    preview.alt = name;
    preview.style.display = "block";
    previewEmpty.style.display = "none";
    previewMeta.style.display = "block";
    previewMeta.textContent = name.split("/").pop();

    chatC.innerHTML = `
      <div class="default-text">
        <div class="welcome-icon"><i class="fa fa-image"></i></div>
        <h2>Image ready</h2>
        <p>Ask anything about this image below.</p>
      </div>`;

    if (suggestionBar) suggestionBar.style.display = "flex";
  };

  sel.addEventListener("change", updatePreview);

  // Auto-select on page load (after upload redirect sends ?image_id=)
  if (typeof SELECTED_IMAGE_ID !== "undefined" && SELECTED_IMAGE_ID) {
    // Find and select the matching option
    for (const opt of sel.options) {
      if (opt.value === String(SELECTED_IMAGE_ID)) {
        opt.selected = true;
        break;
      }
    }
    updatePreview();
  } else if (sel.value) {
    // If the browser already has a selected option (e.g. from "selected" attr)
    updatePreview();
  }

  // --- Render a message bubble ---
  const scrollBottom = () => { chatC.scrollTop = chatC.scrollHeight; };

  const addBubble = (html, type, cls = "") => {
    const div = document.createElement("div");
    div.className = `chat ${type} ${cls}`.trim();
    div.innerHTML = `<div class="chat-content">${html}</div>`;
    if (type === "incoming") {
      const avatar = document.createElement("div");
      avatar.className = "chat-avatar";
      avatar.innerHTML = '<i class="fa fa-robot"></i>';
      div.prepend(avatar);
    }
    // Remove welcome default text on first message
    const welcome = chatC.querySelector(".default-text");
    if (welcome) welcome.remove();
    chatC.appendChild(div);
    scrollBottom();
    return div;
  };

  // --- Send message ---
  sendBtn.addEventListener("click", sendMsg);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMsg(); }
  });

  function sendMsg() {
    const txt = input.value.trim();
    if (!txt) { alert("Type a question first."); return; }
    if (!imageId) { alert("Please select an image first."); return; }
    input.value = "";
    addBubble(`<p>${txt.replace(/</g,"&lt;")}</p>`, "outgoing");
    const loading = addBubble(
      `<div class="typing-dots"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>`,
      "incoming", "loading-msg"
    );

    fetch(AJAX_URL, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded", "X-CSRFToken": CSRF_TOKEN },
      body: new URLSearchParams({ image_id: imageId, message: txt }),
    })
      .then((r) => r.json())
      .then((d) => {
        loading.remove();
        const text = d.bot_response || d.error || "No response.";
        const bubble = addBubble(`<div class="ai-markdown">${renderMd(text)}</div>`, "incoming");
        // Run highlight.js on code blocks
        if (window.hljs) {
          bubble.querySelectorAll("pre code").forEach((b) => hljs.highlightElement(b));
        }
      })
      .catch(() => {
        loading.remove();
        addBubble(`<p style="color:#f87171">Connection error. Please try again.</p>`, "incoming");
      });
  }

  // --- Clear history ---
  clearBtn.addEventListener("click", () => {
    if (!imageId || !confirm("Clear this image's chat history?")) return;
    fetch(AJAX_URL, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded", "X-CSRFToken": CSRF_TOKEN },
      body: new URLSearchParams({ image_id: imageId, action: "clear_history" }),
    }).then(() => {
      chatC.innerHTML = `
        <div class="default-text">
          <div class="welcome-icon"><i class="fa fa-image"></i></div>
          <h2>History cleared</h2>
          <p>Ask a new question about this image.</p>
        </div>`;
    });
  });

  // --- Suggestion chips ---
  if (suggestionBar) {
    suggestionBar.querySelectorAll(".tag-chip").forEach((chip) => {
      chip.addEventListener("click", () => {
        input.value = chip.dataset.prompt || chip.textContent.trim();
        input.focus();
      });
    });
  }
});
