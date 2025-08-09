(function(){
  window.StockScanner = window.StockScanner || {};
  StockScanner.ready = function(fn){ if(document.readyState!=='loading'){ fn(); } else { document.addEventListener('DOMContentLoaded', fn); } };
})();