(function(){
  // Small UI helpers for better polish
  document.addEventListener('DOMContentLoaded', function(){
    // Smooth scroll for in-page anchors
    document.querySelectorAll('a[href^="#"]').forEach(a=>{
      a.addEventListener('click', e=>{
        const id=a.getAttribute('href');
        const el=id && document.querySelector(id);
        if(el){ e.preventDefault(); el.scrollIntoView({ behavior:'smooth', block:'start' }); }
      });
    });
    // Focus ring visibility on keyboard nav only
    function handleFirstTab(e){ if(e.key==='Tab'){ document.body.classList.add('user-is-tabbing'); window.removeEventListener('keydown', handleFirstTab); } }
    window.addEventListener('keydown', handleFirstTab);
  });
})();