document.addEventListener("DOMContentLoaded", () => {
    const chatCont = document.getElementById("chat-container");
    const input = document.getElementById("chat-input");
    const sendBtn = document.getElementById("send-btn");
    const delBtn = document.getElementById("delete-btn");

    // Scroll to bottom initially if there are messages
    if (chatCont) chatCont.scrollTop = chatCont.scrollHeight;

    const render = (html) => {
        chatCont.insertAdjacentHTML("beforeend", html);
        chatCont.scrollTop = chatCont.scrollHeight;
    };

    if (sendBtn) {
        sendBtn.onclick = () => {
            const txt = input.value.trim(); 
            if (!txt || !SESSION_ID) return;
            
            input.value = ""; 
            
            // Remove the default text if it exists
            const defaultText = chatCont.querySelector('.default-text');
            if (defaultText) defaultText.remove();
            
            render(`
                <div class="chat outgoing">
                    <div class="chat-content">
                        <p>${txt.replace(/\n/g, '<br>')}</p>
                    </div>
                </div>
            `);
            
            render(`
                <div class="chat incoming loading-msg">
                    <div class="chat-content">
                        <p>...</p>
                    </div>
                </div>
            `);
            
            fetch(AJAX_URL, {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-CSRFToken": CSRF_TOKEN
                },
                body: new URLSearchParams({session_id: SESSION_ID, message: txt})
            })
            .then(r => r.json())
            .then(d => {
                const loadingMsg = document.querySelector(".chat.incoming.loading-msg");
                if (loadingMsg) loadingMsg.remove();
                
                const responseText = d.bot_response || d.error || "Unknown error occurred.";
                // Simple markdown-to-html line breaks
                const formattedResponse = responseText.replace(/\n/g, '<br>');
                
                render(`
                    <div class="chat incoming">
                        <div class="chat-content">
                            <p>${formattedResponse}</p>
                        </div>
                    </div>
                `);
            })
            .catch(err => {
                const loadingMsg = document.querySelector(".chat.incoming.loading-msg");
                if (loadingMsg) loadingMsg.remove();
                
                render(`
                    <div class="chat incoming">
                        <div class="chat-content" style="background: rgba(239, 68, 68, 0.2); color: #ef4444;">
                            <p>Failed to connect to the server.</p>
                        </div>
                    </div>
                `);
            });
        };
    }

    // Allow pressing Enter to send
    if (input) {
        input.addEventListener("keypress", function(event) {
            if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                sendBtn.click();
            }
        });
    }

    if (delBtn) {
        delBtn.onclick = () => {
            if (!SESSION_ID || !confirm("Clear all chat history for this document?")) return;
            fetch(AJAX_URL, {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-CSRFToken": CSRF_TOKEN
                },
                body: new URLSearchParams({session_id: SESSION_ID, action: "clear_history"})
            })
            .then(() => {
                chatCont.innerHTML = `
                    <div class="default-text" style="text-align: center; margin-top: auto; margin-bottom: auto; color: var(--text-secondary);">
                        <h2>Chat Cleared</h2>
                        <p>History has been erased. You can start over.</p>
                    </div>
                `;
            });
        };
    }
});
