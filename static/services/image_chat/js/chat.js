document.addEventListener("DOMContentLoaded",()=>{
  let imageId="";
  const sel=document.getElementById("img-select"),
        chatC=document.querySelector(".chat-container"),
        input=document.getElementById("chat-input"),
        send=document.getElementById("send-btn"),
        clr=document.getElementById("delete-btn"),
        preview=document.getElementById("image-preview"),
        previewEmpty=document.getElementById("image-preview-empty"),
        previewMeta=document.getElementById("image-preview-meta");

  const updatePreview = () => {
    const selected = sel.selectedOptions[0];
    if (!selected || !selected.value) {
      imageId = "";
      preview.hidden = true;
      preview.removeAttribute("src");
      previewMeta.hidden = true;
      previewMeta.textContent = "";
      previewEmpty.hidden = false;
      return;
    }
    imageId = selected.value;
    preview.src = selected.dataset.url;
    preview.alt = selected.dataset.name || "Selected image";
    preview.hidden = false;
    previewEmpty.hidden = true;
    previewMeta.hidden = false;
    previewMeta.textContent = selected.dataset.name || "Selected image";
    chatC.innerHTML=`<div class="default-text"><h2>Image selected.</h2><p>Ask a question below.</p></div>`;
  };

  sel.onchange=updatePreview;
  if (typeof SELECTED_IMAGE_ID !== "undefined" && SELECTED_IMAGE_ID) {
    updatePreview();
  }

  const escapeHtml = (text) => {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML.replace(/\n/g, "<br>");
  };
  const render=(html)=>{chatC.insertAdjacentHTML("beforeend",html);chatC.scrollTop=chatC.scrollHeight;};

  send.onclick=()=>{
    const txt=input.value.trim();
    if(!txt||!imageId)return;
    const defaultText = chatC.querySelector(".default-text");
    if (defaultText) defaultText.remove();
    input.value="";render(`<div class="chat outgoing"><div class="chat-content"><p>${escapeHtml(txt)}</p></div></div>`);
    render(`<div class="chat incoming loading-msg"><div class="chat-content"><p>...</p></div></div>`);
    fetch(AJAX_URL,{method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded","X-CSRFToken":CSRF_TOKEN},body:new URLSearchParams({image_id:imageId, message:txt})})
      .then(r=>r.json())
      .then(d=>{
        document.querySelectorAll(".chat.incoming.loading-msg").forEach(el=>el.remove());
        render(`<div class="chat incoming"><div class="chat-content"><p>${escapeHtml(d.bot_response||d.error)}</p></div></div>`);
      });
  };

  clr.onclick=()=>{
    if(!imageId||!confirm("Clear?"))return;
    fetch(AJAX_URL,{method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded","X-CSRFToken":CSRF_TOKEN},body:new URLSearchParams({image_id:imageId, action:"clear_history"})})
      .then(()=>chatC.innerHTML="");
  };
});
