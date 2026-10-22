(function () {
  const $ = (s) => document.querySelector(s);
  const q = $('#q'), out = $('#results');
  if (!q || !out) return;
  const PAGE = 40;
  const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const nice = (s) => String(s).replace(/_/g, ' ');
  const state = { shown: PAGE, filters: { venue: '', year: '', purpose: '', tag: '' } };
  let papers = [], weeks = [], paperIdx, weekIdx;

  Promise.all([fetch('data/papers.json').then((r) => r.json()), fetch('data/weeks.json').then((r) => r.json())]).then(([p, w]) => {
    papers = p; weeks = w;
    const common = { fields: ['title', 'abstract', 'tagText'], storeFields: [], searchOptions: { prefix: true, fuzzy: 0.15, boost: { title: 3 } } };
    papers.forEach((x, i) => { x.n = i; x.tagText = x.tags.map(nice).join(' '); });
    paperIdx = new MiniSearch({ idField: 'n', ...common });
    paperIdx.addAll(papers);
    weekIdx = new MiniSearch({ idField: 'slug', fields: ['title', 'summary', 'text'], searchOptions: { prefix: true, fuzzy: 0.15, boost: { title: 3 } } });
    weekIdx.addAll(weeks);
    buildFilters();
    const init = new URLSearchParams(location.search).get('q');
    if (init) q.value = init;
    render();
  });

  function buildFilters() {
    const box = $('#filters');
    const opts = (key, label, vals) => `<select data-k="${key}"><option value="">${label}</option>${vals.map((v) => `<option value="${esc(v)}">${esc(nice(v))}</option>`).join('')}</select>`;
    const uniq = (f) => [...new Set(papers.map(f))].sort();
    box.innerHTML = opts('venue', 'All venues', uniq((p) => p.venue)) + opts('year', 'All years', uniq((p) => String(p.year)).reverse()) +
      opts('purpose', 'Any purpose', uniq((p) => p.purpose)) + opts('tag', 'Any tag', [...new Set(papers.flatMap((p) => p.tags))].sort());
    box.addEventListener('change', (e) => { state.filters[e.target.dataset.k] = e.target.value; state.shown = PAGE; render(); });
  }

  const passes = (p) => {
    const f = state.filters;
    return (!f.venue || p.venue === f.venue) && (!f.year || String(p.year) === f.year) &&
      (!f.purpose || p.purpose === f.purpose) && (!f.tag || p.tags.includes(f.tag));
  };

  function hl(text, terms) {
    let s = esc(text);
    terms.forEach((t) => { if (t.length > 1) s = s.replace(new RegExp('(' + t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'gi'), '<mark>$1</mark>'); });
    return s;
  }

  function paperHtml(p, terms) {
    const link = p.url ? `<a href="${esc(p.url)}" target="_blank" rel="noopener">${hl(p.title, terms)}</a>` : hl(p.title, terms);
    const chips = p.tags.slice(0, 8).map((t) => `<button class="chip" data-tag="${esc(t)}">${esc(nice(t))}</button>`).join('');
    const abs = p.abstract ? `<p class="abstract clamp">${hl(p.abstract, terms)}</p><button class="more-btn">Show more</button>` : '<p class="abstract muted">No abstract available.</p>';
    return `<div class="result"><h3 style="display:inline">${link}</h3>
      <div class="meta">${esc(p.venue)} ${p.year} · ${esc(nice(p.purpose))} · ${esc(p.relation === 'na' ? '' : nice(p.relation))}</div>${abs}<div class="chips">${chips}</div></div>`;
  }
  function weekHtml(w, terms) {
    return `<div class="result"><span class="kind">Week ${esc(w.week)}</span><h3 style="display:inline"><a href="weeks/${esc(w.slug)}.html">${hl(w.title, terms)}</a></h3>
      <div class="meta">${esc(w.date)}</div><p class="abstract">${hl(w.summary || w.text.slice(0, 240), terms)}</p></div>`;
  }

  function render() {
    const text = q.value.trim();
    const terms = text.split(/\s+/).filter(Boolean);
    let ps, ws = [];
    if (text) {
      ps = paperIdx.search(text, { combineWith: 'AND' }).map((r) => papers[r.id]);
      if (!ps.length) ps = paperIdx.search(text).map((r) => papers[r.id]);
      ws = weekIdx.search(text).map((r) => weeks.find((w) => w.slug === r.id));
    } else {
      ps = papers;
    }
    ps = ps.filter(passes);
    const items = ws.map((w) => weekHtml(w, terms)).concat(ps.slice(0, state.shown).map((p) => paperHtml(p, terms)));
    out.innerHTML = `<p class="count">${ws.length ? ws.length + ' week' + (ws.length > 1 ? 's' : '') + ' · ' : ''}${ps.length.toLocaleString()} paper${ps.length === 1 ? '' : 's'}</p>` + items.join('') +
      (ps.length > state.shown ? '<button class="load">Show more</button>' : '');
  }

  let t;
  q.addEventListener('input', () => { clearTimeout(t); t = setTimeout(() => { state.shown = PAGE; render(); }, 120); });
  out.addEventListener('click', (e) => {
    const c = e.target.closest('.chip'), m = e.target.closest('.more-btn'), l = e.target.closest('.load');
    if (c) { q.value = c.dataset.tag.replace(/_/g, ' '); state.shown = PAGE; render(); q.focus(); }
    if (m) { const a = m.previousElementSibling; const open = a.classList.toggle('clamp'); m.textContent = open ? 'Show more' : 'Show less'; }
    if (l) { state.shown += PAGE; render(); }
  });
})();
