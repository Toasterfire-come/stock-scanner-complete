(function(){
  try {
    var ATTR = 'data-tradescan-badge';
    var els = document.querySelectorAll('['+ATTR+']');
    if (!els || els.length === 0) return;

    els.forEach(function(el){
      if (el.__tsp_inited) return; el.__tsp_inited = true;
      var symbol = (el.getAttribute('data-symbol') || 'MARKET').toUpperCase();
      var theme = (el.getAttribute('data-theme') || 'light').toLowerCase();
      var bg = theme === 'dark' ? '#0f172a' : '#ffffff';
      var fg = theme === 'dark' ? '#e2e8f0' : '#0f172a';
      var sub = theme === 'dark' ? '#94a3b8' : '#475569';
      var link = 'https://tradescanpro.com/?utm_source=widget&utm_medium=badge&utm_campaign=embed';

      var root = el.attachShadow ? el.attachShadow({ mode: 'open' }) : el;
      var wrap = document.createElement('div');
      wrap.setAttribute('role','img');
      wrap.style.cssText = [
        'font-family: ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Inter,Helvetica,Arial,sans-serif',
        'display:inline-flex;align-items:center;gap:10px;border:1px solid #e5e7eb;border-radius:12px',
        'padding:10px 12px;background:'+bg+';color:'+fg+';box-shadow:0 1px 2px rgba(0,0,0,.04)'
      ].join(';');

      var icon = document.createElement('div');
      icon.innerHTML = '\n        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">\n          <path d="M3 12h3l3-6 4 10 3-6h5" stroke="'+(theme==='dark'?'#60a5fa':'#2563eb')+'" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>\n        </svg>\n      ';
      icon.setAttribute('aria-hidden','true');

      var text = document.createElement('div');
      text.style.cssText = 'display:flex;flex-direction:column;line-height:1.1';
      var t1 = document.createElement('div');
      t1.textContent = symbol + ' • Market Badge';
      t1.style.cssText = 'font-weight:600;font-size:14px;color:'+fg;
      var t2 = document.createElement('a');
      t2.href = link; t2.target = '_blank'; t2.rel = 'noopener';
      t2.textContent = 'Powered by Trade Scan Pro';
      t2.style.cssText = 'font-size:12px;color:'+(theme==='dark'?'#93c5fd':'#1d4ed8')+';text-decoration:none';
      t2.addEventListener('mouseenter', function(){ t2.style.textDecoration = 'underline'; });
      t2.addEventListener('mouseleave', function(){ t2.style.textDecoration = 'none'; });
      text.appendChild(t1); text.appendChild(t2);

      wrap.appendChild(icon); wrap.appendChild(text);
      root.appendChild(wrap);
    });
  } catch(_) { /* no-op */ }
})();

