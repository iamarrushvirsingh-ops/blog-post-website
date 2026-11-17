// Moving starfield: drifting, twinkling dots joined by faint lines (paused if the visitor prefers reduced motion)
(() => {
  const c = document.getElementById('bg'); if (!c) return;
  const x = c.getContext('2d');
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const LINK = 130;
  const SPEED = 0.95  // movement speed: 0.4 was the old feel, 0.75 is faster, raise it for more
  let w, h, pts = [];
  function size() {
    const dpr = Math.min(devicePixelRatio || 1, 2);
    w = innerWidth; h = innerHeight;
    c.width = w * dpr; c.height = h * dpr; c.style.width = w + 'px'; c.style.height = h + 'px';
    x.setTransform(dpr, 0, 0, dpr, 0, 0);
    const n = Math.min(Math.round(w * h / 14000), 110);
    pts = Array.from({ length: n }, () => ({
      x: Math.random() * w, y: Math.random() * h, r: Math.random() * 1.4 + .6, ph: Math.random() * 6.28,
      vx: (Math.random() - .5) * SPEED, vy: (Math.random() - .5) * SPEED }));
  }
  function frame(t) {
    x.clearRect(0, 0, w, h);
    for (const p of pts) {
      if (!reduce) { p.x += p.vx; p.y += p.vy; if (p.x < 0 || p.x > w) p.vx *= -1; if (p.y < 0 || p.y > h) p.vy *= -1; }
      x.beginPath(); x.arc(p.x, p.y, p.r, 0, 6.283);
      x.fillStyle = 'rgba(0,229,255,' + (.55 + .35 * Math.sin(t / 800 + p.ph)) + ')'; x.fill();
    }
    for (let i = 0; i < pts.length; i++) for (let j = i + 1; j < pts.length; j++) {
      const a = pts[i], b = pts[j], d = Math.hypot(a.x - b.x, a.y - b.y);
      if (d < LINK) { x.strokeStyle = 'rgba(0,229,255,' + .18 * (1 - d / LINK) + ')'; x.beginPath(); x.moveTo(a.x, a.y); x.lineTo(b.x, b.y); x.stroke(); }
    }
    if (!reduce) requestAnimationFrame(frame);
  }
  addEventListener('resize', () => { size(); if (reduce) frame(0); });
  size(); frame(0);
})();