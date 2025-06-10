document.addEventListener("DOMContentLoaded",()=>{
  const btn=document.getElementById("gen-btn"),
        input=document.getElementById("prompt-input"),
        list=document.getElementById("videos-list");

  btn.onclick=()=>{
    const p=input.value.trim();
    if(!p)return;
    input.value="";
    fetch(window.location.pathname,{
      method:"POST",
      headers:{"Content-Type":"application/x-www-form-urlencoded","X-CSRFToken":CSRF_TOKEN},
      body:new URLSearchParams({session_id:SESSION_ID,prompt:p})
    })
    .then(r=>r.json())
    .then(d=>{
      if(d.video_url){
        const html=`<div class="generated-video"><video controls src="${d.video_url}"></video><p>${p}</p></div>`;
        list.insertAdjacentHTML("afterbegin",html);
      } else alert(d.error);
    });
  };
});
