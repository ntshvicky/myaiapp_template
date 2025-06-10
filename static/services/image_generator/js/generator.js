document.addEventListener("DOMContentLoaded",()=>{
  const genBtn=document.getElementById("gen-btn"),
        promptInput=document.getElementById("prompt-input"),
        grid=document.getElementById("images-grid");

  const renderImage=(url,prompt)=>{
    const html=`<div class="generated-image"><img src="${url}"><p>${prompt}</p></div>`;
    grid.insertAdjacentHTML("afterbegin",html);
  };

  genBtn.onclick=()=>{
    const prompt=promptInput.value.trim();
    if(!prompt)return;
    promptInput.value="";
    fetch(window.location.pathname,{
      method:"POST",
      headers:{"Content-Type":"application/x-www-form-urlencoded","X-CSRFToken":CSRF_TOKEN},
      body:new URLSearchParams({session_id:SESSION_ID,prompt:prompt})
    })
    .then(r=>r.json())
    .then(d=>{
      if(d.image_url) renderImage(d.image_url,prompt);
      else alert(d.error);
    })
    .catch(err=>alert("Error."));
  };
});
