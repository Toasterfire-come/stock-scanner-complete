/**
 * Stock Scanner Theme JavaScript
 * Enhanced functionality + session & plan badge behavior + countdown + modal warn + admin-config idle policy + plan refresh
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

    // Time helpers
    function markActivity(){ localStorage.setItem(activityKey, String(Date.now())); }
    function getLastActivity(){ const v = localStorage.getItem(activityKey); return v ? parseInt(v, 10) : 0; }
    function remainingMs(){ const last = getLastActivity(); if (!last) return idleLimitMs; const d = idleLimitMs - (Date.now() - last); return d < 0 ? 0 : d; }
    function fmt(ms){ let s = Math.floor(ms/1000); const h = Math.floor(s/3600); s -= h*3600; const m = Math.floor(s/60); s -= m*60; const pad = (n)=> (n<10? '0'+n : String(n)); if (h>0) return `${pad(h)}:${pad(m)}`; else return `${pad(m)}:${pad(s)}`; }

    // Session timer UI
    const $timer = $('#session-timer');
    function updateTimerBadge(){ if (!$timer.length || !isLoggedIn || !idleEnabled) return; const ms = remainingMs(); $timer.text(fmt(ms)); }

    // Smooth scroll for anchors
    $('a[href^="#"]').on('click', function(e) {
        const href = $(this).attr('href');
        const target = $(href);
        if (target.length) { e.preventDefault(); $('html, body').animate({ scrollTop: target.offset().top - 100 }, 600); }
    });

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

    // Idle logout behavior
    function shouldLogout(){ return remainingMs() === 0; }

    // Warning modal 2 minutes before logout
    let warningShown = false;
    function ensureWarningModal(){
        if ($('#session-warning-modal').length) return;
        const html = `
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
        </div>`;
        $('body').append(html);
        $('#stay-signed-in').on('click', function(){ markActivity(); hideWarning(); warningShown = false; updateTimerBadge(); });
        $('#sign-out-now').on('click', function(){ if (cfg.logout_url) window.location.assign(cfg.logout_url); });
        $(document).on('keydown.sessionmodal', function(e){ if (e.key==='Escape') hideWarning(); });
    }
    function showWarning(){ ensureWarningModal(); const $m = $('#session-warning-modal'); $m.removeClass('hidden').addClass('visible'); $('#stay-signed-in').focus(); }
    function hideWarning(){ const $m=$('#session-warning-modal'); $m.removeClass('visible').addClass('hidden'); }

    if (isLoggedIn && idleEnabled) {
        if (shouldLogout()) {
            if (cfg.logout_url) window.location.assign(cfg.logout_url);
        } else {
            ['click','keydown','mousemove','scroll','touchstart','visibilitychange'].forEach(ev => { window.addEventListener(ev, function(){ if (document.visibilityState !== 'hidden') { markActivity(); updateTimerBadge(); } }, { passive: true }); });
            if (!getLastActivity()) markActivity();
            updateTimerBadge();
            setInterval(function(){ const ms = remainingMs(); updateTimerBadge(); if (ms <= Math.min(warnThresholdMs, idleLimitMs/2) && ms > 0 && !warningShown) { showWarning(); warningShown = true; } if (ms === 0 && cfg.logout_url) { window.location.assign(cfg.logout_url); } }, 1000);
        }
    } else if (!isLoggedIn) {
        try { localStorage.removeItem(activityKey); localStorage.removeItem(loginKey); } catch(e){}
    }

    // Plan badge + Refresh Plan link (Alt to reveal)
    const $planBadge = $('#plan-badge');
    const $refreshLink = $('#refresh-plan');

    function setPlanBadge(name, slug){ if (!$planBadge.length) return; name = name || 'Free'; slug = (slug || name || 'Free').toLowerCase(); $planBadge.text(name).removeClass('premium professional gold silver free').addClass(slug).attr('title','Billing plan: '+name); }
    function loadPlanFromCache(){ if (!planKey) return null; try { const raw = localStorage.getItem(planKey); return raw ? JSON.parse(raw) : null; } catch(e){ return null; } }
    function savePlanToCache(plan){ if (!planKey) return; try { localStorage.setItem(planKey, JSON.stringify({ plan, t: Date.now() })); } catch(e){} }
    function clearPlanCache(){ if (!planKey) return; try { localStorage.removeItem(planKey); } catch(e){} }
    function fetchPlanAndRender(){ if (!$planBadge.length) return; return $.post(cfg.ajax_url, { action: 'stock_scanner_get_current_plan', nonce: cfg.nonce })
        .done(function(res){ let plan=null; if (res && res.success) { if (res.data && res.data.data && res.data.data.plan) plan=res.data.data.plan; else if (res.data && res.data.plan) plan=res.data.plan; } const name=(plan && (plan.name||plan.slug))?(plan.name||plan.slug):'Free'; const slug=(plan && (plan.slug||plan.name))?(plan.slug||plan.name).toLowerCase():'free'; setPlanBadge(name, slug); savePlanToCache({ name, slug }); })
        .fail(function(){ const c = loadPlanFromCache(); if (c && c.plan) setPlanBadge(c.plan.name, c.plan.slug); else setPlanBadge('Free','free'); }); }

    if (isLoggedIn) {
        const prevUser = localStorage.getItem(loginKey);
        const isNewLogin = String(userId || '') !== String(prevUser || '');
        if (isNewLogin) {
            fetchPlanAndRender();
            localStorage.setItem(loginKey, String(userId || ''));
        } else {
            const cached = loadPlanFromCache(); if (cached && cached.plan) setPlanBadge(cached.plan.name, cached.plan.slug); else setPlanBadge('Free','free');
        }
    } else { try { localStorage.removeItem(loginKey); } catch(e){} }

    // Alt key reveal for Refresh Plan
    let altDown = false;
    $(document).on('keydown', function(e){ if (e.altKey) { if (!altDown) { altDown = true; $refreshLink.addClass('visible'); } } });
    $(document).on('keyup', function(e){ if (!e.altKey) { altDown = false; $refreshLink.removeClass('visible'); } });

    $refreshLink.on('click', function(e){ e.preventDefault(); if (!isLoggedIn) return; clearPlanCache(); fetchPlanAndRender(); $refreshLink.removeClass('visible'); });

    // Market status chip
    function updateMarketClock() { const now=new Date(); const open=new Date(); const close=new Date(); open.setHours(9,30,0); close.setHours(16,0,0); const isOpen = now>=open && now<=close && now.getDay()>=1 && now.getDay()<=5; if ($('.market-status').length===0) { $('.user-menu').prepend(`<span class="market-status ${isOpen ? 'open' : 'closed'}">${isOpen ? '🟢 Market Open' : '🔴 Market Closed'}</span>`); } }
    updateMarketClock(); setInterval(updateMarketClock, 60000);

    // Copy stock symbol on click
    $(document).on('click', '.stock-header h3', function(){ const s=$(this).text().trim(); if (navigator.clipboard) navigator.clipboard.writeText(s).then(()=>{ const n=$('<div class="copy-notification">Copied ' + s + '!</div>'); $('body').append(n); setTimeout(()=>{ n.fadeOut(()=>n.remove()); }, 1500); }); });

    // Performance markers
    if (performance.mark && performance.measure) { performance.mark('theme-js-loaded'); window.addEventListener('load', function(){ performance.mark('page-loaded'); performance.measure('page-load-time','navigationStart','page-loaded'); }); }
});

// Styles for dropdowns, mega-menu, session timer & modal are injected elsewhere