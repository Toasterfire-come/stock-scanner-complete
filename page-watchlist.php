<?php
/**
 * Template Name: Watchlist (v3)
 */
get_header(); ?>
<section class="glass-section">
  <div class="container">
    <header class="section-intro">
      <h1 class="section-title text-gradient"><?php _e('My Watchlist', 'stock-scanner'); ?></h1>
      <p class="section-subtitle"><?php _e('Track your favorite stocks and build your lists', 'stock-scanner'); ?></p>
    </header>

    <div class="hero-actions" style="margin-bottom:1rem">
      <button class="btn btn-primary" data-open-modal="#createWatchlistModal"><?php _e('Create Watchlist', 'stock-scanner'); ?></button>
      <button class="btn btn-outline" data-open-modal="#addStockModal"><?php _e('Add Stock', 'stock-scanner'); ?></button>
      <a class="btn btn-secondary" href="/stock-screener/"><?php _e('Open Screener', 'stock-scanner'); ?></a>
      <a class="btn btn-outline" href="/stock-news/"><?php _e('Market News', 'stock-scanner'); ?></a>
    </div>

    <div id="watchlists-container" data-skeleton>
      <!-- lists render here (frontend-only demo) -->
      <div class="card glass-card scroll-reveal"><div class="card-body"><?php _e('No watchlists yet. Create one to get started.', 'stock-scanner'); ?></div></div>
    </div>
  </div>
</section>

<!-- Create Watchlist Modal -->
<div id="createWatchlistModal" class="modal-overlay" aria-hidden="true" role="dialog">
  <div class="modal-panel">
    <div class="modal-header">
      <h3><?php _e('Create Watchlist', 'stock-scanner'); ?></h3>
      <button class="btn btn-outline btn-sm" data-close-modal>×</button>
    </div>
    <div class="modal-body">
      <form id="create-watchlist-form">
        <label class="form-label" for="watchlist-name"><?php _e('Name', 'stock-scanner'); ?></label>
        <input type="text" id="watchlist-name" class="form-control" placeholder="e.g., Tech Growth" required>
        <label class="form-label" for="watchlist-description" style="margin-top:.75rem"><?php _e('Description', 'stock-scanner'); ?></label>
        <textarea id="watchlist-description" class="form-control" rows="3" placeholder="Optional"></textarea>
      </form>
    </div>
    <div class="modal-footer">
      <button class="btn btn-outline" data-close-modal><?php _e('Cancel', 'stock-scanner'); ?></button>
      <button class="btn btn-primary" onclick="watchlistManager.createWatchlist()"><?php _e('Create', 'stock-scanner'); ?></button>
    </div>
  </div>
</div>

<!-- Add Stock Modal -->
<div id="addStockModal" class="modal-overlay" aria-hidden="true" role="dialog">
  <div class="modal-panel">
    <div class="modal-header">
      <h3><?php _e('Add Stock', 'stock-scanner'); ?></h3>
      <button class="btn btn-outline btn-sm" data-close-modal>×</button>
    </div>
    <div class="modal-body">
      <form id="add-stock-form">
        <label class="form-label" for="target-watchlist-id"><?php _e('Watchlist', 'stock-scanner'); ?></label>
        <select id="target-watchlist-id" class="form-control"></select>
        <div style="display:grid;gap:.75rem;margin-top:.75rem;grid-template-columns:1fr 1fr">
          <div>
            <label class="form-label" for="stock-ticker-add"><?php _e('Ticker', 'stock-scanner'); ?></label>
            <input type="text" id="stock-ticker-add" class="form-control" placeholder="AAPL" maxlength="8" required>
          </div>
          <div style="display:flex;align-items:flex-end">
            <button type="button" class="btn btn-outline w-100" onclick="watchlistManager.useCurrentPrice()"><?php _e('Use Current Price', 'stock-scanner'); ?></button>
          </div>
          <div>
            <label class="form-label" for="added-price"><?php _e('Added Price', 'stock-scanner'); ?></label>
            <input type="number" step="0.01" id="added-price" class="form-control" placeholder="Optional">
          </div>
          <div>
            <label class="form-label" for="target-price"><?php _e('Target Price', 'stock-scanner'); ?></label>
            <input type="number" step="0.01" id="target-price" class="form-control" placeholder="Optional">
          </div>
          <div>
            <label class="form-label" for="stop-loss"><?php _e('Stop Loss', 'stock-scanner'); ?></label>
            <input type="number" step="0.01" id="stop-loss" class="form-control" placeholder="Optional">
          </div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:.75rem;margin-top:.75rem">
          <label style="display:flex;gap:.5rem;align-items:center"><input type="checkbox" id="price-alert-enabled" checked> <?php _e('Enable Price Alerts', 'stock-scanner'); ?></label>
          <label style="display:flex;gap:.5rem;align-items:center"><input type="checkbox" id="news-alert-enabled" checked> <?php _e('Enable News Alerts', 'stock-scanner'); ?></label>
        </div>
        <label class="form-label" for="stock-notes" style="margin-top:.75rem"><?php _e('Notes', 'stock-scanner'); ?></label>
        <textarea id="stock-notes" class="form-control" rows="3" placeholder="Optional notes"></textarea>
      </form>
    </div>
    <div class="modal-footer">
      <button class="btn btn-outline" data-close-modal><?php _e('Cancel', 'stock-scanner'); ?></button>
      <button class="btn btn-primary" onclick="watchlistManager.addStock()"><?php _e('Add Stock', 'stock-scanner'); ?></button>
    </div>
  </div>
</div>

<script>
// Simple modal controller
(function(){
  function open(id){ const m=document.querySelector(id); if(!m) return; m.classList.add('show'); m.setAttribute('aria-hidden','false'); }
  function close(el){ const m=el.closest('.modal-overlay'); m?.classList.remove('show'); m?.setAttribute('aria-hidden','true'); }
  document.addEventListener('click', (e)=>{
    const o=e.target.closest('[data-open-modal]'); if(o){ e.preventDefault(); open(o.getAttribute('data-open-modal')); }
    if(e.target.matches('[data-close-modal]') || e.target.classList.contains('modal-overlay')){ close(e.target); }
  });
})();

// Watchlist Manager (frontend-only demo)
window.watchlistManager = {
  createWatchlist(){
    const name=document.getElementById('watchlist-name').value.trim(); if(!name){ return; }
    const container=document.getElementById('watchlists-container');
    const card=document.createElement('div'); card.className='card glass-card scroll-reveal';
    card.innerHTML='<div class="card-body"><strong>'+name+'</strong><div class="section-subtitle" style="margin-top:.25rem"><?php echo esc_js(__('Empty list', 'stock-scanner')); ?></div></div>';
    container.appendChild(card);
    document.querySelector('#createWatchlistModal [data-close-modal]')?.click();
    showToast('Watchlist "'+name+'" created','success');
  },
  useCurrentPrice(){ showToast('Fetched current price (demo)','info'); },
  addStock(){ showToast('Added stock to watchlist (demo)','success'); document.querySelector('#addStockModal [data-close-modal]')?.click(); }
};
</script>

<?php get_footer(); ?>