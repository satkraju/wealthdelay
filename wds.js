/* WealthDelay Score Engine v1.0
 * Calculates WD Score (1-10), injects score UI, generates PNG share card
 * Hooks to #r-hero via MutationObserver - no per-page JS changes needed
 */
(function () {
  'use strict';

  var CIRC = 2 * Math.PI * 46; // SVG arc circumference (r=46)

  /* ─── Score Calculation ──────────────────────────────────────── */
  function calcScore(fv) {
    if (!fv || fv <= 0) return 0;
    var raw = Math.log10(Math.max(fv, 500) / 1000) * 3.5 + 1;
    return Math.min(10, Math.max(0.5, parseFloat(raw.toFixed(1))));
  }

  function scoreTheme(s) {
    if (s >= 9) return { label: 'Severe',     color: '#ff3b30', bg: '#fff1f0' };
    if (s >= 7) return { label: 'High',        color: '#ff6b00', bg: '#fff7ed' };
    if (s >= 5) return { label: 'Significant', color: '#ff9500', bg: '#fffbeb' };
    if (s >= 3) return { label: 'Moderate',    color: '#d97706', bg: '#fefce8' };
    return       { label: 'Low',             color: '#16a34a', bg: '#f0fdf4' };
  }

  function scoreDesc(s, habit) {
    var h = habit || 'This habit';
    if (s >= 9) return h + ' is severely delaying your financial freedom. One of the highest-impact changes you can make.';
    if (s >= 7) return h + ' causes significant wealth delay. Small changes here produce major long-term gains.';
    if (s >= 5) return 'A meaningful drag on your wealth. Worth optimising as part of your financial strategy.';
    if (s >= 3) return 'Moderate impact. Conscious choices here compound quietly over time.';
    return 'Relatively low financial impact. Focus energy on higher-score habits first.';
  }

  /* ─── Parse dollar string ────────────────────────────────────── */
  function parseFV(text) {
    if (!text) return 0;
    var m = text.replace(/[,$\s]/g, '').match(/^(\d+(?:\.\d+)?)(K|M|B)?$/i);
    if (!m) return 0;
    var n = parseFloat(m[1]);
    var mult = { k: 1e3, m: 1e6, b: 1e9 };
    if (m[2]) n *= (mult[m[2].toLowerCase()] || 1);
    return n;
  }

  function fmtFV(n) {
    if (n >= 1e6) return '$' + (n / 1e6).toFixed(1) + 'M';
    if (n >= 1e3) return '$' + Math.round(n / 1e3) + 'K';
    return '$' + Math.round(n).toLocaleString();
  }

  /* ─── Styles ─────────────────────────────────────────────────── */
  function injectStyles() {
    if (document.getElementById('wds-css')) return;
    var s = document.createElement('style');
    s.id = 'wds-css';
    var rules = [
      '#wds-root{background:#fff;border-radius:18px;box-shadow:0 8px 32px rgba(0,0,0,.08),0 2px 8px rgba(0,0,0,.04);border:1px solid rgba(0,0,0,.08);overflow:hidden;}',
      '#wds-head{padding:14px 20px;border-bottom:1px solid rgba(0,0,0,.08);display:flex;align-items:center;justify-content:space-between;}',
      '#wds-head-title{font-size:13px;font-weight:600;color:#3d3d3f;letter-spacing:-.01em;}',
      '#wds-tm{font-size:10px;font-weight:700;color:#aeaeb2;letter-spacing:.06em;}',
      '#wds-body{padding:20px;display:grid;grid-template-columns:130px 1fr;gap:20px;align-items:center;}',
      '@media(max-width:480px){#wds-body{grid-template-columns:1fr;}}',
      '#wds-ring-wrap{position:relative;width:120px;height:120px;}',
      '#wds-ring-wrap svg{width:120px;height:120px;display:block;}',
      '#wds-ring-inner{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;}',
      '#wds-num{font-size:32px;font-weight:800;letter-spacing:-.06em;line-height:1;font-variant-numeric:tabular-nums;transition:color .4s;}',
      '#wds-denom{font-size:12px;color:#aeaeb2;font-weight:600;margin-top:1px;}',
      '#wds-badge{display:inline-flex;align-items:center;font-size:11px;font-weight:700;letter-spacing:.04em;padding:3px 10px;border-radius:99px;border:1px solid transparent;text-transform:uppercase;margin-bottom:8px;transition:all .4s;}',
      '#wds-desc{font-size:13px;color:#6e6e73;line-height:1.6;letter-spacing:-.005em;margin-bottom:14px;}',
      '#wds-dl{display:inline-flex;align-items:center;gap:7px;font-size:13px;font-weight:700;color:#fff;background:#16a34a;border:none;border-radius:9px;padding:9px 16px;cursor:pointer;font-family:inherit;letter-spacing:-.01em;transition:all .15s;}',
      '#wds-dl:hover:not(:disabled){background:#14532d;transform:translateY(-1px);}',
      '#wds-dl:disabled{background:#aeaeb2;cursor:default;transform:none;}',
      '#wds-tw{display:inline-flex;align-items:center;gap:7px;font-size:13px;font-weight:700;color:#fff;background:#000;border:none;border-radius:9px;padding:9px 16px;cursor:pointer;font-family:inherit;letter-spacing:-.01em;transition:all .15s;margin-left:8px;}',
      '#wds-tw:hover:not(:disabled){background:#1a1a1a;transform:translateY(-1px);}',
      '#wds-tw:disabled{background:#aeaeb2;cursor:default;transform:none;}',
    ];
    s.textContent = rules.join('');
    document.head.appendChild(s);
  }

  /* ─── Build UI with DOM APIs ─────────────────────────────────── */
  function buildUI() {
    var root = document.createElement('div');
    root.id = 'wds-root';

    // Head
    var head = document.createElement('div');
    head.id = 'wds-head';
    var headTitle = document.createElement('span');
    headTitle.id = 'wds-head-title';
    headTitle.textContent = 'Wealth Delay Score';
    var tm = document.createElement('span');
    tm.id = 'wds-tm';
    tm.textContent = 'WDS™';
    head.appendChild(headTitle);
    head.appendChild(tm);
    root.appendChild(head);

    // Body
    var body = document.createElement('div');
    body.id = 'wds-body';

    // Ring wrap
    var ringWrap = document.createElement('div');
    ringWrap.id = 'wds-ring-wrap';

    var svgNS = 'http://www.w3.org/2000/svg';
    var svg = document.createElementNS(svgNS, 'svg');
    svg.setAttribute('viewBox', '0 0 100 100');

    var trackCircle = document.createElementNS(svgNS, 'circle');
    trackCircle.setAttribute('cx', '50'); trackCircle.setAttribute('cy', '50');
    trackCircle.setAttribute('r', '46'); trackCircle.setAttribute('fill', 'none');
    trackCircle.setAttribute('stroke', '#f0f0f0'); trackCircle.setAttribute('stroke-width', '7');

    var arcCircle = document.createElementNS(svgNS, 'circle');
    arcCircle.id = 'wds-arc';
    arcCircle.setAttribute('cx', '50'); arcCircle.setAttribute('cy', '50');
    arcCircle.setAttribute('r', '46'); arcCircle.setAttribute('fill', 'none');
    arcCircle.setAttribute('stroke', '#16a34a'); arcCircle.setAttribute('stroke-width', '7');
    arcCircle.setAttribute('stroke-linecap', 'round');
    arcCircle.setAttribute('stroke-dasharray', CIRC.toFixed(1));
    arcCircle.setAttribute('stroke-dashoffset', CIRC.toFixed(1));
    arcCircle.style.cssText = 'transform:rotate(-90deg);transform-origin:50% 50%;transition:stroke-dashoffset 1s cubic-bezier(.4,0,.2,1),stroke .5s';

    svg.appendChild(trackCircle);
    svg.appendChild(arcCircle);
    ringWrap.appendChild(svg);

    var inner = document.createElement('div');
    inner.id = 'wds-ring-inner';
    var numEl = document.createElement('span');
    numEl.id = 'wds-num';
    numEl.textContent = '—';
    var denomEl = document.createElement('span');
    denomEl.id = 'wds-denom';
    denomEl.textContent = '/10';
    inner.appendChild(numEl);
    inner.appendChild(denomEl);
    ringWrap.appendChild(inner);
    body.appendChild(ringWrap);

    // Info column
    var info = document.createElement('div');

    var badge = document.createElement('div');
    badge.id = 'wds-badge';
    badge.textContent = '—';

    var desc = document.createElement('p');
    desc.id = 'wds-desc';
    desc.textContent = 'Calculate above to see your Wealth Delay Score.';

    // Download button
    var btn = document.createElement('button');
    btn.id = 'wds-dl';
    btn.disabled = true;

    var dlSvgNS = 'http://www.w3.org/2000/svg';
    var dlSvg = document.createElementNS(dlSvgNS, 'svg');
    dlSvg.setAttribute('width', '14'); dlSvg.setAttribute('height', '14');
    dlSvg.setAttribute('viewBox', '0 0 24 24'); dlSvg.setAttribute('fill', 'none');
    dlSvg.setAttribute('stroke', 'currentColor'); dlSvg.setAttribute('stroke-width', '2.5');
    dlSvg.setAttribute('stroke-linecap', 'round'); dlSvg.setAttribute('stroke-linejoin', 'round');
    var dlPath = document.createElementNS(dlSvgNS, 'path');
    dlPath.setAttribute('d', 'M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4');
    var dlPoly = document.createElementNS(dlSvgNS, 'polyline');
    dlPoly.setAttribute('points', '7 10 12 15 17 10');
    var dlLine = document.createElementNS(dlSvgNS, 'line');
    dlLine.setAttribute('x1', '12'); dlLine.setAttribute('y1', '15');
    dlLine.setAttribute('x2', '12'); dlLine.setAttribute('y2', '3');
    dlSvg.appendChild(dlPath); dlSvg.appendChild(dlPoly); dlSvg.appendChild(dlLine);
    btn.appendChild(dlSvg);
    btn.appendChild(document.createTextNode(' Download Share Card'));

    // Twitter share button
    var tBtn = document.createElement('button');
    tBtn.id = 'wds-tw';
    tBtn.disabled = true;
    tBtn.appendChild(document.createTextNode('𝕏 Share on X'));

    info.appendChild(badge);
    info.appendChild(desc);
    info.appendChild(btn);
    info.appendChild(tBtn);
    body.appendChild(info);
    root.appendChild(body);

    return root;
  }

  function insertUI() {
    if (document.getElementById('wds-root')) return;
    injectStyles();
    var el = buildUI();
    var insight = document.querySelector('.results .insight');
    if (insight && insight.parentNode) {
      insight.parentNode.insertBefore(el, insight.nextSibling);
    } else {
      var results = document.querySelector('.results');
      if (results) results.appendChild(el);
    }
  }

  /* ─── Update Score Display ───────────────────────────────────── */
  function updateUI(fv, habit) {
    var score  = calcScore(fv);
    var theme  = scoreTheme(score);
    var numEl  = document.getElementById('wds-num');
    var arcEl  = document.getElementById('wds-arc');
    var badge  = document.getElementById('wds-badge');
    var desc   = document.getElementById('wds-desc');
    var dlBtn  = document.getElementById('wds-dl');

    if (!numEl) { insertUI(); updateUI(fv, habit); return; }

    numEl.textContent = score.toFixed(1);
    numEl.style.color = theme.color;

    if (arcEl) {
      arcEl.style.strokeDashoffset = (CIRC - (score / 10) * CIRC).toFixed(1);
      arcEl.style.stroke = theme.color;
    }
    if (badge) {
      badge.textContent = theme.label;
      badge.style.color = theme.color;
      badge.style.background = theme.bg;
      badge.style.borderColor = theme.color + '55';
    }
    if (desc) desc.textContent = scoreDesc(score, habit);
    if (dlBtn) {
      dlBtn.disabled = false;
      dlBtn.onclick = function () { drawCard(fv, score, habit, theme); };
    }
    var twBtn = document.getElementById('wds-tw');
    if (twBtn) {
      twBtn.disabled = false;
      twBtn.onclick = function () {
        var txt = (habit || 'This habit') + ' is costing me ' + fmtFV(fv) + ' in lifetime wealth 🤯\n\nCalculate your wealth delay:';
        window.open(
          'https://twitter.com/intent/tweet?text=' + encodeURIComponent(txt) + '&url=' + encodeURIComponent('https://wealthdelay.com'),
          '_blank', 'width=550,height=420'
        );
      };
    }
  }

  /* ─── Canvas Share Card ──────────────────────────────────────── */
  function drawCard(fv, score, habit, theme) {
    var W = 1200, H = 630;
    var cv = document.createElement('canvas');
    cv.width = W; cv.height = H;
    var c = cv.getContext('2d');

    // Background
    var bg = c.createLinearGradient(0, 0, W, H);
    bg.addColorStop(0, '#07100a');
    bg.addColorStop(1, '#0d1f14');
    c.fillStyle = bg;
    c.fillRect(0, 0, W, H);

    // Dot grid
    c.fillStyle = 'rgba(255,255,255,0.022)';
    for (var gx = 40; gx < W; gx += 56)
      for (var gy = 40; gy < H; gy += 56) {
        c.beginPath();
        c.arc(gx, gy, 1.5, 0, Math.PI * 2);
        c.fill();
      }

    // Left accent stripe
    var stripe = c.createLinearGradient(0, 0, 0, H);
    stripe.addColorStop(0, theme.color);
    stripe.addColorStop(0.7, theme.color + '44');
    stripe.addColorStop(1, 'transparent');
    c.fillStyle = stripe;
    c.fillRect(0, 0, 6, H);

    // Score ring (right column)
    var cx = 880, cy = 315, R = 170;
    c.beginPath(); c.arc(cx, cy, R, 0, Math.PI * 2);
    c.strokeStyle = 'rgba(255,255,255,0.07)'; c.lineWidth = 18; c.stroke();
    c.beginPath(); c.arc(cx, cy, R, -Math.PI / 2, -Math.PI / 2 + (score / 10) * Math.PI * 2);
    c.strokeStyle = theme.color; c.lineWidth = 18; c.lineCap = 'round'; c.stroke();

    c.fillStyle = '#ffffff';
    c.font = '800 108px -apple-system,system-ui,sans-serif';
    c.textAlign = 'center'; c.textBaseline = 'middle';
    c.fillText(score.toFixed(1), cx, cy - 14);

    c.fillStyle = 'rgba(255,255,255,0.35)';
    c.font = '600 28px -apple-system,system-ui,sans-serif';
    c.fillText('/10', cx, cy + 64);

    c.fillStyle = theme.color;
    c.font = '700 20px -apple-system,system-ui,sans-serif';
    c.fillText(theme.label.toUpperCase(), cx, cy + 110);

    // Left column
    c.textAlign = 'left';

    // Logo
    c.font = '800 30px -apple-system,system-ui,sans-serif';
    c.fillStyle = '#16a34a';
    c.fillText('Wealth', 80, 72);
    var ww = c.measureText('Wealth').width;
    c.fillStyle = 'rgba(255,255,255,0.9)';
    c.fillText('Delay', 80 + ww + 5, 72);

    // Eyebrow
    c.fillStyle = 'rgba(255,255,255,0.28)';
    c.font = '600 13px -apple-system,system-ui,sans-serif';
    c.fillText('WEALTH DELAY SCORE™', 80, 158);

    // Habit name
    var habitTxt = (habit || 'This Habit').replace(/['"]/g, '').substring(0, 48);
    c.fillStyle = 'rgba(255,255,255,0.6)';
    c.font = '500 24px -apple-system,system-ui,sans-serif';
    c.fillText(habitTxt, 80, 200);

    // Big FV
    c.fillStyle = '#ffffff';
    c.font = '800 ' + (fv >= 1e6 ? 84 : 96) + 'px -apple-system,system-ui,sans-serif';
    c.fillText(fmtFV(fv), 80, 326);

    c.fillStyle = 'rgba(255,255,255,0.38)';
    c.font = '500 20px -apple-system,system-ui,sans-serif';
    c.fillText('in lifetime wealth lost', 80, 374);

    // Divider
    c.strokeStyle = 'rgba(255,255,255,0.09)'; c.lineWidth = 1;
    c.beginPath(); c.moveTo(80, 424); c.lineTo(680, 424); c.stroke();

    // CTA
    c.fillStyle = 'rgba(255,255,255,0.3)';
    c.font = '500 17px -apple-system,system-ui,sans-serif';
    c.fillText('See your hidden wealth cost at', 80, 464);
    c.fillStyle = '#16a34a';
    c.font = '700 17px -apple-system,system-ui,sans-serif';
    c.fillText('wealthdelay.com', 80, 492);

    var link = document.createElement('a');
    link.download = 'wealth-delay-score-' + score.toFixed(1) + '.png';
    link.href = cv.toDataURL('image/png');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    if (typeof gtag !== 'undefined') {
      gtag('event', 'wds_card_download', { wds_score: score, fv_lost: Math.round(fv) });
    }
  }

  /* ─── MutationObserver hook ──────────────────────────────────── */
  function getLabel() {
    var h1 = document.querySelector('.tool-h1');
    return h1 ? h1.textContent.replace(/[^\w\s$.,\-']/g, '').trim().substring(0, 44) : 'This Habit';
  }

  function hookHero() {
    var hero = document.getElementById('r-hero');
    if (!hero) return;
    function tryUpdate() {
      var fv = parseFV(hero.textContent.trim());
      if (fv > 0) updateUI(fv, getLabel());
    }
    new MutationObserver(tryUpdate).observe(hero, { characterData: true, childList: true, subtree: true });
    tryUpdate();
  }

  /* ─── Boot ───────────────────────────────────────────────────── */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { insertUI(); hookHero(); });
  } else {
    insertUI();
    hookHero();
  }
}());
