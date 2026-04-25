document.addEventListener("DOMContentLoaded",()=>{
  const jdSel=document.getElementById("jd-select"),
        cvSel=document.getElementById("cv-select"),
        btn=document.getElementById("compare-btn"),
        resDiv=document.getElementById("results");

  btn.onclick=()=>{
    const jd=jdSel.value,
          cvs=Array.from(cvSel.selectedOptions).map(o=>o.value);
    if(!jd||!cvs.length) return;
    fetch(AJAX_URL,{
      method:"POST",
      headers:{"Content-Type":"application/x-www-form-urlencoded","X-CSRFToken":CSRF_TOKEN},
      body:new URLSearchParams({jd_id:jd,cv_ids:cvs})
    })
    .then(r=>r.json())
    .then(d=>{
      if (d.error) {
        resDiv.textContent = d.error;
        return;
      }
      resDiv.innerHTML = d.results.map(r=>`<div>CV ${r.cv_id}: score ${r.score}</div>`).join("");
    });
  };
});
