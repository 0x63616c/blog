/* Contents rail on posts: follows the reader, and folds away on small screens. */
(function () {
  'use strict';
  var rail = document.querySelector('.rail');
  if (!rail) return;
  var box = rail.querySelector('details');
  var wide = window.matchMedia('(min-width: 961px)');
  function fit() { box.open = wide.matches; }
  fit();
  if (wide.addEventListener) wide.addEventListener('change', fit); else wide.addListener(fit);

  var links = Array.prototype.slice.call(rail.querySelectorAll('a'));
  var heads = links.map(function (a) { return document.getElementById(a.getAttribute('href').slice(1)); });
  function setCurrent(i) {
    links.forEach(function (a, k) {
      if (k === i) a.setAttribute('aria-current', 'location'); else a.removeAttribute('aria-current');
    });
  }
  function spot() {
    var cur = -1, line = window.innerHeight * 0.3;
    heads.forEach(function (h, k) { if (h && h.getBoundingClientRect().top <= line) cur = k; });
    setCurrent(cur);
  }
  var tick = false;
  window.addEventListener('scroll', function () {
    if (tick) return; tick = true;
    window.requestAnimationFrame(function () { tick = false; spot(); });
  }, { passive: true });
  spot();
})();
