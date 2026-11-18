document.querySelectorAll('form[data-confirm]').forEach(f =>
  f.addEventListener('submit', e => { if (!confirm(f.dataset.confirm)) e.preventDefault(); }));
const ed = document.getElementById('editor');
if (ed) {
  const body = document.getElementById('body'), pv = document.getElementById('preview');
  let t;
  const run = () => fetch(ed.dataset.preview, {
    method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRF': ed.dataset.csrf },
    body: JSON.stringify({ body: body.value })
  }).then(r => r.json()).then(j => { pv.innerHTML = j.html; });  // html is cleaned by the server
  body.addEventListener('input', () => { clearTimeout(t); t = setTimeout(run, 400); });
  run();
}
