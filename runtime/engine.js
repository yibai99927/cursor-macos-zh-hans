/**
 * Cursor 简体中文运行时翻译引擎（轻量版）
 * 由 inject-runtime.py 在安装时注入词典占位符后写入 workbench 目录。
 */
(function () {
  'use strict';

  // __EXACT_ENTRIES__
  var EXACT_ENTRIES = [];
  // __PATTERN_ENTRIES__
  var PATTERN_ENTRIES = [];
  // __FRAGMENT_ENTRIES__
  var FRAGMENT_ENTRIES = [];

  var exactMap = new Map();
  var patterns = [];
  var fragments = [];
  var ATTRS = ['title', 'aria-label', 'placeholder'];
  var SKIP_TAGS = new Set([
    'SCRIPT', 'STYLE', 'TEXTAREA', 'INPUT', 'SELECT', 'OPTION', 'CODE', 'PRE', 'KBD', 'SVG', 'PATH'
  ]);
  var pending = [];
  var scheduled = false;
  var translatedText = new WeakSet();

  function buildIndex() {
    exactMap = new Map(EXACT_ENTRIES);
    patterns = PATTERN_ENTRIES.map(function (p) {
      var flags = p.flags || '';
      try {
        return { re: new RegExp(p.regex, flags), replacement: p.replacement };
      } catch (e) {
        return null;
      }
    }).filter(Boolean);
    fragments = FRAGMENT_ENTRIES.slice().sort(function (a, b) {
      return b[0].length - a[0].length;
    });
  }

  function translateString(value) {
    if (!value || typeof value !== 'string') {
      return null;
    }
    var trimmed = value.trim();
    if (!trimmed) {
      return null;
    }
    if (exactMap.has(trimmed)) {
      var exact = exactMap.get(trimmed);
      if (trimmed === value) {
        return exact;
      }
      return value.replace(trimmed, exact);
    }
    for (var i = 0; i < patterns.length; i++) {
      var pat = patterns[i];
      if (pat.re.test(trimmed)) {
        pat.re.lastIndex = 0;
        var replaced = trimmed.replace(pat.re, pat.replacement);
        if (replaced !== trimmed) {
          return value.replace(trimmed, replaced);
        }
      }
      pat.re.lastIndex = 0;
    }
    var result = trimmed;
    var changed = false;
    for (var j = 0; j < fragments.length; j++) {
      var en = fragments[j][0];
      var zh = fragments[j][1];
      if (en && result.indexOf(en) !== -1) {
        result = result.split(en).join(zh);
        changed = true;
      }
    }
    if (changed) {
      return value.replace(trimmed, result);
    }
    return null;
  }

  function isEditorRegion(node) {
    var el = node.nodeType === Node.TEXT_NODE ? node.parentElement : node;
    if (!el || el.nodeType !== Node.ELEMENT_NODE) {
      return true;
    }
    if (SKIP_TAGS.has(el.tagName)) {
      return true;
    }
    if (el.getAttribute && el.getAttribute('contenteditable') === 'true') {
      return true;
    }
    try {
      if (el.closest && el.closest('.monaco-editor, .overflow-guard, .view-lines, .terminal, .xterm, [contenteditable="true"]')) {
        return true;
      }
    } catch (e) {}
    return false;
  }

  function translateTextNode(node) {
    if (!node || translatedText.has(node)) {
      return;
    }
    if (isEditorRegion(node)) {
      return;
    }
    var next = translateString(node.textContent);
    if (next != null) {
      node.textContent = next;
      translatedText.add(node);
    }
  }

  function translateAttributes(el) {
    if (!el || el.nodeType !== Node.ELEMENT_NODE || isEditorRegion(el)) {
      return;
    }
    for (var i = 0; i < ATTRS.length; i++) {
      var attr = ATTRS[i];
      var val = el.getAttribute(attr);
      var next = translateString(val);
      if (next != null) {
        el.setAttribute(attr, next);
      }
    }
  }

  function walk(root) {
    if (!root) {
      return;
    }
    var stack = [root];
    while (stack.length) {
      var node = stack.pop();
      if (node.nodeType === Node.ELEMENT_NODE) {
        if (SKIP_TAGS.has(node.tagName)) {
          continue;
        }
        if (node.classList && (node.classList.contains('monaco-editor') || node.classList.contains('view-lines'))) {
          continue;
        }
        translateAttributes(node);
        var children = node.childNodes;
        for (var i = children.length - 1; i >= 0; i--) {
          stack.push(children[i]);
        }
      } else if (node.nodeType === Node.TEXT_NODE) {
        translateTextNode(node);
      }
    }
  }

  function flush() {
    var nodes = pending;
    pending = [];
    scheduled = false;
    for (var i = 0; i < nodes.length; i++) {
      try {
        walk(nodes[i]);
      } catch (e) {}
    }
  }

  function enqueue(node) {
    pending.push(node);
    if (!scheduled) {
      scheduled = true;
      requestAnimationFrame(flush);
    }
  }

  function onMutations(mutations) {
    for (var i = 0; i < mutations.length; i++) {
      var m = mutations[i];
      if (m.type === 'childList') {
        for (var j = 0; j < m.addedNodes.length; j++) {
          var n = m.addedNodes[j];
          if (n.nodeType === Node.ELEMENT_NODE || n.nodeType === Node.TEXT_NODE) {
            enqueue(n);
          }
        }
      } else if (m.type === 'characterData' && m.target) {
        enqueue(m.target);
      }
    }
  }

  function translateNow() {
    if (document.body) {
      walk(document.body);
    }
  }

  function boot() {
    buildIndex();
    var target = document.documentElement || document.body;
    if (!target) {
      setTimeout(boot, 50);
      return;
    }
    var observer = new MutationObserver(onMutations);
    observer.observe(target, { childList: true, subtree: true, characterData: true });
    setTimeout(translateNow, 400);
    setTimeout(translateNow, 1500);
  }

  window.CursorZhHans = {
    translateNow: translateNow,
    version: '1.1.0'
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
