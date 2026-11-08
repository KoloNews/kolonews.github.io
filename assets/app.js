/* Коло Новин — логіка сайту */
(() => {
  'use strict';

  // ---------------------------------------------------------------- тексти інтерфейсу
  const LANGS = [
    { code: 'uk', short: 'УКР', name: 'Українська' },
    { code: 'en', short: 'ENG', name: 'English' },
    { code: 'zh', short: '中文', name: '中文' },
    { code: 'ru', short: 'РУС', name: 'Русский' },
  ];

  const T = {
    uk: {
      world: 'Світ', eurasia: 'Європа і Азія', countries: 'Країни', us: 'США', cn: 'Китай', ua: 'Україна', ru: 'Росія',
      worldSub: 'Головне за 24 години',
      stories: { one: 'історія', few: 'історії', many: 'історій', other: 'історії' },
      sources: { one: 'джерело', few: 'джерела', many: 'джерел', other: 'джерела' },
      in24: 'за 24 години', updated: 'Оновлено', top: 'Головне', readAt: 'Читати на', whatSources: 'Що пишуть джерела',
      empty: 'За останні 24 години новин у цій категорії немає', error: 'Не вдалося завантажити новини. Перевірте, чи запущено сервер.',
      retry: 'Спробувати ще', refresh: 'Оновити', theme: 'Змінити тему', close: 'Закрити', language: 'Мова',
      fresh: (n) => `Нових історій: ${n}`, upToDate: 'Новини актуальні',
      note: (n) => `Джерел: ${n}, 4 мовами. Переклад — Google Translate.`, justNow: 'щойно',
      back: 'Назад', related: 'Більше новин', photo: 'Фото', prev: 'Попереднє фото', next: 'Наступне фото',
      gone: 'Цієї новини вже немає: вона старша за 24 години.',
      machine: 'Машинний переклад', original: 'оригінал', showOrig: 'Показати оригінал', showTr: 'Показати переклад',
      noTr: 'Переклад тимчасово недоступний — показано оригінал', origLang: 'Оригінал',
    },
    en: {
      world: 'World', eurasia: 'Europe & Asia', countries: 'Countries', us: 'USA', cn: 'China', ua: 'Ukraine', ru: 'Russia',
      worldSub: 'Top stories of the last 24 hours',
      stories: { one: 'story', other: 'stories' },
      sources: { one: 'source', other: 'sources' },
      in24: 'in 24 hours', updated: 'Updated', top: 'Top story', readAt: 'Read on', whatSources: 'Coverage',
      empty: 'No stories in this category in the last 24 hours', error: 'Couldn’t load the news. Check that the server is running.',
      retry: 'Try again', refresh: 'Refresh', theme: 'Switch theme', close: 'Close', language: 'Language',
      fresh: (n) => `New stories: ${n}`, upToDate: 'You’re up to date',
      note: (n) => `${n} sources in 4 languages. Translation by Google Translate.`, justNow: 'just now',
      back: 'Back', related: 'More news', photo: 'Photo', prev: 'Previous photo', next: 'Next photo',
      gone: 'This story is gone: it’s older than 24 hours.',
      machine: 'Machine translation', original: 'original', showOrig: 'Show original', showTr: 'Show translation',
      noTr: 'Translation is unavailable right now — showing the original', origLang: 'Original',
    },
    zh: {
      world: '世界', eurasia: '欧洲与亚洲', countries: '国家', us: '美国', cn: '中国', ua: '乌克兰', ru: '俄罗斯',
      worldSub: '过去24小时要闻',
      stories: { other: '条报道' },
      sources: { other: '个来源' },
      in24: '（24小时内）', updated: '更新于', top: '头条', readAt: '阅读原文：', whatSources: '各方报道',
      empty: '过去24小时内该类别暂无新闻', error: '无法加载新闻，请检查服务器是否已启动。',
      retry: '重试', refresh: '刷新', theme: '切换主题', close: '关闭', language: '语言',
      fresh: (n) => `新报道：${n}`, upToDate: '已是最新',
      note: (n) => `来源：${n}个，4种语言。翻译：Google 翻译。`, justNow: '刚刚',
      back: '返回', related: '更多新闻', photo: '图片', prev: '上一张', next: '下一张',
      gone: '该新闻已超过24小时，无法查看。',
      machine: '机器翻译', original: '原文', showOrig: '显示原文', showTr: '显示译文',
      noTr: '暂时无法翻译，显示原文', origLang: '原文',
    },
    ru: {
      world: 'Мир', eurasia: 'Европа и Азия', countries: 'Страны', us: 'США', cn: 'Китай', ua: 'Украина', ru: 'Россия',
      worldSub: 'Главное за 24 часа',
      stories: { one: 'история', few: 'истории', many: 'историй', other: 'истории' },
      sources: { one: 'источник', few: 'источника', many: 'источников', other: 'источника' },
      in24: 'за 24 часа', updated: 'Обновлено', top: 'Главное', readAt: 'Читать на', whatSources: 'Что пишут источники',
      empty: 'За последние 24 часа новостей в этой категории нет', error: 'Не удалось загрузить новости. Проверьте, запущен ли сервер.',
      retry: 'Попробовать снова', refresh: 'Обновить', theme: 'Сменить тему', close: 'Закрыть', language: 'Язык',
      fresh: (n) => `Новых историй: ${n}`, upToDate: 'Новости актуальны',
      note: (n) => `Источников: ${n}, на 4 языках. Перевод — Google Translate.`, justNow: 'только что',
      back: 'Назад', related: 'Больше новостей', photo: 'Фото', prev: 'Предыдущее фото', next: 'Следующее фото',
      gone: 'Этой новости уже нет: она старше 24 часов.',
      machine: 'Машинный перевод', original: 'оригинал', showOrig: 'Показать оригинал', showTr: 'Показать перевод',
      noTr: 'Перевод временно недоступен — показан оригинал', origLang: 'Оригинал',
    },
  };

  const GLOBE = '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M3 12h18M12 3c2.8 3 2.8 15 0 18M12 3c-2.8 3-2.8 15 0 18" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>';
  const EURASIA_ICON = '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M4 7.5c2-1.6 4.5-2.3 6.5-1.6 1.6.6 2 2 3.6 2.1 1.7.1 2.6-1.3 4.3-.9 1.3.3 2 1.4 1.6 2.6-.5 1.5-2.4 1.6-3 3-.6 1.3.5 2.8-.6 3.8-1.2 1.1-3 .2-4.2 1-.9.6-.9 2-2 2.4-1.5.5-2.7-1-3-2.4-.3-1.5.6-2.9-.2-4.1-.7-1.1-2.4-1-3.2-2C3.5 10.4 3.2 8.6 4 7.5z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>';
  const CATS = [
    { id: 'world', icon: GLOBE },
    { id: 'eurasia', icon: EURASIA_ICON },
    { id: 'us', flag: '🇺🇸', country: true },
    { id: 'cn', flag: '🇨🇳', country: true },
    { id: 'ua', flag: '🇺🇦', country: true },
    { id: 'ru', flag: '🇷🇺', country: true },
  ];
  const CAT_IDS = CATS.map((c) => c.id);
  const PAGE = 24;
  const AUTO_REFRESH_MS = 10 * 60 * 1000;
  const DAY_MS = 24 * 60 * 60 * 1000;

  // ---------------------------------------------------------------- стан
  const store = {
    get(k, d) { try { return localStorage.getItem(k) || d; } catch (e) { return d; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* приватний режим */ } },
  };
  const state = {
    lang: T[store.get('kolo-lang')] ? store.get('kolo-lang') : 'uk', // за замовчуванням — українська
    cat: 'world',
    data: null,       // відповідь з data/<мова>.json
    list: [],         // історії поточної категорії
    shown: 0,
    loading: false,
    openId: null,
  };

  const $ = (id) => document.getElementById(id);
  const el = {
    grid: $('grid'), title: $('sec-title'), sub: $('sec-sub'), head: $('section-head'), updated: $('updated'),
    sideNav: $('side-nav'), sideInd: $('side-ind'), chips: $('chips'), chipInd: $('chip-ind'), note: $('side-note'),
    langSeg: $('lang-seg'), langDrop: $('lang-drop'), langBtn: $('lang-btn'), langMenu: $('lang-menu'),
    refresh: $('refresh'), theme: $('theme'), listView: $('list-view'), story: $('story-view'),
    toast: $('toast'), sentinel: $('sentinel'), splash: $('splash'),
  };

  const t = () => T[state.lang];
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (ch) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]));
  const safeUrl = (u) => (/^https?:\/\//i.test(u || '') ? u : '#');
  const plural = (n, forms) => {
    const key = new Intl.PluralRules(state.lang).select(n);
    return forms[key] || forms.other;
  };
  const countText = (n, forms) => (state.lang === 'zh' ? `${n} ${forms.other}` : `${n} ${plural(n, forms)}`);
  const ago = (iso) => {
    const diff = (Date.now() - new Date(iso).getTime()) / 1000;
    if (diff < 60) return t().justNow;
    const rtf = new Intl.RelativeTimeFormat(state.lang, { numeric: 'auto', style: 'short' });
    if (diff < 3600) return rtf.format(-Math.round(diff / 60), 'minute');
    return rtf.format(-Math.round(diff / 3600), 'hour');
  };
  const initials = (name) => {
    const w = String(name).replace(/[«»"'“”]/g, '').trim();
    if (/^[一-鿿]/.test(w)) return w[0];
    const parts = w.split(/\s+/).filter(Boolean);
    return (parts.length > 1 && parts[0].length <= 4 ? parts[0] : parts[0][0] + (parts[1] ? parts[1][0] : '')).slice(0, 3).toUpperCase();
  };
  const fresh = (s) => Date.now() - new Date(s.time).getTime() <= DAY_MS;
  const SHORT = { uk: 'УКР', en: 'ENG', ru: 'РУС', zh: '中文', 'zh-Hant': '中文' };
  const baseLang = (c) => String(c || '').split('-')[0];
  const langName = (c) => { try { return new Intl.DisplayNames([state.lang], { type: 'language' }).of(c); } catch (e) { return SHORT[c] || c; } };
  const TR_ICON = '<svg viewBox="0 0 24 24" width="13" height="13" aria-hidden="true"><path d="M4 5h9M8.5 3v2M6 5c.7 3.2 2.8 5.8 6 7.5M11 5c-.8 3.6-3.4 6.6-7 8.5M13 21l4.5-10L22 21M14.5 17.5h6" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/></svg>';

  // ---------------------------------------------------------------- меню
  function buildNav() {
    const L = t();
    const side = [];
    const chips = [];
    CATS.forEach((c, i) => {
      if (c.country && !CATS[i - 1].country) side.push(`<div class="side-label">${esc(L.countries)}</div>`);
      const icon = c.flag ? `<span class="flag">${c.flag}</span>` : c.icon;
      side.push(`<button class="side-link" data-cat="${c.id}" type="button">${icon}<span>${esc(L[c.id])}</span><span class="count" data-count="${c.id}"></span></button>`);
      chips.push(`<button class="chip" data-cat="${c.id}" type="button">${c.flag ? `<span class="flag">${c.flag}</span>` : ''}${esc(L[c.id])}</button>`);
    });
    el.sideNav.innerHTML = '<span class="side-ind" id="side-ind"></span>' + side.join('');
    el.chips.innerHTML = '<span class="chip-ind" id="chip-ind"></span>' + chips.join('');
    el.sideInd = $('side-ind');
    el.chipInd = $('chip-ind');
    markNav(false);
  }

  function markNav(animate = true) {
    document.querySelectorAll('[data-cat]').forEach((b) => {
      const on = b.dataset.cat === state.cat;
      b.classList.toggle('active', on);
      b.setAttribute('aria-current', on ? 'page' : 'false');
    });
    moveIndicators(animate);
  }

  function moveIndicators(animate = true) {
    const side = el.sideNav.querySelector('.side-link.active');
    const chip = el.chips.querySelector('.chip.active');
    [[el.sideInd, side, 'y'], [el.chipInd, chip, 'x']].forEach(([ind, target, axis]) => {
      if (!ind || !target) return;
      if (!animate) ind.style.transition = 'none';
      if (axis === 'y') {
        ind.style.transform = `translateY(${target.offsetTop}px)`;
        ind.style.height = `${target.offsetHeight}px`;
      } else {
        ind.style.transform = `translateX(${target.offsetLeft}px)`;
        ind.style.width = `${target.offsetWidth}px`;
      }
      if (!animate) requestAnimationFrame(() => { ind.style.transition = ''; });
    });
    if (chip && el.chips.offsetParent) {
      const left = chip.offsetLeft - (el.chips.clientWidth - chip.offsetWidth) / 2;
      el.chips.scrollTo({ left, behavior: animate ? 'smooth' : 'auto' });
    }
  }

  function buildLang() {
    el.langSeg.innerHTML = '<span class="seg-ind" id="seg-ind"></span>' + LANGS.map((l) =>
      `<button type="button" role="radio" data-lang="${l.code}" aria-checked="${l.code === state.lang}" title="${esc(l.name)}">${esc(l.short)}</button>`).join('');
    el.langMenu.innerHTML = LANGS.map((l) =>
      `<button type="button" role="menuitemradio" data-lang="${l.code}" aria-checked="${l.code === state.lang}">${esc(l.name)}<span>${esc(l.short)}</span></button>`).join('');
    const cur = LANGS.find((l) => l.code === state.lang);
    el.langBtn.textContent = cur.short;
    el.langBtn.setAttribute('aria-label', `${t().language}: ${cur.name}`);
    moveSeg(false);
  }

  function moveSeg(animate = true) {
    const ind = $('seg-ind');
    const btn = el.langSeg.querySelector('[aria-checked="true"]');
    if (!ind || !btn) return;
    if (!animate) ind.style.transition = 'none';
    ind.style.width = `${btn.offsetWidth}px`;
    ind.style.transform = `translateX(${btn.offsetLeft}px)`;
    if (!animate) requestAnimationFrame(() => { ind.style.transition = ''; });
  }

  function applyTexts() {
    const L = t();
    document.documentElement.lang = state.lang === 'zh' ? 'zh-Hans' : state.lang;
    el.refresh.setAttribute('aria-label', L.refresh);
    el.refresh.title = L.refresh;
    el.theme.setAttribute('aria-label', L.theme);
    el.theme.title = L.theme;
  }

  // ---------------------------------------------------------------- картки
  function cardHTML(s, i, hero) {
    const L = t();
    const n = s.sourceCount;
    const names = s.names || [];
    const av = names.slice(0, 3).map((nm) => `<i>${esc(initials(nm).slice(0, 1))}</i>`).join('');
    const more = names.length > 2 ? ` +${names.length - 2}` : '';
    const img = s.image
      ? `<div class="media"><img src="${esc(safeUrl(s.image))}" alt="" loading="${i < 4 ? 'eager' : 'lazy'}" decoding="async" referrerpolicy="no-referrer"></div>`
      : '<div class="media noimg"></div>';
    return `<article class="card${hero ? ' hero' : ''}" style="--c:${esc(s.color)};--i:${i}" data-id="${esc(s.id)}" tabindex="0" role="button" aria-label="${esc(s.title)}">
      ${img}
      <div class="body">
        ${hero ? `<span class="badge-top">${esc(L.top)}</span>` : ''}
        <div class="meta"><span class="avatars">${av}</span><span>${esc(countText(n, L.sources))}</span><span class="sep">•</span><time datetime="${esc(s.time)}">${esc(ago(s.time))}</time>${s.orig ? `<span class="tr-pill${s.tr === false ? ' raw' : ''}" title="${esc(s.tr === false ? L.noTr : `${L.machine} · ${L.original}: ${langName(s.orig.lang)}`)}">${TR_ICON}${esc(SHORT[s.orig.lang] || s.orig.lang)}</span>` : ''}</div>
        <h3>${esc(s.title)}</h3>
        ${s.summary ? `<p>${esc(s.summary)}</p>` : ''}
        <div class="srcs">${esc(names.slice(0, 2).join(' · '))}${esc(more)}</div>
      </div>
    </article>`;
  }

  function wireImages(root) {
    root.querySelectorAll('.media img:not([data-w])').forEach((img) => {
      img.dataset.w = '1';
      const ok = () => img.classList.add('ok');
      const bad = () => { img.parentElement.classList.add('noimg'); img.remove(); };
      if (img.complete && img.naturalWidth) ok();
      else if (img.complete) bad();
      else { img.addEventListener('load', ok, { once: true }); img.addEventListener('error', bad, { once: true }); }
    });
  }

  function skeleton() {
    const one = '<div class="skel"><div class="s-img"></div><div class="s-line"></div><div class="s-line"></div><div class="s-line short"></div></div>';
    el.grid.innerHTML = one.repeat(6);
  }

  function renderHead(animate) {
    const L = t();
    const n = state.list.length;
    el.title.textContent = L[state.cat];
    const sub = state.cat === 'world' ? `${L.worldSub} · ${countText(n, L.stories)}` : `${countText(n, L.stories)} ${L.in24}`;
    el.sub.textContent = sub;
    if (animate) {
      el.head.classList.remove('swap');
      void el.head.offsetWidth;
      el.head.classList.add('swap');
    }
    if (!state.openId) document.title = state.cat === 'world' ? 'Коло Новин' : `${L[state.cat]} — Коло Новин`;
  }

  function renderCounts() {
    if (!state.data) return;
    const live = state.data.stories.filter(fresh);
    document.querySelectorAll('[data-count]').forEach((c) => {
      c.textContent = live.filter((s) => s.cats.includes(c.dataset.count)).length || '';
    });
  }

  function renderUpdated() {
    if (!state.data) return;
    el.updated.textContent = `${t().updated} ${ago(state.data.generated)}`;
    el.note.textContent = t().note(state.data.sources.length);
  }

  function renderList(animate = true) {
    if (!state.data) return;
    state.list = state.data.stories.filter((s) => s.cats.includes(state.cat) && fresh(s));
    state.shown = 0;
    renderHead(animate);
    if (!state.list.length) {
      el.grid.innerHTML = `<div class="empty"><span class="logo"></span><div>${esc(t().empty)}</div></div>`;
      return;
    }
    el.grid.innerHTML = '';
    appendMore();
  }

  function appendMore() {
    if (state.shown >= state.list.length) return;
    const from = state.shown;
    const part = state.list.slice(from, from + PAGE);
    const html = part.map((s, k) => cardHTML(s, Math.min(k, 10), from + k === 0)).join('');
    el.grid.insertAdjacentHTML('beforeend', html);
    state.shown += part.length;
    wireImages(el.grid);
  }

  function refreshTimes() {
    document.querySelectorAll('.card time').forEach((tm) => { tm.textContent = ago(tm.getAttribute('datetime')); });
    renderUpdated();
  }

  // ---------------------------------------------------------------- перемикання
  let swapTimer;
  function switchCat(cat, push = true) {
    if (!CAT_IDS.includes(cat)) cat = 'world';
    if (push && location.hash !== `#${cat}`) history.pushState({ cat }, '', `#${cat}`);
    if (state.openId) closeStory(true, cat === state.cat);
    if (cat === state.cat && el.grid.children.length) return;
    state.cat = cat;
    markNav(true);
    el.grid.classList.add('leaving');
    clearTimeout(swapTimer);
    swapTimer = setTimeout(() => {
      const top = el.head.getBoundingClientRect().top + window.scrollY - 130;
      if (window.scrollY > top) window.scrollTo({ top: Math.max(0, top), behavior: 'auto' });
      renderList(true);
      el.grid.classList.remove('leaving');
    }, 180);
  }

  async function setLang(code) {
    if (!T[code] || code === state.lang) { closeLangMenu(); return; }
    state.lang = code;
    store.set('kolo-lang', code);
    closeLangMenu();
    el.langSeg.querySelectorAll('button').forEach((b) => b.setAttribute('aria-checked', String(b.dataset.lang === code)));
    moveSeg(true);
    el.grid.classList.add('leaving');
    await new Promise((r) => setTimeout(r, 180));
    window.scrollTo({ top: 0, behavior: 'auto' });
    applyTexts();
    buildNav();
    buildLang();
    skeleton();
    el.grid.classList.remove('leaving');
    await load(false);
    if (state.openId) openStory(state.openId, false);
  }

  function closeLangMenu() {
    el.langDrop.classList.remove('open');
    el.langBtn.setAttribute('aria-expanded', 'false');
  }

  // ---------------------------------------------------------------- завантаження даних
  async function load(silent) {
    if (state.loading) return;
    state.loading = true;
    document.body.classList.add('loading');
    el.refresh.classList.add('spinning');
    const lang = state.lang;
    const oldIds = new Set((state.data && state.data.lang === lang ? state.data.stories : []).map((s) => s.id));
    try {
      const res = await fetch(`data/${lang}.json?t=${Date.now()}`, { cache: 'no-store' });
      if (!res.ok) throw new Error(res.status);
      const data = await res.json();
      if (lang !== state.lang) return;
      state.data = data;
      const added = oldIds.size ? data.stories.filter((s) => !oldIds.has(s.id) && s.cats.includes(state.cat)).length : 0;
      if (!silent || added) renderList(!silent);
      renderCounts();
      renderUpdated();
      if (silent === 'manual') toast(added ? t().fresh(added) : t().upToDate);
      else if (silent && added) toast(t().fresh(added));
    } catch (e) {
      if (!state.data || state.data.lang !== lang) {
        el.grid.innerHTML = `<div class="empty"><span class="logo"></span><div>${esc(t().error)}</div><button type="button" id="retry">${esc(t().retry)}</button></div>`;
        $('retry').onclick = () => { skeleton(); load(false); };
      }
    } finally {
      state.loading = false;
      document.body.classList.remove('loading');
      setTimeout(() => el.refresh.classList.remove('spinning'), 400);
      hideSplash();
    }
  }

  let toastTimer;
  function toast(msg) {
    el.toast.textContent = msg;
    el.toast.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.toast.classList.remove('show'), 2600);
  }

  // ---------------------------------------------------------------- заставка
  const splashStart = Date.now();
  let splashSeen = false;
  try { splashSeen = sessionStorage.getItem('kolo-splash') === '1'; } catch (e) { /* немає сховища */ }
  if (splashSeen) el.splash.classList.add('skip');
  function hideSplash() {
    if (splashSeen) return;
    splashSeen = true;
    try { sessionStorage.setItem('kolo-splash', '1'); } catch (e) { /* немає сховища */ }
    const wait = Math.max(0, 1100 - (Date.now() - splashStart));
    setTimeout(() => {
      el.splash.classList.add('hide');
      setTimeout(() => el.splash.classList.add('skip'), 700);
    }, wait);
  }

  // ---------------------------------------------------------------- сторінка історії
  const ARROW = '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M7 17L17 7M9 7h8v8" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  const CHEV = (d) => `<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="${d === 'l' ? 'M15 5l-7 7 7 7' : 'M9 5l7 7-7 7'}" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
  const details = new Map();   // кеш завантажених історій: "мова/id" -> дані
  let listScroll = 0;
  let storyToken = 0;

  async function fetchDetail(id) {
    const key = `${state.lang}/${id}`;
    if (details.has(key)) return details.get(key);
    const res = await fetch(`data/${state.lang}/${encodeURIComponent(id)}.json?t=${state.data ? Date.parse(state.data.generated) : 0}`);
    if (!res.ok) throw new Error(res.status);
    const d = await res.json();
    details.set(key, d);
    return d;
  }

  function trLine(s) {
    const L = t();
    if (!s.orig) return '';
    return `<div class="d-tr">${TR_ICON}<span>${esc(s.tr === false ? L.noTr : `${L.machine} · ${L.original}: ${langName(s.orig.lang)}`)}</span>${s.tr === false ? '' : `<button type="button" id="tr-toggle">${esc(L.showOrig)}</button>`}</div>`;
  }

  function galleryHTML(images) {
    const L = t();
    if (!images.length) return '<div class="gallery empty-g"></div>';
    const many = images.length > 1;
    return `<div class="gallery" id="gallery">
      <div class="g-track" id="g-track">${images.map((im, k) => `
        <figure class="g-item"><img src="${esc(safeUrl(im.u))}" alt="" loading="${k < 2 ? 'eager' : 'lazy'}" decoding="async" referrerpolicy="no-referrer">
          <figcaption>${esc(L.photo)}: ${esc(im.s)}</figcaption></figure>`).join('')}
      </div>
      ${many ? `<button class="g-nav prev" type="button" data-g="-1" aria-label="${esc(L.prev)}">${CHEV('l')}</button>
      <button class="g-nav next" type="button" data-g="1" aria-label="${esc(L.next)}">${CHEV('r')}</button>
      <div class="g-count" id="g-count">1 / ${images.length}</div>
      <div class="g-dots" id="g-dots">${images.map((_, k) => `<i class="${k ? '' : 'on'}"></i>`).join('')}</div>` : ''}
    </div>`;
  }

  function wireGallery() {
    const track = $('g-track');
    if (!track) return;
    const figs = () => [...track.querySelectorAll('.g-item')];
    track.querySelectorAll('img').forEach((img) => {
      const ok = () => img.classList.add('ok');
      const bad = () => { img.closest('.g-item').remove(); sync(); };
      if (img.complete && img.naturalWidth) ok();
      else if (img.complete) bad();
      else { img.addEventListener('load', ok, { once: true }); img.addEventListener('error', bad, { once: true }); }
    });
    function sync() {
      const n = figs().length;
      const g = $('gallery');
      if (!g) return;
      if (!n) { g.classList.add('empty-g'); g.innerHTML = ''; return; }
      const k = Math.round(track.scrollLeft / Math.max(track.clientWidth, 1));
      const cnt = $('g-count');
      if (cnt) cnt.textContent = `${Math.min(k + 1, n)} / ${n}`;
      const dots = $('g-dots');
      if (dots) {
        while (dots.children.length > n) dots.lastChild.remove();
        [...dots.children].forEach((d, i) => d.classList.toggle('on', i === k));
      }
      g.classList.toggle('single', n < 2);
    }
    track.addEventListener('scroll', () => requestAnimationFrame(sync), { passive: true });
    $('gallery').addEventListener('click', (e) => {
      const b = e.target.closest('[data-g]');
      if (b) track.scrollBy({ left: Number(b.dataset.g) * track.clientWidth, behavior: 'smooth' });
    });
    sync();
  }

  function sourcesHTML(list) {
    const L = t();
    return list.map((x, k) => `
      <div class="sp-src" style="--k:${k}">
        <div class="sp-src-head"><span class="av">${esc(initials(x.name))}</span><b>${esc(x.name)}</b>${baseLang(x.lang) !== state.lang ? `<em class="lang-tag">${esc(SHORT[x.lang] || x.lang)}</em>` : ''}<time>${esc(ago(x.time))}</time></div>
        <h3 data-o="${esc(x.oTitle || '')}">${esc(x.title)}</h3>
        ${x.text ? `<p data-o="${esc(x.oText || '')}">${esc(x.text)}</p>` : ''}
        <a class="sp-link" href="${esc(safeUrl(x.url))}" target="_blank" rel="noopener noreferrer">${esc(L.readAt)} ${esc(x.name)} ${ARROW}</a>
      </div>`).join('');
  }

  function relatedHTML(s) {
    const pool = state.data.stories.filter((x) => x.id !== s.id && fresh(x));
    const cat = s.cats.find((c) => c !== 'world' && c === state.cat) || s.cats.find((c) => c !== 'world') || 'world';
    const rel = pool.filter((x) => x.cats.includes(cat)).slice(0, 6);
    return rel.map((x, k) => cardHTML(x, k, false)).join('');
  }

  function catPills(s) {
    return s.cats.filter((c) => c !== 'world').map((c) => {
      const cc = CATS.find((x) => x.id === c);
      return `<button class="sp-pill" type="button" data-cat="${c}">${cc && cc.flag ? `<span class="flag">${cc.flag}</span>` : ''}${esc(t()[c])}</button>`;
    }).join('');
  }

  // відкриваємо одразу з даними стрічки, а фото й тексти джерел догружаємо
  async function openStory(id, push = true) {
    const s = state.data && state.data.stories.find((x) => x.id === id);
    const L = t();
    const token = ++storyToken;
    if (!state.openId) listScroll = window.scrollY;
    state.openId = id;
    if (push) history.pushState({ cat: state.cat, story: id }, '', `#${state.cat}/${id}`);
    el.listView.hidden = true;
    el.story.hidden = false;
    window.scrollTo({ top: 0, behavior: 'auto' });
    if (!s) {
      el.story.innerHTML = `<div class="sp-top"><button class="sp-back" type="button" data-back>${CHEV('l')}${esc(L.back)}</button></div><div class="empty"><span class="logo"></span><div>${esc(L.gone)}</div></div>`;
      return;
    }
    document.title = `${s.title} — Коло Новин`;
    el.story.style.setProperty('--c', s.color);
    el.story.innerHTML = `
      <div class="sp-top"><button class="sp-back" type="button" data-back>${CHEV('l')}${esc(L.back)}</button><div class="sp-pills">${catPills(s)}</div></div>
      <header class="sp-head">
        <div class="meta"><span class="avatars">${(s.names || []).slice(0, 3).map((n) => `<i>${esc(initials(n).slice(0, 1))}</i>`).join('')}</span><span>${esc(countText(s.sourceCount, L.sources))}</span><span class="sep">•</span><time>${esc(ago(s.time))}</time></div>
        <h1 id="sp-title">${esc(s.title)}</h1>
        ${trLine(s)}
      </header>
      <div id="sp-gallery">${galleryHTML(s.image ? [{ u: s.image, s: (s.names || [''])[0] }] : [])}</div>
      <p class="sp-lead" id="sp-lead">${esc(s.summary || '')}</p>
      <section class="sp-sources" id="sp-sources"><h2>${esc(L.whatSources)}</h2><div class="sp-skel"></div><div class="sp-skel"></div></section>
      <section class="sp-related"><h2>${esc(L.related)}</h2><div class="grid related" id="sp-related">${relatedHTML(s)}</div></section>`;
    wireGallery();
    wireImages($('sp-related'));
    try {
      const d = await fetchDetail(id);
      if (token !== storyToken) return;
      if (d.images && d.images.length > (s.image ? 1 : 0)) {
        $('sp-gallery').innerHTML = galleryHTML(d.images);
        wireGallery();
      }
      if (d.text && d.text.length > (s.summary || '').length) $('sp-lead').textContent = d.text;
      $('sp-sources').innerHTML = `<h2>${esc(L.whatSources)}</h2>${sourcesHTML(d.sources)}`;
      wireToggle(s, d);
    } catch (e) {
      if (token !== storyToken) return;
      $('sp-sources').innerHTML = `<h2>${esc(L.whatSources)}</h2>${sourcesHTML((s.names || []).map((n) => ({ name: n, title: '', url: '#', time: s.time, lang: state.lang })))}`;
      wireToggle(s, null);
    }
  }

  function wireToggle(s, d) {
    const toggle = $('tr-toggle');
    if (!toggle) return;
    const L = t();
    let orig = false;
    toggle.addEventListener('click', () => {
      orig = !orig;
      const h = $('sp-title');
      const lead = $('sp-lead');
      h.textContent = orig ? s.orig.title : s.title;
      h.lang = orig ? s.orig.lang : '';
      lead.textContent = orig ? (s.orig.text || s.orig.summary || '') : ((d && d.text) || s.summary || '');
      [h, lead].forEach((n) => { n.classList.remove('swap-in'); void n.offsetWidth; n.classList.add('swap-in'); });
      document.querySelectorAll('#sp-sources [data-o]').forEach((n) => {
        if (!n.dataset.o) return;
        if (!n.dataset.t) n.dataset.t = n.textContent;
        n.textContent = orig ? n.dataset.o : n.dataset.t;
      });
      toggle.textContent = orig ? L.showTr : L.showOrig;
    });
  }

  function closeStory(fromHistory = false, restore = true) {
    if (!state.openId) return;
    const id = state.openId;
    state.openId = null;
    storyToken++;
    el.story.hidden = true;
    el.story.innerHTML = '';
    el.listView.hidden = false;
    el.listView.classList.remove('back-in');
    void el.listView.offsetWidth;
    el.listView.classList.add('back-in');
    renderHead(false);
    if (restore) window.scrollTo({ top: listScroll, behavior: 'auto' });
    if (!fromHistory && history.state && history.state.story) history.back();
    const card = el.grid.querySelector(`[data-id="${CSS.escape(id)}"]`);
    if (card) card.focus({ preventScroll: true });
  }

  function goBack() {
    if (history.state && history.state.story) history.back();
    else { closeStory(true); history.pushState({ cat: state.cat }, '', `#${state.cat}`); }
  }

  // ---------------------------------------------------------------- маршрути (#ua, #ua/<id>)
  function route(push) {
    const [cat, id] = location.hash.replace('#', '').split('/');
    const c = CAT_IDS.includes(cat) ? cat : 'world';
    if (id && state.data) {
      if (c !== state.cat) { state.cat = c; markNav(false); renderList(false); }
      if (state.openId !== id) openStory(id, false);
    } else {
      if (state.openId) closeStory(true, c === state.cat);
      if (c !== state.cat) switchCat(c, false);
    }
    return push;
  }

  // ---------------------------------------------------------------- події
  document.addEventListener('click', (e) => {
    const catBtn = e.target.closest('[data-cat]');
    if (catBtn) { switchCat(catBtn.dataset.cat); return; }
    const langBtn = e.target.closest('[data-lang]');
    if (langBtn) { setLang(langBtn.dataset.lang); return; }
    if (e.target.closest('[data-back]')) { goBack(); return; }
    const card = e.target.closest('.card');
    if (card) { openStory(card.dataset.id); return; }
    if (!e.target.closest('#lang-drop')) closeLangMenu();
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') { if (state.openId) goBack(); closeLangMenu(); }
    if (state.openId && (e.key === 'ArrowLeft' || e.key === 'ArrowRight') && $('g-track') && !e.target.closest('input,textarea')) {
      const tr = $('g-track');
      tr.scrollBy({ left: (e.key === 'ArrowLeft' ? -1 : 1) * tr.clientWidth, behavior: 'smooth' });
    }
    if ((e.key === 'Enter' || e.key === ' ') && e.target.classList && e.target.classList.contains('card')) {
      e.preventDefault(); openStory(e.target.dataset.id);
    }
  });
  el.langBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    const open = !el.langDrop.classList.contains('open');
    el.langDrop.classList.toggle('open', open);
    el.langBtn.setAttribute('aria-expanded', String(open));
  });
  el.refresh.addEventListener('click', () => load('manual'));
  el.theme.addEventListener('click', () => {
    const next = document.documentElement.dataset.theme === 'light' ? 'dark' : 'light';
    document.documentElement.dataset.theme = next;
    store.set('kolo-theme', next);
    document.querySelector('meta[name="theme-color"]').content = next === 'light' ? '#f4f3ef' : '#0c0e12';
  });
  document.querySelector('.brand').addEventListener('click', (e) => { e.preventDefault(); switchCat('world'); window.scrollTo({ top: 0, behavior: 'smooth' }); });
  window.addEventListener('popstate', () => route(false));
  window.addEventListener('resize', () => { moveIndicators(false); moveSeg(false); });
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden && state.data && Date.now() - new Date(state.data.generated).getTime() > AUTO_REFRESH_MS) load(true);
  });

  new IntersectionObserver((entries) => {
    if (entries.some((en) => en.isIntersecting)) appendMore();
  }, { rootMargin: '800px' }).observe(el.sentinel);

  setInterval(refreshTimes, 60 * 1000);
  setInterval(() => load(true), AUTO_REFRESH_MS);

  // ---------------------------------------------------------------- старт
  if (document.documentElement.dataset.theme === 'light') document.querySelector('meta[name="theme-color"]').content = '#f4f3ef';
  const [startCat] = location.hash.replace('#', '').split('/');
  state.cat = CAT_IDS.includes(startCat) ? startCat : 'world';
  applyTexts();
  buildNav();
  buildLang();
  skeleton();
  load(false).then(() => {
    const [, id] = location.hash.replace('#', '').split('/');
    if (id) openStory(id, false);
  });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => { moveIndicators(false); moveSeg(false); });
})();
