<?php /* Template Name: Market Overview */ if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="section">
  <div class="container grid cols-3">
    <div class="card" style="padding:16px;">
      <h3>Indices</h3>
      <ul>
        <li>S&amp;P 500 <span class="badge badge-green">+0.6%</span></li>
        <li>Nasdaq <span class="badge badge-green">+1.1%</span></li>
        <li>Dow Jones <span class="badge badge-red">-0.2%</span></li>
      </ul>
    </div>
    <div class="card" style="padding:16px;">
      <h3>Sectors</h3>
      <ul>
        <li>Tech <span class="badge badge-green">+1.4%</span></li>
        <li>Energy <span class="badge badge-green">+0.8%</span></li>
        <li>Healthcare <span class="badge badge-red">-0.3%</span></li>
      </ul>
    </div>
    <div class="card" style="padding:16px;">
      <h3>Movers</h3>
      <ul>
        <li class="mono">NVDA</li>
        <li class="mono">AAPL</li>
        <li class="mono">TSLA</li>
      </ul>
    </div>
  </div>
</section>
<?php get_footer(); ?>