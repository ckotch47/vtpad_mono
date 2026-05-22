(function () {
  function normalizeMermaidBlocks() {
    var pres = document.querySelectorAll('pre.mermaid');
    pres.forEach(function (pre) {
      var code = pre.querySelector('code');
      var source = code ? code.textContent : pre.textContent;
      var div = document.createElement('div');
      div.className = 'mermaid';
      div.textContent = (source || '').trim();
      pre.replaceWith(div);
    });
  }

  function initMermaid() {
    if (!window.mermaid) return;

    normalizeMermaidBlocks();

    window.mermaid.initialize({
      startOnLoad: false,
      securityLevel: 'loose'
    });

    if (typeof window.mermaid.run === 'function') {
      window.mermaid.run({ querySelector: '.mermaid' });
      return;
    }

    // Fallback for older Mermaid APIs.
    var nodes = document.querySelectorAll('div.mermaid');
    if (nodes.length && typeof window.mermaid.init === 'function') {
      window.mermaid.init(undefined, nodes);
    }
  }

  if (typeof document$ !== 'undefined' && document$.subscribe) {
    document$.subscribe(function () {
      initMermaid();
    });
  } else {
    document.addEventListener('DOMContentLoaded', initMermaid);
  }
})();
