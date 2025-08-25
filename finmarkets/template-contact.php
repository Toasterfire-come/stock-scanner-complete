<?php /* Template Name: Contact */ if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="section">
  <div class="container content">
    <h1 style="color:var(--navy);">Contact</h1>
    <div class="card" style="padding:20px;">
      <form onsubmit="alert('Submitted (demo)'); return false;" class="grid cols-2">
        <input class="input" placeholder="Your name" />
        <input class="input" type="email" placeholder="Email" />
        <textarea class="input" style="min-height:120px;" placeholder="Message"></textarea>
        <button class="btn btn-primary">Send</button>
      </form>
    </div>
  </div>
</section>
<?php get_footer(); ?>