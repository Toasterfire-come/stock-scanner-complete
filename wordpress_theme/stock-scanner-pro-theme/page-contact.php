<?php
/**
 * Template Name: Contact
 */
get_header(); ?>
<div class="contact-page">
  <div class="container" style="max-width:800px;margin:40px auto;padding:0 20px;">
    <h1>Contact Us</h1>
    <div class="card" style="padding:24px;">
      <p>Have questions? Send us a message and we’ll get back within 1-2 business days.</p>
      <form onsubmit="event.preventDefault(); alert('Thanks! Your message has been received.'); this.reset();">
        <div style="display:grid;gap:12px;">
          <input type="text" name="name" placeholder="Your name" required />
          <input type="email" name="email" placeholder="Your email" required />
          <textarea name="message" rows="5" placeholder="How can we help?" required></textarea>
          <button class="btn btn-primary" type="submit">Send Message</button>
        </div>
      </form>
    </div>
  </div>
</div>
<?php get_footer(); ?>