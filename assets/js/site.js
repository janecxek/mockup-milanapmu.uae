/* ==========================================================================
   Milana PMU Dubai — behaviour
   No dependencies. Everything degrades to working HTML without JS.
   ========================================================================== */
(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* --- Header: stuck state + gold rule as scroll progress ---------------- */
  var header = document.querySelector('.header');
  var rule = document.querySelector('.header__rule');

  function onScroll() {
    var y = window.scrollY || document.documentElement.scrollTop;
    if (header) header.classList.toggle('is-stuck', y > 8);
    if (rule) {
      var max = document.documentElement.scrollHeight - window.innerHeight;
      var pct = max > 0 ? Math.min(100, (y / max) * 100) : 0;
      rule.style.setProperty('--progress', pct.toFixed(2) + '%');
    }
  }
  var ticking = false;
  window.addEventListener('scroll', function () {
    if (ticking) return;
    ticking = true;
    window.requestAnimationFrame(function () { onScroll(); ticking = false; });
  }, { passive: true });
  onScroll();

  /* --- Mobile drawer ----------------------------------------------------- */
  var burger = document.querySelector('.burger');
  if (burger && header) {
    burger.addEventListener('click', function () {
      var open = burger.getAttribute('aria-expanded') === 'true';
      burger.setAttribute('aria-expanded', String(!open));
      header.classList.toggle('drawer-open', !open);
    });
    header.addEventListener('click', function (e) {
      if (e.target.closest('.nav__link') && header.classList.contains('drawer-open')) {
        burger.setAttribute('aria-expanded', 'false');
        header.classList.remove('drawer-open');
      }
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && header.classList.contains('drawer-open')) {
        burger.setAttribute('aria-expanded', 'false');
        header.classList.remove('drawer-open');
        burger.focus();
      }
    });
  }

  /* --- Reveal on scroll -------------------------------------------------- */
  var revealables = document.querySelectorAll('.reveal');
  if (reduceMotion || !('IntersectionObserver' in window)) {
    revealables.forEach(function (el) { el.classList.add('is-in'); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-in');
        io.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -12% 0px', threshold: 0.08 });
    revealables.forEach(function (el) { io.observe(el); });
  }

  /* --- Before / after sliders -------------------------------------------- */
  document.querySelectorAll('.ba').forEach(function (ba) {
    var range = ba.querySelector('.ba__range');
    if (!range) return;
    var apply = function () { ba.style.setProperty('--pos', range.value + '%'); };
    range.addEventListener('input', apply);
    apply();
  });

  /* --- Pigment match (the signature interaction) -------------------------
     Selecting a skin tone shows the pigment mix a camouflage session would
     start from. Illustrative — every real match is made on the skin.        */
  var TONES = {
    'MS-01': { skin: '#F3DCCB', base: '#F0D3BC', corr: '#E8C4A9' },
    'MS-02': { skin: '#EBCBB2', base: '#E6C0A3', corr: '#DDB394' },
    'MS-03': { skin: '#DFB694', base: '#D9AC86', corr: '#CE9E78' },
    'MS-04': { skin: '#CE9E78', base: '#C69168', corr: '#B98459' },
    'MS-05': { skin: '#B5825E', base: '#AB7551', corr: '#9E6A48' },
    'MS-06': { skin: '#986748', base: '#8C5C3E', corr: '#7E5136' },
    'MS-07': { skin: '#7A4F36', base: '#6E452E', corr: '#603C28' },
    'MS-08': { skin: '#5C3A28', base: '#513122', corr: '#45291C' }
  };
  var COPY = {
    en: {
      'MS-01': 'Cool, neutral undertone. Mixed light, then built up over two sessions so the edge never reads pink.',
      'MS-02': 'Neutral undertone. A touch of warmth keeps a healed scar from going grey against the surrounding skin.',
      'MS-03': 'Warm golden undertone. Corrector balances the yellow so the area does not turn sallow as it settles.',
      'MS-04': 'Olive undertone — the one most often mismatched. Green-neutralising corrector goes in before the base.',
      'MS-05': 'Warm undertone. Base carries more red; the mix is tested on skin next to the scar before any work starts.',
      'MS-06': 'Golden-red undertone. Pigment is placed lighter than the target: it darkens as it heals.',
      'MS-07': 'Neutral-cool deep tone. Depth is built in thin layers to avoid an ashy cast.',
      'MS-08': 'Warm-red rich tone. Conservative first pass, then matched precisely at the touch-up.'
    },
    ru: {
      'MS-01': 'Холодный нейтральный подтон. Смешивается светлее и набирается за два визита, чтобы край не отдавал в розовый.',
      'MS-02': 'Нейтральный подтон. Немного тепла не даёт зажившему рубцу уйти в серый рядом с кожей.',
      'MS-03': 'Тёплый золотистый подтон. Корректор уравновешивает жёлтый, чтобы участок не потускнел.',
      'MS-04': 'Оливковый подтон — с ним чаще всего промахиваются. Сначала нейтрализующий зелёный корректор, потом база.',
      'MS-05': 'Тёплый подтон. В базе больше красного; смесь проверяется на коже рядом с рубцом до начала работы.',
      'MS-06': 'Золотисто-красный подтон. Пигмент вводится светлее цели — при заживлении он темнеет.',
      'MS-07': 'Глубокий нейтрально-холодный тон. Плотность набирается тонкими слоями, без пепельного оттенка.',
      'MS-08': 'Насыщенный тёпло-красный тон. Сдержанный первый проход, точное совпадение — на коррекции.'
    }
  };

  var matcher = document.querySelector('[data-matcher]');
  if (matcher) {
    var lang = document.documentElement.lang === 'ru' ? 'ru' : 'en';
    var buttons = matcher.querySelectorAll('.tone');
    var outSkin = matcher.querySelector('[data-out="skin"]');
    var outBase = matcher.querySelector('[data-out="base"]');
    var outCorr = matcher.querySelector('[data-out="corr"]');
    var outCode = matcher.querySelector('[data-out="code"]');
    var outNote = matcher.querySelector('[data-out="note"]');

    var select = function (btn) {
      var code = btn.getAttribute('data-tone');
      var t = TONES[code];
      if (!t) return;
      buttons.forEach(function (b) { b.setAttribute('aria-pressed', String(b === btn)); });
      if (outSkin) outSkin.style.backgroundColor = t.skin;
      if (outBase) outBase.style.backgroundColor = t.base;
      if (outCorr) outCorr.style.backgroundColor = t.corr;
      if (outCode) outCode.textContent = code;
      if (outNote) outNote.textContent = COPY[lang][code] || '';
    };

    buttons.forEach(function (btn) { btn.addEventListener('click', function () { select(btn); }); });
    var initial = matcher.querySelector('.tone[aria-pressed="true"]') || buttons[0];
    if (initial) select(initial);
  }


  /* --- Booking form -> prefilled WhatsApp message ------------------------
     No backend: the form composes the message and hands it to WhatsApp.     */
  var waForm = document.querySelector('[data-wa-form]');
  if (waForm) {
    waForm.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var base = waForm.getAttribute('action').split('?')[0];
      var get = function (n) {
        var el = waForm.elements[n];
        return el && el.value ? el.value.trim() : '';
      };
      var L = document.documentElement.lang === 'ru'
        ? { hi: 'Здравствуйте, Милана!', name: 'Имя', phone: 'Телефон',
            service: 'Процедура', area: 'Район', msg: 'Комментарий' }
        : { hi: 'Hi Milana!', name: 'Name', phone: 'Phone',
            service: 'Treatment', area: 'Area', msg: 'Notes' };
      var lines = [L.hi];
      [['name', L.name], ['phone', L.phone], ['service', L.service],
       ['area', L.area], ['message', L.msg]].forEach(function (pair) {
        var v = get(pair[0]);
        if (v) lines.push(pair[1] + ': ' + v);
      });
      window.open(base + '?text=' + encodeURIComponent(lines.join('\n')), '_blank', 'noopener');
    });
  }

  /* --- Footer year ------------------------------------------------------- */
  document.querySelectorAll('[data-year]').forEach(function (el) {
    el.textContent = String(new Date().getFullYear());
  });
})();
