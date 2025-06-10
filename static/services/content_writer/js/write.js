document.addEventListener("DOMContentLoaded",()=>{
  const btn=document.getElementById("gen-btn"),
        inp=document.getElementById("prompt-input"),
        res=document.getElementById("result");

  btn.onclick=()=>{
    const p=inp.value.trim(); if(!p)return;
    inp.value="";
    fetch(window.location.pathname,{
      method:"POST",
      headers:{"Content-Type":"application/x-www-form-urlencoded","X-CSRFToken":CSRF_TOKEN},
      body:new URLSearchParams({prompt:p})
    })
    .then(r=>r.json())
    .then(d=>{ res.textContent = d.content || d.error; });
  };
});
