document.addEventListener("DOMContentLoaded",()=>{
  let sessionId="";
  const selectDoc=document.getElementById("doc-select"),
        chatCont=document.querySelector(".chat-container"),
        input=document.getElementById("chat-input"),
        sendBtn=document.getElementById("send-btn"),
        delBtn=document.getElementById("delete-btn");

  selectDoc.onchange=()=>{
    if(!selectDoc.value)return;
    // create/get session on server sync if needed
    sessionId=selectDoc.value; // stub: in real life, fetch or create session via AJAX
    chatCont.innerHTML="";
  };

  const render=(html)=>{chatCont.insertAdjacentHTML("beforeend",html);chatCont.scrollTop=chatCont.scrollHeight;};

  sendBtn.onclick=()=>{
    const txt=input.value.trim(); if(!txt||!sessionId)return;
    input.value=""; render(`<div class="chat outgoing"><div class="chat-content"><div class="chat-details"><p>${txt}</p></div></div></div>`);
    render(`<div class="chat incoming"><div class="typing-dots"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div></div>`);
    fetch(AJAX_URL,{method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded","X-CSRFToken":CSRF_TOKEN},body:new URLSearchParams({session_id:sessionId, message:txt})})
      .then(r=>r.json())
      .then(d=>{
        document.querySelectorAll(".chat.incoming").at(-1).remove();
        render(`<div class="chat incoming"><div class="chat-details"><p>${d.bot_response||d.error}</p></div></div>`);
      });
  };

  delBtn.onclick=()=>{
    if(!sessionId||!confirm("Clear?"))return;
    fetch(AJAX_URL,{method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded","X-CSRFToken":CSRF_TOKEN},body:new URLSearchParams({session_id:sessionId, action:"clear_history"})})
      .then(()=>chatCont.innerHTML="");
  };
});
