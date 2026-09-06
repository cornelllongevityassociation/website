/* Mobile navigation toggle. */
(function () {
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('site-nav');
  if (!toggle || !nav) return;

  var mq = window.matchMedia('(max-width: 900px)');

  function collapse() {
    nav.hidden = true;
    toggle.setAttribute('aria-expanded', 'false');
  }

  function sync() {
    if (mq.matches) {
      collapse();
    } else {
      nav.hidden = false;
      toggle.setAttribute('aria-expanded', 'false');
    }
  }

  toggle.addEventListener('click', function () {
    var open = toggle.getAttribute('aria-expanded') === 'true';
    nav.hidden = open;
    toggle.setAttribute('aria-expanded', String(!open));
  });

  // Close after tapping a link, and whenever we cross the breakpoint.
  nav.addEventListener('click', function (e) {
    if (mq.matches && e.target.closest('a')) collapse();
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && mq.matches && !nav.hidden) {
      collapse();
      toggle.focus();
    }
  });

  mq.addEventListener('change', sync);
  sync();
})();
