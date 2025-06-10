document.addEventListener("DOMContentLoaded",()=>{
  const chatContainer=document.querySelector(".chat-container"),
        input=document.getElementById("chat-input"),
        sendBtn=document.getElementById("send-btn"),
        deleteBtn=document.getElementById("delete-btn");

  const scrollBot=()=>chatContainer.scrollTop=chatContainer.scrollHeight;
  const render=(html)=>{chatContainer.insertAdjacentHTML("beforeend",html);scrollBot();};

  const send=()=>{
    const text=input.value.trim();
    if(!text) return;
    input.value=""; render(`<div class="chat outgoing"><div class="chat-content"><div class="chat-details"><p>${text}</p></div></div></div>`);
    render(`<div class="chat incoming"><div class="chat-content"><div class="chat-details"><div class="typing-dots"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div></div></div></div>`);

    fetch(window.location.pathname,{
      method:"POST",
      headers:{
        "Content-Type":"application/x-www-form-urlencoded",
        "X-CSRFToken":CSRF_TOKEN
      },
      body:new URLSearchParams({session_id:SESSION_ID, message:text})
    })
    .then(r=>r.json())
    .then(d=>{
      document.querySelectorAll(".chat.incoming").at(-1).remove();
      render(d.bot_response? 
        `<div class="chat incoming"><div class="chat-content"><div class="chat-details"><p>${d.bot_response}</p></div></div></div>` :
        `<div class="chat incoming"><div class="chat-content"><div class="chat-details"><p class="error">${d.error}</p></div></div></div>`);
    })
    .catch(_=>render(`<div class="chat incoming"><div class="chat-content"><div class="chat-details"><p class="error">Error.</p></div></div></div>`));
  };

  sendBtn.onclick=send;
  input.addEventListener("keydown",e=>{if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();send();}});
  deleteBtn.onclick=()=>{
    if(!confirm("Clear history?"))return;
    fetch(window.location.pathname,{
      method:"POST",
      headers:{"Content-Type":"application/x-www-form-urlencoded","X-CSRFToken":CSRF_TOKEN},
      body:new URLSearchParams({session_id:SESSION_ID, action:"clear_history"})
    }).then(()=>{
      chatContainer.innerHTML=`<div class="default-text"><h1>Webpage Analysis</h1><p>Enter “URL::Your question” to start.</p></div>`;
    });
  };

  scrollBot();
});
