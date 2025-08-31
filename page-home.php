<?php /* Template Name: Home */ get_header(); ?>
<section class="hero">
  <div class="container" style="display:flex;flex-direction:column;gap:16px;">
    <h1 style="font-size:40px;line-height:1.1;">Retail Trade Scanner</h1>
    <p style="max-width:720px;color:#6b7280;">Scan, screen and monitor markets with professional‑grade tools. Create alerts, manage watchlists and stay on top of opportunities.</p>
    <div style="display:flex;gap:12px;">
      <a class="btn btn-primary" href="<?php echo esc_url(site_url('/auth/sign-up')); ?>"><?php echo esc_html__( 'Start free', 'rts' ); ?></a>
      <a class="btn btn-secondary" href="<?php echo esc_url(site_url('/features')); ?>"><?php echo esc_html__( 'See features', 'rts' ); ?></a>
    </div>
  </div>
</section>
<section class="section">
  <div class="container" style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;">
    <?php $features = [
      ['Powerful Screeners','Filter by price, volume, market cap, fundamentals and more.'],
      ['Real-time Alerts','Get notified when price crosses your target levels.'],
      ['Portfolio & Watchlists','Track positions and monitor symbols in one place.'],
    ]; foreach ($features as $f): ?>
    <div class="card" style="padding:24px;">
      <h3 style="margin:0 0 6px 0; font-size:18px;"><?php echo esc_html($f[0]); ?></h3>
      <p style="color:#6b7280;font-size:14px;"><?php echo esc_html($f[1]); ?></p>
    </div>
    <?php endforeach; ?>
  </div>
</section>
<section class="section" style="background:#fff;">
  <div class="container">
    <h3 style="margin-bottom:12px;">Market highlights</h3>
    <div id="rts-market-highlights" class="card" style="padding:16px;">
      <div class="loading" style="color:#6b7280;">Loading market data…</div>
    </div>
  </div>
</section>
<script>
(function($){
  const card = document.getElementById('rts-market-highlights');
  fetch(RTS.rest.endpoints.market_stats, { headers: { 'X-WP-Nonce': RTS.rest.nonce } })
    .then(r=>r.json()).then(d=>{
      if(!d || !d.data){ card.innerHTML='<div style="color:#6b7280;">No data</div>'; return; }
      const top = (d.data.top_gainers||[]).slice(0,5).map(s=>`<li style=\"display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--border);\"><span style=\"font-weight:600;\">${s.ticker}</span><span style=\"color:#16a34a;\">${(s.change_percent||0).toFixed?.(2)}%</span></li>`).join('');
      card.innerHTML = `<h4 style=\"margin:0 0 8px 0;\">Top gainers</h4><ul style=\"list-style:none;padding:0;margin:0;\">${top}</ul>`;
    }).catch(()=>{ card.innerHTML='<div style="color:#b91c1c;">Failed to load data</div>'; });
})(jQuery);
</script>
<?php get_footer(); ?>