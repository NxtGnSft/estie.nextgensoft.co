const dialog = document.getElementById('product-dialog') as HTMLDialogElement;
const cards = Array.from(document.querySelectorAll<HTMLElement>('.card'));
const filter = document.getElementById('material-filter') as HTMLSelectElement;
const count = document.getElementById('result-count')!;
const field = (name: string) => dialog.querySelector<HTMLElement>(`[data-field="${name}"]`)!;

function open(card: HTMLElement) {
  const d = card.dataset;
  for (const k of ['code', 'name', 'material', 'dimensions', 'finish', 'fabric', 'leather']) field(k).textContent = d[k] ?? '';
  for (const k of ['fabric', 'leather']) dialog.querySelectorAll<HTMLElement>(`[data-row="${k}"]`).forEach((el) => (el.hidden = !d[k]));
  const img = card.querySelector('img')!;
  const dimg = field('image') as HTMLImageElement;
  dimg.src = img.currentSrc || img.src; dimg.alt = img.alt;
  (field('wa') as HTMLAnchorElement).href = d.wa!;
  history.replaceState(null, '', `#${card.id}`);
  if (!dialog.open) dialog.showModal();
}

cards.forEach((card) => card.querySelector('.card-open')!.addEventListener('click', () => open(card)));
dialog.addEventListener('close', () => history.replaceState(null, '', location.pathname));
dialog.addEventListener('click', (e) => { if (e.target === dialog) dialog.close(); });
dialog.querySelector('[data-action="copy"]')!.addEventListener('click', async (e) => {
  const btn = e.currentTarget as HTMLButtonElement;
  await navigator.clipboard.writeText(location.href);
  btn.textContent = 'Copied'; setTimeout(() => (btn.textContent = 'Copy link'), 1500);
});

function applyFilter() {
  const v = filter.value;
  let shown = 0;
  for (const c of cards) { const hit = !v || c.dataset.material === v; c.hidden = !hit; if (hit) shown++; }
  count.textContent = `${shown} of ${cards.length}`;
}
filter.addEventListener('change', applyFilter);
applyFilter();

const target = location.hash && document.getElementById(location.hash.slice(1));
if (target?.classList.contains('card')) { target.scrollIntoView({ block: 'center' }); open(target); }
