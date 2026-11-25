'use strict';
const $ = selector => document.querySelector(selector);
const $$ = selector => [...document.querySelectorAll(selector)];
const movie = $('#movie');
const chapterList = $('#chapter-list');
const screenPlay = $('#screen-play');
let chapters = [], chapterButtons = [], active = -1, pendingTime = null;
let items = [], lookup = new Map(), category = 'all', renderMode = 'icon', expanded = false;
let dialogOpener = null;
const typeColors = ['#d9bbf9','#d0c3b4','#fb9854','#6ebdff','#a1d985','#f6d36e','#a6ebea','#ec9181','#d19ef0','#d7b57d','#b4c9ff','#f7a7c0','#b6d270','#ccb685','#b59bf7','#c19aff','#adadcb','#b4d6e3','#fac1e6'];
const preferred = ['mega_charizardite_x','mega_charizardite_y','mega_mewtwonite_x','mega_mewtwonite_y','mega_delta_meteorite','berry_pecha','mega_venusaurite','mega_blastoisinite'];

function el(tag, className, label) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (label !== undefined) node.textContent = label;
  return node;
}
function clock(t) {
  return `${Math.floor(t / 60)}:${String(Math.floor(t % 60)).padStart(2, '0')}`;
}
function showMovieMessage() {
  const message = $('#movie-message');
  message.replaceChildren(document.createTextNode('Lecture indisponible ici. '));
  const a = el('a', '', 'Ouvrir le MP4');
  a.href = 'media/dojo-v077.mp4';
  a.target = '_blank';
  a.rel = 'noopener';
  message.append(a);
  message.hidden = false;
}
function playAt(time) {
  if (time !== null) {
    if (movie.readyState === 0) pendingTime = time;
    else movie.currentTime = time;
  }
  $('#movie-message').hidden = true;
  movie.play().catch(error => {
    // Cliquer deux fois rapidement ou chercher pendant la lecture peut annuler une promesse.
    if (error.name !== 'AbortError') showMovieMessage();
  });
}
for (const trigger of $$('[data-play]')) trigger.addEventListener('click', () => playAt(trigger === screenPlay ? (movie.ended ? 0 : null) : 0));
$('#restart').addEventListener('click', () => playAt(0));
movie.addEventListener('loadedmetadata', () => {
  if (pendingTime !== null) {
    const time = pendingTime;
    pendingTime = null;
    movie.currentTime = Math.min(time, movie.duration);
  }
});
movie.addEventListener('play', () => { screenPlay.hidden = true; followTime(); });
movie.addEventListener('ended', () => { screenPlay.hidden = false; });
movie.addEventListener('error', showMovieMessage);
movie.addEventListener('timeupdate', followTime);
movie.addEventListener('seeked', followTime);

function setChapter(n, align = false, updateTitle = true) {
  if (!chapters[n]) return;
  if (updateTitle) {
    $('#current-title').textContent = n === 0 ? 'Référence PMDO · Drattak' : `${chapters[n].label} · ${chapters[n].pokemon}`;
    $('#current-sub').textContent = n === 0 ? 'Transition d’origine, avant les 18 types' : `Chapitre ${String(n).padStart(2, '0')} / 18 · ${clock(chapters[n].start)}`;
  }
  if (n !== active) {
    if (chapterButtons[active]) {
      chapterButtons[active].classList.remove('is-current');
      chapterButtons[active].removeAttribute('aria-current');
    }
    active = n;
    chapterButtons[n].classList.add('is-current');
    chapterButtons[n].setAttribute('aria-current', 'true');
  }
  if (align) {
    const button = chapterButtons[n];
    const list = chapterList.getBoundingClientRect();
    const target = button.getBoundingClientRect();
    if (target.top < list.top) chapterList.scrollTop -= list.top - target.top + 3;
    else if (target.bottom > list.bottom) chapterList.scrollTop += target.bottom - list.bottom + 3;
  }
}
function followTime() {
  if (!chapters.length || pendingTime !== null) return;
  const n = Math.max(0, chapters.findLastIndex(chapter => chapter.start <= movie.currentTime + .035));
  if (active !== n || !movie.paused) setChapter(n, active !== n);
}
function loadChapters(data) {
  chapters = data;
  chapterButtons = chapters.map((c, n) => {
    const button = el('button', 'chapter');
    button.type = 'button';
    button.dataset.chapter = n;
    button.style.setProperty('--type-color', typeColors[n]);
    const number = el('span','chap-no', n === 0 ? 'REF' : String(n).padStart(2, '0'));
    const dot = el('span','chap-mark');
    dot.setAttribute('aria-hidden','true');
    const name = el('span','chap-name');
    name.append(el('strong','',c.label), el('small','',c.pokemon));
    button.append(number, dot, name, el('span','chap-time',clock(c.start)));
    button.addEventListener('click', () => {
      setChapter(n, true);
      playAt(c.start === 0 ? 0 : c.start + .012);
    });
    button.addEventListener('keydown', event => {
      const move = { ArrowDown:n + 1, ArrowUp:n - 1, Home:0, End:chapters.length - 1 }[event.key];
      if (move === undefined) return;
      event.preventDefault();
      chapterButtons[Math.max(0, Math.min(chapters.length - 1, move))].focus({ preventScroll:true });
      chapterButtons[Math.max(0, Math.min(chapters.length - 1, move))].scrollIntoView({ block:'nearest', inline:'nearest' });
    });
    return button;
  });
  chapterList.replaceChildren(...chapterButtons);
  $('#part-count').textContent = chapters.length;
  if (movie.currentTime === 0 && movie.paused) setChapter(0, false, false);
  else followTime();
}

const withoutAccents = s => s.normalize('NFD').replace(/\p{M}/gu, '').toLowerCase().replace(/œ/g,'oe');
function kind(item) {
  if (item.category === 'baie') return 'Baie de Réverie';
  if (item.category === 'delta') return 'Météorite Delta · Addon';
  return 'Méga-Gemme · Addon';
}
function getMatches() {
  const words = withoutAccents($('#query').value.trim()).split(/\s+/).filter(Boolean);
  return items.filter(item => (category === 'all' || (category === 'variant' ? item.variant : category === 'mega' ? item.category !== 'baie' : item.category === 'baie'))
    && words.every(word => item.search.includes(word)));
}
function makeItem(item) {
  const button = el('button','item');
  button.type = 'button';
  button.dataset.item = item.id;
  button.title = item.name;
  button.style.setProperty('--item-color', item.color);
  const tile = el('span','item-art');
  const img = new Image(33, 33);
  img.alt = '';
  img.src = item[renderMode];
  tile.append(img);
  const name = el('span','item-name');
  name.append(el('strong','',item.name), el('small','',item.pokemon || 'Baie de Réverie'));
  button.append(tile, name);
  return button;
}
function render() {
  const matches = getMatches();
  const shown = expanded ? matches : matches.slice(0, 8);
  const list = $('#item-list');
  const more = $('#show-more');
  $('#result-count').textContent = `${matches.length} objet${matches.length !== 1 ? 's' : ''}${matches.length > shown.length ? ` · ${shown.length} affichés` : ''}`;
  list.replaceChildren(...(shown.length ? shown.map(makeItem) : [el('p','empty','Aucun objet. Essaie un autre nom ou change de filtre.')]));
  more.hidden = matches.length <= 8;
  more.firstChild.textContent = expanded ? 'Réduire la liste ' : `Voir les ${matches.length} objets `;
  more.setAttribute('aria-expanded', String(expanded));
  more.setAttribute('aria-controls', 'item-list');
}
for (const button of $$('#filters button')) button.addEventListener('click', () => {
  if (!items.length) return;
  category = button.dataset.kind;
  expanded = false;
  for (const other of $$('#filters button')) other.setAttribute('aria-pressed', String(button === other));
  render();
});
for (const button of $$('#modes button')) button.addEventListener('click', () => {
  if (!items.length) return;
  renderMode = button.dataset.view;
  for (const other of $$('#modes button')) other.setAttribute('aria-pressed', String(button === other));
  render();
});
$('#query').addEventListener('input', () => {
  if (!items.length) return;
  expanded = false;
  render();
});
$('#show-more').addEventListener('click', () => {
  expanded = !expanded;
  render();
});

const dialog = $('#item-dialog');
function openItem(button) {
  const item = lookup.get(button.dataset.item);
  if (!item || dialog.open) return;
  dialogOpener = button;
  dialog.style.setProperty('--item-color', item.color);
  $('#dialog-icon').src = item[renderMode];
  $('#dialog-kind').textContent = kind(item);
  $('#dialog-title').textContent = item.name;
  $('#dialog-desc').textContent = item.description;
  const preview = $('#dialog-capture');
  const screenshot = $('#dialog-img');
  preview.hidden = !item.screenshot;
  if (item.screenshot) {
    screenshot.alt = `Capture de l’interface PMDO pour ${item.name}`;
    screenshot.src = item.screenshot;
  } else screenshot.removeAttribute('src');
  dialog.showModal();
}
for (const area of [$('.captures'), $('#item-list')]) area.addEventListener('click', event => {
  const button = event.target.closest('[data-item]');
  if (button) openItem(button);
});
$('#dialog-close').addEventListener('click', () => dialog.close());
dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
dialog.addEventListener('close', () => {
  if (dialogOpener?.isConnected) dialogOpener.focus({ preventScroll: true });
  dialogOpener = null;
});

const nav = $$('.topbar nav a');
let queued = false;
function updateNav() {
  queued = false;
  let section = 'haut';
  for (const id of ['dojo','sac','jouer']) if (document.getElementById(id).getBoundingClientRect().top <= 150) section = id;
  for (const a of nav) {
    const current = a.hash === '#' + section;
    a.classList.toggle('nav-active', current);
    if (current) a.setAttribute('aria-current', 'location');
    else a.removeAttribute('aria-current');
  }
}
window.addEventListener('scroll', () => {
  if (!queued) { queued = true; requestAnimationFrame(updateNav); }
}, { passive:true });
updateNav();

fetch('media/apercu.json').then(result => {
  if (!result.ok) throw Error('Catalogue indisponible');
  return result.json();
}).then(data => {
  loadChapters(data.chapters);
  lookup = new Map(data.items.map(item => [item.id, item]));
  items = [...preferred.map(id => lookup.get(id)).filter(Boolean), ...data.items.filter(item => !preferred.includes(item.id))];
  for (const item of items) item.search = withoutAccents([item.name, item.pokemon, item.id, item.description, item.motif].join(' '));
  render();
}).catch(() => {
  chapterList.replaceChildren(el('p','loading','Chapitres indisponibles. La vidéo peut toujours être lue.'));
  $('#result-count').textContent = 'Catalogue indisponible. Actualise la page pour réessayer.';
});
