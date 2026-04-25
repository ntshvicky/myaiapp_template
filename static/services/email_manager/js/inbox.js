document.addEventListener("DOMContentLoaded",()=>{
  const acct=document.getElementById("acct-select"),
        searchIn=document.getElementById("search-input"),
        searchBtn=document.getElementById("search-btn"),
        resList=document.getElementById("results"),
        toIn=document.getElementById("to"),
        subjIn=document.getElementById("subject"),
        bodyIn=document.getElementById("body"),
        sendBtn=document.getElementById("send-btn");

  searchBtn.onclick=()=>{
    if(!acct.value||!searchIn.value) return;
    fetch(AJAX_URL,{
      method:"POST",
      headers:{"Content-Type":"application/x-www-form-urlencoded","X-CSRFToken":CSRF_TOKEN},
      body:new URLSearchParams({action:"search",account_id:acct.value,query:searchIn.value})
    })
    .then(r=>r.json())
    .then(d=>{
      resList.innerHTML="";
      d.results.forEach(r=>resList.insertAdjacentHTML("beforeend",`<li><b>${r.subject}</b>: ${r.snippet}</li>`));
    });
  };

  sendBtn.onclick=()=>{
    if(!acct.value||!toIn.value) return;
    fetch(AJAX_URL,{
      method:"POST",
      headers:{"Content-Type":"application/x-www-form-urlencoded","X-CSRFToken":CSRF_TOKEN},
      body:new URLSearchParams({action:"send",account_id:acct.value,to:toIn.value,subject:subjIn.value,body:bodyIn.value})
    })
    .then(r=>r.json())
    .then(d=>alert(d.sent?"Sent":"Email sending is not connected yet. Add Gmail/Outlook OAuth + SMTP provider settings."));
  };
});
