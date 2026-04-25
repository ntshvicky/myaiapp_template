document.addEventListener("DOMContentLoaded", () => {
  const chatContainer = document.querySelector(".chat-container");
  const input = document.getElementById("chat-input");
  const sendBtn = document.getElementById("send-btn");
  const deleteBtn = document.getElementById("delete-btn");
  const providerSelect = document.getElementById("provider-select");
  const modelName = document.getElementById("model-name");
  const defaultModels = {
    gemini: "gemini-2.5-flash",
    openai: "gpt-4o-mini",
    anthropic: "claude-3-5-haiku-latest"
  };

  const scrollToBottom = () => {
    chatContainer.scrollTop = chatContainer.scrollHeight;
  };

  const renderMarkdown = (content) => {
    if (!window.marked || !window.DOMPurify) {
      const fallback = document.createElement("p");
      fallback.textContent = content;
      return fallback.outerHTML;
    }
    marked.setOptions({
      breaks: true,
      gfm: true
    });
    const rawHtml = marked.parse(content || "");
    return DOMPurify.sanitize(rawHtml, {
      ADD_TAGS: ["iframe"],
      ADD_ATTR: ["target", "rel"]
    });
  };

  const renderMermaidBlocks = async (container) => {
    if (!window.mermaid) return;
    mermaid.initialize({ startOnLoad: false, theme: "dark", securityLevel: "strict" });
    const blocks = container.querySelectorAll("pre code.language-mermaid, pre code[class='mermaid']");
    for (const block of blocks) {
      const source = block.textContent.trim();
      if (!source) continue;
      const wrapper = document.createElement("div");
      wrapper.className = "mermaid-chart";
      try {
        const id = `mermaid-${Date.now()}-${Math.random().toString(36).slice(2)}`;
        const rendered = await mermaid.render(id, source);
        wrapper.innerHTML = rendered.svg;
      } catch (error) {
        wrapper.textContent = source;
      }
      block.closest("pre").replaceWith(wrapper);
    }
  };

  const renderMessage = (content, type) => {
    const wrapper = document.createElement("div");
    wrapper.className = `chat ${type}`;
    const bubble = document.createElement("div");
    bubble.className = "chat-content";
    const details = document.createElement("div");
    details.className = type === "incoming" ? "chat-details ai-markdown" : "chat-details";
    if (type === "incoming") {
      details.innerHTML = renderMarkdown(content);
      renderMermaidBlocks(details);
    } else {
      const paragraph = document.createElement("p");
      paragraph.textContent = content;
      details.appendChild(paragraph);
    }
    bubble.appendChild(details);
    wrapper.appendChild(bubble);
    chatContainer.appendChild(wrapper);
    scrollToBottom();
  };

  const renderHtmlMessage = (content, type) => {
    const html = `
      <div class="chat ${type}">
        <div class="chat-content">
          <div class="chat-details"><p>${content}</p></div>
        </div>
      </div>`;
    chatContainer.insertAdjacentHTML("beforeend", html);
    scrollToBottom();
  };

  const sendMessage = () => {
    const text = input.value.trim();
    if (!text) return;
    input.value = "";
    renderMessage(text, "outgoing");
    // show typing indicator
    renderHtmlMessage(
      `<div class="typing-dots">
         <div class="dot"></div><div class="dot"></div><div class="dot"></div>
       </div>`,
      "incoming"
    );

    fetch(window.location.pathname, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": CSRF_TOKEN
      },
      body: new URLSearchParams({
        session_id: SESSION_ID,
        message: text,
        provider: providerSelect.value,
        model_name: modelName.value
      })
    })
    .then(res => res.json())
    .then(data => {
      // remove typing dots
      const lastInc = document.querySelectorAll(".chat.incoming");
      lastInc[lastInc.length - 1].remove();

      if (data.bot_response) {
        renderMessage(data.bot_response, "incoming");
      } else if (data.error) {
        renderMessage(data.error, "incoming");
      }
    })
    .catch(() => {
      renderMessage("Oops! Something went wrong.", "incoming");
    });
  };

  document.querySelectorAll(".ai-markdown").forEach((node) => {
    const markdown = node.innerText;
    node.innerHTML = renderMarkdown(markdown);
    renderMermaidBlocks(node);
  });

  sendBtn.addEventListener("click", sendMessage);
  input.addEventListener("keydown", e => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  providerSelect.addEventListener("change", () => {
    modelName.value = defaultModels[providerSelect.value] || modelName.value;
  });

  deleteBtn.addEventListener("click", () => {
    if (!confirm("Delete all chats?")) return;
    fetch(window.location.pathname, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": CSRF_TOKEN
      },
      body: new URLSearchParams({
        session_id: SESSION_ID,
        action: "clear_history"
      })
    })
    .then(() => {
      chatContainer.innerHTML = `
        <div class="default-text">
          <h1>AI Chatbot</h1><p>Start a conversation below.</p>
        </div>`;
    });
  });

  scrollToBottom();
});
