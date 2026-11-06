'use strict';
// Progressive enhancement: without JavaScript every paper is simply listed.
(() => {
  const panel = document.querySelector('.pub-filters');
  const list = document.getElementById('pub-list');
  if (!panel || !list) return;
  const items = [...list.querySelectorAll('.publication')];
  const chips = [...panel.querySelectorAll('.chip')];
  const search = panel.querySelector('input[type=search]');
  const firstOnly = panel.querySelector('.first-toggle input');
  const count = panel.querySelector('.pub-count');
  const empty = document.querySelector('.pub-empty');
  let topic = '';

  function apply() {
    const q = search.value.trim().toLowerCase();
    let shown = 0;
    for (const el of items) {
      const ok = (!topic || el.dataset.topics.split(' ').includes(topic))
        && (!firstOnly.checked || el.dataset.first === 'true')
        && (!q || el.dataset.search.includes(q));
      el.hidden = !ok;
      if (ok) shown++;
    }
    count.textContent = shown === items.length ? `${shown} articles` : `${shown} of ${items.length} articles`;
    empty.hidden = shown !== 0;
  }

  chips.forEach(chip => chip.addEventListener('click', () => {
    topic = chip.dataset.topic;
    chips.forEach(c => c.setAttribute('aria-pressed', String(c === chip)));
    apply();
  }));
  search.addEventListener('input', apply);
  firstOnly.addEventListener('change', apply);

  // Copy button inside each BibTeX block
  if (navigator.clipboard) {
    for (const block of list.querySelectorAll('.cite pre')) {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'copy';
      btn.textContent = 'Copy';
      btn.addEventListener('click', async () => {
        try {
          await navigator.clipboard.writeText(block.textContent);
          btn.textContent = 'Copied';
        } catch { btn.textContent = 'Select & copy'; }
        setTimeout(() => { btn.textContent = 'Copy'; }, 1600);
      });
      block.after(btn);
    }
  }

  panel.hidden = false;
  apply();
})();
