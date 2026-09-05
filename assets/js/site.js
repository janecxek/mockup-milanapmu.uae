/* ==========================================================================
   Milana PMU Dubai — behaviour

   Progressive enhancement throughout: every feature here has a working
   plain-HTML fallback. If Lenis fails to load the page scrolls natively; if
   this script never runs, links navigate, the FAQ opens and Book goes
   straight to WhatsApp.
   ========================================================================== */
(function () {
  'use strict';

  var html = document.documentElement;
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var lenis = null;

  /* --- Entry veil ---------------------------------------------------------
     The head script tagged <html> before first paint, so the incoming page is
     already covered. Lift the cover once we are here.                       */
  function clearEntry() {
    if (!html.classList.contains('is-entering')) return;
    var hold = html.classList.contains('is-entering-lang') ? 260 : 0;
    window.setTimeout(function () {
      requestAnimationFrame(function () {
        html.classList.remove('is-entering', 'is-entering-lang');
      });
    }, hold);
  }

  /* --- Lenis: weighted smooth scroll --------------------------------------
     Skipped entirely under reduced motion, and if the CDN is unreachable the
     page keeps its native scroll.                                           */
  function initLenis() {
    if (reduceMotion || typeof Lenis === 'undefined') return null;
    var instance = new Lenis({
      lerp: 0.085,
      smoothWheel: true,
      wheelMultiplier: 1,
      touchMultiplier: 1.5
    });
    function raf(t) { instance.raf(t); requestAnimationFrame(raf); }
    requestAnimationFrame(raf);
    return instance;
  }

  function lockScroll(on) {
    if (lenis) { on ? lenis.stop() : lenis.start(); }
    html.classList.toggle('is-locked', !!on);
  }

  /* Header offset for anchor jumps — measured, so a heading never lands
     underneath the fixed bar on any breakpoint. */
  function headerOffset() {
    var header = document.querySelector('.header');
    return -((header ? header.offsetHeight : 80) + 8);
  }

  function scrollToEl(el) {
    if (lenis) { lenis.scrollTo(el, { offset: headerOffset() }); return; }
    var y = el.getBoundingClientRect().top + window.scrollY + headerOffset();
    window.scrollTo({ top: y, behavior: reduceMotion ? 'auto' : 'smooth' });
  }

  /* --- Header: stuck state + gold rule as scroll progress ---------------- */
  function updateHeader() {
    var header = document.querySelector('.header');
    var rule = document.querySelector('.header__rule');
    var y = window.scrollY || document.documentElement.scrollTop;
    if (header) header.classList.toggle('is-stuck', y > 8);
    if (rule) {
      var max = document.documentElement.scrollHeight - window.innerHeight;
      var pct = max > 0 ? Math.min(100, (y / max) * 100) : 0;
      rule.style.setProperty('--progress', pct.toFixed(2) + '%');
    }
  }

  /* --- Navigation: veil, then go ------------------------------------------
     `mode` is 'page' for an ordinary link and 'lang' for a language change,
     which gets the blur, the mark and the progress bar.                     */
  function leaveTo(url, mode) {
    var veil = document.getElementById('veil');
    try { sessionStorage.setItem('pmu-enter', mode); } catch (e) {}
    if (!veil || reduceMotion) { window.location.href = url; return; }
    veil.classList.add('is-on');
    if (mode === 'lang') veil.classList.add('veil--loading');
    window.setTimeout(function () { window.location.href = url; },
                      mode === 'lang' ? 680 : 200);
  }

  function isPlainLeftClick(e) {
    return !(e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey);
  }

  /* --- Per-page wiring ---------------------------------------------------- */
  function wire() {
    updateHeader();

    /* Mobile drawer */
    var burger = document.querySelector('.burger');
    var header = document.querySelector('.header');
    if (burger && header) {
      burger.addEventListener('click', function () {
        var open = burger.getAttribute('aria-expanded') === 'true';
        burger.setAttribute('aria-expanded', String(!open));
        header.classList.toggle('drawer-open', !open);
        lockScroll(!open);
      });
    }

    /* Reveal on scroll */
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

    /* Before / after sliders */
    document.querySelectorAll('.ba').forEach(function (ba) {
      var range = ba.querySelector('.ba__range');
      if (!range) return;
      var apply = function () { ba.style.setProperty('--pos', range.value + '%'); };
      range.addEventListener('input', apply);
      apply();
    });

    initMatcher();
    initFaq();
    initDialog();

    document.querySelectorAll('[data-year]').forEach(function (el) {
      el.textContent = String(new Date().getFullYear());
    });
  }

  /* --- FAQ: animated disclosure -------------------------------------------
     <details> remains the source of truth, so keyboard and screen-reader
     behaviour is untouched; only the height is animated.                    */
  function initFaq() {
    document.querySelectorAll('.faq details').forEach(function (d) {
      var summary = d.querySelector('summary');
      var panel = d.querySelector('summary + div');
      if (!summary || !panel || summary.dataset.wired) return;
      summary.dataset.wired = '1';

      summary.addEventListener('click', function (e) {
        if (reduceMotion || typeof panel.animate !== 'function') return;
        e.preventDefault();
        if (d.dataset.animating) return;
        d.dataset.animating = '1';

        var opening = !d.open;
        if (opening) d.open = true;
        var h = panel.scrollHeight;
        var frames = opening
          ? [{ height: '0px', opacity: 0 }, { height: h + 'px', opacity: 1 }]
          : [{ height: h + 'px', opacity: 1 }, { height: '0px', opacity: 0 }];

        var anim = panel.animate(frames, {
          duration: opening ? 340 : 260,
          easing: opening ? 'cubic-bezier(.16,1,.3,1)' : 'cubic-bezier(.22,.61,.36,1)'
        });
        anim.onfinish = function () {
          if (!opening) d.open = false;
          delete d.dataset.animating;
          if (lenis) lenis.resize();
        };
      });
    });
  }

  /* --- Booking dialog -----------------------------------------------------
     The trigger is a real WhatsApp link; without JS or <dialog> support it
     simply opens WhatsApp, which is what it promises.                       */
  function initDialog() {
    var dlg = document.getElementById('book-dialog');
    if (!dlg || typeof dlg.showModal !== 'function') return;
    var header = document.querySelector('.header');
    var lastFocus = null;

    function close() {
      if (dlg.classList.contains('is-closing')) return;
      dlg.classList.add('is-closing');
      window.setTimeout(function () {
        dlg.classList.remove('is-closing');
        dlg.close();
        lockScroll(false);
        if (lastFocus) lastFocus.focus();
      }, reduceMotion ? 0 : 200);
    }

    document.querySelectorAll('[data-book]').forEach(function (trigger) {
      if (trigger.dataset.wired) return;
      trigger.dataset.wired = '1';
      trigger.addEventListener('click', function (e) {
        if (!isPlainLeftClick(e)) return;
        e.preventDefault();
        lastFocus = trigger;
        if (header && header.classList.contains('drawer-open')) {
          header.classList.remove('drawer-open');
          var b = document.querySelector('.burger');
          if (b) b.setAttribute('aria-expanded', 'false');
        }
        dlg.showModal();
        lockScroll(true);
      });
    });

    if (dlg.dataset.wired) return;
    dlg.dataset.wired = '1';
    dlg.querySelectorAll('[data-close]').forEach(function (b) {
      b.addEventListener('click', close);
    });
    dlg.addEventListener('cancel', function (e) { e.preventDefault(); close(); });
    dlg.addEventListener('click', function (e) {
      if (e.target === dlg) close();          /* click on the backdrop */
    });
  }

  /* --- Pigment match ------------------------------------------------------
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

  function initMatcher() {
    var matcher = document.querySelector('[data-matcher]');
    if (!matcher) return;
    var lang = html.lang === 'ru' ? 'ru' : 'en';
    var buttons = matcher.querySelectorAll('.tone');
    var outSkin = matcher.querySelector('[data-out="skin"]');
    var outBase = matcher.querySelector('[data-out="base"]');
    var outCorr = matcher.querySelector('[data-out="corr"]');
    var outCode = matcher.querySelector('[data-out="code"]');
    var outNote = matcher.querySelector('[data-out="note"]');

    function select(btn) {
      var code = btn.getAttribute('data-tone');
      var t = TONES[code];
      if (!t) return;
      buttons.forEach(function (b) { b.setAttribute('aria-pressed', String(b === btn)); });
      if (outSkin) outSkin.style.backgroundColor = t.skin;
      if (outBase) outBase.style.backgroundColor = t.base;
      if (outCorr) outCorr.style.backgroundColor = t.corr;
      if (outCode) outCode.textContent = code;
      if (outNote) outNote.textContent = COPY[lang][code] || '';
    }

    buttons.forEach(function (btn) { btn.addEventListener('click', function () { select(btn); }); });
    var initial = matcher.querySelector('.tone[aria-pressed="true"]') || buttons[0];
    if (initial) select(initial);
  }

  /* --- One-time global setup --------------------------------------------- */
  function boot() {
    if (window.__pmuBooted) { wire(); clearEntry(); return; }
    window.__pmuBooted = true;

    lenis = initLenis();
    if (lenis) {
      lenis.on('scroll', updateHeader);
    } else {
      var ticking = false;
      window.addEventListener('scroll', function () {
        if (ticking) return;
        ticking = true;
        requestAnimationFrame(function () { updateHeader(); ticking = false; });
      }, { passive: true });
    }

    /* Escape closes the mobile drawer (the dialog handles its own) */
    document.addEventListener('keydown', function (e) {
      var header = document.querySelector('.header');
      if (e.key !== 'Escape' || !header || !header.classList.contains('drawer-open')) return;
      var burger = document.querySelector('.burger');
      header.classList.remove('drawer-open');
      if (burger) { burger.setAttribute('aria-expanded', 'false'); burger.focus(); }
      lockScroll(false);
    });

    /* Every internal navigation goes through the veil */
    document.addEventListener('click', function (e) {
      var a = e.target.closest && e.target.closest('a[href]');
      if (!a || !isPlainLeftClick(e)) return;
      if (a.target === '_blank' || a.hasAttribute('download') || a.hasAttribute('data-book')) return;

      var href = a.getAttribute('href') || '';
      if (href.charAt(0) === '#') {                    /* same-page anchor */
        var el = document.getElementById(href.slice(1));
        if (!el) return;
        e.preventDefault();
        scrollToEl(el);
        if (history.replaceState) history.replaceState(null, '', href);
        return;
      }
      var url = new URL(a.href, location.href);
      if (url.origin !== location.origin) return;
      if (url.pathname === location.pathname && url.hash) return;   /* let the browser handle it */

      e.preventDefault();
      var header = document.querySelector('.header');
      if (header) header.classList.remove('drawer-open');
      leaveTo(a.href, a.hasAttribute('data-lang') ? 'lang' : 'page');
    });

    /* Coming back through the bfcache must not leave the veil up */
    window.addEventListener('pageshow', function (ev) {
      if (!ev.persisted) return;
      var veil = document.getElementById('veil');
      if (veil) veil.classList.remove('is-on', 'veil--loading');
      html.classList.remove('is-entering', 'is-entering-lang');
      lockScroll(false);
    });

    /* The booking form composes a WhatsApp message; no backend involved. */
    var waForm = document.querySelector('[data-wa-form]');
    if (waForm) {
      waForm.addEventListener('submit', function (ev) {
        ev.preventDefault();
        var base = waForm.getAttribute('action').split('?')[0];
        var get = function (n) {
          var el = waForm.elements[n];
          return el && el.value ? el.value.trim() : '';
        };
        var L = html.lang === 'ru'
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

    wire();
    clearEntry();

    if (location.hash.length > 1) {
      var target = document.getElementById(location.hash.slice(1));
      if (target) window.setTimeout(function () { scrollToEl(target); }, 60);
    }
  }

  window.__initSite = boot;
  boot();
})();
