/* WealthDelay Embed Loader v1.0
 * Drop-in script for third-party sites. Replaces every
 *   <div class="wd-calc" data-tool="<slug>"></div>
 * with a responsive auto-resizing iframe pointing at the embed-mode
 * version of that calculator on wealthdelay.com.
 *
 * Usage on the host page:
 *   <div class="wd-calc" data-tool="coffee-habit-true-cost"></div>
 *   <script src="https://wealthdelay.com/embed-loader.js" async></script>
 */
(function () {
  'use strict';
  var ORIGIN = 'https://wealthdelay.com';

  function buildIframe(div) {
    var slug = div.getAttribute('data-tool');
    if (!slug) return;
    slug = slug.replace(/^\/+|\/+$/g, '').replace(/\.html$/, '');

    var iframe = document.createElement('iframe');
    iframe.src = ORIGIN + '/' + slug + '?embed=1';
    iframe.style.width = '100%';
    iframe.style.maxWidth = '560px';
    iframe.style.height = '780px'; // initial; auto-resized via postMessage
    iframe.style.border = '0';
    iframe.style.borderRadius = '14px';
    iframe.style.boxShadow = '0 4px 20px rgba(0,0,0,.06)';
    iframe.style.display = 'block';
    iframe.style.margin = '0 auto';
    iframe.setAttribute('loading', 'lazy');
    iframe.setAttribute('title', 'Calculator by WealthDelay');
    iframe.dataset.wdSlug = slug;

    div.innerHTML = '';
    div.appendChild(iframe);
  }

  function init() {
    var divs = document.querySelectorAll('.wd-calc[data-tool]');
    for (var i = 0; i < divs.length; i++) buildIframe(divs[i]);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Auto-resize: listen for postMessage from any of our embedded iframes.
  // Security model: we don't trust the origin string (lets dev work); we trust
  // that the message came from a window we created (ev.source matches an iframe
  // we own with a data-wd-slug attribute). An attacker would have to inject a
  // matching iframe into the host page — at which point they have bigger powers
  // than resizing one.
  window.addEventListener('message', function (ev) {
    if (!ev.data || ev.data.type !== 'wd-embed-resize') return;
    var iframes = document.querySelectorAll('iframe[data-wd-slug]');
    for (var i = 0; i < iframes.length; i++) {
      var f = iframes[i];
      if (f.contentWindow !== ev.source) continue;
      f.style.height = (ev.data.height + 8) + 'px';
    }
  }, false);
})();
