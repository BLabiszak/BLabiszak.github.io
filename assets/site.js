'use strict';
const themeButton = document.querySelector('.theme-toggle');
function setTheme(dark) {
  document.documentElement.dataset.theme = dark ? 'dark' : 'light';
  themeButton.setAttribute('aria-pressed', String(dark));
  themeButton.setAttribute('aria-label', dark ? 'Use light colour scheme' : 'Use dark colour scheme');
}
let storedTheme;
try { storedTheme = localStorage.getItem('bl-theme'); } catch { /* Storage may be unavailable. */ }
setTheme(storedTheme === 'dark');
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
