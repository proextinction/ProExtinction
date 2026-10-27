(() => {
  // Fits the diagram labels to their boxes (any language or script).
  const fig = document.currentScript.parentNode, svg = fig.querySelector('svg');
  const tree = svg.classList.contains('dg-tree'), MAX = tree ? 270 : 220, BASE = tree ? 20 : 19;
  const fit = (g, label) => {
    const t = g.querySelector('text'), r = g.querySelector('rect'), x = +t.getAttribute('x');
    if (label != null) t.textContent = label;
    t.style.fontSize = '';
    let w = t.getComputedTextLength();
    if (!w) return;   // hidden view: measured again when it shows
    if (w > MAX) { t.style.fontSize = (BASE * MAX / w) + 'px'; w = MAX; }
    w = Math.max(120, w + 36);
    r.setAttribute('width', w); r.setAttribute('x', x - w / 2);
    if (!tree) r.setAttribute('rx', r.getAttribute('height') / 2);
  };
  const shrink = (t, max, base, label) => {   // headings and verdict: one line, smaller font when too wide
    if (!t) return;
    if (label != null) t.textContent = label;
    t.style.fontSize = '';
    const w = t.getComputedTextLength();
    if (w > max) t.style.fontSize = (base * max / w) + 'px';
  };
  const fitAll = () => {
    svg.querySelectorAll('.node').forEach(g => fit(g));
    shrink(svg.querySelector('.dg-heading'), 600, 52);
    shrink(svg.querySelector('.verdict'), 600, 30);
    svg.querySelectorAll('.center').forEach(t => shrink(t, 270, 40));
  };
  fitAll();
  // cycle: a box lights up exactly when the red dot reaches it. Both read the SVG's own clock (the dot is SMIL, 6 s a lap,
  // nodes at 0, 2 and 4 s), so they stay in step even after the view was hidden or the tab was in the background.
  if (!tree && svg.getCurrentTime) {
    const d = document.documentElement;
    if (matchMedia('(prefers-reduced-motion: reduce)').matches && d.dataset.motion !== 'on') svg.pauseAnimations();
    else {
      const nodes = svg.querySelectorAll('.node');
      let on = true;
      const tick = () => {
        if (on) {
          const t = svg.getCurrentTime() % 6;
          nodes.forEach((g, i) => g.classList.toggle('lit', ((t - 2 * i) % 6 + 6) % 6 < .45));
        }
        requestAnimationFrame(tick);
      };
      if (window.IntersectionObserver) new IntersectionObserver(es => { on = es.some(e => e.isIntersecting); }).observe(svg);
      requestAnimationFrame(tick);
    }
  }
  if (document.fonts) document.fonts.ready.then(fitAll);
  if (window.IntersectionObserver) new IntersectionObserver(es => es.some(e => e.isIntersecting) && fitAll()).observe(svg);
})();
