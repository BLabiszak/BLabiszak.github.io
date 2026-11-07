'use strict';
const themeButton = document.querySelector('.theme-toggle');
function setTheme(dark) {
  document.documentElement.dataset.theme = dark ? 'dark' : 'light';
  themeButton.setAttribute('aria-pressed', String(dark));
  themeButton.setAttribute('aria-label', dark ? 'Use light colour scheme' : 'Use dark colour scheme');
}
let storedTheme;
try { storedTheme = localStorage.getItem('bl-theme'); } catch { /* Storage may be unavailable. */ }
setTheme(storedTheme !== 'light');
themeButton.hidden = false;
themeButton.addEventListener('click', () => {
  const dark = document.documentElement.dataset.theme !== 'dark';
  setTheme(dark);
  try { localStorage.setItem('bl-theme', dark ? 'dark' : 'light'); } catch { /* The current-page toggle still works. */ }
});
const menuButton = document.querySelector('.menu-toggle');
const navigation = document.getElementById('navigation');
const mobile = window.matchMedia('(max-width: 760px)');
function closeMenu() {
  menuButton.setAttribute('aria-expanded', 'false');
  navigation.hidden = mobile.matches;
  // Native hash navigation runs before ResizeObserver after a menu closes.
  const closedHeader = document.querySelector('.site-header');
  if (closedHeader) document.documentElement.style.setProperty('--header-height', `${closedHeader.getBoundingClientRect().height}px`);
}
menuButton.hidden = false;
closeMenu();
mobile.addEventListener('change', closeMenu);
menuButton.addEventListener('click', () => {
  const expanded = menuButton.getAttribute('aria-expanded') === 'true';
  menuButton.setAttribute('aria-expanded', String(!expanded));
  navigation.hidden = expanded;
});
navigation.addEventListener('click', event => { if (event.target.closest('a') && mobile.matches) closeMenu(); });
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && mobile.matches && menuButton.getAttribute('aria-expanded') === 'true') {
    closeMenu(); menuButton.focus();
  }
});
document.getElementById('year').textContent = new Date().getFullYear();

// Match anchor offsets to the actual header, including zoom and an open menu.
const header = document.querySelector('.site-header');
if (header && 'ResizeObserver' in window) {
  new ResizeObserver(() => {
    document.documentElement.style.setProperty('--header-height', `${header.getBoundingClientRect().height}px`);
  }).observe(header);
}

// Only homepage section links participate; the archive keeps aria-current=page.
const sectionLinks = [...navigation.querySelectorAll('a[href^="#"]')]
  .map(link => ({ link, section: document.getElementById(link.hash.slice(1)) }))
  .filter(item => item.section);
if (sectionLinks.length) {
  let pending = false;
  function updateSection() {
    const marker = (header?.getBoundingClientRect().height || 80) + 100;
    let current;
    for (const item of sectionLinks) {
      if (item.section.getBoundingClientRect().top <= marker) current = item;
    }
    if (window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 4) {
      current = sectionLinks[sectionLinks.length - 1];
    }
    for (const item of sectionLinks) {
      if (item === current) item.link.setAttribute('aria-current', 'location');
      else item.link.removeAttribute('aria-current');
    }
    pending = false;
  }
  function scheduleSection() {
    if (!pending) { pending = true; requestAnimationFrame(updateSection); }
  }
  window.addEventListener('scroll', scheduleSection, { passive: true });
  window.addEventListener('resize', scheduleSection);
  window.addEventListener('hashchange', scheduleSection);
  updateSection();
}
