/**
 * Stock Scanner Theme JavaScript
 * Client-side cookies + session data popover + clear cache
 */

jQuery(document).ready(function($) {
    const cfg = window.stock_scanner_theme || {};
    const isLoggedIn = !!cfg.logged_in;
    const userId = cfg.user_id || 0;
    const planKey = userId ? `ssc_plan_info_${userId}` : null;
    const loginKey = 'ssc_logged_in_user';
    const activityKey = 'ssc_last_activity';
    const idleEnabled = cfg.idle_enabled !== undefined ? !!cfg.idle_enabled : true;
    const idleLimitMs = (cfg.idle_limit_ms && Number(cfg.idle_limit_ms)) ? Number(cfg.idle_limit_ms) : 12 * 60 * 60 * 1000;
    const warnThresholdMs = (cfg.warn_threshold_ms && Number(cfg.warn_threshold_ms)) ? Number(cfg.warn_threshold_ms) : 2 * 60 * 1000;

    // Cookie helpers
    function setCookie(name, value, ms){ try{ const d=new Date(Date.now()+ms); document.cookie = `${name}=${encodeURIComponent(value)}; expires=${d.toUTCString()}; path=/; SameSite=Lax`; }catch(e){} }
    function getCookie(name){ const parts = document.cookie.split(';').map(s=>s.trim()); for (const p of parts){ if (!p) continue; const i=p.indexOf('='); const k = i>-1? p.slice(0,i):p; if (k===name){ return decodeURIComponent(i>-1? p.slice(i+1):''); } } return null; }
    function delCookie(name){ try{ document.cookie = `${name}=; Max-Age=0; path=/; SameSite=Lax`; }catch(e){} }

    // Time helpers
    function markActivity(){ localStorage.setItem(activityKey, String(Date.now())); if (idleEnabled) setCookie('ssc_last_activity', String(Date.now()), idleLimitMs + 5*60*1000); }
    function getLastActivity(){ const v = localStorage.getItem(activityKey); return v ? parseInt(v, 10) : 0; }
    function remainingMs(){ const last = getLastActivity(); if (!last) return idleLimitMs; const d = idleLimitMs - (Date.now() - last); return d < 0 ? 0 : d; }
    function fmt(ms){ let s = Math.floor(ms/1000); const h = Math.floor(s/3600); s -= h*3600; const m = Math.floor(s/60); s -= m*60; const pad = (n)=> (n<10? '0'+n : String(n)); if (h>0) return `${pad(h)}:${pad(m)}`; else return `${pad(m)}:${pad(s)}`; }

    // Session timer UI
    const $timer = $('#session-timer');
    function updateTimerBadge(){ if (!$timer.length || !isLoggedIn || !idleEnabled) return; const ms = remainingMs(); $timer.text(fmt(ms)); }

    // Mobile menu toggle
    if (window.innerWidth <= 768) {
        const nav = $('.main-nav'); const header = $('.site-header');
        header.prepend('<button class="mobile-menu-toggle" aria-expanded="false" aria-label="Toggle menu">☰</button>');
        $('.mobile-menu-toggle').on('click', function() { const open = nav.toggleClass('mobile-active').hasClass('mobile-active'); $(this).text(open ? '✕' : '☰').attr('aria-expanded', open); });
    }

    // Dropdown / mega submenu toggles
    $(document).on('click', '.submenu-toggle', function(e){ e.preventDefault(); const $btn=$(this), $li=$btn.closest('li'); const expanded = $li.toggleClass('open').hasClass('open'); $btn.attr('aria-expanded', expanded); $li.children('a.top-link').attr('aria-expanded', expanded); });
    $(document).on('click', function(e){ if (!$(e.target).closest('.main-nav').length) { $('.main-nav .open').removeClass('open').find('.submenu-toggle,[aria-expanded]').attr('aria-expanded','false'); } });
    $(document).on('keydown', '.main-nav .menu-item', function(e){ if (e.key === 'Escape') { $(this).removeClass('open').find('.submenu-toggle,[aria-expanded]').attr('aria-expanded','false').blur(); } });

    // Idle logout behavior + warning modal
    function shouldLogout(){ return remainingMs() === 0; }
    let warningShown = false;
    function ensureWarningModal(){ if ($('#session-warning-modal').length) return; const html = `
      <div id="session-warning-modal" class="session-modal hidden" role="dialog" aria-modal="true" aria-labelledby="session-modal-title">
        <div class="session-modal-backdrop"></div>
        <div class="session-modal-panel" role="document">
          <h3 id="session-modal-title">You are about to be signed out</h3>
          <p>You've been inactive for a while. You'll be signed out soon for your security. Do you want to stay signed in?</p>
          <div class="session-modal-actions">
            <button id="stay-signed-in" class="btn btn-primary"><span>Stay signed in</span></button>
            <button id="sign-out-now" class="btn btn-secondary"><span>Sign out now</span></button>
          </div>
        </div>
      </div>`; $('body').append(html); $('#stay-signed-in').on('click', function(){ markActivity(); hideWarning(); warningShown=false; updateTimerBadge(); }); $('#sign-out-now').on('click', function(){ if (cfg.logout_url) window.location.assign(cfg.logout_url); }); $(document).on('keydown.sessionmodal', function(e){ if (e.key==='Escape') hideWarning(); }); }
    function showWarning(){ ensureWarningModal(); const $m=$('#session-warning-modal'); $m.removeClass('hidden').addClass('visible'); $('#stay-signed-in').focus(); }
    function hideWarning(){ const $m=$('#session-warning-modal'); $m.removeClass('visible').addClass('hidden'); }

    if (isLoggedIn && idleEnabled) {
        if (shouldLogout()) { if (cfg.logout_url) window.location.assign(cfg.logout_url); }
        else {
            ['click','keydown','mousemove','scroll','touchstart','visibilitychange'].forEach(ev => { window.addEventListener(ev, function(){ if (document.visibilityState !== 'hidden') { markActivity(); updateTimerBadge(); } }, { passive: true }); });
            if (!getLastActivity()) markActivity();
            updateTimerBadge();
            setInterval(function(){ const ms = remainingMs(); updateTimerBadge(); if (ms <= Math.min(warnThresholdMs, idleLimitMs/2) && ms > 0 && !warningShown) { showWarning(); warningShown=true; } if (ms === 0 && cfg.logout_url) { window.location.assign(cfg.logout_url); } }, 1000);
        }
    } else if (!isLoggedIn) { try { localStorage.removeItem(activityKey); localStorage.removeItem(loginKey); } catch(e){} }

    // Plan badge + Refresh Plan link
    const $planBadge = $('#plan-badge');
    const $refreshLink = $('#refresh-plan');

    function setPlanBadge(name, slug){ if (!$planBadge.length) return; name = name || 'Free'; slug = (slug || name || 'Free').toLowerCase(); $planBadge.text(name).removeClass('premium professional gold silver free').addClass(slug).attr('title','Billing plan: '+name); }
    function loadPlanFromCache(){ if (!planKey) return null; try { const raw = localStorage.getItem(planKey); return raw ? JSON.parse(raw) : null; } catch(e){ return null; } }
    function savePlanToCache(plan){ if (!planKey) return; try { localStorage.setItem(planKey, JSON.stringify({ plan, t: Date.now() })); setCookie('ssc_plan', `${plan.slug}:${Date.now()}`, 24*60*60*1000); } catch(e){} }
    function clearPlanCache(){ if (!planKey) return; try { localStorage.removeItem(planKey); delCookie('ssc_plan'); } catch(e){} }
    function fetchPlanAndRender(){ if (!$planBadge.length) return; return $.post(cfg.ajax_url, { action: 'stock_scanner_get_current_plan', nonce: cfg.nonce })
        .done(function(res){ let plan=null; if (res && res.success) { if (res.data && res.data.data && res.data.data.plan) plan=res.data.data.plan; else if (res.data && res.data.plan) plan=res.data.plan; } const name=(plan && (plan.name||plan.slug))?(plan.name||plan.slug):'Free'; const slug=(plan && (plan.slug||plan.name))?(plan.slug||plan.name).toLowerCase():'free'; setPlanBadge(name, slug); savePlanToCache({ name, slug }); setCookie('ssc_login_user', String(userId||''), 7*24*60*60*1000); })
        .fail(function(){ const c = loadPlanFromCache(); if (c && c.plan) setPlanBadge(c.plan.name, c.plan.slug); else setPlanBadge('Free','free'); }); }

    if (isLoggedIn) {
        const prevUser = localStorage.getItem(loginKey);
        const isNewLogin = String(userId || '') !== String(prevUser || '');
        if (isNewLogin) { fetchPlanAndRender(); localStorage.setItem(loginKey, String(userId || '')); setCookie('ssc_login_user', String(userId||''), 7*24*60*60*1000); }
        else { const cached = loadPlanFromCache(); if (cached && cached.plan) setPlanBadge(cached.plan.name, cached.plan.slug); else setPlanBadge('Free','free'); }
    } else { try { localStorage.removeItem(loginKey); delCookie('ssc_login_user'); delCookie('ssc_plan'); delCookie('ssc_last_activity'); } catch(e){} }

    // Alt key reveal for Refresh Plan
    let altDown = false;
    $(document).on('keydown', function(e){ if (e.altKey) { if (!altDown) { altDown = true; $refreshLink.addClass('visible'); } } });
    $(document).on('keyup', function(e){ if (!e.altKey) { altDown = false; $refreshLink.removeClass('visible'); } });
    $refreshLink.on('click', function(e){ e.preventDefault(); if (!isLoggedIn) return; clearPlanCache(); fetchPlanAndRender(); $refreshLink.removeClass('visible'); });

    // Session policy popover
    function buildPolicyText(){ const enabled = (cfg.idle_enabled !== undefined) ? !!cfg.idle_enabled : true; const hours = cfg.idle_limit_ms ? Math.max(1, Math.round(Number(cfg.idle_limit_ms)/(60*60*1000))) : 12; if (enabled) return `For your security, you will be signed out automatically after ${hours} hour${hours===1?'':'s'} of inactivity. You will receive a 2-minute warning to stay signed in.`; return 'Auto-logout after inactivity is currently disabled on this site.'; }
    function ensurePolicyPopover(){ if ($('#session-policy-popover').length) return; const html = `<div id="session-policy-popover" role="dialog" aria-live="polite" class="policy-popover hidden"><div class="policy-popover-arrow"></div><div class="policy-popover-content"></div></div>`; $('body').append(html); }
    function togglePolicyPopover(target){ ensurePolicyPopover(); const $p=$('#session-policy-popover'); const $c=$p.find('.policy-popover-content'); $c.text(buildPolicyText()); const rect=target.getBoundingClientRect(); const top=window.scrollY + rect.bottom + 10; const left=window.scrollX + rect.left + (rect.width/2) - 160; $p.css({ top: top + 'px', left: Math.max(12,left) + 'px' }).toggleClass('hidden visible'); }
    $(document).on('click', '#session-policy-link', function(e){ e.preventDefault(); togglePolicyPopover(this); });
    $(document).on('click', function(e){ if (!$(e.target).closest('#session-policy-popover, #session-policy-link').length) { $('#session-policy-popover').removeClass('visible').addClass('hidden'); } });

    // Session data popover (cookies + cache)
    function ensureDataPopover(){ if ($('#session-data-popover').length) return; const html = `<div id=\"session-data-popover\" role=\"dialog\" aria-live=\"polite\" class=\"policy-popover hidden\"><div class=\"policy-popover-arrow\"></div><div class=\"policy-popover-content\"></div></div>`; $('body').append(html); }
    function renderDataContent(){ const lines=[]; const cookieNames=['wordpress_logged_in','ssc_login_user','ssc_last_activity','ssc_plan']; const cookies = document.cookie.split(';').map(s=>s.trim()).filter(Boolean); function hasPrefix(name){ return cookies.some(c => c.startsWith(name + '=')); }
        lines.push(`wordpress_logged_in: ${hasPrefix('wordpress_logged_in') ? 'present' : 'missing'}`);
        lines.push(`ssc_login_user: ${getCookie('ssc_login_user') || 'not set'}`);
        const la = getCookie('ssc_last_activity'); lines.push(`ssc_last_activity: ${la ? new Date(parseInt(la,10)).toLocaleString() : 'not set'}`);
        const sp = getCookie('ssc_plan'); lines.push(`ssc_plan: ${sp || 'not set'}`);
        const lsPlan = planKey ? localStorage.getItem(planKey) : null; lines.push(`localStorage plan: ${lsPlan ? 'present' : 'missing'}`);
        return '<pre style="white-space:pre-wrap;margin:0;">' + lines.join('\n') + '</pre>'; }
    function toggleDataPopover(target){ ensureDataPopover(); const $p=$('#session-data-popover'); const $c=$p.find('.policy-popover-content'); $c.html(renderDataContent()); const rect=target.getBoundingClientRect(); const top=window.scrollY + rect.bottom + 10; const left=window.scrollX + rect.left + (rect.width/2) - 160; $p.css({ top: top + 'px', left: Math.max(12,left) + 'px' }).toggleClass('hidden visible'); }
    $(document).on('click', '#session-data-link', function(e){ e.preventDefault(); toggleDataPopover(this); });
    $(document).on('click', function(e){ if (!$(e.target).closest('#session-data-popover, #session-data-link').length) { $('#session-data-popover').removeClass('visible').addClass('hidden'); } });

    // Clear session data link
    $(document).on('click', '#clear-session-data', function(e){ e.preventDefault(); if (!confirm('Clear cached session data (plan cache and activity markers)?')) return; try { if (planKey) localStorage.removeItem(planKey); localStorage.removeItem(activityKey); delCookie('ssc_plan'); delCookie('ssc_last_activity'); } catch(err){} markActivity(); const c = getCookie('ssc_plan'); setPlanBadge('Free','free'); alert('Cleared. Some data may repopulate on next sign-in.'); });
});

// Inject styles for policy/session popovers and utility links
(function(){
  const css = `
  <style>
    .session-policy-link,.session-data-link,.clear-session-data{margin-left:8px;font-size:.85rem;text-decoration:underline;color:#334155;opacity:.85}
    .session-policy-link:hover,.session-data-link:hover,.clear-session-data:hover{opacity:1}
    .policy-popover{position:absolute;z-index:10001;width:320px;background:#fff;border:1px solid var(--medium-gray);border-radius:12px;box-shadow:var(--shadow-2xl);padding:12px}
    .policy-popover.hidden{display:none}
    .policy-popover.visible{display:block}
    .policy-popover-arrow{position:absolute;top:-8px;left:50%;transform:translateX(-50%);width:16px;height:16px;background:#fff;border-left:1px solid var(--medium-gray);border-top:1px solid var(--medium-gray);transform: translateX(-50%) rotate(45deg)}
    .policy-popover-content{font-size:.9rem;color:#475569}
  </style>`;
  document.head.insertAdjacentHTML('beforeend', css);
})();