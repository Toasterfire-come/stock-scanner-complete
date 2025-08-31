<?php /* Template Name: Contact */ get_header(); ?>
<section class="section"><div class="container">
  <h1>Contact</h1>
  <div class="grid" style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;">
    <div class="card" style="padding:16px;">
      <form id="rts-contact" style="display:flex;flex-direction:column;gap:12px;">
        <div><label>Name</label><input class="input" name="name" /></div>
        <div><label>Email</label><input class="input" name="email" type="email" /></div>
        <div><label>Message</label><textarea class="input" name="message" style="min-height:120px"></textarea></div>
        <button class="btn btn-primary">Send</button>
      </form>
    </div>
    <div class="card" style="padding:16px;">
      <h3>Support</h3>
      <p style="color:#6b7280;font-size:14px;">Email us at support@example.com or use the form.</p>
      <div id="rts-contact-result" style="margin-top:8px;color:#16a34a;display:none;">Thanks! We will get back to you shortly.</div>
    </div>
  </div>
</div></section>
<script>
(function(){ document.getElementById('rts-contact').addEventListener('submit', function(e){ e.preventDefault(); document.getElementById('rts-contact-result').style.display='block'; }); })();
</script>
<?php get_footer(); ?>