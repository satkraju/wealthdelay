/* calc-common.js — shared calculator-tool-page helpers (formatting, sliders, charts, FAQ).
   Used by Step-2 calculator pages. Each page still defines its own calc() function. */

function fmt(n) {
  if (!isFinite(n) || isNaN(n)) return '$0';
  const a = Math.abs(n);
  const sign = n < 0 ? '-' : '';
  if (a >= 1e9) return sign + '$' + (a / 1e9).toFixed(2) + 'B';
  if (a >= 1e6) return sign + '$' + (a / 1e6).toFixed(2) + 'M';
  if (a >= 1e3) return sign + '$' + (a / 1e3).toFixed(1) + 'K';
  return sign + '$' + Math.round(a).toLocaleString();
}
function fmtFull(n) {
  if (!isFinite(n) || isNaN(n)) return '$0';
  return (n < 0 ? '-$' : '$') + Math.round(Math.abs(n)).toLocaleString();
}
function fmtPct(n) { return (n * 100).toFixed(1) + '%'; }

function fvAnnuity(pmt, annualRate, years) {
  const r = annualRate / 12;
  const n = years * 12;
  if (r === 0) return pmt * n;
  return pmt * ((Math.pow(1 + r, n) - 1) / r);
}
function fvLump(pv, annualRate, years) {
  const r = annualRate / 12;
  return pv * Math.pow(1 + r, years * 12);
}

function syncSlider(id, val, pre, suf, comma, abbrev) {
  const el = document.getElementById('v-' + id);
  if (!el) return;
  let d = val;
  if (abbrev) {
    const num = Number(val);
    d = num >= 1e6 ? (num / 1e6).toFixed(1) + 'M' : num >= 1e3 ? (num / 1e3).toFixed(0) + 'K' : num;
  } else if (comma) {
    d = Number(val).toLocaleString();
  }
  el.textContent = pre + d + suf;
  const s = document.getElementById('s-' + id);
  if (s) {
    const p = ((s.value - s.min) / (s.max - s.min)) * 100;
    s.style.background = `linear-gradient(to right,#16A34A 0%,#16A34A ${p}%,#EFE8D8 ${p}%,#EFE8D8 100%)`;
  }
}

function initSliders() {
  document.querySelectorAll('input[type=range]').forEach(s => {
    const p = ((s.value - s.min) / (s.max - s.min)) * 100;
    s.style.background = `linear-gradient(to right,#16A34A 0%,#16A34A ${p}%,#EFE8D8 ${p}%,#EFE8D8 100%)`;
  });
}

function toggleFaq(el) {
  const ico = el.querySelector('.faq-ico'), ans = el.nextElementSibling, open = ans.classList.contains('open');
  document.querySelectorAll('.faq-a').forEach(a => a.classList.remove('open'));
  document.querySelectorAll('.faq-ico').forEach(i => { i.classList.remove('open'); i.textContent = '+'; });
  if (!open) { ans.classList.add('open'); ico.classList.add('open'); }
}

function animateCount(el, target, duration) {
  if (!el || !isFinite(target)) return;
  let startTime = null;
  function step(ts) {
    if (!startTime) startTime = ts;
    const progress = Math.min((ts - startTime) / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 3);
    el.textContent = fmt(ease * target);
    if (progress < 1) requestAnimationFrame(step);
    else el.textContent = fmt(target);
  }
  requestAnimationFrame(step);
}

function makeEditable() {
  document.querySelectorAll('.field-val').forEach(function (span) {
    span.setAttribute('title', 'Click to type an exact value');
    span.addEventListener('click', function () {
      if (span.querySelector('input')) return;
      let raw = span.textContent.trim();
      let numeric = raw.replace(/[$,]/g, '');
      if (/[\d.]+K$/.test(numeric)) numeric = String(parseFloat(numeric) * 1000);
      else if (/[\d.]+M$/.test(numeric)) numeric = String(parseFloat(numeric) * 1000000);
      numeric = numeric.replace(/[^0-9.]/g, '').replace(/^\./, '0.');
      if (!numeric || isNaN(parseFloat(numeric))) numeric = '0';
      const sid = span.id ? span.id.replace('v-', 's-') : null;
      const slider = sid ? document.getElementById(sid) : null;
      const inp = document.createElement('input');
      inp.type = 'text'; inp.inputMode = 'decimal'; inp.value = numeric;
      inp.className = 'field-val-input';
      inp.style.width = Math.max(60, numeric.length * 10 + 20) + 'px';
      span.innerHTML = ''; span.appendChild(inp);
      inp.focus(); inp.select();
      function commit() {
        let v = parseFloat(inp.value.replace(/[$,%\/a-zA-Z\s]/g, '').replace(/,/g, ''));
        if (isNaN(v)) v = slider ? parseFloat(slider.value) : 0;
        if (slider) {
          const mn = parseFloat(slider.min), mx = parseFloat(slider.max), st = parseFloat(slider.step) || 1;
          v = Math.min(mx, Math.max(mn, v));
          v = Math.round((v - mn) / st) * st + mn;
          v = parseFloat(v.toFixed(10));
          slider.value = v;
          slider.dispatchEvent(new Event('input', { bubbles: true }));
        }
      }
      inp.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') { e.preventDefault(); commit(); inp.blur(); }
        if (e.key === 'Escape') { inp.blur(); }
      });
      inp.addEventListener('blur', commit);
    });
  });
}

window.addEventListener('DOMContentLoaded', function () {
  initSliders();
  if (typeof calc === 'function') calc();
  makeEditable();
});
window.addEventListener('resize', function () {
  if (typeof calc === 'function') calc();
});
