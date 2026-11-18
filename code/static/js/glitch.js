// Plays the logo glitch once at the start, then every 30-60 seconds
const g = document.querySelector('.glitch');
if (g && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
  const play = () => { g.classList.add('on'); setTimeout(() => g.classList.remove('on'), 850); };
  const next = () => setTimeout(() => { play(); next(); }, 30000 + Math.random() * 30000);
  setTimeout(play, 3000);
  next();
}
