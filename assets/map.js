(function () {
  const box = document.querySelector('.world');
  if (!box) return;
  const pts = JSON.parse(box.dataset.points), n = +box.dataset.n, res = +box.dataset.res;
  const runner = box.querySelector('.runner'), fa = runner.querySelector('.fa'), fb = runner.querySelector('.fb');
  const coins = [...box.querySelectorAll('.coin')], blocks = [...box.querySelectorAll('.block')];
  const flag = box.querySelector('.flag'), svg = box.querySelector('svg');
  const GROUND = 140;

  // where the visitor last saw the runner: run from there to the current stop
  let from = n;
  try {
    const s = parseInt(localStorage.getItem('pm100_seen'), 10);
    if (!isNaN(s) && s >= 0 && s < n) from = s;
    localStorage.setItem('pm100_seen', String(n));
  } catch (e) {}

  function place(p) {
    const k = Math.min(p * res, pts.length - 1), i = Math.min(Math.floor(k), pts.length - 2), f = k - i;
    const x = pts[i][0] + f * (pts[i + 1][0] - pts[i][0]), y = pts[i][1] + f * (pts[i + 1][1] - pts[i][1]);
    runner.setAttribute('transform', `translate(${x.toFixed(1)},${y.toFixed(1)})`);
    coins.forEach((c) => c.classList.toggle('got', +c.dataset.i <= p + 0.001));
    blocks.forEach((b) => b.classList.toggle('used', +b.dataset.i <= p + 0.001));
    flag.classList.toggle('down', p >= 100);
    return { x, y };
  }
  function frame(running, t, y) {
    const legsTogether = y < GROUND - 3 || (running && Math.floor(t / 110) % 2 === 1);
    fa.style.display = legsTogether ? 'none' : '';
    fb.style.display = legsTogether ? '' : 'none';
  }
  function reveal(x) {
    const k = svg.clientWidth / 960;
    if (box.scrollWidth > box.clientWidth) box.scrollLeft = Math.max(0, x * k - box.clientWidth / 2);
  }

  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches || from === n) {
    const r = place(n); frame(false, 0, r.y); reveal(r.x); return;
  }
  reveal(place(from).x);
  const dur = Math.min(3600, 450 * (n - from) + 500), t0 = performance.now();
  (function step(now) {
    const k = Math.min(1, (now - t0) / dur);
    const r = place(from + (n - from) * k);
    frame(k < 1, now - t0, r.y);
    reveal(r.x);
    if (k < 1) requestAnimationFrame(step);
  })(t0);
})();
