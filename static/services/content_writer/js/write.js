document.addEventListener("DOMContentLoaded", () => {
  // ── Elements ──────────────────────────────────────────────────────────────
  const genBtn       = document.getElementById("gen-btn");
  const promptInput  = document.getElementById("prompt-input");
  const keywordsInput= document.getElementById("keywords-input");
  const outputArea   = document.getElementById("output-area");
  const placeholder  = document.getElementById("cw-placeholder");
  const wordCountOut = document.getElementById("word-count-out");
  const copyBtn      = document.getElementById("copy-btn");
  const downloadBtn  = document.getElementById("download-btn");
  const clearBtn     = document.getElementById("clear-btn");
  const slider       = document.getElementById("word-count-slider");
  const sliderLabel  = document.getElementById("word-count-label");

  // ── State ──────────────────────────────────────────────────────────────────
  let selectedType = "Blog Post";
  let selectedTone = "Professional";
  let rawText      = "";   // plain markdown output for copy/download

  // ── Slider ────────────────────────────────────────────────────────────────
  slider.addEventListener("input", () => {
    sliderLabel.textContent = `~${slider.value} words`;
  });

  // ── Chip selectors ────────────────────────────────────────────────────────
  document.getElementById("type-grid").addEventListener("click", e => {
    const chip = e.target.closest(".cw-select-chip");
    if (!chip) return;
    document.querySelectorAll("#type-grid .cw-select-chip").forEach(c => c.classList.remove("active"));
    chip.classList.add("active");
    selectedType = chip.dataset.val;
  });

  document.getElementById("tone-grid").addEventListener("click", e => {
    const chip = e.target.closest(".cw-select-chip");
    if (!chip) return;
    document.querySelectorAll("#tone-grid .cw-select-chip").forEach(c => c.classList.remove("active"));
    chip.classList.add("active");
    selectedTone = chip.dataset.val;
  });

  // ── Quick prompt chips ────────────────────────────────────────────────────
  document.getElementById("quick-chips").addEventListener("click", e => {
    const chip = e.target.closest(".cw-quick-chip");
    if (!chip) return;
    promptInput.value = chip.dataset.prompt;
    promptInput.focus();
  });

  // ── Render markdown output ────────────────────────────────────────────────
  const renderOutput = (text) => {
    rawText = text;
    if (placeholder) placeholder.remove();

    let html = text;
    if (window.marked && window.DOMPurify) {
      marked.setOptions({ breaks: true, gfm: true });
      html = DOMPurify.sanitize(marked.parse(text));
    } else {
      html = `<p>${text.replace(/\n/g, "<br>")}</p>`;
    }
    outputArea.innerHTML = html;
    if (window.hljs) outputArea.querySelectorAll("pre code").forEach(b => hljs.highlightElement(b));

    // Word count
    const wc = text.trim().split(/\s+/).filter(Boolean).length;
    wordCountOut.textContent = `${wc.toLocaleString()} words`;
    outputArea.scrollTop = 0;
  };

  // ── Show typing indicator ─────────────────────────────────────────────────
  const showTyping = () => {
    if (placeholder) placeholder.style.display = "none";
    outputArea.innerHTML = `
      <div class="cw-typing-pulse">
        <div class="dot"></div><div class="dot"></div><div class="dot"></div>
        <span>Generating your ${selectedType.toLowerCase()}…</span>
      </div>`;
    wordCountOut.textContent = "";
  };

  // ── Build prompt for the API ──────────────────────────────────────────────
  const buildPrompt = () => {
    const topic    = promptInput.value.trim();
    const keywords = keywordsInput.value.trim();
    const words    = slider.value;

    let prompt = `Write a ${selectedTone.toLowerCase()} ${selectedType} about:\n${topic}\n\n`;
    prompt += `Target length: approximately ${words} words.\n`;
    prompt += `Tone: ${selectedTone}.\n`;
    if (keywords) prompt += `Include keywords/focus areas: ${keywords}.\n`;
    prompt += `\nFormat the output with clear headings and well-structured paragraphs. Use markdown formatting.`;
    return prompt;
  };

  // ── Generate ──────────────────────────────────────────────────────────────
  const generate = () => {
    const topic = promptInput.value.trim();
    if (!topic) { promptInput.focus(); promptInput.style.borderColor = "#f87171"; return; }
    promptInput.style.borderColor = "";

    genBtn.disabled = true;
    genBtn.innerHTML = '<i class="fa fa-circle-notch fa-spin"></i> Generating…';
    showTyping();

    fetch(AJAX_URL, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded", "X-CSRFToken": CSRF_TOKEN },
      body: new URLSearchParams({ prompt: buildPrompt() }),
    })
      .then(r => r.json())
      .then(d => {
        genBtn.disabled = false;
        genBtn.innerHTML = '<i class="fa fa-wand-magic-sparkles"></i> Generate Content';
        if (d.error) {
          outputArea.innerHTML = `<p style="color:#f87171"><i class="fa fa-circle-exclamation"></i> ${d.error}</p>`;
          return;
        }
        renderOutput(d.content || "");
      })
      .catch(() => {
        genBtn.disabled = false;
        genBtn.innerHTML = '<i class="fa fa-wand-magic-sparkles"></i> Generate Content';
        outputArea.innerHTML = `<p style="color:#f87171"><i class="fa fa-circle-exclamation"></i> Connection error. Please try again.</p>`;
      });
  };

  genBtn.addEventListener("click", generate);
  promptInput.addEventListener("keydown", e => {
    if (e.key === "Enter" && e.ctrlKey) { e.preventDefault(); generate(); }
  });

  // ── Copy ──────────────────────────────────────────────────────────────────
  copyBtn.addEventListener("click", () => {
    if (!rawText) return;
    navigator.clipboard.writeText(rawText).then(() => {
      copyBtn.innerHTML = '<i class="fa fa-check"></i> Copied!';
      setTimeout(() => { copyBtn.innerHTML = '<i class="fa fa-copy"></i> Copy'; }, 2000);
    });
  });

  // ── Download ──────────────────────────────────────────────────────────────
  downloadBtn.addEventListener("click", () => {
    if (!rawText) return;
    const blob = new Blob([rawText], { type: "text/markdown;charset=utf-8" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    const topic = (promptInput.value.trim().slice(0, 30) || "content").replace(/\s+/g, "_").replace(/[^a-z0-9_]/gi, "");
    a.download = `${selectedType.replace(/\s+/g,"_")}_${topic}.md`;
    a.click();
    URL.revokeObjectURL(a.href);
  });

  // ── Clear ─────────────────────────────────────────────────────────────────
  clearBtn.addEventListener("click", () => {
    rawText = "";
    wordCountOut.textContent = "";
    outputArea.innerHTML = `
      <div class="cw-placeholder" id="cw-placeholder">
        <div class="cw-placeholder-icon"><i class="fa fa-pen-nib"></i></div>
        <h3>Ready to Write</h3>
        <p>Fill in the configuration on the left and click <strong>Generate Content</strong> — or pick a quick prompt above.</p>
      </div>`;
  });
});
