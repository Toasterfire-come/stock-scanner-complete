/**
 * Stock Scanner Theme JavaScript
 * Enhanced functionality for the theme
 */

jQuery(document).ready(function($) {
    // Smooth scroll for anchors
    $('a[href*="#"]').on('click', function(e) {
        const href = $(this).attr('href') || '';
        if (href.startsWith('#')) {
            const target = $(href);
            if (target.length) {
                e.preventDefault();
                $('html, body').stop().animate({ scrollTop: target.offset().top - 100 }, 600);
            }
        }
    });

    // Mobile menu toggle
    if (window.innerWidth <= 768) {
        const nav = $('.main-nav');
        const header = $('.site-header');
        header.prepend('<button class="mobile-menu-toggle" aria-expanded="false" aria-label="Toggle menu">☰</button>');
        $('.mobile-menu-toggle').on('click', function() {
            const open = nav.toggleClass('mobile-active').hasClass('mobile-active');
            $(this).text(open ? '✕' : '☰').attr('aria-expanded', open);
        });
    }

    // Dropdown / mega submenu toggles (click and keyboard)
    $(document).on('click', '.submenu-toggle', function(e){
        e.preventDefault();
        const $btn = $(this);
        const $li = $btn.closest('li');
        const expanded = $li.toggleClass('open').hasClass('open');
        $btn.attr('aria-expanded', expanded);
        const $link = $li.children('a.top-link');
        $link.attr('aria-expanded', expanded);
    });
    // Close on outside click
    $(document).on('click', function(e){
        if (!$(e.target).closest('.main-nav').length) {
            $('.main-nav .open').removeClass('open').find('.submenu-toggle,[aria-expanded]').attr('aria-expanded','false');
        }
    });
    // Keyboard support
    $(document).on('keydown', '.main-nav .menu-item', function(e){
        if (e.key === 'Escape') {
            $(this).removeClass('open').find('.submenu-toggle,[aria-expanded]').attr('aria-expanded','false').blur();
        }
    });

    // Sticky header hide/show on scroll
    let lastScrollTop = 0;
    $(window).on('scroll', function() {
        const scrollTop = $(this).scrollTop();
        const header = $('.site-header');
        if (scrollTop > lastScrollTop && scrollTop > 100) header.addClass('header-hidden'); else header.removeClass('header-hidden');
        lastScrollTop = scrollTop;
    });

    // Animate-in on scroll
    function animateOnScroll() {
        $('.stock-row, .pricing-plan, .watchlist-container, .card').each(function() {
            const t = $(this).offset().top, b = t + $(this).outerHeight();
            const vt = $(window).scrollTop(), vb = vt + $(window).height();
            if (b > vt && t < vb) $(this).addClass('animate-in');
        });
    }
    $(window).on('scroll', animateOnScroll); animateOnScroll();

    // Plan badge fetch
    async function fetchPlanBadge() {
        if (!window.stock_scanner_theme || !stock_scanner_theme.logged_in) return;
        const $badge = $('#plan-badge'); if (!$badge.length) return;
        try {
            const res = await $.post(stock_scanner_theme.ajax_url, { action: 'stock_scanner_get_current_plan', nonce: stock_scanner_theme.nonce });
            if (res && res.success) {
                let plan = null;
                if (res.data && res.data.data && res.data.data.plan) plan = res.data.data.plan; else if (res.data && res.data.plan) plan = res.data.plan;
                let name = 'Free', slug = 'free';
                if (plan && (plan.name || plan.slug)) { name = plan.name || plan.slug; slug = plan.slug || (name || 'free').toLowerCase(); }
                $badge.text(name).removeClass('premium professional gold silver').addClass(slug).attr('title','Billing plan: ' + name);
            } else { $badge.text('Free'); }
        } catch (e) { console.error('Plan badge error', e); }
    }
    fetchPlanBadge();

    // Market status chip
    function updateMarketClock() {
        const now = new Date(); const open = new Date(); const close = new Date();
        open.setHours(9,30,0); close.setHours(16,0,0);
        const isOpen = now >= open && now <= close && now.getDay() >= 1 && now.getDay() <= 5;
        if ($('.market-status').length === 0) {
            $('.user-menu').prepend(`<span class="market-status ${isOpen ? 'open' : 'closed'}">${isOpen ? '🟢 Market Open' : '🔴 Market Closed'}</span>`);
        }
    }
    updateMarketClock(); setInterval(updateMarketClock, 60000);

    // Copy stock symbol on click
    $(document).on('click', '.stock-header h3', function(){
        const s = $(this).text().trim(); if (navigator.clipboard) navigator.clipboard.writeText(s).then(()=>{
            const n = $('<div class="copy-notification">Copied ' + s + '!</div>'); $('body').append(n); setTimeout(()=>{ n.fadeOut(()=>n.remove()); }, 1500);
        });
    });

    // Performance log
    if (performance.mark && performance.measure) {
        performance.mark('theme-js-loaded');
        window.addEventListener('load', function(){ performance.mark('page-loaded'); performance.measure('page-load-time','navigationStart','page-loaded'); });
    }
});

// Inject extra styles
const themeStyles = `
<style>
/* Mobile nav */
@media (max-width: 768px){ .mobile-menu-toggle{display:block;background:none;border:none;color:#111827;font-size:1.5rem;cursor:pointer;padding:.5rem} .main-nav{display:none;position:absolute;top:100%;left:0;right:0;background:#fff;border:1px solid var(--medium-gray);border-radius:12px;box-shadow:var(--shadow-xl);padding:10px;margin:8px} .main-nav.mobile-active{display:block} .main-nav ul{flex-direction:column;gap:.25rem} }

/* Dropdowns */
.main-nav .menu-item{position:relative}
.main-nav .sub-menu{position:absolute; top:calc(100% + 8px); left:0; background:#fff; border:1px solid var(--medium-gray); border-radius:12px; min-width:240px; box-shadow:var(--shadow-xl); opacity:0; transform: translateY(8px); pointer-events:none; transition: all .18s ease; z-index: 1000; padding:6px}
.main-nav .menu-item.open > .sub-menu, .main-nav .menu-item:hover > .sub-menu{opacity:1; transform: translateY(0); pointer-events:auto}
.main-nav .submenu-toggle{background:none;border:none;margin-left:6px;cursor:pointer;line-height:1; padding:6px; border-radius:8px}
.main-nav .submenu-toggle:focus-visible{outline:2px solid #667eea}
.main-nav .submenu-caret{display:inline-block; transition: transform .18s ease}
.main-nav .menu-item.open > .submenu-toggle .submenu-caret{transform: rotate(180deg)}
.main-nav .sub-menu a.sub-link{padding:8px 12px; display:block; border-radius:8px}
.main-nav .sub-menu a.sub-link:hover{background:var(--light-gray)}

/* Mega menu when a top-level item has class "mega" */
.main-nav .menu-item.mega{position:static}
.main-nav .menu-item.mega > .sub-menu{left:50%; transform: translate(-50%, 8px); width:min(1100px, calc(100% - 40px)); padding:16px}
.main-nav .menu-item.mega > .sub-menu{display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap:12px}
.main-nav .menu-item.mega > .sub-menu > li{padding:8px 6px}
.main-nav .menu-item.mega > .sub-menu > li > a{font-weight:600}

/* Animations */
.animate-in{animation: slideInUp .5s ease-out}
@keyframes slideInUp{from{opacity:0;transform:translateY(30px)} to{opacity:1;transform:translateY(0)}}
</style>`;

document.head.insertAdjacentHTML('beforeend', themeStyles);