(function () {
  var d = document.documentElement;
  var btn = document.querySelector('.theme');
  if (btn) btn.addEventListener('click', function () {
    var next = d.dataset.theme === 'dark' ? 'light' : 'dark';
    d.dataset.theme = next;
    try { localStorage.setItem('pe-theme', next); } catch (e) {}
  });
  // Chromium marks a mouse-opened select as :focus-visible, so the ring stayed on the language button; show it only after keyboard use.
  document.addEventListener('keydown', function () { d.dataset.kb = '1'; }, true);
  document.addEventListener('pointerdown', function () { delete d.dataset.kb; }, true);
  var langSel = document.querySelector('.lang-select');
  if (langSel) langSel.addEventListener('change', function () { location.href = langSel.value; });
  // The OS setting "reduce motion" switches animations off. For testing it can be overridden: add ?motion=on (or ?motion=off to undo).
  try {
    var mp = new URLSearchParams(location.search).get('motion');
    if (mp === 'on') localStorage.setItem('pe-motion', 'on');
    if (mp === 'off') localStorage.removeItem('pe-motion');
    if (localStorage.getItem('pe-motion') === 'on') d.dataset.motion = 'on';
  } catch (e) {}
  // ---- WhatsApp: yes/no questions first (dialog from gate_html in build.py). Without JavaScript the button stays a plain link.
  var gate = document.getElementById('join-gate');
  if (gate && gate.showModal) {
    document.addEventListener('click', function (e) {
      var a = e.target.closest && e.target.closest('a[data-gate]');
      if (!a) return;
      e.preventDefault();
      [].forEach.call(gate.querySelectorAll('input'), function (i) { i.checked = false; });
      gate.dataset.step = 'ask'; gate.showModal();
    });
    gate.querySelector('.gate-x').addEventListener('click', function () { gate.close(); });
    gate.addEventListener('click', function (e) { if (e.target === gate) gate.close(); });   // click on the backdrop
    gate.querySelector('.gate-go').addEventListener('click', function () {
      var sets = [].slice.call(gate.querySelectorAll('fieldset'));
      if (sets.some(function (f) { return !f.querySelector('input:checked'); })) { gate.dataset.step = 'missing'; return; }
      gate.dataset.step = sets.every(function (f) { return f.querySelector('input:checked').value === f.dataset.a; }) ? 'ok' : 'fail';
      gate.scrollTop = 0;
    });
  }

  // ---- WhatsApp closed (WHATSAPP_OPEN in build.py): the buttons open a note pointing to Discord.
  var waClosed = document.getElementById('wa-closed');
  if (waClosed && waClosed.showModal) {
    document.addEventListener('click', function (e) {
      if (!(e.target.closest && e.target.closest('a[data-wa-closed]'))) return;
      e.preventDefault(); waClosed.showModal();
    });
    waClosed.querySelector('.gate-x').addEventListener('click', function () { waClosed.close(); });
    waClosed.addEventListener('click', function (e) { if (e.target === waClosed) waClosed.close(); });
  }
  // ---- Share: the system's share sheet on touch screens, otherwise the dialog from share_html in build.py with links and the address.
  var box = document.getElementById('share-box');
  if (box && box.showModal) {
    [].forEach.call(document.querySelectorAll('[data-share][hidden]'), function (x) { x.hidden = false; });
    var NETS = { whatsapp: 'https://wa.me/?text={t}%20{u}', x: 'https://x.com/intent/post?text={t}&url={u}',
      facebook: 'https://www.facebook.com/sharer/sharer.php?u={u}', telegram: 'https://t.me/share/url?url={u}&text={t}',
      reddit: 'https://www.reddit.com/submit?url={u}&title={t}', mail: 'mailto:?subject={t}&body={u}' };
    var field = box.querySelector('.share-url'), done = box.querySelector('.share-done');
    document.addEventListener('click', function (e) {
      if (!(e.target.closest && e.target.closest('.share'))) return;
      var u = location.origin + location.pathname, t = box.dataset.text;
      if (navigator.share && matchMedia('(pointer: coarse)').matches) {
        navigator.share({ title: 'Pro Extinction', text: t, url: u }).catch(function () {});
        return;
      }
      [].forEach.call(box.querySelectorAll('[data-net]'), function (a) {
        a.href = NETS[a.dataset.net].replace('{u}', encodeURIComponent(u)).replace('{t}', encodeURIComponent('Pro Extinction: ' + t));
      });
      field.value = u; done.hidden = true; box.showModal();
    });
    box.querySelector('.share-copy button').addEventListener('click', function () {
      field.select();
      var ok = function () { done.hidden = false; };
      if (navigator.clipboard) navigator.clipboard.writeText(field.value).then(ok, function () { if (document.execCommand('copy')) ok(); });
      else if (document.execCommand('copy')) ok();
    });
    box.querySelector('.gate-x').addEventListener('click', function () { box.close(); });
    box.addEventListener('click', function (e) { if (e.target === box) box.close(); });
  }

  // ---- expandable menu below 1000px
  var topBar = document.querySelector('.top'), menuBtn = document.querySelector('.menu-toggle');
  function setTopH() { if (topBar) d.style.setProperty('--top-h', Math.max(0, topBar.getBoundingClientRect().bottom) + 'px'); }
  function closeNav() { d.classList.remove('nav-open'); if (menuBtn) menuBtn.setAttribute('aria-expanded', 'false'); }
  if (menuBtn) {
    menuBtn.addEventListener('click', function () {
      var open = !d.classList.contains('nav-open'); setTopH();
      d.classList.toggle('nav-open', open); menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && d.classList.contains('nav-open')) { closeNav(); menuBtn.focus(); } });
    document.addEventListener('click', function (e) {
      if (!d.classList.contains('nav-open')) return;
      if (e.target.closest('.sitenav a')) { closeNav(); return; }
      if (!e.target.closest('.sitenav') && !e.target.closest('.menu-toggle')) closeNav();
    });
    window.addEventListener('resize', function () { if (window.innerWidth >= 1000) closeNav(); else setTopH(); });
    window.addEventListener('scroll', function () { if (d.classList.contains('nav-open')) setTopH(); }, { passive: true });
  }
  var bar = document.querySelector('.progress i');
  function onScroll() {
    if (!bar) return;
    var h = d.scrollHeight - d.clientHeight;
    bar.style.width = (h > 0 ? Math.min(100, (d.scrollTop / h) * 100) : 0) + '%';
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // ---- scroll-to-top button: shown once the reader is a screen down
  var up = document.querySelector('.to-top');
  function upShow() { if (up) up.classList.toggle('on', (d.scrollTop || document.body.scrollTop) > innerHeight * .8); }
  window.addEventListener('scroll', upShow, { passive: true }); upShow();
  var links = [].slice.call(document.querySelectorAll('.toc a'));
  if (links.length && 'IntersectionObserver' in window) {
    var map = {};
    links.forEach(function (a) { var k = a.getAttribute('href').slice(1); (map[k] = map[k] || []).push(a); });
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting) {
          links.forEach(function (a) { a.removeAttribute('aria-current'); });
          (map[e.target.id] || []).forEach(function (a) { a.setAttribute('aria-current', 'true'); });
        }
      });
    }, { rootMargin: '-15% 0px -75% 0px' });
    [].slice.call(document.querySelectorAll('.prose h2, .prose h3.sub')).forEach(function (h) { io.observe(h); });
  }
  var rail = document.querySelector('.sitenav');
  var railList = rail && rail.querySelector('ul');
  // the scrolling element is the rail itself (A) or just its list inside a bordered card (C); fade only that one
  function railMore() {
    [rail, railList].forEach(function (el) {
      if (!el) return;
      var scrolls = el.scrollHeight - el.clientHeight > 6 && getComputedStyle(el).overflowY !== 'visible';
      var more = scrolls && el.scrollHeight - el.clientHeight - el.scrollTop > 6;
      if (more) el.setAttribute('data-more', ''); else el.removeAttribute('data-more');
    });
  }
  if (rail) {
    [rail, railList].forEach(function (el) { el.addEventListener('scroll', railMore, { passive: true }); });
    window.addEventListener('resize', railMore); railMore();
  }
  var cur = document.querySelector('.sitenav [aria-current=page]');
  if (cur && cur.scrollIntoView && getComputedStyle(cur.parentNode.parentNode).overflowX === 'auto') {
    cur.parentNode.parentNode.scrollLeft = cur.offsetLeft - 16;
  }
})();
