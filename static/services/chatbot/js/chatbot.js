// Initialise Mermaid once (before DOMContentLoaded so it's ready)
if (window.mermaid) {
  mermaid.initialize({
    startOnLoad: false,
    theme: "dark",
    securityLevel: "loose",
    flowchart: { htmlLabels: true, curve: "basis" },
    themeVariables: { fontSize: "14px" },
  });
}

document.addEventListener("DOMContentLoaded", () => {
  const chatContainer = document.getElementById("chat-container");
  const input = document.getElementById("chat-input");
  const sendBtn = document.getElementById("send-btn");
  const deleteBtn = document.getElementById("delete-btn");
  const providerSelect = document.getElementById("provider-select");
  const modelSelect = document.getElementById("model-select");
  const tokenCount = document.getElementById("token-count");

  const MODELS = {
    gemini: [
      { value: "gemini-2.5-flash", label: "Gemini 2.5 Flash" },
      { value: "gemini-2.5-pro", label: "Gemini 2.5 Pro" },
      { value: "gemini-2.0-flash", label: "Gemini 2.0 Flash" },
      { value: "gemini-1.5-pro", label: "Gemini 1.5 Pro" },
    ],
    openai: [
      { value: "gpt-4o", label: "GPT-4o" },
      { value: "gpt-4o-mini", label: "GPT-4o Mini" },
      { value: "gpt-4-turbo", label: "GPT-4 Turbo" },
      { value: "o1-mini", label: "o1 Mini" },
    ],
    anthropic: [
      { value: "claude-opus-4-7", label: "Claude Opus 4.7" },
      { value: "claude-sonnet-4-6", label: "Claude Sonnet 4.6" },
      { value: "claude-haiku-4-5-20251001", label: "Claude Haiku 4.5" },
      { value: "claude-3-5-haiku-latest", label: "Claude 3.5 Haiku" },
    ],
  };

  // --- Model dropdown ---
  function populateModels(provider, selectedModel) {
    const list = MODELS[provider] || [];
    modelSelect.innerHTML = "";
    list.forEach(({ value, label }) => {
      const opt = document.createElement("option");
      opt.value = value;
      opt.textContent = label;
      if (value === selectedModel) opt.selected = true;
      modelSelect.appendChild(opt);
    });
    if (!modelSelect.value && list.length) modelSelect.value = list[0].value;
  }

  populateModels(SESSION_PROVIDER, SESSION_MODEL);

  providerSelect.addEventListener("change", () => {
    populateModels(providerSelect.value, null);
  });

  // --- Auto-resize textarea ---
  input.addEventListener("input", () => {
    input.style.height = "auto";
    input.style.height = Math.min(input.scrollHeight, 140) + "px";
  });

  // --- Scroll helper ---
  const scrollToBottom = () => {
    chatContainer.scrollTop = chatContainer.scrollHeight;
  };

  // --- Markdown rendering ---
  const renderMarkdown = (content) => {
    if (!window.marked || !window.DOMPurify) {
      return `<p>${content.replace(/\n/g, "<br>")}</p>`;
    }
    marked.setOptions({ breaks: true, gfm: true });
    const rawHtml = marked.parse(content || "");
    return DOMPurify.sanitize(rawHtml, {
      ADD_TAGS: ["iframe"],
      ADD_ATTR: ["target", "rel"],
    });
  };

  // --- Mermaid rendering ---
  const renderMermaidBlocks = async (container) => {
    if (!window.mermaid) return;
    // Select both language-mermaid and bare mermaid class
    const blocks = container.querySelectorAll(
      "pre code.language-mermaid, pre code[class='mermaid'], pre code[class='language-mermaid']"
    );
    for (const block of blocks) {
      const source = block.textContent.trim();
      if (!source) continue;
      const pre = block.closest("pre");
      if (!pre) continue;
      const wrapper = document.createElement("div");
      wrapper.className = "mermaid-chart";
      try {
        const id = `mermaid-${Date.now()}-${Math.random().toString(36).slice(2)}`;
        const { svg } = await mermaid.render(id, source);
        wrapper.innerHTML = svg;
      } catch (err) {
        console.warn("Mermaid render failed:", err);
        // Show as styled code block, not raw
        wrapper.innerHTML = `<div class="mermaid-fallback"><i class="fa fa-diagram-project"></i> Diagram could not render — syntax error in Mermaid source.<pre>${source}</pre></div>`;
      }
      pre.replaceWith(wrapper);
    }
  };

  // --- Chart.js rendering ---
  const renderChartBlocks = (container) => {
    if (!window.Chart) return;
    const blocks = container.querySelectorAll("pre code.language-chart-json, pre code.language-chart");
    blocks.forEach((block) => {
      let cfg;
      try {
        cfg = JSON.parse(block.textContent.trim());
      } catch {
        return;
      }
      const wrapper = document.createElement("div");
      wrapper.className = "chart-wrapper";
      const canvas = document.createElement("canvas");
      wrapper.appendChild(canvas);
      block.closest("pre").replaceWith(wrapper);

      const isDark = true;
      Chart.defaults.color = "#94a3b8";
      Chart.defaults.borderColor = "rgba(255,255,255,0.1)";

      // Build datasets with default colors if not provided
      const palette = ["#2f80ed", "#56ccf2", "#27ae60", "#f2c94c", "#eb5757", "#9b51e0", "#f2994a"];
      if (cfg.data && cfg.data.datasets) {
        cfg.data.datasets = cfg.data.datasets.map((ds, i) => ({
          backgroundColor: palette[i % palette.length] + "cc",
          borderColor: palette[i % palette.length],
          borderWidth: 2,
          ...ds,
        }));
      }

      new Chart(canvas, {
        ...cfg,
        options: {
          responsive: true,
          plugins: {
            legend: { labels: { color: "#f8fafc" } },
            title: cfg.options?.plugins?.title || {},
          },
          scales: cfg.type !== "pie" && cfg.type !== "doughnut" ? {
            x: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.07)" } },
            y: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.07)" } },
          } : undefined,
          ...(cfg.options || {}),
        },
      });
    });
  };

  // --- Highlight.js for code ---
  const highlightCodeBlocks = (container) => {
    if (!window.hljs) return;
    // Exclude mermaid/chart blocks — those are handled by their own renderers
    const selector = "pre code:not(.language-mermaid):not(.mermaid):not(.language-chart):not(.language-chart-json)";
    container.querySelectorAll(selector).forEach((block) => {
      if (block.dataset.highlighted) return; // already done
      hljs.highlightElement(block);
    });
    // Add copy button to each pre block
    container.querySelectorAll("pre").forEach((pre) => {
      if (pre.querySelector(".copy-code-btn")) return;
      const btn = document.createElement("button");
      btn.className = "copy-code-btn";
      btn.innerHTML = '<i class="fa fa-copy"></i>';
      btn.title = "Copy code";
      btn.addEventListener("click", () => {
        const code = pre.querySelector("code");
        navigator.clipboard.writeText(code ? code.textContent : pre.textContent).then(() => {
          btn.innerHTML = '<i class="fa fa-check"></i>';
          setTimeout(() => { btn.innerHTML = '<i class="fa fa-copy"></i>'; }, 1800);
        });
      });
      pre.style.position = "relative";
      pre.appendChild(btn);
    });
  };

  // --- Render an AI message node (async: Mermaid must finish before hljs) ---
  const processAINode = async (node) => {
    const raw = node.textContent;
    node.innerHTML = renderMarkdown(raw);
    // Mermaid FIRST — it replaces <pre><code> blocks with SVG
    await renderMermaidBlocks(node);
    // Chart.js next — replaces chart-json blocks with canvas
    renderChartBlocks(node);
    // highlight.js last — only touches remaining code blocks
    highlightCodeBlocks(node);
  };

  // --- Create message DOM ---
  const renderMessage = (content, type) => {
    const welcome = document.getElementById("default-welcome");
    if (welcome) welcome.remove();

    const wrapper = document.createElement("div");
    wrapper.className = `chat ${type}`;

    if (type === "incoming") {
      const avatar = document.createElement("div");
      avatar.className = "chat-avatar";
      avatar.innerHTML = '<i class="fa fa-robot"></i>';
      wrapper.appendChild(avatar);
    }

    const bubble = document.createElement("div");
    bubble.className = "chat-content";
    const details = document.createElement("div");

    if (type === "incoming") {
      details.className = "chat-details ai-markdown";
      details.textContent = content;
      bubble.appendChild(details);
      wrapper.appendChild(bubble);
      chatContainer.appendChild(wrapper);
      scrollToBottom();
      processAINode(details);
    } else {
      details.className = "chat-details";
      const p = document.createElement("p");
      p.textContent = content;
      details.appendChild(p);
      bubble.appendChild(details);
      wrapper.appendChild(bubble);
      chatContainer.appendChild(wrapper);
      scrollToBottom();
    }
  };

  // --- Typing indicator ---
  const showTyping = () => {
    const wrapper = document.createElement("div");
    wrapper.className = "chat incoming typing-message";
    wrapper.innerHTML = `
      <div class="chat-avatar"><i class="fa fa-robot"></i></div>
      <div class="chat-content">
        <div class="chat-details">
          <div class="typing-dots"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>
        </div>
      </div>`;
    chatContainer.appendChild(wrapper);
    scrollToBottom();
    return wrapper;
  };

  // --- Send message ---
  const sendMessage = () => {
    const text = input.value.trim();
    if (!text) return;
    input.value = "";
    input.style.height = "auto";
    sendBtn.disabled = true;

    renderMessage(text, "outgoing");
    const typingEl = showTyping();

    fetch(window.location.pathname, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": CSRF_TOKEN,
      },
      body: new URLSearchParams({
        session_id: SESSION_ID,
        message: text,
        provider: providerSelect.value,
        model_name: modelSelect.value,
      }),
    })
      .then((res) => res.json())
      .then((data) => {
        typingEl.remove();
        if (data.bot_response) {
          renderMessage(data.bot_response, "incoming");
        } else if (data.error) {
          renderMessage(`Error: ${data.error}`, "incoming");
        }
        if (data.total_tokens !== undefined && tokenCount) {
          const current = parseInt(tokenCount.textContent.replace(/,/g, ""), 10) || 0;
          tokenCount.textContent = (current + data.total_tokens).toLocaleString();
        }
      })
      .catch(() => {
        typingEl.remove();
        renderMessage("Connection error. Please try again.", "incoming");
      })
      .finally(() => {
        sendBtn.disabled = false;
        input.focus();
      });
  };

  // --- Process existing AI messages on load ---
  document.querySelectorAll(".ai-markdown").forEach(processAINode);

  // --- Suggestion tag clicks ---
  document.querySelectorAll(".tag-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      input.value = chip.dataset.prompt || chip.textContent.trim();
      input.dispatchEvent(new Event("input"));
      input.focus();
    });
  });

  // --- Event listeners ---
  sendBtn.addEventListener("click", sendMessage);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  deleteBtn.addEventListener("click", () => {
    if (!confirm("Clear all messages in this conversation?")) return;
    fetch(window.location.pathname, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": CSRF_TOKEN,
      },
      body: new URLSearchParams({ session_id: SESSION_ID, action: "clear_history" }),
    }).then(() => {
      chatContainer.innerHTML = `
        <div class="default-text" id="default-welcome">
          <div class="welcome-icon"><i class="fa fa-robot"></i></div>
          <h2>AI Chatbot</h2>
          <p>Ask me anything — I can research, explain, compare, write code, create diagrams, and more.</p>
        </div>`;
      if (tokenCount) tokenCount.textContent = "0";
    });
  });

  scrollToBottom();
});
