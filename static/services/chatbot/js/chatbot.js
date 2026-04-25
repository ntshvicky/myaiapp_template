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

  const emptyStateHtml = `
    <div class="default-text">
      <h1>AI Chatbot</h1>
      <p>Start with a prompt or choose a suggestion.</p>
      <div class="suggestion-grid" aria-label="Suggested prompts">
        <button type="button" class="suggestion-chip" data-prompt="Explain artificial intelligence vs human intelligence with a concise table and a simple diagram.">
          <i class="fa fa-diagram-project"></i>
          <span>Explain with diagram</span>
        </button>
        <button type="button" class="suggestion-chip" data-prompt="Research this topic deeply and give me key points, risks, examples, and next steps.">
          <i class="fa fa-magnifying-glass-chart"></i>
          <span>Research a topic</span>
        </button>
        <button type="button" class="suggestion-chip" data-prompt="Turn these notes into a professional summary with headings, bullets, and action items.">
          <i class="fa fa-list-check"></i>
          <span>Summarize notes</span>
        </button>
        <button type="button" class="suggestion-chip" data-prompt="Create a clear comparison table for two options, then recommend the best choice.">
          <i class="fa fa-table-columns"></i>
          <span>Compare options</span>
        </button>
      </div>
    </div>`;

  const clearEmptyState = () => {
    const emptyState = chatContainer.querySelector(".default-text");
    if (emptyState) {
      emptyState.remove();
    }
  };

  const bindSuggestionChips = () => {
    chatContainer.querySelectorAll(".suggestion-chip").forEach((button) => {
      button.addEventListener("click", () => {
        input.value = button.dataset.prompt || button.textContent.trim();
        input.focus();
        sendMessage();
      });
    });
  };

  const renderMarkdown = (content) => {
    if (!window.marked || !window.DOMPurify) {
      return renderBasicMarkdown(content);
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

  const escapeHtml = (text) => {
    const div = document.createElement("div");
    div.textContent = text || "";
    return div.innerHTML;
  };

  const renderInlineMarkdown = (text) => {
    return escapeHtml(text)
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*(.+?)\*/g, "<em>$1</em>")
      .replace(/`(.+?)`/g, "<code>$1</code>");
  };

  const renderBasicMarkdown = (content) => {
    const lines = (content || "").split(/\r?\n/);
    const html = [];
    let inList = false;

    const closeList = () => {
      if (inList) {
        html.push("</ul>");
        inList = false;
      }
    };

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed) {
        closeList();
        continue;
      }
      if (trimmed.startsWith("### ")) {
        closeList();
        html.push(`<h3>${renderInlineMarkdown(trimmed.slice(4))}</h3>`);
      } else if (trimmed.startsWith("## ")) {
        closeList();
        html.push(`<h2>${renderInlineMarkdown(trimmed.slice(3))}</h2>`);
      } else if (trimmed.startsWith("# ")) {
        closeList();
        html.push(`<h1>${renderInlineMarkdown(trimmed.slice(2))}</h1>`);
      } else if (/^[-*]\s+/.test(trimmed)) {
        if (!inList) {
          html.push("<ul>");
          inList = true;
        }
        html.push(`<li>${renderInlineMarkdown(trimmed.replace(/^[-*]\s+/, ""))}</li>`);
      } else {
        closeList();
        html.push(`<p>${renderInlineMarkdown(trimmed)}</p>`);
      }
    }
    closeList();
    return html.join("");
  };

  const renderMermaidBlocks = async (container) => {
    if (!window.mermaid) {
      convertRawMermaidText(container);
      return;
    }
    mermaid.initialize({ startOnLoad: false, theme: "dark", securityLevel: "strict" });
    const blocks = container.querySelectorAll("pre code.language-mermaid, pre code[class='mermaid']");
    for (const block of blocks) {
      const source = normalizeMermaidSource(block.textContent.trim());
      if (!source) continue;
      let wrapper = document.createElement("div");
      wrapper.className = "mermaid-chart";
      try {
        await mermaid.parse(source);
        const id = `mermaid-${Date.now()}-${Math.random().toString(36).slice(2)}`;
        const rendered = await mermaid.render(id, source);
        if (looksLikeMermaidError(rendered.svg)) {
          wrapper = buildMermaidFallback(source);
        } else {
          wrapper.innerHTML = rendered.svg;
        }
      } catch (error) {
        wrapper = buildMermaidFallback(source);
      }
      block.closest("pre").replaceWith(wrapper);
    }
    convertRawMermaidText(container);
  };

  const looksLikeMermaidError = (svg) => {
    return /syntax error|mermaid version|parse error|error-icon/i.test(svg || "");
  };

  const buildMermaidFallback = (source) => {
    const fallback = document.createElement("div");
    fallback.className = "mermaid-fallback";
    fallback.innerHTML = `
      <div class="diagram-error-title">Diagram unavailable</div>
      <p>The AI returned diagram syntax that Mermaid could not render.</p>
      <details>
        <summary>Show raw diagram text</summary>
        <pre><code>${escapeHtml(source)}</code></pre>
      </details>
    `;
    return fallback;
  };

  const convertRawMermaidText = (container) => {
    const paragraphs = Array.from(container.querySelectorAll("p"));
    for (const paragraph of paragraphs) {
      const text = paragraph.textContent.trim();
      if (!looksLikeRawMermaid(text)) continue;

      paragraph.replaceWith(buildMermaidFallback(text));
    }
  };

  const looksLikeRawMermaid = (text) => {
    return /^graph\s+(TD|TB|BT|RL|LR)\s+/i.test(text)
      || /^flowchart\s+(TD|TB|BT|RL|LR)\s+/i.test(text)
      || /^sequenceDiagram\s+/i.test(text)
      || /^classDiagram\s+/i.test(text);
  };

  const normalizeMermaidSource = (source) => {
    return (source || "")
      .replace(/^graph\s+(TD|TB|BT|RL|LR)\s+subgraph\s+/i, "flowchart $1\nsubgraph ")
      .replace(/^graph\s+/i, "flowchart ")
      .replace(/\s+end\s+/g, "\nend\n")
      .replace(/\s+(?=[A-Za-z0-9_]+\[)/g, "\n")
      .replace(/\s+(?=[A-Za-z0-9_]+\s*--[->])/g, "\n")
      .replace(/\s+(?=subgraph\s+)/gi, "\n")
      .trim();
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
    clearEmptyState();
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
    const source = node.querySelector(".markdown-source");
    const markdown = source ? source.innerText : node.innerText;
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
      chatContainer.innerHTML = emptyStateHtml;
      bindSuggestionChips();
    });
  });

  bindSuggestionChips();
  scrollToBottom();
});
