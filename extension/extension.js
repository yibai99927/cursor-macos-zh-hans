const vscode = require("vscode");
const path = require("path");
const fs = require("fs");

/** @type {Array<[string, string]>} */
let sortedPairs = [];
let observer = null;
let intervalId = null;
const translatedNodes = new WeakSet();

function loadTranslations(context) {
  const file = path.join(context.extensionPath, "translations.json");
  const raw = JSON.parse(fs.readFileSync(file, "utf8"));
  sortedPairs = Object.entries(raw).sort((a, b) => b[0].length - a[0].length);
}

function applyText(value) {
  if (!value || typeof value !== "string") {
    return value;
  }
  let result = value;
  for (const [en, zh] of sortedPairs) {
    if (result.includes(en)) {
      result = result.split(en).join(zh);
    }
  }
  return result === value ? null : result;
}

function translateTextNode(node) {
  if (translatedNodes.has(node)) {
    return;
  }
  const original = node.textContent;
  if (!original || !original.trim()) {
    return;
  }
  const next = applyText(original);
  if (next) {
    node.textContent = next;
    translatedNodes.add(node);
  }
}

function translateElementAttributes(el) {
  for (const attr of ["aria-label", "placeholder", "title", "data-search-aliases"]) {
    const value = el.getAttribute(attr);
    const next = applyText(value);
    if (next) {
      el.setAttribute(attr, next);
    }
  }
}

function walk(root) {
  if (!root) {
    return;
  }
  if (root.nodeType === Node.TEXT_NODE) {
    translateTextNode(root);
    return;
  }
  if (root.nodeType !== Node.ELEMENT_NODE) {
    return;
  }
  translateElementAttributes(root);
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  let node = walker.nextNode();
  while (node) {
    translateTextNode(node);
    node = walker.nextNode();
  }
}

function translateDocument() {
  walk(document.body);
}

function activate(context) {
  loadTranslations(context);

  observer = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      for (const added of mutation.addedNodes) {
        walk(added);
      }
    }
    translateDocument();
  });

  if (document.body) {
    observer.observe(document.body, { childList: true, subtree: true });
    translateDocument();
  } else {
    window.addEventListener(
      "DOMContentLoaded",
      () => {
        observer.observe(document.body, { childList: true, subtree: true });
        translateDocument();
      },
      { once: true }
    );
  }

  intervalId = setInterval(translateDocument, 1500);
  context.subscriptions.push({
    dispose() {
      if (observer) {
        observer.disconnect();
      }
      if (intervalId) {
        clearInterval(intervalId);
      }
    },
  });
}

function deactivate() {
  if (observer) {
    observer.disconnect();
  }
  if (intervalId) {
    clearInterval(intervalId);
  }
}

module.exports = { activate, deactivate };
