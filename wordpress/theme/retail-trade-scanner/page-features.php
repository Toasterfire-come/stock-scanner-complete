<?php /* Template Name: Features */ get_header(); ?>
<section class="section">
  <div class="container">
    <h1>Features</h1>
    <div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin-top:16px;">
      <?php $items = [
        ['Advanced Scanner','Build complex queries with price, volume, valuation and momentum filters.'],
        ['Alerts','Price crosses, percent moves, volume spikes and more delivered via email.'],
        ['Watchlists','Organize symbols with notes and targets.'],
        ['Portfolio','Track cost basis, P/L and exposure.'],
      ]; foreach ($items as $it): ?>
      <div class="card" style="padding:24px;">
        <h3 style="margin:0 0 6px 0; font-size:18px;"><?php echo esc_html($it[0]); ?></h3>
        <p style="color:#6b7280;font-size:14px;"><?php echo esc_html($it[1]); ?></p>
      </div>
      <?php endforeach; ?>
    </div>
  </div>
</section>
<?php get_footer(); ?>