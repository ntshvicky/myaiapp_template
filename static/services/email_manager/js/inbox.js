/* Email Manager — full IMAP/SMTP client with AI */
document.addEventListener("DOMContentLoaded", () => {
  if (!ACCOUNT_ID) return;                       // no account yet → setup form shown

  const emailList    = document.getElementById("email-list");
  const detailEmpty  = document.getElementById("email-detail-empty");
  const detailView   = document.getElementById("email-detail-view");
  const detailSub    = document.getElementById("detail-subject");
  const detailFrom   = document.getElementById("detail-from");
  const detailTo     = document.getElementById("detail-to");
  const detailDate   = document.getElementById("detail-date");
  const detailBody   = document.getElementById("detail-body");
  const aiResultBox  = document.getElementById("ai-result-box");
  const composeOverlay  = document.getElementById("compose-overlay");
  const addAccOverlay   = document.getElementById("add-account-overlay");
  const composeAiResult = document.getElementById("compose-ai-result");

  let selectedUid = null;

  // ─── Markdown helper ───
  const renderMd = (text) => {
    if (!window.marked || !window.DOMPurify) return `<p>${text.replace(/\n/g, "<br>")}</p>`;
    marked.setOptions({ breaks: true, gfm: true });
    return DOMPurify.sanitize(marked.parse(text || ""));
  };

  // ─── POST helper ───
  function post(data) {
    return fetch(AJAX_URL, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded", "X-CSRFToken": CSRF_TOKEN },
      body: new URLSearchParams({ account_id: ACCOUNT_ID, ...data }),
    }).then(r => r.json());
  }

  // ─── Load emails for a folder ───
  function loadFolder(folder) {
    currentFolder = folder;
    // Update active folder button
    document.querySelectorAll(".email-folder-btn").forEach(btn => {
      btn.classList.toggle("active", btn.dataset.folder === folder);
    });
    emailList.innerHTML = `<div class="email-list-loading"><i class="fa fa-circle-notch fa-spin"></i><p>Loading ${folder}…</p></div>`;
    detailEmpty.style.display = "";
    if (detailView) detailView.style.display = "none";

    post({ action: "list_emails", folder }).then(d => {
      renderEmailList(d.emails || []);
    }).catch(() => {
      emailList.innerHTML = `<div class="email-list-loading"><i class="fa fa-exclamation-triangle" style="color:#f87171"></i><p>Failed to load emails.</p></div>`;
    });
  }

  // ─── Render email list ───
  function renderEmailList(emails) {
    if (!emails.length) {
      emailList.innerHTML = `<div class="email-list-loading"><i class="fa fa-inbox" style="color:var(--text-secondary)"></i><p>No emails found.</p></div>`;
      return;
    }
    emailList.innerHTML = emails.map(e => `
      <div class="email-row ${e.read ? '' : 'unread'}" data-uid="${e.uid}" data-folder="${currentFolder}">
        <div class="email-row-from">${escHtml(e.from || "—")}</div>
        <div class="email-row-subject">${escHtml(e.subject || "(no subject)")}</div>
        <div class="email-row-date">${formatDate(e.date)}</div>
      </div>
    `).join("");

    emailList.querySelectorAll(".email-row").forEach(row => {
      row.addEventListener("click", () => openEmail(row.dataset.uid, row.dataset.folder));
    });
  }

  // ─── Open a single email ───
  function openEmail(uid, folder) {
    selectedUid = uid;
    detailEmpty.style.display = "none";
    if (detailView) {
      detailView.style.display = "flex";
      detailSub.textContent  = "Loading…";
      detailFrom.textContent = "";
      detailTo.textContent   = "";
      detailDate.textContent = "";
      detailBody.innerHTML   = `<div style="text-align:center;padding:2rem"><i class="fa fa-circle-notch fa-spin fa-2x"></i></div>`;
      if (aiResultBox) { aiResultBox.style.display = "none"; aiResultBox.innerHTML = ""; }
    }
    // Mark visually as read
    document.querySelectorAll(`.email-row[data-uid="${uid}"]`).forEach(r => r.classList.remove("unread"));

    post({ action: "read_email", uid, folder: folder || currentFolder }).then(d => {
      if (d.error) {
        detailBody.innerHTML = `<p style="color:#f87171">${escHtml(d.error)}</p>`;
        return;
      }
      detailSub.textContent  = d.subject || "(no subject)";
      detailFrom.textContent = d.from    || "";
      detailTo.textContent   = d.to      || "";
      detailDate.textContent = d.date    || "";

      // Render body — prefer HTML, fallback to plain text markdown
      if (d.body && d.body.trim().startsWith("<")) {
        // Sanitize and display HTML
        detailBody.innerHTML = window.DOMPurify ? DOMPurify.sanitize(d.body) : d.body;
      } else {
        detailBody.innerHTML = renderMd(d.body || "");
      }
    }).catch(() => {
      detailBody.innerHTML = `<p style="color:#f87171">Failed to load email.</p>`;
    });
  }

  // ─── AI actions on open email ───
  document.querySelectorAll(".ai-pill[data-task]").forEach(btn => {
    btn.addEventListener("click", () => {
      if (!selectedUid || !detailBody) return;
      const task    = btn.dataset.task;
      const content = detailBody.innerText || detailBody.textContent;
      aiResultBox.style.display = "block";
      aiResultBox.innerHTML = `<div style="text-align:center"><i class="fa fa-circle-notch fa-spin"></i> AI is working…</div>`;
      post({ action: "ai_assist", task, content }).then(d => {
        aiResultBox.innerHTML = `
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.4rem">
            <strong style="font-size:0.8rem;color:var(--accent)"><i class="fa fa-robot"></i> AI Result</strong>
            <button onclick="document.getElementById('ai-result-box').style.display='none'" style="background:none;border:none;color:var(--text-secondary);cursor:pointer"><i class="fa fa-xmark"></i></button>
          </div>
          <div class="ai-markdown">${renderMd(d.result || d.error || "No result.")}</div>`;
      }).catch(() => {
        aiResultBox.innerHTML = `<p style="color:#f87171">AI request failed.</p>`;
      });
    });
  });

  // ─── AI actions on compose ───
  document.querySelectorAll(".ai-pill[data-compose-task]").forEach(btn => {
    btn.addEventListener("click", () => {
      const composeBody = document.getElementById("compose-body");
      if (!composeBody) return;
      const content = composeBody.value.trim();
      if (!content) { alert("Write something first."); return; }
      composeAiResult.style.display = "block";
      composeAiResult.innerHTML = `<i class="fa fa-circle-notch fa-spin"></i> Working…`;
      post({ action: "ai_assist", task: btn.dataset.composeTask, content }).then(d => {
        const result = d.result || d.error || "";
        composeAiResult.innerHTML = `
          <div style="display:flex;justify-content:space-between;margin-bottom:0.4rem">
            <strong style="font-size:0.75rem;color:var(--accent)">AI suggestion</strong>
            <button onclick="document.getElementById('compose-body').value=this.closest('[id]').querySelector('.ai-text').textContent;document.getElementById('compose-ai-result').style.display='none'" style="background:var(--accent);color:#fff;border:none;padding:0.2rem 0.5rem;border-radius:0.3rem;cursor:pointer;font-size:0.72rem">Use this</button>
          </div>
          <span class="ai-text" style="white-space:pre-wrap">${escHtml(result)}</span>`;
      });
    });
  });

  // ─── Search ───
  const searchInput = document.getElementById("email-search");
  const searchBtn   = document.getElementById("search-btn");
  if (searchBtn) {
    searchBtn.addEventListener("click", () => {
      const q = searchInput?.value.trim();
      if (!q) { loadFolder(currentFolder); return; }
      emailList.innerHTML = `<div class="email-list-loading"><i class="fa fa-circle-notch fa-spin"></i><p>Searching…</p></div>`;
      post({ action: "search", query: q, folder: currentFolder }).then(d => {
        renderEmailList(d.emails || []);
      });
    });
    searchInput?.addEventListener("keydown", e => { if (e.key === "Enter") searchBtn.click(); });
  }

  // ─── Folder navigation ───
  document.querySelectorAll(".email-folder-btn").forEach(btn => {
    btn.addEventListener("click", () => loadFolder(btn.dataset.folder));
  });

  // ─── Compose ───
  const composeBtn = document.getElementById("compose-btn");
  if (composeBtn && composeOverlay) {
    composeBtn.addEventListener("click", () => {
      composeOverlay.style.display = "flex";
      document.getElementById("compose-to")?.focus();
    });
  }
  document.getElementById("close-compose-btn")?.addEventListener("click", () => {
    if (composeOverlay) composeOverlay.style.display = "none";
  });

  const sendEmailBtn = document.getElementById("send-email-btn");
  if (sendEmailBtn) {
    sendEmailBtn.addEventListener("click", () => {
      const to      = document.getElementById("compose-to")?.value.trim();
      const subject = document.getElementById("compose-subject")?.value.trim();
      const body    = document.getElementById("compose-body")?.value.trim();
      if (!to) { alert("Enter a recipient."); return; }
      sendEmailBtn.disabled = true;
      sendEmailBtn.innerHTML = `<i class="fa fa-circle-notch fa-spin"></i> Sending…`;
      post({ action: "send", to, subject: subject || "(no subject)", body }).then(d => {
        sendEmailBtn.disabled = false;
        sendEmailBtn.innerHTML = `<i class="fa fa-paper-plane"></i> Send`;
        if (d.sent) {
          alert("Email sent!");
          if (composeOverlay) composeOverlay.style.display = "none";
          document.getElementById("compose-to").value = "";
          document.getElementById("compose-subject").value = "";
          document.getElementById("compose-body").value = "";
        } else {
          alert("Failed: " + (d.error || "Unknown error"));
        }
      }).catch(() => {
        sendEmailBtn.disabled = false;
        sendEmailBtn.innerHTML = `<i class="fa fa-paper-plane"></i> Send`;
        alert("Connection error. Please try again.");
      });
    });
  }

  // ─── Add account overlay ───
  document.getElementById("add-account-btn")?.addEventListener("click", () => {
    if (addAccOverlay) addAccOverlay.style.display = "flex";
  });
  document.getElementById("close-add-overlay")?.addEventListener("click", () => {
    if (addAccOverlay) addAccOverlay.style.display = "none";
  });
  addAccOverlay?.addEventListener("click", e => {
    if (e.target === addAccOverlay) addAccOverlay.style.display = "none";
  });

  // ─── Utils ───
  function escHtml(s) {
    return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
  }
  function formatDate(dateStr) {
    if (!dateStr) return "";
    try {
      const d = new Date(dateStr);
      const now = new Date();
      const isToday = d.toDateString() === now.toDateString();
      return isToday
        ? d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
        : d.toLocaleDateString([], { month: "short", day: "numeric" });
    } catch { return dateStr.substring(0, 16); }
  }

  // ─── Initial load ───
  loadFolder(currentFolder || "INBOX");
});
