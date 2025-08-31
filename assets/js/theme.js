(function($){
  // Footer subscribe form
  $(document).on('submit', '#rts-subscribe', function(e){
    e.preventDefault(); const email = $(this).find('input[type="email"]').val();
    if(!email) return;
    fetch(RTS.rest.root + 'stock-scanner/v1/subscription', { method: 'POST', headers:{ 'Content-Type':'application/json','X-WP-Nonce': RTS.rest.nonce }, body: JSON.stringify({ email }) })
      .then(r=>r.json()).then(()=> alert('Subscribed'))
      .catch(()=> alert('Subscription failed'));
  });
})(jQuery);