document.addEventListener("DOMContentLoaded", () => {
  const chatContainer = document.querySelector(".chat-container");
  const input = document.getElementById("chat-input");
  const sendBtn = document.getElementById("send-btn");
  const deleteBtn = document.getElementById("delete-btn");

  const scrollToBottom = () => {
    chatContainer.scrollTop = chatContainer.scrollHeight;
  };

  const renderMessage = (content, type) => {
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
    renderMessage(
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
        message: text
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

  sendBtn.addEventListener("click", sendMessage);
  input.addEventListener("keydown", e => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
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
