(function () {
  const box = document.querySelector('.world');
  if (!box) return;
  const pts = JSON.parse(box.dataset.points), n = +box.dataset.n;
  const runner = box.querySelector('.runner'), fa = runner.querySelector('.fa'), fb = runner.querySelector('.fb');
  const trail = box.querySelector('.trail'), dots = [...box.querySelectorAll('.dot')];
  const svg = box.querySelector('svg');
  const SPRITE_W = 36, SPRITE_H = 42;

  // where the visitor last saw the runner: walk from there to the current stop
  let from = n;
  try {
    const s = parseInt(localStorage.getItem('pm100_seen'), 10);
    if (!isNaN(s) && s >= 0 && s < n) from = s;
    localStorage.setItem('pm100_seen', String(n));
  } catch (e) {}

  let dir = 1;
  function place(p, walking) {
    const i = Math.min(Math.floor(p), 99), f = p - i;
    const a = pts[i], b = pts[i + 1] || pts[i];
    const x = a[0] + f * (b[0] - a[0]), y = a[1] + f * (b[1] - a[1]);
    if (walking && Math.abs(b[0] - a[0]) > 0.5) dir = b[0] >= a[0] ? 1 : -1;
    runner.setAttribute('transform', `translate(${x.toFixed(1)},${y.toFixed(1)}) scale(${dir},1) translate(${-SPRITE_W / 2},${-SPRITE_H + 2})`);
    trail.setAttribute('stroke-dasharray', `${p.toFixed(2)} 200`);
    dots.forEach((d) => d.classList.toggle('read', +d.dataset.i <= p + 0.001));
    return x;
  }
  function frame(walking, t) {
    const b = walking && Math.floor(t / 130) % 2 === 1;
    fa.style.display = b ? 'none' : '';
    fb.style.display = b ? '' : 'none';
  }
  function reveal(x) {
    const k = svg.clientWidth / 960;
    if (box.scrollWidth > box.clientWidth) box.scrollLeft = Math.max(0, x * k - box.clientWidth / 2);
  }

  const still = window.matchMedia('(prefers-reduced-motion: reduce)').matches || from === n;
  if (still) { reveal(place(n, false)); frame(false, 0); return; }
  reveal(place(from, false));
  const dur = Math.min(3000, 500 * (n - from) + 400), t0 = performance.now();
  (function step(now) {
    const k = Math.min(1, (now - t0) / dur), e = k < .5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;
    const x = place(from + (n - from) * e, k < 1);
    frame(k < 1, now - t0);
    reveal(x);
    if (k < 1) requestAnimationFrame(step); else frame(false, 0);
  })(t0);
})();
