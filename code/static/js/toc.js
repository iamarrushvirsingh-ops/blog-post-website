const links = [...document.querySelectorAll('.toc a')];
const heads = links.map(a => document.getElementById(a.hash.slice(1))).filter(Boolean);
function mark() {
  let cur = heads[0];
  heads.forEach(h => { if (h.getBoundingClientRect().top < 150) cur = h; });
  links.forEach(a => {
    const on = cur && a.hash === '#' + cur.id;
    a.classList.toggle('active', on);
    a.firstElementChild.textContent = on ? '[x]' : '[ ]';
  });
}
if (heads.length) { addEventListener('scroll', mark); mark(); }
