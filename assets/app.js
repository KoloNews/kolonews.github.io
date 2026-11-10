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
      popular: 'Популярне', science: 'Наука', tech: 'Технології', crime: 'Кримінал', sport: 'Спорт', economy: 'Економіка', games: 'Ігри', crypto: 'Криптовалюта',
      world: 'Весь світ', eurasia: 'Європа і Азія', us: 'США', cn: 'Китай', ua: 'Україна', ru: 'Росія',
      sections: 'Розділи', region: 'Регіон',
      stories: { one: 'історія', few: 'історії', many: 'історій', other: 'історії' },
      sources: { one: 'джерело', few: 'джерела', many: 'джерел', other: 'джерела' },
      sub: (n) => `${n} за часом · за 24 години`, updated: 'Оновлено', top: 'Головне', readAt: 'Читати на',
      empty: 'За останні 24 години новин тут немає', error: 'Не вдалося завантажити новини. Перевірте з’єднання.',
      retry: 'Спробувати ще', refresh: 'Оновити', theme: 'Змінити тему', language: 'Мова',
      fresh: (n) => `Нових історій: ${n}`, upToDate: 'Новини актуальні',
      note: (n) => `Джерел: ${n}, 4 мовами. Тексти — ШІ Gemini, переклад — Google Translate.`, justNow: 'щойно',
      back: 'Назад', related: 'Більше новин', photo: 'Фото', prev: 'Попереднє фото', next: 'Наступне фото',
      gone: 'Цієї новини вже немає: вона старша за 24 години або випала з топу.',
      machine: 'Машинний переклад', original: 'оригінал', showOrig: 'Показати оригінал', showTr: 'Показати переклад',
      noTr: 'Переклад тимчасово недоступний — показано оригінал',
      aiBy: (s) => `Текст написав ШІ на основі ${s}`, aiTr: 'перекладено з української', aiShort: 'ШІ',
      points: 'Головне', srcTitle: 'Джерела', descBy: 'Короткий опис від видання',
    },
    en: {
      popular: 'Popular', science: 'Science', tech: 'Tech', crime: 'Crime', sport: 'Sport', economy: 'Economy', games: 'Games', crypto: 'Crypto',
      world: 'Whole world', eurasia: 'Europe & Asia', us: 'USA', cn: 'China', ua: 'Ukraine', ru: 'Russia',
      sections: 'Sections', region: 'Region',
      stories: { one: 'story', other: 'stories' },
      sources: { one: 'source', other: 'sources' },
      sub: (n) => `${n} by time · last 24 hours`, updated: 'Updated', top: 'Top story', readAt: 'Read on',
      empty: 'No stories here in the last 24 hours', error: 'Couldn’t load the news. Check your connection.',
      retry: 'Try again', refresh: 'Refresh', theme: 'Switch theme', language: 'Language',
      fresh: (n) => `New stories: ${n}`, upToDate: 'You’re up to date',
      note: (n) => `${n} sources in 4 languages. Texts by Gemini AI, translation by Google Translate.`, justNow: 'just now',
      back: 'Back', related: 'More news', photo: 'Photo', prev: 'Previous photo', next: 'Next photo',
      gone: 'This story is gone: it’s older than 24 hours or dropped out of the top.',
      machine: 'Machine translation', original: 'original', showOrig: 'Show original', showTr: 'Show translation',
      noTr: 'Translation is unavailable right now — showing the original',
      aiBy: (s) => `Written by AI from ${s}`, aiTr: 'translated from Ukrainian', aiShort: 'AI',
      points: 'Key points', srcTitle: 'Sources', descBy: 'Short description from the outlet',
    },
    zh: {
      popular: '热门', science: '科学', tech: '科技', crime: '犯罪', sport: '体育', economy: '经济', games: '游戏', crypto: '加密货币',
      world: '全世界', eurasia: '欧洲与亚洲', us: '美国', cn: '中国', ua: '乌克兰', ru: '俄罗斯',
      sections: '栏目', region: '地区',
      stories: { other: '条报道' },
      sources: { other: '个来源' },
      sub: (n) => `${n} · 按时间排序 · 24小时内`, updated: '更新于', top: '头条', readAt: '阅读原文：',
      empty: '过去24小时内暂无新闻', error: '无法加载新闻，请检查网络连接。',
      retry: '重试', refresh: '刷新', theme: '切换主题', language: '语言',
      fresh: (n) => `新报道：${n}`, upToDate: '已是最新',
      note: (n) => `来源：${n}个，4种语言。正文由 Gemini AI 撰写，Google 翻译。`, justNow: '刚刚',
      back: '返回', related: '更多新闻', photo: '图片', prev: '上一张', next: '下一张',
      gone: '该新闻已超过24小时或已不在榜单中。',
      machine: '机器翻译', original: '原文', showOrig: '显示原文', showTr: '显示译文',
      noTr: '暂时无法翻译，显示原文',
      aiBy: (s) => `AI 根据${s}撰写`, aiTr: '译自乌克兰语', aiShort: 'AI',
      points: '要点', srcTitle: '来源', descBy: '媒体简介',
    },
    ru: {
      popular: 'Популярное', science: 'Наука', tech: 'Технологии', crime: 'Криминал', sport: 'Спорт', economy: 'Экономика', games: 'Игры', crypto: 'Криптовалюта',
      world: 'Весь мир', eurasia: 'Европа и Азия', us: 'США', cn: 'Китай', ua: 'Украина', ru: 'Россия',
      sections: 'Разделы', region: 'Регион',
      stories: { one: 'история', few: 'истории', many: 'историй', other: 'истории' },
      sources: { one: 'источник', few: 'источника', many: 'источников', other: 'источника' },
      sub: (n) => `${n} по времени · за 24 часа`, updated: 'Обновлено', top: 'Главное', readAt: 'Читать на',
      empty: 'За последние 24 часа новостей здесь нет', error: 'Не удалось загрузить новости. Проверьте соединение.',
      retry: 'Попробовать снова', refresh: 'Обновить', theme: 'Сменить тему', language: 'Язык',
      fresh: (n) => `Новых историй: ${n}`, upToDate: 'Новости актуальны',
      note: (n) => `Источников: ${n}, на 4 языках. Тексты — ИИ Gemini, перевод — Google Translate.`, justNow: 'только что',
      back: 'Назад', related: 'Больше новостей', photo: 'Фото', prev: 'Предыдущее фото', next: 'Следующее фото',
      gone: 'Этой новости уже нет: она старше 24 часов или выпала из топа.',
      machine: 'Машинный перевод', original: 'оригинал', showOrig: 'Показать оригинал', showTr: 'Показать перевод',
      noTr: 'Перевод временно недоступен — показан оригинал',
      aiBy: (s) => `Текст написал ИИ на основе ${s}`, aiTr: 'переведено с украинского', aiShort: 'ИИ',
      points: 'Главное', srcTitle: 'Источники', descBy: 'Краткое описание от издания',
    },
  };

  // однокольорові контурні іконки (колір тексту)
  const ic = (d) => `<svg class="ico" viewBox="0 0 24 24" aria-hidden="true">${d}</svg>`;
  const ICONS = {
    popular: ic('<path d="M12 3c1.2 3.4 4.5 5.4 4.5 9.6a4.5 4.5 0 0 1-9 0c0-2.2 1-3.6 2.1-4.6.1 2 1 3.2 2.1 3.4-.4-3.1-.5-5.6.3-8.4z"/>'),
    tech: ic('<rect x="6.5" y="6.5" width="11" height="11" rx="2"/><rect x="9.8" y="9.8" width="4.4" height="4.4" rx=".8"/><path d="M9.5 3.5v3M14.5 3.5v3M9.5 17.5v3M14.5 17.5v3M3.5 9.5h3M3.5 14.5h3M17.5 9.5h3M17.5 14.5h3"/>'),
    economy: ic('<path d="M3.5 16.5l5.5-5.5 4 4 7-7"/><path d="M15 8h5v5"/>'),
    crime: ic('<path d="M12 3.2l7.5 2.8v5.6c0 4.6-3.2 7.9-7.5 9.2-4.3-1.3-7.5-4.6-7.5-9.2V6z"/><path d="M12 8.2v4.6M12 15.8v.1"/>'),
    sport: ic('<circle cx="12" cy="12" r="8.6"/><path d="M12 7.6l3.6 2.6-1.4 4.2H9.8l-1.4-4.2z"/><path d="M12 3.4v4.2M15.6 10.2l4.2-1.4M14.2 14.4l2.6 3.6M9.8 14.4l-2.6 3.6M8.4 10.2l-4.2-1.4"/>'),
    science: ic('<path d="M9.5 3.5h5M10.5 3.5v5.8L5.3 18a1.9 1.9 0 0 0 1.6 2.9h10.2a1.9 1.9 0 0 0 1.6-2.9l-5.2-8.7V3.5"/><path d="M7.6 15h8.8"/>'),
    games: ic('<path d="M7 8h10a4.5 4.5 0 0 1 4.5 4.5v.3a3.7 3.7 0 0 1-6.6 2.3L14.3 14H9.7l-.6 1.1a3.7 3.7 0 0 1-6.6-2.3v-.3A4.5 4.5 0 0 1 7 8z"/><path d="M7.5 10.5v3.5M5.75 12.25h3.5M15.8 11.2v.1M17.8 13v.1"/>'),
    crypto: ic('<rect x="4" y="12.5" width="3.4" height="7.5" rx="1"/><rect x="10.3" y="8" width="3.4" height="12" rx="1"/><rect x="16.6" y="4" width="3.4" height="16" rx="1"/>'),
    world: ic('<circle cx="12" cy="12" r="8.6"/><path d="M3.4 12h17.2M12 3.4c2.6 2.6 2.6 14.6 0 17.2M12 3.4c-2.6 2.6-2.6 14.6 0 17.2"/>'),
    eurasia: ic('<circle cx="12" cy="12" r="8.6"/><path d="M6.2 7.6c1.5-.3 2.4.4 3.4 1.4.9.9 2.2.6 3.2.1 1.4-.7 3-.4 4 .8M8 15.2c1.2-.8 2.6-.5 3.6.3 1 .8 2.4.9 3.6.2"/>'),
  };
  // порядок розділів; у науці, іграх і криптовалюті — лише «Весь світ»
  const TOPICS = ['popular', 'tech', 'economy', 'crime', 'sport', 'science', 'games', 'crypto'].map((id) => ({ id, svg: ICONS[id] }));
  const WORLD_ONLY = new Set(['science', 'games', 'crypto']);
  const REGIONS = [
    { id: 'world', svg: ICONS.world }, { id: 'eurasia', svg: ICONS.eurasia },
    { id: 'us', cc: 'US' }, { id: 'cn', cc: 'CN' }, { id: 'ua', cc: 'UA' },
  ];
  const iconOf = (x) => (x.svg ? x.svg : `<span class="cc" aria-hidden="true">${x.cc}</span>`);
  const TOPIC_IDS = TOPICS.map((x) => x.id);
  const REGION_IDS = REGIONS.map((x) => x.id);
  const PER_SECTION = 15;
  const AUTO_REFRESH_MS = 10 * 60 * 1000;
  const DAY_MS = 24 * 60 * 60 * 1000;

  // ---------------------------------------------------------------- стан
  const store = {
    get(k, d) { try { return localStorage.getItem(k) || d; } catch (e) { return d; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* приватний режим */ } },
  };
  const state = {
    lang: T[store.get('kolo-lang')] ? store.get('kolo-lang') : 'uk', // за замовчуванням — українська
    topic: 'popular',
    region: 'world',
    data: null,
    list: [],
    loading: false,
    openId: null,
  };

  const $ = (id) => document.getElementById(id);
  const el = {
    grid: $('grid'), title: $('sec-title'), sub: $('sec-sub'), head: $('section-head'), updated: $('updated'),
    sideTopics: $('side-topics'), sideRegions: $('side-regions'), chipsT: $('chips-t'), chipsR: $('chips-r'),
    labelT: $('label-t'), labelR: $('label-r'),
    langSeg: $('lang-seg'), langDrop: $('lang-drop'), langBtn: $('lang-btn'), langMenu: $('lang-menu'),
    refresh: $('refresh'), theme: $('theme'), listView: $('list-view'), story: $('story-view'),
    toast: $('toast'), splash: $('splash'),
  };

  const t = () => T[state.lang];
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (ch) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]));
  const safeUrl = (u) => (/^https?:\/\//i.test(u || '') ? u : '#');
  const plural = (n, forms) => forms[new Intl.PluralRules(state.lang).select(n)] || forms.other;
  const countText = (n, forms) => (state.lang === 'zh' ? `${n} ${forms.other}` : `${n} ${plural(n, forms)}`);
  const ago = (iso) => {
    const diff = (Date.now() - new Date(iso).getTime()) / 1000;
    if (diff < 60) return t().justNow;
    const rtf = new Intl.RelativeTimeFormat(state.lang, { numeric: 'auto', style: 'short' });
    if (diff < 3600) return rtf.format(-Math.round(diff / 60), 'minute');
    return rtf.format(-Math.round(diff / 3600), 'hour');
  };
  // точний час новини: сьогодні — «14:32», учора — «вчора, 14:32», раніше — «9 лист., 14:32» (часовий пояс пристрою)
  const when = (iso) => {
    const d = new Date(iso);
    if (isNaN(d)) return '';
    const hm = d.toLocaleTimeString(state.lang, { hour: '2-digit', minute: '2-digit', hour12: false });
    const day = (x) => new Date(x.getFullYear(), x.getMonth(), x.getDate()).getTime();
    const diff = Math.round((day(new Date()) - day(d)) / DAY_MS);
    if (diff <= 0) return hm;
    if (diff === 1) {
      const y = new Intl.RelativeTimeFormat(state.lang, { numeric: 'auto' }).format(-1, 'day');
      return state.lang === 'zh' ? `${y} ${hm}` : `${y}, ${hm}`;
    }
    const dt = d.toLocaleDateString(state.lang, { day: 'numeric', month: 'short' });
    return state.lang === 'zh' ? `${dt} ${hm}` : `${dt}, ${hm}`;
  };
  const startOf = (s) => s.first || s.time;
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
  const AI_ICON = '<svg viewBox="0 0 24 24" width="13" height="13" aria-hidden="true"><path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8zM18.5 15l.9 2.6 2.6.9-2.6.9-.9 2.6-.9-2.6-2.6-.9 2.6-.9z" fill="currentColor"/></svg>';
  const matches = (s, topic, region) => s.cats.includes(region) && (topic === 'popular' || (s.topics || []).includes(topic)) && fresh(s);
  const sectionList = (topic, region) => (state.data ? state.data.stories.filter((s) => matches(s, topic, region)).slice(0, PER_SECTION) : []);
  // головна (перша) новина різна в різних розділах: обираємо по черзі розділів —
  // якщо найрейтинговіша вже головна в попередньому розділі, головною стає наступна
  const heroCache = new Map();
  const heroesFor = (region) => {
    if (heroCache.has(region)) return heroCache.get(region);
    const used = new Set();
    const map = {};
    TOPIC_IDS.forEach((t) => {
      const list = sectionList(t, regionFor(t, region));
      const h = list.find((x) => !used.has(x.id)) || list[0];
      if (h) { map[t] = h.id; used.add(h.id); }
    });
    heroCache.set(region, map);
    return map;
  };
  const orderedSection = (topic, region) => {
    // «Головне» (найрейтинговіша, різна в розділах) — першою, решта — від найновіших за часом першої появи
    const hid = heroesFor(region)[topic];
    const list = sectionList(topic, region);
    const hero = list.find((x) => x.id === hid);
    const rest = list.filter((x) => x !== hero).sort((a, b) => new Date(startOf(b)) - new Date(startOf(a)));
    return hero ? [hero, ...rest] : rest;
  };
  const regionFor = (topic, region) => (WORLD_ONLY.has(topic) ? 'world' : region);
  const hashFor = (topic, region, id) => `#${topic}/${regionFor(topic, region)}${id ? `/${id}` : ''}`;

  // ---------------------------------------------------------------- меню: розділи × регіони
  function buildNav() {
    const L = t();
    el.labelT.textContent = L.sections;
    el.labelR.textContent = L.region;
    const icon = iconOf;
    el.sideTopics.innerHTML = '<span class="side-ind"></span>' + TOPICS.map((x) =>
      `<button class="side-link" data-topic="${x.id}" type="button">${icon(x)}<span>${esc(L[x.id])}</span><span class="count" data-ct="${x.id}"></span></button>`).join('');
    el.sideRegions.innerHTML = '<span class="side-ind"></span>' + REGIONS.map((x) =>
      `<button class="side-link" data-region="${x.id}" type="button">${icon(x)}<span>${esc(L[x.id])}</span><span class="count" data-cr="${x.id}"></span></button>`).join('');
    el.chipsT.innerHTML = '<span class="chip-ind"></span>' + TOPICS.map((x) =>
      `<button class="chip" data-topic="${x.id}" type="button">${iconOf(x)}${esc(L[x.id])}</button>`).join('');
    el.chipsR.innerHTML = '<span class="chip-ind"></span>' + REGIONS.map((x) =>
      `<button class="chip" data-region="${x.id}" type="button">${iconOf(x)}${esc(L[x.id])}</button>`).join('');
    markNav(false);
    renderCounts();
  }

  function toggleRegions() {
    // у науці, іграх і криптовалюті показуємо лише підкатегорію «Весь світ»
    const worldOnly = WORLD_ONLY.has(state.topic);
    [el.sideRegions, el.chipsR].forEach((box) => box.querySelectorAll('[data-region]').forEach((b) => {
      b.hidden = worldOnly && b.dataset.region !== 'world';
    }));
  }

  function markNav(animate = true) {
    toggleRegions();
    [el.sideTopics, el.chipsT].forEach((box) => box.querySelectorAll('[data-topic]').forEach((b) => {
      const on = b.dataset.topic === state.topic;
      b.classList.toggle('active', on);
      b.setAttribute('aria-current', on ? 'page' : 'false');
    }));
    [el.sideRegions, el.chipsR].forEach((box) => box.querySelectorAll('[data-region]').forEach((b) => {
      const on = b.dataset.region === state.region;
      b.classList.toggle('active', on);
      b.setAttribute('aria-current', on ? 'page' : 'false');
    }));
    moveIndicators(animate);
  }

  function moveIndicators(animate = true) {
    [el.sideTopics, el.sideRegions, el.chipsT, el.chipsR].forEach((box) => {
      const ind = box.querySelector('.side-ind, .chip-ind');
      const target = box.querySelector('.active');
      if (!ind || !target) return;
      if (!animate) ind.style.transition = 'none';
      ind.style.transform = `translate(${target.offsetLeft}px, ${target.offsetTop}px)`;
      ind.style.width = `${target.offsetWidth}px`;
      ind.style.height = `${target.offsetHeight}px`;
      if (!animate) requestAnimationFrame(() => { ind.style.transition = ''; });
      if (box.classList.contains('chips') && box.offsetParent) {
        const left = target.offsetLeft - (box.clientWidth - target.offsetWidth) / 2;
        box.scrollTo({ left, behavior: animate ? 'smooth' : 'auto' });
      }
    });
  }

  function renderCounts() {
    if (!state.data) return;
    // біля розділу — усі різні новини з усіх його підкатегорій (регіонів), без повторів
    const topicTotal = (topic) => {
      const ids = new Set();
      (WORLD_ONLY.has(topic) ? ['world'] : REGION_IDS).forEach((r) => sectionList(topic, r).forEach((x) => ids.add(x.id)));
      return ids.size;
    };
    document.querySelectorAll('[data-ct]').forEach((c) => { c.textContent = topicTotal(c.dataset.ct) || ''; });
    document.querySelectorAll('[data-cr]').forEach((c) => { c.textContent = sectionList(state.topic, c.dataset.cr).length || ''; });
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
  function pill(s) {
    const L = t();
    if (s.ai) return ''; // позначку «ШІ» на картках прибрано (рішення користувача)
    if (s.orig) return `<span class="tr-pill${s.tr === false ? ' raw' : ''}" title="${esc(s.tr === false ? L.noTr : `${L.machine} · ${L.original}: ${langName(s.orig.lang)}`)}">${TR_ICON}${esc(SHORT[s.orig.lang] || s.orig.lang)}</span>`;
    return '';
  }

  // фото з надрукованим текстом показуємо цілим (без обрізання), фон — розмита копія цього ж фото
  function mediaHTML(url, hasText, eager) {
    const u = esc(safeUrl(url));
    const bg = hasText ? `<div class="media-bg" style="background-image:url('${u}')"></div>` : '';
    return `<div class="media${hasText ? ' fit' : ''}">${bg}<img src="${u}" alt="" loading="${eager ? 'eager' : 'lazy'}" decoding="async" referrerpolicy="no-referrer"></div>`;
  }

  function cardHTML(s, i, hero) {
    const L = t();
    const names = s.names || [];
    const av = names.slice(0, 3).map((nm) => `<i>${esc(initials(nm).slice(0, 1))}</i>`).join('');
    const more = names.length > 2 ? ` +${names.length - 2}` : '';
    const img = s.image ? mediaHTML(s.image, s.imageText, i < 4) : '<div class="media noimg"></div>';
    return `<article class="card${hero ? ' hero' : ''}" style="--c:${esc(s.color)};--i:${i}" data-id="${esc(s.id)}" tabindex="0" role="button" aria-label="${esc(s.title)}">
      ${img}
      <div class="body">
        ${hero ? `<span class="badge-top">${esc(L.top)}</span>` : ''}
        <div class="meta"><span class="avatars">${av}</span><span>${esc(countText(s.sourceCount, L.sources))}</span><span class="sep">•</span><time datetime="${esc(startOf(s))}">${esc(when(startOf(s)))}</time>${pill(s)}</div>
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

  function sectionTitle() {
    const L = t();
    return state.region === 'world' ? L[state.topic] : `${L[state.topic]} · ${L[state.region]}`;
  }

  function renderHead(animate) {
    const L = t();
    el.title.textContent = sectionTitle();
    el.sub.textContent = L.sub(countText(state.list.length, L.stories));
    if (animate) {
      el.head.classList.remove('swap');
      void el.head.offsetWidth;
      el.head.classList.add('swap');
    }
    if (!state.openId) document.title = state.topic === 'popular' && state.region === 'world' ? 'Коло Новин' : `${sectionTitle()} — Коло Новин`;
  }

  // годинник: поточний час пристрою у форматі його регіону (12-годинний «2:30 PM» або 24-годинний «14:30»)
  const clockFmt = new Intl.DateTimeFormat(navigator.languages?.[0] || navigator.language || undefined, { hour: 'numeric', minute: '2-digit', second: '2-digit' });
  function renderUpdated() {
    const now = clockFmt.format(new Date());
    if (el.updated.textContent !== now) el.updated.textContent = now;
  }

  function renderList(animate = true) {
    if (!state.data) return;
    state.list = orderedSection(state.topic, state.region);
    renderHead(animate);
    if (!state.list.length) {
      el.grid.innerHTML = `<div class="empty"><span class="logo"></span><div>${esc(t().empty)}</div></div>`;
      return;
    }
    el.grid.innerHTML = state.list.map((s, k) => cardHTML(s, Math.min(k, 10), k === 0)).join('');
    wireImages(el.grid);
  }

  function refreshTimes() {
    document.querySelectorAll('time[datetime]').forEach((tm) => { tm.textContent = when(tm.getAttribute('datetime')); });
    renderUpdated();
  }

  // ---------------------------------------------------------------- перемикання
  let swapTimer;
  function go(topic, region, push = true) {
    topic = TOPIC_IDS.includes(topic) ? topic : 'popular';
    region = regionFor(topic, REGION_IDS.includes(region) ? region : 'world');
    const target = hashFor(topic, region);
    if (push && location.hash !== target) history.pushState({ topic, region }, '', target);
    const same = topic === state.topic && region === state.region;
    if (state.openId) closeStory(true, same);
    if (same && el.grid.children.length) return;
    state.topic = topic;
    state.region = region;
    markNav(true);
    renderCounts();
    el.grid.classList.add('leaving');
    clearTimeout(swapTimer);
    swapTimer = setTimeout(() => {
      const top = el.head.getBoundingClientRect().top + window.scrollY - 150;
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
      heroCache.clear();
      const added = oldIds.size ? sectionList(state.topic, state.region).filter((s) => !oldIds.has(s.id)).length : 0;
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
  const ARROW = '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path d="M7 17L17 7M9 7h8v8" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  const CHEV = (d) => `<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="${d === 'l' ? 'M15 5l-7 7 7 7' : 'M9 5l7 7-7 7'}" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
  const details = new Map();
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

  function infoLine(s) {
    const L = t();
    if (s.ai) return ''; // рядок «Текст написав ШІ» прибрано (рішення користувача)
    if (!s.orig) return '';
    return `<div class="d-tr">${TR_ICON}<span>${esc(s.tr === false ? L.noTr : `${L.machine} · ${L.original}: ${langName(s.orig.lang)}`)}</span>${s.tr === false ? '' : `<button type="button" id="tr-toggle">${esc(L.showOrig)}</button>`}</div>`;
  }

  function galleryHTML(images) {
    const L = t();
    if (!images.length) return '<div class="gallery empty-g"></div>';
    const many = images.length > 1;
    return `<div class="gallery${many ? '' : ' single'}" id="gallery">
      <div class="g-track" id="g-track">${images.map((im, k) => `
        <figure class="g-item${im.t ? ' fit' : ''}">${im.t ? `<div class="media-bg" style="background-image:url('${esc(safeUrl(im.u))}')"></div>` : ''}<img src="${esc(safeUrl(im.u))}" alt="" loading="${k < 2 ? 'eager' : 'lazy'}" decoding="async" referrerpolicy="no-referrer">
          <figcaption>${esc(L.photo)}: ${esc(im.s)}</figcaption></figure>`).join('')}
      </div>
      <button class="g-nav prev" type="button" data-g="-1" aria-label="${esc(L.prev)}">${CHEV('l')}</button>
      <button class="g-nav next" type="button" data-g="1" aria-label="${esc(L.next)}">${CHEV('r')}</button>
      <div class="g-count" id="g-count">1 / ${images.length}</div>
      <div class="g-dots" id="g-dots">${images.map((_, k) => `<i class="${k ? '' : 'on'}"></i>`).join('')}</div>
    </div>`;
  }

  function wireGallery() {
    const track = $('g-track');
    const g = $('gallery');
    if (!track || !g) return;
    const figs = () => [...track.querySelectorAll('.g-item')];
    let index = 0;
    const show = (k) => {
      const n = figs().length;
      index = Math.max(0, Math.min(n - 1, k));
      track.scrollTo({ left: index * track.clientWidth, behavior: 'smooth' });
    };
    function sync() {
      const n = figs().length;
      if (!n) { g.classList.add('empty-g'); g.innerHTML = ''; return; }
      const k = Math.min(n - 1, Math.round(track.scrollLeft / Math.max(track.clientWidth, 1)));
      index = k;
      const cnt = $('g-count');
      if (cnt) cnt.textContent = `${k + 1} / ${n}`;
      const dots = $('g-dots');
      if (dots) {
        while (dots.children.length > n) dots.lastChild.remove();
        [...dots.children].forEach((d, i) => d.classList.toggle('on', i === k));
      }
      g.classList.toggle('single', n < 2);
    }
    track.querySelectorAll('img').forEach((img) => {
      const ok = () => img.classList.add('ok');
      const bad = () => { img.closest('.g-item').remove(); sync(); };
      if (img.complete && img.naturalWidth) ok();
      else if (img.complete) bad();
      else { img.addEventListener('load', ok, { once: true }); img.addEventListener('error', bad, { once: true }); }
    });
    track.addEventListener('scroll', () => requestAnimationFrame(sync), { passive: true });
    g.addEventListener('click', (e) => {
      const b = e.target.closest('[data-g]');
      if (b) show(index + Number(b.dataset.g));
    });
    // тачпад: вертикальне гортання завжди гортає сторінку, горизонтальний свайп перемикає фото.
    // Один свайп = одне фото. Після свайпу тачпад ще якийсь час шле «інерційні» події, які лише
    // СЛАБШАЮТЬ — їх ігноруємо. Новий свайп видно за різким ПОСИЛЕННЯМ руху (або після паузи).
    let acc = 0;
    let fired = false;
    let firedAt = 0;
    let lastAbs = 0;
    let quiet;
    track.addEventListener('wheel', (e) => {
      if (Math.abs(e.deltaX) <= Math.abs(e.deltaY)) return;
      e.preventDefault();
      const a = Math.abs(e.deltaX);
      clearTimeout(quiet);
      quiet = setTimeout(() => { acc = 0; fired = false; lastAbs = 0; }, 160);
      if (fired && Date.now() - firedAt > 280 && a > lastAbs + 6 && a > 10) {
        fired = false; // рух посилився — це новий свайп, а не інерція
        acc = 0;
      }
      lastAbs = a;
      if (fired) return;
      acc += e.deltaX;
      if (Math.abs(acc) < 30) return;
      fired = true;
      firedAt = Date.now();
      show(index + (acc > 0 ? 1 : -1));
    }, { passive: false });
    sync();
  }

  function sourcesHTML(list) {
    // лише посилання: назва видання + стрілка (рішення користувача)
    const L = t();
    return list.filter((x) => x.url && x.url !== '#').map((x, k) => `
      <a class="src-link" style="--k:${k}" href="${esc(safeUrl(x.url))}" target="_blank" rel="noopener noreferrer" title="${esc(L.readAt)} ${esc(x.name)}">${esc(x.name)}${ARROW}</a>`).join('');
  }

  function bodyHTML(s, d) {
    const L = t();
    if (d && d.ai) {
      return `<p class="sp-lead">${esc(d.ai.lead)}</p>
        <div class="sp-body">${d.ai.body.map((p) => `<p>${esc(p)}</p>`).join('')}</div>
        ${d.ai.points && d.ai.points.length ? `<aside class="sp-points"><h2>${esc(L.points)}</h2><ul>${d.ai.points.map((p) => `<li>${esc(p)}</li>`).join('')}</ul></aside>` : ''}`;
    }
    const text = (d && d.text && d.text.length > (s.summary || '').length) ? d.text : (s.summary || '');
    return `<p class="sp-lead" id="sp-lead">${esc(text)}</p>${s.ai ? '' : `<p class="sp-desc-note">${esc(L.descBy)}</p>`}`;
  }

  function relatedHTML(s) {
    const topic = state.topic !== 'popular' && (s.topics || []).includes(state.topic) ? state.topic : 'popular';
    const region = s.cats.includes(state.region) ? state.region : 'world';
    return sectionList(topic, region).filter((x) => x.id !== s.id).slice(0, 6).map((x, k) => cardHTML(x, k, false)).join('');
  }

  function storyPills(s) {
    const L = t();
    const tp = (s.topics || []).map((id) => {
      const x = TOPICS.find((y) => y.id === id);
      return `<button class="sp-pill" type="button" data-topic="${id}" data-go="1">${x ? iconOf(x) : ''}${esc(L[id])}</button>`;
    });
    const rg = s.cats.filter((c) => c !== 'world' && REGION_IDS.includes(c)).map((id) => {
      const x = REGIONS.find((y) => y.id === id);
      return `<button class="sp-pill" type="button" data-region="${id}" data-go="1">${x ? iconOf(x) : ''}${esc(L[id])}</button>`;
    });
    return tp.concat(rg).join('');
  }

  async function openStory(id, push = true) {
    const s = state.data && state.data.stories.find((x) => x.id === id);
    const L = t();
    const token = ++storyToken;
    if (!state.openId) listScroll = window.scrollY;
    state.openId = id;
    if (push) history.pushState({ story: id }, '', hashFor(state.topic, state.region, id));
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
      <div class="sp-top"><button class="sp-back" type="button" data-back>${CHEV('l')}${esc(L.back)}</button><div class="sp-pills">${storyPills(s)}</div></div>
      <header class="sp-head">
        <div class="meta"><span class="avatars">${(s.names || []).slice(0, 3).map((n) => `<i>${esc(initials(n).slice(0, 1))}</i>`).join('')}</span><span>${esc(countText(s.sourceCount, L.sources))}</span><span class="sep">•</span><time datetime="${esc(startOf(s))}">${esc(when(startOf(s)))}</time></div>
        <h1 id="sp-title">${esc(s.title)}</h1>
        ${infoLine(s)}
      </header>
      <div id="sp-gallery">${galleryHTML(s.image ? [{ u: s.image, s: (s.names || [''])[0], t: s.imageText ? 1 : 0 }] : [])}</div>
      <div id="sp-text">${bodyHTML(s, null)}</div>
      <section class="sp-sources" id="sp-sources"><h2>${esc(L.srcTitle)}</h2><div class="sp-skel"></div></section>
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
      $('sp-text').innerHTML = bodyHTML(s, d);
      $('sp-sources').innerHTML = `<h2>${esc(L.srcTitle)}</h2><div class="sp-src-list">${sourcesHTML(d.sources)}</div>`;
      wireToggle(s, d);
    } catch (e) {
      if (token !== storyToken) return;
      $('sp-sources').innerHTML = `<h2>${esc(L.srcTitle)}</h2><div class="sp-src-list">${sourcesHTML((s.names || []).map((n) => ({ name: n, title: '', url: '#', time: s.time, lang: state.lang })))}</div>`;
    }
  }

  function wireToggle(s, d) {
    const toggle = $('tr-toggle');
    if (!toggle || !s.orig) return;
    const L = t();
    let orig = false;
    toggle.addEventListener('click', () => {
      orig = !orig;
      const h = $('sp-title');
      const lead = $('sp-lead');
      h.textContent = orig ? s.orig.title : s.title;
      h.lang = orig ? s.orig.lang : '';
      if (lead) lead.textContent = orig ? (s.orig.text || s.orig.summary || '') : ((d && d.text) || s.summary || '');
      [h, lead].filter(Boolean).forEach((n) => { n.classList.remove('swap-in'); void n.offsetWidth; n.classList.add('swap-in'); });
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
    else { closeStory(true); history.pushState({}, '', hashFor(state.topic, state.region)); }
  }

  // ---------------------------------------------------------------- маршрути: #розділ/регіон[/id]
  function parseHash() {
    const [a, b, c] = location.hash.replace('#', '').split('/');
    const topic = TOPIC_IDS.includes(a) ? a : 'popular';
    return { topic, region: regionFor(topic, REGION_IDS.includes(b) ? b : 'world'), id: c || null };
  }

  function route() {
    const r = parseHash();
    if (r.id && state.data) {
      if (r.topic !== state.topic || r.region !== state.region) {
        state.topic = r.topic; state.region = r.region; markNav(false); renderCounts(); renderList(false);
      }
      if (state.openId !== r.id) openStory(r.id, false);
    } else {
      const same = r.topic === state.topic && r.region === state.region;
      if (state.openId) closeStory(true, same);
      if (!same) go(r.topic, r.region, false);
    }
  }

  // ---------------------------------------------------------------- події
  document.addEventListener('click', (e) => {
    const tb = e.target.closest('[data-topic]');
    if (tb) {
      // зі сторінки історії розділ відкриваємо для «Весь світ», щоб новин було більше
      go(tb.dataset.topic, tb.dataset.go ? 'world' : state.region);
      return;
    }
    const rb = e.target.closest('[data-region]');
    if (rb) { go(rb.dataset.go ? 'popular' : state.topic, rb.dataset.region); return; }
    const langBtn = e.target.closest('[data-lang]');
    if (langBtn) { setLang(langBtn.dataset.lang); return; }
    if (e.target.closest('[data-back]')) { goBack(); return; }
    const card = e.target.closest('.card');
    if (card) { openStory(card.dataset.id); return; }
    if (!e.target.closest('#lang-drop')) closeLangMenu();
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') { if (state.openId) goBack(); closeLangMenu(); }
    if (state.openId && (e.key === 'ArrowLeft' || e.key === 'ArrowRight') && $('gallery')) {
      const btn = $('gallery').querySelector(e.key === 'ArrowLeft' ? '.g-nav.prev' : '.g-nav.next');
      if (btn) btn.click();
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
  document.querySelector('.brand').addEventListener('click', (e) => { e.preventDefault(); go('popular', 'world'); window.scrollTo({ top: 0, behavior: 'smooth' }); });
  window.addEventListener('popstate', route);
  window.addEventListener('resize', () => { moveIndicators(false); moveSeg(false); });
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden && state.data && Date.now() - new Date(state.data.generated).getTime() > AUTO_REFRESH_MS) load(true);
  });

  setInterval(refreshTimes, 60 * 1000);
  renderUpdated();
  setInterval(renderUpdated, 1000);
  setInterval(() => load(true), AUTO_REFRESH_MS);

  // ---------------------------------------------------------------- старт
  if (document.documentElement.dataset.theme === 'light') document.querySelector('meta[name="theme-color"]').content = '#f4f3ef';
  const start = parseHash();
  state.topic = start.topic;
  state.region = start.region;
  applyTexts();
  buildNav();
  buildLang();
  skeleton();
  load(false).then(() => { if (start.id) openStory(start.id, false); });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => { moveIndicators(false); moveSeg(false); });
})();
