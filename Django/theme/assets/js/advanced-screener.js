(function(){
  const THEME = window.ssTheme || window.stock_scanner_theme || {};
  const lc = 'screenerSavedScreens';
  const api = (action, body={}) => fetch(THEME.ajax_url, {
    method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded'},
    body: new URLSearchParams(Object.assign({ action, nonce: THEME.nonce }, body))
  }).then(r=>r.json());

  // Serialize filters to query safely (client-side only; server validates on use)
  function encodeFilters(filters){
    // Keep benign fields only; do not include user IDs or privileged flags
    const allow = ['marketCaps','minPrice','maxPrice','minVolume','volumeFilter','dayChange','yearPerformance','sectors','technicals','sortBy','page'];
    const safe = {};
    for (const k of allow){ if (filters[k] !== undefined) safe[k]=filters[k]; }
    return btoa(unescape(encodeURIComponent(JSON.stringify(safe))));
  }
  function decodeFilters(str){
    try { return JSON.parse(decodeURIComponent(escape(atob(str)))); } catch(e){ return {}; }
  }

  // Apply URL sync with gating:
  // - Reading filters from URL never grants data access; server checks membership on query execution.
  // - We only apply decoded filters to UI; results still come from secure endpoints.
  window.screenerUrl = {
    write(filters){
      const qs = new URLSearchParams(location.search);
      qs.set('q', encodeFilters(filters));
      const url = location.pathname + '?' + qs.toString();
      history.replaceState(null, '', url);
    },
    read(){
      const qs = new URLSearchParams(location.search);
      const blob = qs.get('q');
      if (!blob) return {};
      const decoded = decodeFilters(blob);
      // Basic sanity cap
      if (decoded && typeof decoded === 'object') return decoded;
      return {};
    }
  };

  // Saved screens via server (membership-gated)
  window.screenerSaved = {
    async list(){
      const res = await api('screener_list_screens');
      if (!res.success) throw new Error(res.data||'Failed');
      return res.data||[];
    },
    async save(name, filters){
      const res = await api('screener_save_screen', { name, payload: encodeFilters(filters) });
      if (!res.success) throw new Error(res.data||'Failed');
      return res.data;
    },
    async get(id){
      const res = await api('screener_get_screen', { id });
      if (!res.success) throw new Error(res.data||'Failed');
      return decodeFilters(res.data.payload||'');
    },
    async remove(id){
      const res = await api('screener_delete_screen', { id });
      if (!res.success) throw new Error(res.data||'Failed');
      return true;
    }
  };
})();