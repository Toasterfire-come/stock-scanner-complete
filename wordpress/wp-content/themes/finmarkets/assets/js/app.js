(function(){
  const $ = (sel, root=document) => root.querySelector(sel);
  const $$ = (sel, root=document) => Array.from(root.querySelectorAll(sel));
  const fmt = new Intl.NumberFormat(undefined, { style: 'currency', currency: 'USD', maximumFractionDigits: 2 });
  const getWL = () => JSON.parse(localStorage.getItem('finm_wl') || '[]');
  const setWL = (arr) => localStorage.setItem('finm_wl', JSON.stringify(arr));

  function renderPreview(){
    const tbody = $('#previewBody');
    if(!tbody || !window.MockData) return;
    tbody.innerHTML = (window.MockData.stocks||[]).slice(0,6).map(s => `
      <tr>
        <td class="mono symbol-cell" data-symbol="${s.symbol}">${s.symbol}</td>
        <td>${s.name}</td>
        <td>${fmt.format(s.price)}</td>
        <td>${s.change >= 0 ? `<span class="badge badge-green">+${s.change}%</span>` : `<span class="badge badge-red">${s.change}%</span>`}</td>
      </tr>`).join('');
  }

  function uniqueSectors(){
    if(!window.MockData || !window.MockData.stocks) return;
    const sectors = Array.from(new Set(window.MockData.stocks.map(s => s.sector)));
    const sel = $('#sector');
    if(!sel) return;
    sel.innerHTML = [`<option value="all">All sectors</option>`, ...sectors.map(x => `<option value="${x}">${x}</option>`)].join('');
  }

  function renderScreener(){
    if(!window.MockData || !window.MockData.stocks) return;
    const q = $('#q')?.value?.trim().toLowerCase() || '';
    const sector = $('#sector')?.value || 'all';
    const body = $('#screenerBody'); if(!body) return;
    const wl = new Set(getWL());
    let rows = window.MockData.stocks.filter(s => {
      const matchText = (s.symbol||'').toLowerCase().includes(q) || (s.name||'').toLowerCase().includes(q);
      const matchSector = sector === 'all' || s.sector === sector;
      return matchText && matchSector;
    });
    if($('#sortPrice')){
      if($('#sortPrice').dataset.dir === 'asc') rows.sort((a,b) => a.price - b.price);
      if($('#sortPrice').dataset.dir === 'desc') rows.sort((a,b) => b.price - a.price);
    }
    body.innerHTML = rows.map(s => {
      const inWl = wl.has(s.symbol);
      return `
        <tr>
          <td class="mono symbol-cell" data-symbol="${s.symbol}">${s.symbol}</td>
          <td>${s.name}</td>
          <td>${s.sector}</td>
          <td>${fmt.format(s.price)}</td>
          <td>${s.change >= 0 ? `<span class="badge badge-green">+${s.change}%</span>` : `<span class="badge badge-red">${s.change}%</span>`}</td>
          <td><button class="btn ${inWl ? 'btn-success' : ''}" data-symbol="${s.symbol}">${inWl ? 'Added' : 'Add'}</button></td>
        </tr>`;
    }).join('');
  }

  function bindScreener(){
    const q = $('#q'); const sector = $('#sector'); const sort = $('#sortPrice');
    if(!q || !sector || !sort) return;
    q.addEventListener('input', renderScreener);
    sector.addEventListener('change', renderScreener);
    sort.addEventListener('click', () => {
      const dir = sort.dataset.dir;
      sort.dataset.dir = dir === 'asc' ? 'desc' : (dir === 'desc' ? '' : 'asc');
      sort.setAttribute('aria-pressed', sort.dataset.dir ? 'true' : 'false');
      renderScreener();
    });
    $('#screenerBody').addEventListener('click', async (e) => {
      const symCell = e.target.closest('.symbol-cell');
      if(symCell && window.finmApi){ try { await window.finmApi.usageTrack('view', symCell.dataset.symbol); } catch(_){} }
      const btn = e.target.closest('button[data-symbol]');
      if(!btn) return;
      const sym = btn.getAttribute('data-symbol');
      const wl = new Set(getWL());
      if(wl.has(sym)) wl.delete(sym); else wl.add(sym);
      setWL(Array.from(wl));
      renderScreener();
      renderWatchlist();
      if(window.finmApi){ try { await window.finmApi.usageTrack('watchlist_add', sym); } catch(_){} }
    });
  }

  function renderWatchlist(){
    const list = $('#watchlistItems');
    if(!list || !window.MockData || !window.MockData.stocks) return;
    const wl = new Set(getWL());
    const items = window.MockData.stocks.filter(s => wl.has(s.symbol));
    list.innerHTML = items.map(s => `<li style="display:flex; justify-content:space-between; align-items:center; padding:8px; border-bottom:1px solid var(--gray-200);"><span class="mono">${s.symbol}</span> <span>${fmt.format(s.price)}</span></li>`).join('') || '<li class="muted">No symbols yet. Add from the Screener.</li>';
  }

  function renderNews(){
    const grid = $('#newsGrid');
    if(!grid || !window.MockData) return;
    grid.innerHTML = (window.MockData.news||[]).slice(0,6).map(n => `
      <article class="card" style="padding:14px;">
        <div class="badge">${n.source}</div>
        <h4 style="margin:8px 0; color:var(--navy);">${n.title}</h4>
        <div class="muted">${n.time}</div>
      </article>`).join('');
  }

  function loginDemo(){
    const btn = $('#loginBtn');
    if(!btn) return;
    btn.addEventListener('click', () => {
      const name = prompt('Enter any name to simulate login (stored locally):');
      if(!name) return;
      localStorage.setItem('finm_user', JSON.stringify({ name }));
      btn.textContent = 'Signed in';
    });
    try { const u = JSON.parse(localStorage.getItem('finm_user')||'null'); if(u){ btn.textContent = 'Signed in'; } } catch(e){}
  }

  function refreshAll(){ renderPreview(); uniqueSectors(); renderScreener(); renderWatchlist(); renderNews(); }

  document.addEventListener('DOMContentLoaded', function(){
    if(!window.MockData){ console.warn('Mock data not loaded'); return; }
    bindScreener();
    refreshAll();
    loginDemo();
  });

  document.addEventListener('finm:api-ready', function(){ refreshAll(); });

  // Global unauthorized handler
  window.addEventListener('finm:unauthorized', function(){ try { localStorage.removeItem('finm_user'); }catch(_){} window.location.href = '/login/?next=' + encodeURIComponent(location.pathname + location.search); });
})();