document.addEventListener("DOMContentLoaded",()=>{
  let sessionId="";
  const sel=document.getElementById("img-select"),
        chatC=document.querySelector(".chat-container"),
        input=document.getElementById("chat-input"),
        send=document.getElementById("send-btn"),
        clr=document.getElementById("delete-btn");

  sel.onchange=()=>{
    if(!sel.value)return;
    sessionId=sel.value; // stub
    chatC.innerHTML="";
  };

  const render=(html)=>{chatC.insertAdjacentHTML("beforeend",html);chatC.scrollTop=chatC.scrollHeight;};

  send.onclick=()=>{
    const txt=input.value.trim();
    if(!txt||!sessionId)return;
    input.value="";render(`<div class="chat outgoing"><div class="chat-details"><p>${txt}</p></div></div>`);
    render(`<div class="chat incoming"><div class="typing-dots"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div></div>`);
    fetch(AJAX_URL,{method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded","X-CSRFToken":CSRF_TOKEN},body:new URLSearchParams({session_id:sessionId, message:txt})})
      .then(r=>r.json())
      .then(d=>{
        document.querySelectorAll(".chat.incoming").at(-1).remove();
        render(`<div class="chat incoming"><div class="chat-details"><p>${d.bot_response||d.error}</p></div></div>`);
      });
  };

  clr.onclick=()=>{
    if(!sessionId||!confirm("Clear?"))return;
    fetch(AJAX_URL,{method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded","X-CSRFToken":CSRF_TOKEN},body:new URLSearchParams({session_id:sessionId, action:"clear_history"})})
      .then(()=>chatC.innerHTML="");
  };
});
