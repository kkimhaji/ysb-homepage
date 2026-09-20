/* Yonsei OM — site.js */
(function () {
  'use strict';

  var LANG_KEY = 'omysb-lang';
  var THEME_KEY = 'omysb-theme';
  var root = document.documentElement;

  /* ---------- language ---------- */
  function applyLang(lang) {
    root.setAttribute('data-lang', lang);
    root.setAttribute('lang', lang === 'en' ? 'en' : 'ko');
    try { localStorage.setItem(LANG_KEY, lang); } catch (e) {}
    var t = document.body.getAttribute(lang === 'en' ? 'data-title-en' : 'data-title-ko');
    if (t) document.title = t;
    document.querySelectorAll('[data-lang-btn]').forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.getAttribute('data-lang-btn') === lang));
    });
    /* placeholder 는 속성이라 CSS 로 바꿀 수 없다 */
    document.querySelectorAll('[data-ph-ko]').forEach(function (el) {
      var v = el.getAttribute(lang === 'en' ? 'data-ph-en' : 'data-ph-ko');
      if (v) el.setAttribute('placeholder', v);
    });
  }
  document.querySelectorAll('[data-lang-btn]').forEach(function (b) {
    b.addEventListener('click', function () { applyLang(b.getAttribute('data-lang-btn')); });
  });
  applyLang(root.getAttribute('data-lang') || 'ko');

  /* ---------- theme ---------- */
  function applyTheme(mode) {
    if (mode === 'auto') root.removeAttribute('data-theme');
    else root.setAttribute('data-theme', mode);
    try { localStorage.setItem(THEME_KEY, mode); } catch (e) {}
  }
  function currentIsDark() {
    var m = root.getAttribute('data-theme');
    if (m) return m === 'dark';
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  }
  var themeBtn = document.querySelector('[data-theme-btn]');
  if (themeBtn) {
    themeBtn.addEventListener('click', function () {
      applyTheme(currentIsDark() ? 'light' : 'dark');
    });
  }

  /* ---------- header ---------- */
  var hdr = document.querySelector('.hdr');
  if (hdr) {
    var onScroll = function () { hdr.classList.toggle('is-stuck', window.scrollY > 8); };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  var burger = document.querySelector('[data-burger]');
  var nav = document.querySelector('.nav');
  if (burger && nav) {
    burger.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      burger.setAttribute('aria-expanded', String(open));
    });
    nav.addEventListener('click', function (e) {
      if (e.target.closest('a')) { nav.classList.remove('is-open'); burger.setAttribute('aria-expanded', 'false'); }
    });
  }

  /* ---------- reveal on scroll ---------- */
  var rvs = document.querySelectorAll('.rv');
  if ('IntersectionObserver' in window && rvs.length) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        var el = en.target;
        var d = parseInt(el.getAttribute('data-delay') || '0', 10);
        setTimeout(function () { el.classList.add('in'); }, d);
        io.unobserve(el);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    rvs.forEach(function (el) { io.observe(el); });
  } else {
    rvs.forEach(function (el) { el.classList.add('in'); });
  }
  /* 안전장치: 어떤 이유로든 관찰이 동작하지 않으면 강제로 노출 */
  setTimeout(function () {
    rvs.forEach(function (el) { el.classList.add('in'); });
  }, 2600);

  /* ---------- 숫자 세어 올리기 ----------
     화면에 들어올 때 0부터 실제 값까지 굴러간다. 마크업에는 처음부터 실제
     값이 적혀 있어서 자바스크립트가 꺼져 있어도 숫자는 제대로 보인다.
     움직임을 줄이도록 설정한 사용자에게는 굴리지 않는다. */
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var nums = document.querySelectorAll('[data-count]');
  if (nums.length && !reduce && 'IntersectionObserver' in window) {
    var io2 = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        var el = en.target, target = parseInt(el.getAttribute('data-count'), 10);
        var t0 = null, done = false;
        function finish() { if (!done) { done = true; el.textContent = target; } }
        function step(ts) {
          if (done) return;
          if (!t0) t0 = ts;
          var p = Math.min((ts - t0) / 1100, 1);
          if (p < 1) { el.textContent = Math.round(target * (1 - Math.pow(1 - p, 3)));
                       requestAnimationFrame(step); }
          else { finish(); }
        }
        requestAnimationFrame(step);
        /* 안전장치: 굴리는 도중 멈추더라도 2초 뒤에는 정확한 값을 보여 준다.
           틀린 숫자가 남는 것보다 굴러가는 연출을 포기하는 편이 낫다. */
        setTimeout(finish, 2000);
        io2.unobserve(el);
      });
    }, { threshold: 0.4 });
    nums.forEach(function (el) { io2.observe(el); });
  }

  /* ---------- generic filter/search ---------- */
  function wireFilter(scopeSel) {
    var scope = document.querySelector(scopeSel);
    if (!scope) return;
    var input = scope.querySelector('[data-search]');
    var segs = scope.querySelectorAll('[data-filter]');
    var items = scope.querySelectorAll('[data-item]');
    var empty = scope.querySelector('[data-empty]');
    var groups = scope.querySelectorAll('[data-group]');
    var state = { q: '', f: 'all' };

    function run() {
      var shown = 0;
      items.forEach(function (el) {
        var tags = (el.getAttribute('data-tags') || '').toLowerCase();
        var text = (el.textContent || '').toLowerCase();
        var okF = state.f === 'all' || tags.indexOf(state.f) > -1;
        var okQ = !state.q || text.indexOf(state.q) > -1;
        var ok = okF && okQ;
        el.style.display = ok ? '' : 'none';
        if (ok) shown++;
      });
      groups.forEach(function (g) {
        var any = Array.prototype.some.call(g.querySelectorAll('[data-item]'), function (el) {
          return el.style.display !== 'none';
        });
        g.style.display = any ? '' : 'none';
      });
      if (empty) empty.style.display = shown ? 'none' : '';
    }
    if (input) input.addEventListener('input', function () { state.q = input.value.trim().toLowerCase(); run(); });
    segs.forEach(function (b) {
      b.addEventListener('click', function () {
        state.f = b.getAttribute('data-filter');
        segs.forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
        run();
      });
    });
    run();
  }
  wireFilter('[data-scope="alumni"]');
  wireFilter('[data-scope="students"]');
  wireFilter('[data-scope="seminars"]');
  wireFilter('[data-scope="community"]');

  /* ---------- faculty photo slots (hide broken images) ---------- */
  document.querySelectorAll('.fcard__ph img').forEach(function (img) {
    img.addEventListener('error', function () { img.remove(); });
  });

  /* ---------- year ---------- */
  document.querySelectorAll('[data-year-now]').forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });
})();
