/**
 * Stock Scanner Theme JavaScript (adds session policy popover)
 */

jQuery(document).ready(function($) {
    const cfg = window.stock_scanner_theme || {};

    // Create session policy popover
    function buildPolicyText(){
        const enabled = (cfg.idle_enabled !== undefined) ? !!cfg.idle_enabled : true;
        const hours = cfg.idle_limit_ms ? Math.max(1, Math.round(Number(cfg.idle_limit_ms)/(60*60*1000))) : 12;
        if (enabled) return `For your security, you will be signed out automatically after ${hours} hour${hours===1?'':'s'} of inactivity. You will receive a 2-minute warning to stay signed in.`;
        return 'Auto-logout after inactivity is currently disabled on this site.';
    }

    function ensurePolicyPopover(){
        if ($('#session-policy-popover').length) return;
        const html = `
          <div id="session-policy-popover" role="dialog" aria-live="polite" class="policy-popover hidden">
            <div class="policy-popover-arrow"></div>
            <div class="policy-popover-content"></div>
          </div>`;
        $('body').append(html);
    }

    function togglePolicyPopover(target){
        ensurePolicyPopover();
        const $p = $('#session-policy-popover');
        const $c = $p.find('.policy-popover-content');
        $c.text(buildPolicyText());
        const rect = target.getBoundingClientRect();
        const top = window.scrollY + rect.bottom + 10;
        const left = window.scrollX + rect.left + (rect.width/2) - 160; // center approx (320px width)
        $p.css({ top: top + 'px', left: Math.max(12, left) + 'px' }).toggleClass('hidden visible');
    }

    $(document).on('click', '#session-policy-link', function(e){ e.preventDefault(); togglePolicyPopover(this); });
    $(document).on('click', function(e){ if (!$(e.target).closest('#session-policy-popover, #session-policy-link').length) { $('#session-policy-popover').removeClass('visible').addClass('hidden'); } });
});

// Inject minimal styles for policy popover and link
(function(){
  const css = `
  <style>
    .session-policy-link{margin-left:8px;font-size:.85rem;text-decoration:underline;color:#334155;opacity:.85}
    .session-policy-link:hover{opacity:1}
    .policy-popover{position:absolute;z-index:10001;width:320px;background:#fff;border:1px solid var(--medium-gray);border-radius:12px;box-shadow:var(--shadow-2xl);padding:12px}
    .policy-popover.hidden{display:none}
    .policy-popover.visible{display:block}
    .policy-popover-arrow{position:absolute;top:-8px;left:50%;transform:translateX(-50%);width:16px;height:16px;background:#fff;border-left:1px solid var(--medium-gray);border-top:1px solid var(--medium-gray);transform: translateX(-50%) rotate(45deg)}
    .policy-popover-content{font-size:.9rem;color:#475569}
  </style>`;
  document.head.insertAdjacentHTML('beforeend', css);
})();