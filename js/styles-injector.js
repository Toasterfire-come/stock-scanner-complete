/**
 * Stock Scanner Pro - CSS via Vanilla JS Injector (conversion v6.1)
 * Refined brand palettes; remove micro-survey styles; keep cohesive theme styling.
 */
(function(){
  'use strict';

  const css = `
:root { --color-primary:#667eea; --color-secondary:#764ba2; --gradient-primary: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%); --gradient-hero: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); --color-text:#1f2937; --color-text-muted:#6b7280; --color-white:#fff; --color-bg:#fff; --color-bg-light:#f9fafb; --color-bg-lighter:#f3f4f6; --color-surface:#ffffff; --color-border:#e5e7eb; --space-2:.5rem; --space-3:.75rem; --space-4:1rem; --space-6:1.5rem; --space-8:2rem; --space-16:4rem; --radius-lg:.5rem; --radius-xl:.75rem; --radius-2xl:1rem; --z-dropdown:1000; --z-sticky:1020; }
[data-theme="dark"]{ --color-text:#f9fafb; --color-text-muted:#9ca3af; --color-bg:#111827; --color-bg-light:#1f2937; --color-bg-lighter:#374151; --color-surface:#111827; --color-border:#374151; }

/* Refined brand palettes */
html[data-accent="emerald"]{--color-primary:#10b981;--color-secondary:#059669;--gradient-primary:linear-gradient(135deg,#10b981 0%,#059669 100%);--gradient-hero:linear-gradient(135deg,#10b981 0%,#059669 50%,#34d399 100%)}
html[data-accent="amber"]{--color-primary:#f59e0b;--color-secondary:#d97706;--gradient-primary:linear-gradient(135deg,#f59e0b 0%,#d97706 100%);--gradient-hero:linear-gradient(135deg,#f59e0b 0%,#d97706 50%,#fbbf24 100%)}
html[data-accent="violet"]{--color-primary:#8b5cf6;--color-secondary:#6d28d9;--gradient-primary:linear-gradient(135deg,#8b5cf6 0%,#6d28d9 100%);--gradient-hero:linear-gradient(135deg,#8b5cf6 0%,#6d28d9 50%,#a78bfa 100%)}
html[data-accent="indigo"]{--color-primary:#6366f1;--color-secondary:#4338ca;--gradient-primary:linear-gradient(135deg,#6366f1 0%,#4338ca 100%);--gradient-hero:linear-gradient(135deg,#6366f1 0%,#4338ca 50%,#a78bfa 100%)}
html[data-accent="teal"]{--color-primary:#14b8a6;--color-secondary:#0d9488;--gradient-primary:linear-gradient(135deg,#14b8a6 0%,#0d9488 100%);--gradient-hero:linear-gradient(135deg,#14b8a6 0%,#0d9488 50%,#2dd4bf 100%)}
html[data-accent="cyan"]{--color-primary:#06b6d4;--color-secondary:#0891b2;--gradient-primary:linear-gradient(135deg,#06b6d4 0%,#0891b2 100%);--gradient-hero:linear-gradient(135deg,#06b6d4 0%,#0891b2 50%,#22d3ee 100%)}
html[data-accent="rose"]{--color-primary:#f43f5e;--color-secondary:#be123c;--gradient-primary:linear-gradient(135deg,#f43f5e 0%,#be123c 100%);--gradient-hero:linear-gradient(135deg,#f43f5e 0%,#be123c 50%,#fb7185 100%)}
html[data-accent="slate"]{--color-primary:#64748b;--color-secondary:#334155;--gradient-primary:linear-gradient(135deg,#64748b 0%,#334155 100%);--gradient-hero:linear-gradient(135deg,#64748b 0%,#334155 50%,#94a3b8 100%)}
html[data-accent="orange"]{--color-primary:#f97316;--color-secondary:#ea580c;--gradient-primary:linear-gradient(135deg,#f97316 0%,#ea580c 100%);--gradient-hero:linear-gradient(135deg,#f97316 0%,#ea580c 50%,#fdba74 100%)}
html[data-accent="fuchsia"]{--color-primary:#d946ef;--color-secondary:#a21caf;--gradient-primary:linear-gradient(135deg,#d946ef 0%,#a21caf 100%);--gradient-hero:linear-gradient(135deg,#d946ef 0%,#a21caf 50%,#e879f9 100%)}

/* Base & header/nav */
body{font-family:'Inter',system-ui,-apple-system,'Segoe UI',Roboto,Arial,sans-serif;color:var(--color-text);background:var(--color-bg-light)}
.container{max-width:1200px;margin:0 auto;padding:0 1rem}
.header-container{display:flex;align-items:center;justify-content:space-between;gap:1rem;padding:.75rem 1rem}
.main-navigation{display:flex;align-items:center}
.enhanced-nav{display:flex;gap:.75rem;list-style:none;margin:0;padding:0}
.enhanced-nav a{display:inline-flex;align-items:center;gap:.25rem;padding:.5rem .75rem;border-radius:.5rem;color:inherit;text-decoration:none}
.enhanced-nav a:hover{background:var(--color-bg-lighter)}
.menu-toggle{display:none}
@media(max-width:768px){ .menu-toggle{display:inline-flex;align-items:center;justify-content:center;width:40px;height:40px;border-radius:999px} .main-navigation{position:absolute;top:100%;left:0;right:0;display:none;flex-direction:column;gap:.25rem;background:var(--color-bg);border-bottom:1px solid var(--color-border);box-shadow:0 8px 24px rgba(0,0,0,.08);z-index:var(--z-dropdown);padding:.5rem} .main-navigation.mobile-active{display:flex} }

/* Buttons */
.btn{display:inline-flex;align-items:center;justify-content:center;gap:.5rem;padding:.75rem 1.25rem;border:2px solid transparent;border-radius:1rem;cursor:pointer;text-decoration:none;transition:.2s}
.btn-primary{background:var(--gradient-primary);color:#fff}
.btn-outline{background:transparent;color:var(--color-primary);border-color:var(--color-primary)}
.btn-secondary{background:var(--color-surface);color:var(--color-text);border-color:var(--color-border)}
.btn-sm{padding:.5rem .875rem;border-radius:.5rem;font-size:.875rem}
.btn-lg{padding:1rem 1.5rem;border-radius:1.25rem;font-size:1.125rem}

/* Sections/cards */
.glass-section{padding:var(--space-16) 0}
.section-intro{text-align:center;margin-bottom:var(--space-8)}
.section-title{font-size:2rem;font-weight:800;margin:0 0 .25rem}
.section-subtitle{color:var(--color-text-muted);max-width:800px;margin:0 auto}
.features-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1.25rem}
.card{border:1px solid var(--color-border);border-radius:var(--radius-2xl);background:var(--color-surface);box-shadow:0 1px 3px rgba(0,0,0,.06)}
.card-body{padding:var(--space-6)}

/* Carousel */
.carousel{position:relative;overflow:hidden}
.carousel-track{display:flex;transition:transform .35s ease}
.carousel-item{flex:0 0 100%; padding:.5rem}
.carousel-dots{display:flex;gap:.35rem;justify-content:center;margin-top:.5rem}
.carousel-dot{width:8px;height:8px;border-radius:999px;background:var(--color-border);cursor:pointer}
.carousel-dot.active{background:var(--color-primary)}

/* Pricing toggle */
.pricing-toggle{display:flex;align-items:center;gap:.5rem;justify-content:center;padding:.5rem;border:1px solid var(--color-border);border-radius:999px}
.toggle-switch{position:relative;width:52px;height:28px;border-radius:999px;border:1px solid var(--color-border);background:var(--color-bg);cursor:pointer}
.toggle-switch .toggle-slider{position:absolute;top:2px;left:2px;width:24px;height:24px;border-radius:999px;background:var(--color-primary);transition:left .2s}
.toggle-switch.active .toggle-slider{left:26px}
.savings-badge{display:inline-flex;align-items:center;gap:.25rem;padding:.2rem .5rem;border-radius:999px;background:rgba(16,185,129,.15);color:#065f46;font-size:.75rem}

/* Search overlay */
.search-overlay{position:fixed;inset:0;background:rgba(0,0,0,.5);display:none;align-items:center;justify-content:center;z-index:var(--z-sticky)}
.search-overlay.show{display:flex}
.search-container{position:relative;width:min(760px,95vw)}
.search-input-group{display:flex;gap:.5rem;align-items:center;background:var(--color-surface);border:1px solid var(--color-border);border-radius:var(--radius-2xl);padding:.35rem .5rem}
.search-field{flex:1;border:0;background:transparent;color:inherit;padding:.5rem 1rem;outline:none}
.search-submit{display:inline-flex;align-items:center;justify-content:center;width:44px;height:44px;border:0;border-radius:999px;background:var(--gradient-primary);color:#fff;cursor:pointer}

/* Table helpers */
.table-responsive{overflow-x:auto}
[data-sortable] th{cursor:pointer}
.badge-yes{background:rgba(16,185,129,.15);color:#065f46;padding:.125rem .5rem;border-radius:999px;font-size:.75rem}
.badge-no{background:rgba(239,68,68,.15);color:#7f1d1d;padding:.125rem .5rem;border-radius:999px;font-size:.75rem}

/* Sticky CTA & Loading bar */
.sticky-cta{position:fixed;left:0;right:0;bottom:0;z-index:var(--z-sticky);background:var(--color-surface);border-top:1px solid var(--color-border);padding:.5rem 1rem;display:none;align-items:center;justify-content:center;gap:.5rem}
.sticky-cta.show{display:flex}
.page-loading-bar{position:fixed;top:0;left:0;height:3px;width:0;background:var(--gradient-primary);z-index:var(--z-sticky)}

/* Footer */
.site-footer{background:linear-gradient(135deg,#1f2937 0%,#374151 100%);color:#fff;margin-top:2rem}
.footer-container{padding:2rem 1rem}
.footer-widgets{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1.25rem}
.footer-menu{list-style:none;display:grid;gap:.35rem;padding:0;margin:0}
.footer-menu a{color:#e5e7eb;text-decoration:none}
.footer-menu a:hover{text-decoration:underline}
`;

  let styleEl = document.getElementById('stock-scanner-styles');
  if(!styleEl){ styleEl=document.createElement('style'); styleEl.id='stock-scanner-styles'; styleEl.type='text/css'; document.head.appendChild(styleEl); }
  styleEl.textContent = css;
})();