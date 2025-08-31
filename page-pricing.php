<?php /* Template Name: Pricing */ get_header(); ?>
<section class="section"><div class="container">
  <h1>Pricing</h1>
  <div class="grid" style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin-top:16px;">
    <?php $plans = [ ['Free','$0',['Basic screener','Community templates','Email support']], ['Pro','$19/mo',['Realtime alerts','Portfolio & watchlists','Priority support']], ['Enterprise','Contact',['SLA','Custom integrations','Dedicated support']] ]; foreach ($plans as $p): ?>
      <div class="card" style="padding:24px;">
        <h3 style="margin:0;"><?php echo esc_html($p[0]); ?></h3>
        <p style="font-family:Poppins,Inter,sans-serif;font-size:28px;margin:4px 0 0 0;"><?php echo esc_html($p[1]); ?></p>
        <ul style="margin:12px 0 0 16px;">
          <?php foreach ($p[2] as $f): ?><li style="color:#6b7280;font-size:14px;"><?php echo esc_html('• '.$f); ?></li><?php endforeach; ?>
        </ul>
        <a href="#" class="btn btn-primary" style="display:block;margin-top:16px;text-align:center;">Choose <?php echo esc_html($p[0]); ?></a>
      </div>
    <?php endforeach; ?>
  </div>
</div></section>
<?php get_footer(); ?>