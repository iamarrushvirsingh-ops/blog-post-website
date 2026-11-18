const dd = document.querySelector('.dd');
if (dd) {
  const btn = dd.querySelector('button');
  const set = (open) => { dd.classList.toggle('open', open); btn.setAttribute('aria-expanded', open); };
  btn.addEventListener('click', () => set(!dd.classList.contains('open')));
  document.addEventListener('click', (e) => { if (!dd.contains(e.target)) set(false); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') set(false); });
}
