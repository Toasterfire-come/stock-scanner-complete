<?php /* Template Name: Design System */ get_header(); ?>
<section class="section"><div class="container">
  <h1>Design System</h1>
  <p style="color:#6b7280;">Tokens and components used across the app.</p>
  <div class="grid" style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;">
    <?php $tokens = ['--background'=>'Background','--foreground'=>'Foreground','--accent'=>'Accent (Coral)','--secondary'=>'Secondary (Blue)','--muted'=>'Muted','--border'=>'Border']; foreach ($tokens as $var=>$name): ?>
      <div class="card" style="padding:16px;">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;"><div style="font-weight:600;"><?php echo esc_html($name); ?></div><code style="font-size:12px;"><?php echo esc_html($var); ?></code></div>
        <div style="height:64px;border-radius:10px;border:1px solid var(--border);background:hsl(var(<?php echo esc_html($var); ?>));"></div>
      </div>
    <?php endforeach; ?>
  </div>
  <div class="grid" style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin-top:16px;">
    <div class="card" style="padding:16px;">
      <div style="font-weight:600;">Buttons</div>
      <div style="display:flex;gap:8px;margin-top:8px;">
        <button class="btn btn-primary">Primary</button>
        <button class="btn btn-secondary">Secondary</button>
        <button class="btn btn-outline">Outline</button>
      </div>
    </div>
    <div class="card" style="padding:16px;">
      <div style="font-weight:600;">Inputs</div>
      <div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin-top:8px;">
        <input class="input" placeholder="Text" />
        <input class="input" placeholder="Number" type="number" />
        <select class="input"><option>Option</option></select>
        <input class="input" placeholder="With ring focus" />
      </div>
    </div>
  </div>
</div></section>
<?php get_footer(); ?>