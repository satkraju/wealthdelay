/* WealthDelay Embed Runtime v1.0
 * Loaded on every calculator page. When ?embed=1 is in the URL it:
 *   - Strips nav, footer, ads, related-tools, PDF gate, FAQ, sources, share UI
 *     so only the calculator (+ Quick Answer + comparison table) renders.
 *   - Injects a slim "Powered by WealthDelay" attribution footer with a
 *     do-follow link back to the full calculator (utm-tagged for analytics).
 *   - Posts {type:'wd-embed-resize', height} to the parent window on every
 *     content size change so the host iframe can size itself, eliminating
 *     scrollbars in the embed.
 *   - Reports embed-source (parent URL via document.referrer) to GA so we
 *     can see who is actually embedding us.
 *
 * Pages are otherwise untouched if ?embed=1 is absent — zero impact on
 * the canonical SEO page.
 */
(function () {
  'use strict';

  var params = new URLSearchParams(window.location.search);
  if (params.get('embed') !== '1') return;

  /* ─── 1. Strip chrome via CSS class on <body> ──────────────────── */
  var style = document.createElement('style');
  style.textContent = [
    'body.wd-embed nav,',
    'body.wd-embed footer,',
    'body.wd-embed .related-wrap,',
    'body.wd-embed .faq-wrap,',
    'body.wd-embed .pdf-gate,',
    'body.wd-embed .ad-slot,',
    'body.wd-embed .ad-lb,',
    'body.wd-embed .ad-rect,',
    'body.wd-embed .disclaimer,',
    'body.wd-embed #wds-share,',
    'body.wd-embed #wds-tw,',
    'body.wd-embed .wd-byline,',
    'body.wd-embed .ticker,',
    /* hide the long "About / How it works / Sources" tail on calc pages */
    'body.wd-embed section[style*="max-width:760px"]:not(.wd-quick-answer) {',
    '  display: none !important;',
    '}',
    'body.wd-embed { background: transparent !important; padding-bottom: 56px; }',
    'body.wd-embed .tool-hero { padding-top: 24px !important; padding-bottom: 16px !important; }',
    'body.wd-embed .workspace { padding-top: 16px !important; padding-bottom: 24px !important; }',
    /* attribution footer */
    '.wd-embed-attrib {',
    '  position: fixed; left: 0; right: 0; bottom: 0;',
    '  background: #fff; border-top: 1px solid rgba(0,0,0,.08);',
    '  padding: 10px 16px; z-index: 9999;',
    '  display: flex; align-items: center; justify-content: space-between;',
    '  font-family: "Plus Jakarta Sans", system-ui, -apple-system, sans-serif;',
    '  font-size: 13px; color: #6e6e73;',
    '  box-shadow: 0 -2px 12px rgba(0,0,0,.04);',
    '}',
    '.wd-embed-attrib .wd-brand {',
    '  display: inline-flex; align-items: center; gap: 8px;',
    '  font-weight: 600; color: #1d1d1f; text-decoration: none;',
    '}',
    '.wd-embed-attrib .wd-brand .wd-dot {',
    '  width: 8px; height: 8px; border-radius: 50%;',
    '  background: #16A34A; flex-shrink: 0;',
    '}',
    '.wd-embed-attrib .wd-cta {',
    '  background: #16A34A; color: #fff;',
    '  padding: 7px 14px; border-radius: 8px;',
    '  font-weight: 600; font-size: 13px; text-decoration: none;',
    '  transition: background .15s;',
    '}',
    '.wd-embed-attrib .wd-cta:hover { background: #14532D; }',
    '@media (max-width: 480px) {',
    '  .wd-embed-attrib { padding: 8px 12px; font-size: 12px; }',
    '  .wd-embed-attrib .wd-cta { padding: 6px 10px; font-size: 12px; }',
    '}'
  ].join('\n');
  document.head.appendChild(style);
  document.body.classList.add('wd-embed');

  /* ─── 2. Inject "Powered by" attribution footer ────────────────── */
  // Build canonical URL for the back-link (drop the ?embed=1 query)
  var canonical = window.location.origin + window.location.pathname;
  var utm = '?utm_source=embed&utm_medium=widget&utm_campaign=' +
            encodeURIComponent((document.referrer && new URL(document.referrer).hostname) || 'unknown');

  var attrib = document.createElement('div');
  attrib.className = 'wd-embed-attrib';
  attrib.innerHTML =
    '<a class="wd-brand" href="' + canonical + utm + '" target="_blank" rel="noopener">' +
      '<span class="wd-dot"></span>Powered by WealthDelay' +
    '</a>' +
    '<a class="wd-cta" href="' + canonical + utm + '" target="_blank" rel="noopener">' +
      'Open Full Calculator &rarr;' +
    '</a>';
  // Mount when body is ready
  function mount() { document.body.appendChild(attrib); }
  if (document.body) mount();
  else document.addEventListener('DOMContentLoaded', mount);

  /* ─── 3. Auto-resize via postMessage to parent ─────────────────── */
  var lastSent = 0;
  var pendingTimer = null;
  function measure() {
    return Math.max(
      document.documentElement.scrollHeight,
      document.body ? document.body.scrollHeight : 0,
      document.documentElement.offsetHeight
    );
  }
  function _sendHeight() {
    pendingTimer = null;
    if (window.parent === window) return;
    var h = measure();
    // Suppress when the change is < 8px to avoid resize feedback loops
    if (Math.abs(h - lastSent) < 8) return;
    lastSent = h;
    try {
      window.parent.postMessage({
        type: 'wd-embed-resize',
        tool: window.location.pathname.replace(/^\//, ''),
        height: h
      }, '*');
    } catch (e) { /* parent rejected, ignore */ }
  }
  function postHeight() {
    // Debounce to 100ms so chart-render + score-paint coalesce
    if (pendingTimer) return;
    pendingTimer = setTimeout(_sendHeight, 100);
  }
  // Observe layout changes
  function start() {
    if (typeof ResizeObserver !== 'undefined' && document.body) {
      var ro = new ResizeObserver(function () { postHeight(); });
      ro.observe(document.body);
    } else {
      // Fallback: poll every 500ms
      setInterval(postHeight, 500);
    }
    // Also fire when calculator recomputes (most pages call calc() on slider input)
    document.addEventListener('input', function () { setTimeout(postHeight, 50); }, true);
    document.addEventListener('click', function () { setTimeout(postHeight, 50); }, true);
    postHeight();
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }

  /* ─── 4. Report embed source to GA (if loaded) ─────────────────── */
  function reportEmbed() {
    if (typeof window.gtag !== 'function') return;
    var host = '';
    try { host = new URL(document.referrer).hostname; } catch (e) {}
    window.gtag('event', 'embed_view', {
      embed_host: host || 'unknown',
      tool: window.location.pathname.replace(/^\//, '')
    });
  }
  // Wait a tick so gtag is initialized
  setTimeout(reportEmbed, 800);
})();
